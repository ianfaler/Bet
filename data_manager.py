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
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "demo_key")
SPORTSDATA_API_KEY = os.getenv("SPORTSDATA_API_KEY", "demo_key")

# Soccer Leagues Configuration (50 leagues as specified)
SOCCER_LEAGUES = {
    "Argentina": {
        "Argentine Primera División": {"id": 1, "priority": 1},
        "Argentina Primera Nacional": {"id": 2, "priority": 2}
    },
    "Australia": {
        "A-League": {"id": 3, "priority": 1}
    },
    "Austria": {
        "Austrian Bundesliga": {"id": 4, "priority": 1}
    },
    "Belgium": {
        "Belgian Pro League": {"id": 5, "priority": 1}
    },
    "Brazil": {
        "Brazilian Serie A": {"id": 6, "priority": 1}
    },
    "Chile": {
        "Chilean Primera Division": {"id": 7, "priority": 1}
    },
    "China": {
        "Chinese Super League": {"id": 8, "priority": 1}
    },
    "Colombia": {
        "Colombian Primera A": {"id": 9, "priority": 1}
    },
    "Croatia": {
        "Croatian HNL": {"id": 10, "priority": 1}
    },
    "Cyprus": {
        "Cypriot First Division": {"id": 11, "priority": 1}
    },
    "Czech Republic": {
        "Czech First League": {"id": 12, "priority": 1}
    },
    "Denmark": {
        "Danish Superliga": {"id": 13, "priority": 1},
        "Danish 1st Division": {"id": 14, "priority": 2}
    },
    "Ecuador": {
        "Ecuadorian Serie A": {"id": 15, "priority": 1}
    },
    "England": {
        "English Premier League": {"id": 16, "priority": 1},
        "English Championship": {"id": 17, "priority": 2}
    },
    "France": {
        "French Ligue 1": {"id": 18, "priority": 1},
        "French Ligue 2": {"id": 19, "priority": 2}
    },
    "Germany": {
        "German Bundesliga": {"id": 20, "priority": 1},
        "German 2. Bundesliga": {"id": 21, "priority": 2}
    },
    "Greece": {
        "Greek Super League": {"id": 22, "priority": 1}
    },
    "India": {
        "Indian Super League": {"id": 23, "priority": 1}
    },
    "Israel": {
        "Israeli Premier League": {"id": 24, "priority": 1}
    },
    "Italy": {
        "Italian Serie A": {"id": 25, "priority": 1},
        "Italian Serie B": {"id": 26, "priority": 2}
    },
    "Japan": {
        "Japanese J1 League": {"id": 27, "priority": 1},
        "Japanese J2 League": {"id": 28, "priority": 2}
    },
    "Mexico": {
        "Liga MX": {"id": 29, "priority": 1}
    },
    "Netherlands": {
        "Dutch Eredivisie": {"id": 30, "priority": 1}
    },
    "Norway": {
        "Norwegian Eliteserien": {"id": 31, "priority": 1},
        "Norwegian OBOS-ligaen": {"id": 32, "priority": 2}
    },
    "Peru": {
        "Peruvian Liga 1": {"id": 33, "priority": 1}
    },
    "Poland": {
        "Polish Ekstraklasa": {"id": 34, "priority": 1}
    },
    "Portugal": {
        "Portuguese Primeira Liga": {"id": 35, "priority": 1}
    },
    "Qatar": {
        "Qatari Stars League": {"id": 36, "priority": 1}
    },
    "Romania": {
        "Romanian Liga I": {"id": 37, "priority": 1}
    },
    "Russia": {
        "Russian Premier League": {"id": 38, "priority": 1}
    },
    "Saudi Arabia": {
        "Saudi Professional League": {"id": 39, "priority": 1}
    },
    "Scotland": {
        "Scottish Premiership": {"id": 40, "priority": 1}
    },
    "Serbia": {
        "Serbian SuperLiga": {"id": 41, "priority": 1}
    },
    "South Korea": {
        "K League 1": {"id": 42, "priority": 1}
    },
    "Spain": {
        "Spanish La Liga": {"id": 43, "priority": 1},
        "Spanish LaLiga2": {"id": 44, "priority": 2}
    },
    "Sweden": {
        "Swedish Allsvenskan": {"id": 45, "priority": 1}
    },
    "Switzerland": {
        "Swiss Super League": {"id": 46, "priority": 1}
    },
    "Turkey": {
        "Turkish Super Lig": {"id": 47, "priority": 1}
    },
    "Ukraine": {
        "Ukrainian Premier League": {"id": 48, "priority": 1}
    },
    "United States": {
        "US MLS": {"id": 49, "priority": 1}
    },
    "Uruguay": {
        "Uruguayan Primera Division": {"id": 50, "priority": 1}
    }
}

