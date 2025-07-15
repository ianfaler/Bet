#!/usr/bin/env python3
"""
FootyStats League Configuration Script

This script fetches available leagues from FootyStats API and creates a mapping
for the 50 leagues we need for historical data download.
"""

import json
import requests
import os
from typing import Dict, List
from difflib import get_close_matches

# API Configuration
FOOTYSTATS_API_KEY = "b44de69d5777cd2c78d81d59a85d0a91154e836320016b53ecdc1f646fc95b97"

# Target leagues we need to map
TARGET_LEAGUES = [
    # Argentina
    "Argentine Primera División", "Argentina Primera Nacional",
    # Australia
    "A-League",
    # Austria
    "Austrian Bundesliga",
    # Belgium
    "Belgian Pro League",
    # Brazil
    "Brazilian Serie A",
    # Chile
    "Chilean Primera Division",
    # China
    "Chinese Super League",
    # Colombia
    "Colombian Primera A",
    # Croatia
    "Croatian HNL",
    # Cyprus
    "Cypriot First Division",
    # Czech Republic
    "Czech First League",
    # Denmark
    "Danish Superliga", "Danish 1st Division",
    # Ecuador
    "Ecuadorian Serie A",
    # England
    "English Premier League", "English Championship",
    # France
    "French Ligue 1", "French Ligue 2",
    # Germany
    "German Bundesliga", "German 2. Bundesliga",
    # Greece
    "Greek Super League",
    # India
    "Indian Super League",
    # Israel
    "Israeli Premier League",
    # Italy
    "Italian Serie A", "Italian Serie B",
    # Japan
    "Japanese J1 League", "Japanese J2 League",
    # Mexico
    "Liga MX",
    # Netherlands
    "Dutch Eredivisie",
    # Norway
    "Norwegian Eliteserien", "Norwegian OBOS-ligaen",
    # Peru
    "Peruvian Liga 1",
    # Poland
    "Polish Ekstraklasa",
    # Portugal
    "Portuguese Primeira Liga",
    # Qatar
    "Qatari Stars League",
    # Romania
    "Romanian Liga I",
    # Russia
    "Russian Premier League",
    # Saudi Arabia
    "Saudi Professional League",
    # Scotland
    "Scottish Premiership",
    # Serbia
    "Serbian SuperLiga",
    # South Korea
    "K League 1",
    # Spain
    "Spanish La Liga", "Spanish LaLiga2",
    # Sweden
    "Swedish Allsvenskan",
    # Switzerland
    "Swiss Super League",
    # Turkey
    "Turkish Super Lig",
    # Ukraine
    "Ukrainian Premier League",
    # United States
    "US MLS",
    # Uruguay
    "Uruguayan Primera Division"
]

