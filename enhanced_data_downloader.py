#!/usr/bin/env python3
"""
Enhanced Data Downloader for Universal Betting Dashboard

Advanced data collection from multiple sources with better error handling,
validation, and fallback mechanisms.
"""

import os
import sys
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Import correct FootyStats configuration
from footystats_config import FOOTYSTATS_API_KEY, FOOTYSTATS_LEAGUE_IDS, LEAGUE_BY_COUNTRY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path("data")
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"

# Create directories
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True)

# API Keys and Configuration
API_KEYS = {
    "footystats": FOOTYSTATS_API_KEY,
    "sportsdata": os.getenv("SPORTSDATA_API_KEY", "demo_key"),
    "football_data": os.getenv("FOOTBALL_DATA_API_KEY", "demo_key"),
    "api_sports": os.getenv("API_SPORTS_KEY", "demo_key")
}

# Data source configurations
DATA_SOURCES = {
    "soccer": {
        "primary": "footystats",
        "fallback": ["football_data", "api_sports"],
        "cache_duration": 3600  # 1 hour
    },
    "mlb": {
        "primary": "sportsdata",
        "fallback": ["api_sports"],
        "cache_duration": 1800  # 30 minutes
    }
}

# Updated league configurations using correct 2025 FootyStats IDs
LEAGUE_CONFIGS = {
    "soccer": {
        "footystats": FOOTYSTATS_LEAGUE_IDS,
        "football_data": {
            # Football-Data.org IDs (fallback)
            "English Premier League": 2021,
            "Spanish La Liga": 2014,
            "German Bundesliga": 2002,
            "Italian Serie A": 2019,
            "French Ligue 1": 2015,
        },
        "api_sports": {
            # API-Sports IDs (fallback)
            "English Premier League": 39,
            "Spanish La Liga": 140,
            "German Bundesliga": 78,
            "Italian Serie A": 135,
            "French Ligue 1": 61,
        }
    },
    "mlb": {
        "sportsdata": "mlb",  # SportsData.io uses sport codes
        "api_sports": 1  # API-Sports MLB league ID
    }
}


