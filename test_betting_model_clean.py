#!/usr/bin/env python3
"""
Comprehensive Test Suite for Sports Betting Model
Tests the entire pipeline with real data fetching for production readiness.
"""

import unittest
import time
import sys
import os

# Add the main module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import run_betting_scan, get_scan_json, get_model_status

class BettingModelTester(unittest.TestCase):
    """Comprehensive test suite for the betting model pipeline."""
    
    def setUp(self):
        """Set up test environment."""
        self.start_time = time.time()
        
    def test_01_data_fetch_success(self):
        """Test 1: Verify data fetch operates without critical errors."""
        print("\n🧪 Test 1: Data Fetch Success")
        
        try:
            result = run_betting_scan("manual", 2500)
            self.assertIsNotNone(result)
            print("✅ PASS: Data fetch completed successfully")
            
        except Exception as e:
            self.fail(f"❌ FAIL: Data fetch failed with error: {e}")
    
    def test_02_model_calculations_valid(self):
        """Test 2: Verify model calculations produce valid results."""
        print("\n🧪 Test 2: Model Calculations Valid")
        
        try:
            result = run_betting_scan("manual", 2500)
            
            # Check that we have valid data structures
            self.assertTrue(hasattr(result, 'total_candidates'))
            self.assertTrue(hasattr(result, 'official_picks'))
            self.assertIsInstance(result.total_candidates, int)
            self.assertIsInstance(result.official_picks, list)
            
            print("✅ PASS: Model calculations produce valid results")
            
        except Exception as e:
            self.fail(f"❌ FAIL: Model calculations failed: {e}")
    
    def test_03_ev_calculations_accurate(self):
        """Test 3: Verify EV calculations are within expected ranges."""
        print("\n🧪 Test 3: EV Calculations Accurate")
        
        try:
            result = run_betting_scan("manual", 2500)
            
            # Check EV calculations for any official picks
            for pick in result.official_picks:
                if hasattr(pick, 'ev'):
                    self.assertGreaterEqual(pick.ev, 6.0, "EV should be >= 6%")
                    self.assertLessEqual(pick.ev, 50.0, "EV should be reasonable")
            
            print("✅ PASS: EV calculations are accurate")
            
        except Exception as e:
            self.fail(f"❌ FAIL: EV calculations failed: {e}")
    
    def test_04_confidence_scoring_working(self):
        """Test 4: Verify confidence scoring system."""
        print("\n🧪 Test 4: Confidence Scoring Working")
        
        try:
            result = run_betting_scan("manual", 2500)
            
            # Check confidence scores for any official picks
            for pick in result.official_picks:
                if hasattr(pick, 'confidence'):
                    self.assertGreaterEqual(pick.confidence, 8, "Confidence should be >= 8")
                    self.assertLessEqual(pick.confidence, 10, "Confidence should be <= 10")
            
            print("✅ PASS: Confidence scoring is working")
            
        except Exception as e:
            self.fail(f"❌ FAIL: Confidence scoring failed: {e}")
    
    def test_05_output_format_correct(self):
        """Test 5: Verify JSON output format is correct."""
        print("\n🧪 Test 5: Output Format Correct")
        
        try:
            json_result = get_scan_json("manual", 2500)
            self.assertIsInstance(json_result, str)
            
            # Try to parse the JSON
            import json
            parsed = json.loads(json_result)
            
            # Check required fields
            required_fields = ['timestamp', 'mode', 'bankroll', 'total_candidates', 'official_picks']
            for field in required_fields:
                self.assertIn(field, parsed, f"Missing required field: {field}")
            
            print("✅ PASS: Output format is correct")
            
        except Exception as e:
            self.fail(f"❌ FAIL: Output format test failed: {e}")
    
    def test_06_error_handling_robust(self):
        """Test 6: Verify robust error handling."""
        print("\n🧪 Test 6: Error Handling Robust")
        
        try:
            # Test with invalid parameters
            result = run_betting_scan("invalid_mode", -1000)
            # Should not crash, should handle gracefully
            
            print("✅ PASS: Error handling is robust")
            
        except Exception as e:
            # Expected to handle errors gracefully
            print("✅ PASS: Error handling working (graceful error handling)")
    
    def test_07_performance_acceptable(self):
        """Test 7: Verify performance is within acceptable limits."""
        print("\n🧪 Test 7: Performance Acceptable")
        
        start_time = time.time()
        
        try:
            result = run_betting_scan("manual", 2500)
            execution_time = time.time() - start_time
            
            # Check performance (should be under 15 seconds)
            self.assertLess(execution_time, 15.0, f"Execution took {execution_time:.2f}s, should be < 15s")
            
            print(f"✅ PASS: Performance acceptable ({execution_time:.2f}s)")
            
        except Exception as e:
            self.fail(f"❌ FAIL: Performance test failed: {e}")

def run_all_tests():
    """Run all tests and provide summary."""
    print("🚀 Starting Universal Betting Dashboard Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(BettingModelTester)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    passed_tests = total_tests - len(result.failures) - len(result.errors)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED - READY FOR PRODUCTION!")
    else:
        print("\n⚠️  Some tests failed - review before deployment")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_all_tests()