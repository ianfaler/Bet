"""
Sharp Betting Predictor Integration

This file demonstrates how to integrate the Sharp Betting Predictor
into your existing Flask web application.

Usage:
1. Import this module in your main web_app.py
2. Initialize the SharpWebInterface with your Flask app
3. Access the Sharp Predictor at /sharp

Example Integration:
    from sharp_integration import integrate_sharp_predictor
    
    # In your web_app.py
    integrate_sharp_predictor(app)
"""

from flask import Flask
import logging
from sharp_web_interface import SharpWebInterface

def integrate_sharp_predictor(app: Flask) -> SharpWebInterface:
    """
    Integrate Sharp Betting Predictor into existing Flask app.
    
    Args:
        app: Flask application instance
        
    Returns:
        SharpWebInterface instance
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Sharp Web Interface
    sharp_interface = SharpWebInterface(app)
    
    # Add custom error handlers
    @app.errorhandler(404)
    def sharp_not_found(error):
        if '/sharp' in str(error):
            return "Sharp Predictor page not found", 404
        return error
    
    @app.errorhandler(500)
    def sharp_server_error(error):
        if '/sharp' in str(error):
            return "Sharp Predictor server error", 500
        return error
    
    return sharp_interface


def create_standalone_app() -> Flask:
    """
    Create a standalone Flask app with Sharp Predictor.
    Useful for testing and development.
    
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    app.secret_key = 'sharp-predictor-secret-key'
    
    # Basic route for the root
    @app.route('/')
    def index():
        return '''
        <html>
        <head><title>Sharp Betting Predictor</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h1>🏆 Sharp Betting Predictor</h1>
            <p>Welcome to the Sharp Betting Predictor platform!</p>
            <div style="margin-top: 30px;">
                <h2>🚀 Quick Start</h2>
                <p><a href="/sharp" style="color: #667eea; text-decoration: none; font-size: 18px;">→ Launch Sharp Predictor Dashboard</a></p>
                <p><a href="/sharp/demo" style="color: #667eea; text-decoration: none; font-size: 18px;">→ Run Demo Analysis</a></p>
            </div>
            <div style="margin-top: 30px;">
                <h2>📊 Features</h2>
                <ul>
                    <li><strong>Sharp Detection:</strong> RLM, Steam, Sharp Money, Consensus indicators</li>
                    <li><strong>Fair Value:</strong> Model vs market odds comparison with edge calculation</li>
                    <li><strong>EV Analysis:</strong> Expected value with Kelly Criterion staking</li>
                    <li><strong>Confidence Scoring:</strong> 1-10 scale based on multiple factors</li>
                    <li><strong>Data Management:</strong> CSV/JSON upload and manual entry</li>
                </ul>
            </div>
        </body>
        </html>
        '''
    
    # Integrate Sharp Predictor
    integrate_sharp_predictor(app)
    
    return app


def demo_analysis():
    """
    Run a demo analysis and print results.
    Useful for testing the system without the web interface.
    """
    from sharp_predictor import create_demo_analysis
    
    print("🚀 Running Sharp Betting Predictor Demo...")
    print("=" * 60)
    
    # Run demo analysis
    results = create_demo_analysis()
    
    print(f"📊 Analysis Results:")
    print(f"   Total Opportunities: {results.total_opportunities}")
    print(f"   Qualified Opportunities: {results.qualified_opportunities}")
    print(f"   High Confidence Bets: {results.high_confidence_count}")
    print(f"   Execution Time: {results.execution_time:.2f}s")
    print()
    
    if results.best_opportunities:
        print("🎯 Best Opportunities:")
        print("-" * 60)
        
        for i, opp in enumerate(results.best_opportunities[:5], 1):
            print(f"{i}. {opp.matchup}")
            print(f"   Bet: {opp.bet_type} {opp.bet_side}")
            print(f"   Odds: {opp.market_odds:+d} → Fair: {opp.fair_odds:+d}")
            print(f"   Edge: {opp.edge_percentage:+.1f}% | EV: ${opp.expected_value:.2f}")
            print(f"   Confidence: {opp.confidence_score}/10 ({opp.confidence_tier})")
            print(f"   Flags: {opp.flag_emojis or 'None'}")
            print(f"   Rationale: {opp.rationale}")
            print(f"   Recommended Stake: ${opp.recommended_stake:.0f}")
            print()
    
    print("📈 Summary Statistics:")
    stats = results.summary_stats
    print(f"   Average Edge: {stats['avg_edge']:.1f}%")
    print(f"   Average Confidence: {stats['avg_confidence']:.1f}/10")
    print(f"   Total Recommended Stake: ${stats['total_recommended_stake']:.0f}")
    print(f"   Bankroll Utilization: {stats['bankroll_utilization']:.1f}%")
    print()
    
    if stats['sharp_flag_distribution']:
        print("🔍 Sharp Flag Distribution:")
        for flag, count in stats['sharp_flag_distribution'].items():
            print(f"   {flag}: {count}")
    
    print("=" * 60)
    print("✅ Demo completed successfully!")


