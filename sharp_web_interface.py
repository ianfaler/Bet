"""
Sharp Betting Predictor Web Interface

Extends the existing Flask web app with Sharp Predictor functionality:
- API endpoints for sharp analysis
- Data upload interfaces
- Sharp predictor dashboard
- JSON API for frontend consumption
- Manual input forms
"""

from flask import Flask, request, jsonify, render_template_string, redirect, url_for, flash
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Import Sharp Predictor components
from sharp_predictor import SharpPredictor, create_demo_analysis, BettingOpportunity, SharpPredictorResults
from data_input_manager import DataInputManager, create_odds_data, create_public_betting_data
from sharp_detector import SharpDetector
from fair_value_calculator import FairValueCalculator
from ev_engine import EVEngine
from confidence_scorer import ConfidenceScorer


class SharpWebInterface:
    """Web interface for the Sharp Betting Predictor."""
    
    def __init__(self, app: Flask):
        self.app = app
        self.predictor = SharpPredictor()
        self.data_manager = DataInputManager()
        self.logger = logging.getLogger(__name__)
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all Sharp Predictor routes."""
        
        @self.app.route('/sharp')
        def sharp_dashboard():
            """Main Sharp Predictor dashboard."""
            return render_template_string(SHARP_DASHBOARD_TEMPLATE)
        
        @self.app.route('/api/sharp/analyze', methods=['POST'])
        def analyze_sharp_opportunities():
            """API endpoint to analyze sharp opportunities."""
            try:
                # Get analysis parameters
                data = request.get_json()
                
                bankroll = data.get('bankroll', 10000)
                min_ev = data.get('min_ev', 3.0)
                min_confidence = data.get('min_confidence', 7)
                
                # Configure predictor
                predictor = SharpPredictor(
                    bankroll=bankroll, 
                    min_ev=min_ev, 
                    min_confidence=min_confidence
                )
                
                # Get games to analyze
                games = self.data_manager.get_all_games()
                
                if not games:
                    # Use demo data if no games available
                    results = create_demo_analysis()
                else:
                    # Analyze actual games
                    results = predictor.analyze_multiple_games(games)
                
                # Convert to JSON
                json_response = predictor.to_json(results)
                
                return json_response, 200, {'Content-Type': 'application/json'}
                
            except Exception as e:
                self.logger.error(f"Error in sharp analysis: {str(e)}")
                return jsonify({
                    'error': 'Analysis failed',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/sharp/upload-csv', methods=['POST'])
        def upload_csv_data():
            """Upload CSV data for analysis."""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file uploaded'}), 400
                
                file = request.files['file']
                data_type = request.form.get('data_type')
                
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                if not data_type:
                    return jsonify({'error': 'Data type not specified'}), 400
                
                # Read file content
                file_content = file.read().decode('utf-8')
                
                # Process CSV
                result = self.data_manager.upload_csv_data(file_content, data_type)
                
                return jsonify(result)
                
            except Exception as e:
                self.logger.error(f"Error uploading CSV: {str(e)}")
                return jsonify({
                    'error': 'Upload failed',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/sharp/upload-json', methods=['POST'])
        def upload_json_data():
            """Upload JSON data for analysis."""
            try:
                data = request.get_json()
                json_content = data.get('content')
                data_type = data.get('data_type')
                
                if not json_content or not data_type:
                    return jsonify({'error': 'Missing content or data type'}), 400
                
                # Process JSON
                result = self.data_manager.upload_json_data(json_content, data_type)
                
                return jsonify(result)
                
            except Exception as e:
                self.logger.error(f"Error uploading JSON: {str(e)}")
                return jsonify({
                    'error': 'Upload failed',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/sharp/manual-entry', methods=['POST'])
        def create_manual_entry():
            """Create manual game entry."""
            try:
                data = request.get_json()
                
                # Create odds data
                odds_data = create_odds_data(
                    moneyline_home=data.get('moneyline_home', -110),
                    moneyline_away=data.get('moneyline_away', -110),
                    spread_line=data.get('spread_line', -3.5),
                    spread_odds=data.get('spread_odds', -110),
                    total_line=data.get('total_line', 8.5),
                    total_odds=data.get('total_odds', -110),
                    book=data.get('book', 'Manual')
                )
                
                # Create public betting data if provided
                public_data = None
                if data.get('include_public_data'):
                    public_data = create_public_betting_data(
                        moneyline_home_bets=data.get('ml_home_bets', 50),
                        moneyline_home_money=data.get('ml_home_money', 50),
                        spread_favorite_bets=data.get('spread_fav_bets', 50),
                        spread_favorite_money=data.get('spread_fav_money', 50),
                        total_over_bets=data.get('total_over_bets', 50),
                        total_over_money=data.get('total_over_money', 50)
                    )
                
                # Create model predictions if provided
                model_predictions = None
                if data.get('include_predictions'):
                    model_predictions = {
                        'moneyline_home_prob': data.get('home_win_prob', 0.5),
                        'moneyline_away_prob': data.get('away_win_prob', 0.5),
                        'spread_favorite_prob': data.get('spread_prob', 0.5),
                        'total_over_prob': data.get('over_prob', 0.5)
                    }
                
                # Create game entry
                game_data = self.data_manager.create_manual_game_entry(
                    sport=data.get('sport', 'Unknown'),
                    home_team=data.get('home_team', 'Home'),
                    away_team=data.get('away_team', 'Away'),
                    game_date=data.get('game_date', datetime.now().strftime('%Y-%m-%d')),
                    odds_data=odds_data,
                    public_data=public_data,
                    model_predictions=model_predictions
                )
                
                return jsonify({
                    'success': True,
                    'game_id': game_data.game_id,
                    'message': 'Game entry created successfully'
                })
                
            except Exception as e:
                self.logger.error(f"Error creating manual entry: {str(e)}")
                return jsonify({
                    'error': 'Entry creation failed',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/sharp/add-line-movement', methods=['POST'])
        def add_line_movement():
            """Add line movement data."""
            try:
                data = request.get_json()
                
                result = self.data_manager.add_line_movement(
                    game_id=data.get('game_id'),
                    book=data.get('book', 'Unknown'),
                    bet_type=data.get('bet_type', 'moneyline'),
                    from_line=data.get('from_line', 0),
                    to_line=data.get('to_line', 0),
                    timestamp=data.get('timestamp')
                )
                
                return jsonify(result)
                
            except Exception as e:
                self.logger.error(f"Error adding line movement: {str(e)}")
                return jsonify({
                    'error': 'Line movement addition failed',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/sharp/data-summary')
        def get_data_summary():
            """Get summary of uploaded data."""
            try:
                summary = self.data_manager.get_data_summary()
                return jsonify(summary)
            except Exception as e:
                self.logger.error(f"Error getting data summary: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/sharp/csv-template/<data_type>')
        def get_csv_template(data_type):
            """Get CSV template for data upload."""
            try:
                template = self.data_manager.export_data_template(data_type)
                
                if not template:
                    return jsonify({'error': 'Invalid data type'}), 400
                
                return template, 200, {
                    'Content-Type': 'text/csv',
                    'Content-Disposition': f'attachment; filename={data_type}_template.csv'
                }
            except Exception as e:
                self.logger.error(f"Error generating template: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/sharp/demo')
        def sharp_demo():
            """Run demo analysis and display results."""
            try:
                results = create_demo_analysis()
                
                # Convert to display format
                display_data = self._format_results_for_display(results)
                
                return render_template_string(SHARP_RESULTS_TEMPLATE, 
                                            results=display_data,
                                            timestamp=results.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                
            except Exception as e:
                self.logger.error(f"Error in demo: {str(e)}")
                return f"Demo failed: {str(e)}", 500
        
        @self.app.route('/sharp/data-upload')
        def data_upload_page():
            """Data upload interface."""
            return render_template_string(DATA_UPLOAD_TEMPLATE)
        
        @self.app.route('/sharp/manual-entry')
        def manual_entry_page():
            """Manual entry interface."""
            return render_template_string(MANUAL_ENTRY_TEMPLATE)
    
    def _format_results_for_display(self, results: SharpPredictorResults) -> Dict[str, Any]:
        """Format results for HTML display."""
        formatted_opportunities = []
        
        for opp in results.best_opportunities:
            formatted_opp = {
                'matchup': opp.matchup,
                'bet': f"{opp.bet_type} {opp.bet_side}",
                'odds': f"{opp.market_odds:+d}",
                'best_book': opp.best_book,
                'sharp_flags': opp.flag_emojis,
                'fair_odds': f"{opp.fair_odds:+d}",
                'edge': f"{opp.edge_percentage:+.1f}%",
                'ev_dollar': f"${opp.expected_value:.2f}",
                'confidence': f"{opp.confidence_score}/10",
                'rationale': opp.rationale
            }
            formatted_opportunities.append(formatted_opp)
        
        return {
            'opportunities': formatted_opportunities,
            'total_opportunities': results.total_opportunities,
            'qualified_opportunities': results.qualified_opportunities,
            'high_confidence_count': results.high_confidence_count,
            'execution_time': f"{results.execution_time:.2f}s",
            'summary_stats': results.summary_stats
        }


# HTML Templates for the Sharp Predictor Interface

SHARP_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sharp Betting Predictor</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .nav { display: flex; gap: 15px; margin-bottom: 30px; }
        .nav-item { background: white; padding: 15px 25px; border-radius: 8px; text-decoration: none; color: #333; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .nav-item:hover { transform: translateY(-2px); }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        .btn:hover { background: #5a6fd8; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #5a6268; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .results-container { margin-top: 30px; }
        .loading { text-align: center; padding: 40px; color: #667eea; }
        .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 6px; border: 1px solid #f5c6cb; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 6px; border: 1px solid #c3e6cb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Sharp Betting Predictor</h1>
            <p>Identify sharp betting opportunities with advanced analysis</p>
        </div>
        
        <div class="nav">
            <a href="/sharp" class="nav-item">🏠 Dashboard</a>
            <a href="/sharp/demo" class="nav-item">🚀 Demo Analysis</a>
            <a href="/sharp/data-upload" class="nav-item">📁 Data Upload</a>
            <a href="/sharp/manual-entry" class="nav-item">✏️ Manual Entry</a>
        </div>
        
        <div class="card">
            <h2>🎯 Run Sharp Analysis</h2>
            <p>Configure your analysis parameters and discover sharp betting opportunities.</p>
            
            <div class="form-group">
                <label for="bankroll">Bankroll ($)</label>
                <input type="number" id="bankroll" value="10000" min="100" step="100">
            </div>
            
            <div class="form-group">
                <label for="min_ev">Minimum EV (%)</label>
                <input type="number" id="min_ev" value="3.0" min="0" step="0.1">
            </div>
            
            <div class="form-group">
                <label for="min_confidence">Minimum Confidence (1-10)</label>
                <input type="number" id="min_confidence" value="7" min="1" max="10">
            </div>
            
            <button class="btn" onclick="runAnalysis()">🔍 Analyze Opportunities</button>
            <button class="btn btn-secondary" onclick="loadDataSummary()">📊 Data Summary</button>
        </div>
        
        <div id="results-container" class="results-container"></div>
    </div>
    
    <script>
        async function runAnalysis() {
            const resultsContainer = document.getElementById('results-container');
            resultsContainer.innerHTML = '<div class="loading">🔄 Analyzing opportunities...</div>';
            
            try {
                const response = await fetch('/api/sharp/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        bankroll: parseFloat(document.getElementById('bankroll').value),
                        min_ev: parseFloat(document.getElementById('min_ev').value),
                        min_confidence: parseInt(document.getElementById('min_confidence').value)
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const results = await response.json();
                displayResults(results);
                
            } catch (error) {
                resultsContainer.innerHTML = `<div class="error">❌ Analysis failed: ${error.message}</div>`;
            }
        }
        
        function displayResults(results) {
            const container = document.getElementById('results-container');
            
            let html = `
                <div class="card">
                    <h2>📈 Analysis Results</h2>
                    <p><strong>Execution Time:</strong> ${results.execution_time.toFixed(2)}s</p>
                    <p><strong>Total Opportunities:</strong> ${results.total_opportunities}</p>
                    <p><strong>Qualified Opportunities:</strong> ${results.qualified_opportunities}</p>
                    <p><strong>High Confidence Bets:</strong> ${results.high_confidence_count}</p>
                </div>
            `;
            
            if (results.opportunities && results.opportunities.length > 0) {
                html += `
                    <div class="card">
                        <h3>🎯 Best Opportunities</h3>
                        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                            <thead>
                                <tr style="background: #f8f9fa; text-align: left;">
                                    <th style="padding: 12px; border: 1px solid #dee2e6;">Match</th>
                                    <th style="padding: 12px; border: 1px solid #dee2e6;">Bet</th>
                                    <th style="padding: 12px; border: 1px solid #dee2e6;">Odds</th>
                                    <th style="padding: 12px; border: 1px solid #dee2e6;">Flags</th>
                                    <th style="padding: 12px; border: 1px solid #dee2e6;">Edge</th>
                                    <th style="padding: 12px; border: 1px solid #dee2e6;">EV</th>
                                    <th style="padding: 12px; border: 1px solid #dee2e6;">Confidence</th>
                                    <th style="padding: 12px; border: 1px solid #dee2e6;">Stake</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                results.opportunities.forEach(opp => {
                    html += `
                        <tr>
                            <td style="padding: 12px; border: 1px solid #dee2e6;">${opp.matchup}</td>
                            <td style="padding: 12px; border: 1px solid #dee2e6;">${opp.bet_type} ${opp.bet_side}</td>
                            <td style="padding: 12px; border: 1px solid #dee2e6;">${opp.market_odds > 0 ? '+' : ''}${opp.market_odds}</td>
                            <td style="padding: 12px; border: 1px solid #dee2e6;">${opp.flag_emojis || '—'}</td>
                            <td style="padding: 12px; border: 1px solid #dee2e6; color: ${opp.edge_percentage > 0 ? 'green' : 'red'};">${opp.edge_percentage.toFixed(1)}%</td>
                            <td style="padding: 12px; border: 1px solid #dee2e6;">$${opp.expected_value.toFixed(2)}</td>
                            <td style="padding: 12px; border: 1px solid #dee2e6;">${opp.confidence_score}/10</td>
                            <td style="padding: 12px; border: 1px solid #dee2e6;">$${opp.recommended_stake.toFixed(0)}</td>
                        </tr>
                    `;
                });
                
                html += `
                            </tbody>
                        </table>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        async function loadDataSummary() {
            try {
                const response = await fetch('/api/sharp/data-summary');
                const summary = await response.json();
                
                const resultsContainer = document.getElementById('results-container');
                resultsContainer.innerHTML = `
                    <div class="card">
                        <h3>📊 Data Summary</h3>
                        <p><strong>Games:</strong> ${summary.games_count}</p>
                        <p><strong>Sports:</strong> ${summary.sports.join(', ') || 'None'}</p>
                        <p><strong>Data Files:</strong> ${summary.data_files.length}</p>
                        <p><strong>Last Upload:</strong> ${summary.last_upload || 'None'}</p>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading data summary:', error);
            }
        }
    </script>
</body>
</html>
"""

