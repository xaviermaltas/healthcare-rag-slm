"""
Automatic Evaluation Script for Discharge Summaries
Evaluates generated discharge summaries against gold standard references
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import requests
from datetime import datetime
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main.evaluation.metrics import DischargeSummaryMetrics, EvaluationResult

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


API_URL = "http://localhost:8000"
CASES_DIR = project_root / "data" / "evaluation" / "discharge_summary" / "cases"
GOLD_STANDARD_DIR = project_root / "data" / "evaluation" / "discharge_summary" / "gold_standard"
RESULTS_DIR = project_root / "data" / "evaluation" / "discharge_summary" / "results"


def load_test_case(case_file: Path) -> Dict[str, Any]:
    """Load a test case from JSON file"""
    with open(case_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_gold_standard(case_id: str) -> str:
    """Load gold standard reference for a case"""
    gold_file = GOLD_STANDARD_DIR / f"{case_id}.txt"
    if not gold_file.exists():
        logger.warning(f"Gold standard not found for {case_id}")
        return ""
    
    with open(gold_file, 'r', encoding='utf-8') as f:
        return f.read()


def generate_discharge_summary(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate discharge summary using the API"""
    try:
        # Prepare request
        request_data = {
            'patient_context': case_data['patient_context'],
            'admission_reason': case_data['admission_reason'],
            'procedures': case_data['procedures'],
            'current_medications': case_data['current_medications'],
            'language': case_data.get('language', 'ca'),
            'specialty': case_data.get('specialty')
        }
        
        # Call API
        response = requests.post(
            f"{API_URL}/generate/discharge-summary",
            json=request_data,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return None


def evaluate_case(case_file: Path) -> EvaluationResult:
    """Evaluate a single test case"""
    logger.info(f"\n{'='*80}")
    logger.info(f"Evaluating: {case_file.stem}")
    logger.info(f"{'='*80}")
    
    # Load test case
    case_data = load_test_case(case_file)
    case_id = case_data['case_id']
    
    # Load gold standard
    reference_text = load_gold_standard(case_id)
    if not reference_text:
        logger.error(f"Skipping {case_id}: no gold standard found")
        return None
    
    # Generate discharge summary
    logger.info("Generating discharge summary...")
    generated_response = generate_discharge_summary(case_data)
    
    if not generated_response:
        logger.error(f"Failed to generate summary for {case_id}")
        return None
    
    generated_text = generated_response.get('summary', '')
    
    # Extract structured codes from API response (diagnoses + medications)
    # These are more reliable than text regex extraction
    structured_codes = {
        'snomed': set(),
        'icd10': set(),
        'atc': set()
    }
    for diag in generated_response.get('diagnoses', []):
        if diag.get('snomed_code'):
            structured_codes['snomed'].add(diag['snomed_code'])
        if diag.get('icd10_code'):
            structured_codes['icd10'].add(diag['icd10_code'])
    for med in generated_response.get('medications', []):
        if med.get('atc_code'):
            structured_codes['atc'].add(med['atc_code'])
    
    logger.info(f"Structured codes from response - SNOMED: {structured_codes['snomed']}, "
                f"ICD-10: {structured_codes['icd10']}, ATC: {structured_codes['atc']}")
    
    # Build metadata with case_id included (needed for EvaluationResult labeling)
    case_metadata = case_data.get('metadata', {})
    case_metadata['case_id'] = case_id
    
    # Evaluate
    logger.info("Calculating metrics...")
    result = DischargeSummaryMetrics.evaluate(
        generated_text=generated_text,
        reference_text=reference_text,
        case_metadata=case_metadata,
        structured_codes=structured_codes
    )
    
    # Print results
    print_evaluation_result(result)
    
    # Save generated summary
    save_generated_summary(case_id, generated_text, generated_response)
    
    return result


def print_evaluation_result(result: EvaluationResult):
    """Print evaluation results in a readable format"""
    print(f"\n📊 EVALUATION RESULTS - {result.case_id}")
    print(f"{'='*80}\n")
    
    print("📝 TEXT SIMILARITY:")
    print(f"   BLEU:      {result.bleu_score:.4f}")
    print(f"   ROUGE-1:   {result.rouge_1_f1:.4f}")
    print(f"   ROUGE-2:   {result.rouge_2_f1:.4f}")
    print(f"   ROUGE-L:   {result.rouge_l_f1:.4f}")
    if result.bertscore_f1 > 0:
        print(f"   BERTScore: {result.bertscore_f1:.4f}")
    
    print(f"\n📋 STRUCTURAL COMPLETENESS: {result.completeness_score:.2%}")
    print(f"   Sections present: {len(result.sections_present)}/{len(DischargeSummaryMetrics.EXPECTED_SECTIONS)}")
    if result.sections_missing:
        print(f"   Missing: {', '.join(result.sections_missing)}")
    
    print(f"\n🏥 CODE ACCURACY:")
    print(f"   SNOMED CT - P: {result.snomed_precision:.2%}, R: {result.snomed_recall:.2%}, F1: {result.snomed_f1:.4f}")
    print(f"   ICD-10    - P: {result.icd10_precision:.2%}, R: {result.icd10_recall:.2%}, F1: {result.icd10_f1:.4f}")
    print(f"   ATC       - P: {result.atc_precision:.2%}, R: {result.atc_recall:.2%}, F1: {result.atc_f1:.4f}")
    
    print(f"\n📊 CLINICAL CONTENT:")
    print(f"   Diagnoses:   {result.diagnoses_count} / {result.expected_diagnoses_count} expected")
    print(f"   Medications: {result.medications_count} / {result.expected_medications_count} expected")
    
    print(f"\n⭐ OVERALL SCORE: {result.overall_score:.4f} ({result.overall_score*100:.1f}%)")
    
    # Quality assessment
    if result.overall_score >= 0.8:
        quality = "🟢 EXCELLENT"
    elif result.overall_score >= 0.7:
        quality = "🟡 GOOD"
    elif result.overall_score >= 0.6:
        quality = "🟠 ACCEPTABLE"
    else:
        quality = "🔴 NEEDS IMPROVEMENT"
    
    print(f"   Quality: {quality}\n")


def save_generated_summary(case_id: str, generated_text: str, full_response: Dict[str, Any]):
    """Save generated summary and full response"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save generated text
    text_file = RESULTS_DIR / f"{case_id}_generated.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(generated_text)
    
    # Save full response
    json_file = RESULTS_DIR / f"{case_id}_response.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(full_response, f, indent=2, ensure_ascii=False)


def generate_report(results: List[EvaluationResult]):
    """Generate evaluation report"""
    if not results:
        logger.error("No results to report")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 EVALUATION REPORT - {len(results)} cases")
    print(f"{'='*80}\n")
    
    # Calculate averages
    avg_bleu = sum(r.bleu_score for r in results) / len(results)
    avg_rouge_l = sum(r.rouge_l_f1 for r in results) / len(results)
    avg_completeness = sum(r.completeness_score for r in results) / len(results)
    avg_snomed_f1 = sum(r.snomed_f1 for r in results) / len(results)
    avg_icd10_f1 = sum(r.icd10_f1 for r in results) / len(results)
    avg_overall = sum(r.overall_score for r in results) / len(results)
    
    print("📈 AVERAGE METRICS:")
    print(f"   BLEU Score:        {avg_bleu:.4f}")
    print(f"   ROUGE-L F1:        {avg_rouge_l:.4f}")
    print(f"   Completeness:      {avg_completeness:.2%}")
    print(f"   SNOMED CT F1:      {avg_snomed_f1:.4f}")
    print(f"   ICD-10 F1:         {avg_icd10_f1:.4f}")
    print(f"   Overall Score:     {avg_overall:.4f} ({avg_overall*100:.1f}%)\n")
    
    # Quality distribution
    excellent = sum(1 for r in results if r.overall_score >= 0.8)
    good = sum(1 for r in results if 0.7 <= r.overall_score < 0.8)
    acceptable = sum(1 for r in results if 0.6 <= r.overall_score < 0.7)
    poor = sum(1 for r in results if r.overall_score < 0.6)
    
    print("📊 QUALITY DISTRIBUTION:")
    print(f"   🟢 Excellent (≥0.8):     {excellent} ({excellent/len(results)*100:.1f}%)")
    print(f"   🟡 Good (0.7-0.8):       {good} ({good/len(results)*100:.1f}%)")
    print(f"   🟠 Acceptable (0.6-0.7): {acceptable} ({acceptable/len(results)*100:.1f}%)")
    print(f"   🔴 Poor (<0.6):          {poor} ({poor/len(results)*100:.1f}%)\n")
    
    # Per-case summary
    print("📋 PER-CASE SUMMARY:")
    for result in sorted(results, key=lambda r: r.overall_score, reverse=True):
        quality_icon = "🟢" if result.overall_score >= 0.8 else "🟡" if result.overall_score >= 0.7 else "🟠" if result.overall_score >= 0.6 else "🔴"
        print(f"   {quality_icon} {result.case_id:40s} {result.overall_score:.4f}")
    
    # Save report
    report_file = RESULTS_DIR / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'total_cases': len(results),
        'averages': {
            'bleu': avg_bleu,
            'rouge_l': avg_rouge_l,
            'completeness': avg_completeness,
            'snomed_f1': avg_snomed_f1,
            'icd10_f1': avg_icd10_f1,
            'overall': avg_overall
        },
        'quality_distribution': {
            'excellent': excellent,
            'good': good,
            'acceptable': acceptable,
            'poor': poor
        },
        'cases': [r.to_dict() for r in results]
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Report saved to: {report_file}")


def main():
    """Main evaluation function"""
    logger.info("🚀 Starting Discharge Summary Evaluation")
    logger.info(f"Cases directory: {CASES_DIR}")
    logger.info(f"Gold standard directory: {GOLD_STANDARD_DIR}")
    logger.info(f"Results directory: {RESULTS_DIR}\n")
    
    # Find all test cases
    case_files = sorted(CASES_DIR.glob("*.json"))
    
    if not case_files:
        logger.error(f"No test cases found in {CASES_DIR}")
        return 1
    
    logger.info(f"Found {len(case_files)} test cases\n")
    
    # Evaluate each case
    results = []
    for case_file in case_files:
        result = evaluate_case(case_file)
        if result:
            results.append(result)
    
    # Generate report
    if results:
        generate_report(results)
        
        # Return exit code based on average score
        avg_score = sum(r.overall_score for r in results) / len(results)
        if avg_score >= 0.7:
            logger.info("\n✅ EVALUATION PASSED (average score ≥ 0.7)")
            return 0
        else:
            logger.warning(f"\n⚠️  EVALUATION NEEDS IMPROVEMENT (average score: {avg_score:.4f})")
            return 1
    else:
        logger.error("\n❌ EVALUATION FAILED (no results)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
