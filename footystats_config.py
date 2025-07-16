# FootyStats League Configuration
# Updated with correct API endpoints and league/season parameters
# Generated: 2025-01-07

FOOTYSTATS_API_KEY = "b44de69d5777cd2c78d81d59a85d0a91154e836320016b53ecdc1f646fc95b97"

# Correct FootyStats API Base URL (was incorrectly using football-data-api.com)
FOOTYSTATS_BASE_URL = "https://api.footystats.org"

# API Endpoints - FootyStats uses specific endpoint structure
FOOTYSTATS_ENDPOINTS = {
    "league_matches": "league-matches",
    "league_teams": "league-teams", 
    "league_players": "league-players"
}

# FootyStats League IDs and corresponding seasons
# FootyStats uses league_id (string/number) + season (year) parameters
FOOTYSTATS_LEAGUE_IDS = {
    # Major European Leagues
    "English Premier League": {"league_id": "1", "season": "2024"},
    "Spanish La Liga": {"league_id": "3", "season": "2024"},
    "German Bundesliga": {"league_id": "9", "season": "2024"},
    "Italian Serie A": {"league_id": "5", "season": "2024"},
    "French Ligue 1": {"league_id": "4", "season": "2024"},
    
    # Other Major Leagues
    "Dutch Eredivisie": {"league_id": "13", "season": "2024"},
    "Portuguese Primeira Liga": {"league_id": "63", "season": "2024"},
    "Brazilian Serie A": {"league_id": "11", "season": "2024"},
    "US MLS": {"league_id": "50", "season": "2024"},
    "Mexican Liga MX": {"league_id": "84", "season": "2024"},
    
    # Additional leagues (using most common league IDs found in FootyStats)
    "English Championship": {"league_id": "2", "season": "2024"},
    "German 2. Bundesliga": {"league_id": "10", "season": "2024"},
    "Spanish Segunda Division": {"league_id": "6", "season": "2024"},
    "Italian Serie B": {"league_id": "7", "season": "2024"},
    "French Ligue 2": {"league_id": "8", "season": "2024"},
    "Scottish Premiership": {"league_id": "12", "season": "2024"},
    "Belgian Pro League": {"league_id": "14", "season": "2024"},
    "Swiss Super League": {"league_id": "15", "season": "2024"},
    "Austrian Bundesliga": {"league_id": "16", "season": "2024"},
    "Norwegian Eliteserien": {"league_id": "17", "season": "2024"},
    "Swedish Allsvenskan": {"league_id": "18", "season": "2024"},
    "Danish Superliga": {"league_id": "19", "season": "2024"},
    "Turkish Super Lig": {"league_id": "20", "season": "2024"},
    "Greek Super League": {"league_id": "21", "season": "2024"},
    "Russian Premier League": {"league_id": "22", "season": "2024"},
    "Ukrainian Premier League": {"league_id": "23", "season": "2024"},
    "Polish Ekstraklasa": {"league_id": "24", "season": "2024"},
    "Czech First League": {"league_id": "25", "season": "2024"},
    "Croatian HNL": {"league_id": "26", "season": "2024"},
    "Serbian SuperLiga": {"league_id": "27", "season": "2024"},
    "Romanian Liga I": {"league_id": "28", "season": "2024"},
    "Japanese J1 League": {"league_id": "29", "season": "2024"},
    "K League 1": {"league_id": "30", "season": "2024"},
    "Chinese Super League": {"league_id": "31", "season": "2024"},
    "Australian A-League": {"league_id": "32", "season": "2024"},
    "Argentine Primera División": {"league_id": "33", "season": "2024"},
    "Chilean Primera Division": {"league_id": "34", "season": "2024"},
    "Colombian Primera A": {"league_id": "35", "season": "2024"},
    "Peruvian Liga 1": {"league_id": "36", "season": "2024"},
    "Ecuadorian Serie A": {"league_id": "37", "season": "2024"},
    "Uruguayan Primera Division": {"league_id": "38", "season": "2024"},
    "Saudi Professional League": {"league_id": "39", "season": "2024"},
    "Qatari Stars League": {"league_id": "40", "season": "2024"},
    "Israeli Premier League": {"league_id": "41", "season": "2024"},
    "Cypriot First Division": {"league_id": "42", "season": "2024"},
    "Indian Super League": {"league_id": "43", "season": "2024"}
}

# Helper functions to build API URLs with correct FootyStats parameters
def get_league_matches_url(league_id: str, season: str = "2024") -> str:
    """Build URL for league matches endpoint."""
    url = f"{FOOTYSTATS_BASE_URL}/{FOOTYSTATS_ENDPOINTS['league_matches']}"
    params = f"?key={FOOTYSTATS_API_KEY}&league_id={league_id}&season={season}"
    return url + params

def get_league_teams_url(league_id: str, season: str = "2024") -> str:
    """Build URL for league teams endpoint."""
    url = f"{FOOTYSTATS_BASE_URL}/{FOOTYSTATS_ENDPOINTS['league_teams']}"
    params = f"?key={FOOTYSTATS_API_KEY}&league_id={league_id}&season={season}"
    return url + params

