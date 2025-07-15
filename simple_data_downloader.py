#!/usr/bin/env python3
"""
Simplified Historical Data Downloader

This script downloads:
1. MLB historical data from SportsData.io
2. Provides framework for FootyStats soccer data (manual configuration)

Usage:
    python3 simple_data_downloader.py --mlb
    python3 simple_data_downloader.py --soccer --test-api
    python3 simple_data_downloader.py --all
"""

import argparse
import json
import os
import time
import requests
from datetime import datetime
from pathlib import Path

# Create data directories
DATA_DIR = Path("historical_data")
MLB_DATA_DIR = DATA_DIR / "mlb"
SOCCER_DATA_DIR = DATA_DIR / "soccer"

for dir_path in [DATA_DIR, MLB_DATA_DIR, SOCCER_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Configuration
FOOTYSTATS_API_KEY = "b44de69d5777cd2c78d81d59a85d0a91154e836320016b53ecdc1f646fc95b97"
ODDS_API_KEY = "f25b4597c8275546821c5d47a2f727eb"
SPORTSDATA_IO_URL = "https://sportsdata.io/members/download-file?product=f1cdda93-8f32-47bf-b5a9-4bc4f93947f6"

# Sample FootyStats endpoints to test
FOOTYSTATS_TEST_ENDPOINTS = [
    "https://api.footystats.org/leagues",
    "https://api.footystats.org/season-league-table",
    "https://api.footystats.org/league-matches",
]

class SimpleDataDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Historical Data Downloader v1.0'
        })
    
    def download_mlb_data(self) -> bool:
        """Download MLB historical data from SportsData.io"""
        print("🏈 Downloading MLB historical data from SportsData.io...")
        
        try:
            print(f"🔗 Fetching data from: {SPORTSDATA_IO_URL}")
            response = self.session.get(SPORTSDATA_IO_URL, timeout=300)
            response.raise_for_status()
            
            # Save the data
            filename = MLB_DATA_DIR / f"mlb_historical_data_{datetime.now().strftime('%Y%m%d')}.zip"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size_mb = len(response.content) / (1024*1024)
            print(f"✅ MLB data downloaded successfully!")
            print(f"📁 File: {filename}")
            print(f"📊 Size: {file_size_mb:.2f} MB")
            
            # Extract some basic info about the file
            if response.headers.get('content-type'):
                print(f"📄 Content-Type: {response.headers.get('content-type')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error downloading MLB data: {e}")
            return False
    
    def test_footystats_api(self) -> bool:
        """Test different FootyStats API endpoints to find the correct one"""
        print("🔌 Testing FootyStats API endpoints...")
        print(f"🔑 API Key: {FOOTYSTATS_API_KEY[:20]}...")
        
        success_count = 0
        
        for endpoint in FOOTYSTATS_TEST_ENDPOINTS:
            try:
                print(f"\n🧪 Testing: {endpoint}")
                
                # Try different parameter formats
                test_params = [
                    {"key": FOOTYSTATS_API_KEY},
                    {"api_key": FOOTYSTATS_API_KEY},
                    {"token": FOOTYSTATS_API_KEY},
                ]
                
                for i, params in enumerate(test_params):
                    try:
                        response = self.session.get(endpoint, params=params, timeout=10)
                        
                        print(f"  📊 Status Code: {response.status_code}")
                        print(f"  📋 Response Headers: {dict(response.headers)}")
                        
                        if response.status_code == 200:
                            print(f"  ✅ Success with params: {params}")
                            
                            # Try to parse JSON
                            try:
                                data = response.json()
                                print(f"  📄 Response Type: {type(data)}")
                                if isinstance(data, dict):
                                    print(f"  🔑 Keys: {list(data.keys())}")
                                elif isinstance(data, list):
                                    print(f"  📊 List Length: {len(data)}")
                                
                                # Save successful response for analysis
                                test_file = SOCCER_DATA_DIR / f"test_response_{endpoint.split('/')[-1]}.json"
                                with open(test_file, 'w') as f:
                                    json.dump(data, f, indent=2)
                                print(f"  💾 Response saved to: {test_file}")
                                
                                success_count += 1
                                break
                                
                            except json.JSONDecodeError:
                                print(f"  📄 Response (first 200 chars): {response.text[:200]}")
                        else:
                            print(f"  ❌ Failed with status {response.status_code}")
                            if response.text:
                                print(f"  📄 Error: {response.text[:200]}")
                    
                    except requests.exceptions.RequestException as e:
                        print(f"  ❌ Request failed: {e}")
                        continue
                
            except Exception as e:
                print(f"❌ Error testing {endpoint}: {e}")
                continue
        
        print(f"\n📊 Test Summary: {success_count}/{len(FOOTYSTATS_TEST_ENDPOINTS)} endpoints successful")
        return success_count > 0
    
    def download_sample_soccer_data(self):
        """Download sample soccer data if API is working"""
        print("⚽ Attempting to download sample soccer data...")
        
        # Test a simple request first
        sample_requests = [
            {
                "name": "Premier League Matches",
                "url": "https://api.footystats.org/league-matches",
                "params": {"key": FOOTYSTATS_API_KEY, "league_id": "premier-league", "season": "2023"}
            },
            {
                "name": "Available Leagues",
                "url": "https://api.footystats.org/leagues", 
                "params": {"key": FOOTYSTATS_API_KEY}
            }
        ]
        
        for request in sample_requests:
            try:
                print(f"\n📥 Trying: {request['name']}")
                response = self.session.get(request["url"], params=request["params"], timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    filename = SOCCER_DATA_DIR / f"sample_{request['name'].lower().replace(' ', '_')}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"✅ Saved: {filename}")
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text[:100]}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def create_api_documentation(self):
        """Create documentation with the API keys and usage instructions"""
        doc_content = f"""# Historical Data Download Configuration

## API Keys Configured

### FootyStats API
- **API Key**: {FOOTYSTATS_API_KEY}
- **Website**: https://footystats.org
- **Documentation**: Check API documentation for correct endpoints

### The Odds API  
- **API Key**: {ODDS_API_KEY}
- **Website**: https://the-odds-api.com
- **Documentation**: https://the-odds-api.com/liveapi/guides/v4/

### SportsData.io MLB Data
- **Download URL**: {SPORTSDATA_IO_URL}
- **Data Type**: Historical MLB data archive

## Usage Instructions

### Download MLB Data
```bash
python3 simple_data_downloader.py --mlb
```

### Test FootyStats API
```bash
python3 simple_data_downloader.py --soccer --test-api
```

### Download All Available Data
```bash
python3 simple_data_downloader.py --all
```

## File Structure
```
historical_data/
├── mlb/
│   └── mlb_historical_data_YYYYMMDD.zip
├── soccer/
│   ├── test_responses/
│   └── sample_data/
└── download_report_YYYYMMDD_HHMM.json
```

## Soccer Leagues Target List (50 leagues)
{self._get_league_list()}

## Next Steps
1. Run the test commands to verify API connectivity
2. Check test responses to understand the data structure
3. Update the download script with correct league IDs
4. Implement bulk historical data download

## Manual League Configuration
If you need to configure specific league IDs manually, create a file called 
`soccer_league_config.json` with the following structure:

```json
{{
  "leagues": {{
    "English Premier League": {{
      "id": "premier-league",
      "country": "England",
      "priority": 1
    }},
    "Spanish La Liga": {{
      "id": "la-liga", 
      "country": "Spain",
      "priority": 1
    }}
  }}
}}
```
"""
        
        doc_file = DATA_DIR / "API_CONFIGURATION.md"
        with open(doc_file, 'w') as f:
            f.write(doc_content)
        
        print(f"📚 API documentation created: {doc_file}")
        return doc_file
    
    def _get_league_list(self):
        """Get formatted list of target leagues"""
        leagues = [
            "🇦🇷 Argentina: Argentine Primera División, Argentina Primera Nacional",
            "🇦🇺 Australia: A-League", 
            "🇦🇹 Austria: Austrian Bundesliga",
            "🇧🇪 Belgium: Belgian Pro League",
            "🇧🇷 Brazil: Brazilian Serie A",
            "🇨🇱 Chile: Chilean Primera Division",
            "🇨🇳 China: Chinese Super League",
            "🇨🇴 Colombia: Colombian Primera A",
            "🇭🇷 Croatia: Croatian HNL",
            "🇨🇾 Cyprus: Cypriot First Division",
            "🇨🇿 Czech Republic: Czech First League",
            "🇩🇰 Denmark: Danish Superliga, Danish 1st Division",
            "🇪🇨 Ecuador: Ecuadorian Serie A",
            "🏴󠁧󠁢󠁥󠁮󠁧󠁿 England: English Premier League, English Championship",
            "🇫🇷 France: French Ligue 1, French Ligue 2",
            "🇩🇪 Germany: German Bundesliga, German 2. Bundesliga",
            "🇬🇷 Greece: Greek Super League",
            "🇮🇳 India: Indian Super League",
            "🇮🇱 Israel: Israeli Premier League",
            "🇮🇹 Italy: Italian Serie A, Italian Serie B",
            "🇯🇵 Japan: Japanese J1 League, Japanese J2 League",
            "🇲🇽 Mexico: Liga MX",
            "🇳🇱 Netherlands: Dutch Eredivisie",
            "🇳🇴 Norway: Norwegian Eliteserien, Norwegian OBOS-ligaen",
            "🇵🇪 Peru: Peruvian Liga 1",
            "🇵🇱 Poland: Polish Ekstraklasa",
            "🇵🇹 Portugal: Portuguese Primeira Liga",
            "🇶🇦 Qatar: Qatari Stars League",
            "🇷🇴 Romania: Romanian Liga I",
            "🇷🇺 Russia: Russian Premier League",
            "🇸🇦 Saudi Arabia: Saudi Professional League",
            "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland: Scottish Premiership",
            "🇷🇸 Serbia: Serbian SuperLiga",
            "🇰🇷 South Korea: K League 1",
            "🇪🇸 Spain: Spanish La Liga, Spanish LaLiga2",
            "🇸🇪 Sweden: Swedish Allsvenskan",
            "🇨🇭 Switzerland: Swiss Super League",
            "🇹🇷 Turkey: Turkish Super Lig",
            "🇺🇦 Ukraine: Ukrainian Premier League",
            "🇺🇸 United States: US MLS",
            "🇺🇾 Uruguay: Uruguayan Primera Division"
        ]
        return "\n".join([f"- {league}" for league in leagues])
    
    def generate_summary_report(self):
        """Generate summary report of downloaded data"""
        print("\n📋 Generating summary report...")
        
        report = {
            "download_date": datetime.now().isoformat(),
            "api_keys_configured": {
                "footystats": FOOTYSTATS_API_KEY[:20] + "...",
                "odds_api": ODDS_API_KEY[:20] + "...",
                "sportsdata_io": "Direct download URL"
            },
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
        soccer_files = list(SOCCER_DATA_DIR.glob("*.json"))
        if soccer_files:
            report["soccer_data"]["test_files"] = len(soccer_files)
            report["soccer_data"]["files"] = [f.name for f in soccer_files]
        
        # Calculate total size
        for file_path in DATA_DIR.rglob("*"):
            if file_path.is_file():
                report["total_files"] += 1
                report["total_size_mb"] += file_path.stat().st_size / (1024 * 1024)
        
        # Save report
        report_file = DATA_DIR / f"download_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Summary report saved: {report_file}")
        print(f"📁 Total files: {report['total_files']}")
        print(f"💾 Total size: {report['total_size_mb']:.2f} MB")
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Download historical sports data")
    parser.add_argument("--mlb", action="store_true", help="Download MLB data")
    parser.add_argument("--soccer", action="store_true", help="Test soccer API")
    parser.add_argument("--test-api", action="store_true", help="Test FootyStats API endpoints")
    parser.add_argument("--all", action="store_true", help="Download all available data")
    
    args = parser.parse_args()
    
    downloader = SimpleDataDownloader()
    
    print("🚀 Simplified Historical Sports Data Downloader")
    print("=" * 60)
    
    # Create API documentation
    downloader.create_api_documentation()
    
    if args.mlb or args.all:
        print("\n" + "="*60)
        downloader.download_mlb_data()
    
    if args.soccer or args.all or args.test_api:
        print("\n" + "="*60)
        if args.test_api or args.all:
            downloader.test_footystats_api()
        
        if args.soccer or args.all:
            downloader.download_sample_soccer_data()
    
    # Generate summary report
    print("\n" + "="*60)
    downloader.generate_summary_report()
    
    print(f"\n✅ Process completed!")
    print(f"📁 Data directory: {DATA_DIR.absolute()}")
    print(f"📚 Documentation: {DATA_DIR / 'API_CONFIGURATION.md'}")

if __name__ == "__main__":
    main()