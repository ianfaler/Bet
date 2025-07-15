# Production Readiness Testing Framework

## Overview

This comprehensive testing framework validates your betting app's production readiness across 5 critical phases:

1. **API Integration Tests** - Validates The Odds API, FootyStats API, and WNBA scraping
2. **Data Processing Tests** - Tests model calculations, EV formulas, and Kelly staking
3. **End-to-End Tests** - User journey and workflow validation
4. **Load & Performance Tests** - Concurrent users and response time testing
5. **Security & Compliance Tests** - Data protection and regulatory compliance

## 🚀 Quick Start

### 1. Set Up Environment

```bash
# Install test dependencies
python run_production_tests.py --setup

# Set required API keys (replace with your actual keys)
export ODDS_API_KEY="your_odds_api_key_here"
export FOOTYSTATS_API_KEY="your_footystats_api_key_here"
```

### 2. Run All Tests

```bash
# Run complete test suite
python run_production_tests.py

# Run only critical tests (faster)
python run_production_tests.py --quick

# Run specific phases
python run_production_tests.py --phases "API Integration Tests" "Data Processing Tests"
```

### 3. Review Results

The framework generates:
- Console output with real-time results
- Detailed JSON report with timestamps
- Pass/fail status for each test
- Production readiness recommendation

## 📋 Test Phases

### Phase 1: API Integration Tests (`test_api_integrations.py`)

**Critical Tests:**
- ✅ The Odds API authentication and rate limiting
- ✅ **Moneyline data retrieval** (h2h markets)
- ✅ **Spreads data retrieval** (point spreads)
- ✅ **Totals data retrieval** (over/under)
- ✅ FootyStats API connection (50 leagues)
- ✅ WNBA scraping with proper rate limiting

**Key Validations:**
- Real API data only (no dummy data)
- All bet types confirmed available
- Rate limits respected
- Error handling robust

### Phase 2: Data Processing Tests (`test_data_processing.py`)

**Model Validation:**
- ✅ Poisson model accuracy (~0.55 probability)
- ✅ Monte Carlo simulation variance <0.02
- ✅ EV calculation formula correctness
- ✅ Confidence scoring with RLM (+2 boost)
- ✅ Kelly criterion staking ($2500 bankroll)

**Filtering Tests:**
- ✅ EV threshold ≥3% applied
- ✅ Confidence threshold ≥7/10 applied
- ✅ Risk management limits enforced

### Phase 3: Load & Performance Tests (`test_load_performance.py`)

**Performance Targets:**
- ✅ Response time <2s for individual requests
- ✅ Full pipeline <10s for complete processing
- ✅ 100-500 concurrent users supported
- ✅ Memory usage monitoring (no leaks)

**Scalability Tests:**
- ✅ Cache performance improvements
- ✅ API rate limit distribution
- ✅ Stress testing under load

## 🔧 Individual Test Execution

### Run API Tests Only

```bash
python tests/test_api_integrations.py
```

Expected output:
```
🚀 Starting API Integration Tests
================================

🎯 CRITICAL DATA VALIDATION:
✅ Available Markets: ['h2h', 'spreads', 'totals']
✅ MONEYLINES: Available
✅ SPREADS: Available  
✅ TOTALS: Available
🎉 ALL REQUIRED BET TYPES CONFIRMED!
```

### Run Data Processing Tests Only

```bash
python tests/test_data_processing.py
```

### Run Performance Tests Only

```bash
# Note: Requires app to be running locally
python app.py &  # Start your app first
python tests/test_load_performance.py
```

## 📊 Success Criteria

### Critical Requirements (Must Pass)

1. **✅ Real Data Only**: Zero dummy/mock data in production tests
2. **✅ Complete Odds Coverage**: Moneylines, spreads, totals confirmed
3. **✅ API Reliability**: <1% failure rate across all integrations
4. **✅ Model Accuracy**: EV calculations and Kelly staking working
5. **✅ Performance Standards**: <2s response time, <10s full pipeline

### Performance Targets

- **Response Time**: <2s for bet recommendations
- **Full Pipeline**: <10s for complete data fetch + processing
- **Concurrent Users**: 100-500 users supported
- **Success Rate**: >80% under load
- **Memory Usage**: No significant leaks

### Data Validation

- **The Odds API**: h2h, spreads, totals markets accessible
- **FootyStats API**: 47/50+ leagues available (94%+ coverage)
- **WNBA Scraping**: Rate limiting compliant, no 429 errors

## 🚨 Troubleshooting

### Common Issues

**API Key Errors:**
```bash
# Verify API keys are set
echo $ODDS_API_KEY
echo $FOOTYSTATS_API_KEY

# Set them if missing
export ODDS_API_KEY="your_key_here"
```

**Missing Dependencies:**
```bash
pip install -r requirements.txt
pip install pytest pytest-cov locust psutil
```

**App Not Running (Performance Tests):**
```bash
# Start your betting app first
python app.py &
# Then run performance tests
python tests/test_load_performance.py
```

**Rate Limiting Issues:**
- FootyStats API may have changed endpoints
- Reduce test frequency in `test_api_integrations.py`
- Check API documentation for current limits

### Expected Test Output

**Successful Run:**
```
🏁 PRODUCTION READINESS TEST SUMMARY
====================================
🎉 STATUS: PRODUCTION READY ✅
📊 Test Duration: 45.2s
📈 Overall Success Rate: 94.2%
🧪 Total Tests: 52

📋 PHASE RESULTS:
• API Integration Tests: ✅ PASS (CRITICAL)
• Data Processing Tests: ✅ PASS (CRITICAL)  
• Load and Performance Tests: ✅ PASS

🔍 DATA VALIDATION:
• moneylines: ✅ Confirmed
• spreads: ✅ Confirmed
• totals: ✅ Confirmed
• real_data_only: ✅ No dummy data

💡 RECOMMENDATIONS:
• 🎉 All tests passed! App is production ready.
```

## 📁 File Structure

```
tests/
├── README.md                    # This file
├── test_api_integrations.py     # API testing (Phase 1)
├── test_data_processing.py      # Model testing (Phase 2)
├── test_load_performance.py     # Performance testing (Phase 4)
└── __init__.py                  # Package initialization

run_production_tests.py          # Master test runner
PRODUCTION_READINESS_TESTING_CHECKLIST.md  # Detailed checklist
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Production Readiness Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      ODDS_API_KEY: ${{ secrets.ODDS_API_KEY }}
      FOOTYSTATS_API_KEY: ${{ secrets.FOOTYSTATS_API_KEY }}
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: python run_production_tests.py --setup
      - name: Run production tests
        run: python run_production_tests.py --quick
```

## 📈 Continuous Monitoring

### Daily Health Checks

```bash
# Create a daily cron job
0 9 * * * cd /path/to/betting-app && python run_production_tests.py --quick
```

### Production Deployment Checklist

Before deploying:

1. ✅ Run `python run_production_tests.py` 
2. ✅ Verify "PRODUCTION READY ✅" status
3. ✅ Check all critical tests pass
4. ✅ Review performance metrics
5. ✅ Confirm API keys are production keys
6. ✅ Test with real future date (e.g., July 15, 2025)

## 🎯 Success Metrics

**Target: 80%+ overall success rate with 100% critical test success**

The framework ensures your betting app meets professional standards with:
- Reliable data sources
- Accurate calculations  
- Robust error handling
- Production-grade performance
- Regulatory compliance

---

**Need help?** Check the detailed test reports generated after each run, or review individual test files for specific implementation details.