"""
Referral Document Evaluation Script
Avalua la qualitat dels informes de derivació generats
"""

import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.main.evaluation.metrics import calculate_bleu_score, calculate_rouge_scores

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
CASES_DIR = BASE_DIR / "data" / "evaluation" / "referral" / "cases"
GOLD_STANDARD_DIR = BASE_DIR / "data" / "evaluation" / "referral" / "gold_standard"
RESULTS_DIR = BASE_DIR / "data" / "evaluation" / "referral" / "results"

# API configuration
API_URL = "http://localhost:8000"


def load_test_case(case_file: Path) -> Dict[str, Any]:
    """Load a test case from JSON file"""
    with open(case_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_gold_standard(case_id: str) -> str:
    """Load gold standard referral document"""
    gold_file = GOLD_STANDARD_DIR / f"{case_id}.txt"
    with open(gold_file, 'r', encoding='utf-8') as f:
        return f.read()


def generate_referral(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Generate referral document via API"""
    endpoint = f"{API_URL}/generate/referral"
    
    payload = {
        "patient_context": test_case["patient_context"],
        "referral_reason": test_case["referral_reason"],
        "relevant_history": test_case["relevant_history"],
        "examinations": test_case["examinations"],
        "current_medications": test_case["current_medications"],
        "target_specialty": test_case.get("specialty"),
        "urgency": test_case.get("urgency", "normal"),
        "additional_info": test_case.get("additional_info"),
        "language": test_case.get("language", "ca")
    }
    
    response = requests.post(endpoint, json=payload, timeout=120)
    
    if response.status_code != 200:
        error_detail = response.json().get("error", "Unknown error")
        logger.error(f"API error {response.status_code}: {error_detail}")
        raise Exception(f"API request failed: {error_detail}")
    
    return response.json()


def evaluate_specialty_accuracy(
    generated_specialty: str,
    expected_specialty: str
) -> float:
    """
    Evaluate if the detected specialty is correct
    Returns 1.0 if correct, 0.0 if incorrect
    """
    return 1.0 if generated_specialty.lower() == expected_specialty.lower() else 0.0


def evaluate_urgency_accuracy(
    generated_urgency: str,
    expected_urgency: str
) -> float:
    """
    Evaluate if the urgency level is correct
    Returns 1.0 if correct, 0.5 if one level off, 0.0 if completely wrong
    """
    urgency_levels = ["normal", "preferent", "urgent"]
    
    try:
        gen_idx = urgency_levels.index(generated_urgency.lower())
        exp_idx = urgency_levels.index(expected_urgency.lower())
        
        diff = abs(gen_idx - exp_idx)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.5
        else:
            return 0.0
    except ValueError:
        return 0.0


def evaluate_case(case_file: Path) -> Dict[str, Any]:
    """Evaluate a single test case"""
    case_id = case_file.stem
    logger.info(f"\n{'='*80}")
    logger.info(f"Evaluating: {case_id}")
    logger.info(f"{'='*80}")
    
    # Load test case and gold standard
    test_case = load_test_case(case_file)
    gold_standard = load_gold_standard(case_id)
    
    # Generate referral document
    logger.info("Generating referral document...")
    try:
        response = generate_referral(test_case)
        generated_document = response["referral_document"]
        generated_specialty = response["target_specialty"]
        generated_urgency = response["urgency_level"]
        generation_time = response["metadata"].get("generation_time_ms", 0)
        
    except Exception as e:
        logger.error(f"Failed to generate referral for {case_id}")
        return None
    
    # Calculate metrics
    logger.info("Calculating metrics...")
    
    # Text similarity metrics
    bleu_score = calculate_bleu_score(generated_document, gold_standard)
    rouge_scores = calculate_rouge_scores(generated_document, gold_standard)
    
    text_metrics = {
        "bleu": bleu_score,
        "rouge_1": rouge_scores["rouge-1"]["f"],
        "rouge_2": rouge_scores["rouge-2"]["f"],
        "rouge_l": rouge_scores["rouge-l"]["f"]
    }
    
    # Specialty accuracy
    expected_specialty = test_case["metadata"]["expected_specialty"]
    specialty_accuracy = evaluate_specialty_accuracy(
        generated_specialty,
        expected_specialty
    )
    
    # Urgency accuracy
    expected_urgency = test_case["metadata"]["expected_urgency"]
    urgency_accuracy = evaluate_urgency_accuracy(
        generated_urgency,
        expected_urgency
    )
    
    # SNOMED CT code accuracy (if available)
    expected_codes = test_case["metadata"].get("expected_reason_codes", [])
    generated_codes = response.get("referral_reason_codes", [])
    
    snomed_f1 = 0.0
    if expected_codes and generated_codes:
        expected_snomed = {c["snomed_code"] for c in expected_codes if c.get("snomed_code")}
        generated_snomed = {c.get("snomed_code") for c in generated_codes if c.get("snomed_code")}
        
        if expected_snomed or generated_snomed:
            tp = len(expected_snomed & generated_snomed)
            fp = len(generated_snomed - expected_snomed)
            fn = len(expected_snomed - generated_snomed)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            snomed_f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Overall score
    overall_score = (
        0.40 * (text_metrics["bleu"] + text_metrics["rouge_l"]) / 2 +
        0.30 * specialty_accuracy +
        0.15 * urgency_accuracy +
        0.15 * snomed_f1
    )
    
    # Print results
    print(f"\n📊 EVALUATION RESULTS - {case_id}")
    print("=" * 80)
    print(f"\n📝 TEXT SIMILARITY:")
    print(f"   BLEU:      {text_metrics['bleu']:.4f}")
    print(f"   ROUGE-1:   {text_metrics['rouge_1']:.4f}")
    print(f"   ROUGE-2:   {text_metrics['rouge_2']:.4f}")
    print(f"   ROUGE-L:   {text_metrics['rouge_l']:.4f}")
    
    print(f"\n🎯 CLINICAL ACCURACY:")
    print(f"   Specialty:  {specialty_accuracy*100:.1f}% ({'✓' if specialty_accuracy == 1.0 else '✗'} {generated_specialty} vs {expected_specialty})")
    print(f"   Urgency:    {urgency_accuracy*100:.1f}% ({'✓' if urgency_accuracy == 1.0 else '✗'} {generated_urgency} vs {expected_urgency})")
    print(f"   SNOMED F1:  {snomed_f1:.4f}")
    
    print(f"\n⭐ OVERALL SCORE: {overall_score:.4f} ({overall_score*100:.1f}%)")
    
    quality_label = "🟢 Excellent" if overall_score >= 0.8 else \
                   "🟡 Good" if overall_score >= 0.7 else \
                   "🟠 Acceptable" if overall_score >= 0.6 else \
                   "🔴 NEEDS IMPROVEMENT"
    print(f"   Quality: {quality_label}")
    
    # Save results
    result = {
        "case_id": case_id,
        "generated_document": generated_document,
        "generated_specialty": generated_specialty,
        "generated_urgency": generated_urgency,
        "expected_specialty": expected_specialty,
        "expected_urgency": expected_urgency,
        "metrics": {
            "bleu": text_metrics["bleu"],
            "rouge_1": text_metrics["rouge_1"],
            "rouge_2": text_metrics["rouge_2"],
            "rouge_l": text_metrics["rouge_l"],
            "specialty_accuracy": specialty_accuracy,
            "urgency_accuracy": urgency_accuracy,
            "snomed_f1": snomed_f1,
            "overall_score": overall_score
        },
        "generation_time_ms": generation_time,
        "timestamp": datetime.now().isoformat()
    }
    
    result_file = RESULTS_DIR / f"{case_id}_response.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result


def main():
    """Main evaluation function"""
    logger.info("🚀 Starting Referral Document Evaluation")
    logger.info(f"Cases directory: {CASES_DIR}")
    logger.info(f"Gold standard directory: {GOLD_STANDARD_DIR}")
    logger.info(f"Results directory: {RESULTS_DIR}")
    
    # Create results directory
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get all test cases
    case_files = sorted(CASES_DIR.glob("*.json"))
    logger.info(f"Found {len(case_files)} test cases\n")
    
    # Evaluate each case
    results = []
    for case_file in case_files:
        result = evaluate_case(case_file)
        if result:
            results.append(result)
    
    if not results:
        logger.error("\n❌ EVALUATION FAILED (no results)")
        return
    
    # Calculate aggregate metrics
    avg_bleu = sum(r["metrics"]["bleu"] for r in results) / len(results)
    avg_rouge_l = sum(r["metrics"]["rouge_l"] for r in results) / len(results)
    avg_specialty = sum(r["metrics"]["specialty_accuracy"] for r in results) / len(results)
    avg_urgency = sum(r["metrics"]["urgency_accuracy"] for r in results) / len(results)
    avg_snomed = sum(r["metrics"]["snomed_f1"] for r in results) / len(results)
    avg_overall = sum(r["metrics"]["overall_score"] for r in results) / len(results)
    
    # Print summary
    print(f"\n\n{'='*80}")
    print(f"📊 EVALUATION REPORT - {len(results)} cases")
    print("=" * 80)
    
    print(f"\n📈 AVERAGE METRICS:")
    print(f"   BLEU Score:        {avg_bleu:.4f}")
    print(f"   ROUGE-L F1:        {avg_rouge_l:.4f}")
    print(f"   Specialty Accuracy: {avg_specialty*100:.1f}%")
    print(f"   Urgency Accuracy:   {avg_urgency*100:.1f}%")
    print(f"   SNOMED CT F1:      {avg_snomed:.4f}")
    print(f"   Overall Score:     {avg_overall:.4f} ({avg_overall*100:.1f}%)")
    
    # Quality distribution
    excellent = sum(1 for r in results if r["metrics"]["overall_score"] >= 0.8)
    good = sum(1 for r in results if 0.7 <= r["metrics"]["overall_score"] < 0.8)
    acceptable = sum(1 for r in results if 0.6 <= r["metrics"]["overall_score"] < 0.7)
    poor = sum(1 for r in results if r["metrics"]["overall_score"] < 0.6)
    
    print(f"\n📊 QUALITY DISTRIBUTION:")
    print(f"   🟢 Excellent (≥0.8):     {excellent} ({excellent/len(results)*100:.1f}%)")
    print(f"   🟡 Good (0.7-0.8):       {good} ({good/len(results)*100:.1f}%)")
    print(f"   🟠 Acceptable (0.6-0.7): {acceptable} ({acceptable/len(results)*100:.1f}%)")
    print(f"   🔴 Poor (<0.6):          {poor} ({poor/len(results)*100:.1f}%)")
    
    # Per-case summary
    print(f"\n📋 PER-CASE SUMMARY:")
    sorted_results = sorted(results, key=lambda x: x["metrics"]["overall_score"], reverse=True)
    for r in sorted_results:
        quality_icon = "🟢" if r["metrics"]["overall_score"] >= 0.8 else \
                      "🟡" if r["metrics"]["overall_score"] >= 0.7 else \
                      "🟠" if r["metrics"]["overall_score"] >= 0.6 else "🔴"
        print(f"   {quality_icon} {r['case_id']:<45} {r['metrics']['overall_score']:.4f}")
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = RESULTS_DIR / f"evaluation_report_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(results),
        "average_metrics": {
            "bleu": avg_bleu,
            "rouge_l": avg_rouge_l,
            "specialty_accuracy": avg_specialty,
            "urgency_accuracy": avg_urgency,
            "snomed_f1": avg_snomed,
            "overall_score": avg_overall
        },
        "quality_distribution": {
            "excellent": excellent,
            "good": good,
            "acceptable": acceptable,
            "poor": poor
        },
        "per_case_results": sorted_results
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Report saved to: {report_file}")
    
    # Final verdict
    if avg_overall >= 0.6:
        logger.info(f"\n✅ EVALUATION PASSED (average score: {avg_overall:.4f})")
    else:
        logger.warning(f"\n⚠️  EVALUATION NEEDS IMPROVEMENT (average score: {avg_overall:.4f})")


if __name__ == "__main__":
    main()
