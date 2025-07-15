#!/usr/bin/env python3
"""
Flask Web App Example for Universal Betting Dashboard

This demonstrates how to integrate the betting model into a web application.
Provides REST API endpoints for scanning, status, and configuration.
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from main import get_scan_json, get_model_status, run_betting_scan
import json
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML template for basic web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Betting Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .scan-form { background: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .results { background: #e8f5e8; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .error { background: #f5e8e8; color: #d32f2f; }
        .pick { background: white; margin: 10px 0; padding: 15px; border-left: 4px solid #4caf50; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .metric { background: #f0f0f0; padding: 15px; text-align: center; border-radius: 5px; }
        button { background: #4caf50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #45a049; }
        select, input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        .loading { text-align: center; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Universal Betting Dashboard</h1>
            <p>Sophisticated Sports Betting Analysis with Sharp Detection</p>
        </div>
        
        <div class="scan-form">
            <h3>📡 Run Betting Scan</h3>
            <form id="scanForm">
                <label>Mode:</label>
                <select id="mode">
                    <option value="manual">Manual</option>
                    <option value="morning">Morning (8:00 ET)</option>
                    <option value="midday">Midday (12:00 ET)</option>
                    <option value="final">Final (4:30 ET)</option>
                </select>
                
                <label>Bankroll ($):</label>
                <input type="number" id="bankroll" value="2500" min="100" step="100">
                
                <button type="submit">🚀 Start Scan</button>
            </form>
        </div>
        
        <div id="results"></div>
        
        <div class="scan-form">
            <h3>⚙️ Model Status</h3>
            <button onclick="checkStatus()">📊 Check Status</button>
            <div id="status"></div>
        </div>
    </div>

    <script>
        document.getElementById('scanForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const mode = document.getElementById('mode').value;
            const bankroll = document.getElementById('bankroll').value;
            const results = document.getElementById('results');
            
            results.innerHTML = '<div class="loading">🔄 Scanning markets...</div>';
            
            try {
                const response = await fetch(`/api/scan?mode=${mode}&bankroll=${bankroll}`);
                const data = await response.json();
                
                if (data.error) {
                    results.innerHTML = `<div class="results error"><h3>❌ Error</h3><p>${data.error}</p></div>`;
                    return;
                }
                
                let html = `
                    <div class="results">
                        <h3>🎯 Scan Results - ${data.mode.toUpperCase()}</h3>
                        <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                        
                        <div class="metrics">
                            <div class="metric">
                                <strong>Total Candidates</strong><br>
                                <span style="font-size: 24px;">${data.total_candidates}</span>
                            </div>
                            <div class="metric">
                                <strong>Qualified Picks</strong><br>
                                <span style="font-size: 24px;">${data.qualified_candidates}</span>
                            </div>
                            <div class="metric">
                                <strong>Official Picks</strong><br>
                                <span style="font-size: 24px;">${data.official_picks.length}</span>
                            </div>
                            <div class="metric">
                                <strong>Execution Time</strong><br>
                                <span style="font-size: 24px;">${data.execution_time}s</span>
                            </div>
                        </div>
                `;
                
                if (data.official_picks.length > 0) {
                    html += '<h4>🏆 Official Picks:</h4>';
                    data.official_picks.forEach(pick => {
                        const flags = pick.flags.length > 0 ? ` | ${pick.flags.join(', ')}` : '';
                        html += `
                            <div class="pick">
                                <strong>${pick.sport}: ${pick.pick}</strong><br>
                                Odds: ${pick.odds > 0 ? '+' : ''}${pick.odds} | 
                                EV: +${pick.ev}% | 
                                Confidence: ${pick.confidence}/10 | 
                                Stake: $${pick.stake}${flags}
                            </div>
                        `;
                    });
                } else {
                    html += '<p><em>No qualified picks found in this scan.</em></p>';
                }
                
                html += `
                        <h4>📊 Risk Metrics:</h4>
                        <p>Total Risk: $${data.risk_metrics.total_risk} (${data.risk_metrics.risk_percentage}%)</p>
                        <p>Remaining Capacity: $${data.risk_metrics.remaining_capacity}</p>
                        
                        <h4>🔬 Model Performance:</h4>
                        <p>Average EV: ${data.model_performance.avg_ev}% | Average Confidence: ${data.model_performance.avg_confidence}/10</p>
                        <p>Qualification Rate: ${data.model_performance.qualification_rate}%</p>
                    </div>
                `;
                
                results.innerHTML = html;
                
            } catch (error) {
                results.innerHTML = `<div class="results error"><h3>❌ Error</h3><p>${error.message}</p></div>`;
            }
        });
        
        async function checkStatus() {
            const status = document.getElementById('status');
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                let html = `
                    <div class="results">
                        <h4>Model Configuration:</h4>
                        <p>Min EV Threshold: ${data.model_config.min_ev_threshold}%</p>
                        <p>Min Confidence: ${data.model_config.min_confidence_threshold}/10</p>
                        <p>Monte Carlo Simulations: ${data.model_config.mc_simulations}</p>
                        <p>Default Bankroll: $${data.model_config.default_bankroll}</p>
                        
                        <h4>Supported Sports:</h4>
                        <p>${data.supported_sports.join(', ')}</p>
                        
                        <h4>Status:</h4>
                        <p style="color: green;"><strong>${data.status.toUpperCase()}</strong> | Version ${data.version}</p>
                    </div>
                `;
                
                status.innerHTML = html;
                
            } catch (error) {
                status.innerHTML = `<div class="results error">Error: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Serve the main web interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/scan', methods=['GET'])
def api_scan():
    """API endpoint for running betting scans."""
    try:
        mode = request.args.get('mode', 'manual')
        bankroll = float(request.args.get('bankroll', 2500))
        
        logger.info(f"Starting {mode} scan with bankroll ${bankroll}")
        
        # Get JSON result from the main betting system
        json_result = get_scan_json(mode, bankroll)
        result_data = json.loads(json_result)
        
        logger.info(f"Scan completed: {result_data.get('total_candidates', 0)} candidates, "
                   f"{len(result_data.get('official_picks', []))} picks")
        
        return jsonify(result_data)
        
    except Exception as e:
        logger.error(f"Scan error: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'failed'
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """API endpoint for model status and configuration."""
    try:
        status_data = get_model_status()
        return jsonify(status_data)
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/scan-raw', methods=['GET'])
def api_scan_raw():
    """API endpoint returning raw Python objects (for advanced integrations)."""
    try:
        mode = request.args.get('mode', 'manual')
        bankroll = float(request.args.get('bankroll', 2500))
        
        # Get raw result object from the betting system
        result = run_betting_scan(mode, bankroll)
        
        # Convert to dict for JSON serialization
        result_dict = {
            'timestamp': result.timestamp,
            'mode': result.mode,
            'bankroll': result.bankroll,
            'total_candidates': result.total_candidates,
            'qualified_candidates': result.qualified_candidates,
            'official_picks': result.official_picks,
            'execution_time': result.execution_time,
            'sports_scanned': result.sports_scanned,
            'risk_metrics': result.risk_metrics,
            'model_performance': result.model_performance
        }
        
        return jsonify(result_dict)
        
    except Exception as e:
        logger.error(f"Raw scan error: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'failed'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    })

if __name__ == '__main__':
    print("🚀 Starting Universal Betting Dashboard Web App")
    print("📊 Access the dashboard at: http://localhost:5000")
    print("📡 API endpoints:")
    print("   GET /api/scan?mode=manual&bankroll=2500")
    print("   GET /api/status")
    print("   GET /health")
    
    # Run the Flask app
    app.run(debug=False, host='0.0.0.0', port=5000)
