#!/usr/bin/env python3
"""
Test Anti-Patterns Elimination
Valida que NO hi ha cap ús de MedicalTranslator (anti-pattern) al codi
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_antipattern_usage(root_dir: str) -> List[Tuple[str, int, str]]:
    """
    Busca usos de MedicalTranslator al codi
    
    Returns:
        List of (file_path, line_number, line_content)
    """
    antipatterns = []
    
    # Patterns to search for
    patterns = [
        r'MedicalTranslator\.',  # Direct usage
        r'from.*medical_translator.*import.*MedicalTranslator',  # Import
        r'import.*medical_translator',  # Module import
    ]
    
    # Directories to search
    search_dirs = [
        'src/main/api/routes',
        'src/main/core/coding',
        'src/main/core/prompts',
        'src/main/core/parsers'
    ]
    
    for search_dir in search_dirs:
        dir_path = Path(root_dir) / search_dir
        if not dir_path.exists():
            continue
        
        # Search all Python files
        for py_file in dir_path.rglob('*.py'):
            # Skip __pycache__ and test files
            if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                continue
            
            # Skip medical_translator.py itself (it's the legacy file)
            if 'medical_translator.py' in str(py_file):
                logger.info(f"⚠️ Skipping legacy file: {py_file}")
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        # Check each pattern
                        for pattern in patterns:
                            if re.search(pattern, line):
                                # Check if it's a comment explaining removal
                                if 'ELIMINAT' in line or 'anti-pattern' in line.lower():
                                    logger.info(f"✅ Found removal comment in {py_file}:{line_num}")
                                    continue
                                
                                antipatterns.append((
                                    str(py_file),
                                    line_num,
                                    line.strip()
                                ))
            except Exception as e:
                logger.warning(f"Error reading {py_file}: {e}")
    
    return antipatterns


def check_semantic_architecture(root_dir: str) -> dict:
    """
    Verifica que els endpoints usen arquitectura semàntica
    
    Returns:
        Dict amb estadístiques
    """
    stats = {
        'endpoints_checked': 0,
        'using_semantic': 0,
        'using_legacy': 0,
        'details': []
    }
    
    # Check main endpoint files
    endpoint_files = [
        'src/main/api/routes/discharge_summary.py',
        'src/main/api/routes/referral.py',
        'src/main/api/routes/clinical_summary.py'
    ]
    
    for endpoint_file in endpoint_files:
        file_path = Path(root_dir) / endpoint_file
        if not file_path.exists():
            logger.warning(f"⚠️ Endpoint file not found: {endpoint_file}")
            continue
        
        stats['endpoints_checked'] += 1
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for semantic methods
            has_semantic = bool(re.search(r'get_\w+_code_semantic', content))
            
            # Check for direct MedicalTranslator usage (bad)
            has_translator = bool(re.search(r'MedicalTranslator\.', content))
            
            if has_semantic and not has_translator:
                stats['using_semantic'] += 1
                status = "✅ SEMANTIC"
            elif has_translator:
                stats['using_legacy'] += 1
                status = "❌ LEGACY (MedicalTranslator)"
            else:
                status = "⚠️ UNKNOWN"
            
            stats['details'].append({
                'file': endpoint_file,
                'status': status,
                'has_semantic': has_semantic,
                'has_translator': has_translator
            })
    
    return stats


def main():
    """Test principal"""
    logger.info("🔍 Testing for Anti-Patterns Elimination...")
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    logger.info(f"Project root: {project_root}")
    
    # ========================================================================
    # TEST 1: Search for MedicalTranslator usage
    # ========================================================================
    
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Searching for MedicalTranslator anti-pattern usage...")
    logger.info("="*80)
    
    antipatterns = find_antipattern_usage(str(project_root))
    
    if antipatterns:
        logger.error(f"\n❌ Found {len(antipatterns)} anti-pattern usages:")
        for file_path, line_num, line_content in antipatterns:
            logger.error(f"  {file_path}:{line_num}")
            logger.error(f"    {line_content}")
        logger.error("\n⚠️ ANTI-PATTERNS DETECTED! Please refactor these usages.")
    else:
        logger.info("\n✅ No anti-pattern usages found in production code!")
    
    # ========================================================================
    # TEST 2: Check semantic architecture in endpoints
    # ========================================================================
    
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Checking semantic architecture in endpoints...")
    logger.info("="*80)
    
    stats = check_semantic_architecture(str(project_root))
    
    logger.info(f"\nEndpoints checked: {stats['endpoints_checked']}")
    logger.info(f"Using SEMANTIC architecture: {stats['using_semantic']}")
    logger.info(f"Using LEGACY architecture: {stats['using_legacy']}")
    
    for detail in stats['details']:
        logger.info(f"\n  {detail['status']} - {detail['file']}")
        logger.info(f"    Semantic methods: {detail['has_semantic']}")
        logger.info(f"    MedicalTranslator: {detail['has_translator']}")
    
    # ========================================================================
    # FINAL VERDICT
    # ========================================================================
    
    logger.info("\n" + "="*80)
    logger.info("FINAL VERDICT")
    logger.info("="*80)
    
    all_semantic = stats['using_semantic'] == stats['endpoints_checked']
    no_antipatterns = len(antipatterns) == 0
    
    if all_semantic and no_antipatterns:
        logger.info("\n🎉 SUCCESS! All endpoints use SEMANTIC architecture")
        logger.info("✅ No anti-patterns detected")
        logger.info("✅ Architecture is RAG-compliant")
        return 0
    else:
        logger.error("\n❌ FAILURE! Architecture issues detected:")
        if not all_semantic:
            logger.error(f"  - {stats['using_legacy']} endpoints still using legacy architecture")
        if not no_antipatterns:
            logger.error(f"  - {len(antipatterns)} anti-pattern usages found")
        return 1


if __name__ == "__main__":
    exit(main())
