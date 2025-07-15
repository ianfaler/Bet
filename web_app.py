#!/usr/bin/env python3
"""
Flask Web App for Universal Betting Dashboard

Production-ready web application providing REST API endpoints for 
the sports betting analysis system.
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from app import get_scan_json, get_model_status, run_betting_scan
import json
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML template for web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Betting Dashboard</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header { 
            text-align: center; 
            color: #333; 
            margin-bottom: 40px; 
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .scan-form { 
            background: #f8f9fa; 
            padding: 25px; 
            border-radius: 10px; 
            margin-bottom: 30px; 
            border-left: 5px solid #667eea;
        }
        .results { 
            background: #e8f5e8; 
            padding: 20px; 
            border-radius: 10px; 
            margin-top: 20px; 
        }
        .error { 
            background: #f5e8e8; 
            color: #d32f2f; 
        }
        .pick { 
            background: white; 
            margin: 15px 0; 
            padding: 20px; 
            border-left: 5px solid #4caf50; 
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .metrics { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin: 30px 0; 
        }
        .metric { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white;
            padding: 20px; 
            text-align: center; 
            border-radius: 10px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .metric h3 {
            margin: 0 0 10px 0;
            font-size: 2em;
        }
        button { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            padding: 12px 25px; 
            border: none; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 16px;
            transition: transform 0.2s;
        }
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        select, input { 
            padding: 12px; 
            margin: 8px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 16px;
        }
        .loading { 
            text-align: center; 
            padding: 40px; 
            font-size: 18px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .status-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Universal Betting Dashboard</h1>
            <p>Sophisticated Sports Betting Analysis with Sharp Detection & Risk Management</p>
        </div>
        
        <div class="scan-form">
            <h3>📡 Run Betting Scan</h3>
            <form id="scanForm">
                <label><strong>Mode:</strong></label>
                <select id="mode">
                    <option value="manual">Manual Scan</option>
                    <option value="morning">Morning Scan (8:00 ET)</option>
                    <option value="midday">Midday Scan (12:00 ET)</option>
                    <option value="final">Final Scan (4:30 ET)</option>
                </select>
                
                <label><strong>Bankroll ($):</strong></label>
                <input type="number" id="bankroll" value="2500" min="100" step="100">
                
                <button type="submit">🚀 Start Analysis</button>
            </form>
        </div>
        
        <div id="results"></div>
        
        <div class="scan-form">
            <h3>⚙️ System Status</h3>
            <button onclick="checkStatus()">📊 Check Model Status</button>
            <div id="status"></div>
        </div>
    </div>

    <script>
        document.getElementById('scanForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const mode = document.getElementById('mode').value;
            const bankroll = document.getElementById('bankroll').value;
            const results = document.getElementById('results');
            
            results.innerHTML = '<div class="loading">🔄 Analyzing markets and generating picks...</div>';
            
            try {
                const response = await fetch(`/api/scan?mode=${mode}&bankroll=${bankroll}`);
                const data = await response.json();
                
                if (data.error) {
                    results.innerHTML = `<div class="results error"><h3>❌ Error</h3><p>${data.error}</p></div>`;
                    return;
                }
                
                let html = '<div class="results"><h3>✅ Scan Results</h3>';
                
                // Metrics
                html += '<div class="metrics">';
                html += `<div class="metric"><h3>${data.total_candidates}</h3><p>Total Candidates</p></div>`;
                html += `<div class="metric"><h3>${data.qualified_candidates}</h3><p>Qualified Bets</p></div>`;
                html += `<div class="metric"><h3>${data.official_picks.length}</h3><p>Final Picks</p></div>`;
                html += `<div class="metric"><h3>${data.execution_time}s</h3><p>Execution Time</p></div>`;
                html += '</div>';
                
                // Risk metrics
                if (data.risk_metrics) {
                    html += '<div class="metrics">';
                    html += `<div class="metric"><h3>$${data.risk_metrics.total_risk.toFixed(2)}</h3><p>Total Risk</p></div>`;
                    html += `<div class="metric"><h3>${data.risk_metrics.risk_percentage}%</h3><p>Risk %</p></div>`;
                    html += `<div class="metric"><h3>$${data.risk_metrics.remaining_capacity.toFixed(2)}</h3><p>Remaining Capacity</p></div>`;
                    html += '</div>';
                }
                
                // Official picks
                if (data.official_picks && data.official_picks.length > 0) {
                    html += '<h4>🏆 Official Picks:</h4>';
                    data.official_picks.forEach((pick, index) => {
                        const flags = pick.flags && pick.flags.length > 0 ? `[${pick.flags.join(', ')}]` : '';
                        html += `<div class="pick">
                            <strong>#${index + 1}: ${pick.bet_type}</strong><br>
                            <strong>Odds:</strong> ${pick.odds > 0 ? '+' : ''}${pick.odds}<br>
                            <strong>EV:</strong> +${pick.ev.toFixed(1)}% | 
                            <strong>Confidence:</strong> ${pick.confidence}/10 | 
                            <strong>Stake:</strong> $${pick.stake.toFixed(2)} ${flags}
                        </div>`;
                    });
                } else {
                    html += '<p><strong>⚠️ No qualified picks found with current thresholds</strong></p>';
                    html += '<p>This indicates good selectivity - the model maintains high standards.</p>';
                }
                
                html += '</div>';
                results.innerHTML = html;
                
            } catch (error) {
                results.innerHTML = `<div class="results error"><h3>❌ Network Error</h3><p>${error.message}</p></div>`;
            }
        });
        
        async function checkStatus() {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = '<div class="loading">🔄 Checking system status...</div>';
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                let html = '<div class="status-grid">';
                
                // Model config
                html += '<div class="status-card">';
                html += '<h4>🎛️ Model Configuration</h4>';
                html += `<p><strong>Min EV:</strong> ${data.model_config.min_ev_threshold}%</p>`;
                html += `<p><strong>Min Confidence:</strong> ${data.model_config.min_confidence_threshold}/10</p>`;
                html += `<p><strong>Simulations:</strong> ${data.model_config.mc_simulations.toLocaleString()}</p>`;
                html += `<p><strong>Default Bankroll:</strong> $${data.model_config.default_bankroll.toLocaleString()}</p>`;
                html += '</div>';
                
                // Supported sports
                html += '<div class="status-card">';
                html += '<h4>🏈 Supported Sports</h4>';
                html += `<p>${data.supported_sports.join(', ')}</p>`;
                html += '</div>';
                
                // Features
                html += '<div class="status-card">';
                html += '<h4>⚡ Model Features</h4>';
                data.model_features.forEach(feature => {
                    html += `<p>• ${feature}</p>`;
                });
                html += '</div>';
                
                // System status
                html += '<div class="status-card">';
                html += '<h4>📊 System Status</h4>';
                html += `<p><strong>Status:</strong> ${data.status}</p>`;
                html += `<p><strong>Version:</strong> ${data.version}</p>`;
                html += `<p><strong>Last Check:</strong> ${new Date().toLocaleTimeString()}</p>`;
                html += '</div>';
                
                html += '</div>';
                statusDiv.innerHTML = html;
                
            } catch (error) {
                statusDiv.innerHTML = `<div class="error"><h4>❌ Status Check Failed</h4><p>${error.message}</p></div>`;
            }
        }
    </script>
</body>
</html>
"""

