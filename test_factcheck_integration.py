"""
Test the complete 5-service system with fact-check integration
"""
import requests
import json

url = "http://localhost:8000/run"
payload = {"query": "artificial intelligence"}

print("🔍 Testing complete system with fact-check integration...")
print(f"Query: {payload['query']}\n")

try:
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    
    data = response.json()
    
    print("✅ Response received successfully!\n")
    print("=" * 60)
    
    # Check fact-check integration
    if "factcheck_analysis" in data:
        fc = data["factcheck_analysis"]
        print("📋 FACT-CHECK ANALYSIS:")
        print(f"  Status: {fc.get('status')}")
        print(f"  Headlines Analyzed: {fc.get('headlines_analyzed')}")
        print(f"\n  Analysis:\n{fc.get('analysis', 'N/A')[:800]}...")
        print("=" * 60)
    else:
        print("⚠️  No fact-check analysis found in response")
    
    # Show summary
    if "summary" in data:
        summary = data["summary"]
        if "fact_check" in summary:
            print("\n📊 FACT-CHECK IN SUMMARY:")
            print(summary["fact_check"][:500])
            print("=" * 60)
    
    print(f"\n✅ Complete! Response size: {len(json.dumps(data))} bytes")
    print(f"   Sections: {list(data.keys())}")
    
except requests.exceptions.Timeout:
    print("❌ Request timed out after 120 seconds")
except Exception as e:
    print(f"❌ Error: {e}")
