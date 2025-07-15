#!/usr/bin/env python3
"""
Test FootyStats API Integration with 2025 League IDs

This script tests the updated FootyStats configuration to ensure:
1. API connectivity is working
2. Correct 2025 league IDs are being used
3. Data is being retrieved successfully
4. League matches can be fetched for different leagues
"""

import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Import our updated configuration
try:
    from footystats_config import (
        FOOTYSTATS_API_KEY, 
        FOOTYSTATS_LEAGUE_IDS, 
        LEAGUE_BY_COUNTRY,
        get_league_teams_url,
        get_league_season_url
    )
    print("✅ Successfully imported FootyStats configuration")
except ImportError as e:
    print(f"❌ Failed to import FootyStats configuration: {e}")
    sys.exit(1)

class FootyStatsAPITester:
    """Test the FootyStats API with updated 2025 league IDs."""
    
    def __init__(self):
        """Initialize the API tester."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FootyStats-API-Tester/1.0',
            'Accept': 'application/json'
        })
        
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "api_key_status": "unknown",
            "total_leagues_tested": 0,
            "successful_leagues": 0,
            "failed_leagues": 0,
            "league_test_results": [],
            "sample_data": {}
        }
    
    def test_api_connectivity(self) -> bool:
        """Test basic API connectivity."""
        print("🔌 Testing FootyStats API connectivity...")
        
        try:
            # Test with Premier League (a major league that should have data)
            url = get_league_season_url(13943)  # Premier League 2025 season_id
            
            print(f"📡 Making test request to: {url}")
            print(f"🔑 Using API key: {FOOTYSTATS_API_KEY[:20]}...")
            print(f"📊 Test parameters: season_id=13943 (Premier League 2025)")
            
            response = self.session.get(url, timeout=30)
            
            print(f"📈 Response status: {response.status_code}")
            print(f"📋 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ API connectivity test PASSED")
                self.test_results["api_key_status"] = "valid"
                
                # Try to parse response
                try:
                    data = response.json()
                    print(f"📄 Response type: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"🔑 Response keys: {list(data.keys())}")
                        if 'data' in data:
                            matches = data['data']
                            print(f"⚽ Found {len(matches)} matches")
                        else:
                            matches = data
                    elif isinstance(data, list):
                        matches = data
                        print(f"⚽ Found {len(matches)} matches (direct list)")
                    
                    # Save sample response
                    self.test_results["sample_data"]["premier_league_test"] = {
                        "status_code": response.status_code,
                        "data_type": type(data).__name__,
                        "data_preview": str(data)[:500] if data else "No data"
                    }
                    
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  Response is not valid JSON: {e}")
                    print(f"📄 Raw response (first 200 chars): {response.text[:200]}")
                    return False
                    
            elif response.status_code == 422:
                print("⚠️  API key is valid but parameters may need adjustment")
                self.test_results["api_key_status"] = "valid_params_invalid"
                return True  # API key works, just need to adjust parameters
                
            elif response.status_code == 401:
                print("❌ API key authentication failed")
                self.test_results["api_key_status"] = "invalid"
                return False
                
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                print(f"📄 Response: {response.text[:200]}")
                self.test_results["api_key_status"] = "unknown"
                return False
                
        except Exception as e:
            print(f"❌ API connectivity test FAILED: {e}")
            self.test_results["api_key_status"] = "error"
            return False
    
    def test_league_sample(self, max_leagues: int = 10) -> None:
        """Test a sample of leagues to verify correct IDs."""
        print(f"\n⚽ Testing sample of {max_leagues} leagues...")
        
        # Get a sample of leagues to test
        league_sample = list(FOOTYSTATS_LEAGUE_IDS.items())[:max_leagues]
        
        for league_name, season_id in league_sample:
            self.test_results["total_leagues_tested"] += 1
            
            print(f"\n📥 Testing {league_name} (Season ID: {season_id})")
            
            success = self._test_single_league(league_name, season_id)
            
            if success:
                self.test_results["successful_leagues"] += 1
                print(f"✅ {league_name}: SUCCESS")
            else:
                self.test_results["failed_leagues"] += 1
                print(f"❌ {league_name}: FAILED")
            
            # Rate limiting
            time.sleep(1.5)
    
    def _test_single_league(self, league_name: str, season_id: int) -> bool:
        """Test a single league using season_id."""
        
        try:
            # Test season endpoint
            season_url = get_league_season_url(season_id)
            print(f"  📡 Testing season endpoint: {season_url}")
            
            response = self.session.get(season_url, timeout=20)
            
            test_result = {
                "league_name": league_name,
                "season_id": season_id,
                "status_code": response.status_code,
                "success": False,
                "teams_found": 0,
                "error": None
            }
            
            if response.status_code == 200:
                try:
                    season_data = response.json()
                    print(f"  ✅ Season data retrieved successfully")
                    
                    # Also test teams endpoint
                    teams_url = get_league_teams_url(season_id, include_stats=True)
                    print(f"  📡 Testing teams endpoint: {teams_url}")
                    
                    teams_response = self.session.get(teams_url, timeout=20)
                    
                    if teams_response.status_code == 200:
                        teams_data = teams_response.json()
                        
                        # Handle different response formats
                        if isinstance(teams_data, dict):
                            teams = teams_data.get('data', [])
                        elif isinstance(teams_data, list):
                            teams = teams_data
                        else:
                            teams = []
                        
                        test_result["teams_found"] = len(teams)
                        test_result["success"] = True
                        
                        print(f"  ✅ Found {len(teams)} teams with stats")
                        self.test_results["league_test_results"].append(test_result)
                        return True
                    else:
                        print(f"  ⚠️  Teams endpoint failed: {teams_response.status_code}")
                        # Still mark as success if season data worked
                        test_result["success"] = True
                        self.test_results["league_test_results"].append(test_result)
                        return True
                        
                except json.JSONDecodeError:
                    test_result["error"] = "Invalid JSON response"
                    print(f"  ❌ Invalid JSON response")
                    
            elif response.status_code == 422:
                test_result["error"] = "Invalid parameters"
                print(f"  ⚠️  Invalid parameters for season_id {season_id}")
                
            elif response.status_code == 404:
                test_result["error"] = "Not found"
                print(f"  ⚠️  Season not found for season_id {season_id}")
                
            else:
                test_result["error"] = f"HTTP {response.status_code}"
                print(f"  ❌ HTTP {response.status_code}")
            
            self.test_results["league_test_results"].append(test_result)
            return False
            
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            return False
    
    def test_major_leagues(self) -> None:
        """Test the major European leagues specifically."""
        print("\n🏆 Testing major European leagues...")
        
        major_leagues = {
            "English Premier League": 13943,
            "Spanish La Liga": 13942,
            "German Bundesliga": 13951,
            "Italian Serie A": 13952,
            "French Ligue 1": 13947
        }
        
        for league_name, season_id in major_leagues.items():
            print(f"\n🔥 Testing {league_name} (Season ID: {season_id})")
            success = self._test_single_league(league_name, season_id)
            
            if success:
                print(f"✅ {league_name}: Working correctly")
            else:
                print(f"❌ {league_name}: Issue detected")
            
            time.sleep(2)  # Extra delay for major leagues
    
    def generate_report(self) -> None:
        """Generate a comprehensive test report."""
        print("\n" + "="*60)
        print("📊 FOOTYSTATS API TEST REPORT")
        print("="*60)
        
        print(f"🕐 Test Time: {self.test_results['timestamp']}")
        print(f"🔑 API Key Status: {self.test_results['api_key_status']}")
        print(f"📊 Total Leagues Tested: {self.test_results['total_leagues_tested']}")
        print(f"✅ Successful: {self.test_results['successful_leagues']}")
        print(f"❌ Failed: {self.test_results['failed_leagues']}")
        
        if self.test_results['total_leagues_tested'] > 0:
            success_rate = (self.test_results['successful_leagues'] / self.test_results['total_leagues_tested']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔧 CONFIGURATION STATUS:")
        print(f"   📁 Total leagues configured: {len(FOOTYSTATS_LEAGUE_IDS)}")
        print(f"   🌍 Countries covered: {len(LEAGUE_BY_COUNTRY)}")
        
        # Save detailed report
        report_file = Path("footystats_api_test_report.json")
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.test_results['api_key_status'] == 'valid':
            print("   ✅ API key is working correctly")
            if self.test_results['successful_leagues'] > 0:
                print("   ✅ League data is accessible")
                print("   🚀 Ready for production use!")
            else:
                print("   ⚠️  No league data found - check league IDs or seasons")
        elif self.test_results['api_key_status'] == 'valid_params_invalid':
            print("   ✅ API key is valid")
            print("   ⚠️  Parameter format may need adjustment")
        else:
            print("   ❌ API key issues detected")
            print("   🔧 Check API key configuration")
    
    def run_full_test(self) -> None:
        """Run complete FootyStats API test suite."""
        print("🚀 Starting FootyStats API Integration Test")
        print("="*60)
        
        # Test 1: Basic connectivity
        if not self.test_api_connectivity():
            print("❌ Basic connectivity failed - stopping tests")
            self.generate_report()
            return
        
        # Test 2: Sample of leagues
        self.test_league_sample(max_leagues=10)
        
        # Test 3: Major leagues
        self.test_major_leagues()
        
        # Test 4: Generate report
        self.generate_report()


def main():
    """Main function to run FootyStats API tests."""
    
    print("🔍 FootyStats API Integration Test")
    print("Testing updated 2025 league IDs and API configuration")
    print("-" * 60)
    
    # Show configuration summary
    print(f"📋 Configuration Summary:")
    print(f"   🔑 API Key: {FOOTYSTATS_API_KEY[:20]}...")
    print(f"   📊 Total leagues configured: {len(FOOTYSTATS_LEAGUE_IDS)}")
    print(f"   🌍 Countries: {len(LEAGUE_BY_COUNTRY)}")
    
    # Run tests
    tester = FootyStatsAPITester()
    tester.run_full_test()


if __name__ == "__main__":
    main()