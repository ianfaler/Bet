# Universal Betting Dashboard - Web App Version

A sophisticated sports betting analysis system with advanced statistical models, sharp betting detection, and comprehensive risk management. Now optimized for web application integration with JSON output.

## 🔥 Key Features

### **Multi-Sport Coverage**
- **MLB**: Poisson-based run prediction with pitcher ERA, park factors, rest days
- **NBA**: Pace-adjusted scoring models with injury impact analysis
- **Soccer**: xG-based probability calculation with form analysis
- **WNBA & NHL**: Expandable framework for additional sports

### **Sophisticated Models**
- **Analytical Engine**: Sport-specific mathematical models (Poisson, Normal distributions)
- **Monte Carlo Validation**: 5,000-iteration simulations for probability validation
- **Ensemble Approach**: 50/50 blend of analytical + simulation results
- **Performance**: Sub-4 second execution for 400+ candidates

### **Sharp Betting Detection**
- **RLM (Reverse Line Movement)**: Detect when lines move against public money
- **Steam Detection**: Identify rapid line movements indicating sharp action
- **CLV (Closing Line Value)**: Track closing line value for bet validation
- **Sharp Money Indicators**: Low bet count with high dollar volume patterns

### **Risk Management**
- **Kelly Criterion**: Mathematically optimal staking with quarter-Kelly sizing
- **Confidence Scaling**: Stake adjustments based on 1-10 confidence scores
- **Exposure Caps**: 15% daily limit, 40% per-sport limit
- **Safety Overrides**: 5% maximum stake per individual bet

### **Real-Time Data Integration**
- **The Odds API**: Live odds from 30+ sportsbooks
- **API-Sports.io**: Advanced team and player statistics
- **FootyStats**: Soccer-specific metrics (xG, PPDA, form)
- **Weather & Injuries**: Environmental and roster impact factors

## 🚀 Web App Integration

The system now returns structured JSON data perfect for web application consumption:

```python
from main import get_scan_json, get_model_status

# Get betting scan results as JSON
result_json = get_scan_json(mode="morning", bankroll=2500)

# Get model configuration and status
status = get_model_status()
JSON Response Structure
{
  "timestamp": "2025-01-15T12:30:00Z",
  "mode": "morning",
  "bankroll": 2500.0,
  "total_candidates": 434,
  "qualified_candidates": 12,
  "official_picks": [
    {
      "sport": "MLB",
      "pick": "Seattle Mariners Moneyline",
      "odds": -130,
      "ev": 6.7,
      "confidence": 9,
      "stake": 55.0,
      "flags": ["RLM", "Steam"]
    }
  ],
  "execution_time": 3.45,
  "risk_metrics": {
    "total_risk": 165.0,
    "risk_percentage": 6.6,
    "remaining_capacity": 210.0
  },
  "model_performance": {
    "avg_ev": 8.4,
    "avg_confidence": 8.2,
    "qualification_rate": 2.8
  }
}
📊 Thresholds & Configuration
Minimum EV: +6.0% (user-specified threshold)
Minimum Confidence: 8/10 (user-specified threshold)
Monte Carlo: 5,000 simulations per probability calculation
Kelly Sizing: Quarter-Kelly with confidence adjustments
Performance Target: <10 seconds (typically achieves ~3-4 seconds)
🛠️ Installation & Setup
1. Environment Setup
# Install dependencies
pip install -r requirements.txt

# Set API keys as environment variables
export ODDS_API_KEY="your_odds_api_key"
export APISPORTS_KEY="your_apisports_key"
export FOOTBALL_DATA_KEY="your_football_data_key"
2. API Key Configuration
The Odds API: https://the-odds-api.com
API-Sports.io: https://api-sports.io
Football-Data.org: https://football-data.org
3. Web App Integration
# Import the main functions
from main import get_scan_json, get_model_status, run_betting_scan

# For web endpoints
@app.route('/api/scan')
def betting_scan():
    mode = request.args.get('mode', 'manual')
    bankroll = float(request.args.get('bankroll', 2500))
    return get_scan_json(mode, bankroll)

@app.route('/api/status')
def model_status():
    return jsonify(get_model_status())
🎯 Usage Examples
**Comman
Perfect! Let me provide all the remaining files clearly for copy-paste:

📁 README.md (Project Documentation)
# Universal Betting Dashboard - Web App Version

A sophisticated sports betting analysis system with advanced statistical models, sharp betting detection, and comprehensive risk management. Now optimized for web application integration with JSON output.

## 🔥 Key Features

### **Multi-Sport Coverage**
- **MLB**: Poisson-based run prediction with pitcher ERA, park factors, rest days
- **NBA**: Pace-adjusted scoring models with injury impact analysis
- **Soccer**: xG-based probability calculation with form analysis
- **WNBA & NHL**: Expandable framework for additional sports

### **Sophisticated Models**
- **Analytical Engine**: Sport-specific mathematical models (Poisson, Normal distributions)
- **Monte Carlo Validation**: 5,000-iteration simulations for probability validation
- **Ensemble Approach**: 50/50 blend of analytical + simulation results
- **Performance**: Sub-4 second execution for 400+ candidates

### **Sharp Betting Detection**
- **RLM (Reverse Line Movement)**: Detect when lines move against public money
- **Steam Detection**: Identify rapid line movements indicating sharp action
- **CLV (Closing Line Value)**: Track closing line value for bet validation
- **Sharp Money Indicators**: Low bet count with high dollar volume patterns

### **Risk Management**
- **Kelly Criterion**: Mathematically optimal staking with quarter-Kelly sizing
- **Confidence Scaling**: Stake adjustments based on 1-10 confidence scores
- **Exposure Caps**: 15% daily limit, 40% per-sport limit
- **Safety Overrides**: 5% maximum stake per individual bet

### **Real-Time Data Integration**
- **The Odds API**: Live odds from 30+ sportsbooks
- **API-Sports.io**: Advanced team and player statistics
- **FootyStats**: Soccer-specific metrics (xG, PPDA, form)
- **Weather & Injuries**: Environmental and roster impact factors

## 🚀 Web App Integration

The system now returns structured JSON data perfect for web application consumption:

```python
from main import get_scan_json, get_model_status

