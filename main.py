# -*- coding: utf-8 -*-
"""Universal Betting Dashboard – Web App Version

This script pulls real-time odds, fetches advanced stats, generates betting
candidates, scores them, applies staking rules and returns structured data
for web app consumption.

Features:
- Multi-sport betting (MLB, NBA, Soccer, WNBA, NHL)
- Sophisticated analytical models (Poisson + Monte Carlo)
- Sharp betting indicators (RLM, CLV, Steam detection)
- Real-time data from multiple APIs
- JSON output for web app integration
- Risk management with Kelly criterion staking
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import requests
from scipy import stats
from tenacity import retry, stop_after_attempt, wait_fixed

warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# Configuration and API keys
# ---------------------------------------------------------------------------

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "f25b4597c8275546821c5d47a2f727eb")
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "b44de69d5777cd2c78d81d59a85d0a91154e836320016b53ecdc1f646fc95b97")
APISPORTS_KEY = os.getenv("APISPORTS_KEY", "0002b89b1ff8422f9c09c72a69c1f3ab")

📁 main.py - Section 1: Imports and Configuration
# -*- coding: utf-8 -*-
"""Universal Betting Dashboard – Web App Version

This script pulls real-time odds, fetches advanced stats, generates betting
candidates, scores them, applies staking rules and returns structured data
for web app consumption.

Features:
- Multi-sport betting (MLB, NBA, Soccer, WNBA, NHL)
- Sophisticated analytical models (Poisson + Monte Carlo)
- Sharp betting indicators (RLM, CLV, Steam detection)
- Real-time data from multiple APIs
- JSON output for web app integration
- Risk management with Kelly criterion staking
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import requests
from scipy import stats
from tenacity import retry, stop_after_attempt, wait_fixed

warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# Configuration and API keys
# ---------------------------------------------------------------------------

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "f25b4597c8275546821c5d47a2f727eb")
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "b44de69d5777cd2c78d81d59a85d0a91154e836320016b53ecdc1f646fc95b97")
APISPORTS_KEY = os.getenv("APISPORTS_KEY", "0002b89b7e2b4bb110848c3aec142b96")
FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY", "1976d5a0686f42d289b6d95f6365b702")
THESPORTSDB_KEY = os.getenv("THESPORTSDB_KEY", "123")

# Model constants
DEFAULT_BANKROLL = 2500
MIN_EV_THRESHOLD = 6.0  # +6% minimum as specified
MIN_CONFIDENCE_THRESHOLD = 8  # Conf >= 8 as specified
MC_SIMULATIONS = 5000
LEAGUE_AVG_RUNS = 4.5  # MLB
LEAGUE_AVG_POINTS = 110  # NBA

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    sport: str
    pick: str
    odds: float
    game_data: Dict[str, Any] = field(default_factory=dict)
    ev: float = 0.0
    confidence: float = 0.0
    flags: List[str] = field(default_factory=list)
    clv_delta: float = 0.0
    model_prob: float = 0.0
    implied_prob: float = 0.0

@dataclass
class Pick(Candidate):
    stake: float = 0.0

@dataclass
class ScanResult:
    timestamp: str
    mode: str
    bankroll: float
    total_candidates: int
    qualified_candidates: int
    official_picks: List[Dict[str, Any]]
    execution_time: float
    sports_scanned: List[str]
    risk_metrics: Dict[str, Any]
    model_performance: Dict[str, Any]
📁 main.py - Section 2: Data Fetching Functions
# ---------------------------------------------------------------------------
# Data fetching functions
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_json(url: str, headers: Dict[str, str] = None, params: Dict[str, str] = None) -> Any:
    """Fetch JSON data with retry logic."""
    try:
        response = requests.get(url, headers=headers or {}, params=params or {}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return {}

def fetch_odds_data(sport: str) -> List[Dict[str, Any]]:
    """Fetch odds from The Odds API."""
    sport_mapping = {
        'MLB': 'baseball_mlb',
        'NBA': 'basketball_nba', 
        'Soccer': 'soccer_epl',
        'WNBA': 'basketball_wnba',
        'NHL': 'icehockey_nhl'
    }
    
    api_sport = sport_mapping.get(sport, sport.lower())
    url = f"https://api.the-odds-api.com/v4/sports/{api_sport}/odds/"
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american'
    }
    
    data = fetch_json(url, params=params)
    return data if isinstance(data, list) else []

def fetch
I see the issue! The main.py file is quite large (858 lines) and may have been truncated or hard to see. Let me break it down into manageable sections for you to copy-paste:

📁 main.py - Section 1: Imports and Configuration
# -*- coding: utf-8 -*-
"""Universal Betting Dashboard – Web App Version

This script pulls real-time odds, fetches advanced stats, generates betting
candidates, scores them, applies staking rules and returns structured data
for web app consumption.

Features:
- Multi-sport betting (MLB, NBA, Soccer, WNBA, NHL)
- Sophisticated analytical models (Poisson + Monte Carlo)
- Sharp betting indicators (RLM, CLV, Steam detection)
- Real-time data from multiple APIs
- JSON output for web app integration
- Risk management with Kelly criterion staking
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import requests
from scipy import stats
from tenacity import retry, stop_after_attempt, wait_fixed

warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# Configuration and API keys
# ---------------------------------------------------------------------------

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "f25b4597c8275546821c5d47a2f727eb")
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "b44de69d5777cd2c78d81d59a85d0a91154e836320016b53ecdc1f646fc95b97")
APISPORTS_KEY = os.getenv("APISPORTS_KEY", "0002b89b7e2b4bb110848c3aec142b96")
FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY", "1976d5a0686f42d289b6d95f6365b702")
THESPORTSDB_KEY = os.getenv("THESPORTSDB_KEY", "123")

# Model constants
DEFAULT_BANKROLL = 2500
MIN_EV_THRESHOLD = 6.0  # +6% minimum as specified
MIN_CONFIDENCE_THRESHOLD = 8  # Conf >= 8 as specified
MC_SIMULATIONS = 5000
LEAGUE_AVG_RUNS = 4.5  # MLB
LEAGUE_AVG_POINTS = 110  # NBA

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    sport: str
    pick: str
    odds: float
    game_data: Dict[str, Any] = field(default_factory=dict)
    ev: float = 0.0
    confidence: float = 0.0
    flags: List[str] = field(default_factory=list)
    clv_delta: float = 0.0
    model_prob: float = 0.0
    implied_prob: float = 0.0

@dataclass
class Pick(Candidate):
    stake: float = 0.0

@dataclass
class ScanResult:
    timestamp: str
    mode: str
    bankroll: float
    total_candidates: int
    qualified_candidates: int
    official_picks: List[Dict[str, Any]]
    execution_time: float
    sports_scanned: List[str]
    risk_metrics: Dict[str, Any]
    model_performance: Dict[str, Any]
📁 main.py - Section 2: Data Fetching Functions
# ---------------------------------------------------------------------------
# Data fetching functions
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_json(url: str, headers: Dict[str, str] = None, params: Dict[str, str] = None) -> Any:
    """Fetch JSON data with retry logic."""
    try:
        response = requests.get(url, headers=headers or {}, params=params or {}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return {}

def fetch_odds_data(sport: str) -> List[Dict[str, Any]]:
    """Fetch odds from The Odds API."""
    sport_mapping = {
        'MLB': 'baseball_mlb',
        'NBA': 'basketball_nba', 
        'Soccer': 'soccer_epl',
        'WNBA': 'basketball_wnba',
        'NHL': 'icehockey_nhl'
    }
    
    api_sport = sport_mapping.get(sport, sport.lower())
    url = f"https://api.the-odds-api.com/v4/sports/{api_sport}/odds/"
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american'
    }
    
    data = fetch_json(url, params=params)
    return data if isinstance(data, list) else []

def fetch_mlb_stats(date: str = None) -> Dict[str, Any]:
    """Fetch MLB advanced stats."""
    # In production, this would call MLB StatsAPI or Statcast
    # For now, return realistic sample data structure
    return {
        'pitcher_stats': {
            'era_home': 3.45,
            'era_away': 4.82,
            'xfip_home': 3.22,
            'xfip_away': 4.55,
            'k_rate_home': 0.24,
            'k_rate_away': 0.21
        },
        'team_stats': {
            'wrc_plus_home': 108,
            'wrc_plus_away': 95,
            'bullpen_era_home': 3.78,
            'bullpen_era_away': 4.15
        },
        'game_factors': {
            'park_factor': 0.98,
            'weather_wind': 8,
            'weather_temp': 72,
            'umpire_k_rate': 0.22
        }
    }

def fetch_soccer_stats(date: str = None) -> Dict[str, Any]:
    """Fetch soccer stats from FootyStats API."""
    url = 'https://api.footystats.org/league-matches'
    params = {
        'key': FOOTBALL_DATA_KEY,  # Using Football-Data key for now
        'date': date or datetime.now().strftime('%Y-%m-%d')
    }
    
    data = fetch_json(url, params=params)
    
    # Return sample structure if API fails
    if not data:
        return {
            'team_stats': {
                'xg_home': 1.65,
                'xg_away': 1.42,
                'ppda_home': 12.5,
                'ppda_away': 15.2,
                'form_home': 'WWLDW',
                'form_away': 'DLWWL'
            },
            'match_factors': {
                'importance': 0.8,
                'rest_days_home': 3,
                'rest
I see the issue! The main.py file is quite large (858 lines) and may have been truncated or hard to see. Let me break it down into manageable sections for you to copy-paste:

📁 main.py - Section 1: Imports and Configuration
# -*- coding: utf-8 -*-
"""Universal Betting Dashboard – Web App Version

This script pulls real-time odds, fetches advanced stats, generates betting
candidates, scores them, applies staking rules and returns structured data
for web app consumption.

Features:
- Multi-sport betting (MLB, NBA, Soccer, WNBA, NHL)
- Sophisticated analytical models (Poisson + Monte Carlo)
- Sharp betting indicators (RLM, CLV, Steam detection)
- Real-time data from multiple APIs
- JSON output for web app integration
- Risk management with Kelly criterion staking
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import requests
from scipy import stats
from tenacity import retry, stop_after_attempt, wait_fixed

warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# Configuration and API keys
# ---------------------------------------------------------------------------

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "f25b4597c8275546821c5d47a2f727eb")
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "b44de69d5777cd2c78d81d59a85d0a91154e836320016b53ecdc1f646fc95b97")
APISPORTS_KEY = os.getenv("APISPORTS_KEY", "0002b89b7e2b4bb110848c3aec142b96")
FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY", "1976d5a0686f42d289b6d95f6365b702")
THESPORTSDB_KEY = os.getenv("THESPORTSDB_KEY", "123")

# Model constants
DEFAULT_BANKROLL = 2500
MIN_EV_THRESHOLD = 6.0  # +6% minimum as specified
MIN_CONFIDENCE_THRESHOLD = 8  # Conf >= 8 as specified
MC_SIMULATIONS = 5000
LEAGUE_AVG_RUNS = 4.5  # MLB
LEAGUE_AVG_POINTS = 110  # NBA

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    sport: str
    pick: str
    odds: float
    game_data: Dict[str, Any] = field(default_factory=dict)
    ev: float = 0.0
    confidence: float = 0.0
    flags: List[str] = field(default_factory=list)
    clv_delta: float = 0.0
    model_prob: float = 0.0
    implied_prob: float = 0.0

@dataclass
class Pick(Candidate):
    stake: float = 0.0

@dataclass
class ScanResult:
    timestamp: str
    mode: str
    bankroll: float
    total_candidates: int
    qualified_candidates: int
    official_picks: List[Dict[str, Any]]
    execution_time: float
    sports_scanned: List[str]
    risk_metrics: Dict[str, Any]
    model_performance: Dict[str, Any]
📁 main.py - Section 2: Data Fetching Functions
# ---------------------------------------------------------------------------
# Data fetching functions
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_json(url: str, headers: Dict[str, str] = None, params: Dict[str, str] = None) -> Any:
    """Fetch JSON data with retry logic."""
    try:
        response = requests.get(url, headers=headers or {}, params=params or {}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return {}

def fetch_odds_data(sport: str) -> List[Dict[str, Any]]:
    """Fetch odds from The Odds API."""
    sport_mapping = {
        'MLB': 'baseball_mlb',
        'NBA': 'basketball_nba', 
        'Soccer': 'soccer_epl',
        'WNBA': 'basketball_wnba',
        'NHL': 'icehockey_nhl'
    }
    
    api_sport = sport_mapping.get(sport, sport.lower())
    url = f"https://api.the-odds-api.com/v4/sports/{api_sport}/odds/"
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american'
    }
    
    data = fetch_json(url, params=params)
    return data if isinstance(data, list) else []

def fetch_mlb_stats(date: str = None) -> Dict[str, Any]:
    """Fetch MLB advanced stats."""
    # In production, this would call MLB StatsAPI or Statcast
    # For now, return realistic sample data structure
    return {
        'pitcher_stats': {
            'era_home': 3.45,
            'era_away': 4.82,
            'xfip_home': 3.22,
            'xfip_away': 4.55,
            'k_rate_home': 0.24,
            'k_rate_away': 0.21
        },
        'team_stats': {
            'wrc_plus_home': 108,
            'wrc_plus_away': 95,
            'bullpen_era_home': 3.78,
            'bullpen_era_away': 4.15
        },
        'game_factors': {
            'park_factor': 0.98,
            'weather_wind': 8,
            'weather_temp': 72,
            'umpire_k_rate': 0.22
        }
    }

def fetch_soccer_stats(date: str = None, league_id: int = None) -> Dict[str, Any]:
    """Fetch soccer stats from FootyStats API using correct 2025 league IDs."""
    from footystats_config import FOOTYSTATS_API_KEY
    
    url = 'https://api.footystats.org/league-matches'
    params = {
        'key': FOOTYSTATS_API_KEY,
        'league_id': str(league_id or 13943),  # Default to Premier League
        'season': str(datetime.now().year)
    }
    
    if date:
        params['date'] = date
    
    data = fetch_json(url, params=params)
    
    # Return sample structure if API fails
    if not data:
        return {
            'team_stats': {
                'xg_home': 1.65,
                'xg_away': 1.42,
                'ppda_home': 12.5,
                'ppda_away': 15.2,
                'form_home': 'WWLDW',
                'form_away': 'DLWWL'
            },
            'match_factors': {
                'importance': 0.8,
                'rest_days_home': 3,
                'rest_days_away': 4
            }
        }
    return data

def fetch_nba_stats() -> Dict[str, Any]:
    """Fetch NBA advanced stats."""
    # Would use balldontlie or NBA.com API
    return {
        'team_stats': {
            'pace_home': 102.5,
            'pace_away': 98.7,
            'efg_home': 0.545,
            'efg_away': 0.521,
            'ts_home': 0.572,
            'ts_away': 0.548
        },
        'injury_impact': {
            'home_impact': 0.02,
            'away_impact': 0.05
        }
    }

