"""
Test the improved fact-check formatting
"""
import requests
import json
import time

# Test contradictory headlines
headlines = [
    "Apple stock hits all-time high on strong iPhone sales",
    "Apple shares plummet as iPhone sales disappoint",
    "Tech sector shows mixed performance today"
]

print("=" * 70)
print("TESTING IMPROVED FACT-CHECK FORMATTING")
print("=" * 70)
print("\nTest Headlines:")
for i, h in enumerate(headlines, 1):
    print(f"  {i}. {h}")

print("\n" + "=" * 70)
print("Sending request to fact-check agent...")
print("=" * 70)

try:
    response = requests.post(
        "http://localhost:8004/run",
        json={"headlines": headlines},
        timeout=45
    )
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Response received successfully!")
        print(f"\nStatus: {data.get('status')}")
        print(f"Headlines Analyzed: {data.get('headlines_analyzed')}")
        
        print("\n" + "=" * 70)
        print("FORMATTED ANALYSIS (No markdown symbols):")
        print("=" * 70)
        print(data.get('analysis', 'N/A'))
        print("\n" + "=" * 70)
        
        # Check for markdown symbols
        analysis_text = data.get('analysis', '')
        has_markdown = any(symbol in analysis_text for symbol in ['**', '##', '###', '***', '___'])
        
        if has_markdown:
            print("\n⚠️  Warning: Some markdown symbols still present")
        else:
            print("\n✅ SUCCESS: Clean formatting without markdown symbols!")
    else:
        print(f"\n❌ Error: HTTP {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("\n⏱️  Request timed out. The agent may still be processing...")
except Exception as e:
    print(f"\n❌ Error: {e}")
