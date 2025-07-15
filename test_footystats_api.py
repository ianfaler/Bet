#!/usr/bin/env python3
"""
FootyStats API Tester

This script tests various endpoint patterns to find working FootyStats API endpoints.
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
FOOTYSTATS_API_KEY = "b44de69d5777cd2c78d81d59a85d0a91154e836320016b53ecdc1f646fc95b97"

# Common endpoint patterns to test
ENDPOINT_PATTERNS = [
    # Original pattern that returned 404
    "https://api.footystats.org/leagues",
    "https://api.footystats.org/league-table",
    "https://api.footystats.org/league-matches",
    
    # Alternative patterns
    "https://api.footystats.org/v1/leagues",
    "https://api.footystats.org/v2/leagues",
    "https://footystats.org/api/leagues",
    "https://footystats.org/api/v1/leagues",
    "https://api.footystats.org/competitions",
    "https://api.footystats.org/leagues-list",
    
    # Different base URLs
    "https://footystats.com/api/leagues",
    "https://www.footystats.org/api/leagues",
    "https://app.footystats.org/api/leagues",
    
    # Test with different endpoints
    "https://api.footystats.org",
    "https://api.footystats.org/status",
    "https://api.footystats.org/health",
]

class FootyStatsAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FootyStats API Tester v1.0',
            'Accept': 'application/json'
        })
    
    def test_endpoint(self, url, params=None):
        """Test a single endpoint"""
        if params is None:
            params = {"key": FOOTYSTATS_API_KEY}
        
        try:
            print(f"Testing: {url}")
            response = self.session.get(url, params=params, timeout=10)
            
            print(f"  Status: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  SUCCESS! Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"  List length: {len(data)}")
                        if data:
                            print(f"  First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                    return True, data
                except json.JSONDecodeError:
                    print(f"  Response not JSON: {response.text[:200]}")
                    return False, response.text
            else:
                print(f"  Error: {response.text[:200]}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            return False, None
        
        print()
        return False, None
    
    def test_alternative_auth_methods(self, base_url):
        """Test different authentication methods"""
        print(f"\n=== Testing alternative auth methods for {base_url} ===")
        
        auth_methods = [
            # Query parameter
            {"key": FOOTYSTATS_API_KEY},
            {"api_key": FOOTYSTATS_API_KEY},
            {"apikey": FOOTYSTATS_API_KEY},
            {"token": FOOTYSTATS_API_KEY},
            {"access_token": FOOTYSTATS_API_KEY},
        ]
        
        for params in auth_methods:
            print(f"Trying with params: {params}")
            success, data = self.test_endpoint(base_url, params)
            if success:
                return True, data
                
        # Try with headers
        header_methods = [
            {"Authorization": f"Bearer {FOOTYSTATS_API_KEY}"},
            {"Authorization": f"Token {FOOTYSTATS_API_KEY}"},
            {"X-API-Key": FOOTYSTATS_API_KEY},
            {"X-Auth-Token": FOOTYSTATS_API_KEY},
        ]
        
        for headers in header_methods:
            print(f"Trying with headers: {headers}")
            old_headers = self.session.headers.copy()
            self.session.headers.update(headers)
            try:
                success, data = self.test_endpoint(base_url, {})
                if success:
                    return True, data
            finally:
                self.session.headers = old_headers
                
        return False, None
    
    def run_tests(self):
        """Run all tests"""
        print("🧪 FootyStats API Endpoint Tester")
        print("=" * 50)
        
        working_endpoints = []
        
        for endpoint in ENDPOINT_PATTERNS:
            success, data = self.test_endpoint(endpoint)
            if success:
                working_endpoints.append((endpoint, data))
                print(f"✅ WORKING ENDPOINT FOUND: {endpoint}")
            else:
                # Try alternative auth methods for base URLs
                if not '/' in endpoint.split('://', 1)[1].split('/', 1)[-1]:
                    alt_success, alt_data = self.test_alternative_auth_methods(endpoint)
                    if alt_success:
                        working_endpoints.append((endpoint, alt_data))
                        print(f"✅ WORKING ENDPOINT FOUND with alternative auth: {endpoint}")
            
            time.sleep(1)  # Be respectful to the API
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS")
        print("=" * 50)
        
        if working_endpoints:
            print(f"✅ Found {len(working_endpoints)} working endpoint(s):")
            for url, data in working_endpoints:
                print(f"  - {url}")
                
            # Save successful endpoint data
            with open("footystats_successful_endpoints.json", "w") as f:
                results = {
                    "timestamp": datetime.now().isoformat(),
                    "working_endpoints": [
                        {"url": url, "sample_data": str(data)[:500]} 
                        for url, data in working_endpoints
                    ]
                }
                json.dump(results, f, indent=2)
                
            print(f"\n💾 Results saved to footystats_successful_endpoints.json")
            return working_endpoints[0]  # Return first working endpoint
        else:
            print("❌ No working endpoints found")
            print("\nPossible issues:")
            print("1. API key may be invalid or expired")
            print("2. API endpoints may have changed")
            print("3. API may require different authentication method")
            print("4. API may require paid subscription for access")
            return None
        
        

if __name__ == "__main__":
    tester = FootyStatsAPITester()
    result = tester.run_tests()
    
    if result:
        print(f"\n🎉 Ready to proceed with endpoint: {result[0]}")
    else:
        print(f"\n🔧 Next steps:")
        print("1. Verify API key is still valid")
        print("2. Check FootyStats website for updated documentation")
        print("3. Contact FootyStats support for assistance")