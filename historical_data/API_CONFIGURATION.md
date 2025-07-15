# Historical Data Download Configuration

## API Keys Configured

### FootyStats API
- **API Key**: b44de69d5777cd2c78d81d59a85d0a91154e836320016b53ecdc1f646fc95b97
- **Website**: https://footystats.org
- **Documentation**: Check API documentation for correct endpoints

### The Odds API  
- **API Key**: f25b4597c8275546821c5d47a2f727eb
- **Website**: https://the-odds-api.com
- **Documentation**: https://the-odds-api.com/liveapi/guides/v4/

### SportsData.io MLB Data
- **Download URL**: https://sportsdata.io/members/download-file?product=f1cdda93-8f32-47bf-b5a9-4bc4f93947f6
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
- 🇦🇷 Argentina: Argentine Primera División, Argentina Primera Nacional
- 🇦🇺 Australia: A-League
- 🇦🇹 Austria: Austrian Bundesliga
- 🇧🇪 Belgium: Belgian Pro League
- 🇧🇷 Brazil: Brazilian Serie A
- 🇨🇱 Chile: Chilean Primera Division
- 🇨🇳 China: Chinese Super League
- 🇨🇴 Colombia: Colombian Primera A
- 🇭🇷 Croatia: Croatian HNL
- 🇨🇾 Cyprus: Cypriot First Division
- 🇨🇿 Czech Republic: Czech First League
- 🇩🇰 Denmark: Danish Superliga, Danish 1st Division
- 🇪🇨 Ecuador: Ecuadorian Serie A
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England: English Premier League, English Championship
- 🇫🇷 France: French Ligue 1, French Ligue 2
- 🇩🇪 Germany: German Bundesliga, German 2. Bundesliga
- 🇬🇷 Greece: Greek Super League
- 🇮🇳 India: Indian Super League
- 🇮🇱 Israel: Israeli Premier League
- 🇮🇹 Italy: Italian Serie A, Italian Serie B
- 🇯🇵 Japan: Japanese J1 League, Japanese J2 League
- 🇲🇽 Mexico: Liga MX
- 🇳🇱 Netherlands: Dutch Eredivisie
- 🇳🇴 Norway: Norwegian Eliteserien, Norwegian OBOS-ligaen
- 🇵🇪 Peru: Peruvian Liga 1
- 🇵🇱 Poland: Polish Ekstraklasa
- 🇵🇹 Portugal: Portuguese Primeira Liga
- 🇶🇦 Qatar: Qatari Stars League
- 🇷🇴 Romania: Romanian Liga I
- 🇷🇺 Russia: Russian Premier League
- 🇸🇦 Saudi Arabia: Saudi Professional League
- 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland: Scottish Premiership
- 🇷🇸 Serbia: Serbian SuperLiga
- 🇰🇷 South Korea: K League 1
- 🇪🇸 Spain: Spanish La Liga, Spanish LaLiga2
- 🇸🇪 Sweden: Swedish Allsvenskan
- 🇨🇭 Switzerland: Swiss Super League
- 🇹🇷 Turkey: Turkish Super Lig
- 🇺🇦 Ukraine: Ukrainian Premier League
- 🇺🇸 United States: US MLS
- 🇺🇾 Uruguay: Uruguayan Primera Division

## Next Steps
1. Run the test commands to verify API connectivity
2. Check test responses to understand the data structure
3. Update the download script with correct league IDs
4. Implement bulk historical data download

## Manual League Configuration
If you need to configure specific league IDs manually, create a file called 
`soccer_league_config.json` with the following structure:

```json
{
  "leagues": {
    "English Premier League": {
      "id": "premier-league",
      "country": "England",
      "priority": 1
    },
    "Spanish La Liga": {
      "id": "la-liga", 
      "country": "Spain",
      "priority": 1
    }
  }
}
```
