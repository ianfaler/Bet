#!/usr/bin/env python3
"""
Historical Data Downloader for MLB and Soccer Leagues

This script downloads:
1. MLB historical data from SportsData.io
2. Historical data for 50 soccer leagues from FootyStats API

Usage:
    python download_historical_data.py --sport mlb
    python download_historical_data.py --sport soccer --league "English Premier League"
    python download_historical_data.py --sport all
"""

import argparse
import json
import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path

# Create data directories
DATA_DIR = Path("historical_data")
MLB_DATA_DIR = DATA_DIR / "mlb"
SOCCER_DATA_DIR = DATA_DIR / "soccer"

for dir_path in [DATA_DIR, MLB_DATA_DIR, SOCCER_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Configuration
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "YOUR_FOOTYSTATS_API_KEY")  # Replace with actual key
SPORTSDATA_IO_URL = "https://sportsdata.io/members/download-file?product=f1cdda93-8f32-47bf-b5a9-4bc4f93947f6"

# Soccer Leagues Configuration - 50 leagues as specified
SOCCER_LEAGUES = {
    "Argentina": {
        "Argentine Primera División": {"id": "primera-division", "priority": 1},
        "Argentina Primera Nacional": {"id": "primera-nacional", "priority": 2}
    },
    "Australia": {
        "A-League": {"id": "a-league", "priority": 1}
    },
    "Austria": {
        "Austrian Bundesliga": {"id": "bundesliga", "priority": 1}
    },
    "Belgium": {
        "Belgian Pro League": {"id": "pro-league", "priority": 1}
    },
    "Brazil": {
        "Brazilian Serie A": {"id": "serie-a", "priority": 1}
    },
    "Chile": {
        "Chilean Primera Division": {"id": "primera-division", "priority": 1}
    },
    "China": {
        "Chinese Super League": {"id": "super-league", "priority": 1}
    },
    "Colombia": {
        "Colombian Primera A": {"id": "primera-a", "priority": 1}
    },
    "Croatia": {
        "Croatian HNL": {"id": "hnl", "priority": 1}
    },
    "Cyprus": {
        "Cypriot First Division": {"id": "first-division", "priority": 1}
    },
    "Czech Republic": {
        "Czech First League": {"id": "first-league", "priority": 1}
    },
    "Denmark": {
        "Danish Superliga": {"id": "superliga", "priority": 1},
        "Danish 1st Division": {"id": "1st-division", "priority": 2}
    },
    "Ecuador": {
        "Ecuadorian Serie A": {"id": "serie-a", "priority": 1}
    },
    "England": {
        "English Premier League": {"id": "premier-league", "priority": 1},
        "English Championship": {"id": "championship", "priority": 2}
    },
    "France": {
        "French Ligue 1": {"id": "ligue-1", "priority": 1},
        "French Ligue 2": {"id": "ligue-2", "priority": 2}
    },
    "Germany": {
        "German Bundesliga": {"id": "bundesliga", "priority": 1},
        "German 2. Bundesliga": {"id": "2-bundesliga", "priority": 2}
    },
    "Greece": {
        "Greek Super League": {"id": "super-league", "priority": 1}
    },
    "India": {
        "Indian Super League": {"id": "super-league", "priority": 1}
    },
    "Israel": {
        "Israeli Premier League": {"id": "premier-league", "priority": 1}
    },
    "Italy": {
        "Italian Serie A": {"id": "serie-a", "priority": 1},
        "Italian Serie B": {"id": "serie-b", "priority": 2}
    },
    "Japan": {
        "Japanese J1 League": {"id": "j1-league", "priority": 1},
        "Japanese J2 League": {"id": "j2-league", "priority": 2}
    },
    "Mexico": {
        "Liga MX": {"id": "liga-mx", "priority": 1}
    },
    "Netherlands": {
        "Dutch Eredivisie": {"id": "eredivisie", "priority": 1}
    },
    "Norway": {
        "Norwegian Eliteserien": {"id": "eliteserien", "priority": 1},
        "Norwegian OBOS-ligaen": {"id": "obos-ligaen", "priority": 2}
    },
    "Peru": {
        "Peruvian Liga 1": {"id": "liga-1", "priority": 1}
    },
    "Poland": {
        "Polish Ekstraklasa": {"id": "ekstraklasa", "priority": 1}
    },
    "Portugal": {
        "Portuguese Primeira Liga": {"id": "primeira-liga", "priority": 1}
    },
    "Qatar": {
        "Qatari Stars League": {"id": "stars-league", "priority": 1}
    },
    "Romania": {
        "Romanian Liga I": {"id": "liga-i", "priority": 1}
    },
    "Russia": {
        "Russian Premier League": {"id": "premier-league", "priority": 1}
    },
    "Saudi Arabia": {
        "Saudi Professional League": {"id": "professional-league", "priority": 1}
    },
    "Scotland": {
        "Scottish Premiership": {"id": "premiership", "priority": 1}
    },
    "Serbia": {
        "Serbian SuperLiga": {"id": "superliga", "priority": 1}
    },
    "South Korea": {
        "K League 1": {"id": "k-league-1", "priority": 1}
    },
    "Spain": {
        "Spanish La Liga": {"id": "la-liga", "priority": 1},
        "Spanish LaLiga2": {"id": "laliga2", "priority": 2}
    },
    "Sweden": {
        "Swedish Allsvenskan": {"id": "allsvenskan", "priority": 1}
    },
    "Switzerland": {
        "Swiss Super League": {"id": "super-league", "priority": 1}
    },
    "Turkey": {
        "Turkish Super Lig": {"id": "super-lig", "priority": 1}
    },
    "Ukraine": {
        "Ukrainian Premier League": {"id": "premier-league", "priority": 1}
    },
    "United States": {
        "US MLS": {"id": "mls", "priority": 1}
    },
    "Uruguay": {
        "Uruguayan Primera Division": {"id": "primera-division", "priority": 1}
    }
}

class HistoricalDataDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_mlb_data(self) -> bool:
        """Download MLB historical data from SportsData.io"""
        print("🏈 Downloading MLB historical data from SportsData.io...")
        
        try:
            response = self.session.get(SPORTSDATA_IO_URL, timeout=300)
            response.raise_for_status()
            
            # Save the data
            filename = MLB_DATA_DIR / f"mlb_historical_data_{datetime.now().strftime('%Y%m%d')}.zip"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ MLB data downloaded successfully: {filename}")
            print(f"📊 File size: {len(response.content) / (1024*1024):.2f} MB")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading MLB data: {e}")
            return False
    
    def get_footystats_leagues(self) -> List[Dict]:
        """Fetch available leagues from FootyStats API"""
        if FOOTYSTATS_API_KEY == "YOUR_FOOTYSTATS_API_KEY":
            print("⚠️  FootyStats API key not configured. Please set FOOTYSTATS_API_KEY environment variable.")
            return []
        
        try:
            url = "https://api.footystats.org/leagues"
            params = {"key": FOOTYSTATS_API_KEY}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"❌ Error fetching FootyStats leagues: {e}")
            return []
    
    def download_league_data(self, league_name: str, league_id: str, country: str, seasons: List[str] = None) -> bool:
        """Download historical data for a specific league"""
        if FOOTYSTATS_API_KEY == "YOUR_FOOTYSTATS_API_KEY":
            print(f"⚠️  Skipping {league_name} - API key not configured")
            return False
        
        print(f"⚽ Downloading {league_name} ({country}) data...")
        
        # Default to last 3 seasons if not specified
        if not seasons:
            current_year = datetime.now().year
            seasons = [f"{current_year-2}-{current_year-1}", f"{current_year-1}-{current_year}", f"{current_year}-{current_year+1}"]
        
        league_dir = SOCCER_DATA_DIR / country.replace(" ", "_") / league_name.replace(" ", "_")
        league_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        
        for season in seasons:
            try:
                # Download matches
                matches_url = "https://api.footystats.org/league-matches"
                params = {
                    "key": FOOTYSTATS_API_KEY,
                    "league_id": league_id,
                    "season": season
                }
                
                response = self.session.get(matches_url, params=params, timeout=60)
                response.raise_for_status()
                matches_data = response.json()
                
                # Save matches data
                matches_file = league_dir / f"matches_{season.replace('-', '_')}.json"
                with open(matches_file, 'w') as f:
                    json.dump(matches_data, f, indent=2)
                
                # Download team stats
                stats_url = "https://api.footystats.org/league-table"
                response = self.session.get(stats_url, params=params, timeout=60)
                response.raise_for_status()
                stats_data = response.json()
                
                # Save stats data
                stats_file = league_dir / f"stats_{season.replace('-', '_')}.json"
                with open(stats_file, 'w') as f:
                    json.dump(stats_data, f, indent=2)
                
                print(f"  ✅ {season} data downloaded")
                success_count += 1
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Error downloading {season} data: {e}")
                continue
        
        print(f"📊 {league_name}: {success_count}/{len(seasons)} seasons downloaded")
        return success_count > 0
    
    def download_all_soccer_leagues(self) -> Dict[str, bool]:
        """Download data for all 50 soccer leagues"""
        print("⚽ Starting download of all 50 soccer leagues...")
        results = {}
        
        for country, leagues in SOCCER_LEAGUES.items():
            print(f"\n🌍 Processing {country}...")
            
            for league_name, config in leagues.items():
                league_id = config["id"]
                success = self.download_league_data(league_name, league_id, country)
                results[f"{country} - {league_name}"] = success
                
                # Be respectful to the API
                time.sleep(2)
        
        return results
    
    def download_specific_league(self, league_name: str) -> bool:
        """Download data for a specific league"""
        for country, leagues in SOCCER_LEAGUES.items():
            if league_name in leagues:
                config = leagues[league_name]
                return self.download_league_data(league_name, config["id"], country)
        
        print(f"❌ League '{league_name}' not found in configuration")
        return False
    
    def generate_summary_report(self):
        """Generate a summary report of downloaded data"""
        print("\n📋 Generating summary report...")
        
        report = {
            "download_date": datetime.now().isoformat(),
            "mlb_data": {},
            "soccer_data": {},
            "total_files": 0,
            "total_size_mb": 0
        }
        
        # Check MLB data
        mlb_files = list(MLB_DATA_DIR.glob("*"))
        if mlb_files:
            report["mlb_data"]["files"] = len(mlb_files)
            report["mlb_data"]["latest_file"] = str(max(mlb_files, key=os.path.getctime))
        
        # Check soccer data
        for country_dir in SOCCER_DATA_DIR.iterdir():
            if country_dir.is_dir():
                country_name = country_dir.name.replace("_", " ")
                report["soccer_data"][country_name] = {}
                
                for league_dir in country_dir.iterdir():
                    if league_dir.is_dir():
                        league_name = league_dir.name.replace("_", " ")
                        files = list(league_dir.glob("*.json"))
                        report["soccer_data"][country_name][league_name] = len(files)
                        report["total_files"] += len(files)
        
        # Calculate total size
        for file_path in DATA_DIR.rglob("*"):
            if file_path.is_file():
                report["total_size_mb"] += file_path.stat().st_size / (1024 * 1024)
        
        # Save report
        report_file = DATA_DIR / f"download_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Summary report saved: {report_file}")
        print(f"📁 Total files: {report['total_files']}")
        print(f"💾 Total size: {report['total_size_mb']:.2f} MB")

def main():
    parser = argparse.ArgumentParser(description="Download historical sports data")
    parser.add_argument("--sport", choices=["mlb", "soccer", "all"], default="all",
                       help="Sport to download data for")
    parser.add_argument("--league", type=str, help="Specific soccer league to download")
    parser.add_argument("--seasons", nargs="+", help="Specific seasons to download (e.g., 2023-2024)")
    
    args = parser.parse_args()
    
    downloader = HistoricalDataDownloader()
    
    print("🚀 Historical Sports Data Downloader")
    print("=" * 50)
    
    if args.sport in ["mlb", "all"]:
        downloader.download_mlb_data()
    
    if args.sport in ["soccer", "all"]:
        if args.league:
            downloader.download_specific_league(args.league)
        else:
            downloader.download_all_soccer_leagues()
    
    # Generate summary report
    downloader.generate_summary_report()
    
    print("\n✅ Download process completed!")
    print(f"📁 Data saved in: {DATA_DIR.absolute()}")

if __name__ == "__main__":
    main()