"""
Analyze completeness of referral documents
"""

import json
from pathlib import Path

RESULTS_DIR = Path("data/evaluation/referral/results")

sections = [
    '1. DADES DEL PACIENT',
    '2. ESPECIALITAT DESTÍ',
    '3. URGÈNCIA',
    '4. MOTIU DE DERIVACIÓ',
    '5. ANTECEDENTS RELLEVANTS',
    '6. EXPLORACIONS I PROVES REALITZADES',
    '7. TRACTAMENT ACTUAL',
    '8. INFORMACIÓ ADDICIONAL'
]

print("📋 COMPLETENESS ANALYSIS - REFERRAL DOCUMENTS")
print("=" * 80)

case_files = sorted(RESULTS_DIR.glob("*_response.json"))
completeness_scores = []

for case_file in case_files:
    if "evaluation_report" in case_file.name:
        continue
        
    with open(case_file, 'r') as f:
        data = json.load(f)
    
    case_id = data['case_id']
    doc = data['generated_document']
    
    print(f"\n{case_id}")
    print("-" * 80)
    
    present_sections = []
    for section in sections:
        present = section in doc
        present_sections.append(present)
        status = '✓' if present else '✗'
        print(f"  {status} {section}")
    
    completeness = sum(present_sections) / len(sections) * 100
    completeness_scores.append(completeness)
    print(f"\n  Completeness: {completeness:.1f}%")

print("\n" + "=" * 80)
print(f"📊 AVERAGE COMPLETENESS: {sum(completeness_scores)/len(completeness_scores):.1f}%")
print(f"   Min: {min(completeness_scores):.1f}%")
print(f"   Max: {max(completeness_scores):.1f}%")
