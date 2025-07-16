"""
Data Input Manager for Sharp Betting Predictor

Handles data input from multiple sources:
- CSV file uploads (odds, public betting data, line movements)
- JSON data uploads
- Manual admin panel input
- Data validation and transformation
- Integration with existing system APIs
"""

import csv
import json
import pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
import io
import logging
from pathlib import Path


@dataclass
class GameData:
    """Structured game data for analysis."""
    game_id: str
    sport: str
    home_team: str
    away_team: str
    game_date: datetime
    matchup_data: Dict[str, Any]
    odds_data: Dict[str, Any]
    public_betting_data: Dict[str, Any]
    line_movement_data: List[Dict[str, Any]]
    model_predictions: Optional[Dict[str, Any]] = None
    sharp_indicators: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BettingLine:
    """Individual betting line data."""
    book: str
    bet_type: str  # "moneyline", "spread", "total"
    line_value: Optional[float]  # spread or total number
    odds: int  # American odds
    timestamp: datetime
    is_current: bool = True


@dataclass
class PublicBettingInfo:
    """Public betting percentage data."""
    bet_type: str
    side: str  # "home", "away", "over", "under", "favorite", "underdog"
    bets_percentage: float
    money_percentage: float
    ticket_count: Optional[int] = None
    handle_amount: Optional[float] = None
    timestamp: Optional[datetime] = None