SHARP_RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sharp Analysis Results</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border: 1px solid #dee2e6; }
        th { background: #f8f9fa; font-weight: 600; }
        .positive { color: #28a745; }
        .negative { color: #dc3545; }
        .nav-link { color: #667eea; text-decoration: none; margin-right: 20px; }
        .nav-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Sharp Analysis Results</h1>
            <p>Generated on {{ timestamp }}</p>
            <div style="margin-top: 20px;">
                <a href="/sharp" class="nav-link">← Back to Dashboard</a>
                <a href="/sharp/demo" class="nav-link">🔄 Run Demo Again</a>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ results.total_opportunities }}</div>
                <div class="stat-label">Total Opportunities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ results.qualified_opportunities }}</div>
                <div class="stat-label">Qualified Bets</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ results.high_confidence_count }}</div>
                <div class="stat-label">High Confidence</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ results.execution_time }}</div>
                <div class="stat-label">Execution Time</div>
            </div>
        </div>
        
        {% if results.opportunities %}
        <div class="card">
            <h2>🎯 Best Sharp Opportunities</h2>
            <table>
                <thead>
                    <tr>
                        <th>Match</th>
                        <th>Bet</th>
                        <th>Odds</th>
                        <th>Book</th>
                        <th>Flags</th>
                        <th>Fair Odds</th>
                        <th>Edge %</th>
                        <th>EV $</th>
                        <th>Confidence</th>
                        <th>Rationale</th>
                    </tr>
                </thead>
                <tbody>
                    {% for opp in results.opportunities %}
                    <tr>
                        <td>{{ opp.matchup }}</td>
                        <td>{{ opp.bet }}</td>
                        <td>{{ opp.odds }}</td>
                        <td>{{ opp.best_book }}</td>
                        <td>{{ opp.sharp_flags }}</td>
                        <td>{{ opp.fair_odds }}</td>
                        <td class="positive">{{ opp.edge }}</td>
                        <td class="positive">{{ opp.ev_dollar }}</td>
                        <td>{{ opp.confidence }}</td>
                        <td style="font-size: 0.9em;">{{ opp.rationale }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        <div class="card">
            <h3>📊 Summary Statistics</h3>
            <p><strong>Average Edge:</strong> {{ "%.1f"|format(results.summary_stats.avg_edge) }}%</p>
            <p><strong>Average Confidence:</strong> {{ "%.1f"|format(results.summary_stats.avg_confidence) }}/10</p>
            <p><strong>Total Recommended Stake:</strong> ${{ "%.0f"|format(results.summary_stats.total_recommended_stake) }}</p>
            <p><strong>Bankroll Utilization:</strong> {{ "%.1f"|format(results.summary_stats.bankroll_utilization) }}%</p>
        </div>
    </div>
</body>
</html>
"""

DATA_UPLOAD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Upload - Sharp Predictor</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
        .form-group select, .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        .btn:hover { background: #5a6fd8; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #5a6268; }
        .nav-link { color: #667eea; text-decoration: none; margin-right: 20px; }
        .nav-link:hover { text-decoration: underline; }
        .result { margin-top: 20px; padding: 15px; border-radius: 6px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📁 Data Upload</h1>
            <p>Upload CSV or JSON data for sharp analysis</p>
            <div style="margin-top: 20px;">
                <a href="/sharp" class="nav-link">← Back to Dashboard</a>
            </div>
        </div>
        
        <div class="card">
            <h2>📄 CSV Upload</h2>
            <form id="csv-upload-form" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="data-type">Data Type</label>
                    <select id="data-type" name="data_type">
                        <option value="odds">Odds Data</option>
                        <option value="public_betting">Public Betting Data</option>
                        <option value="line_movements">Line Movements</option>
                        <option value="games">Games</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="csv-file">CSV File</label>
                    <input type="file" id="csv-file" name="file" accept=".csv" required>
                </div>
                
                <button type="submit" class="btn">📤 Upload CSV</button>
                <button type="button" class="btn btn-secondary" onclick="downloadTemplate()">📋 Download Template</button>
            </form>
        </div>
        
        <div class="card">
            <h2>📝 JSON Upload</h2>
            <form id="json-upload-form">
                <div class="form-group">
                    <label for="json-data-type">Data Type</label>
                    <select id="json-data-type">
                        <option value="odds">Odds Data</option>
                        <option value="public_betting">Public Betting Data</option>
                        <option value="line_movements">Line Movements</option>
                        <option value="games">Games</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="json-content">JSON Content</label>
                    <textarea id="json-content" rows="10" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace;" placeholder='{"example": "data"}'></textarea>
                </div>
                
                <button type="submit" class="btn">📤 Upload JSON</button>
            </form>
        </div>
        
        <div id="upload-result"></div>
    </div>
    
    <script>
        document.getElementById('csv-upload-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('file', document.getElementById('csv-file').files[0]);
            formData.append('data_type', document.getElementById('data-type').value);
            
            try {
                const response = await fetch('/api/sharp/upload-csv', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                showResult(result, response.ok);
                
            } catch (error) {
                showResult({error: error.message}, false);
            }
        });
        
        document.getElementById('json-upload-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const response = await fetch('/api/sharp/upload-json', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        content: document.getElementById('json-content').value,
                        data_type: document.getElementById('json-data-type').value
                    })
                });
                
                const result = await response.json();
                showResult(result, response.ok);
                
            } catch (error) {
                showResult({error: error.message}, false);
            }
        });
        
        function showResult(result, success) {
            const resultDiv = document.getElementById('upload-result');
            const className = success ? 'success' : 'error';
            const message = success ? 
                `✅ Upload successful! Processed ${result.processed_rows || 'data'} successfully.` :
                `❌ Upload failed: ${result.error || result.message}`;
            
            resultDiv.innerHTML = `<div class="result ${className}">${message}</div>`;
        }
        
        async function downloadTemplate() {
            const dataType = document.getElementById('data-type').value;
            window.open(`/api/sharp/csv-template/${dataType}`, '_blank');
        }
    </script>
</body>
</html>
"""

MANUAL_ENTRY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manual Entry - Sharp Predictor</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        .btn:hover { background: #5a6fd8; }
        .nav-link { color: #667eea; text-decoration: none; margin-right: 20px; }
        .nav-link:hover { text-decoration: underline; }
        .result { margin-top: 20px; padding: 15px; border-radius: 6px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
        .checkbox-group input[type="checkbox"] { width: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✏️ Manual Entry</h1>
            <p>Create manual game entries for analysis</p>
            <div style="margin-top: 20px;">
                <a href="/sharp" class="nav-link">← Back to Dashboard</a>
            </div>
        </div>
        
        <div class="card">
            <h2>🏈 Game Information</h2>
            <form id="manual-entry-form">
                <div class="form-row">
                    <div class="form-group">
                        <label for="sport">Sport</label>
                        <select id="sport">
                            <option value="MLB">MLB</option>
                            <option value="NBA">NBA</option>
                            <option value="NFL">NFL</option>
                            <option value="NHL">NHL</option>
                            <option value="Soccer">Soccer</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="game-date">Game Date</label>
                        <input type="datetime-local" id="game-date">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="home-team">Home Team</label>
                        <input type="text" id="home-team" placeholder="e.g., Yankees" required>
                    </div>
                    <div class="form-group">
                        <label for="away-team">Away Team</label>
                        <input type="text" id="away-team" placeholder="e.g., Red Sox" required>
                    </div>
                </div>
                
                <h3>💰 Odds Information</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="ml-home">Moneyline Home</label>
                        <input type="number" id="ml-home" value="-150">
                    </div>
                    <div class="form-group">
                        <label for="ml-away">Moneyline Away</label>
                        <input type="number" id="ml-away" value="+130">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="spread-line">Spread Line</label>
                        <input type="number" id="spread-line" value="-2.5" step="0.5">
                    </div>
                    <div class="form-group">
                        <label for="total-line">Total Line</label>
                        <input type="number" id="total-line" value="8.5" step="0.5">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="book">Sportsbook</label>
                    <input type="text" id="book" value="Manual" placeholder="e.g., DraftKings">
                </div>
                
                <div class="checkbox-group">
                    <input type="checkbox" id="include-public">
                    <label for="include-public">Include Public Betting Data</label>
                </div>
                
                <div id="public-data" style="display: none;">
                    <h4>📊 Public Betting Percentages</h4>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="ml-home-bets">ML Home Bets %</label>
                            <input type="number" id="ml-home-bets" value="65" min="0" max="100">
                        </div>
                        <div class="form-group">
                            <label for="ml-home-money">ML Home Money %</label>
                            <input type="number" id="ml-home-money" value="72" min="0" max="100">
                        </div>
                    </div>
                </div>
                
                <div class="checkbox-group">
                    <input type="checkbox" id="include-predictions">
                    <label for="include-predictions">Include Model Predictions</label>
                </div>
                
                <div id="prediction-data" style="display: none;">
                    <h4>🎯 Model Predictions</h4>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="home-win-prob">Home Win Probability</label>
                            <input type="number" id="home-win-prob" value="0.58" min="0" max="1" step="0.01">
                        </div>
                        <div class="form-group">
                            <label for="spread-prob">Spread Cover Probability</label>
                            <input type="number" id="spread-prob" value="0.52" min="0" max="1" step="0.01">
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn">✅ Create Entry</button>
            </form>
        </div>
        
        <div id="entry-result"></div>
    </div>
    
    <script>
        // Initialize form
        document.getElementById('game-date').value = new Date().toISOString().slice(0, 16);
        
        // Toggle sections
        document.getElementById('include-public').addEventListener('change', (e) => {
            document.getElementById('public-data').style.display = e.target.checked ? 'block' : 'none';
        });
        
        document.getElementById('include-predictions').addEventListener('change', (e) => {
            document.getElementById('prediction-data').style.display = e.target.checked ? 'block' : 'none';
        });
        
        // Handle form submission
        document.getElementById('manual-entry-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                sport: document.getElementById('sport').value,
                home_team: document.getElementById('home-team').value,
                away_team: document.getElementById('away-team').value,
                game_date: document.getElementById('game-date').value,
                moneyline_home: parseInt(document.getElementById('ml-home').value),
                moneyline_away: parseInt(document.getElementById('ml-away').value),
                spread_line: parseFloat(document.getElementById('spread-line').value),
                total_line: parseFloat(document.getElementById('total-line').value),
                book: document.getElementById('book').value,
                include_public_data: document.getElementById('include-public').checked,
                include_predictions: document.getElementById('include-predictions').checked
            };
            
            if (formData.include_public_data) {
                formData.ml_home_bets = parseFloat(document.getElementById('ml-home-bets').value);
                formData.ml_home_money = parseFloat(document.getElementById('ml-home-money').value);
            }
            
            if (formData.include_predictions) {
                formData.home_win_prob = parseFloat(document.getElementById('home-win-prob').value);
                formData.away_win_prob = 1 - formData.home_win_prob;
                formData.spread_prob = parseFloat(document.getElementById('spread-prob').value);
                formData.over_prob = 0.5; // Default
            }
            
            try {
                const response = await fetch('/api/sharp/manual-entry', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                showResult(result, response.ok);
                
                if (response.ok) {
                    document.getElementById('manual-entry-form').reset();
                    document.getElementById('game-date').value = new Date().toISOString().slice(0, 16);
                }
                
            } catch (error) {
                showResult({error: error.message}, false);
            }
        });
        
        function showResult(result, success) {
            const resultDiv = document.getElementById('entry-result');
            const className = success ? 'success' : 'error';
            const message = success ? 
                `✅ Entry created successfully! Game ID: ${result.game_id}` :
                `❌ Entry failed: ${result.error || result.message}`;
            
            resultDiv.innerHTML = `<div class="result ${className}">${message}</div>`;
        }
    </script>
</body>
</html>
"""