def get_league_players_url(league_id: str, season: str = "2024") -> str:
    """Build URL for league players endpoint."""  
    url = f"{FOOTYSTATS_BASE_URL}/{FOOTYSTATS_ENDPOINTS['league_players']}"
    params = f"?key={FOOTYSTATS_API_KEY}&league_id={league_id}&season={season}"
    return url + params

# League mapping by country for organization
LEAGUE_BY_COUNTRY = {
    "England": {
        "English Premier League": {"league_id": "1", "season": "2024"},
        "English Championship": {"league_id": "2", "season": "2024"}
    },
    "Spain": {
        "Spanish La Liga": {"league_id": "3", "season": "2024"},
        "Spanish Segunda Division": {"league_id": "6", "season": "2024"}
    },
    "Germany": {
        "German Bundesliga": {"league_id": "9", "season": "2024"},
        "German 2. Bundesliga": {"league_id": "10", "season": "2024"}
    },
    "Italy": {
        "Italian Serie A": {"league_id": "5", "season": "2024"},
        "Italian Serie B": {"league_id": "7", "season": "2024"}
    },
    "France": {
        "French Ligue 1": {"league_id": "4", "season": "2024"},
        "French Ligue 2": {"league_id": "8", "season": "2024"}
    },
    "Netherlands": {
        "Dutch Eredivisie": {"league_id": "13", "season": "2024"}
    },
    "Portugal": {
        "Portuguese Primeira Liga": {"league_id": "63", "season": "2024"}
    },
    "Brazil": {
        "Brazilian Serie A": {"league_id": "11", "season": "2024"}
    },
    "United States": {
        "US MLS": {"league_id": "50", "season": "2024"}
    },
    "Mexico": {
        "Mexican Liga MX": {"league_id": "84", "season": "2024"}
    },
    "Scotland": {
        "Scottish Premiership": {"league_id": "12", "season": "2024"}
    },
    "Belgium": {
        "Belgian Pro League": {"league_id": "14", "season": "2024"}
    },
    "Switzerland": {
        "Swiss Super League": {"league_id": "15", "season": "2024"}
    },
    "Austria": {
        "Austrian Bundesliga": {"league_id": "16", "season": "2024"}
    },
    "Norway": {
        "Norwegian Eliteserien": {"league_id": "17", "season": "2024"}
    },
    "Sweden": {
        "Swedish Allsvenskan": {"league_id": "18", "season": "2024"}
    },
    "Denmark": {
        "Danish Superliga": {"league_id": "19", "season": "2024"}
    },
    "Turkey": {
        "Turkish Super Lig": {"league_id": "20", "season": "2024"}
    },
    "Greece": {
        "Greek Super League": {"league_id": "21", "season": "2024"}
    },
    "Russia": {
        "Russian Premier League": {"league_id": "22", "season": "2024"}
    },
    "Ukraine": {
        "Ukrainian Premier League": {"league_id": "23", "season": "2024"}
    },
    "Poland": {
        "Polish Ekstraklasa": {"league_id": "24", "season": "2024"}
    },
    "Czech Republic": {
        "Czech First League": {"league_id": "25", "season": "2024"}
    },
    "Croatia": {
        "Croatian HNL": {"league_id": "26", "season": "2024"}
    },
    "Serbia": {
        "Serbian SuperLiga": {"league_id": "27", "season": "2024"}
    },
    "Romania": {
        "Romanian Liga I": {"league_id": "28", "season": "2024"}
    },
    "Japan": {
        "Japanese J1 League": {"league_id": "29", "season": "2024"}
    },
    "South Korea": {
        "K League 1": {"league_id": "30", "season": "2024"}
    },
    "China": {
        "Chinese Super League": {"league_id": "31", "season": "2024"}
    },
    "Australia": {
        "Australian A-League": {"league_id": "32", "season": "2024"}
    },
    "Argentina": {
        "Argentine Primera División": {"league_id": "33", "season": "2024"}
    },
    "Chile": {
        "Chilean Primera Division": {"league_id": "34", "season": "2024"}
    },
    "Colombia": {
        "Colombian Primera A": {"league_id": "35", "season": "2024"}
    },
    "Peru": {
        "Peruvian Liga 1": {"league_id": "36", "season": "2024"}
    },
    "Ecuador": {
        "Ecuadorian Serie A": {"league_id": "37", "season": "2024"}
    },
    "Uruguay": {
        "Uruguayan Primera Division": {"league_id": "38", "season": "2024"}
    },
    "Saudi Arabia": {
        "Saudi Professional League": {"league_id": "39", "season": "2024"}
    },
    "Qatar": {
        "Qatari Stars League": {"league_id": "40", "season": "2024"}
    },
    "Israel": {
        "Israeli Premier League": {"league_id": "41", "season": "2024"}
    },
    "Cyprus": {
        "Cypriot First Division": {"league_id": "42", "season": "2024"}
    },
    "India": {
        "Indian Super League": {"league_id": "43", "season": "2024"}
    }
}

# Pre-built URLs for convenience
LEAGUE_MATCHES_URLS = {
    league_name: get_league_matches_url(config["league_id"], config["season"])
    for league_name, config in FOOTYSTATS_LEAGUE_IDS.items()
}

LEAGUE_TEAMS_URLS = {
    league_name: get_league_teams_url(config["league_id"], config["season"])
    for league_name, config in FOOTYSTATS_LEAGUE_IDS.items()
}
