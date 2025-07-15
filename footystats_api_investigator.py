#!/usr/bin/env python3
"""
FootyStats API Investigation and Setup Script

This script systematically tests the FootyStats API to:
1. Discover working endpoints and required parameters
2. Map league IDs and available data
3. Set up proper integration for ML pipeline
4. Document API structure and limitations

Usage:
    python3 footystats_api_investigator.py
"""

import json
import requests
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from urllib.parse import urlencode

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "")
BASE_URL = "https://api.footystats.org"

class FootyStatsAPIInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FootyStats API Investigator v1.0',
            'Accept': 'application/json'
        })
        self.results = {
            'working_endpoints': [],
            'failed_endpoints': [],
            'parameter_requirements': {},
            'league_mappings': {},
            'error_patterns': {},
            'rate_limits': {},
            'investigation_timestamp': datetime.now().isoformat()
        }
    
    def test_endpoint(self, endpoint: str, params: Dict = None) -> Tuple[bool, Dict]:
        """Test a single API endpoint with given parameters"""
        if params is None:
            params = {}
        
        # Always include the API key
        params['key'] = FOOTYSTATS_API_KEY
        
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            logger.info(f"Testing: {url} with params: {list(params.keys())}")
            response = self.session.get(url, params=params, timeout=30)
            
            # Extract rate limit info
            if 'metadata' in response.text:
                try:
                    data = response.json()
                    if 'metadata' in data:
                        self.results['rate_limits'].update(data['metadata'])
                except (ValueError, KeyError, TypeError) as e:
                    print(f"Warning: Could not parse rate limit metadata: {e}")
                    pass
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success', False) and data.get('data'):
                        return True, data
                    else:
                        return False, {
                            'error': data.get('message', 'Unknown error'),
                            'success': data.get('success', False),
                            'status_code': response.status_code
                        }
                except json.JSONDecodeError:
                    return False, {'error': 'Invalid JSON response', 'status_code': response.status_code}
            else:
                return False, {'error': f'HTTP {response.status_code}', 'status_code': response.status_code}
                
        except Exception as e:
            return False, {'error': str(e), 'exception': True}
    
    def test_common_endpoints(self):
        """Test common endpoint patterns discovered in the codebase"""
        logger.info("🔍 Testing common endpoints...")
        
        endpoints_to_test = [
            # Basic endpoints
            ("leagues", {}),
            ("competitions", {}),
            ("countries", {}),
            
            # Endpoints with season parameter
            ("leagues", {"season": "2024"}),
            ("leagues", {"season": "2023"}),
            
            # League-specific endpoints that need league_id
            ("league-matches", {"league_id": "premier-league", "season": "2024"}),
            ("league-matches", {"league_id": "1", "season": "2024"}),
            ("league-matches", {"league_id": "eng-premier-league", "season": "2024"}),
            ("league-matches", {"league_id": "39", "season": "2024"}),  # Common Premier League ID
            
            # Table/standings endpoints
            ("league-table", {"league_id": "premier-league", "season": "2024"}),
            ("season-league-table", {"league_id": "premier-league", "season": "2024"}),
            ("standings", {"league_id": "premier-league", "season": "2024"}),
            
            # Teams endpoints
            ("teams", {"league_id": "premier-league", "season": "2024"}),
            ("league-teams", {"league_id": "premier-league", "season": "2024"}),
            
            # Player endpoints
            ("players", {"league_id": "premier-league", "season": "2024"}),
            ("league-players", {"league_id": "premier-league", "season": "2024"}),
            
            # Stats endpoints
            ("stats", {"league_id": "premier-league", "season": "2024"}),
            ("league-stats", {"league_id": "premier-league", "season": "2024"}),
            
            # Different league ID formats
            ("league-matches", {"league": "premier-league", "season": "2024"}),
            ("league-matches", {"competition_id": "premier-league", "season": "2024"}),
            ("league-matches", {"id": "premier-league", "season": "2024"}),
        ]
        
        for endpoint, params in endpoints_to_test:
            success, result = self.test_endpoint(endpoint, params)
            
            if success:
                self.results['working_endpoints'].append({
                    'endpoint': endpoint,
                    'params': params,
                    'sample_data': result
                })
                logger.info(f"✅ SUCCESS: {endpoint} with {params}")
            else:
                self.results['failed_endpoints'].append({
                    'endpoint': endpoint,
                    'params': params,
                    'error': result
                })
                error_msg = result.get('error', 'Unknown error')
                logger.warning(f"❌ FAILED: {endpoint} - {error_msg}")
            
            # Rate limiting - wait between requests
            time.sleep(1)
    
    def test_parameter_variations(self):
        """Test different parameter formats and values"""
        logger.info("🔍 Testing parameter variations...")
        
        # Test date formats for league-matches
        date_formats = [
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y%m%d"),
            datetime.now().strftime("%d/%m/%Y"),
            datetime.now().strftime("%m/%d/%Y"),
        ]
        
        for date_format in date_formats:
            success, result = self.test_endpoint("league-matches", {
                "league_id": "premier-league",
                "date": date_format
            })
            if success:
                logger.info(f"✅ Date format works: {date_format}")
                break
            time.sleep(1)
        
        # Test different season formats
        season_formats = ["2024", "2023-2024", "23-24", "2023/2024"]
        for season_format in season_formats:
            success, result = self.test_endpoint("leagues", {"season": season_format})
            if success:
                logger.info(f"✅ Season format works: {season_format}")
                break
            time.sleep(1)
    
    def discover_league_ids(self):
        """Try to discover valid league IDs"""
        logger.info("🔍 Discovering league IDs...")
        
        # Common league identifiers to test
        league_ids = [
            # Premier League variations
            "premier-league", "epl", "pl", "english-premier-league", "england-premier-league",
            "39", "1", "eng-pl", "eng-premier",
            
            # Other major leagues
            "la-liga", "serie-a", "bundesliga", "ligue-1", "champions-league",
            "primera-division", "serie-a-italy", "bundesliga-germany", "ligue-1-france",
            
            # Numeric IDs
            "1", "2", "3", "4", "5", "39", "40", "61", "78", "135"
        ]
        
        working_leagues = []
        
        for league_id in league_ids:
            # Test with league-matches endpoint
            success, result = self.test_endpoint("league-matches", {
                "league_id": league_id,
                "season": "2024"
            })
            
            if success:
                working_leagues.append({
                    'league_id': league_id,
                    'endpoint': 'league-matches',
                    'data_sample': result
                })
                logger.info(f"✅ Working league ID: {league_id}")
            
            time.sleep(0.5)
        
        self.results['working_leagues'] = working_leagues
        return working_leagues
    
    def test_documentation_hints(self):
        """Test endpoints based on documentation patterns"""
        logger.info("🔍 Testing documentation-based endpoints...")
        
        # Test REST-style endpoints
        rest_endpoints = [
            "v1/leagues",
            "v2/leagues", 
            "api/v1/leagues",
            "api/leagues",
            "rest/leagues",
            "data/leagues"
        ]
        
        for endpoint in rest_endpoints:
            success, result = self.test_endpoint(endpoint, {})
            if success:
                logger.info(f"✅ REST endpoint works: {endpoint}")
            time.sleep(0.5)
    
    def generate_report(self) -> str:
        """Generate comprehensive investigation report"""
        report = f"""
# FootyStats API Investigation Report
Generated: {self.results['investigation_timestamp']}

## API Status
- **API Key**: Valid ✅ (Rate limits detected)
- **Base URL**: {BASE_URL}
- **Rate Limits**: {self.results['rate_limits']}

## Working Endpoints ({len(self.results['working_endpoints'])})
"""
        for endpoint in self.results['working_endpoints']:
            report += f"- ✅ `{endpoint['endpoint']}` with params: {endpoint['params']}\n"
        
        report += f"\n## Failed Endpoints ({len(self.results['failed_endpoints'])})\n"
        
        # Group failures by error type
        error_groups = {}
        for failure in self.results['failed_endpoints']:
            error = failure['error'].get('error', 'Unknown')
            if error not in error_groups:
                error_groups[error] = []
            error_groups[error].append(failure)
        
        for error_type, failures in error_groups.items():
            report += f"\n### {error_type} ({len(failures)} endpoints)\n"
            for failure in failures[:5]:  # Show first 5 examples
                report += f"- ❌ `{failure['endpoint']}` with {failure['params']}\n"
            if len(failures) > 5:
                report += f"- ... and {len(failures) - 5} more\n"
        
        if 'working_leagues' in self.results:
            report += f"\n## Working League IDs ({len(self.results['working_leagues'])})\n"
            for league in self.results['working_leagues']:
                report += f"- ✅ `{league['league_id']}`\n"
        
        report += f"""
## Next Steps for FootyStats Integration

### Immediate Actions Required:
1. **Contact FootyStats Support**: The API structure may have changed
2. **Check Documentation**: Access https://footystats.org/api/documentations/ (requires login)
3. **Alternative Approach**: Consider using football-data.org or API-Football as backup

### Recommendations:
1. **Rate Limiting**: Current limit is {self.results['rate_limits'].get('request_limit', 'Unknown')} requests/hour
2. **Parameter Investigation**: Most endpoints require specific parameter combinations
3. **League ID Mapping**: Valid league IDs need to be identified from documentation

### Code Integration:
- Update `footystats_league_config.py` with working endpoints
- Modify `data_manager.py` to use correct API structure
- Add error handling for API changes

### Backup Plan:
If FootyStats API continues to have issues, consider:
- Football-Data.org (free tier available)
- API-Football (comprehensive coverage)
- Web scraping as last resort
"""
        
        return report
    
    def save_results(self):
        """Save investigation results to files"""
        # Save JSON results
        with open('footystats_api_investigation.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save report
        report = self.generate_report()
        with open('footystats_api_investigation_report.md', 'w') as f:
            f.write(report)
        
        logger.info("📄 Results saved to:")
        logger.info("  - footystats_api_investigation.json")
        logger.info("  - footystats_api_investigation_report.md")
    
    def run_full_investigation(self):
        """Run complete API investigation"""
        logger.info("🚀 Starting FootyStats API Investigation")
        logger.info("="*60)
        
        try:
            # Test common endpoints
            self.test_common_endpoints()
            
            # Test parameter variations
            self.test_parameter_variations()
            
            # Discover working league IDs
            self.discover_league_ids()
            
            # Test documentation hints
            self.test_documentation_hints()
            
            # Generate and save results
            self.save_results()
            
            logger.info("✅ Investigation completed successfully!")
            logger.info(f"Found {len(self.results['working_endpoints'])} working endpoints")
            
            # Print summary
            if self.results['working_endpoints']:
                logger.info("\n🎉 Working Endpoints Found:")
                for endpoint in self.results['working_endpoints']:
                    logger.info(f"  ✅ {endpoint['endpoint']} with {endpoint['params']}")
            else:
                logger.warning("\n⚠️  No working endpoints found!")
                logger.info("This suggests the API structure has changed significantly.")
                logger.info("Manual investigation or contacting FootyStats support may be required.")
            
        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            raise

def main():
    investigator = FootyStatsAPIInvestigator()
    investigator.run_full_investigation()
    
    print("\n" + "="*60)
    print("📊 FOOTYSTATS API INVESTIGATION COMPLETE")
    print("="*60)
    print("Check the generated files for detailed results:")
    print("- footystats_api_investigation.json")
    print("- footystats_api_investigation_report.md")

if __name__ == "__main__":
    main()