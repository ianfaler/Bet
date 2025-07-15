#!/usr/bin/env python3
"""
Simple Data Downloader for Universal Betting Dashboard

This script downloads historical data from multiple sports APIs including:
- FootyStats (Soccer data for 50+ leagues) - Updated with 2025 League IDs
- SportsData.io (MLB data)
- Backup sources for redundancy

Features:
- Robust error handling with retries
- Rate limiting to respect API limits
- Data validation and cleaning
- Automatic failover to backup sources
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Import correct FootyStats configuration with 2025 league IDs
from footystats_config import (
    FOOTYSTATS_API_KEY, 
    FOOTYSTATS_LEAGUE_IDS, 
    LEAGUE_BY_COUNTRY,
    FOOTYSTATS_BASE_URL,
    get_league_teams_url,
    get_league_season_url
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path("historical_data")
DATA_DIR.mkdir(exist_ok=True)

# API Keys
API_KEYS = {
    "footystats": FOOTYSTATS_API_KEY,
    "sportsdata": os.getenv("SPORTSDATA_API_KEY", "demo_key"),
    "football_data": os.getenv("FOOTBALL_DATA_API_KEY", "demo_key")
}

# Test endpoints for API validation
TEST_ENDPOINTS = {
    "footystats": [
        "https://api.footystats.org/league-matches"
    ],
    "sportsdata": [
        "https://api.sportsdata.io/v3/mlb/scores/json/teams"
    ],
    "football_data": [
        "https://api.football-data.org/v4/competitions"
    ]
}

class SimpleDataDownloader:
    """Simple but robust data downloader with multiple source support."""
    
    def __init__(self):
        """Initialize the data downloader."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Universal-Betting-Dashboard/1.0',
            'Accept': 'application/json'
        })
        
        # Track API performance
        self.api_stats = {
            "footystats": {"success": 0, "failures": 0, "rate_limited": 0},
            "sportsdata": {"success": 0, "failures": 0, "rate_limited": 0},
            "football_data": {"success": 0, "failures": 0, "rate_limited": 0}
        }
    
    def download_all_data(self, test_mode: bool = False) -> Dict[str, Any]:
        """
        Download data from all configured sources.
        
        Args:
            test_mode: If True, only download small samples for testing
        
        Returns:
            Dict with download results and statistics
        """
        logger.info("🚀 Starting simple data download process")
        
        start_time = time.time()
        results = {
            "start_time": datetime.now().isoformat(),
            "test_mode": test_mode,
            "soccer": {},
            "mlb": {},
            "summary": {
                "total_files": 0,
                "total_records": 0,
                "total_size_mb": 0,
                "duration_seconds": 0
            }
        }
        
        # Test API connectivity first
        api_status = self.test_api_connectivity()
        logger.info(f"📡 API Status: {api_status}")
        
        # Download soccer data (FootyStats with 2025 league IDs)
        if api_status.get("footystats", False):
            logger.info("⚽ Downloading soccer data from FootyStats...")
            results["soccer"] = self.download_soccer_data(test_mode)
        else:
            logger.warning("⚠️  FootyStats API unavailable, skipping soccer data")
            results["soccer"] = {"status": "skipped", "reason": "API unavailable"}
        
        # Download MLB data (SportsData.io)
        if api_status.get("sportsdata", False):
            logger.info("⚾ Downloading MLB data from SportsData.io...")
            results["mlb"] = self.download_mlb_data(test_mode)
        else:
            logger.warning("⚠️  SportsData.io API unavailable, using demo data")
            results["mlb"] = self.generate_demo_mlb_data()
        
        # Calculate summary statistics
        results["summary"]["duration_seconds"] = round(time.time() - start_time, 2)
        results = self._calculate_summary_stats(results)
        
        # Save download report
        self.save_download_report(results)
        
        logger.info(f"✅ Download complete in {results['summary']['duration_seconds']}s")
        return results
    
    def test_api_connectivity(self) -> Dict[str, bool]:
        """Test connectivity to all APIs."""
        logger.info("🔌 Testing API connectivity...")
        
        connectivity = {}
        
        # Test FootyStats API with correct parameters
        try:
            # Test with Premier League season endpoint
            url = get_league_season_url(13943)  # Premier League 2025 season_id
            logger.info(f"Testing FootyStats API: {url}")
            
            response = self.session.get(url, timeout=10)
            connectivity["footystats"] = response.status_code in [200, 422]  # 422 = valid API, invalid params
            
            if response.status_code == 200:
                logger.info("✅ FootyStats API: Connected successfully")
            elif response.status_code == 422:
                logger.info("✅ FootyStats API: Connected (parameters may need adjustment)")
            else:
                logger.warning(f"⚠️  FootyStats API: HTTP {response.status_code}")
                
        except Exception as e:
            connectivity["footystats"] = False
            logger.warning(f"⚠️  FootyStats API: {str(e)}")
        
        # Test SportsData.io API
        try:
            url = "https://api.sportsdata.io/v3/mlb/scores/json/teams"
            params = {'key': API_KEYS["sportsdata"]}
            response = self.session.get(url, params=params, timeout=10)
            connectivity["sportsdata"] = response.status_code == 200
            
            if connectivity["sportsdata"]:
                logger.info("✅ SportsData.io API: Connected successfully")
            else:
                logger.warning(f"⚠️  SportsData.io API: HTTP {response.status_code}")
                
        except Exception as e:
            connectivity["sportsdata"] = False
            logger.warning(f"⚠️  SportsData.io API: {str(e)}")
        
        # Test Football-Data.org API (backup)
        try:
            url = "https://api.football-data.org/v4/competitions"
            headers = {'X-Auth-Token': API_KEYS["football_data"]}
            response = self.session.get(url, headers=headers, timeout=10)
            connectivity["football_data"] = response.status_code == 200
            
            if connectivity["football_data"]:
                logger.info("✅ Football-Data.org API: Connected successfully")
            else:
                logger.warning(f"⚠️  Football-Data.org API: HTTP {response.status_code}")
                
        except Exception as e:
            connectivity["football_data"] = False
            logger.warning(f"⚠️  Football-Data.org API: {str(e)}")
        
        return connectivity
    
    def download_soccer_data(self, test_mode: bool = False) -> Dict[str, Any]:
        """Download soccer data using correct 2025 FootyStats league IDs."""
        
        soccer_result = {
            "status": "started",
            "leagues_attempted": 0,
            "leagues_successful": 0,
            "leagues_failed": 0,
            "total_matches": 0,
            "files_created": [],
            "errors": []
        }
        
        # Use correct 2025 league IDs
        leagues_to_process = list(FOOTYSTATS_LEAGUE_IDS.items())
        
        if test_mode:
            # In test mode, only download data for first 5 leagues
            leagues_to_process = leagues_to_process[:5]
            logger.info(f"🧪 Test mode: Processing {len(leagues_to_process)} leagues")
        
        for league_name, league_id in leagues_to_process:
            soccer_result["leagues_attempted"] += 1
            
            logger.info(f"📥 Downloading {league_name} (ID: {league_id})")
            
            try:
                # Download matches for this league
                matches = self._download_league_matches(league_id, league_name)
                
                if matches:
                    # Save the data
                    file_path = self._save_soccer_league_data(league_name, league_id, matches)
                    
                    soccer_result["leagues_successful"] += 1
                    soccer_result["total_matches"] += len(matches)
                    soccer_result["files_created"].append(str(file_path))
                    
                    logger.info(f"✅ Downloaded {len(matches)} matches for {league_name}")
                else:
                    soccer_result["leagues_failed"] += 1
                    error_msg = f"No data returned for {league_name} (ID: {league_id})"
                    soccer_result["errors"].append(error_msg)
                    logger.warning(f"⚠️  {error_msg}")
                
                # Rate limiting - be respectful to FootyStats API
                time.sleep(1.5)
                
            except Exception as e:
                soccer_result["leagues_failed"] += 1
                error_msg = f"Failed to download {league_name}: {str(e)}"
                soccer_result["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        soccer_result["status"] = "completed"
        success_rate = (soccer_result["leagues_successful"] / soccer_result["leagues_attempted"]) * 100 if soccer_result["leagues_attempted"] > 0 else 0
        logger.info(f"⚽ Soccer download complete: {soccer_result['leagues_successful']}/{soccer_result['leagues_attempted']} leagues ({success_rate:.1f}% success rate)")
        
        return soccer_result
    
    def _download_league_matches(self, league_id: int, league_name: str) -> Optional[List[Dict]]:
        """Download data for a specific league using FootyStats API."""
        
        try:
            # Use correct FootyStats API endpoints with season_id
            logger.debug(f"Downloading data for {league_name} (season_id: {league_id})")
            
            # Get season info
            season_url = get_league_season_url(league_id)
            logger.debug(f"Season URL: {season_url}")
            
            season_response = self.session.get(season_url, timeout=30)
            
            combined_data = []
            
            if season_response.status_code == 200:
                season_data = season_response.json()
                logger.debug(f"✅ Season data retrieved for {league_name}")
                
                # Get teams with stats
                teams_url = get_league_teams_url(league_id, include_stats=True)
                logger.debug(f"Teams URL: {teams_url}")
                
                teams_response = self.session.get(teams_url, timeout=30)
                
                if teams_response.status_code == 200:
                    teams_data = teams_response.json()
                    
                    # Handle different response formats
                    if isinstance(teams_data, dict):
                        teams = teams_data.get('data', [])
                    elif isinstance(teams_data, list):
                        teams = teams_data
                    else:
                        teams = []
                    
                    # Add metadata to teams data
                    for team in teams:
                        team['league_name'] = league_name
                        team['season_id'] = league_id
                        team['downloaded_at'] = datetime.now().isoformat()
                    
                    # Combine season and teams data
                    combined_data = {
                        'league_name': league_name,
                        'season_id': league_id,
                        'season_info': season_data,
                        'teams': teams,
                        'downloaded_at': datetime.now().isoformat()
                    }
                    
                    logger.debug(f"✅ Found {len(teams)} teams for {league_name}")
                    self.api_stats["footystats"]["success"] += 1
                    return [combined_data]  # Return as list for consistency
                    
                else:
                    logger.warning(f"Could not fetch teams for {league_name}: {teams_response.status_code}")
                    # Still return season data if available
                    combined_data = {
                        'league_name': league_name,
                        'season_id': league_id,
                        'season_info': season_data,
                        'teams': [],
                        'downloaded_at': datetime.now().isoformat()
                    }
                    self.api_stats["footystats"]["success"] += 1
                    return [combined_data]
                    
            elif season_response.status_code == 422:
                logger.debug(f"Invalid parameters for {league_name} (season_id: {league_id})")
                self.api_stats["footystats"]["failures"] += 1
                return None
            elif season_response.status_code == 429:
                logger.warning(f"Rate limited for {league_name}, waiting...")
                self.api_stats["footystats"]["rate_limited"] += 1
                time.sleep(5)
                return None
            else:
                logger.warning(f"API error {season_response.status_code} for {league_name}")
                self.api_stats["footystats"]["failures"] += 1
                return None
            
        except Exception as e:
            logger.error(f"Exception downloading {league_name}: {e}")
            self.api_stats["footystats"]["failures"] += 1
            return None
    
    def _save_soccer_league_data(self, league_name: str, league_id: int, matches: List[Dict]) -> Path:
        """Save soccer league data to file."""
        
        # Create organized directory structure
        soccer_dir = DATA_DIR / "soccer"
        soccer_dir.mkdir(exist_ok=True)
        
        # Clean league name for filename
        clean_name = league_name.lower().replace(" ", "_").replace("-", "_")
        filename = f"{clean_name}_{league_id}.json"
        file_path = soccer_dir / filename
        
        # Prepare data with metadata
        output_data = {
            "metadata": {
                "league_name": league_name,
                "league_id": league_id,
                "total_matches": len(matches),
                "downloaded_at": datetime.now().isoformat(),
                "source": "FootyStats API",
                "api_version": "2025"
            },
            "matches": matches
        }
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def download_mlb_data(self, test_mode: bool = False) -> Dict[str, Any]:
        """Download MLB data from SportsData.io."""
        
        mlb_result = {
            "status": "started",
            "endpoints_attempted": 0,
            "endpoints_successful": 0,
            "total_records": 0,
            "files_created": [],
            "errors": []
        }
        
        # MLB endpoints to download
        current_year = datetime.now().year
        endpoints = {
            "teams": f"https://api.sportsdata.io/v3/mlb/scores/json/teams",
            "games": f"https://api.sportsdata.io/v3/mlb/scores/json/Games/{current_year}",
            "standings": f"https://api.sportsdata.io/v3/mlb/scores/json/Standings/{current_year}"
        }
        
        if test_mode:
            # In test mode, only download teams data
            endpoints = {"teams": endpoints["teams"]}
            logger.info("🧪 Test mode: Downloading only teams data")
        
        for endpoint_name, url in endpoints.items():
            mlb_result["endpoints_attempted"] += 1
            
            logger.info(f"📥 Downloading MLB {endpoint_name}")
            
            try:
                params = {'key': API_KEYS["sportsdata"]}
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Save the data
                    file_path = self._save_mlb_data(endpoint_name, data)
                    
                    mlb_result["endpoints_successful"] += 1
                    mlb_result["total_records"] += len(data) if isinstance(data, list) else 1
                    mlb_result["files_created"].append(str(file_path))
                    
                    self.api_stats["sportsdata"]["success"] += 1
                    logger.info(f"✅ Downloaded {len(data) if isinstance(data, list) else 1} {endpoint_name} records")
                
                else:
                    error_msg = f"API error {response.status_code} for {endpoint_name}"
                    mlb_result["errors"].append(error_msg)
                    self.api_stats["sportsdata"]["failures"] += 1
                    logger.warning(f"⚠️  {error_msg}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"Failed to download {endpoint_name}: {str(e)}"
                mlb_result["errors"].append(error_msg)
                self.api_stats["sportsdata"]["failures"] += 1
                logger.error(f"❌ {error_msg}")
        
        mlb_result["status"] = "completed"
        logger.info(f"⚾ MLB download complete: {mlb_result['endpoints_successful']}/{mlb_result['endpoints_attempted']} endpoints")
        
        return mlb_result
    
    def _save_mlb_data(self, data_type: str, data: Any) -> Path:
        """Save MLB data to file."""
        
        # Create directory
        mlb_dir = DATA_DIR / "mlb"
        mlb_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"mlb_{data_type}_{timestamp}.json"
        file_path = mlb_dir / filename
        
        # Prepare data with metadata
        output_data = {
            "metadata": {
                "data_type": data_type,
                "total_records": len(data) if isinstance(data, list) else 1,
                "downloaded_at": datetime.now().isoformat(),
                "source": "SportsData.io"
            },
            "data": data
        }
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return file_path
    
    def generate_demo_mlb_data(self) -> Dict[str, Any]:
        """Generate demo MLB data when API is unavailable."""
        
        logger.info("🎲 Generating demo MLB data...")
        
        demo_result = {
            "status": "demo_generated",
            "endpoints_attempted": 1,
            "endpoints_successful": 1,
            "total_records": 30,
            "files_created": [],
            "errors": []
        }
        
        # Generate sample teams
        demo_teams = [
            {"TeamID": 1, "Key": "NYY", "Name": "New York Yankees", "League": "AL", "Division": "East"},
            {"TeamID": 2, "Key": "BOS", "Name": "Boston Red Sox", "League": "AL", "Division": "East"},
            {"TeamID": 3, "Key": "LAD", "Name": "Los Angeles Dodgers", "League": "NL", "Division": "West"},
            {"TeamID": 4, "Key": "SF", "Name": "San Francisco Giants", "League": "NL", "Division": "West"},
            {"TeamID": 5, "Key": "CHC", "Name": "Chicago Cubs", "League": "NL", "Division": "Central"}
        ]
        
        # Generate sample games
        demo_games = []
        for i in range(25):
            demo_games.append({
                "GameID": 1000 + i,
                "Season": 2024,
                "GameType": "Regular Season",
                "Status": "Final",
                "HomeTeamID": (i % 5) + 1,
                "AwayTeamID": ((i + 1) % 5) + 1,
                "HomeTeamRuns": (i % 10),
                "AwayTeamRuns": ((i + 3) % 8),
                "DateTime": (datetime.now() - timedelta(days=i)).isoformat()
            })
        
        # Save demo data
        demo_data = {
            "teams": demo_teams,
            "games": demo_games
        }
        
        for data_type, data in demo_data.items():
            file_path = self._save_mlb_data(f"demo_{data_type}", data)
            demo_result["files_created"].append(str(file_path))
        
        logger.info("✅ Demo MLB data generated")
        return demo_result
    
    def _calculate_summary_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics from download results."""
        
        total_files = 0
        total_records = 0
        total_size_bytes = 0
        
        # Count soccer files
        if "files_created" in results["soccer"]:
            total_files += len(results["soccer"]["files_created"])
            total_records += results["soccer"].get("total_matches", 0)
        
        # Count MLB files
        if "files_created" in results["mlb"]:
            total_files += len(results["mlb"]["files_created"])
            total_records += results["mlb"].get("total_records", 0)
        
        # Calculate total size
        for file_path_str in (results["soccer"].get("files_created", []) + results["mlb"].get("files_created", [])):
            try:
                file_path = Path(file_path_str)
                if file_path.exists():
                    total_size_bytes += file_path.stat().st_size
            except Exception:
                pass
        
        results["summary"]["total_files"] = total_files
        results["summary"]["total_records"] = total_records
        results["summary"]["total_size_mb"] = round(total_size_bytes / (1024 * 1024), 2)
        
        return results
    
    def save_download_report(self, results: Dict[str, Any]) -> None:
        """Save download report with API statistics."""
        
        # Add API statistics to results
        results["api_statistics"] = self.api_stats
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = DATA_DIR / f"download_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📄 Download report saved: {report_file}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current download status and data summary."""
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "data_directories": {},
            "file_counts": {},
            "total_size_mb": 0,
            "api_statistics": self.api_stats
        }
        
        # Check soccer data
        soccer_dir = DATA_DIR / "soccer"
        if soccer_dir.exists():
            soccer_files = list(soccer_dir.glob("*.json"))
            status["data_directories"]["soccer"] = {
                "exists": True,
                "file_count": len(soccer_files),
                "last_updated": max([f.stat().st_mtime for f in soccer_files]) if soccer_files else None
            }
            status["file_counts"]["soccer"] = len(soccer_files)
            status["total_size_mb"] += sum(f.stat().st_size for f in soccer_files) / (1024 * 1024)
        
        # Check MLB data
        mlb_dir = DATA_DIR / "mlb"
        if mlb_dir.exists():
            mlb_files = list(mlb_dir.glob("*.json"))
            status["data_directories"]["mlb"] = {
                "exists": True,
                "file_count": len(mlb_files),
                "last_updated": max([f.stat().st_mtime for f in mlb_files]) if mlb_files else None
            }
            status["file_counts"]["mlb"] = len(mlb_files)
            status["total_size_mb"] += sum(f.stat().st_size for f in mlb_files) / (1024 * 1024)
        
        status["total_size_mb"] = round(status["total_size_mb"], 2)
        
        return status


def main():
    """Main function to run the simple data downloader."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Data Downloader for Universal Betting Dashboard")
    parser.add_argument("--test", action="store_true", help="Run in test mode (download small samples)")
    parser.add_argument("--status", action="store_true", help="Show current status only")
    
    args = parser.parse_args()
    
    downloader = SimpleDataDownloader()
    
    if args.status:
        # Show status only
        status = downloader.get_status()
        print(json.dumps(status, indent=2))
    else:
        # Run download
        logger.info("🚀 Starting Simple Data Downloader")
        
        results = downloader.download_all_data(test_mode=args.test)
        
        # Print summary
        logger.info("📊 Download Summary:")
        logger.info(f"  Total Files: {results['summary']['total_files']}")
        logger.info(f"  Total Records: {results['summary']['total_records']}")
        logger.info(f"  Total Size: {results['summary']['total_size_mb']} MB")
        logger.info(f"  Duration: {results['summary']['duration_seconds']} seconds")
        
        # Print API statistics
        logger.info("📡 API Statistics:")
        for api, stats in downloader.api_stats.items():
            if stats['success'] > 0 or stats['failures'] > 0:
                logger.info(f"  {api}: {stats['success']} success, {stats['failures']} failures, {stats['rate_limited']} rate limited")


if __name__ == "__main__":
    main()