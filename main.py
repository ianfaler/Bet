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

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY", "")
APISPORTS_KEY = os.getenv("APISPORTS_KEY", "")

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