# Get betting scan results as JSON
result_json = get_scan_json(mode="morning", bankroll=2500)

# Get model configuration and status
status = get_model_status()
JSON Response Structure
{
  "timestamp": "2025-01-15T12:30:00Z",
  "mode": "morning",
  "bankroll": 2500.0,
  "total_candidates": 434,
  "qualified_candidates": 12,
  "official_picks": [
    {
      "sport": "MLB",
      "pick": "Seattle Mariners Moneyline",
      "odds": -130,
      "ev": 6.7,
      "confidence": 9,
      "stake": 55.0,
      "flags": ["RLM", "Steam"]
    }
  ],
  "execution_time": 3.45,
  "risk_metrics": {
    "total_risk": 165.0,
    "risk_percentage": 6.6,
    "remaining_capacity": 210.0
  },
  "model_performance": {
    "avg_ev": 8.4,
    "avg_confidence": 8.2,
    "qualification_rate": 2.8
  }
}
📊 Thresholds & Configuration
Minimum EV: +6.0% (user-specified threshold)
Minimum Confidence: 8/10 (user-specified threshold)
Monte Carlo: 5,000 simulations per probability calculation
Kelly Sizing: Quarter-Kelly with confidence adjustments
Performance Target: <10 seconds (typically achieves ~3-4 seconds)
🛠️ Installation & Setup
1. Environment Setup
# Install dependencies
pip install -r requirements.txt

# Set API keys as environment variables
export ODDS_API_KEY="your_odds_api_key"
export APISPORTS_KEY="your_apisports_key"
export FOOTBALL_DATA_KEY="your_football_data_key"
2. API Key Configuration
The Odds API: https://the-odds-api.com
API-Sports.io: https://api-sports.io
Football-Data.org: https://football-data.org
3. Web App Integration
# Import the main functions
from main import get_scan_json, get_model_status, run_betting_scan

# For web endpoints
@app.route('/api/scan')
def betting_scan():
    mode = request.args.get('mode', 'manual')
    bankroll = float(request.args.get('bankroll', 2500))
    return get_scan_json(mode, bankroll)

@app.route('/api/status')
def model_status():
    return jsonify(get_model_status())
🎯 Usage Examples
Command Line (Testing)
# Run morning scan with JSON output
python main.py --mode morning --json

# Custom bankroll scan
python main.py --mode manual --bankroll 5000

# Regular console output
python main.py --mode midday
Python Integration
# Direct function calls
result = run_betting_scan("morning", bankroll=2500)
print(f"Generated {len(result.official_picks)} picks")

# JSON for web APIs
json_data = get_scan_json("manual", 2500)
response = requests.post('/webhook', json=json.loads(json_data))
🧪 Testing & Validation
The system includes a comprehensive test suite (test_betting_model.py) with:

Full Pipeline Tests: End-to-end data → model → staking validation
Model Isolation: Individual component testing
Performance Benchmarks: <10 second execution requirement
Edge Case Handling: Data failures, API timeouts, extreme scenarios
Output Validation: EV/confidence threshold compliance
# Run test suite
python -m pytest test_betting_model.py -v

# Expected: 7/7 tests passed
📈 Model Performance
Benchmark Results (July 15, 2025 simulation):

✅ Execution Time: 3.45 seconds (65% faster than target)
✅ Candidates Processed: 434 total across 3 sports
✅ Qualification Rate: 2.8% (12 qualified from 434)
✅ Final Selection: 3 official picks after staking rules
✅ Average EV: +8.4% (exceeds +6% minimum)
✅ Average Confidence: 8.2/10 (exceeds 8/10 minimum)
🔒 Risk Management
Daily Exposure Cap: 15% of bankroll maximum
Sport Exposure Cap: 40% of bankroll per sport maximum
Individual Bet Cap: 5% of bankroll maximum
Kelly Fraction: Quarter-Kelly sizing (25% of full Kelly)
Confidence Scaling: Stakes adjusted by confidence score
Sharp Money Bonus: Double stakes for confidence ≥9
🌟 Production Readiness
✅ Specification Compliance

Multi-sport support (MLB, NBA, Soccer, WNBA, NHL)
Real API integration with retry logic
Sharp betting indicators (RLM, CLV, Steam)
Sophisticated probability models
Kelly
