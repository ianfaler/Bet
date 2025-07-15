"""
Production Readiness Testing Framework for Betting App

This package contains comprehensive tests for validating production readiness
across API integrations, data processing, performance, and security.

Test Phases:
1. API Integration Tests - The Odds API, FootyStats API, WNBA scraping
2. Data Processing Tests - Model calculations, EV formulas, Kelly staking  
3. Load and Performance Tests - Concurrent users, response times
4. End-to-End Tests - User journeys and workflows
5. Security and Compliance Tests - Data protection and regulations

Usage:
    # Run all tests
    python run_production_tests.py
    
    # Run critical tests only
    python run_production_tests.py --quick
    
    # Run individual test files
    python tests/test_api_integrations.py
    python tests/test_data_processing.py
    python tests/test_load_performance.py
"""

__version__ = "1.0.0"
__author__ = "Betting App Development Team"