class EnhancedDataDownloader:
    """
    Enhanced data downloader with multiple source support, caching, and validation.
    """
    
    def __init__(self):
        """Initialize the enhanced data downloader."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Universal-Betting-Dashboard/2.0',
            'Accept': 'application/json'
        })
        
        # Rate limiting
        self.rate_limits = {}
        
        # Data validation schemas
        self.schemas = self._load_validation_schemas()
    
    def _load_validation_schemas(self) -> Dict:
        """Load data validation schemas."""
        return {
            "soccer_match": {
                "required_fields": ["home_team", "away_team", "date"],
                "optional_fields": ["home_goals", "away_goals", "home_xg", "away_xg"]
            },
            "mlb_game": {
                "required_fields": ["home_team", "away_team", "date"],
                "optional_fields": ["home_runs", "away_runs", "inning"]
            }
        }
    
    # ========================================================================
    # Main Download Methods
    # ========================================================================
    
    def download_all_data(self, sports: List[str] = None, timeframe: str = "recent") -> Dict[str, Any]:
        """
        Download data for all configured sports.
        
        Args:
            sports: List of sports to download (default: ["soccer", "mlb"])
            timeframe: "recent", "season", or "historical"
        
        Returns:
            Dict with download results and statistics
        """
        if sports is None:
            sports = ["soccer", "mlb"]
        
        logger.info(f"🚀 Starting enhanced data download for: {sports}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "timeframe": timeframe,
            "results": {},
            "summary": {
                "total_sources": 0,
                "successful_downloads": 0,
                "failed_downloads": 0,
                "cached_responses": 0
            }
        }
        
        for sport in sports:
            logger.info(f"📥 Downloading {sport} data...")
            
            sport_result = self._download_sport_data(sport, timeframe)
            results["results"][sport] = sport_result
            
            # Update summary
            results["summary"]["total_sources"] += sport_result.get("total_attempts", 0)
            results["summary"]["successful_downloads"] += sport_result.get("successful", 0)
            results["summary"]["failed_downloads"] += sport_result.get("failed", 0)
            results["summary"]["cached_responses"] += sport_result.get("cached", 0)
        
        # Save download report
        self._save_download_report(results)
        
        logger.info(f"✅ Enhanced data download complete: {results['summary']}")
        return results
    
    def _download_sport_data(self, sport: str, timeframe: str) -> Dict[str, Any]:
        """Download data for a specific sport."""
        
        result = {
            "sport": sport,
            "timeframe": timeframe,
            "sources_attempted": [],
            "successful": 0,
            "failed": 0,
            "cached": 0,
            "total_attempts": 0,
            "data_files": []
        }
        
        if sport == "soccer":
            return self._download_soccer_data(timeframe)
        elif sport == "mlb":
            return self._download_mlb_data(timeframe)
        else:
            logger.warning(f"⚠️  Unknown sport: {sport}")
            return result
    
    # ========================================================================
    # Soccer Data Download
    # ========================================================================
    
    def _download_soccer_data(self, timeframe: str) -> Dict[str, Any]:
        """Download soccer data from multiple sources with correct 2025 league IDs."""
        
        result = {
            "sport": "soccer",
            "leagues_processed": 0,
            "successful": 0,
            "failed": 0,
            "cached": 0,
            "total_attempts": 0,
            "data_files": []
        }
        
        primary_source = DATA_SOURCES["soccer"]["primary"]
        fallback_sources = DATA_SOURCES["soccer"]["fallback"]
        
        # Process leagues using correct 2025 FootyStats IDs
        for league_name, league_id in FOOTYSTATS_LEAGUE_IDS.items():
            result["total_attempts"] += 1
            result["leagues_processed"] += 1
            
            logger.info(f"📥 Downloading {league_name} (ID: {league_id})")
            
            # Try primary source first (FootyStats)
            data = self._download_from_source(
                source=primary_source,
                sport="soccer", 
                league_name=league_name,
                league_id=league_id,
                timeframe=timeframe
            )
            
            if data:
                result["successful"] += 1
                file_path = self._save_league_data(league_name, primary_source, data, timeframe)
                result["data_files"].append(str(file_path))
                logger.info(f"✅ Downloaded {league_name} from {primary_source}")
            else:
                # Try fallback sources
                success = False
                for fallback_source in fallback_sources:
                    logger.info(f"🔄 Trying fallback: {fallback_source} for {league_name}")
                    
                    fallback_data = self._download_from_source(
                        source=fallback_source,
                        sport="soccer",
                        league_name=league_name,
                        league_id=self._get_fallback_league_id(league_name, fallback_source),
                        timeframe=timeframe
                    )
                    
                    if fallback_data:
                        result["successful"] += 1
                        file_path = self._save_league_data(league_name, fallback_source, fallback_data, timeframe)
                        result["data_files"].append(str(file_path))
                        logger.info(f"✅ Downloaded {league_name} from {fallback_source}")
                        success = True
                        break
                
                if not success:
                    result["failed"] += 1
                    logger.warning(f"⚠️  Failed to download {league_name} from any source")
            
            # Rate limiting
            time.sleep(1)
        
        return result
    
    def _get_fallback_league_id(self, league_name: str, source: str) -> Optional[int]:
        """Get league ID for fallback source."""
        try:
            return LEAGUE_CONFIGS["soccer"][source].get(league_name)
        except KeyError:
            return None
    
    def _download_from_source(self, source: str, sport: str, league_name: str, 
                             league_id: Any, timeframe: str) -> Optional[List]:
        """Download data from a specific source."""
        
        if source == "footystats":
            return self._download_footystats(league_id, timeframe)
        elif source == "football_data":
            return self._download_football_data(league_id, timeframe)
        elif source == "api_sports":
            return self._download_api_sports(sport, league_id, timeframe)
        elif source == "sportsdata":
            return self._download_sportsdata(sport, timeframe)
        else:
            logger.warning(f"⚠️  Unknown source: {source}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _download_footystats(self, league_id: int, timeframe: str) -> Optional[List]:
        """Download data from FootyStats API using correct 2025 league IDs."""
        
        try:
            url = "https://api.footystats.org/league-matches"
            
            # Determine season based on timeframe
            current_year = datetime.now().year
            if timeframe == "recent":
                season = current_year
            elif timeframe == "season":
                season = current_year
            else:  # historical
                season = current_year - 1
            
            params = {
                'key': API_KEYS["footystats"],
                'league_id': str(league_id),
                'season': str(season)
            }
            
            logger.debug(f"FootyStats request: {url} with params {params}")
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, dict):
                    matches = data.get('data', [])
                elif isinstance(data, list):
                    matches = data
                else:
                    logger.warning(f"⚠️  Unexpected data format from FootyStats")
                    return None
                
                logger.debug(f"✅ FootyStats returned {len(matches)} matches for league {league_id}")
                return matches
                
            elif response.status_code == 422:
                logger.warning(f"⚠️  Invalid parameters for FootyStats league {league_id}")
                return None
            elif response.status_code == 404:
                logger.warning(f"⚠️  No data found for FootyStats league {league_id}")
                return None
            else:
                logger.warning(f"⚠️  FootyStats API error {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to download from FootyStats: {e}")
            return None
    
    def _download_football_data(self, league_id: int, timeframe: str) -> Optional[List]:
        """Download data from Football-Data.org API."""
        
        try:
            if not league_id:
                return None
            
            url = f"https://api.football-data.org/v4/competitions/{league_id}/matches"
            
            headers = {
                'X-Auth-Token': API_KEYS["football_data"]
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                logger.debug(f"✅ Football-Data returned {len(matches)} matches")
                return matches
            else:
                logger.warning(f"⚠️  Football-Data API error {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to download from Football-Data: {e}")
            return None
    
    def _download_api_sports(self, sport: str, league_id: int, timeframe: str) -> Optional[List]:
        """Download data from API-Sports."""
        
        try:
            if not league_id:
                return None
            
            if sport == "soccer":
                url = "https://v3.football.api-sports.io/fixtures"
                params = {'league': league_id}
            elif sport == "mlb":
                url = "https://v1.baseball.api-sports.io/games"
                params = {'league': league_id}
            else:
                return None
            
            headers = {
                'X-RapidAPI-Key': API_KEYS["api_sports"]
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                logger.debug(f"✅ API-Sports returned {len(matches)} matches")
                return matches
            else:
                logger.warning(f"⚠️  API-Sports error {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to download from API-Sports: {e}")
            return None
    
    # ========================================================================
    # MLB Data Download
    # ========================================================================
    
    def _download_mlb_data(self, timeframe: str) -> Dict[str, Any]:
        """Download MLB data from multiple sources."""
        
        result = {
            "sport": "mlb",
            "successful": 0,
            "failed": 0,
            "cached": 0,
            "total_attempts": 1,
            "data_files": []
        }
        
        primary_source = DATA_SOURCES["mlb"]["primary"]
        
        # Download MLB data
        data = self._download_sportsdata("mlb", timeframe)
        
        if data:
            result["successful"] = 1
            file_path = self._save_mlb_data(primary_source, data, timeframe)
            result["data_files"].append(str(file_path))
            logger.info(f"✅ Downloaded MLB data from {primary_source}")
        else:
            result["failed"] = 1
            logger.warning(f"⚠️  Failed to download MLB data")
        
        return result
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _download_sportsdata(self, sport: str, timeframe: str) -> Optional[List]:
        """Download data from SportsData.io."""
        
        try:
            # SportsData.io endpoints
            current_year = datetime.now().year
            
            if sport == "mlb":
                url = f"https://api.sportsdata.io/v3/mlb/scores/json/Games/{current_year}"
            else:
                return None
            
            params = {'key': API_KEYS["sportsdata"]}
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"✅ SportsData returned {len(data)} games")
                return data
            else:
                logger.warning(f"⚠️  SportsData API error {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to download from SportsData: {e}")
            return None
    
    # ========================================================================
    # Data Saving and Processing
    # ========================================================================
    
    def _save_league_data(self, league_name: str, source: str, data: List, timeframe: str) -> Path:
        """Save league data to file."""
        
        # Create directory structure
        sport_dir = RAW_DATA_DIR / "soccer" / source
        sport_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{league_name.lower().replace(' ', '_')}_{timeframe}_{timestamp}.json"
        file_path = sport_dir / filename
        
        # Save data with metadata
        output_data = {
            "metadata": {
                "league_name": league_name,
                "source": source,
                "timeframe": timeframe,
                "downloaded_at": datetime.now().isoformat(),
                "record_count": len(data)
            },
            "data": data
        }
        
        with open(file_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return file_path
    
    def _save_mlb_data(self, source: str, data: List, timeframe: str) -> Path:
        """Save MLB data to file."""
        
        # Create directory structure
        sport_dir = RAW_DATA_DIR / "mlb" / source
        sport_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mlb_{timeframe}_{timestamp}.json"
        file_path = sport_dir / filename
        
        # Save data with metadata
        output_data = {
            "metadata": {
                "sport": "mlb",
                "source": source,
                "timeframe": timeframe,
                "downloaded_at": datetime.now().isoformat(),
                "record_count": len(data)
            },
            "data": data
        }
        
        with open(file_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return file_path
    
    def _save_download_report(self, results: Dict) -> None:
        """Save download report."""
        
        report_file = PROCESSED_DATA_DIR / f"download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📄 Download report saved: {report_file}")
    
    # ========================================================================
    # Data Validation and Quality Checks
    # ========================================================================
    
    def validate_downloaded_data(self) -> Dict[str, Any]:
        """Validate all downloaded data."""
        
        logger.info("🔍 Validating downloaded data...")
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "soccer": self._validate_sport_data("soccer"),
            "mlb": self._validate_sport_data("mlb")
        }
        
        # Save validation report
        validation_file = PROCESSED_DATA_DIR / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(validation_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        logger.info(f"✅ Data validation complete: {validation_file}")
        return validation_results
    
    def _validate_sport_data(self, sport: str) -> Dict[str, Any]:
        """Validate data for a specific sport."""
        
        validation_result = {
            "sport": sport,
            "files_checked": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "total_records": 0,
            "valid_records": 0,
            "issues": []
        }
        
        sport_dir = RAW_DATA_DIR / sport
        if not sport_dir.exists():
            validation_result["issues"].append(f"No data directory found for {sport}")
            return validation_result
        
        # Check all data files
        for data_file in sport_dir.rglob("*.json"):
            validation_result["files_checked"] += 1
            
            try:
                with open(data_file, 'r') as f:
                    file_data = json.load(f)
                
                # Validate file structure
                if self._validate_file_structure(file_data, sport):
                    validation_result["valid_files"] += 1
                    
                    # Count and validate records
                    records = file_data.get("data", [])
                    validation_result["total_records"] += len(records)
                    
                    valid_record_count = sum(1 for record in records if self._validate_record(record, sport))
                    validation_result["valid_records"] += valid_record_count
                    
                    if valid_record_count < len(records):
                        validation_result["issues"].append(f"Invalid records in {data_file.name}")
                
                else:
                    validation_result["invalid_files"] += 1
                    validation_result["issues"].append(f"Invalid file structure: {data_file.name}")
            
            except Exception as e:
                validation_result["invalid_files"] += 1
                validation_result["issues"].append(f"Error reading {data_file.name}: {str(e)}")
        
        return validation_result
    
    def _validate_file_structure(self, file_data: Dict, sport: str) -> bool:
        """Validate file structure."""
        required_keys = ["metadata", "data"]
        return all(key in file_data for key in required_keys)
    
    def _validate_record(self, record: Dict, sport: str) -> bool:
        """Validate individual record."""
        if sport == "soccer":
            schema = self.schemas["soccer_match"]
        elif sport == "mlb":
            schema = self.schemas["mlb_game"]
        else:
            return False
        
        # Check required fields
        return all(field in record for field in schema["required_fields"])
    
    # ========================================================================
    # Utilities and Status
    # ========================================================================
    
    def get_download_status(self) -> Dict[str, Any]:
        """Get current download status and statistics."""
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "data_directories": {},
            "recent_downloads": {},
            "api_status": {}
        }
        
        # Check data directories
        for sport in ["soccer", "mlb"]:
            sport_dir = RAW_DATA_DIR / sport
            if sport_dir.exists():
                files = list(sport_dir.rglob("*.json"))
                status["data_directories"][sport] = {
                    "exists": True,
                    "file_count": len(files),
                    "total_size": sum(f.stat().st_size for f in files),
                    "last_download": max([f.stat().st_mtime for f in files]) if files else None
                }
            else:
                status["data_directories"][sport] = {"exists": False}
        
        # Check recent download reports
        report_files = list(PROCESSED_DATA_DIR.glob("download_report_*.json"))
        if report_files:
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest_report, 'r') as f:
                    status["recent_downloads"] = json.load(f)
            except Exception:
                pass
        
        # Check API status (basic connectivity)
        status["api_status"] = self._check_api_status()
        
        return status
    
    def _check_api_status(self) -> Dict[str, bool]:
        """Check basic API connectivity."""
        
        api_status = {}
        
        # Test FootyStats API
        try:
            url = "https://api.footystats.org/league-matches"
            params = {'key': API_KEYS["footystats"], 'league_id': '13943', 'season': '2025'}
            response = requests.get(url, params=params, timeout=10)
            api_status["footystats"] = response.status_code in [200, 422]  # 422 means API works but params may be invalid
        except Exception:
            api_status["footystats"] = False
        
        # Test other APIs similarly...
        api_status["sportsdata"] = API_KEYS["sportsdata"] != "demo_key"
        api_status["football_data"] = API_KEYS["football_data"] != "demo_key"
        api_status["api_sports"] = API_KEYS["api_sports"] != "demo_key"
        
        return api_status


def main():
    """Main function for testing the enhanced data downloader."""
    
    logger.info("🚀 Starting Enhanced Data Downloader Test")
    
    # Initialize downloader
    downloader = EnhancedDataDownloader()
    
    # Download recent data for all sports
    results = downloader.download_all_data(
        sports=["soccer", "mlb"],
        timeframe="recent"
    )
    
    # Validate downloaded data
    validation_results = downloader.validate_downloaded_data()
    
    # Get status
    status = downloader.get_download_status()
    
    # Print results
    logger.info("📊 Enhanced Download Results:")
    logger.info(f"  Total Sources: {results['summary']['total_sources']}")
    logger.info(f"  Successful: {results['summary']['successful_downloads']}")
    logger.info(f"  Failed: {results['summary']['failed_downloads']}")
    logger.info(f"  Validation Status: {validation_results}")


if __name__ == "__main__":
    main()