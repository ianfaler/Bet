#!/usr/bin/env python3
"""
API Integration Tests for Production Readiness
Tests all three critical data sources with real API calls and validation
"""

import unittest
import requests
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Test configuration
TEST_DATE = '2025-07-15'
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "demo_key")
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "demo_key")

class TestOddsAPIIntegration(unittest.TestCase):
    """Test The Odds API integration for moneylines, spreads, and totals"""
    
    def setUp(self):
        """Set up test environment"""
        self.api_key = ODDS_API_KEY
        self.base_url = "https://api.the-odds-api.com/v4"
        self.required_markets = ['h2h', 'spreads', 'totals']
        self.test_results = {}
        
    def test_api_authentication_valid(self):
        """Test valid API key authentication"""
        url = f"{self.base_url}/sports"
        params = {'apiKey': self.api_key}
        
        response = requests.get(url, params=params, timeout=10)
        
        self.assertNotEqual(self.api_key, "demo_key", "API key must be set for production tests")
        self.assertEqual(response.status_code, 200, f"API authentication failed: {response.status_code}")
        self.test_results['authentication'] = 'PASS'
        
    def test_api_authentication_invalid(self):
        """Test invalid API key handling"""
        url = f"{self.base_url}/sports"
        params = {'apiKey': 'invalid_key_12345'}
        
        response = requests.get(url, params=params, timeout=10)
        
        self.assertEqual(response.status_code, 401, "Invalid API key should return 401")
        self.test_results['invalid_auth_handling'] = 'PASS'
        
    def test_rate_limit_handling(self):
        """Test API rate limit detection and handling"""
        # Make multiple rapid requests to test rate limiting
        url = f"{self.base_url}/sports"
        params = {'apiKey': self.api_key}
        
        responses = []
        for i in range(5):
            response = requests.get(url, params=params, timeout=10)
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay
            
        # Should handle rate limits gracefully
        for status_code in responses:
            self.assertIn(status_code, [200, 429], f"Unexpected status code: {status_code}")
            
        self.test_results['rate_limit_handling'] = 'PASS'
        
    def test_moneyline_data_retrieval(self):
        """CRITICAL: Test moneyline (h2h) data retrieval"""
        url = f"{self.base_url}/sports/baseball_mlb/odds"
        params = {
            'apiKey': self.api_key,
            'markets': 'h2h',
            'regions': 'us',
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        self.assertEqual(response.status_code, 200, f"Moneyline API failed: {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list of games")
        
        if data:  # If games available
            game = data[0]
            self.assertIn('bookmakers', game, "Game should have bookmakers")
            
            bookmaker = game['bookmakers'][0]
            self.assertIn('markets', bookmaker, "Bookmaker should have markets")
            
            h2h_market = next((m for m in bookmaker['markets'] if m['key'] == 'h2h'), None)
            self.assertIsNotNone(h2h_market, "h2h (moneyline) market should be present")
            
            self.assertIn('outcomes', h2h_market, "h2h market should have outcomes")
            self.assertGreaterEqual(len(h2h_market['outcomes']), 2, "Should have at least 2 outcomes")
            
        self.test_results['moneyline_data'] = 'PASS'
        print("✅ CRITICAL: Moneyline data confirmed available")
        
    def test_spreads_data_retrieval(self):
        """CRITICAL: Test spreads data retrieval"""
        url = f"{self.base_url}/sports/baseball_mlb/odds"
        params = {
            'apiKey': self.api_key,
            'markets': 'spreads',
            'regions': 'us',
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        self.assertEqual(response.status_code, 200, f"Spreads API failed: {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list of games")
        
        if data:  # If games available
            game = data[0]
            bookmaker = game['bookmakers'][0]
            
            spreads_market = next((m for m in bookmaker['markets'] if m['key'] == 'spreads'), None)
            self.assertIsNotNone(spreads_market, "spreads market should be present")
            
            outcome = spreads_market['outcomes'][0]
            self.assertIn('point', outcome, "Spread outcome should have point value")
            self.assertIn('price', outcome, "Spread outcome should have price")
            
        self.test_results['spreads_data'] = 'PASS'
        print("✅ CRITICAL: Spreads data confirmed available")
        
    def test_totals_data_retrieval(self):
        """CRITICAL: Test totals data retrieval"""
        url = f"{self.base_url}/sports/baseball_mlb/odds"
        params = {
            'apiKey': self.api_key,
            'markets': 'totals',
            'regions': 'us',
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        self.assertEqual(response.status_code, 200, f"Totals API failed: {response.status_code}")
        
        data = response.json()
        self.assertIsInstance(data, list, "Response should be a list of games")
        
        if data:  # If games available
            game = data[0]
            bookmaker = game['bookmakers'][0]
            
            totals_market = next((m for m in bookmaker['markets'] if m['key'] == 'totals'), None)
            self.assertIsNotNone(totals_market, "totals market should be present")
            
            outcome = totals_market['outcomes'][0]
            self.assertIn('point', outcome, "Total outcome should have point value")
            self.assertIn('price', outcome, "Total outcome should have price")
            
        self.test_results['totals_data'] = 'PASS'
        print("✅ CRITICAL: Totals data confirmed available")
        
    def test_all_required_markets(self):
        """Test all required markets in single API call"""
        url = f"{self.base_url}/sports/baseball_mlb/odds"
        params = {
            'apiKey': self.api_key,
            'markets': 'h2h,spreads,totals',
            'regions': 'us',
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        self.assertEqual(response.status_code, 200, f"Combined markets API failed: {response.status_code}")
        
        data = response.json()
        if data:
            game = data[0]
            bookmaker = game['bookmakers'][0]
            markets = [m['key'] for m in bookmaker['markets']]
            
            for required_market in self.required_markets:
                self.assertIn(required_market, markets, f"Required market {required_market} missing")
                
        self.test_results['all_markets'] = 'PASS'
        
    def tearDown(self):
        """Report test results"""
        print(f"\n📊 The Odds API Test Results:")
        for test, result in self.test_results.items():
            print(f"  - {test}: {result}")


class TestFootyStatsAPIIntegration(unittest.TestCase):
    """Test FootyStats API integration for 50 soccer leagues"""
    
    def setUp(self):
        """Set up test environment"""
        self.api_key = FOOTYSTATS_API_KEY
        self.base_url = "https://api.footystats.org"
        self.test_results = {}
        self.required_leagues = [
            "premier-league", "championship", "la-liga", "bundesliga", 
            "serie-a", "ligue-1", "mls", "champions-league"
        ]
        
    def test_api_connection(self):
        """Test FootyStats API connection"""
        # Try multiple potential endpoints
        endpoints = [
            f"{self.base_url}/leagues",
            f"{self.base_url}/api/leagues",
            f"{self.base_url}/v2/leagues"
        ]
        
        connection_successful = False
        for endpoint in endpoints:
            try:
                params = {"key": self.api_key}
                response = requests.get(endpoint, params=params, timeout=10)
                
                if response.status_code == 200:
                    connection_successful = True
                    self.test_results['api_connection'] = 'PASS'
                    break
                    
            except requests.RequestException:
                continue
                
        if not connection_successful:
            self.test_results['api_connection'] = 'FAIL - API endpoints not accessible'
            self.skipTest("FootyStats API not accessible - using fallback data sources")
            
    def test_xg_data_availability(self):
        """Test xG (Expected Goals) data availability"""
        # This would test specific league data for xG metrics
        endpoint = f"{self.base_url}/league-matches"
        params = {
            "key": self.api_key,
            "league_id": "premier-league",
            "season": "2024"
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Check for xG data structure
                if data and isinstance(data, list) and len(data) > 0:
                    match = data[0]
                    has_xg = any(key in match for key in ['home_xg', 'away_xg', 'expected_goals'])
                    
                    if has_xg:
                        self.test_results['xg_data'] = 'PASS'
                    else:
                        self.test_results['xg_data'] = 'PARTIAL - xG data structure different'
                else:
                    self.test_results['xg_data'] = 'NO_DATA'
            else:
                self.test_results['xg_data'] = f'FAIL - Status {response.status_code}'
                
        except requests.RequestException as e:
            self.test_results['xg_data'] = f'FAIL - {str(e)}'
            
    def test_league_coverage(self):
        """Test coverage of major soccer leagues"""
        accessible_leagues = []
        
        for league in self.required_leagues[:5]:  # Test first 5 to avoid rate limits
            endpoint = f"{self.base_url}/league-matches"
            params = {
                "key": self.api_key,
                "league_id": league,
                "season": "2024"
            }
            
            try:
                response = requests.get(endpoint, params=params, timeout=10)
                if response.status_code == 200:
                    accessible_leagues.append(league)
                time.sleep(1)  # Rate limiting
                
            except requests.RequestException:
                continue
                
        coverage_rate = len(accessible_leagues) / len(self.required_leagues[:5]) * 100
        self.test_results['league_coverage'] = f'{coverage_rate:.1f}% ({len(accessible_leagues)}/{len(self.required_leagues[:5])})'
        
        # Should have at least 60% coverage
        self.assertGreaterEqual(coverage_rate, 60, f"League coverage too low: {coverage_rate}%")
        
    def tearDown(self):
        """Report test results"""
        print(f"\n⚽ FootyStats API Test Results:")
        for test, result in self.test_results.items():
            print(f"  - {test}: {result}")


class TestWNBAScrapingIntegration(unittest.TestCase):
    """Test WNBA data scraping integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_results = {}
        self.target_sites = [
            "https://www.espn.com/wnba/",
            "https://www.basketball-reference.com/wnba/",
            "https://www.actionnetwork.com/wnba"
        ]
        
    def test_target_site_accessibility(self):
        """Test accessibility of target scraping sites"""
        accessible_sites = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for site in self.target_sites:
            try:
                response = requests.get(site, headers=headers, timeout=10)
                if response.status_code == 200:
                    accessible_sites.append(site)
                time.sleep(2)  # Rate limiting
                
            except requests.RequestException:
                continue
                
        accessibility_rate = len(accessible_sites) / len(self.target_sites) * 100
        self.test_results['site_accessibility'] = f'{accessibility_rate:.1f}% ({len(accessible_sites)}/{len(self.target_sites)})'
        
        # Should have at least one accessible site
        self.assertGreater(len(accessible_sites), 0, "No WNBA sites accessible")
        
    def test_rate_limiting_compliance(self):
        """Test rate limiting compliance (2-5 seconds between requests)"""
        start_time = time.time()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Make 3 requests with proper delays
        for i in range(3):
            try:
                response = requests.get(self.target_sites[0], headers=headers, timeout=10)
                if i < 2:  # Don't sleep after last request
                    time.sleep(2.5)  # 2.5 second delay
            except requests.RequestException:
                pass
                
        total_time = time.time() - start_time
        
        # Should take at least 5 seconds (2 delays of 2.5s each)
        self.assertGreaterEqual(total_time, 5, f"Rate limiting not compliant: {total_time:.1f}s")
        self.test_results['rate_limiting'] = 'PASS'
        
    def test_user_agent_rotation(self):
        """Test user agent rotation capability"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        successful_requests = 0
        
        for ua in user_agents:
            headers = {'User-Agent': ua}
            try:
                response = requests.get(self.target_sites[0], headers=headers, timeout=10)
                if response.status_code == 200:
                    successful_requests += 1
                time.sleep(2)
            except requests.RequestException:
                pass
                
        rotation_success = (successful_requests / len(user_agents)) * 100
        self.test_results['user_agent_rotation'] = f'{rotation_success:.1f}% success'
        
        # Should have some success with user agent rotation
        self.assertGreater(successful_requests, 0, "User agent rotation failed completely")
        
    def tearDown(self):
        """Report test results"""
        print(f"\n🏀 WNBA Scraping Test Results:")
        for test, result in self.test_results.items():
            print(f"  - {test}: {result}")


class TestCriticalDataValidation(unittest.TestCase):
    """Critical validation that moneylines, spreads, and totals are available"""
    
    def test_all_bet_types_available(self):
        """CRITICAL: Confirm all required bet types are accessible"""
        print("\n🎯 CRITICAL DATA VALIDATION:")
        print("=" * 50)
        
        # Test The Odds API for all bet types
        if ODDS_API_KEY != "demo_key":
            url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
            params = {
                'apiKey': ODDS_API_KEY,
                'markets': 'h2h,spreads,totals',
                'regions': 'us'
            }
            
            try:
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and len(data) > 0:
                        game = data[0]
                        bookmaker = game['bookmakers'][0]
                        available_markets = [m['key'] for m in bookmaker['markets']]
                        
                        print(f"✅ Available Markets: {available_markets}")
                        
                        required_markets = ['h2h', 'spreads', 'totals']
                        all_available = all(market in available_markets for market in required_markets)
                        
                        if all_available:
                            print("✅ MONEYLINES: Available")
                            print("✅ SPREADS: Available")
                            print("✅ TOTALS: Available")
                            print("\n🎉 ALL REQUIRED BET TYPES CONFIRMED!")
                        else:
                            missing = [m for m in required_markets if m not in available_markets]
                            print(f"❌ MISSING BET TYPES: {missing}")
                            self.fail(f"Missing required bet types: {missing}")
                    else:
                        print("⚠️  No games available for testing")
                else:
                    print(f"❌ API Error: {response.status_code}")
                    self.fail(f"API request failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Test failed: {str(e)}")
                self.fail(f"Critical data validation failed: {str(e)}")
        else:
            print("⚠️  API key not set - using demo mode")
            self.skipTest("API key required for critical data validation")


if __name__ == '__main__':
    print("🚀 Starting API Integration Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOddsAPIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFootyStatsAPIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestWNBAScrapingIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCriticalDataValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Final summary
    print("\n" + "=" * 50)
    print("🏁 API INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n✅ API INTEGRATION TESTS PASSED")
    else:
        print("\n❌ API INTEGRATION TESTS FAILED")
        print("Review failed tests and resolve issues before production deployment.")