# API Routes
@app.route('/')
def home():
    """Serve the main web interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/scan')
def api_scan():
    """API endpoint for betting scan."""
    try:
        mode = request.args.get('mode', 'manual')
        bankroll = request.args.get('bankroll', type=float)
        
        logger.info(f"API scan request - Mode: {mode}, Bankroll: {bankroll}")
        
        # Get JSON result
        json_result = get_scan_json(mode, bankroll)
        result = json.loads(json_result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API scan error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'failed'
        }), 500

@app.route('/api/status')
def api_status():
    """API endpoint for model status."""
    try:
        status = get_model_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"API status error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'failed'
        }), 500

@app.route('/health')
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Universal Betting Dashboard',
        'version': '2.0.0'
    })

@app.route('/api/scan-raw')
def api_scan_raw():
    """API endpoint returning raw Python objects (for advanced integrations)."""
    try:
        mode = request.args.get('mode', 'manual')
        bankroll = request.args.get('bankroll', type=float)
        
        # Get raw result object
        result = run_betting_scan(mode, bankroll)
        
        # Convert dataclasses to dict for JSON serialization
        from dataclasses import asdict
        return jsonify(asdict(result))
        
    except Exception as e:
        logger.error(f"API scan-raw error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'failed'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/api/scan',
            '/api/status', 
            '/health',
            '/api/scan-raw'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Universal Betting Dashboard Web App")
    print("=" * 50)
    print("📱 Web Interface: http://localhost:5000")
    print("🔌 API Endpoints:")
    print("   • GET /api/scan?mode={mode}&bankroll={amount}")
    print("   • GET /api/status")
    print("   • GET /health")
    print("   • GET /api/scan-raw")
    print("=" * 50)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)