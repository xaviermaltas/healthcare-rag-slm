#!/usr/bin/env python3
"""
Healthcare RAG System Verification Script
Verifies that all components are properly installed and configured
"""

import sys
import asyncio
import requests
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[0;34m",
        "SUCCESS": "\033[0;32m", 
        "WARNING": "\033[1;33m",
        "ERROR": "\033[0;31m"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')}[{status}]{reset} {message}")

def test_python_version():
    """Test Python version"""
    print_status("Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} ✓", "SUCCESS")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - requires 3.11+", "ERROR")
        return False

def test_python_packages():
    """Test required Python packages"""
    print_status("Testing Python packages...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "qdrant_client",
        "sentence_transformers",
        "transformers",
        "torch",
        "pydantic",
        "aiohttp",
        "httpx",
        "numpy",
        "pandas"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_status(f"  {package} ✓", "SUCCESS")
        except ImportError:
            print_status(f"  {package} ✗", "ERROR")
            missing_packages.append(package)
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "ERROR")
        return False
    
    print_status("All required packages installed ✓", "SUCCESS")
    return True

def test_ollama():
    """Test Ollama connection and models"""
    print_status("Testing Ollama connection...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print_status("Ollama connection ✓", "SUCCESS")
            
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            print_status(f"Available models: {', '.join(model_names)}", "INFO")
            
            # Check for required models
            required_models = ["mistral", "llama3.2"]
            missing_models = []
            
            for required_model in required_models:
                if any(required_model in model_name for model_name in model_names):
                    print_status(f"  {required_model} ✓", "SUCCESS")
                else:
                    print_status(f"  {required_model} ✗", "WARNING")
                    missing_models.append(required_model)
            
            if missing_models:
                print_status(f"Consider downloading: {', '.join(missing_models)}", "WARNING")
            
            return True
        else:
            print_status(f"Ollama HTTP error: {response.status_code}", "ERROR")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"Ollama connection failed: {e}", "ERROR")
        return False

def test_qdrant():
    """Test Qdrant connection"""
    print_status("Testing Qdrant connection...")
    
    try:
        response = requests.get("http://localhost:6333/healthz", timeout=10)
        if response.status_code == 200:
            print_status("Qdrant connection ✓", "SUCCESS")
            
            # Get collections info
            collections_response = requests.get("http://localhost:6333/collections", timeout=10)
            if collections_response.status_code == 200:
                collections = collections_response.json()
                print_status(f"Collections available: {len(collections.get('result', {}).get('collections', []))}", "INFO")
            
            return True
        else:
            print_status(f"Qdrant HTTP error: {response.status_code}", "ERROR")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"Qdrant connection failed: {e}", "ERROR")
        return False

def test_api():
    """Test Healthcare RAG API"""
    print_status("Testing Healthcare RAG API...")
    
    try:
        # Test liveness endpoint
        response = requests.get("http://localhost:8000/health/live", timeout=10)
        if response.status_code == 200:
            print_status("API liveness check ✓", "SUCCESS")
        else:
            print_status(f"API liveness check failed: {response.status_code}", "ERROR")
            return False
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health/", timeout=30)
        if response.status_code == 200:
            health_data = response.json()
            print_status("API health check ✓", "SUCCESS")
            print_status(f"Overall status: {health_data.get('status', 'unknown')}", "INFO")
            
            # Check component statuses
            components = health_data.get('components', {})
            for component, info in components.items():
                status = info.get('status', 'unknown')
                if status == 'healthy':
                    print_status(f"  {component}: {status} ✓", "SUCCESS")
                else:
                    print_status(f"  {component}: {status} ⚠", "WARNING")
        else:
            print_status(f"API health check failed: {response.status_code}", "WARNING")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_status(f"API connection failed: {e}", "ERROR")
        return False

def test_embeddings():
    """Test embeddings functionality"""
    print_status("Testing embeddings functionality...")
    
    try:
        from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
        print_status("BGE-M3 embeddings model (sentence-transformers) pot ser importat ✓", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Embeddings test failed: {e}", "ERROR")
        return False

def test_directories():
    """Test required directories exist"""
    print_status("Testing directory structure...")
    
    required_dirs = [
        "data",
        "data/raw",
        "data/processed",
        "data/embeddings",
        "data/qdrant_storage",
        "config",
        "src/main/api",
        "src/main/core",
        "src/main/infrastructure",
        "src/test",
        "deploy/compose"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print_status(f"  {dir_path} ✓", "SUCCESS")
        else:
            print_status(f"  {dir_path} ✗", "ERROR")
            all_exist = False
    
    return all_exist

def test_configuration():
    """Test configuration files"""
    print_status("Testing configuration...")
    
    config_files = [
        ".env",
        ".env.example",
        "requirements.txt",
        "deploy/compose/docker-compose.yml"
    ]
    
    all_exist = True
    for config_file in config_files:
        file_path = project_root / config_file
        if file_path.exists():
            print_status(f"  {config_file} ✓", "SUCCESS")
        else:
            print_status(f"  {config_file} ✗", "ERROR")
            all_exist = False
    
    return all_exist

def main():
    """Run all verification tests"""
    print_status("🏥 Healthcare RAG System Verification")
    print_status("=" * 40)
    
    tests = [
        ("Python Version", test_python_version),
        ("Python Packages", test_python_packages),
        ("Directory Structure", test_directories),
        ("Configuration Files", test_configuration),
        ("Ollama Service", test_ollama),
        ("Qdrant Database", test_qdrant),
        ("Healthcare RAG API", test_api),
        ("Embeddings Model", test_embeddings)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print_status(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Test {test_name} failed with exception: {e}", "ERROR")
            results.append((test_name, False))
    
    # Summary
    print_status("\n" + "=" * 40)
    print_status("VERIFICATION SUMMARY")
    print_status("=" * 40)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print_status(f"{test_name}: PASS ✓", "SUCCESS")
            passed += 1
        else:
            print_status(f"{test_name}: FAIL ✗", "ERROR")
            failed += 1
    
    print_status(f"\nTotal: {len(results)} tests")
    print_status(f"Passed: {passed}", "SUCCESS")
    print_status(f"Failed: {failed}", "ERROR" if failed > 0 else "SUCCESS")
    
    if failed == 0:
        print_status("\n🎉 All tests passed! Healthcare RAG system is ready.", "SUCCESS")
        return 0
    else:
        print_status(f"\n⚠️  {failed} test(s) failed. Please check the errors above.", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())
