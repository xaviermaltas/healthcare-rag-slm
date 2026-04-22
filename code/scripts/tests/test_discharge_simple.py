#!/usr/bin/env python3
"""
Simple test for discharge summary endpoint with shorter timeout
"""

import requests
import json

API_URL = "http://localhost:8000"
ENDPOINT = f"{API_URL}/generate/discharge-summary"

# Very simple case
request_data = {
    "patient_context": "Home 65 anys, HTA",
    "admission_reason": "Dolor toràcic",
    "procedures": ["ECG"],
    "current_medications": ["AAS 100mg"],
    "language": "es",
    "specialty": "Cardiologia"
}

print("📤 Sending simple request...")
print(json.dumps(request_data, indent=2))

try:
    response = requests.post(
        ENDPOINT,
        json=request_data,
        headers={"Content-Type": "application/json"},
        timeout=120  # 2 minutes
    )
    
    print(f"\n✅ Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📄 SUMMARY (first 1000 chars):")
        print("-" * 80)
        print(result['summary'][:1000])
        print("-" * 80)
        
        print(f"\n📊 Protocols retrieved: {len(result.get('sources', []))}")
        for source in result.get('sources', []):
            print(f"  - {source['title']} (score: {source['score']:.4f})")
        
        print(f"\n⏱️  Generation time: {result['generation_metadata']['generation_time_seconds']:.2f}s")
    else:
        print(f"\n❌ ERROR:")
        print(response.text)

except requests.exceptions.Timeout:
    print("\n❌ Timeout after 120s")
except Exception as e:
    print(f"\n❌ Error: {e}")
