#!/usr/bin/env python3
"""Mini Token Test - Single Query Comparison with Logging"""
import json, time, requests, os
from datetime import datetime

API_KEY = "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"
QUERY = "I want to buy running shoes under $150"

# Setup logging
LOG_DIR = "tests/token_comparison/test_logs"
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def test_approach(search_mode=None, response_mode="full"):
    url = "http://localhost:8000/api/v1/search"
    
    if search_mode is None:
        # Use GET request for default search mode
        params = {"query": QUERY, "limit": 3, "api_key": API_KEY}
        if response_mode != "full":
            params["response_mode"] = response_mode
        
        search_url = f"{url}?" + "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
        
        start = time.time()
        response = requests.get(url, params=params)
        time_ms = int((time.time() - start) * 1000)
    else:
        # Use POST request for explicit search modes
        payload = {"query": QUERY, "search_mode": search_mode, "response_mode": response_mode, "limit": 3}
        headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
        
        search_url = f"{url}?query={requests.utils.quote(QUERY)}&search_mode={search_mode}&response_mode={response_mode}&limit=3&api_key={API_KEY}"
        
        start = time.time()
        response = requests.post(url, json=payload, headers=headers)
        time_ms = int((time.time() - start) * 1000)
    
    if response.status_code == 200:
        data = response.json()
        tokens = len(json.dumps(data)) // 4
        service = data["results"][0]["service"]["name"] if data.get("results") else "None"
        return tokens, time_ms, service, data, search_url
    return 0, time_ms, "Error", {}, search_url, search_url

print("🥾 MINI TOKEN TEST")
print("=" * 50)
print(f"Query: '{QUERY}'")
print()

# Test approaches - show default vs optimized tools approaches
approaches = [
    ("Default", None, "full"),
    ("Tools Full", "tools_only", "full"),
    ("Tools Compact", "tools_only", "compact"), 
    ("Tools Minimal", "tools_only", "minimal")
]
results, detailed_results = [], {}

for name, search_mode, response_mode in approaches:
    tokens, time_ms, service, raw_data, search_url = test_approach(search_mode, response_mode)
    results.append((name, tokens, time_ms, service))
    detailed_results[name] = {
        "tokens": tokens, 
        "response_time_ms": time_ms, 
        "service_found": service,
        "search_url": search_url,
        "search_mode": search_mode if search_mode is not None else "default",
        "response_mode": response_mode,
        "correct_service": service == "ShoesAgent"
    }
    
    # Add visual indicator for correct/incorrect service
    indicator = "✅" if service == "ShoesAgent" else "❌" 
    print(f"{name:<25} {tokens:>5} tokens {time_ms:>4}ms → {service} {indicator}")

print("\n" + "=" * 60)
# Find best among working approaches (all should work now)
working_results = [(name, tokens, time_ms, service) for name, tokens, time_ms, service in results if "ShoesAgent" in service]
best = min(working_results, key=lambda x: x[1]) if working_results else results[0]
default_result = results[0]  # First result is default
tools_full = next((r for r in results if "Tools Full" in r[0]), None)

if tools_full and working_results:
    savings_vs_full = ((tools_full[1] - best[1]) / tools_full[1] * 100) if tools_full[1] > 0 else 0
    print(f"🏆 Most Efficient: {best[0]} ({best[1]} tokens)")
    print(f"💰 Token Savings vs Tools Full: {savings_vs_full:.1f}%")
    if default_result[3] == "ShoesAgent":
        print(f"✅ Default Search: Correctly finds {default_result[3]} ({default_result[1]} tokens)")
    else:
        print(f"⚠️  Default Search: Found {default_result[3]} instead of ShoesAgent")
else:
    baseline = results[0][1]
    savings = ((baseline - best[1]) / baseline * 100) if baseline > 0 and best[1] > 0 else 0
    print(f"🏆 Most Efficient: {best[0]} ({best[1]} tokens)")
    if savings > 0:
        print(f"💰 Token Savings: {savings:.1f}% vs default")
    if default_result[3] == "ShoesAgent":
        print(f"✅ Default Search: Correctly finds {default_result[3]}")
    else:
        print(f"⚠️  Default Search: Found {default_result[3]} instead of ShoesAgent")
print("✅ Test Complete!")

# Save results to logs
log_file = f"{LOG_DIR}/mini_token_test_{timestamp}.log"
json_file = f"{LOG_DIR}/mini_token_test_{timestamp}_results.json"

with open(log_file, 'w') as f:
    f.write(f"Mini Token Test - {datetime.now()}\nQuery: {QUERY}\n\nResults:\n")
    for name, tokens, time_ms, service in results:
        search_url = detailed_results[name]["search_url"]
        correct = "✅ CORRECT" if service == "ShoesAgent" else "❌ WRONG SERVICE"
        f.write(f"{name}: {tokens} tokens, {time_ms}ms, {service} {correct}\n")
        f.write(f"  URL: {search_url}\n\n")
    
    if working_results:
        f.write(f"Best Working Approach: {best[0]} ({best[1]} tokens)\n")
        if default_result[3] == "ShoesAgent":
            f.write(f"Default Search: Successfully finds {default_result[3]} ({default_result[1]} tokens)\n")
        else:
            f.write(f"Default Search Issue: Returns {default_result[3]} instead of ShoesAgent\n")
    else:
        f.write(f"Best: {best[0]} ({best[1]} tokens)\n")

with open(json_file, 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "query": QUERY,
        "results": detailed_results,
        "analysis": {
            "default_approach": {
                "name": results[0][0],
                "service_found": results[0][3],
                "correct_service": results[0][3] == "ShoesAgent",
                "status": "Correct service found" if results[0][3] == "ShoesAgent" else "Wrong service found"
            },
            "best_approach": best[0] if working_results else "None",
            "token_optimization": f"{savings_vs_full:.1f}% reduction vs Tools Full" if 'savings_vs_full' in locals() else "N/A"
        }
    }, f, indent=2)

print(f"\n📁 Results saved to:")
print(f"   Log: {log_file}")
print(f"   JSON: {json_file}")