class DataManager:
    """Main class for managing historical data downloads and processing."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Universal-Betting-Dashboard/2.0.0',
            'Accept': 'application/json'
        })
    
    # ========================================================================
    # MLB Data Management
    # ========================================================================
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def download_mlb_historical_data(self, years: List[int] = None) -> bool:
        """
        Download MLB historical data from SportsData.io
        
        Args:
            years: List of years to download (default: last 5 years)
        
        Returns:
            bool: Success status
        """
        if years is None:
            current_year = datetime.now().year
            years = list(range(current_year - 4, current_year + 1))  # Last 5 years
        
        logger.info(f"🏀 Starting MLB historical data download for years: {years}")
        
        try:
            # Download the historical data file
            download_url = "https://sportsdata.io/members/download-file?product=f1cdda93-8f32-47bf-b5a9-4bc4f93947f6"
            
            logger.info("📥 Downloading MLB historical data file...")
            response = self.session.get(download_url, timeout=300)  # 5 minute timeout
            response.raise_for_status()
            
            # Save the downloaded file
            zip_file_path = MLB_DATA_DIR / "mlb_historical_data.zip"
            with open(zip_file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ MLB data downloaded successfully: {zip_file_path}")
            
            # Extract the ZIP file
            self._extract_mlb_data(zip_file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download MLB data: {e}")
            return False
    
    def _extract_mlb_data(self, zip_file_path: Path) -> None:
        """Extract and organize MLB data from ZIP file."""
        
        try:
            logger.info("📦 Extracting MLB historical data...")
            
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Extract to MLB data directory
                extract_path = MLB_DATA_DIR / "extracted"
                extract_path.mkdir(exist_ok=True)
                zip_ref.extractall(extract_path)
            
            logger.info("✅ MLB data extracted successfully")
            
            # Process and organize the extracted data
            self._process_mlb_data(extract_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to extract MLB data: {e}")
    
    def _process_mlb_data(self, extract_path: Path) -> None:
        """Process and clean MLB data for ML model consumption."""
        
        try:
            logger.info("🔄 Processing MLB data for ML models...")
            
            # Find CSV files in the extracted directory
            csv_files = list(extract_path.rglob("*.csv"))
            
            processed_data = {}
            
            for csv_file in csv_files:
                try:
                    # Load and clean the data
                    df = pd.read_csv(csv_file)
                    
                    # Basic data cleaning
                    df = df.dropna(subset=['GameID']) if 'GameID' in df.columns else df
                    df = df.drop_duplicates()
                    
                    # Store processed data
                    file_key = csv_file.stem
                    processed_data[file_key] = df
                    
                    # Save processed data
                    output_path = PROCESSED_DATA_DIR / f"mlb_{file_key}_processed.csv"
                    df.to_csv(output_path, index=False)
                    
                    logger.info(f"✅ Processed {file_key}: {len(df)} records")
                    
                except Exception as e:
                    logger.error(f"⚠️  Failed to process {csv_file}: {e}")
            
            # Save metadata
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "files_processed": len(processed_data),
                "total_records": sum(len(df) for df in processed_data.values())
            }
            
            with open(PROCESSED_DATA_DIR / "mlb_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
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
            for league_name, league_info in leagues.items():
                try:
                    success = self._download_league_data(country, league_name, league_info, seasons)
                    if success:
                        success_count += 1
                    
                    # Rate limiting - be respectful to the API
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to download {league_name}: {e}")
        
        logger.info(f"✅ Soccer data download complete: {success_count}/{total_leagues} leagues")
        return success_count > 0
    
    def _download_league_data(self, country: str, league_name: str, league_info: Dict, seasons: int) -> bool:
        """Download data for a specific league."""
        
        league_id = league_info["id"]
        priority = league_info["priority"]
        
        logger.info(f"📥 Downloading {league_name} ({country}) - Priority {priority}")
        
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
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {league_name}: {e}")
            return False
    
    def _fetch_season_data(self, league_id: int, season_year: int) -> Optional[Dict]:
        """Fetch season data from FootyStats API."""
        
        # FootyStats API endpoints (example structure)
        base_url = "https://api.footystats.org/v2"
        
        endpoints = {
            "matches": f"{base_url}/matches",
            "teams": f"{base_url}/teams",
            "standings": f"{base_url}/standings"
        }
        
        season_data = {
            "league_id": league_id,
            "season": season_year,
            "matches": [],
            "teams": [],
            "standings": []
        }
        
        try:
            # Fetch matches
            matches_params = {
                "key": FOOTYSTATS_API_KEY,
                "league_id": league_id,
                "season": season_year
            }
            
            response = self.session.get(endpoints["matches"], params=matches_params, timeout=30)
            if response.status_code == 200:
                season_data["matches"] = response.json().get("data", [])
            
            # Fetch teams and standings (similar pattern)
            # Note: Actual FootyStats API structure may vary
            
            return season_data
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch season data for league {league_id}: {e}")
            return None
    
    def _generate_sample_soccer_data(self) -> bool:
        """Generate sample soccer data when API is not available."""
        
        logger.info("🎲 Generating sample soccer data for testing...")
        
        try:
            for country, leagues in SOCCER_LEAGUES.items():
                for league_name, league_info in leagues.items():
                    # Create sample data structure
                    league_dir = SOCCER_DATA_DIR / country.lower().replace(" ", "_") / league_name.lower().replace(" ", "_")
                    league_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Generate sample season data
                    current_year = datetime.now().year
                    for season_offset in range(3):  # 3 seasons
                        season_year = current_year - season_offset
                        
                        sample_data = {
                            "league_id": league_info["id"],
                            "league_name": league_name,
                            "country": country,
                            "season": season_year,
                            "matches": self._generate_sample_matches(20),  # 20 sample matches
                            "last_updated": datetime.now().isoformat()
                        }
                        
                        season_file = league_dir / f"{season_year}_season.json"
                        with open(season_file, 'w') as f:
                            json.dump(sample_data, f, indent=2)
            
            logger.info("✅ Sample soccer data generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate sample soccer data: {e}")
            return False
    
    def _generate_sample_matches(self, count: int) -> List[Dict]:
        """Generate sample match data."""
        import random
        
        teams = ["Team A", "Team B", "Team C", "Team D", "Team E", "Team F"]
        matches = []
        
        for i in range(count):
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            home_goals = random.randint(0, 4)
            away_goals = random.randint(0, 4)
            
            match = {
                "match_id": f"match_{i}",
                "date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "home_xg": round(random.uniform(0.5, 3.0), 2),
                "away_xg": round(random.uniform(0.5, 3.0), 2),
                "possession": {
                    "home": random.randint(30, 70),
                    "away": random.randint(30, 70)
                },
                "shots": {
                    "home": random.randint(5, 20),
                    "away": random.randint(5, 20)
                }
            }
            matches.append(match)
        
        return matches
    
    # ========================================================================
    # Data Processing and ML Integration
    # ========================================================================
    
    def process_all_data(self) -> Dict[str, bool]:
        """Process all historical data for ML model consumption."""
        
        logger.info("🔄 Processing all historical data for ML models...")
        
        results = {
            "mlb_processed": False,
            "soccer_processed": False
        }
        
        try:
            # Process MLB data
            results["mlb_processed"] = self._process_mlb_for_ml()
            
            # Process Soccer data
            results["soccer_processed"] = self._process_soccer_for_ml()
            
            # Generate summary statistics
            self._generate_data_summary()
            
            logger.info(f"✅ Data processing complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to process data: {e}")
            return results
    
    def _process_mlb_for_ml(self) -> bool:
        """Process MLB data specifically for ML model training."""
        
        try:
            logger.info("🏀 Processing MLB data for ML models...")
            
            # Load processed MLB data
            mlb_files = list(PROCESSED_DATA_DIR.glob("mlb_*_processed.csv"))
            
            if not mlb_files:
                logger.warning("⚠️  No processed MLB files found")
                return False
            
            # Combine and feature engineer
            combined_data = []
            
            for file_path in mlb_files:
                df = pd.read_csv(file_path)
                
                # Basic feature engineering
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                    df['DayOfWeek'] = df['Date'].dt.dayofweek
                    df['Month'] = df['Date'].dt.month
                
                combined_data.append(df)
            
            if combined_data:
                # Combine all data
                final_df = pd.concat(combined_data, ignore_index=True)
                
                # Save ML-ready dataset
                ml_file_path = PROCESSED_DATA_DIR / "mlb_ml_dataset.csv"
                final_df.to_csv(ml_file_path, index=False)
                
                logger.info(f"✅ MLB ML dataset created: {len(final_df)} records")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to process MLB data for ML: {e}")
            return False
    
    def _process_soccer_for_ml(self) -> bool:
        """Process soccer data specifically for ML model training."""
        
        try:
            logger.info("⚽ Processing soccer data for ML models...")
            
            all_matches = []
            
            # Walk through all soccer data directories
            for country_dir in SOCCER_DATA_DIR.iterdir():
                if country_dir.is_dir():
                    for league_dir in country_dir.iterdir():
                        if league_dir.is_dir():
                            # Process each league
                            league_matches = self._process_league_for_ml(league_dir)
                            all_matches.extend(league_matches)
            
            if all_matches:
                # Create ML dataset
                df = pd.DataFrame(all_matches)
                
                # Feature engineering for soccer
                df = self._engineer_soccer_features(df)
                
                # Save ML-ready dataset
                ml_file_path = PROCESSED_DATA_DIR / "soccer_ml_dataset.csv"
                df.to_csv(ml_file_path, index=False)
                
                logger.info(f"✅ Soccer ML dataset created: {len(df)} matches")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to process soccer data for ML: {e}")
            return False
    
    def _process_league_for_ml(self, league_dir: Path) -> List[Dict]:
        """Process a single league's data for ML."""
        
        matches = []
        
        try:
            # Load all season files for this league
            season_files = list(league_dir.glob("*_season.json"))
            
            for season_file in season_files:
                with open(season_file, 'r') as f:
                    season_data = json.load(f)
                
                # Extract matches
                for match in season_data.get("matches", []):
                    # Add league context
                    match["league_name"] = season_data.get("league_name", "Unknown")
                    match["country"] = season_data.get("country", "Unknown")
                    match["season"] = season_data.get("season", 0)
                    
                    matches.append(match)
        
        except Exception as e:
            logger.error(f"❌ Failed to process league {league_dir}: {e}")
        
        return matches
    
    def _engineer_soccer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for soccer ML model."""
        
        try:
            # Basic feature engineering
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df['day_of_week'] = df['date'].dt.dayofweek
                df['month'] = df['date'].dt.month
            
            # Goal-related features
            if 'home_goals' in df.columns and 'away_goals' in df.columns:
                df['total_goals'] = df['home_goals'] + df['away_goals']
                df['goal_difference'] = df['home_goals'] - df['away_goals']
                df['result'] = df['goal_difference'].apply(
                    lambda x: 'home_win' if x > 0 else ('away_win' if x < 0 else 'draw')
                )
            
            # xG features if available
            if 'home_xg' in df.columns and 'away_xg' in df.columns:
                df['total_xg'] = df['home_xg'] + df['away_xg']
                df['xg_difference'] = df['home_xg'] - df['away_xg']
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to engineer soccer features: {e}")
            return df
    
    def _generate_data_summary(self) -> None:
        """Generate summary statistics for all processed data."""
        
        try:
            summary = {
                "last_updated": datetime.now().isoformat(),
                "mlb_data": {},
                "soccer_data": {},
                "total_records": 0
            }
            
            # MLB summary
            mlb_file = PROCESSED_DATA_DIR / "mlb_ml_dataset.csv"
            if mlb_file.exists():
                mlb_df = pd.read_csv(mlb_file)
                summary["mlb_data"] = {
                    "records": len(mlb_df),
                    "columns": list(mlb_df.columns),
                    "date_range": {
                        "start": str(mlb_df['Date'].min()) if 'Date' in mlb_df.columns else "Unknown",
                        "end": str(mlb_df['Date'].max()) if 'Date' in mlb_df.columns else "Unknown"
                    }
                }
                summary["total_records"] += len(mlb_df)
            
            # Soccer summary
            soccer_file = PROCESSED_DATA_DIR / "soccer_ml_dataset.csv"
            if soccer_file.exists():
                soccer_df = pd.read_csv(soccer_file)
                summary["soccer_data"] = {
                    "records": len(soccer_df),
                    "columns": list(soccer_df.columns),
                    "leagues": len(soccer_df['league_name'].unique()) if 'league_name' in soccer_df.columns else 0,
                    "countries": len(soccer_df['country'].unique()) if 'country' in soccer_df.columns else 0
                }
                summary["total_records"] += len(soccer_df)
            
            # Save summary
            with open(PROCESSED_DATA_DIR / "data_summary.json", 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"✅ Data summary generated: {summary['total_records']} total records")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate data summary: {e}")
    
    # ========================================================================
    # Data Management Utilities
    # ========================================================================
    
    def update_all_data(self) -> Dict[str, bool]:
        """Update all historical data sources."""
        
        logger.info("🔄 Starting complete data update...")
        
        results = {
            "mlb_download": False,
            "soccer_download": False,
            "processing": False
        }
        
        try:
            # Download MLB data
            results["mlb_download"] = self.download_mlb_historical_data()
            
            # Download Soccer data
            results["soccer_download"] = self.download_soccer_historical_data()
            
            # Process all data
            processing_results = self.process_all_data()
            results["processing"] = any(processing_results.values())
            
            logger.info(f"✅ Data update complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to update data: {e}")
            return results
    
    def get_data_status(self) -> Dict:
        """Get current status of all data sources."""
        
        status = {
            "last_checked": datetime.now().isoformat(),
            "mlb": {
                "raw_data_exists": (MLB_DATA_DIR / "mlb_historical_data.zip").exists(),
                "processed_data_exists": (PROCESSED_DATA_DIR / "mlb_ml_dataset.csv").exists(),
                "last_updated": "Unknown"
            },
            "soccer": {
                "leagues_downloaded": 0,
                "processed_data_exists": (PROCESSED_DATA_DIR / "soccer_ml_dataset.csv").exists(),
                "last_updated": "Unknown"
            }
        }
        
        try:
            # Check soccer leagues
            if SOCCER_DATA_DIR.exists():
                league_count = 0
                for country_dir in SOCCER_DATA_DIR.iterdir():
                    if country_dir.is_dir():
                        for league_dir in country_dir.iterdir():
                            if league_dir.is_dir() and list(league_dir.glob("*_season.json")):
                                league_count += 1
                status["soccer"]["leagues_downloaded"] = league_count
            
            # Check metadata files for last updated times
            mlb_metadata = PROCESSED_DATA_DIR / "mlb_metadata.json"
            if mlb_metadata.exists():
                with open(mlb_metadata, 'r') as f:
                    metadata = json.load(f)
                    status["mlb"]["last_updated"] = metadata.get("last_updated", "Unknown")
            
            summary_file = PROCESSED_DATA_DIR / "data_summary.json"
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
                    status["soccer"]["last_updated"] = summary.get("last_updated", "Unknown")
            
        except Exception as e:
            logger.error(f"❌ Failed to get data status: {e}")
        
        return status
    
    def clean_old_data(self, days_old: int = 30) -> bool:
        """Clean up old data files to save space."""
        
        try:
            logger.info(f"🧹 Cleaning data older than {days_old} days...")
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            # Clean old files in all data directories
            for directory in [MLB_DATA_DIR, SOCCER_DATA_DIR]:
                if directory.exists():
                    for file_path in directory.rglob("*"):
                        if file_path.is_file():
                            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                            if file_time < cutoff_date:
                                file_path.unlink()
                                cleaned_count += 1
            
            logger.info(f"✅ Cleaned {cleaned_count} old files")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to clean old data: {e}")
            return False

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main CLI interface for data management."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Historical Data Manager for Universal Betting Dashboard")
    parser.add_argument("--action", choices=["download-mlb", "download-soccer", "process", "update-all", "status", "clean"], 
                       default="status", help="Action to perform")
    parser.add_argument("--years", type=int, default=5, help="Number of years for MLB data")
    parser.add_argument("--seasons", type=int, default=3, help="Number of seasons for soccer data")
    parser.add_argument("--clean-days", type=int, default=30, help="Days old for cleaning")
    
    args = parser.parse_args()
    
    data_manager = DataManager()
    
    if args.action == "download-mlb":
        print("🏀 Downloading MLB historical data...")
        success = data_manager.download_mlb_historical_data()
        print(f"{'✅ Success' if success else '❌ Failed'}")
    
    elif args.action == "download-soccer":
        print("⚽ Downloading soccer historical data...")
        success = data_manager.download_soccer_historical_data(args.seasons)
        print(f"{'✅ Success' if success else '❌ Failed'}")
    
    elif args.action == "process":
        print("🔄 Processing all data...")
        results = data_manager.process_all_data()
        print(f"Results: {results}")
    
    elif args.action == "update-all":
        print("🚀 Updating all data sources...")
        results = data_manager.update_all_data()
        print(f"Results: {results}")
    
    elif args.action == "status":
        print("📊 Checking data status...")
        status = data_manager.get_data_status()
        print(json.dumps(status, indent=2))
    
    elif args.action == "clean":
        print(f"🧹 Cleaning data older than {args.clean_days} days...")
        success = data_manager.clean_old_data(args.clean_days)
        print(f"{'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    main()