def test_components():
    """
    Test individual components of the Sharp Predictor.
    """
    print("🧪 Testing Sharp Predictor Components...")
    print("=" * 60)
    
    # Test Sharp Detector
    print("1. Testing Sharp Detector...")
    from sharp_detector import SharpDetector, create_manual_rlm_input
    
    detector = SharpDetector()
    rlm_data = create_manual_rlm_input(
        open_line=-1.0,
        current_line=-1.5,
        public_bets_pct=65.0,
        public_money_pct=72.0
    )
    
    indicators = detector.analyze_manual_input(rlm_data)
    print(f"   Found {len(indicators)} sharp indicators")
    for indicator in indicators:
        print(f"   - {indicator.flag_type}: {indicator.description}")
    
    # Test Fair Value Calculator
    print("\n2. Testing Fair Value Calculator...")
    from fair_value_calculator import FairValueCalculator, create_manual_moneyline_input
    
    fv_calc = FairValueCalculator()
    ml_data = create_manual_moneyline_input(
        home_prob=0.58,
        away_prob=0.42,
        home_odds=-150,
        away_odds=+130
    )
    
    fv_results = fv_calc.analyze_manual_input(ml_data)
    for result in fv_results:
        if result.is_positive_ev:
            print(f"   Positive EV: {result.outcome} at {result.edge_percentage:+.1f}% edge")
    
    # Test EV Engine
    print("\n3. Testing EV Engine...")
    from ev_engine import EVEngine, create_manual_ev_input
    
    ev_engine = EVEngine(bankroll=10000)
    ev_data = create_manual_ev_input(
        win_probability=0.58,
        odds=-150,
        stake=100
    )
    
    ev_results = ev_engine.analyze_manual_input(ev_data)
    for result in ev_results:
        print(f"   EV: ${result.expected_value:.2f} ({result.ev_percentage:+.1f}%)")
        print(f"   Recommended Stake: ${result.recommended_stake:.0f}")
    
    # Test Confidence Scorer
    print("\n4. Testing Confidence Scorer...")
    from confidence_scorer import ConfidenceScorer, create_manual_confidence_input
    
    conf_scorer = ConfidenceScorer()
    conf_data = create_manual_confidence_input(
        sharp_indicators=["RLM", "Sharp $"],
        ev_percentage=8.5,
        model_confidence=0.85,
        market_stability=0.8
    )
    
    conf_result = conf_scorer.analyze_manual_input(conf_data)
    print(f"   Confidence Score: {conf_result.final_score}/10")
    print(f"   Explanation: {conf_result.explanation}")
    
    print("\n✅ All components tested successfully!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "demo":
            demo_analysis()
        elif command == "test":
            test_components()
        elif command == "web":
            app = create_standalone_app()
            print("🌐 Starting Sharp Predictor Web Server...")
            print("📍 Access the dashboard at: http://localhost:5000/sharp")
            print("🚀 Demo analysis at: http://localhost:5000/sharp/demo")
            app.run(debug=True, host='0.0.0.0', port=5000)
        else:
            print("Usage: python sharp_integration.py [demo|test|web]")
    else:
        print("Sharp Betting Predictor Integration")
        print("=" * 40)
        print("Available commands:")
        print("  demo  - Run demo analysis in terminal")
        print("  test  - Test individual components")
        print("  web   - Start web server")
        print()
        print("Example usage:")
        print("  python sharp_integration.py demo")
        print("  python sharp_integration.py web")