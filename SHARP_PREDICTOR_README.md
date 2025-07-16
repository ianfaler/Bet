# 📊 Sharp Betting Predictor

A comprehensive sharp betting analysis system that identifies profitable betting opportunities by detecting sharp action, calculating fair values, and providing confidence-based recommendations.

## 🎯 Overview

The Sharp Betting Predictor replicates the core functionality of Action Network's sharp indicators and Unabated's fair value calculator, using advanced algorithms to:

- **Detect Sharp Action**: RLM, Steam Moves, Handle vs Ticket Split, Consensus Shifts
- **Calculate Fair Values**: Model probabilities vs market odds with edge calculation
- **Analyze Expected Value**: Kelly Criterion staking with risk adjustments
- **Score Confidence**: 1-10 scoring based on multiple factors
- **Provide Clear Rationale**: Human-readable explanations for each opportunity

## 🏗️ System Architecture

```
Sharp Betting Predictor
├── sharp_detector.py          # Sharp betting indicators (RLM, Steam, etc.)
├── fair_value_calculator.py   # Fair odds calculation and edge analysis  
├── ev_engine.py               # Expected value and Kelly Criterion staking
├── confidence_scorer.py       # 1-10 confidence scoring system
├── data_input_manager.py      # CSV/JSON upload and manual entry
├── sharp_predictor.py         # Main analysis engine (coordinates all components)
├── sharp_web_interface.py     # Flask web interface and API endpoints
└── sharp_integration.py       # Integration tools and demo functions
```

## 🔍 Core Components

### 1. Sharp Detection Module (`sharp_detector.py`)

Detects professional betting activity through multiple indicators:

- **Reverse Line Movement (RLM)**: Line moves against public money
- **Steam Moves**: Rapid line movement across multiple books  
- **Sharp Money Split**: Handle % significantly higher than ticket %
- **Consensus Shifts**: Agreement across multiple sportsbooks

**Example Usage:**
```python
from sharp_detector import SharpDetector, create_manual_rlm_input

detector = SharpDetector()

# Manual RLM input: line moved from -1 to -1.5 with 65% public on +1.5
rlm_data = create_manual_rlm_input(
    open_line=-1.0,
    current_line=-1.5, 
    public_bets_pct=65.0,
    public_money_pct=72.0
)

indicators = detector.analyze_manual_input(rlm_data)
# Returns: [SharpIndicator(flag_type="RLM", strength=2, description="Line moved -0.5 against 65% public")]
```

### 2. Fair Value Calculator (`fair_value_calculator.py`)

Calculates fair odds from model probabilities and compares to market:

- **Fair Odds Calculation**: `fair_odds = 1 / model_win_prob`
- **Edge Calculation**: `edge = (model_implied_prob - market_prob) * 100`
- **No-Vig Calculations**: Remove sportsbook margins
- **Multiple Bet Types**: Moneyline, spread, totals

**Example Usage:**
```python
from fair_value_calculator import FairValueCalculator, create_manual_moneyline_input

calculator = FairValueCalculator()

# Model thinks home team has 58% chance, market has them at -150 odds
ml_data = create_manual_moneyline_input(
    home_prob=0.58,
    away_prob=0.42,
    home_odds=-150,  # Market odds
    away_odds=+130
)

results = calculator.analyze_manual_input(ml_data)
# Returns edge percentage and value rating
```

### 3. EV Engine (`ev_engine.py`)

Calculates Expected Value with advanced risk management:

- **Basic EV**: `EV = (win_prob * payout) - (lose_prob * stake)`
- **Kelly Criterion**: Optimal stake sizing with quarter-Kelly safety
- **Risk Factors**: Weather, injuries, lineup changes, variance
- **Manual Overrides**: Disable bets or adjust probabilities

**Example Usage:**
```python
from ev_engine import EVEngine, create_manual_ev_input, create_risk_factor

ev_engine = EVEngine(bankroll=10000)

# Create risk factors
risk_factors = [
    create_risk_factor("weather", -0.1, "Heavy rain expected"),
    create_risk_factor("injury", -0.15, "Star player questionable")
]

ev_data = create_manual_ev_input(
    win_probability=0.58,
    odds=-150,
    stake=100,
    risk_factors=risk_factors
)

results = ev_engine.analyze_manual_input(ev_data)
# Returns EV calculation with recommended stake
```

### 4. Confidence Scorer (`confidence_scorer.py`)

Generates 1-10 confidence scores based on:

- **Sharp Indicators** (max 3 points): RLM, Steam, Sharp Money, Consensus
- **EV Tier** (max 3 points): Excellent (10%+), Good (6%+), Fair (3%+)  
- **Model Confidence** (max 2 points): High model certainty
- **Market Stability** (max 2 points): Stable lines and high data quality
- **Volatility Penalty** (max -2 points): Risk factors like weather/injuries

**Example Usage:**
```python
from confidence_scorer import ConfidenceScorer, create_manual_confidence_input

scorer = ConfidenceScorer()

conf_data = create_manual_confidence_input(
    sharp_indicators=["RLM", "Sharp $"],
    ev_percentage=8.5,
    model_confidence=0.85,
    market_stability=0.8,
    volatility_factors=["weather"]
)

result = scorer.analyze_manual_input(conf_data)
# Returns: ConfidenceBreakdown(final_score=8, explanation="Confidence 8/10: Strong sharp indicators, Good EV...")
```

## 🌐 Web Interface

### Dashboard Features

- **Analysis Configuration**: Set bankroll, EV threshold, confidence minimums
- **Real-time Analysis**: Run sharp predictor on uploaded or manual data
- **Data Upload**: CSV/JSON file upload with templates
- **Manual Entry**: Create game entries through web forms
- **Results Display**: Sortable table with all opportunity details

### API Endpoints

```
POST /api/sharp/analyze          # Run sharp analysis
POST /api/sharp/upload-csv       # Upload CSV data
POST /api/sharp/upload-json      # Upload JSON data  
POST /api/sharp/manual-entry     # Create manual game entry
GET  /api/sharp/data-summary     # Get data summary
GET  /api/sharp/csv-template/{type}  # Download CSV templates
```

### Web Interface Pages

```
/sharp                    # Main dashboard
/sharp/demo              # Demo analysis with sample data
/sharp/data-upload       # CSV/JSON upload interface  
/sharp/manual-entry      # Manual game entry form
```

## 🚀 Getting Started

### 1. Quick Demo (Terminal)

```bash
python sharp_integration.py demo
```

This runs a complete demo analysis and shows:
- Sample betting opportunities
- Sharp indicators detected
- Fair value calculations  
- EV analysis with recommended stakes
- Confidence scores and explanations

### 2. Web Interface

```bash
python sharp_integration.py web
```

Then visit:
- Dashboard: `http://localhost:5000/sharp`
- Demo Analysis: `http://localhost:5000/sharp/demo`

### 3. Component Testing

```bash
python sharp_integration.py test
```

Tests each component individually to verify functionality.

### 4. Integration with Existing App

```python
# In your existing web_app.py
from sharp_integration import integrate_sharp_predictor

app = Flask(__name__)

# Add your existing routes...

# Integrate Sharp Predictor
integrate_sharp_predictor(app)

if __name__ == "__main__":
    app.run()
```

## 📊 Example Output

### Terminal Demo Output
```
🚀 Running Sharp Betting Predictor Demo...
============================================================
📊 Analysis Results:
   Total Opportunities: 6
   Qualified Opportunities: 3
   High Confidence Bets: 2
   Execution Time: 0.12s

🎯 Best Opportunities:
------------------------------------------------------------
1. Red Sox @ Yankees
   Bet: Moneyline Home
   Odds: -150 → Fair: -138
   Edge: +3.5% | EV: $2.31
   Confidence: 8/10 (High)
   Flags: 📉 💸
   Rationale: Fair 3.5% edge | Sharp signals: RLM, Sharp $ | Model 58% vs Market 55%
   Recommended Stake: $87

📈 Summary Statistics:
   Average Edge: 5.2%
   Average Confidence: 7.8/10
   Total Recommended Stake: $234
   Bankroll Utilization: 2.3%
============================================================
```

### Web Dashboard Display

| Match | Bet | Odds | Flags | Edge | EV | Confidence | Stake |
|-------|-----|------|-------|------|----|-----------|----- |
| Red Sox @ Yankees | ML Home | -150 | 📉💸 | +3.5% | $2.31 | 8/10 | $87 |
| Lakers @ Warriors | Spread -2.5 | -110 | 🔥 | +4.1% | $1.95 | 7/10 | $65 |

## 📁 Data Input Formats

### CSV Upload Templates

**Odds Data:**
```csv
game_id,book,bet_type,odds,line_value,timestamp
MLB_NYY_BOS_2025-01-15,DraftKings,moneyline,-150,,2025-01-15 19:00:00
MLB_NYY_BOS_2025-01-15,DraftKings,spread,-110,-1.5,2025-01-15 19:00:00
```