def fetch_injury_data(sport: str) -> Dict[str, Any]:
    """Fetch injury data from RotoWire."""
    sport_urls = {
        'MLB': 'https://www.rotowire.com/baseball/injury-report.php',
        'NBA': 'https://www.rotowire.com/basketball/nba/injury-report.php',
        'NFL': 'https://www.rotowire.com/football/nfl/injury-report.php'
    }
    
    url = sport_urls.get(sport)
    if not url:
        return {}
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            tables = pd.read_html(response.text)
            if tables:
                return {'injuries': tables[0].to_dict('records')}
    except Exception as e:
        print(f"Injury fetch failed for {sport}: {e}")
    
    return {}
Would you like me to continue with the remaining sections of main.py? There are about 6 more sections:

Section 3: Sophisticated Model Functions
Section 4: Candidate Generation and Scoring
Section 5: Bankroll Management
Section 6: Main Workflow Orchestration
Section 7: Web App Interface Functions
Section 8: CLI Entry Point
Just let me know and I'll provide the next sections!

yes provide them all
Thought for 4s
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_
Thought for 1s
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_nba_probability(game_data)
        elif sport == 'Soccer':
            return _calculate_soccer_probability(game_data)
        else:
            return 0.5  # Default neutral probability
    except Exception as e:
        print(f"Analytical calculation error for {sport}: {e}")
        return 0.5

