#!/usr/bin/env python3
"""
Historical Data Manager for Universal Betting Dashboard

This module handles downloading, processing, and managing historical data for:
1. MLB data from SportsData.io
2. Soccer data from FootyStats API (50 leagues)

Features:
- Automated data downloading and updates
- Data validation and cleaning
- Efficient storage and retrieval
- Integration with ML models
"""

import os
import json
import time
import requests
import zipfile
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Import FootyStats configuration with correct API structure
from footystats_config import (
    FOOTYSTATS_API_KEY, 
    FOOTYSTATS_LEAGUE_IDS, 
    LEAGUE_BY_COUNTRY,
    FOOTYSTATS_BASE_URL,
    FOOTYSTATS_ENDPOINTS,
    get_league_teams_url,
    get_league_season_url
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path("data")
MLB_DATA_DIR = DATA_DIR / "mlb"
SOCCER_DATA_DIR = DATA_DIR / "soccer"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Create directories
for dir_path in [DATA_DIR, MLB_DATA_DIR, SOCCER_DATA_DIR, PROCESSED_DATA_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration
SPORTSDATA_API_KEY = os.getenv("SPORTSDATA_API_KEY", "demo_key")

# Soccer Leagues Configuration (Updated with correct 2025 FootyStats League IDs)
SOCCER_LEAGUES = LEAGUE_BY_COUNTRY

class DataManager:
    """
    Comprehensive data manager for historical sports data.
    
    Handles downloading, processing, and storage of:
    - MLB historical data
    - Soccer historical data from 50+ leagues worldwide
    """
    
    def __init__(self):
        """Initialize the data manager."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Universal-Betting-Dashboard/1.0',
            'Accept': 'application/json'
        })
    
    # ========================================================================
    # Core Data Management Methods
    # ========================================================================
    
    def download_all_historical_data(self, years: int = 3) -> Dict[str, bool]:
        """
        Download all historical data for both MLB and Soccer.
        
        Args:
            years: Number of years to download (default: 3)
        
        Returns:
            Dict[str, bool]: Success status for each data source
        """
        logger.info(f"🚀 Starting complete historical data download for {years} years")
        
        results = {}
        
        # Download MLB data
        logger.info("⚾ Starting MLB data download...")
        results['mlb'] = self.download_mlb_historical_data(years)
        
        # Download Soccer data
        logger.info("⚽ Starting Soccer data download...")
        results['soccer'] = self.download_soccer_historical_data(years)
        
        # Process all downloaded data
        logger.info("🔄 Processing downloaded data...")
        self.process_all_data()
        
        success_count = sum(results.values())
        logger.info(f"✅ Historical data download complete: {success_count}/2 sources successful")
        
        return results
    
    def get_data_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all historical data."""
        status = {
            'timestamp': datetime.now().isoformat(),
            'mlb': self._get_mlb_status(),
            'soccer': self._get_soccer_status(),
            'processed': self._get_processed_status()
        }
        
        return status
    
    # ========================================================================
    # MLB Data Management (SportsData.io)
    # ========================================================================
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def download_mlb_historical_data(self, years: int = 3) -> bool:
        """
        Download MLB historical data from SportsData.io.
        
        Args:
            years: Number of years to download (default: 3)
        
        Returns:
            bool: Success status
        """
        logger.info(f"⚾ Starting MLB historical data download for {years} years")
        
        if SPORTSDATA_API_KEY == "demo_key":
            logger.warning("⚠️  Using demo mode for SportsData.io - generating sample data")
            return self._generate_sample_mlb_data()
        
        try:
            current_year = datetime.now().year
            
            for year_offset in range(years):
                season = current_year - year_offset
                
                # Download season data
                success = self._download_mlb_season(season)
                if not success:
                    logger.warning(f"⚠️  Failed to download MLB {season} season")
                    continue
                
                # Rate limiting
                time.sleep(1)
            
            logger.info(f"✅ MLB historical data download complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download MLB historical data: {e}")
            return False
    
    def _download_mlb_season(self, season: int) -> bool:
        """Download data for a specific MLB season."""
        logger.info(f"📥 Downloading MLB {season} season data")
        
        try:
            # Create season directory
            season_dir = MLB_DATA_DIR / str(season)
            season_dir.mkdir(exist_ok=True)
            
            # SportsData.io endpoints
            endpoints = {
                'games': f'https://api.sportsdata.io/v3/mlb/scores/json/Games/{season}',
                'teams': f'https://api.sportsdata.io/v3/mlb/scores/json/teams',
                'players': f'https://api.sportsdata.io/v3/mlb/scores/json/Players',
                'stadiums': f'https://api.sportsdata.io/v3/mlb/scores/json/Stadiums'
            }
            
            # Download each data type
            for data_type, url in endpoints.items():
                data = self._fetch_mlb_data(url)
                if data:
                    file_path = season_dir / f"{data_type}.json"
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    logger.info(f"✅ Downloaded {data_type}: {len(data) if isinstance(data, list) else 1} records")
                
                # Rate limiting
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download MLB {season}: {e}")
            return False
    
    def _fetch_mlb_data(self, url: str) -> Optional[List]:
        """Fetch data from SportsData.io API."""
        try:
            params = {'key': SPORTSDATA_API_KEY}
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️  MLB API error {response.status_code}: {url}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch MLB data: {e}")
            return None
    
    def _generate_sample_mlb_data(self) -> bool:
        """Generate sample MLB data for demo mode."""
        logger.info("🎲 Generating sample MLB data for demo mode")
        
        try:
            sample_data = {
                'games': [
                    {
                        'GameID': 1,
                        'Season': 2024,
                        'HomeTeam': 'NYY',
                        'AwayTeam': 'BOS',
                        'HomeTeamRuns': 7,
                        'AwayTeamRuns': 4,
                        'DateTime': '2024-04-15T19:05:00'
                    }
                ],
                'teams': [
                    {'TeamID': 1, 'Key': 'NYY', 'Name': 'New York Yankees'},
                    {'TeamID': 2, 'Key': 'BOS', 'Name': 'Boston Red Sox'}
                ]
            }
            
            # Save sample data
            sample_dir = MLB_DATA_DIR / "2024"
            sample_dir.mkdir(exist_ok=True)
            
            for data_type, data in sample_data.items():
                file_path = sample_dir / f"{data_type}.json"
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            logger.info("✅ Sample MLB data generated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate sample MLB data: {e}")
            return False
    
    def _get_mlb_status(self) -> Dict:
        """Get MLB data status."""
        if not MLB_DATA_DIR.exists():
            return {'status': 'no_data', 'seasons': [], 'total_files': 0}
        
        seasons = []
        total_files = 0
        
        for season_dir in MLB_DATA_DIR.iterdir():
            if season_dir.is_dir() and season_dir.name.isdigit():
                season_files = list(season_dir.glob('*.json'))
                seasons.append({
                    'season': season_dir.name,
                    'files': len(season_files),
                    'last_updated': max([f.stat().st_mtime for f in season_files]) if season_files else None
                })
                total_files += len(season_files)
        
        return {
            'status': 'available' if seasons else 'no_data',
            'seasons': sorted(seasons, key=lambda x: x['season'], reverse=True),
            'total_files': total_files
        }
    
    def process_mlb_data(self):
        """Process and clean MLB historical data."""
        logger.info("🔄 Processing MLB historical data...")
        
        try:
            processed_data = []
            
            for season_dir in MLB_DATA_DIR.iterdir():
                if season_dir.is_dir() and season_dir.name.isdigit():
                    season_data = self._process_mlb_season(season_dir)
                    if season_data:
                        processed_data.extend(season_data)
            
            if processed_data:
                # Save processed data
                processed_file = PROCESSED_DATA_DIR / "mlb_processed.json"
                with open(processed_file, 'w') as f:
                    json.dump(processed_data, f, indent=2)
            
            logger.info(f"✅ MLB data processing complete: {len(processed_data)} files processed")
            
        except Exception as e:
            logger.error(f"❌ Failed to process MLB data: {e}")
    
    # ========================================================================
    # Soccer Data Management (FootyStats)
    # ========================================================================
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def download_soccer_historical_data(self, seasons: int = 3) -> bool:
        """
        Download historical soccer data from FootyStats API for all 50 leagues.
        
        Args:
            seasons: Number of recent seasons to download (default: 3)
        
        Returns:
            bool: Success status
        """
        logger.info(f"⚽ Starting soccer historical data download for {seasons} seasons")
        
        if FOOTYSTATS_API_KEY == "demo_key":
            logger.warning("⚠️  Using demo mode for FootyStats - generating sample data")
            return self._generate_sample_soccer_data()
        
        success_count = 0
        total_leagues = sum(len(leagues) for leagues in SOCCER_LEAGUES.values())
        
        for country, leagues in SOCCER_LEAGUES.items():
            for league_name, league_id in leagues.items():
                try:
                    success = self._download_league_data(country, league_name, league_id, seasons)
                    if success:
                        success_count += 1
                    
                    # Rate limiting - be respectful to the API
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to download {league_name}: {e}")
        
        logger.info(f"✅ Soccer data download complete: {success_count}/{total_leagues} leagues")
        return success_count > 0
    
    def _download_league_data(self, country: str, league_name: str, league_id: int, seasons: int) -> bool:
        """Download data for a specific league using correct FootyStats API structure."""
        
        logger.info(f"📥 Downloading {league_name} ({country}) - League ID: {league_id}")
        
        try:
            # Create league directory
            league_dir = SOCCER_DATA_DIR / country.lower().replace(" ", "_") / league_name.lower().replace(" ", "_")
            league_dir.mkdir(parents=True, exist_ok=True)
            
            # Download recent seasons
            current_year = datetime.now().year
            
            for season_offset in range(seasons):
                season_year = current_year - season_offset
                season_data = self._fetch_season_data(league_id, season_year)
                
                if season_data:
                    # Save season data
                    season_file = league_dir / f"{season_year}_season.json"
                    with open(season_file, 'w') as f:
                        json.dump(season_data, f, indent=2)
                    
                    logger.info(f"✅ Downloaded {league_name} {season_year}: {len(season_data.get('matches', []))} matches")
                else:
                    logger.warning(f"⚠️  No data for {league_name} {season_year}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {league_name}: {e}")
            return False
    
    def _fetch_season_data(self, league_id: int, season_year: int) -> Optional[Dict]:
        """Fetch season data from FootyStats API using correct structure."""
        
        try:
            # Use correct FootyStats API endpoints and parameters
            
            # Try league-season endpoint first (general season info)
            season_url = get_league_season_url(league_id)
            logger.debug(f"Fetching season data from: {season_url}")
            
            response = self.session.get(season_url, timeout=30)
            
            season_data = {
                "season_id": league_id,
                "season_year": season_year,
                "teams": [],
                "season_info": {},
                "fetched_at": datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"✅ Season data fetched successfully")
                
                # Store season info
                season_data["season_info"] = data
                
                # Also try to get teams with stats
                teams_url = get_league_teams_url(league_id, include_stats=True)
                logger.debug(f"Fetching teams data from: {teams_url}")
                
                teams_response = self.session.get(teams_url, timeout=30)
                
                if teams_response.status_code == 200:
                    teams_data = teams_response.json()
                    season_data["teams"] = teams_data.get('data', []) if isinstance(teams_data, dict) else teams_data
                    logger.debug(f"✅ Teams data fetched: {len(season_data['teams'])} teams")
                else:
                    logger.warning(f"⚠️  Could not fetch teams data: {teams_response.status_code}")
                
                return season_data
                
            elif response.status_code == 422:
                logger.warning(f"⚠️  Invalid parameters for season_id {league_id}")
                return None
            elif response.status_code == 404:
                logger.warning(f"⚠️  No data found for season_id {league_id}")
                return None
            else:
                logger.warning(f"⚠️  FootyStats API error {response.status_code} for season_id {league_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch season data for season_id {league_id}: {e}")
            return None
    
    def _generate_sample_soccer_data(self) -> bool:
        """Generate sample soccer data for demo mode."""
        logger.info("🎲 Generating sample soccer data for demo mode")
        
        try:
            sample_matches = [
                {
                    'id': 1,
                    'home_team': 'Manchester United',
                    'away_team': 'Liverpool',
                    'home_goals': 2,
                    'away_goals': 1,
                    'date': '2024-04-15',
                    'league_id': 13943  # Premier League
                }
            ]
            
            # Save sample data for a few leagues
            sample_leagues = list(FOOTYSTATS_LEAGUE_IDS.items())[:5]
            
            for league_name, league_id in sample_leagues:
                # Create directory structure
                country = "sample_country"
                league_dir = SOCCER_DATA_DIR / country / league_name.lower().replace(" ", "_")
                league_dir.mkdir(parents=True, exist_ok=True)
                
                season_data = {
                    "league_id": league_id,
                    "season": 2024,
                    "matches": sample_matches
                }
                
                season_file = league_dir / "2024_season.json"
                with open(season_file, 'w') as f:
                    json.dump(season_data, f, indent=2)
            
            logger.info("✅ Sample soccer data generated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate sample soccer data: {e}")
            return False
    
    def _get_soccer_status(self) -> Dict:
        """Get soccer data status."""
        if not SOCCER_DATA_DIR.exists():
            return {'status': 'no_data', 'leagues': [], 'total_files': 0}
        
        leagues = []
        total_files = 0
        
        for country_dir in SOCCER_DATA_DIR.iterdir():
            if country_dir.is_dir():
                for league_dir in country_dir.iterdir():
                    if league_dir.is_dir():
                        season_files = list(league_dir.glob('*.json'))
                        leagues.append({
                            'country': country_dir.name,
                            'league': league_dir.name,
                            'seasons': len(season_files),
                            'last_updated': max([f.stat().st_mtime for f in season_files]) if season_files else None
                        })
                        total_files += len(season_files)
        
        return {
            'status': 'available' if leagues else 'no_data',
            'leagues': leagues,
            'total_files': total_files
        }
    
    def process_soccer_data(self):
        """Process and clean soccer historical data."""
        logger.info("🔄 Processing soccer historical data...")
        
        try:
            processed_data = []
            
            for country_dir in SOCCER_DATA_DIR.iterdir():
                if country_dir.is_dir():
                    for league_dir in country_dir.iterdir():
                        if league_dir.is_dir():
                            league_data = self._process_soccer_league(country_dir.name, league_dir)
                            if league_data:
                                processed_data.extend(league_data)
            
            if processed_data:
                # Save processed data
                processed_file = PROCESSED_DATA_DIR / "soccer_processed.json"
                with open(processed_file, 'w') as f:
                    json.dump(processed_data, f, indent=2)
            
            logger.info(f"✅ Soccer data processing complete: {len(processed_data)} records processed")
            
        except Exception as e:
            logger.error(f"❌ Failed to process soccer data: {e}")
    
    def _process_soccer_league(self, country: str, league_dir: Path) -> List[Dict]:
        """Process data for a specific soccer league."""
        processed_matches = []
        
        try:
            for season_file in league_dir.glob('*.json'):
                with open(season_file, 'r') as f:
                    season_data = json.load(f)
                
                for match in season_data.get('matches', []):
                    processed_match = {
                        'country': country,
                        'league': league_dir.name,
                        'season': season_data.get('season'),
                        'league_id': season_data.get('league_id'),
                        'match_data': match,
                        'processed_at': datetime.now().isoformat()
                    }
                    processed_matches.append(processed_match)
        
        except Exception as e:
            logger.error(f"❌ Failed to process league {league_dir.name}: {e}")
        
        return processed_matches
    
    # ========================================================================
    # Data Processing and Utilities
    # ========================================================================
    
    def process_all_data(self):
        """Process all downloaded historical data."""
        logger.info("🔄 Processing all historical data...")
        
        self.process_mlb_data()
        self.process_soccer_data()
        
        logger.info("✅ All data processing complete")
    
    def _get_processed_status(self) -> Dict:
        """Get processed data status."""
        processed_files = list(PROCESSED_DATA_DIR.glob('*.json'))
        
        status = {
            'status': 'available' if processed_files else 'no_data',
            'files': []
        }
        
        for file_path in processed_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                status['files'].append({
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'records': len(data) if isinstance(data, list) else 1,
                    'last_updated': file_path.stat().st_mtime
                })
            except Exception:
                pass
        
        return status
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up data older than specified days."""
        logger.info(f"🧹 Cleaning up data older than {days} days")
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        cleaned_count = 0
        
        for data_dir in [MLB_DATA_DIR, SOCCER_DATA_DIR]:
            if data_dir.exists():
                for file_path in data_dir.rglob('*.json'):
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
        
        logger.info(f"✅ Cleaned up {cleaned_count} old files")


def main():
    """Main function for testing the data manager."""
    logger.info("🚀 Starting Data Manager Test")
    
    # Initialize data manager
    dm = DataManager()
    
    # Download historical data (3 years)
    results = dm.download_all_historical_data(years=3)
    
    # Get status
    status = dm.get_data_status()
    
    # Print results
    logger.info("📊 Data Manager Results:")
    logger.info(f"  MLB Success: {results.get('mlb', False)}")
    logger.info(f"  Soccer Success: {results.get('soccer', False)}")
    logger.info(f"  Status: {json.dumps(status, indent=2)}")


if __name__ == "__main__":
    main()