**Public Betting Data:**
```csv  
game_id,bet_type,side,bets_pct,money_pct,timestamp
MLB_NYY_BOS_2025-01-15,moneyline,home,65,72,2025-01-15 19:00:00
```

**Line Movements:**
```csv
game_id,book,bet_type,from_line,to_line,timestamp
MLB_NYY_BOS_2025-01-15,DraftKings,spread,-1.0,-1.5,2025-01-15 18:30:00
```

### Manual Entry

The web interface provides forms for:
- Game information (teams, date, sport)
- Odds data (moneyline, spread, totals)
- Public betting percentages  
- Model predictions
- Line movement tracking

## 🔧 Configuration

### Analysis Parameters

```python
predictor = SharpPredictor(
    bankroll=10000.0,      # Available bankroll
    min_ev=3.0,            # Minimum EV % threshold  
    min_confidence=7       # Minimum confidence score (1-10)
)
```

### Sharp Detection Thresholds

```python
detector = SharpDetector()
detector.rlm_threshold = 0.5      # Minimum line movement for RLM
detector.steam_threshold = 0.5    # Minimum rapid movement for steam  
detector.split_threshold = 10.0   # Minimum % difference for handle/ticket split
```

### Fair Value Settings

```python
calculator = FairValueCalculator()
calculator.min_edge_threshold = 3.0        # Minimum edge to consider
calculator.excellent_edge_threshold = 10.0  # Excellent value cutoff
calculator.good_edge_threshold = 6.0        # Good value cutoff
```

## 📈 Integration with Existing Systems

### API Integration

The system is designed to easily integrate with real-time APIs:

```python
# Replace manual input with API calls
def get_live_odds(game_id):
    # Call The Odds API
    return odds_data

def get_public_percentages(game_id):  
    # Call Action Network or similar
    return public_data

# Update predictor to use live data
results = predictor.analyze_multiple_games(games, live_predictions)
```

### Database Integration

```python
# Save results to database
def save_opportunities(opportunities):
    for opp in opportunities:
        db.session.add(BettingOpportunity(
            game_id=opp.game_id,
            edge_percentage=opp.edge_percentage,
            confidence_score=opp.confidence_score,
            # ... other fields
        ))
    db.session.commit()
```

## 🎯 Use Cases

### 1. Sharp Action Detection
- Monitor line movements against public percentages
- Identify when professional money is moving lines
- Track steam moves across multiple books
- Detect consensus sharp plays

### 2. Value Betting
- Compare model probabilities to market odds
- Calculate precise edge percentages  
- Identify overvalued and undervalued lines
- Find closing line value opportunities

### 3. Bankroll Management
- Kelly Criterion optimal sizing
- Risk-adjusted staking
- Exposure limits and safety overrides
- Portfolio-level risk management

### 4. Research and Analysis
- Historical sharp indicator performance
- Model calibration and accuracy tracking
- Market efficiency analysis
- Sportsbook comparison

## 🔍 Advanced Features

### Risk Factor Analysis
- Weather impact modeling
- Injury probability adjustments
- Lineup change detection
- Market volatility assessment

### Multi-Model Consensus
- Combine multiple prediction models
- Weight models by historical accuracy
- Detect model disagreement
- Ensemble probability calculation

### Real-time Monitoring
- Live line movement tracking
- Alert system for sharp indicators
- Automated opportunity detection
- Performance tracking and reporting

## 📋 Dependencies

```
requests>=2.31.0
pandas>=2.0.0  
numpy>=1.24.0
flask>=2.3.0
flask-cors>=4.0.0
```

## 🚀 Future Enhancements

### Planned Features
- **Real-time APIs**: Integration with The Odds API, Action Network
- **Machine Learning**: Automated sharp detection model training
- **Mobile Interface**: Responsive design for mobile devices
- **Database Backend**: PostgreSQL integration for historical data
- **Alert System**: Email/SMS notifications for high-value opportunities
- **Portfolio Tracking**: P&L tracking and performance analytics

### API Upgrade Path
The system is built for easy API integration:

1. **Replace manual input** with live API calls
2. **Add real-time line monitoring** for instant steam detection  
3. **Integrate public betting APIs** for live percentage data
4. **Connect model prediction services** for automated probability updates

## 📞 Support

For questions, issues, or feature requests, the system includes:
- Comprehensive error handling and logging
- Demo data for testing all functionality
- Modular design for easy customization
- Well-documented APIs and data formats

The Sharp Betting Predictor provides professional-grade sharp betting analysis while maintaining the flexibility for manual input during initial deployment, with a clear path to full automation as API integrations are added.