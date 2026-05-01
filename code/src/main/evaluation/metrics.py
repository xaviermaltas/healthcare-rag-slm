"""
Metrics for evaluating discharge summary quality
Implements BLEU, ROUGE, BERTScore, and clinical-specific metrics
"""

import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Results from evaluating a discharge summary"""
    case_id: str
    
    # Text similarity metrics
    bleu_score: float = 0.0
    rouge_1_f1: float = 0.0
    rouge_2_f1: float = 0.0
    rouge_l_f1: float = 0.0
    bertscore_f1: float = 0.0
    
    # Structural completeness
    sections_present: List[str] = field(default_factory=list)
    sections_missing: List[str] = field(default_factory=list)
    completeness_score: float = 0.0
    
    # Code accuracy
    snomed_precision: float = 0.0
    snomed_recall: float = 0.0
    snomed_f1: float = 0.0
    icd10_precision: float = 0.0
    icd10_recall: float = 0.0
    icd10_f1: float = 0.0
    atc_precision: float = 0.0
    atc_recall: float = 0.0
    atc_f1: float = 0.0
    
    # Clinical content
    diagnoses_count: int = 0
    medications_count: int = 0
    expected_diagnoses_count: int = 0
    expected_medications_count: int = 0
    
    # Overall score
    overall_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'case_id': self.case_id,
            'text_similarity': {
                'bleu': round(self.bleu_score, 4),
                'rouge_1_f1': round(self.rouge_1_f1, 4),
                'rouge_2_f1': round(self.rouge_2_f1, 4),
                'rouge_l_f1': round(self.rouge_l_f1, 4),
                'bertscore_f1': round(self.bertscore_f1, 4)
            },
            'structural_completeness': {
                'sections_present': self.sections_present,
                'sections_missing': self.sections_missing,
                'completeness_score': round(self.completeness_score, 4)
            },
            'code_accuracy': {
                'snomed': {
                    'precision': round(self.snomed_precision, 4),
                    'recall': round(self.snomed_recall, 4),
                    'f1': round(self.snomed_f1, 4)
                },
                'icd10': {
                    'precision': round(self.icd10_precision, 4),
                    'recall': round(self.icd10_recall, 4),
                    'f1': round(self.icd10_f1, 4)
                },
                'atc': {
                    'precision': round(self.atc_precision, 4),
                    'recall': round(self.atc_recall, 4),
                    'f1': round(self.atc_f1, 4)
                }
            },
            'clinical_content': {
                'diagnoses_count': self.diagnoses_count,
                'expected_diagnoses_count': self.expected_diagnoses_count,
                'medications_count': self.medications_count,
                'expected_medications_count': self.expected_medications_count
            },
            'overall_score': round(self.overall_score, 4)
        }


class DischargeSummaryMetrics:
    """Metrics calculator for discharge summaries"""
    
    # Expected sections in discharge summary
    EXPECTED_SECTIONS = [
        'dades del pacient',
        'motiu d\'ingrés',
        'diagnòstic principal',
        'diagnòstics secundaris',
        'procediments realitzats',
        'tractament i medicació',
        'evolució clínica',
        'recomanacions de seguiment',
        'contraindicacions'
    ]
    
    # Code patterns - More specific to avoid false positives
    # Match codes only when preceded by the code label
    SNOMED_PATTERN = r'(?:SNOMED|Codi\s+SNOMED|Código\s+SNOMED|SNOMED\s+CT)\s*(?:és|es|is)?\s*:?\s*(\d{6,18})'
    ICD10_PATTERN = r'(?:ICD-10|ICD10|Codi\s+ICD-10|Código\s+ICD-10|Codi\s+ICD|Código\s+ICD)\s*(?:és|es|is)?\s*:?\s*([A-Z]\d{2}(?:\.\d{1,2})?)'
    ATC_PATTERN = r'(?:ATC|Codi\s+ATC|Código\s+ATC)\s*(?:és|es|is)?\s*:?\s*([A-Z]\d{2}[A-Z]{2}\d{2})'
    
    @classmethod
    def evaluate(cls,
                generated_text: str,
                reference_text: str,
                case_metadata: Dict[str, Any],
                structured_codes: Optional[Dict[str, Set[str]]] = None) -> EvaluationResult:
        """
        Evaluate a generated discharge summary against reference
        
        Args:
            generated_text: Generated discharge summary
            reference_text: Gold standard reference
            case_metadata: Metadata with expected codes and counts
            structured_codes: Pre-extracted codes from API structured response
                              (more reliable than text regex). Keys: snomed, icd10, atc
            
        Returns:
            EvaluationResult with all metrics
        """
        result = EvaluationResult(case_id=case_metadata.get('case_id', 'unknown'))
        
        # 1. Text similarity metrics
        result.bleu_score = calculate_bleu_score(generated_text, reference_text)
        rouge_scores = calculate_rouge_scores(generated_text, reference_text)
        result.rouge_1_f1 = rouge_scores.get('rouge-1', {}).get('f', 0.0)
        result.rouge_2_f1 = rouge_scores.get('rouge-2', {}).get('f', 0.0)
        result.rouge_l_f1 = rouge_scores.get('rouge-l', {}).get('f', 0.0)
        
        # BERTScore (optional, requires model)
        try:
            result.bertscore_f1 = calculate_bertscore(generated_text, reference_text)
        except Exception as e:
            logger.warning(f"BERTScore calculation failed: {e}")
            result.bertscore_f1 = 0.0
        
        # 2. Structural completeness
        sections_present, sections_missing = cls._check_sections(generated_text)
        result.sections_present = sections_present
        result.sections_missing = sections_missing
        result.completeness_score = len(sections_present) / len(cls.EXPECTED_SECTIONS)
        
        # 3. Code accuracy
        # Use structured codes from API response when available (more reliable than text regex)
        # Fall back to text extraction when not provided
        text_extracted = cls._extract_codes(generated_text)
        expected_codes = case_metadata.get('expected_codes', {})
        
        def _merge(text_set: Set[str], struct_set: Set[str]) -> Set[str]:
            """Merge text-extracted and structured codes, preferring structured ones."""
            return struct_set if struct_set else text_set
        
        final_snomed = _merge(
            text_extracted['snomed'],
            structured_codes.get('snomed', set()) if structured_codes else set()
        )
        final_icd10 = _merge(
            text_extracted['icd10'],
            structured_codes.get('icd10', set()) if structured_codes else set()
        )
        final_atc = _merge(
            text_extracted['atc'],
            structured_codes.get('atc', set()) if structured_codes else set()
        )
        
        # SNOMED codes
        snomed_metrics = cls._calculate_code_metrics(
            final_snomed,
            set(expected_codes.get('snomed', []))
        )
        result.snomed_precision = snomed_metrics['precision']
        result.snomed_recall = snomed_metrics['recall']
        result.snomed_f1 = snomed_metrics['f1']
        
        # ICD-10 codes
        icd10_metrics = cls._calculate_code_metrics(
            final_icd10,
            set(expected_codes.get('icd10', []))
        )
        result.icd10_precision = icd10_metrics['precision']
        result.icd10_recall = icd10_metrics['recall']
        result.icd10_f1 = icd10_metrics['f1']
        
        # ATC codes
        atc_metrics = cls._calculate_code_metrics(
            final_atc,
            set(expected_codes.get('atc', []))
        )
        result.atc_precision = atc_metrics['precision']
        result.atc_recall = atc_metrics['recall']
        result.atc_f1 = atc_metrics['f1']
        
        # 4. Clinical content counts
        result.diagnoses_count = len(final_snomed) + len(final_icd10)
        result.medications_count = len(final_atc)
        result.expected_diagnoses_count = case_metadata.get('expected_diagnoses_count', 0)
        result.expected_medications_count = case_metadata.get('expected_medications_count', 0)
        
        # 5. Calculate overall score (weighted average)
        result.overall_score = cls._calculate_overall_score(result)
        
        return result
    
    @classmethod
    def _check_sections(cls, text: str) -> tuple[List[str], List[str]]:
        """Check which sections are present in the text"""
        text_lower = text.lower()
        present = []
        missing = []
        
        for section in cls.EXPECTED_SECTIONS:
            # Check for section header (with or without numbers)
            pattern = re.escape(section)
            if re.search(pattern, text_lower):
                present.append(section)
            else:
                missing.append(section)
        
        return present, missing
    
    @classmethod
    def _extract_codes(cls, text: str) -> Dict[str, Set[str]]:
        """Extract medical codes from text"""
        return {
            'snomed': set(re.findall(cls.SNOMED_PATTERN, text)),
            'icd10': set(re.findall(cls.ICD10_PATTERN, text)),
            'atc': set(re.findall(cls.ATC_PATTERN, text))
        }
    
    @classmethod
    def _calculate_code_metrics(cls, 
                                generated: Set[str], 
                                expected: Set[str]) -> Dict[str, float]:
        """Calculate precision, recall, F1 for codes.
        
        Supports both exact and prefix matching.
        Prefix match (e.g. 'I63' vs 'I63.4') gives 0.75 credit.
        """
        if not expected:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
        
        if not generated:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
        
        # Exact matches
        exact = generated & expected
        
        # Prefix matches on remaining codes: I63 matches I63.4 (0.75 credit)
        unmatched_gen = generated - exact
        unmatched_exp = expected - exact
        prefix_gen: Set[str] = set()
        for gen in unmatched_gen:
            for exp in unmatched_exp:
                if len(gen) >= 3 and (exp.startswith(gen) or gen.startswith(exp)):
                    prefix_gen.add(gen)
                    break
        
        # Base code matches: E11.9 and E11.10 share base E11 (0.50 credit)
        still_unmatched = unmatched_gen - prefix_gen
        base_gen: Set[str] = set()
        for gen in still_unmatched:
            gen_base = gen[:3]
            for exp in unmatched_exp:
                if exp[:3] == gen_base and len(gen_base) == 3:
                    base_gen.add(gen)
                    break
        
        tp = len(exact) + 0.75 * len(prefix_gen) + 0.50 * len(base_gen)
        precision = tp / len(generated)
        recall    = tp / len(expected)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'precision': round(precision, 4),
            'recall':    round(recall,    4),
            'f1':        round(f1,        4)
        }
    
    @classmethod
    def _calculate_overall_score(cls, result: EvaluationResult) -> float:
        """Calculate weighted overall score"""
        weights = {
            'text_similarity': 0.30,      # 30%
            'completeness': 0.20,          # 20%
            'code_accuracy': 0.30,         # 30%
            'content_counts': 0.20         # 20%
        }
        
        # Text similarity (average of ROUGE-L and BLEU)
        text_sim = (result.rouge_l_f1 + result.bleu_score) / 2
        
        # Code accuracy (average of F1 scores)
        code_acc = (result.snomed_f1 + result.icd10_f1 + result.atc_f1) / 3
        
        # Content counts (how close to expected)
        diag_ratio = min(result.diagnoses_count / result.expected_diagnoses_count, 1.0) if result.expected_diagnoses_count > 0 else 0.0
        med_ratio = min(result.medications_count / result.expected_medications_count, 1.0) if result.expected_medications_count > 0 else 0.0
        content_score = (diag_ratio + med_ratio) / 2
        
        overall = (
            weights['text_similarity'] * text_sim +
            weights['completeness'] * result.completeness_score +
            weights['code_accuracy'] * code_acc +
            weights['content_counts'] * content_score
        )
        
        return overall


def calculate_bleu_score(generated: str, reference: str) -> float:
    """
    Calculate BLEU score (simplified implementation)
    For production, use nltk.translate.bleu_score
    """
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        from nltk.tokenize import word_tokenize
        
        reference_tokens = [word_tokenize(reference.lower())]
        generated_tokens = word_tokenize(generated.lower())
        
        smoothie = SmoothingFunction().method4
        score = sentence_bleu(reference_tokens, generated_tokens, smoothing_function=smoothie)
        return score
    except ImportError:
        logger.warning("NLTK not available, using simple n-gram overlap")
        return _simple_ngram_overlap(generated, reference)


def calculate_rouge_scores(generated: str, reference: str) -> Dict[str, Dict[str, float]]:
    """
    Calculate ROUGE scores
    For production, use rouge_score library
    """
    try:
        from rouge_score import rouge_scorer
        
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        scores = scorer.score(reference, generated)
        
        return {
            'rouge-1': {'f': scores['rouge1'].fmeasure, 'p': scores['rouge1'].precision, 'r': scores['rouge1'].recall},
            'rouge-2': {'f': scores['rouge2'].fmeasure, 'p': scores['rouge2'].precision, 'r': scores['rouge2'].recall},
            'rouge-l': {'f': scores['rougeL'].fmeasure, 'p': scores['rougeL'].precision, 'r': scores['rougeL'].recall}
        }
    except ImportError:
        logger.warning("rouge_score not available, using simple overlap")
        overlap = _simple_ngram_overlap(generated, reference)
        return {
            'rouge-1': {'f': overlap, 'p': overlap, 'r': overlap},
            'rouge-2': {'f': overlap * 0.8, 'p': overlap * 0.8, 'r': overlap * 0.8},
            'rouge-l': {'f': overlap * 0.9, 'p': overlap * 0.9, 'r': overlap * 0.9}
        }


def calculate_bertscore(generated: str, reference: str) -> float:
    """
    Calculate BERTScore
    Requires bert_score library and model
    """
    try:
        from bert_score import score
        
        P, R, F1 = score([generated], [reference], lang='ca', verbose=False)
        return F1.item()
    except ImportError:
        logger.warning("bert_score not available, skipping BERTScore")
        return 0.0
    except Exception as e:
        logger.warning(f"BERTScore calculation failed: {e}")
        return 0.0


def _simple_ngram_overlap(text1: str, text2: str, n: int = 2) -> float:
    """Simple n-gram overlap as fallback"""
    def get_ngrams(text: str, n: int) -> Set[str]:
        words = text.lower().split()
        return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))
    
    ngrams1 = get_ngrams(text1, n)
    ngrams2 = get_ngrams(text2, n)
    
    if not ngrams1 or not ngrams2:
        return 0.0
    
    intersection = len(ngrams1 & ngrams2)
    union = len(ngrams1 | ngrams2)
    
    return intersection / union if union > 0 else 0.0