class DataInputManager:
    """Manages all data input for the Sharp Betting Predictor."""
    
    def __init__(self, data_directory: str = "data"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Validation rules
        self.required_csv_columns = {
            "odds": ["game_id", "book", "bet_type", "odds"],
            "public_betting": ["game_id", "bet_type", "bets_pct", "money_pct"],
            "line_movements": ["game_id", "book", "from_line", "to_line", "timestamp"],
            "games": ["game_id", "sport", "home_team", "away_team", "game_date"]
        }
    
    def upload_csv_data(self, file_content: str, data_type: str) -> Dict[str, Any]:
        """
        Upload and process CSV data.
        
        Args:
            file_content: CSV file content as string
            data_type: Type of data ("odds", "public_betting", "line_movements", "games")
            
        Returns:
            Dict with processing results
        """
        try:
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(file_content))
            rows = list(csv_reader)
            
            # Validate columns
            if not self._validate_csv_columns(rows, data_type):
                return {
                    "success": False,
                    "error": f"Invalid CSV format for {data_type}",
                    "required_columns": self.required_csv_columns.get(data_type, [])
                }
            
            # Process data based on type
            processed_data = self._process_csv_data(rows, data_type)
            
            # Save to file
            filename = f"{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.data_directory / filename
            
            with open(filepath, 'w') as f:
                json.dump(processed_data, f, indent=2, default=str)
            
            return {
                "success": True,
                "processed_rows": len(rows),
                "data_type": data_type,
                "filename": filename,
                "data": processed_data
            }
            
        except Exception as e:
            self.logger.error(f"Error processing CSV: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_json_data(self, json_content: str, data_type: str) -> Dict[str, Any]:
        """
        Upload and process JSON data.
        
        Args:
            json_content: JSON content as string
            data_type: Type of data
            
        Returns:
            Dict with processing results
        """
        try:
            data = json.loads(json_content)
            
            # Validate JSON structure
            if not self._validate_json_structure(data, data_type):
                return {
                    "success": False,
                    "error": f"Invalid JSON structure for {data_type}"
                }
            
            # Process and normalize data
            processed_data = self._process_json_data(data, data_type)
            
            # Save to file
            filename = f"{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.data_directory / filename
            
            with open(filepath, 'w') as f:
                json.dump(processed_data, f, indent=2, default=str)
            
            return {
                "success": True,
                "data_type": data_type,
                "filename": filename,
                "data": processed_data
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON format: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Error processing JSON: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_manual_game_entry(
        self,
        sport: str,
        home_team: str,
        away_team: str,
        game_date: str,
        odds_data: Dict[str, Any],
        public_data: Optional[Dict[str, Any]] = None,
        model_predictions: Optional[Dict[str, Any]] = None
    ) -> GameData:
        """
        Create a manual game entry.
        
        Args:
            sport: Sport type
            home_team: Home team name
            away_team: Away team name
            game_date: Game date (YYYY-MM-DD or YYYY-MM-DD HH:MM)
            odds_data: Odds information
            public_data: Public betting data (optional)
            model_predictions: Model prediction data (optional)
            
        Returns:
            GameData object
        """
        game_id = f"{sport}_{home_team}_{away_team}_{game_date}".replace(" ", "_")
        
        # Parse game date
        try:
            if " " in game_date:
                parsed_date = datetime.strptime(game_date, "%Y-%m-%d %H:%M")
            else:
                parsed_date = datetime.strptime(game_date, "%Y-%m-%d")
        except ValueError:
            parsed_date = datetime.now()
        
        # Structure the data
        game_data = GameData(
            game_id=game_id,
            sport=sport,
            home_team=home_team,
            away_team=away_team,
            game_date=parsed_date,
            matchup_data={
                "home_team": home_team,
                "away_team": away_team,
                "sport": sport
            },
            odds_data=odds_data,
            public_betting_data=public_data or {},
            line_movement_data=[],
            model_predictions=model_predictions,
            metadata={
                "created_manually": True,
                "created_at": datetime.now().isoformat()
            }
        )
        
        return game_data
    
    def add_line_movement(
        self,
        game_id: str,
        book: str,
        bet_type: str,
        from_line: float,
        to_line: float,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add line movement data to a game.
        
        Args:
            game_id: Game identifier
            book: Sportsbook name
            bet_type: Type of bet
            from_line: Starting line
            to_line: Ending line
            timestamp: When movement occurred (optional)
            
        Returns:
            Dict with operation result
        """
        movement_data = {
            "game_id": game_id,
            "book": book,
            "bet_type": bet_type,
            "from_line": from_line,
            "to_line": to_line,
            "movement_size": abs(to_line - from_line),
            "direction": "up" if to_line > from_line else "down",
            "timestamp": timestamp or datetime.now().isoformat()
        }
        
        # Save to movements file
        movements_file = self.data_directory / "line_movements.json"
        
        if movements_file.exists():
            with open(movements_file, 'r') as f:
                movements = json.load(f)
        else:
            movements = []
        
        movements.append(movement_data)
        
        with open(movements_file, 'w') as f:
            json.dump(movements, f, indent=2)
        
        return {
            "success": True,
            "movement_added": movement_data
        }
    
    def get_game_data(self, game_id: str) -> Optional[GameData]:
        """
        Retrieve game data by ID.
        
        Args:
            game_id: Game identifier
            
        Returns:
            GameData object if found, None otherwise
        """
        # Look through all game files
        for game_file in self.data_directory.glob("games_*.json"):
            with open(game_file, 'r') as f:
                games = json.load(f)
                
                for game in games:
                    if game.get("game_id") == game_id:
                        return self._dict_to_game_data(game)
        
        return None
    
    def get_all_games(self, sport: Optional[str] = None) -> List[GameData]:
        """
        Get all game data, optionally filtered by sport.
        
        Args:
            sport: Sport filter (optional)
            
        Returns:
            List of GameData objects
        """
        all_games = []
        
        for game_file in self.data_directory.glob("games_*.json"):
            with open(game_file, 'r') as f:
                games = json.load(f)
                
                for game in games:
                    game_data = self._dict_to_game_data(game)
                    if sport is None or game_data.sport.lower() == sport.lower():
                        all_games.append(game_data)
        
        return all_games
    
    def _validate_csv_columns(self, rows: List[Dict], data_type: str) -> bool:
        """Validate CSV has required columns."""
        if not rows:
            return False
        
        required_cols = self.required_csv_columns.get(data_type, [])
        if not required_cols:
            return True
        
        row_columns = set(rows[0].keys())
        required_columns = set(required_cols)
        
        return required_columns.issubset(row_columns)
    
    def _validate_json_structure(self, data: Any, data_type: str) -> bool:
        """Validate JSON structure."""
        # Basic validation - can be expanded
        if data_type == "games":
            if isinstance(data, list):
                return all(isinstance(game, dict) and "game_id" in game for game in data)
            elif isinstance(data, dict):
                return "game_id" in data
        
        return True
    
    def _process_csv_data(self, rows: List[Dict], data_type: str) -> List[Dict]:
        """Process CSV data based on type."""
        processed = []
        
        for row in rows:
            if data_type == "odds":
                processed_row = {
                    "game_id": row["game_id"],
                    "book": row["book"],
                    "bet_type": row["bet_type"],
                    "odds": int(row["odds"]),
                    "line_value": float(row.get("line_value", 0)) if row.get("line_value") else None,
                    "timestamp": row.get("timestamp", datetime.now().isoformat())
                }
            
            elif data_type == "public_betting":
                processed_row = {
                    "game_id": row["game_id"],
                    "bet_type": row["bet_type"],
                    "side": row.get("side", "home"),
                    "bets_percentage": float(row["bets_pct"]),
                    "money_percentage": float(row["money_pct"]),
                    "split_difference": float(row["money_pct"]) - float(row["bets_pct"]),
                    "timestamp": row.get("timestamp", datetime.now().isoformat())
                }
            
            elif data_type == "line_movements":
                processed_row = {
                    "game_id": row["game_id"],
                    "book": row["book"],
                    "bet_type": row.get("bet_type", "moneyline"),
                    "from_line": float(row["from_line"]),
                    "to_line": float(row["to_line"]),
                    "movement_size": abs(float(row["to_line"]) - float(row["from_line"])),
                    "direction": "up" if float(row["to_line"]) > float(row["from_line"]) else "down",
                    "timestamp": row.get("timestamp", datetime.now().isoformat())
                }
            
            elif data_type == "games":
                processed_row = {
                    "game_id": row["game_id"],
                    "sport": row["sport"],
                    "home_team": row["home_team"],
                    "away_team": row["away_team"],
                    "game_date": row["game_date"],
                    "created_at": datetime.now().isoformat()
                }
            
            else:
                processed_row = row
            
            processed.append(processed_row)
        
        return processed
    
    def _process_json_data(self, data: Any, data_type: str) -> Any:
        """Process JSON data."""
        # Add timestamps and normalize structure
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "timestamp" not in item:
                    item["timestamp"] = datetime.now().isoformat()
        elif isinstance(data, dict) and "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()
        
        return data
    
    def _dict_to_game_data(self, game_dict: Dict) -> GameData:
        """Convert dictionary to GameData object."""
        return GameData(
            game_id=game_dict["game_id"],
            sport=game_dict["sport"],
            home_team=game_dict["home_team"],
            away_team=game_dict["away_team"],
            game_date=datetime.fromisoformat(game_dict["game_date"]) if isinstance(game_dict["game_date"], str) else game_dict["game_date"],
            matchup_data=game_dict.get("matchup_data", {}),
            odds_data=game_dict.get("odds_data", {}),
            public_betting_data=game_dict.get("public_betting_data", {}),
            line_movement_data=game_dict.get("line_movement_data", []),
            model_predictions=game_dict.get("model_predictions"),
            sharp_indicators=game_dict.get("sharp_indicators"),
            metadata=game_dict.get("metadata", {})
        )
    
    def export_data_template(self, data_type: str) -> str:
        """
        Export CSV template for data upload.
        
        Args:
            data_type: Type of data template needed
            
        Returns:
            CSV template as string
        """
        templates = {
            "odds": [
                ["game_id", "book", "bet_type", "odds", "line_value", "timestamp"],
                ["MLB_NYY_BOS_2025-01-15", "DraftKings", "moneyline", "-150", "", "2025-01-15 19:00:00"],
                ["MLB_NYY_BOS_2025-01-15", "DraftKings", "spread", "-110", "-1.5", "2025-01-15 19:00:00"]
            ],
            "public_betting": [
                ["game_id", "bet_type", "side", "bets_pct", "money_pct", "timestamp"],
                ["MLB_NYY_BOS_2025-01-15", "moneyline", "home", "65", "72", "2025-01-15 19:00:00"],
                ["MLB_NYY_BOS_2025-01-15", "spread", "favorite", "58", "68", "2025-01-15 19:00:00"]
            ],
            "line_movements": [
                ["game_id", "book", "bet_type", "from_line", "to_line", "timestamp"],
                ["MLB_NYY_BOS_2025-01-15", "DraftKings", "spread", "-1.0", "-1.5", "2025-01-15 18:30:00"],
                ["MLB_NYY_BOS_2025-01-15", "FanDuel", "spread", "-1.0", "-1.5", "2025-01-15 18:32:00"]
            ],
            "games": [
                ["game_id", "sport", "home_team", "away_team", "game_date"],
                ["MLB_NYY_BOS_2025-01-15", "MLB", "Yankees", "Red Sox", "2025-01-15 19:00:00"],
                ["NBA_LAL_GSW_2025-01-15", "NBA", "Lakers", "Warriors", "2025-01-15 20:30:00"]
            ]
        }
        
        if data_type not in templates:
            return ""
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        
        for row in templates[data_type]:
            writer.writerow(row)
        
        return output.getvalue()
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all uploaded data."""
        summary = {
            "games_count": 0,
            "odds_files": 0,
            "public_betting_files": 0,
            "line_movement_files": 0,
            "last_upload": None,
            "sports": set(),
            "data_files": []
        }
        
        for data_file in self.data_directory.glob("*.json"):
            file_info = {
                "filename": data_file.name,
                "size": data_file.stat().st_size,
                "modified": datetime.fromtimestamp(data_file.stat().st_mtime).isoformat()
            }
            summary["data_files"].append(file_info)
            
            if "games_" in data_file.name:
                summary["games_count"] += 1
                
                # Count sports
                try:
                    with open(data_file, 'r') as f:
                        games = json.load(f)
                        for game in games:
                            summary["sports"].add(game.get("sport", "Unknown"))
                except:
                    pass
            
            elif "odds_" in data_file.name:
                summary["odds_files"] += 1
            elif "public_betting_" in data_file.name:
                summary["public_betting_files"] += 1
            elif "line_movements" in data_file.name:
                summary["line_movement_files"] += 1
        
        summary["sports"] = list(summary["sports"])
        
        if summary["data_files"]:
            summary["last_upload"] = max(f["modified"] for f in summary["data_files"])
        
        return summary


# Helper functions for easy data creation
def create_odds_data(
    moneyline_home: int,
    moneyline_away: int,
    spread_line: float,
    spread_odds: int = -110,
    total_line: float = 8.5,
    total_odds: int = -110,
    book: str = "Manual"
) -> Dict[str, Any]:
    """Helper to create odds data structure."""
    return {
        "moneyline": {
            "home": moneyline_home,
            "away": moneyline_away,
            "book": book
        },
        "spread": {
            "line": spread_line,
            "home_odds": spread_odds,
            "away_odds": spread_odds,
            "book": book
        },
        "total": {
            "line": total_line,
            "over_odds": total_odds,
            "under_odds": total_odds,
            "book": book
        }
    }


def create_public_betting_data(
    moneyline_home_bets: float,
    moneyline_home_money: float,
    spread_favorite_bets: float,
    spread_favorite_money: float,
    total_over_bets: float,
    total_over_money: float
) -> Dict[str, Any]:
    """Helper to create public betting data structure."""
    return {
        "moneyline": {
            "home_bets_pct": moneyline_home_bets,
            "home_money_pct": moneyline_home_money,
            "away_bets_pct": 100 - moneyline_home_bets,
            "away_money_pct": 100 - moneyline_home_money
        },
        "spread": {
            "favorite_bets_pct": spread_favorite_bets,
            "favorite_money_pct": spread_favorite_money,
            "underdog_bets_pct": 100 - spread_favorite_bets,
            "underdog_money_pct": 100 - spread_favorite_money
        },
        "total": {
            "over_bets_pct": total_over_bets,
            "over_money_pct": total_over_money,
            "under_bets_pct": 100 - total_over_bets,
            "under_money_pct": 100 - total_over_money
        }
    }