def _calculate_mlb_probability(game_data: Dict[str, Any]) -> float:
    """MLB-specific Poisson-based probability calculation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    # Calculate expected runs (better pitcher = lower ERA = fewer runs allowed)
    home_expected_runs = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_expected_runs = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    # Adjust for rest days
    rest_home = game_data.get('rest_days_home', 1)
    rest_away = game_data.get('rest_days_away', 1)
    
    if rest_home >= 2:
        home_expected_runs *= 1.05
    if rest_away >= 2:
        away_expected_runs *= 1.05
    
    # Calculate win probability using Poisson distribution
    home_win_prob = 0.0
    for home_runs in range(0, 15):
        for away_runs in range(0, 15):
            home_prob = stats.poisson.pmf(home_runs, home_expected_runs)
            away_prob = stats.poisson.pmf(away_runs, away_expected_runs)
            if home_runs > away_runs:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def _calculate_nba_probability(game_data: Dict[str, Any]) -> float:
    """NBA-specific probability calculation."""
    # Simplified model based on pace and efficiency
    pace_home = game_data.get('pace_home', 100)
    pace_away = game_data.get('pace_away', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    # Calculate expected points
    avg_pace = (pace_home + pace_away) / 2
    home_efficiency = efg_home / 0.52  # Relative to league average
    away_efficiency = efg_away / 0.52
    
    home_expected = LEAGUE_AVG_POINTS * home_efficiency * (avg_pace / 100)
    away_expected = LEAGUE_AVG_POINTS * away_efficiency * (avg_pace / 100)
    
    # Use normal distribution for basketball scoring
    home_std = home_expecte
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_nba_probability(game_data)
        elif sport == 'Soccer':
            return _calculate_soccer_probability(game_data)
        else:
            return 0.5  # Default neutral probability
    except Exception as e:
        print(f"Analytical calculation error for {sport}: {e}")
        return 0.5

def _calculate_mlb_probability(game_data: Dict[str, Any]) -> float:
    """MLB-specific Poisson-based probability calculation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    # Calculate expected runs (better pitcher = lower ERA = fewer runs allowed)
    home_expected_runs = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_expected_runs = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    # Adjust for rest days
    rest_home = game_data.get('rest_days_home', 1)
    rest_away = game_data.get('rest_days_away', 1)
    
    if rest_home >= 2:
        home_expected_runs *= 1.05
    if rest_away >= 2:
        away_expected_runs *= 1.05
    
    # Calculate win probability using Poisson distribution
    home_win_prob = 0.0
    for home_runs in range(0, 15):
        for away_runs in range(0, 15):
            home_prob = stats.poisson.pmf(home_runs, home_expected_runs)
            away_prob = stats.poisson.pmf(away_runs, away_expected_runs)
            if home_runs > away_runs:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def _calculate_nba_probability(game_data: Dict[str, Any]) -> float:
    """NBA-specific probability calculation."""
    # Simplified model based on pace and efficiency
    pace_home = game_data.get('pace_home', 100)
    pace_away = game_data.get('pace_away', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    # Calculate expected points
    avg_pace = (pace_home + pace_away) / 2
    home_efficiency = efg_home / 0.52  # Relative to league average
    away_efficiency = efg_away / 0.52
    
    home_expected = LEAGUE_AVG_POINTS * home_efficiency * (avg_pace / 100)
    away_expected = LEAGUE_AVG_POINTS * away_efficiency * (avg_pace / 100)
    
    # Use normal distribution for basketball scoring
    home_std = home_expected * 0.15  # ~15% standard deviation
    away_std = away_expected * 0.15
    
    # Monte Carlo approach for win probability
    home_wins = 0
    simulations = 1000
    for _ in range(simulations):
        home_score = np.random.normal(home_expected, home_std)
        away_score = np.random.normal(away_expected, away_std)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / simulations

def _calculate_soccer_probability(game_data: Dict[str, Any]) -> float:
    """Soccer-specific xG-based probability calculation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    # Use Poisson distribution for goal scoring
    home_win_prob = 0.0
    for home_goals in range(0, 8):
        for away_goals in range(0, 8):
            home_prob = stats.poisson.pmf(home_goals, xg_home)
            away_prob = stats.poisson.pmf(away_goals, xg_away)
            if home_goals > away_goals:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def run_monte_carlo_simulation(game_data: Dict[str, Any], sport: str, n_sims: int = MC_SIMULATIONS) -> float:
    """Run Monte Carlo simulation for game outcome."""
    try:
        if sport == 'MLB':
            return _monte_carlo_mlb(game_data, n_sims)
        elif sport == 'NBA':
            return _monte_carlo_nba(game_data, n_sims)
        elif sport == 'Soccer':
            return _monte_carlo_soccer(game_data, n_sims)
        else:
            return 0.5
    except Exception as e:
        print(f"Monte Carlo error for {sport}: {e}")
        return 0.5

def _monte_carlo_mlb(game_data: Dict[str, Any], n_sims: int) -> float:
    """MLB Monte Carlo simulation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    home_lambda = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_lambda = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    home_wins = 0
    for _ in range(n_sims):
        home_runs = np.random.poisson(home_lambda)
        away_runs = np.random.poisson(away_lambda)
        if home_runs > away_runs:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_nba(game_data: Dict[str, Any], n_sims: int) -> float:
    """NBA Monte Carlo simulation."""
    pace_home = game_data.get('pace_home', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    home_expected = LEAGUE_AVG_POINTS * (efg_home / 0.52) * (pace_home / 100)
    away_expected = LEAGUE_AVG_POINTS * (efg_away / 0.52) * (pace_home / 100)
    
    home_wins = 0
    for _ in range(n_sims):
        home_score = np.random.normal(home_expected, home_expected * 0.15)
        away_score = np.random
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_nba_probability(game_data)
        elif sport == 'Soccer':
            return _calculate_soccer_probability(game_data)
        else:
            return 0.5  # Default neutral probability
    except Exception as e:
        print(f"Analytical calculation error for {sport}: {e}")
        return 0.5

def _calculate_mlb_probability(game_data: Dict[str, Any]) -> float:
    """MLB-specific Poisson-based probability calculation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    # Calculate expected runs (better pitcher = lower ERA = fewer runs allowed)
    home_expected_runs = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_expected_runs = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    # Adjust for rest days
    rest_home = game_data.get('rest_days_home', 1)
    rest_away = game_data.get('rest_days_away', 1)
    
    if rest_home >= 2:
        home_expected_runs *= 1.05
    if rest_away >= 2:
        away_expected_runs *= 1.05
    
    # Calculate win probability using Poisson distribution
    home_win_prob = 0.0
    for home_runs in range(0, 15):
        for away_runs in range(0, 15):
            home_prob = stats.poisson.pmf(home_runs, home_expected_runs)
            away_prob = stats.poisson.pmf(away_runs, away_expected_runs)
            if home_runs > away_runs:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def _calculate_nba_probability(game_data: Dict[str, Any]) -> float:
    """NBA-specific probability calculation."""
    # Simplified model based on pace and efficiency
    pace_home = game_data.get('pace_home', 100)
    pace_away = game_data.get('pace_away', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    # Calculate expected points
    avg_pace = (pace_home + pace_away) / 2
    home_efficiency = efg_home / 0.52  # Relative to league average
    away_efficiency = efg_away / 0.52
    
    home_expected = LEAGUE_AVG_POINTS * home_efficiency * (avg_pace / 100)
    away_expected = LEAGUE_AVG_POINTS * away_efficiency * (avg_pace / 100)
    
    # Use normal distribution for basketball scoring
    home_std = home_expected * 0.15  # ~15% standard deviation
    away_std = away_expected * 0.15
    
    # Monte Carlo approach for win probability
    home_wins = 0
    simulations = 1000
    for _ in range(simulations):
        home_score = np.random.normal(home_expected, home_std)
        away_score = np.random.normal(away_expected, away_std)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / simulations

def _calculate_soccer_probability(game_data: Dict[str, Any]) -> float:
    """Soccer-specific xG-based probability calculation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    # Use Poisson distribution for goal scoring
    home_win_prob = 0.0
    for home_goals in range(0, 8):
        for away_goals in range(0, 8):
            home_prob = stats.poisson.pmf(home_goals, xg_home)
            away_prob = stats.poisson.pmf(away_goals, xg_away)
            if home_goals > away_goals:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def run_monte_carlo_simulation(game_data: Dict[str, Any], sport: str, n_sims: int = MC_SIMULATIONS) -> float:
    """Run Monte Carlo simulation for game outcome."""
    try:
        if sport == 'MLB':
            return _monte_carlo_mlb(game_data, n_sims)
        elif sport == 'NBA':
            return _monte_carlo_nba(game_data, n_sims)
        elif sport == 'Soccer':
            return _monte_carlo_soccer(game_data, n_sims)
        else:
            return 0.5
    except Exception as e:
        print(f"Monte Carlo error for {sport}: {e}")
        return 0.5

def _monte_carlo_mlb(game_data: Dict[str, Any], n_sims: int) -> float:
    """MLB Monte Carlo simulation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    home_lambda = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_lambda = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    home_wins = 0
    for _ in range(n_sims):
        home_runs = np.random.poisson(home_lambda)
        away_runs = np.random.poisson(away_lambda)
        if home_runs > away_runs:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_nba(game_data: Dict[str, Any], n_sims: int) -> float:
    """NBA Monte Carlo simulation."""
    pace_home = game_data.get('pace_home', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    home_expected = LEAGUE_AVG_POINTS * (efg_home / 0.52) * (pace_home / 100)
    away_expected = LEAGUE_AVG_POINTS * (efg_away / 0.52) * (pace_home / 100)
    
    home_wins = 0
    for _ in range(n_sims):
        home_score = np.random.normal(home_expected, home_expected * 0.15)
        away_score = np.random.normal(away_expected, away_expected * 0.15)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_soccer(game_data: Dict[str, Any], n_sims: int) -> float:
    """Soccer Monte Carlo simulation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    home_wins = 0
    for _ in range(n_sims):
        home_goals = np.random.poisson(xg_home)
        away_goals = np.random.poisson(xg_away)
        if home_goals > away_goals:
            home_wins += 1
    
    return home_wins / n_sims

def calculate_ensemble_probability(analytical_prob: float, mc_prob: float) -> float:
    """Blend analytical and Monte Carlo probabilities (50/50)."""
    return (analytical_prob + mc_prob) / 2

def calculate_ev_percentage(model_prob: float, odds: int) -> float:
    """Calculate Expected Value percentage."""
    try:
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Calculate implied probability
        implied_prob = 1 / decimal_odds
        
        # Calculate EV%
        ev_percentage = ((model_prob - implied_prob) / implied_prob) * 100
        return ev_percentage
    except Exception as e:
        print(f"EV calculation error: {e}")
        return -100

def calculate_confidence_score(game_data: Dict[str, Any], sport: str) -> int:
    """Calculate confidence score (1-10)."""
    confidence = 5  # Base score
    
    try:
        # Universal factors
        if game_data.get('rlm_flag', False):
            confidence += 2
        if game_data.get('steam_detected', False):
            confidence += 1
        if game_data.get('sharp_money', False):
            confidence += 1
        
        # Sport-specific factors
        if sport == 'MLB':
            era_home = game_data.get('era_home_starter', 4.0)
            era_away = game_data.get('era_away_starter', 4.0)
            era_diff = abs(era_home - era_away)
            if era_diff > 1.0:
                confidence += 1
            
            wind = game_data.get('weather_wind', 0)
            if wind > 15:
                confidence -= 1
        
        elif sport == 'NBA':
            injury_impact = game_data.get('injury_impact_total', 0)
            if injury_impact > 0.05:
                confidence += 1
        
        elif sport == 'Soccer':
            form_diff = game_data.get('form_difference', 0)
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_nba_probability(game_data)
        elif sport == 'Soccer':
            return _calculate_soccer_probability(game_data)
        else:
            return 0.5  # Default neutral probability
    except Exception as e:
        print(f"Analytical calculation error for {sport}: {e}")
        return 0.5

def _calculate_mlb_probability(game_data: Dict[str, Any]) -> float:
    """MLB-specific Poisson-based probability calculation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    # Calculate expected runs (better pitcher = lower ERA = fewer runs allowed)
    home_expected_runs = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_expected_runs = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    # Adjust for rest days
    rest_home = game_data.get('rest_days_home', 1)
    rest_away = game_data.get('rest_days_away', 1)
    
    if rest_home >= 2:
        home_expected_runs *= 1.05
    if rest_away >= 2:
        away_expected_runs *= 1.05
    
    # Calculate win probability using Poisson distribution
    home_win_prob = 0.0
    for home_runs in range(0, 15):
        for away_runs in range(0, 15):
            home_prob = stats.poisson.pmf(home_runs, home_expected_runs)
            away_prob = stats.poisson.pmf(away_runs, away_expected_runs)
            if home_runs > away_runs:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def _calculate_nba_probability(game_data: Dict[str, Any]) -> float:
    """NBA-specific probability calculation."""
    # Simplified model based on pace and efficiency
    pace_home = game_data.get('pace_home', 100)
    pace_away = game_data.get('pace_away', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    # Calculate expected points
    avg_pace = (pace_home + pace_away) / 2
    home_efficiency = efg_home / 0.52  # Relative to league average
    away_efficiency = efg_away / 0.52
    
    home_expected = LEAGUE_AVG_POINTS * home_efficiency * (avg_pace / 100)
    away_expected = LEAGUE_AVG_POINTS * away_efficiency * (avg_pace / 100)
    
    # Use normal distribution for basketball scoring
    home_std = home_expected * 0.15  # ~15% standard deviation
    away_std = away_expected * 0.15
    
    # Monte Carlo approach for win probability
    home_wins = 0
    simulations = 1000
    for _ in range(simulations):
        home_score = np.random.normal(home_expected, home_std)
        away_score = np.random.normal(away_expected, away_std)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / simulations

def _calculate_soccer_probability(game_data: Dict[str, Any]) -> float:
    """Soccer-specific xG-based probability calculation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    # Use Poisson distribution for goal scoring
    home_win_prob = 0.0
    for home_goals in range(0, 8):
        for away_goals in range(0, 8):
            home_prob = stats.poisson.pmf(home_goals, xg_home)
            away_prob = stats.poisson.pmf(away_goals, xg_away)
            if home_goals > away_goals:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def run_monte_carlo_simulation(game_data: Dict[str, Any], sport: str, n_sims: int = MC_SIMULATIONS) -> float:
    """Run Monte Carlo simulation for game outcome."""
    try:
        if sport == 'MLB':
            return _monte_carlo_mlb(game_data, n_sims)
        elif sport == 'NBA':
            return _monte_carlo_nba(game_data, n_sims)
        elif sport == 'Soccer':
            return _monte_carlo_soccer(game_data, n_sims)
        else:
            return 0.5
    except Exception as e:
        print(f"Monte Carlo error for {sport}: {e}")
        return 0.5

def _monte_carlo_mlb(game_data: Dict[str, Any], n_sims: int) -> float:
    """MLB Monte Carlo simulation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    home_lambda = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_lambda = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    home_wins = 0
    for _ in range(n_sims):
        home_runs = np.random.poisson(home_lambda)
        away_runs = np.random.poisson(away_lambda)
        if home_runs > away_runs:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_nba(game_data: Dict[str, Any], n_sims: int) -> float:
    """NBA Monte Carlo simulation."""
    pace_home = game_data.get('pace_home', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    home_expected = LEAGUE_AVG_POINTS * (efg_home / 0.52) * (pace_home / 100)
    away_expected = LEAGUE_AVG_POINTS * (efg_away / 0.52) * (pace_home / 100)
    
    home_wins = 0
    for _ in range(n_sims):
        home_score = np.random.normal(home_expected, home_expected * 0.15)
        away_score = np.random.normal(away_expected, away_expected * 0.15)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_soccer(game_data: Dict[str, Any], n_sims: int) -> float:
    """Soccer Monte Carlo simulation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    home_wins = 0
    for _ in range(n_sims):
        home_goals = np.random.poisson(xg_home)
        away_goals = np.random.poisson(xg_away)
        if home_goals > away_goals:
            home_wins += 1
    
    return home_wins / n_sims

def calculate_ensemble_probability(analytical_prob: float, mc_prob: float) -> float:
    """Blend analytical and Monte Carlo probabilities (50/50)."""
    return (analytical_prob + mc_prob) / 2

def calculate_ev_percentage(model_prob: float, odds: int) -> float:
    """Calculate Expected Value percentage."""
    try:
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Calculate implied probability
        implied_prob = 1 / decimal_odds
        
        # Calculate EV%
        ev_percentage = ((model_prob - implied_prob) / implied_prob) * 100
        return ev_percentage
    except Exception as e:
        print(f"EV calculation error: {e}")
        return -100

def calculate_confidence_score(game_data: Dict[str, Any], sport: str) -> int:
    """Calculate confidence score (1-10)."""
    confidence = 5  # Base score
    
    try:
        # Universal factors
        if game_data.get('rlm_flag', False):
            confidence += 2
        if game_data.get('steam_detected', False):
            confidence += 1
        if game_data.get('sharp_money', False):
            confidence += 1
        
        # Sport-specific factors
        if sport == 'MLB':
            era_home = game_data.get('era_home_starter', 4.0)
            era_away = game_data.get('era_away_starter', 4.0)
            era_diff = abs(era_home - era_away)
            if era_diff > 1.0:
                confidence += 1
            
            wind = game_data.get('weather_wind', 0)
            if wind > 15:
                confidence -= 1
        
        elif sport == 'NBA':
            injury_impact = game_data.get('injury_impact_total', 0)
            if injury_impact > 0.05:
                confidence += 1
        
        elif sport == 'Soccer':
            form_diff = game_data.get('form_difference', 0)
            if abs(form_diff) > 2:
                confidence += 1
        
        # Public betting factor
        public_pct = game_data.get('public_pct_home', 50)
        if public_pct > 75 or public_pct < 25:
            confidence += 1
        
        return max(1, min(10, confidence))
    except Exception as e:
        print(f"Confidence calculation error: {e}")
        return 5

def detect_sharp_indicators(game_data: Dict[str, Any]) -> List[str]:
    """Detect sharp betting indicators."""
    flags = []
    
    # Reverse Line Movement
    if game_data.get('public_pct_home', 50) > 65 and game_data.get('line_movement', 0) < 0:
        flags.append('RLM')
        game_data['rlm_flag'] = True
    
    # Steam detection (rapid line movement)
    line_velocity = game_data.get('line_velocity', 0)
    if abs(line_velocity) > 5:  # 5+ point move in short time
        flags.append('Steam')
        game_data['steam_detected'] = True
    
    # Sharp money indicators
    if game_data.get('bet_count_ratio', 1) < 0.3:  # Few bets but big money
        flags.append('Sharp-Money')
        game_data['sharp_money'] = True
    
    return flags

def calculate_clv(current_odds: float, opening_odds: float) -> float:
    """Calculate Closing Line Value."""
    try:
        if opening_odds == 0:
            return 0.0
        
        # Convert to decimal odds
        def to_decimal(american_odds):
            if american_odds > 0:
                return (american_odds / 100) + 1
            else:
                return (100 / abs(american_odds)) + 1
        
        current_decimal = to_decimal(current_odds)
        opening_decimal = to_decimal(opening_odds)
        
        # CLV as percentage improvement
        clv = ((current_decimal - opening_decimal) / opening_decimal) * 100
        return round(clv, 2)
    except:
        return 0.0

def calculate_kelly_stake(ev_percentage: float, odds: int, bankroll: float, confidence: int) -> float:
    """Calculate stake using Kelly criterion with confidence adjustments."""
    try:
        if ev_percentage <= 0:
            return 0
        
        # Convert to decimal odds
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Kelly calculation
        edge = ev_percentage / 100
        kelly_fraction = edge / (decimal_odds - 1)
        
        # Apply conservative sizing (quarter Kelly)
        base_stake = bankroll * kelly_fraction * 0.25
        
        # Confidence adjustment
        confidence
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_nba_probability(game_data)
        elif sport == 'Soccer':
            return _calculate_soccer_probability(game_data)
        else:
            return 0.5  # Default neutral probability
    except Exception as e:
        print(f"Analytical calculation error for {sport}: {e}")
        return 0.5

def _calculate_mlb_probability(game_data: Dict[str, Any]) -> float:
    """MLB-specific Poisson-based probability calculation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    # Calculate expected runs (better pitcher = lower ERA = fewer runs allowed)
    home_expected_runs = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_expected_runs = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    # Adjust for rest days
    rest_home = game_data.get('rest_days_home', 1)
    rest_away = game_data.get('rest_days_away', 1)
    
    if rest_home >= 2:
        home_expected_runs *= 1.05
    if rest_away >= 2:
        away_expected_runs *= 1.05
    
    # Calculate win probability using Poisson distribution
    home_win_prob = 0.0
    for home_runs in range(0, 15):
        for away_runs in range(0, 15):
            home_prob = stats.poisson.pmf(home_runs, home_expected_runs)
            away_prob = stats.poisson.pmf(away_runs, away_expected_runs)
            if home_runs > away_runs:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def _calculate_nba_probability(game_data: Dict[str, Any]) -> float:
    """NBA-specific probability calculation."""
    # Simplified model based on pace and efficiency
    pace_home = game_data.get('pace_home', 100)
    pace_away = game_data.get('pace_away', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    # Calculate expected points
    avg_pace = (pace_home + pace_away) / 2
    home_efficiency = efg_home / 0.52  # Relative to league average
    away_efficiency = efg_away / 0.52
    
    home_expected = LEAGUE_AVG_POINTS * home_efficiency * (avg_pace / 100)
    away_expected = LEAGUE_AVG_POINTS * away_efficiency * (avg_pace / 100)
    
    # Use normal distribution for basketball scoring
    home_std = home_expected * 0.15  # ~15% standard deviation
    away_std = away_expected * 0.15
    
    # Monte Carlo approach for win probability
    home_wins = 0
    simulations = 1000
    for _ in range(simulations):
        home_score = np.random.normal(home_expected, home_std)
        away_score = np.random.normal(away_expected, away_std)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / simulations

def _calculate_soccer_probability(game_data: Dict[str, Any]) -> float:
    """Soccer-specific xG-based probability calculation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    # Use Poisson distribution for goal scoring
    home_win_prob = 0.0
    for home_goals in range(0, 8):
        for away_goals in range(0, 8):
            home_prob = stats.poisson.pmf(home_goals, xg_home)
            away_prob = stats.poisson.pmf(away_goals, xg_away)
            if home_goals > away_goals:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def run_monte_carlo_simulation(game_data: Dict[str, Any], sport: str, n_sims: int = MC_SIMULATIONS) -> float:
    """Run Monte Carlo simulation for game outcome."""
    try:
        if sport == 'MLB':
            return _monte_carlo_mlb(game_data, n_sims)
        elif sport == 'NBA':
            return _monte_carlo_nba(game_data, n_sims)
        elif sport == 'Soccer':
            return _monte_carlo_soccer(game_data, n_sims)
        else:
            return 0.5
    except Exception as e:
        print(f"Monte Carlo error for {sport}: {e}")
        return 0.5

def _monte_carlo_mlb(game_data: Dict[str, Any], n_sims: int) -> float:
    """MLB Monte Carlo simulation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    home_lambda = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_lambda = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    home_wins = 0
    for _ in range(n_sims):
        home_runs = np.random.poisson(home_lambda)
        away_runs = np.random.poisson(away_lambda)
        if home_runs > away_runs:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_nba(game_data: Dict[str, Any], n_sims: int) -> float:
    """NBA Monte Carlo simulation."""
    pace_home = game_data.get('pace_home', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    home_expected = LEAGUE_AVG_POINTS * (efg_home / 0.52) * (pace_home / 100)
    away_expected = LEAGUE_AVG_POINTS * (efg_away / 0.52) * (pace_home / 100)
    
    home_wins = 0
    for _ in range(n_sims):
        home_score = np.random.normal(home_expected, home_expected * 0.15)
        away_score = np.random.normal(away_expected, away_expected * 0.15)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_soccer(game_data: Dict[str, Any], n_sims: int) -> float:
    """Soccer Monte Carlo simulation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    home_wins = 0
    for _ in range(n_sims):
        home_goals = np.random.poisson(xg_home)
        away_goals = np.random.poisson(xg_away)
        if home_goals > away_goals:
            home_wins += 1
    
    return home_wins / n_sims

def calculate_ensemble_probability(analytical_prob: float, mc_prob: float) -> float:
    """Blend analytical and Monte Carlo probabilities (50/50)."""
    return (analytical_prob + mc_prob) / 2

def calculate_ev_percentage(model_prob: float, odds: int) -> float:
    """Calculate Expected Value percentage."""
    try:
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Calculate implied probability
        implied_prob = 1 / decimal_odds
        
        # Calculate EV%
        ev_percentage = ((model_prob - implied_prob) / implied_prob) * 100
        return ev_percentage
    except Exception as e:
        print(f"EV calculation error: {e}")
        return -100

def calculate_confidence_score(game_data: Dict[str, Any], sport: str) -> int:
    """Calculate confidence score (1-10)."""
    confidence = 5  # Base score
    
    try:
        # Universal factors
        if game_data.get('rlm_flag', False):
            confidence += 2
        if game_data.get('steam_detected', False):
            confidence += 1
        if game_data.get('sharp_money', False):
            confidence += 1
        
        # Sport-specific factors
        if sport == 'MLB':
            era_home = game_data.get('era_home_starter', 4.0)
            era_away = game_data.get('era_away_starter', 4.0)
            era_diff = abs(era_home - era_away)
            if era_diff > 1.0:
                confidence += 1
            
            wind = game_data.get('weather_wind', 0)
            if wind > 15:
                confidence -= 1
        
        elif sport == 'NBA':
            injury_impact = game_data.get('injury_impact_total', 0)
            if injury_impact > 0.05:
                confidence += 1
        
        elif sport == 'Soccer':
            form_diff = game_data.get('form_difference', 0)
            if abs(form_diff) > 2:
                confidence += 1
        
        # Public betting factor
        public_pct = game_data.get('public_pct_home', 50)
        if public_pct > 75 or public_pct < 25:
            confidence += 1
        
        return max(1, min(10, confidence))
    except Exception as e:
        print(f"Confidence calculation error: {e}")
        return 5

def detect_sharp_indicators(game_data: Dict[str, Any]) -> List[str]:
    """Detect sharp betting indicators."""
    flags = []
    
    # Reverse Line Movement
    if game_data.get('public_pct_home', 50) > 65 and game_data.get('line_movement', 0) < 0:
        flags.append('RLM')
        game_data['rlm_flag'] = True
    
    # Steam detection (rapid line movement)
    line_velocity = game_data.get('line_velocity', 0)
    if abs(line_velocity) > 5:  # 5+ point move in short time
        flags.append('Steam')
        game_data['steam_detected'] = True
    
    # Sharp money indicators
    if game_data.get('bet_count_ratio', 1) < 0.3:  # Few bets but big money
        flags.append('Sharp-Money')
        game_data['sharp_money'] = True
    
    return flags

def calculate_clv(current_odds: float, opening_odds: float) -> float:
    """Calculate Closing Line Value."""
    try:
        if opening_odds == 0:
            return 0.0
        
        # Convert to decimal odds
        def to_decimal(american_odds):
            if american_odds > 0:
                return (american_odds / 100) + 1
            else:
                return (100 / abs(american_odds)) + 1
        
        current_decimal = to_decimal(current_odds)
        opening_decimal = to_decimal(opening_odds)
        
        # CLV as percentage improvement
        clv = ((current_decimal - opening_decimal) / opening_decimal) * 100
        return round(clv, 2)
    except:
        return 0.0

def calculate_kelly_stake(ev_percentage: float, odds: int, bankroll: float, confidence: int) -> float:
    """Calculate stake using Kelly criterion with confidence adjustments."""
    try:
        if ev_percentage <= 0:
            return 0
        
        # Convert to decimal odds
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Kelly calculation
        edge = ev_percentage / 100
        kelly_fraction = edge / (decimal_odds - 1)
        
        # Apply conservative sizing (quarter Kelly)
        base_stake = bankroll * kelly_fraction * 0.25
        
        # Confidence adjustment
        confidence_multiplier = confidence / 10.0
        stake = base_stake * confidence_multiplier
        
        # Double stake if confidence >= 9 (as specified)
        if confidence >= 9:
            stake *= 2
        
        # Safety caps
        max_stake = bankroll * 0.05  # 5% max per bet
        return min(stake, max_stake)
    except Exception as e:
        print(f"Stake calculation error: {e}")
        return 0
📁 main.py - Section 4: Candidate Generation and Scoring
# ---------------------------------------------------------------------------
# Candidate generation and scoring
# ---------------------------------------------------------------------------

def build_candidates(sport: str, odds_data: List[Dict[str, Any]], advanced_stats: Dict[str, Any]) -> List[Candidate]:
    """Generate betting candidates from odds and stats."""
    candidates = []
    
    for game in odds_data:
        if not game.get('bookmakers'):
            continue
            
        # Extract game info
        home_team = game.get('home_team', 'Unknown')
        away_team = game.get('away_team', 'Unknown')
        
        # Combine game data
        game_data = {
            'home_team': home_team,
            'away_team': away_team,
            **advanced_stats.get('team_stats', {}),
            **advanced_stats.get('game_factors', {}),
            **advanced_stats.get('match_factors', {}),
            **advanced_stats.get('pitcher_stats', {})
        }
        
        # Process each bookmaker's markets
        for bookmaker in game.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                market_type = market.get('key', '')
                
                for outcome in market.get('outcomes', []):
                    pick_name = outcome.get('name', '')
                    odds_value = outcome.get('price', 0)
                    
                    if odds_value and abs(odds_value) >= 100:  # Valid American odds
                        pick_description = f"{pick_name} ({market_type})"
                        if market_type == 'h2h':
                            pick_description = f"{pick_name} Moneyline"
                        
                        candidate = Candidate(
                            sport=sport,
                            pick=pick_description,
                            odds=odds_value,
                            game_data=game_data.copy()
                        )
                        candidates.append(candidate)
    
    return candidates

def score_candidate(candidate: Candidate) -> Candidate:
    """Score a betting candidate with sophisticated models."""
    try:
        # Calculate probabilities
        analytical_prob = calculate_analytical_probability(candidate.game_data, candidate.sport)
        mc_prob = run_monte_carlo_simulation(candidate.game_data, candidate.sport, 1000)  # Reduced for speed
        model_prob = calculate_ensemble_probability(analytical_prob, mc_prob)
        
        # Calculate metrics
        ev_percentage = calculate_ev_percentage(model_prob, candidate.odds)
        confidence = calculate_confidence_score(candidate.game_data, candidate.sport)
        
        # Detect sharp indicators
        sharp_flags = detect_sharp_indicators(candidate.game_data)
        
        # Calculate CLV if opening odds available
        opening_odds = candidate.game_data.get('opening_odds', candidate.odds)
        clv = calculate_clv(candidate.odds, opening_odds)
        
        # Update candidate
        candidate.ev = round(ev_percentage, 2)
        candidate.confidence = confidence
        candidate.model_prob = roun
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_nba_probability(game_data)
        elif sport == 'Soccer':
            return _calculate_soccer_probability(game_data)
        else:
            return 0.5  # Default neutral probability
    except Exception as e:
        print(f"Analytical calculation error for {sport}: {e}")
        return 0.5

def _calculate_mlb_probability(game_data: Dict[str, Any]) -> float:
    """MLB-specific Poisson-based probability calculation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    # Calculate expected runs (better pitcher = lower ERA = fewer runs allowed)
    home_expected_runs = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_expected_runs = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    # Adjust for rest days
    rest_home = game_data.get('rest_days_home', 1)
    rest_away = game_data.get('rest_days_away', 1)
    
    if rest_home >= 2:
        home_expected_runs *= 1.05
    if rest_away >= 2:
        away_expected_runs *= 1.05
    
    # Calculate win probability using Poisson distribution
    home_win_prob = 0.0
    for home_runs in range(0, 15):
        for away_runs in range(0, 15):
            home_prob = stats.poisson.pmf(home_runs, home_expected_runs)
            away_prob = stats.poisson.pmf(away_runs, away_expected_runs)
            if home_runs > away_runs:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def _calculate_nba_probability(game_data: Dict[str, Any]) -> float:
    """NBA-specific probability calculation."""
    # Simplified model based on pace and efficiency
    pace_home = game_data.get('pace_home', 100)
    pace_away = game_data.get('pace_away', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    # Calculate expected points
    avg_pace = (pace_home + pace_away) / 2
    home_efficiency = efg_home / 0.52  # Relative to league average
    away_efficiency = efg_away / 0.52
    
    home_expected = LEAGUE_AVG_POINTS * home_efficiency * (avg_pace / 100)
    away_expected = LEAGUE_AVG_POINTS * away_efficiency * (avg_pace / 100)
    
    # Use normal distribution for basketball scoring
    home_std = home_expected * 0.15  # ~15% standard deviation
    away_std = away_expected * 0.15
    
    # Monte Carlo approach for win probability
    home_wins = 0
    simulations = 1000
    for _ in range(simulations):
        home_score = np.random.normal(home_expected, home_std)
        away_score = np.random.normal(away_expected, away_std)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / simulations

def _calculate_soccer_probability(game_data: Dict[str, Any]) -> float:
    """Soccer-specific xG-based probability calculation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    # Use Poisson distribution for goal scoring
    home_win_prob = 0.0
    for home_goals in range(0, 8):
        for away_goals in range(0, 8):
            home_prob = stats.poisson.pmf(home_goals, xg_home)
            away_prob = stats.poisson.pmf(away_goals, xg_away)
            if home_goals > away_goals:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def run_monte_carlo_simulation(game_data: Dict[str, Any], sport: str, n_sims: int = MC_SIMULATIONS) -> float:
    """Run Monte Carlo simulation for game outcome."""
    try:
        if sport == 'MLB':
            return _monte_carlo_mlb(game_data, n_sims)
        elif sport == 'NBA':
            return _monte_carlo_nba(game_data, n_sims)
        elif sport == 'Soccer':
            return _monte_carlo_soccer(game_data, n_sims)
        else:
            return 0.5
    except Exception as e:
        print(f"Monte Carlo error for {sport}: {e}")
        return 0.5

def _monte_carlo_mlb(game_data: Dict[str, Any], n_sims: int) -> float:
    """MLB Monte Carlo simulation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    home_lambda = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_lambda = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    home_wins = 0
    for _ in range(n_sims):
        home_runs = np.random.poisson(home_lambda)
        away_runs = np.random.poisson(away_lambda)
        if home_runs > away_runs:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_nba(game_data: Dict[str, Any], n_sims: int) -> float:
    """NBA Monte Carlo simulation."""
    pace_home = game_data.get('pace_home', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    home_expected = LEAGUE_AVG_POINTS * (efg_home / 0.52) * (pace_home / 100)
    away_expected = LEAGUE_AVG_POINTS * (efg_away / 0.52) * (pace_home / 100)
    
    home_wins = 0
    for _ in range(n_sims):
        home_score = np.random.normal(home_expected, home_expected * 0.15)
        away_score = np.random.normal(away_expected, away_expected * 0.15)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_soccer(game_data: Dict[str, Any], n_sims: int) -> float:
    """Soccer Monte Carlo simulation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    home_wins = 0
    for _ in range(n_sims):
        home_goals = np.random.poisson(xg_home)
        away_goals = np.random.poisson(xg_away)
        if home_goals > away_goals:
            home_wins += 1
    
    return home_wins / n_sims

def calculate_ensemble_probability(analytical_prob: float, mc_prob: float) -> float:
    """Blend analytical and Monte Carlo probabilities (50/50)."""
    return (analytical_prob + mc_prob) / 2

def calculate_ev_percentage(model_prob: float, odds: int) -> float:
    """Calculate Expected Value percentage."""
    try:
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Calculate implied probability
        implied_prob = 1 / decimal_odds
        
        # Calculate EV%
        ev_percentage = ((model_prob - implied_prob) / implied_prob) * 100
        return ev_percentage
    except Exception as e:
        print(f"EV calculation error: {e}")
        return -100

def calculate_confidence_score(game_data: Dict[str, Any], sport: str) -> int:
    """Calculate confidence score (1-10)."""
    confidence = 5  # Base score
    
    try:
        # Universal factors
        if game_data.get('rlm_flag', False):
            confidence += 2
        if game_data.get('steam_detected', False):
            confidence += 1
        if game_data.get('sharp_money', False):
            confidence += 1
        
        # Sport-specific factors
        if sport == 'MLB':
            era_home = game_data.get('era_home_starter', 4.0)
            era_away = game_data.get('era_away_starter', 4.0)
            era_diff = abs(era_home - era_away)
            if era_diff > 1.0:
                confidence += 1
            
            wind = game_data.get('weather_wind', 0)
            if wind > 15:
                confidence -= 1
        
        elif sport == 'NBA':
            injury_impact = game_data.get('injury_impact_total', 0)
            if injury_impact > 0.05:
                confidence += 1
        
        elif sport == 'Soccer':
            form_diff = game_data.get('form_difference', 0)
            if abs(form_diff) > 2:
                confidence += 1
        
        # Public betting factor
        public_pct = game_data.get('public_pct_home', 50)
        if public_pct > 75 or public_pct < 25:
            confidence += 1
        
        return max(1, min(10, confidence))
    except Exception as e:
        print(f"Confidence calculation error: {e}")
        return 5

def detect_sharp_indicators(game_data: Dict[str, Any]) -> List[str]:
    """Detect sharp betting indicators."""
    flags = []
    
    # Reverse Line Movement
    if game_data.get('public_pct_home', 50) > 65 and game_data.get('line_movement', 0) < 0:
        flags.append('RLM')
        game_data['rlm_flag'] = True
    
    # Steam detection (rapid line movement)
    line_velocity = game_data.get('line_velocity', 0)
    if abs(line_velocity) > 5:  # 5+ point move in short time
        flags.append('Steam')
        game_data['steam_detected'] = True
    
    # Sharp money indicators
    if game_data.get('bet_count_ratio', 1) < 0.3:  # Few bets but big money
        flags.append('Sharp-Money')
        game_data['sharp_money'] = True
    
    return flags

def calculate_clv(current_odds: float, opening_odds: float) -> float:
    """Calculate Closing Line Value."""
    try:
        if opening_odds == 0:
            return 0.0
        
        # Convert to decimal odds
        def to_decimal(american_odds):
            if american_odds > 0:
                return (american_odds / 100) + 1
            else:
                return (100 / abs(american_odds)) + 1
        
        current_decimal = to_decimal(current_odds)
        opening_decimal = to_decimal(opening_odds)
        
        # CLV as percentage improvement
        clv = ((current_decimal - opening_decimal) / opening_decimal) * 100
        return round(clv, 2)
    except:
        return 0.0

def calculate_kelly_stake(ev_percentage: float, odds: int, bankroll: float, confidence: int) -> float:
    """Calculate stake using Kelly criterion with confidence adjustments."""
    try:
        if ev_percentage <= 0:
            return 0
        
        # Convert to decimal odds
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Kelly calculation
        edge = ev_percentage / 100
        kelly_fraction = edge / (decimal_odds - 1)
        
        # Apply conservative sizing (quarter Kelly)
        base_stake = bankroll * kelly_fraction * 0.25
        
        # Confidence adjustment
        confidence_multiplier = confidence / 10.0
        stake = base_stake * confidence_multiplier
        
        # Double stake if confidence >= 9 (as specified)
        if confidence >= 9:
            stake *= 2
        
        # Safety caps
        max_stake = bankroll * 0.05  # 5% max per bet
        return min(stake, max_stake)
    except Exception as e:
        print(f"Stake calculation error: {e}")
        return 0
📁 main.py - Section 4: Candidate Generation and Scoring
# ---------------------------------------------------------------------------
# Candidate generation and scoring
# ---------------------------------------------------------------------------

def build_candidates(sport: str, odds_data: List[Dict[str, Any]], advanced_stats: Dict[str, Any]) -> List[Candidate]:
    """Generate betting candidates from odds and stats."""
    candidates = []
    
    for game in odds_data:
        if not game.get('bookmakers'):
            continue
            
        # Extract game info
        home_team = game.get('home_team', 'Unknown')
        away_team = game.get('away_team', 'Unknown')
        
        # Combine game data
        game_data = {
            'home_team': home_team,
            'away_team': away_team,
            **advanced_stats.get('team_stats', {}),
            **advanced_stats.get('game_factors', {}),
            **advanced_stats.get('match_factors', {}),
            **advanced_stats.get('pitcher_stats', {})
        }
        
        # Process each bookmaker's markets
        for bookmaker in game.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                market_type = market.get('key', '')
                
                for outcome in market.get('outcomes', []):
                    pick_name = outcome.get('name', '')
                    odds_value = outcome.get('price', 0)
                    
                    if odds_value and abs(odds_value) >= 100:  # Valid American odds
                        pick_description = f"{pick_name} ({market_type})"
                        if market_type == 'h2h':
                            pick_description = f"{pick_name} Moneyline"
                        
                        candidate = Candidate(
                            sport=sport,
                            pick=pick_description,
                            odds=odds_value,
                            game_data=game_data.copy()
                        )
                        candidates.append(candidate)
    
    return candidates

def score_candidate(candidate: Candidate) -> Candidate:
    """Score a betting candidate with sophisticated models."""
    try:
        # Calculate probabilities
        analytical_prob = calculate_analytical_probability(candidate.game_data, candidate.sport)
        mc_prob = run_monte_carlo_simulation(candidate.game_data, candidate.sport, 1000)  # Reduced for speed
        model_prob = calculate_ensemble_probability(analytical_prob, mc_prob)
        
        # Calculate metrics
        ev_percentage = calculate_ev_percentage(model_prob, candidate.odds)
        confidence = calculate_confidence_score(candidate.game_data, candidate.sport)
        
        # Detect sharp indicators
        sharp_flags = detect_sharp_indicators(candidate.game_data)
        
        # Calculate CLV if opening odds available
        opening_odds = candidate.game_data.get('opening_odds', candidate.odds)
        clv = calculate_clv(candidate.odds, opening_odds)
        
        # Update candidate
        candidate.ev = round(ev_percentage, 2)
        candidate.confidence = confidence
        candidate.model_prob = round(model_prob, 3)
        candidate.implied_prob = round(1 / ((abs(candidate.odds) / 100) + 1), 3)
        candidate.flags = sharp_flags
        candidate.clv_delta = clv
        
        return candidate
    except Exception as e:
        print(f"Scoring error for {candidate.pick}: {e}")
        return candidate

def filter_qualified_picks(candidates: List[Candidate]) -> List[Candidate]:
    """Filter to only qualified picks meeting EV and confidence thresholds."""
    qualified = []
    for candidate in candidates:
        if (candidate.ev >= MIN_EV_THRESHOLD and 
            candidate.confidence >= MIN_CONFIDENCE_THRESHOLD):
            qualified.append(candidate)
    return qualified
📁 main.py - Section 5: Bankroll Management and Staking
# ---------------------------------------------------------------------------
# Bankroll management and staking
# ---------------------------------------------------------------------------

def apply_staking_rules(qualified_picks: List[Candidate], bankroll: float) -> List[Pick]:
    """Apply bankroll management and calculate stakes."""
    picks = []
    daily_risk = 0.0
    max_daily_risk = bankroll * 0.15  # 15% daily cap
    max_sport_risk = bankroll * 0.40  # 40% per sport cap
    sport_risks = {}
    
    for candidate in qualified_picks:
        # Calculate stake
        stake = calculate_kelly_stake(candidate.ev, candidate.odds, bankroll, candidate.confidence)
        
        # Check sport exposure
        sport_risk = sport_risks.get(candidate.sport, 0.0)
        if sport_risk + stake > max_sport_risk:
            continue  # Skip if exceeds sport limit
        
        # Check daily exposure
        if daily_risk + stake > max_daily_risk:
            continue  # Skip if exceeds daily limit
        
        # Add to picks
        pick = Pick(**candidate.__dict__, stake=round(stake, 2))
        picks.append(pick)
        
        # Update risk tracking
        daily_risk += stake
        sport_risks[candidate.sport] = sport_risk + stake
    
    return picks
📁 main.py - Section 6: Main Workflow Orchestration
# ---------------------------------------------------------------------------
# Main workflow orchestration
# ---------------------------------------------------------------------------

def run_betting_scan(mode: str, bankroll: float =
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_nba_probability(game_data)
        elif sport == 'Soccer':
            return _calculate_soccer_probability(game_data)
        else:
            return 0.5  # Default neutral probability
    except Exception as e:
        print(f"Analytical calculation error for {sport}: {e}")
        return 0.5

def _calculate_mlb_probability(game_data: Dict[str, Any]) -> float:
    """MLB-specific Poisson-based probability calculation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    # Calculate expected runs (better pitcher = lower ERA = fewer runs allowed)
    home_expected_runs = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_expected_runs = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    # Adjust for rest days
    rest_home = game_data.get('rest_days_home', 1)
    rest_away = game_data.get('rest_days_away', 1)
    
    if rest_home >= 2:
        home_expected_runs *= 1.05
    if rest_away >= 2:
        away_expected_runs *= 1.05
    
    # Calculate win probability using Poisson distribution
    home_win_prob = 0.0
    for home_runs in range(0, 15):
        for away_runs in range(0, 15):
            home_prob = stats.poisson.pmf(home_runs, home_expected_runs)
            away_prob = stats.poisson.pmf(away_runs, away_expected_runs)
            if home_runs > away_runs:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def _calculate_nba_probability(game_data: Dict[str, Any]) -> float:
    """NBA-specific probability calculation."""
    # Simplified model based on pace and efficiency
    pace_home = game_data.get('pace_home', 100)
    pace_away = game_data.get('pace_away', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    # Calculate expected points
    avg_pace = (pace_home + pace_away) / 2
    home_efficiency = efg_home / 0.52  # Relative to league average
    away_efficiency = efg_away / 0.52
    
    home_expected = LEAGUE_AVG_POINTS * home_efficiency * (avg_pace / 100)
    away_expected = LEAGUE_AVG_POINTS * away_efficiency * (avg_pace / 100)
    
    # Use normal distribution for basketball scoring
    home_std = home_expected * 0.15  # ~15% standard deviation
    away_std = away_expected * 0.15
    
    # Monte Carlo approach for win probability
    home_wins = 0
    simulations = 1000
    for _ in range(simulations):
        home_score = np.random.normal(home_expected, home_std)
        away_score = np.random.normal(away_expected, away_std)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / simulations

def _calculate_soccer_probability(game_data: Dict[str, Any]) -> float:
    """Soccer-specific xG-based probability calculation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    # Use Poisson distribution for goal scoring
    home_win_prob = 0.0
    for home_goals in range(0, 8):
        for away_goals in range(0, 8):
            home_prob = stats.poisson.pmf(home_goals, xg_home)
            away_prob = stats.poisson.pmf(away_goals, xg_away)
            if home_goals > away_goals:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def run_monte_carlo_simulation(game_data: Dict[str, Any], sport: str, n_sims: int = MC_SIMULATIONS) -> float:
    """Run Monte Carlo simulation for game outcome."""
    try:
        if sport == 'MLB':
            return _monte_carlo_mlb(game_data, n_sims)
        elif sport == 'NBA':
            return _monte_carlo_nba(game_data, n_sims)
        elif sport == 'Soccer':
            return _monte_carlo_soccer(game_data, n_sims)
        else:
            return 0.5
    except Exception as e:
        print(f"Monte Carlo error for {sport}: {e}")
        return 0.5

def _monte_carlo_mlb(game_data: Dict[str, Any], n_sims: int) -> float:
    """MLB Monte Carlo simulation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    home_lambda = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_lambda = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    home_wins = 0
    for _ in range(n_sims):
        home_runs = np.random.poisson(home_lambda)
        away_runs = np.random.poisson(away_lambda)
        if home_runs > away_runs:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_nba(game_data: Dict[str, Any], n_sims: int) -> float:
    """NBA Monte Carlo simulation."""
    pace_home = game_data.get('pace_home', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    home_expected = LEAGUE_AVG_POINTS * (efg_home / 0.52) * (pace_home / 100)
    away_expected = LEAGUE_AVG_POINTS * (efg_away / 0.52) * (pace_home / 100)
    
    home_wins = 0
    for _ in range(n_sims):
        home_score = np.random.normal(home_expected, home_expected * 0.15)
        away_score = np.random.normal(away_expected, away_expected * 0.15)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_soccer(game_data: Dict[str, Any], n_sims: int) -> float:
    """Soccer Monte Carlo simulation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    home_wins = 0
    for _ in range(n_sims):
        home_goals = np.random.poisson(xg_home)
        away_goals = np.random.poisson(xg_away)
        if home_goals > away_goals:
            home_wins += 1
    
    return home_wins / n_sims

def calculate_ensemble_probability(analytical_prob: float, mc_prob: float) -> float:
    """Blend analytical and Monte Carlo probabilities (50/50)."""
    return (analytical_prob + mc_prob) / 2

def calculate_ev_percentage(model_prob: float, odds: int) -> float:
    """Calculate Expected Value percentage."""
    try:
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Calculate implied probability
        implied_prob = 1 / decimal_odds
        
        # Calculate EV%
        ev_percentage = ((model_prob - implied_prob) / implied_prob) * 100
        return ev_percentage
    except Exception as e:
        print(f"EV calculation error: {e}")
        return -100

def calculate_confidence_score(game_data: Dict[str, Any], sport: str) -> int:
    """Calculate confidence score (1-10)."""
    confidence = 5  # Base score
    
    try:
        # Universal factors
        if game_data.get('rlm_flag', False):
            confidence += 2
        if game_data.get('steam_detected', False):
            confidence += 1
        if game_data.get('sharp_money', False):
            confidence += 1
        
        # Sport-specific factors
        if sport == 'MLB':
            era_home = game_data.get('era_home_starter', 4.0)
            era_away = game_data.get('era_away_starter', 4.0)
            era_diff = abs(era_home - era_away)
            if era_diff > 1.0:
                confidence += 1
            
            wind = game_data.get('weather_wind', 0)
            if wind > 15:
                confidence -= 1
        
        elif sport == 'NBA':
            injury_impact = game_data.get('injury_impact_total', 0)
            if injury_impact > 0.05:
                confidence += 1
        
        elif sport == 'Soccer':
            form_diff = game_data.get('form_difference', 0)
            if abs(form_diff) > 2:
                confidence += 1
        
        # Public betting factor
        public_pct = game_data.get('public_pct_home', 50)
        if public_pct > 75 or public_pct < 25:
            confidence += 1
        
        return max(1, min(10, confidence))
    except Exception as e:
        print(f"Confidence calculation error: {e}")
        return 5

def detect_sharp_indicators(game_data: Dict[str, Any]) -> List[str]:
    """Detect sharp betting indicators."""
    flags = []
    
    # Reverse Line Movement
    if game_data.get('public_pct_home', 50) > 65 and game_data.get('line_movement', 0) < 0:
        flags.append('RLM')
        game_data['rlm_flag'] = True
    
    # Steam detection (rapid line movement)
    line_velocity = game_data.get('line_velocity', 0)
    if abs(line_velocity) > 5:  # 5+ point move in short time
        flags.append('Steam')
        game_data['steam_detected'] = True
    
    # Sharp money indicators
    if game_data.get('bet_count_ratio', 1) < 0.3:  # Few bets but big money
        flags.append('Sharp-Money')
        game_data['sharp_money'] = True
    
    return flags

def calculate_clv(current_odds: float, opening_odds: float) -> float:
    """Calculate Closing Line Value."""
    try:
        if opening_odds == 0:
            return 0.0
        
        # Convert to decimal odds
        def to_decimal(american_odds):
            if american_odds > 0:
                return (american_odds / 100) + 1
            else:
                return (100 / abs(american_odds)) + 1
        
        current_decimal = to_decimal(current_odds)
        opening_decimal = to_decimal(opening_odds)
        
        # CLV as percentage improvement
        clv = ((current_decimal - opening_decimal) / opening_decimal) * 100
        return round(clv, 2)
    except:
        return 0.0

def calculate_kelly_stake(ev_percentage: float, odds: int, bankroll: float, confidence: int) -> float:
    """Calculate stake using Kelly criterion with confidence adjustments."""
    try:
        if ev_percentage <= 0:
            return 0
        
        # Convert to decimal odds
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Kelly calculation
        edge = ev_percentage / 100
        kelly_fraction = edge / (decimal_odds - 1)
        
        # Apply conservative sizing (quarter Kelly)
        base_stake = bankroll * kelly_fraction * 0.25
        
        # Confidence adjustment
        confidence_multiplier = confidence / 10.0
        stake = base_stake * confidence_multiplier
        
        # Double stake if confidence >= 9 (as specified)
        if confidence >= 9:
            stake *= 2
        
        # Safety caps
        max_stake = bankroll * 0.05  # 5% max per bet
        return min(stake, max_stake)
    except Exception as e:
        print(f"Stake calculation error: {e}")
        return 0
📁 main.py - Section 4: Candidate Generation and Scoring
# ---------------------------------------------------------------------------
# Candidate generation and scoring
# ---------------------------------------------------------------------------

def build_candidates(sport: str, odds_data: List[Dict[str, Any]], advanced_stats: Dict[str, Any]) -> List[Candidate]:
    """Generate betting candidates from odds and stats."""
    candidates = []
    
    for game in odds_data:
        if not game.get('bookmakers'):
            continue
            
        # Extract game info
        home_team = game.get('home_team', 'Unknown')
        away_team = game.get('away_team', 'Unknown')
        
        # Combine game data
        game_data = {
            'home_team': home_team,
            'away_team': away_team,
            **advanced_stats.get('team_stats', {}),
            **advanced_stats.get('game_factors', {}),
            **advanced_stats.get('match_factors', {}),
            **advanced_stats.get('pitcher_stats', {})
        }
        
        # Process each bookmaker's markets
        for bookmaker in game.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                market_type = market.get('key', '')
                
                for outcome in market.get('outcomes', []):
                    pick_name = outcome.get('name', '')
                    odds_value = outcome.get('price', 0)
                    
                    if odds_value and abs(odds_value) >= 100:  # Valid American odds
                        pick_description = f"{pick_name} ({market_type})"
                        if market_type == 'h2h':
                            pick_description = f"{pick_name} Moneyline"
                        
                        candidate = Candidate(
                            sport=sport,
                            pick=pick_description,
                            odds=odds_value,
                            game_data=game_data.copy()
                        )
                        candidates.append(candidate)
    
    return candidates

def score_candidate(candidate: Candidate) -> Candidate:
    """Score a betting candidate with sophisticated models."""
    try:
        # Calculate probabilities
        analytical_prob = calculate_analytical_probability(candidate.game_data, candidate.sport)
        mc_prob = run_monte_carlo_simulation(candidate.game_data, candidate.sport, 1000)  # Reduced for speed
        model_prob = calculate_ensemble_probability(analytical_prob, mc_prob)
        
        # Calculate metrics
        ev_percentage = calculate_ev_percentage(model_prob, candidate.odds)
        confidence = calculate_confidence_score(candidate.game_data, candidate.sport)
        
        # Detect sharp indicators
        sharp_flags = detect_sharp_indicators(candidate.game_data)
        
        # Calculate CLV if opening odds available
        opening_odds = candidate.game_data.get('opening_odds', candidate.odds)
        clv = calculate_clv(candidate.odds, opening_odds)
        
        # Update candidate
        candidate.ev = round(ev_percentage, 2)
        candidate.confidence = confidence
        candidate.model_prob = round(model_prob, 3)
        candidate.implied_prob = round(1 / ((abs(candidate.odds) / 100) + 1), 3)
        candidate.flags = sharp_flags
        candidate.clv_delta = clv
        
        return candidate
    except Exception as e:
        print(f"Scoring error for {candidate.pick}: {e}")
        return candidate

def filter_qualified_picks(candidates: List[Candidate]) -> List[Candidate]:
    """Filter to only qualified picks meeting EV and confidence thresholds."""
    qualified = []
    for candidate in candidates:
        if (candidate.ev >= MIN_EV_THRESHOLD and 
            candidate.confidence >= MIN_CONFIDENCE_THRESHOLD):
            qualified.append(candidate)
    return qualified
📁 main.py - Section 5: Bankroll Management and Staking
# ---------------------------------------------------------------------------
# Bankroll management and staking
# ---------------------------------------------------------------------------

def apply_staking_rules(qualified_picks: List[Candidate], bankroll: float) -> List[Pick]:
    """Apply bankroll management and calculate stakes."""
    picks = []
    daily_risk = 0.0
    max_daily_risk = bankroll * 0.15  # 15% daily cap
    max_sport_risk = bankroll * 0.40  # 40% per sport cap
    sport_risks = {}
    
    for candidate in qualified_picks:
        # Calculate stake
        stake = calculate_kelly_stake(candidate.ev, candidate.odds, bankroll, candidate.confidence)
        
        # Check sport exposure
        sport_risk = sport_risks.get(candidate.sport, 0.0)
        if sport_risk + stake > max_sport_risk:
            continue  # Skip if exceeds sport limit
        
        # Check daily exposure
        if daily_risk + stake > max_daily_risk:
            continue  # Skip if exceeds daily limit
        
        # Add to picks
        pick = Pick(**candidate.__dict__, stake=round(stake, 2))
        picks.append(pick)
        
        # Update risk tracking
        daily_risk += stake
        sport_risks[candidate.sport] = sport_risk + stake
    
    return picks
📁 main.py - Section 6: Main Workflow Orchestration
# ---------------------------------------------------------------------------
# Main workflow orchestration
# ---------------------------------------------------------------------------

def run_betting_scan(mode: str, bankroll: float = None) -> ScanResult:
    """Main orchestration function for the betting scan."""
    print(f"🚀 Starting {mode} betting scan...")
    start_time = time.time()
    
    # Use provided bankroll or default
    if bankroll is None:
        bankroll = DEFAULT_BANKROLL
    
    print(f"💰 Current bankroll: ${bankroll:,.2f}")
    
    all_candidates = []
    all_qualified = []
    sports_scanned = []
    
    # Scan each sport
    sports_to_scan = ['MLB', 'NBA', 'Soccer']  # Add more as needed
    
    for sport in sports_to_scan:
        print(f"\n📡 Scanning {sport}...")
        sports_scanned.append(sport)
        
        try:
            # Fetch data
            odds_data = fetch_odds_data(sport)
            
            # Get sport-specific advanced stats
            if sport == 'MLB':
                advanced_stats = fetch_mlb_stats()
            elif sport == 'NBA':
                advanced_stats = fetch_nba_stats()
            elif sport == 'Soccer':
                advanced_stats = fetch_soccer_stats()
            else:
                advanced_stats = {}
            
            # Build and score candidates
            candidates = build_candidates(sport, odds_data, advanced_stats)
            scored_candidates = [score_candidate(c) for c in candidates]
            qualified = filter_qualified_picks(scored_candidates)
            
            all_candidates.extend(scored_candidates)
            all_qualified.extend(qualified)
            
            print(f"   {len(candidates)} candidates, {len(qualified)} qualified")
            
        except Exception as e:
            print(f"   Error scanning {sport}: {e}")
    
    # Apply staking rules
    official_picks = apply_staking_rules(all_qualified, bankroll)
    
    execution_time = time.time() - start_time
    
    # Calculate risk metrics
    total_risk = sum(pick.stake for pick in official_picks)
    risk_percentage = (total_risk / bankroll) * 100
    
    risk_metrics = {
        'total_risk': round(total_risk, 2),
        'risk_percentage': round(risk_percentage, 2),
        'max_daily_risk': round(bankroll * 0.15, 2),
        'remaining_capacity': round((bankroll * 0.15) - total_risk, 2)
    }
    
    # Model performance metrics
    if all_candidates:
        avg_ev = sum(c.ev for c in all_qualified) / len(all_qualified) if all_qualified else 0
        avg_confidence = sum(c.confidence for c in all_qualified) / len(all_qualified) if all_qualified else 0
        model_performance = {
            'avg_ev': round(avg_ev, 2),
            'avg_confidence': round(avg_confidence, 2),
            'qualification_rate': round((len(all_qualified) / len(all_candidates)) * 100, 2),
            'final_selection_rate': round((len(official_picks) / len(all_qualified)) * 100, 2) if all_qualified else 0
        }
    else:
        model_performance = {'error': 'No candidates generated'}
    
    print(f"\n🎯 Final Results:")
    print(f"   Total candidates: {len(all_candidates)}")
    print(f"   Qualified picks: {len(all_qualified)}")
    print(f"   Official picks: {len(official_picks)}")
    print(f"\n⏱️  
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_nba_probability(game_data)
        elif sport == 'Soccer':
            return _calculate_soccer_probability(game_data)
        else:
            return 0.5  # Default neutral probability
    except Exception as e:
        print(f"Analytical calculation error for {sport}: {e}")
        return 0.5

def _calculate_mlb_probability(game_data: Dict[str, Any]) -> float:
    """MLB-specific Poisson-based probability calculation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    # Calculate expected runs (better pitcher = lower ERA = fewer runs allowed)
    home_expected_runs = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_expected_runs = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    # Adjust for rest days
    rest_home = game_data.get('rest_days_home', 1)
    rest_away = game_data.get('rest_days_away', 1)
    
    if rest_home >= 2:
        home_expected_runs *= 1.05
    if rest_away >= 2:
        away_expected_runs *= 1.05
    
    # Calculate win probability using Poisson distribution
    home_win_prob = 0.0
    for home_runs in range(0, 15):
        for away_runs in range(0, 15):
            home_prob = stats.poisson.pmf(home_runs, home_expected_runs)
            away_prob = stats.poisson.pmf(away_runs, away_expected_runs)
            if home_runs > away_runs:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def _calculate_nba_probability(game_data: Dict[str, Any]) -> float:
    """NBA-specific probability calculation."""
    # Simplified model based on pace and efficiency
    pace_home = game_data.get('pace_home', 100)
    pace_away = game_data.get('pace_away', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    # Calculate expected points
    avg_pace = (pace_home + pace_away) / 2
    home_efficiency = efg_home / 0.52  # Relative to league average
    away_efficiency = efg_away / 0.52
    
    home_expected = LEAGUE_AVG_POINTS * home_efficiency * (avg_pace / 100)
    away_expected = LEAGUE_AVG_POINTS * away_efficiency * (avg_pace / 100)
    
    # Use normal distribution for basketball scoring
    home_std = home_expected * 0.15  # ~15% standard deviation
    away_std = away_expected * 0.15
    
    # Monte Carlo approach for win probability
    home_wins = 0
    simulations = 1000
    for _ in range(simulations):
        home_score = np.random.normal(home_expected, home_std)
        away_score = np.random.normal(away_expected, away_std)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / simulations

def _calculate_soccer_probability(game_data: Dict[str, Any]) -> float:
    """Soccer-specific xG-based probability calculation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    # Use Poisson distribution for goal scoring
    home_win_prob = 0.0
    for home_goals in range(0, 8):
        for away_goals in range(0, 8):
            home_prob = stats.poisson.pmf(home_goals, xg_home)
            away_prob = stats.poisson.pmf(away_goals, xg_away)
            if home_goals > away_goals:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def run_monte_carlo_simulation(game_data: Dict[str, Any], sport: str, n_sims: int = MC_SIMULATIONS) -> float:
    """Run Monte Carlo simulation for game outcome."""
    try:
        if sport == 'MLB':
            return _monte_carlo_mlb(game_data, n_sims)
        elif sport == 'NBA':
            return _monte_carlo_nba(game_data, n_sims)
        elif sport == 'Soccer':
            return _monte_carlo_soccer(game_data, n_sims)
        else:
            return 0.5
    except Exception as e:
        print(f"Monte Carlo error for {sport}: {e}")
        return 0.5

def _monte_carlo_mlb(game_data: Dict[str, Any], n_sims: int) -> float:
    """MLB Monte Carlo simulation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    home_lambda = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_lambda = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    home_wins = 0
    for _ in range(n_sims):
        home_runs = np.random.poisson(home_lambda)
        away_runs = np.random.poisson(away_lambda)
        if home_runs > away_runs:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_nba(game_data: Dict[str, Any], n_sims: int) -> float:
    """NBA Monte Carlo simulation."""
    pace_home = game_data.get('pace_home', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    home_expected = LEAGUE_AVG_POINTS * (efg_home / 0.52) * (pace_home / 100)
    away_expected = LEAGUE_AVG_POINTS * (efg_away / 0.52) * (pace_home / 100)
    
    home_wins = 0
    for _ in range(n_sims):
        home_score = np.random.normal(home_expected, home_expected * 0.15)
        away_score = np.random.normal(away_expected, away_expected * 0.15)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_soccer(game_data: Dict[str, Any], n_sims: int) -> float:
    """Soccer Monte Carlo simulation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    home_wins = 0
    for _ in range(n_sims):
        home_goals = np.random.poisson(xg_home)
        away_goals = np.random.poisson(xg_away)
        if home_goals > away_goals:
            home_wins += 1
    
    return home_wins / n_sims

def calculate_ensemble_probability(analytical_prob: float, mc_prob: float) -> float:
    """Blend analytical and Monte Carlo probabilities (50/50)."""
    return (analytical_prob + mc_prob) / 2

def calculate_ev_percentage(model_prob: float, odds: int) -> float:
    """Calculate Expected Value percentage."""
    try:
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Calculate implied probability
        implied_prob = 1 / decimal_odds
        
        # Calculate EV%
        ev_percentage = ((model_prob - implied_prob) / implied_prob) * 100
        return ev_percentage
    except Exception as e:
        print(f"EV calculation error: {e}")
        return -100

def calculate_confidence_score(game_data: Dict[str, Any], sport: str) -> int:
    """Calculate confidence score (1-10)."""
    confidence = 5  # Base score
    
    try:
        # Universal factors
        if game_data.get('rlm_flag', False):
            confidence += 2
        if game_data.get('steam_detected', False):
            confidence += 1
        if game_data.get('sharp_money', False):
            confidence += 1
        
        # Sport-specific factors
        if sport == 'MLB':
            era_home = game_data.get('era_home_starter', 4.0)
            era_away = game_data.get('era_away_starter', 4.0)
            era_diff = abs(era_home - era_away)
            if era_diff > 1.0:
                confidence += 1
            
            wind = game_data.get('weather_wind', 0)
            if wind > 15:
                confidence -= 1
        
        elif sport == 'NBA':
            injury_impact = game_data.get('injury_impact_total', 0)
            if injury_impact > 0.05:
                confidence += 1
        
        elif sport == 'Soccer':
            form_diff = game_data.get('form_difference', 0)
            if abs(form_diff) > 2:
                confidence += 1
        
        # Public betting factor
        public_pct = game_data.get('public_pct_home', 50)
        if public_pct > 75 or public_pct < 25:
            confidence += 1
        
        return max(1, min(10, confidence))
    except Exception as e:
        print(f"Confidence calculation error: {e}")
        return 5

def detect_sharp_indicators(game_data: Dict[str, Any]) -> List[str]:
    """Detect sharp betting indicators."""
    flags = []
    
    # Reverse Line Movement
    if game_data.get('public_pct_home', 50) > 65 and game_data.get('line_movement', 0) < 0:
        flags.append('RLM')
        game_data['rlm_flag'] = True
    
    # Steam detection (rapid line movement)
    line_velocity = game_data.get('line_velocity', 0)
    if abs(line_velocity) > 5:  # 5+ point move in short time
        flags.append('Steam')
        game_data['steam_detected'] = True
    
    # Sharp money indicators
    if game_data.get('bet_count_ratio', 1) < 0.3:  # Few bets but big money
        flags.append('Sharp-Money')
        game_data['sharp_money'] = True
    
    return flags

def calculate_clv(current_odds: float, opening_odds: float) -> float:
    """Calculate Closing Line Value."""
    try:
        if opening_odds == 0:
            return 0.0
        
        # Convert to decimal odds
        def to_decimal(american_odds):
            if american_odds > 0:
                return (american_odds / 100) + 1
            else:
                return (100 / abs(american_odds)) + 1
        
        current_decimal = to_decimal(current_odds)
        opening_decimal = to_decimal(opening_odds)
        
        # CLV as percentage improvement
        clv = ((current_decimal - opening_decimal) / opening_decimal) * 100
        return round(clv, 2)
    except:
        return 0.0

def calculate_kelly_stake(ev_percentage: float, odds: int, bankroll: float, confidence: int) -> float:
    """Calculate stake using Kelly criterion with confidence adjustments."""
    try:
        if ev_percentage <= 0:
            return 0
        
        # Convert to decimal odds
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Kelly calculation
        edge = ev_percentage / 100
        kelly_fraction = edge / (decimal_odds - 1)
        
        # Apply conservative sizing (quarter Kelly)
        base_stake = bankroll * kelly_fraction * 0.25
        
        # Confidence adjustment
        confidence_multiplier = confidence / 10.0
        stake = base_stake * confidence_multiplier
        
        # Double stake if confidence >= 9 (as specified)
        if confidence >= 9:
            stake *= 2
        
        # Safety caps
        max_stake = bankroll * 0.05  # 5% max per bet
        return min(stake, max_stake)
    except Exception as e:
        print(f"Stake calculation error: {e}")
        return 0
📁 main.py - Section 4: Candidate Generation and Scoring
# ---------------------------------------------------------------------------
# Candidate generation and scoring
# ---------------------------------------------------------------------------

def build_candidates(sport: str, odds_data: List[Dict[str, Any]], advanced_stats: Dict[str, Any]) -> List[Candidate]:
    """Generate betting candidates from odds and stats."""
    candidates = []
    
    for game in odds_data:
        if not game.get('bookmakers'):
            continue
            
        # Extract game info
        home_team = game.get('home_team', 'Unknown')
        away_team = game.get('away_team', 'Unknown')
        
        # Combine game data
        game_data = {
            'home_team': home_team,
            'away_team': away_team,
            **advanced_stats.get('team_stats', {}),
            **advanced_stats.get('game_factors', {}),
            **advanced_stats.get('match_factors', {}),
            **advanced_stats.get('pitcher_stats', {})
        }
        
        # Process each bookmaker's markets
        for bookmaker in game.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                market_type = market.get('key', '')
                
                for outcome in market.get('outcomes', []):
                    pick_name = outcome.get('name', '')
                    odds_value = outcome.get('price', 0)
                    
                    if odds_value and abs(odds_value) >= 100:  # Valid American odds
                        pick_description = f"{pick_name} ({market_type})"
                        if market_type == 'h2h':
                            pick_description = f"{pick_name} Moneyline"
                        
                        candidate = Candidate(
                            sport=sport,
                            pick=pick_description,
                            odds=odds_value,
                            game_data=game_data.copy()
                        )
                        candidates.append(candidate)
    
    return candidates

def score_candidate(candidate: Candidate) -> Candidate:
    """Score a betting candidate with sophisticated models."""
    try:
        # Calculate probabilities
        analytical_prob = calculate_analytical_probability(candidate.game_data, candidate.sport)
        mc_prob = run_monte_carlo_simulation(candidate.game_data, candidate.sport, 1000)  # Reduced for speed
        model_prob = calculate_ensemble_probability(analytical_prob, mc_prob)
        
        # Calculate metrics
        ev_percentage = calculate_ev_percentage(model_prob, candidate.odds)
        confidence = calculate_confidence_score(candidate.game_data, candidate.sport)
        
        # Detect sharp indicators
        sharp_flags = detect_sharp_indicators(candidate.game_data)
        
        # Calculate CLV if opening odds available
        opening_odds = candidate.game_data.get('opening_odds', candidate.odds)
        clv = calculate_clv(candidate.odds, opening_odds)
        
        # Update candidate
        candidate.ev = round(ev_percentage, 2)
        candidate.confidence = confidence
        candidate.model_prob = round(model_prob, 3)
        candidate.implied_prob = round(1 / ((abs(candidate.odds) / 100) + 1), 3)
        candidate.flags = sharp_flags
        candidate.clv_delta = clv
        
        return candidate
    except Exception as e:
        print(f"Scoring error for {candidate.pick}: {e}")
        return candidate

def filter_qualified_picks(candidates: List[Candidate]) -> List[Candidate]:
    """Filter to only qualified picks meeting EV and confidence thresholds."""
    qualified = []
    for candidate in candidates:
        if (candidate.ev >= MIN_EV_THRESHOLD and 
            candidate.confidence >= MIN_CONFIDENCE_THRESHOLD):
            qualified.append(candidate)
    return qualified
📁 main.py - Section 5: Bankroll Management and Staking
# ---------------------------------------------------------------------------
# Bankroll management and staking
# ---------------------------------------------------------------------------

def apply_staking_rules(qualified_picks: List[Candidate], bankroll: float) -> List[Pick]:
    """Apply bankroll management and calculate stakes."""
    picks = []
    daily_risk = 0.0
    max_daily_risk = bankroll * 0.15  # 15% daily cap
    max_sport_risk = bankroll * 0.40  # 40% per sport cap
    sport_risks = {}
    
    for candidate in qualified_picks:
        # Calculate stake
        stake = calculate_kelly_stake(candidate.ev, candidate.odds, bankroll, candidate.confidence)
        
        # Check sport exposure
        sport_risk = sport_risks.get(candidate.sport, 0.0)
        if sport_risk + stake > max_sport_risk:
            continue  # Skip if exceeds sport limit
        
        # Check daily exposure
        if daily_risk + stake > max_daily_risk:
            continue  # Skip if exceeds daily limit
        
        # Add to picks
        pick = Pick(**candidate.__dict__, stake=round(stake, 2))
        picks.append(pick)
        
        # Update risk tracking
        daily_risk += stake
        sport_risks[candidate.sport] = sport_risk + stake
    
    return picks
📁 main.py - Section 6: Main Workflow Orchestration
# ---------------------------------------------------------------------------
# Main workflow orchestration
# ---------------------------------------------------------------------------

def run_betting_scan(mode: str, bankroll: float = None) -> ScanResult:
    """Main orchestration function for the betting scan."""
    print(f"🚀 Starting {mode} betting scan...")
    start_time = time.time()
    
    # Use provided bankroll or default
    if bankroll is None:
        bankroll = DEFAULT_BANKROLL
    
    print(f"💰 Current bankroll: ${bankroll:,.2f}")
    
    all_candidates = []
    all_qualified = []
    sports_scanned = []
    
    # Scan each sport
    sports_to_scan = ['MLB', 'NBA', 'Soccer']  # Add more as needed
    
    for sport in sports_to_scan:
        print(f"\n📡 Scanning {sport}...")
        sports_scanned.append(sport)
        
        try:
            # Fetch data
            odds_data = fetch_odds_data(sport)
            
            # Get sport-specific advanced stats
            if sport == 'MLB':
                advanced_stats = fetch_mlb_stats()
            elif sport == 'NBA':
                advanced_stats = fetch_nba_stats()
            elif sport == 'Soccer':
                advanced_stats = fetch_soccer_stats()
            else:
                advanced_stats = {}
            
            # Build and score candidates
            candidates = build_candidates(sport, odds_data, advanced_stats)
            scored_candidates = [score_candidate(c) for c in candidates]
            qualified = filter_qualified_picks(scored_candidates)
            
            all_candidates.extend(scored_candidates)
            all_qualified.extend(qualified)
            
            print(f"   {len(candidates)} candidates, {len(qualified)} qualified")
            
        except Exception as e:
            print(f"   Error scanning {sport}: {e}")
    
    # Apply staking rules
    official_picks = apply_staking_rules(all_qualified, bankroll)
    
    execution_time = time.time() - start_time
    
    # Calculate risk metrics
    total_risk = sum(pick.stake for pick in official_picks)
    risk_percentage = (total_risk / bankroll) * 100
    
    risk_metrics = {
        'total_risk': round(total_risk, 2),
        'risk_percentage': round(risk_percentage, 2),
        'max_daily_risk': round(bankroll * 0.15, 2),
        'remaining_capacity': round((bankroll * 0.15) - total_risk, 2)
    }
    
    # Model performance metrics
    if all_candidates:
        avg_ev = sum(c.ev for c in all_qualified) / len(all_qualified) if all_qualified else 0
        avg_confidence = sum(c.confidence for c in all_qualified) / len(all_qualified) if all_qualified else 0
        model_performance = {
            'avg_ev': round(avg_ev, 2),
            'avg_confidence': round(avg_confidence, 2),
            'qualification_rate': round((len(all_qualified) / len(all_candidates)) * 100, 2),
            'final_selection_rate': round((len(official_picks) / len(all_qualified)) * 100, 2) if all_qualified else 0
        }
    else:
        model_performance = {'error': 'No candidates generated'}
    
    print(f"\n🎯 Final Results:")
    print(f"   Total candidates: {len(all_candidates)}")
    print(f"   Qualified picks: {len(all_qualified)}")
    print(f"   Official picks: {len(official_picks)}")
    print(f"\n⏱️  Scan completed in {execution_time:.2f} seconds")
    
    # Display picks
    if official_picks:
        print(f"\n🏆 Official Picks:")
        for pick in official_picks:
            flags_str = f" | {', '.join(pick.flags)}" if pick.flags else ""
            print(f"   {pick.sport}: {pick.pick} @ {pick.odds:+d} | "
                  f"EV: +{pick.ev:.1f}% | Conf: {pick.confidence}/10 | "
                  f"Stake: ${pick.stake:.0f}{flags_str}")
    
    # Create result object
    result = ScanResult(
        timestamp=datetime.utcnow().isoformat(),
        mode=mode,
        bankroll=bankroll,
        total_candidates=len(all_candidates),
        qualified_candidates=len(all_qualified),
        official_picks=[asdict(pick) for pick in official_picks],
        execution_time=round(execution_time, 2),
        sports_scanned=sports_scanned,
        risk_metrics=risk_metrics,
        model_performance=model_performance
    )
    
    return result
📁 main.py - Section 7: Web App Interface Functions
# ---------------------------------------------------------------------------
# Web App Interface Functions
# ---------------------------------------------------------------------------

def get_scan_json(mode: str = "manual", bankroll: float = None) -> str:
    """Run scan and return JSON result for web app consumption."""
    try:
        result = run_betting_scan(mode, bankroll)
        return json.dumps(asdict(result), indent=2)
    except Exception as e:
        error_result = {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'mode': mode,
            'status': 'failed'
        }
        return json.dumps(error_result, indent=2)

def get_model_status() -> Dict[str, Any]:
    """Return model status and configuration for web app."""
    return {
        'model_config': {
            'min_ev_threshold': MIN_EV_THRESHOLD,
            'min_confidence_threshold': MIN_CONFIDENCE_THRESHOLD,
            'mc_simulations': MC_SIMULATIONS,
            'default_bankroll': DEFAULT_BANKROLL
        },
        'supported_sports': ['MLB', 'NBA', 'Soccer', 'WNBA', 'NHL'],
        'model_features': [
            'Poisson + Monte Carlo probability models',
            'Sharp betting detection (RLM, CLV, Steam)',
            'Kelly criterion staking with confidence adjustments',
            'Multi-sport advanced statistics integration',
            'Risk management with exposure caps'
        ],
        'status': 'operational',
        'version': '2.0.0'
    }
📁 main.py - Section 8: CLI Entry Point
# ---------------------------------------------------------------------------
# CLI entry
📁 main.py - Section 3: Sophisticated Model Functions
# ---------------------------------------------------------------------------
# Sophisticated Model Functions
# ---------------------------------------------------------------------------

def calculate_analytical_probability(game_data: Dict[str, Any], sport: str) -> float:
    """Calculate win probability using analytical models."""
    try:
        if sport == 'MLB':
            return _calculate_mlb_probability(game_data)
        elif sport == 'NBA':
            return _calculate_nba_probability(game_data)
        elif sport == 'Soccer':
            return _calculate_soccer_probability(game_data)
        else:
            return 0.5  # Default neutral probability
    except Exception as e:
        print(f"Analytical calculation error for {sport}: {e}")
        return 0.5

def _calculate_mlb_probability(game_data: Dict[str, Any]) -> float:
    """MLB-specific Poisson-based probability calculation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    # Calculate expected runs (better pitcher = lower ERA = fewer runs allowed)
    home_expected_runs = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_expected_runs = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    # Adjust for rest days
    rest_home = game_data.get('rest_days_home', 1)
    rest_away = game_data.get('rest_days_away', 1)
    
    if rest_home >= 2:
        home_expected_runs *= 1.05
    if rest_away >= 2:
        away_expected_runs *= 1.05
    
    # Calculate win probability using Poisson distribution
    home_win_prob = 0.0
    for home_runs in range(0, 15):
        for away_runs in range(0, 15):
            home_prob = stats.poisson.pmf(home_runs, home_expected_runs)
            away_prob = stats.poisson.pmf(away_runs, away_expected_runs)
            if home_runs > away_runs:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def _calculate_nba_probability(game_data: Dict[str, Any]) -> float:
    """NBA-specific probability calculation."""
    # Simplified model based on pace and efficiency
    pace_home = game_data.get('pace_home', 100)
    pace_away = game_data.get('pace_away', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    # Calculate expected points
    avg_pace = (pace_home + pace_away) / 2
    home_efficiency = efg_home / 0.52  # Relative to league average
    away_efficiency = efg_away / 0.52
    
    home_expected = LEAGUE_AVG_POINTS * home_efficiency * (avg_pace / 100)
    away_expected = LEAGUE_AVG_POINTS * away_efficiency * (avg_pace / 100)
    
    # Use normal distribution for basketball scoring
    home_std = home_expected * 0.15  # ~15% standard deviation
    away_std = away_expected * 0.15
    
    # Monte Carlo approach for win probability
    home_wins = 0
    simulations = 1000
    for _ in range(simulations):
        home_score = np.random.normal(home_expected, home_std)
        away_score = np.random.normal(away_expected, away_std)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / simulations

def _calculate_soccer_probability(game_data: Dict[str, Any]) -> float:
    """Soccer-specific xG-based probability calculation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    # Use Poisson distribution for goal scoring
    home_win_prob = 0.0
    for home_goals in range(0, 8):
        for away_goals in range(0, 8):
            home_prob = stats.poisson.pmf(home_goals, xg_home)
            away_prob = stats.poisson.pmf(away_goals, xg_away)
            if home_goals > away_goals:
                home_win_prob += home_prob * away_prob
    
    return max(0.1, min(0.9, home_win_prob))

def run_monte_carlo_simulation(game_data: Dict[str, Any], sport: str, n_sims: int = MC_SIMULATIONS) -> float:
    """Run Monte Carlo simulation for game outcome."""
    try:
        if sport == 'MLB':
            return _monte_carlo_mlb(game_data, n_sims)
        elif sport == 'NBA':
            return _monte_carlo_nba(game_data, n_sims)
        elif sport == 'Soccer':
            return _monte_carlo_soccer(game_data, n_sims)
        else:
            return 0.5
    except Exception as e:
        print(f"Monte Carlo error for {sport}: {e}")
        return 0.5

def _monte_carlo_mlb(game_data: Dict[str, Any], n_sims: int) -> float:
    """MLB Monte Carlo simulation."""
    home_era = game_data.get('era_home_starter', 4.0)
    away_era = game_data.get('era_away_starter', 4.0)
    park_factor = game_data.get('park_factor', 1.0)
    
    home_lambda = LEAGUE_AVG_RUNS * (away_era / 4.0) * park_factor
    away_lambda = LEAGUE_AVG_RUNS * (home_era / 4.0)
    
    home_wins = 0
    for _ in range(n_sims):
        home_runs = np.random.poisson(home_lambda)
        away_runs = np.random.poisson(away_lambda)
        if home_runs > away_runs:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_nba(game_data: Dict[str, Any], n_sims: int) -> float:
    """NBA Monte Carlo simulation."""
    pace_home = game_data.get('pace_home', 100)
    efg_home = game_data.get('efg_home', 0.52)
    efg_away = game_data.get('efg_away', 0.52)
    
    home_expected = LEAGUE_AVG_POINTS * (efg_home / 0.52) * (pace_home / 100)
    away_expected = LEAGUE_AVG_POINTS * (efg_away / 0.52) * (pace_home / 100)
    
    home_wins = 0
    for _ in range(n_sims):
        home_score = np.random.normal(home_expected, home_expected * 0.15)
        away_score = np.random.normal(away_expected, away_expected * 0.15)
        if home_score > away_score:
            home_wins += 1
    
    return home_wins / n_sims

def _monte_carlo_soccer(game_data: Dict[str, Any], n_sims: int) -> float:
    """Soccer Monte Carlo simulation."""
    xg_home = game_data.get('xg_home', 1.3)
    xg_away = game_data.get('xg_away', 1.1)
    
    home_wins = 0
    for _ in range(n_sims):
        home_goals = np.random.poisson(xg_home)
        away_goals = np.random.poisson(xg_away)
        if home_goals > away_goals:
            home_wins += 1
    
    return home_wins / n_sims

def calculate_ensemble_probability(analytical_prob: float, mc_prob: float) -> float:
    """Blend analytical and Monte Carlo probabilities (50/50)."""
    return (analytical_prob + mc_prob) / 2

def calculate_ev_percentage(model_prob: float, odds: int) -> float:
    """Calculate Expected Value percentage."""
    try:
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Calculate implied probability
        implied_prob = 1 / decimal_odds
        
        # Calculate EV%
        ev_percentage = ((model_prob - implied_prob) / implied_prob) * 100
        return ev_percentage
    except Exception as e:
        print(f"EV calculation error: {e}")
        return -100

def calculate_confidence_score(game_data: Dict[str, Any], sport: str) -> int:
    """Calculate confidence score (1-10)."""
    confidence = 5  # Base score
    
    try:
        # Universal factors
        if game_data.get('rlm_flag', False):
            confidence += 2
        if game_data.get('steam_detected', False):
            confidence += 1
        if game_data.get('sharp_money', False):
            confidence += 1
        
        # Sport-specific factors
        if sport == 'MLB':
            era_home = game_data.get('era_home_starter', 4.0)
            era_away = game_data.get('era_away_starter', 4.0)
            era_diff = abs(era_home - era_away)
            if era_diff > 1.0:
                confidence += 1
            
            wind = game_data.get('weather_wind', 0)
            if wind > 15:
                confidence -= 1
        
        elif sport == 'NBA':
            injury_impact = game_data.get('injury_impact_total', 0)
            if injury_impact > 0.05:
                confidence += 1
        
        elif sport == 'Soccer':
            form_diff = game_data.get('form_difference', 0)
            if abs(form_diff) > 2:
                confidence += 1
        
        # Public betting factor
        public_pct = game_data.get('public_pct_home', 50)
        if public_pct > 75 or public_pct < 25:
            confidence += 1
        
        return max(1, min(10, confidence))
    except Exception as e:
        print(f"Confidence calculation error: {e}")
        return 5

def detect_sharp_indicators(game_data: Dict[str, Any]) -> List[str]:
    """Detect sharp betting indicators."""
    flags = []
    
    # Reverse Line Movement
    if game_data.get('public_pct_home', 50) > 65 and game_data.get('line_movement', 0) < 0:
        flags.append('RLM')
        game_data['rlm_flag'] = True
    
    # Steam detection (rapid line movement)
    line_velocity = game_data.get('line_velocity', 0)
    if abs(line_velocity) > 5:  # 5+ point move in short time
        flags.append('Steam')
        game_data['steam_detected'] = True
    
    # Sharp money indicators
    if game_data.get('bet_count_ratio', 1) < 0.3:  # Few bets but big money
        flags.append('Sharp-Money')
        game_data['sharp_money'] = True
    
    return flags

def calculate_clv(current_odds: float, opening_odds: float) -> float:
    """Calculate Closing Line Value."""
    try:
        if opening_odds == 0:
            return 0.0
        
        # Convert to decimal odds
        def to_decimal(american_odds):
            if american_odds > 0:
                return (american_odds / 100) + 1
            else:
                return (100 / abs(american_odds)) + 1
        
        current_decimal = to_decimal(current_odds)
        opening_decimal = to_decimal(opening_odds)
        
        # CLV as percentage improvement
        clv = ((current_decimal - opening_decimal) / opening_decimal) * 100
        return round(clv, 2)
    except:
        return 0.0

def calculate_kelly_stake(ev_percentage: float, odds: int, bankroll: float, confidence: int) -> float:
    """Calculate stake using Kelly criterion with confidence adjustments."""
    try:
        if ev_percentage <= 0:
            return 0
        
        # Convert to decimal odds
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Kelly calculation
        edge = ev_percentage / 100
        kelly_fraction = edge / (decimal_odds - 1)
        
        # Apply conservative sizing (quarter Kelly)
        base_stake = bankroll * kelly_fraction * 0.25
        
        # Confidence adjustment
        confidence_multiplier = confidence / 10.0
        stake = base_stake * confidence_multiplier
        
        # Double stake if confidence >= 9 (as specified)
        if confidence >= 9:
            stake *= 2
        
        # Safety caps
        max_stake = bankroll * 0.05  # 5% max per bet
        return min(stake, max_stake)
    except Exception as e:
        print(f"Stake calculation error: {e}")
        return 0
📁 main.py - Section 4: Candidate Generation and Scoring
# ---------------------------------------------------------------------------
# Candidate generation and scoring
# ---------------------------------------------------------------------------

def build_candidates(sport: str, odds_data: List[Dict[str, Any]], advanced_stats: Dict[str, Any]) -> List[Candidate]:
    """Generate betting candidates from odds and stats."""
    candidates = []
    
    for game in odds_data:
        if not game.get('bookmakers'):
            continue
            
        # Extract game info
        home_team = game.get('home_team', 'Unknown')
        away_team = game.get('away_team', 'Unknown')
        
        # Combine game data
        game_data = {
            'home_team': home_team,
            'away_team': away_team,
            **advanced_stats.get('team_stats', {}),
            **advanced_stats.get('game_factors', {}),
            **advanced_stats.get('match_factors', {}),
            **advanced_stats.get('pitcher_stats', {})
        }
        
        # Process each bookmaker's markets
        for bookmaker in game.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                market_type = market.get('key', '')
                
                for outcome in market.get('outcomes', []):
                    pick_name = outcome.get('name', '')
                    odds_value = outcome.get('price', 0)
                    
                    if odds_value and abs(odds_value) >= 100:  # Valid American odds
                        pick_description = f"{pick_name} ({market_type})"
                        if market_type == 'h2h':
                            pick_description = f"{pick_name} Moneyline"
                        
                        candidate = Candidate(
                            sport=sport,
                            pick=pick_description,
                            odds=odds_value,
                            game_data=game_data.copy()
                        )
                        candidates.append(candidate)
    
    return candidates

def score_candidate(candidate: Candidate) -> Candidate:
    """Score a betting candidate with sophisticated models."""
    try:
        # Calculate probabilities
        analytical_prob = calculate_analytical_probability(candidate.game_data, candidate.sport)
        mc_prob = run_monte_carlo_simulation(candidate.game_data, candidate.sport, 1000)  # Reduced for speed
        model_prob = calculate_ensemble_probability(analytical_prob, mc_prob)
        
        # Calculate metrics
        ev_percentage = calculate_ev_percentage(model_prob, candidate.odds)
        confidence = calculate_confidence_score(candidate.game_data, candidate.sport)
        
        # Detect sharp indicators
        sharp_flags = detect_sharp_indicators(candidate.game_data)
        
        # Calculate CLV if opening odds available
        opening_odds = candidate.game_data.get('opening_odds', candidate.odds)
        clv = calculate_clv(candidate.odds, opening_odds)
        
        # Update candidate
        candidate.ev = round(ev_percentage, 2)
        candidate.confidence = confidence
        candidate.model_prob = round(model_prob, 3)
        candidate.implied_prob = round(1 / ((abs(candidate.odds) / 100) + 1), 3)
        candidate.flags = sharp_flags
        candidate.clv_delta = clv
        
        return candidate
    except Exception as e:
        print(f"Scoring error for {candidate.pick}: {e}")
        return candidate

def filter_qualified_picks(candidates: List[Candidate]) -> List[Candidate]:
    """Filter to only qualified picks meeting EV and confidence thresholds."""
    qualified = []
    for candidate in candidates:
        if (candidate.ev >= MIN_EV_THRESHOLD and 
            candidate.confidence >= MIN_CONFIDENCE_THRESHOLD):
            qualified.append(candidate)
    return qualified
📁 main.py - Section 5: Bankroll Management and Staking
# ---------------------------------------------------------------------------
# Bankroll management and staking
# ---------------------------------------------------------------------------

def apply_staking_rules(qualified_picks: List[Candidate], bankroll: float) -> List[Pick]:
    """Apply bankroll management and calculate stakes."""
    picks = []
    daily_risk = 0.0
    max_daily_risk = bankroll * 0.15  # 15% daily cap
    max_sport_risk = bankroll * 0.40  # 40% per sport cap
    sport_risks = {}
    
    for candidate in qualified_picks:
        # Calculate stake
        stake = calculate_kelly_stake(candidate.ev, candidate.odds, bankroll, candidate.confidence)
        
        # Check sport exposure
        sport_risk = sport_risks.get(candidate.sport, 0.0)
        if sport_risk + stake > max_sport_risk:
            continue  # Skip if exceeds sport limit
        
        # Check daily exposure
        if daily_risk + stake > max_daily_risk:
            continue  # Skip if exceeds daily limit
        
        # Add to picks
        pick = Pick(**candidate.__dict__, stake=round(stake, 2))
        picks.append(pick)
        
        # Update risk tracking
        daily_risk += stake
        sport_risks[candidate.sport] = sport_risk + stake
    
    return picks
📁 main.py - Section 6: Main Workflow Orchestration
# ---------------------------------------------------------------------------
# Main workflow orchestration
# ---------------------------------------------------------------------------

def run_betting_scan(mode: str, bankroll: float = None) -> ScanResult:
    """Main orchestration function for the betting scan."""
    print(f"🚀 Starting {mode} betting scan...")
    start_time = time.time()
    
    # Use provided bankroll or default
    if bankroll is None:
        bankroll = DEFAULT_BANKROLL
    
    print(f"💰 Current bankroll: ${bankroll:,.2f}")
    
    all_candidates = []
    all_qualified = []
    sports_scanned = []
    
    # Scan each sport
    sports_to_scan = ['MLB', 'NBA', 'Soccer']  # Add more as needed
    
    for sport in sports_to_scan:
        print(f"\n📡 Scanning {sport}...")
        sports_scanned.append(sport)
        
        try:
            # Fetch data
            odds_data = fetch_odds_data(sport)
            
            # Get sport-specific advanced stats
            if sport == 'MLB':
                advanced_stats = fetch_mlb_stats()
            elif sport == 'NBA':
                advanced_stats = fetch_nba_stats()
            elif sport == 'Soccer':
                advanced_stats = fetch_soccer_stats()
            else:
                advanced_stats = {}
            
            # Build and score candidates
            candidates = build_candidates(sport, odds_data, advanced_stats)
            scored_candidates = [score_candidate(c) for c in candidates]
            qualified = filter_qualified_picks(scored_candidates)
            
            all_candidates.extend(scored_candidates)
            all_qualified.extend(qualified)
            
            print(f"   {len(candidates)} candidates, {len(qualified)} qualified")
            
        except Exception as e:
            print(f"   Error scanning {sport}: {e}")
    
    # Apply staking rules
    official_picks = apply_staking_rules(all_qualified, bankroll)
    
    execution_time = time.time() - start_time
    
    # Calculate risk metrics
    total_risk = sum(pick.stake for pick in official_picks)
    risk_percentage = (total_risk / bankroll) * 100
    
    risk_metrics = {
        'total_risk': round(total_risk, 2),
        'risk_percentage': round(risk_percentage, 2),
        'max_daily_risk': round(bankroll * 0.15, 2),
        'remaining_capacity': round((bankroll * 0.15) - total_risk, 2)
    }
    
    # Model performance metrics
    if all_candidates:
        avg_ev = sum(c.ev for c in all_qualified) / len(all_qualified) if all_qualified else 0
        avg_confidence = sum(c.confidence for c in all_qualified) / len(all_qualified) if all_qualified else 0
        model_performance = {
            'avg_ev': round(avg_ev, 2),
            'avg_confidence': round(avg_confidence, 2),
            'qualification_rate': round((len(all_qualified) / len(all_candidates)) * 100, 2),
            'final_selection_rate': round((len(official_picks) / len(all_qualified)) * 100, 2) if all_qualified else 0
        }
    else:
        model_performance = {'error': 'No candidates generated'}
    
    print(f"\n🎯 Final Results:")
    print(f"   Total candidates: {len(all_candidates)}")
    print(f"   Qualified picks: {len(all_qualified)}")
    print(f"   Official picks: {len(official_picks)}")
    print(f"\n⏱️  Scan completed in {execution_time:.2f} seconds")
    
    # Display picks
    if official_picks:
        print(f"\n🏆 Official Picks:")
        for pick in official_picks:
            flags_str = f" | {', '.join(pick.flags)}" if pick.flags else ""
            print(f"   {pick.sport}: {pick.pick} @ {pick.odds:+d} | "
                  f"EV: +{pick.ev:.1f}% | Conf: {pick.confidence}/10 | "
                  f"Stake: ${pick.stake:.0f}{flags_str}")
    
    # Create result object
    result = ScanResult(
        timestamp=datetime.utcnow().isoformat(),
        mode=mode,
        bankroll=bankroll,
        total_candidates=len(all_candidates),
        qualified_candidates=len(all_qualified),
        official_picks=[asdict(pick) for pick in official_picks],
        execution_time=round(execution_time, 2),
        sports_scanned=sports_scanned,
        risk_metrics=risk_metrics,
        model_performance=model_performance
    )
    
    return result
📁 main.py - Section 7: Web App Interface Functions
# ---------------------------------------------------------------------------
# Web App Interface Functions
# ---------------------------------------------------------------------------

def get_scan_json(mode: str = "manual", bankroll: float = None) -> str:
    """Run scan and return JSON result for web app consumption."""
    try:
        result = run_betting_scan(mode, bankroll)
        return json.dumps(asdict(result), indent=2)
    except Exception as e:
        error_result = {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'mode': mode,
            'status': 'failed'
        }
        return json.dumps(error_result, indent=2)

def get_model_status() -> Dict[str, Any]:
    """Return model status and configuration for web app."""
    return {
        'model_config': {
            'min_ev_threshold': MIN_EV_THRESHOLD,
            'min_confidence_threshold': MIN_CONFIDENCE_THRESHOLD,
            'mc_simulations': MC_SIMULATIONS,
            'default_bankroll': DEFAULT_BANKROLL
        },
        'supported_sports': ['MLB', 'NBA', 'Soccer', 'WNBA', 'NHL'],
        'model_features': [
            'Poisson + Monte Carlo probability models',
            'Sharp betting detection (RLM, CLV, Steam)',
            'Kelly criterion staking with confidence adjustments',
            'Multi-sport advanced statistics integration',
            'Risk management with exposure caps'
        ],
        'status': 'operational',
        'version': '2.0.0'
    }
📁 main.py - Section 8: CLI Entry Point
# ---------------------------------------------------------------------------
# CLI entry point (for testing)
# ---------------------------------------------------------------------------

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Universal Betting Dashboard - Web App Version",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--mode",
        choices=["morning", "midday", "final", "manual"],
        default="manual",
        help="Scan mode: morning (08:00 ET), midday (12:00 ET), final (16:30 ET), manual"
    )
    parser.add_argument(
        "--bankroll",
        type=float,
        help="Override default bankroll amount"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format for web app consumption"
    )
    return parser.parse_args()

def main() -> None:
    """Main entry point."""
    try:
        args = parse_arguments()
        
        if args.json:
            # JSON output for web app
            json_result = get_scan_json(args.mode, args.bankroll)
            print(json_result)
        else:
            # Regular console output
            result = run_betting_scan(args.mode, args.bankroll)
            print(f"\n✅ Scan completed successfully")
            print(f"📊 Generated {len(result.official_picks)} official picks")
            
    except KeyboardInterrupt:
        print("\n⚠️  Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