class FootyStatsLeagueMapper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Historical Data Downloader v1.0'
        })
    
    def fetch_all_leagues(self) -> List[Dict]:
        """Fetch all available leagues from FootyStats API"""
        print("🌍 Fetching all leagues from FootyStats API...")
        
        try:
            url = "https://api.footystats.org/leagues"
            params = {"key": FOOTYSTATS_API_KEY}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict) and 'data' in data:
                leagues = data['data']
            else:
                leagues = data
            
            print(f"✅ Found {len(leagues)} leagues in FootyStats API")
            return leagues
            
        except Exception as e:
            print(f"❌ Error fetching leagues: {e}")
            return []
    
    def create_league_mapping(self, api_leagues: List[Dict]) -> Dict:
        """Create mapping between target leagues and FootyStats league IDs"""
        print("🔗 Creating league mapping...")
        
        # Create a searchable list of API league names
        api_league_names = []
        api_league_lookup = {}
        
        for league in api_leagues:
            name = league.get('name', '')
            league_id = league.get('id', '')
            country = league.get('country', {}).get('name', '') if isinstance(league.get('country'), dict) else str(league.get('country', ''))
            
            api_league_names.append(name)
            api_league_lookup[name] = {
                'id': league_id,
                'name': name,
                'country': country,
                'season_format': league.get('season_format', ''),
                'active': league.get('active', True)
            }
        
        # Map target leagues to API leagues
        mapping = {}
        unmapped = []
        
        for target_league in TARGET_LEAGUES:
            # Try exact match first
            if target_league in api_league_lookup:
                mapping[target_league] = api_league_lookup[target_league]
                continue
            
            # Try fuzzy matching
            matches = get_close_matches(target_league, api_league_names, n=3, cutoff=0.6)
            if matches:
                best_match = matches[0]
                mapping[target_league] = api_league_lookup[best_match]
                mapping[target_league]['fuzzy_match'] = True
                mapping[target_league]['original_target'] = target_league
                print(f"  📍 Fuzzy match: '{target_league}' -> '{best_match}'")
            else:
                unmapped.append(target_league)
                print(f"  ❌ No match found for: '{target_league}'")
        
        print(f"✅ Mapped {len(mapping)}/{len(TARGET_LEAGUES)} leagues")
        if unmapped:
            print(f"⚠️  Unmapped leagues: {len(unmapped)}")
        
        return mapping, unmapped
    
    def save_configuration(self, mapping: Dict, unmapped: List[str]):
        """Save the league mapping configuration"""
        config = {
            "footystats_api_key": FOOTYSTATS_API_KEY,
            "mapped_leagues": mapping,
            "unmapped_leagues": unmapped,
            "total_mapped": len(mapping),
            "total_unmapped": len(unmapped),
            "generated_at": "2024-01-01T12:00:00Z"
        }
        
        # Save detailed configuration
        with open('footystats_league_mapping.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create Python configuration file
        python_config = f'''# FootyStats League Configuration
# Generated automatically from FootyStats API

FOOTYSTATS_API_KEY = "{FOOTYSTATS_API_KEY}"

# League ID mappings for historical data download
FOOTYSTATS_LEAGUE_IDS = {{
'''
        
        for target_league, info in mapping.items():
            league_id = info['id']
            country = info['country']
            python_config += f'    "{target_league}": {{"id": "{league_id}", "country": "{country}"}},\n'
        
        python_config += '}\n'
        
        with open('footystats_config.py', 'w') as f:
            f.write(python_config)
        
        print("💾 Configuration saved:")
        print(f"  📄 JSON config: footystats_league_mapping.json")
        print(f"  🐍 Python config: footystats_config.py")
        
        return config
    
    def test_api_connection(self):
        """Test FootyStats API connection"""
        print("🔌 Testing FootyStats API connection...")
        
        try:
            url = "https://api.footystats.org/leagues"
            params = {"key": FOOTYSTATS_API_KEY}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            print("✅ API connection successful!")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    def display_summary(self, mapping: Dict, unmapped: List[str]):
        """Display a summary of the mapping results"""
        print("\n" + "="*60)
        print("📊 FOOTYSTATS LEAGUE MAPPING SUMMARY")
        print("="*60)
        
        print(f"\n✅ Successfully mapped: {len(mapping)} leagues")
        print(f"❌ Failed to map: {len(unmapped)} leagues")
        print(f"📈 Success rate: {len(mapping)/(len(mapping)+len(unmapped))*100:.1f}%")
        
        if unmapped:
            print(f"\n⚠️  Unmapped leagues:")
            for league in unmapped:
                print(f"   • {league}")
        
        print(f"\n🔑 API Key configured: {FOOTYSTATS_API_KEY[:20]}...")
        print(f"📁 Config files generated: footystats_league_mapping.json, footystats_config.py")

def main():
    mapper = FootyStatsLeagueMapper()
    
    print("🚀 FootyStats League Configuration Tool")
    print("="*50)
    
    # Test API connection
    if not mapper.test_api_connection():
        print("❌ Cannot proceed without valid API connection")
        return
    
    # Fetch all leagues
    api_leagues = mapper.fetch_all_leagues()
    if not api_leagues:
        print("❌ No leagues fetched from API")
        return
    
    # Create mapping
    mapping, unmapped = mapper.create_league_mapping(api_leagues)
    
    # Save configuration
    config = mapper.save_configuration(mapping, unmapped)
    
    # Display summary
    mapper.display_summary(mapping, unmapped)
    
    print(f"\n✅ Configuration complete! You can now run:")
    print(f"   python3 download_historical_data.py --sport soccer")

if __name__ == "__main__":
    main()