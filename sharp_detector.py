"""
Enhanced Sharp Betting Detection Module

Detects sharp betting indicators including:
- Reverse Line Movement (RLM)
- Steam Moves
- Handle vs Ticket Split
- Consensus Line Shift
- Public vs Sharp Money patterns

Supports both manual input and automated detection.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json


@dataclass
class LineMovement:
    """Represents line movement data for sharp detection."""
    open_line: float
    current_line: float
    movement_direction: str  # "up" or "down"
    movement_size: float
    timestamp: datetime
    books_moved: List[str]


@dataclass
class PublicBettingData:
    """Public betting percentage data."""
    bets_percentage: float  # % of tickets
    money_percentage: float  # % of handle
    split_difference: float  # money% - bets%
    total_bets: Optional[int] = None
    total_handle: Optional[float] = None


@dataclass
class SharpIndicator:
    """Sharp betting indicator result."""
    flag_type: str  # "RLM", "Steam", "Sharp $", "Consensus"
    strength: int  # 1-3 (1=weak, 2=moderate, 3=strong)
    description: str
    detected_at: datetime
    confidence: float  # 0-1


class SharpDetector:
    """Enhanced sharp betting detection system."""
    
    def __init__(self):
        self.rlm_threshold = 0.5  # Minimum line movement for RLM
        self.steam_threshold = 0.5  # Minimum rapid movement for steam
        self.split_threshold = 10.0  # Minimum % difference for handle/ticket split
        self.consensus_threshold = 3  # Minimum books for consensus
    
    def detect_reverse_line_movement(
        self, 
        line_data: LineMovement, 
        public_data: PublicBettingData
    ) -> Optional[SharpIndicator]:
        """
        Detect Reverse Line Movement - when line moves against public money.
        
        Args:
            line_data: Line movement information
            public_data: Public betting percentages
            
        Returns:
            SharpIndicator if RLM detected, None otherwise
        """
        # Check if line moved significantly
        if abs(line_data.movement_size) < self.rlm_threshold:
            return None
        
        # Determine if movement is against public money
        is_rlm = False
        strength = 1
        
        # If majority public is on one side but line moved the other way
        if public_data.bets_percentage > 60:  # Heavy public action
            if line_data.movement_direction == "up" and public_data.bets_percentage > 50:
                is_rlm = True
            elif line_data.movement_direction == "down" and public_data.bets_percentage < 50:
                is_rlm = True
        
        if not is_rlm:
            return None
        
        # Determine strength based on movement size and public %
        if abs(line_data.movement_size) >= 1.0 and public_data.bets_percentage >= 70:
            strength = 3
        elif abs(line_data.movement_size) >= 0.75 and public_data.bets_percentage >= 65:
            strength = 2
        
        description = f"Line moved {line_data.movement_size:+.1f} against {public_data.bets_percentage:.1f}% public"
        
        return SharpIndicator(
            flag_type="RLM",
            strength=strength,
            description=description,
            detected_at=datetime.now(),
            confidence=min(0.9, strength * 0.3)
        )
    
    def detect_steam_move(
        self, 
        line_movements: List[LineMovement], 
        time_window_minutes: int = 15
    ) -> Optional[SharpIndicator]:
        """
        Detect steam moves - rapid line movement across multiple books.
        
        Args:
            line_movements: List of recent line movements
            time_window_minutes: Time window to check for steam
            
        Returns:
            SharpIndicator if steam detected, None otherwise
        """
        if len(line_movements) < 2:
            return None
        
        # Check for rapid movement across books
        recent_movements = [
            lm for lm in line_movements 
            if (datetime.now() - lm.timestamp).total_seconds() <= time_window_minutes * 60
        ]
        
        if len(recent_movements) < 2:
            return None
        
        # Calculate total movement and books involved
        total_movement = sum(abs(lm.movement_size) for lm in recent_movements)
        unique_books = set()
        for lm in recent_movements:
            unique_books.update(lm.books_moved)
        
        # Steam criteria: >= 0.5 point movement, >= 3 books
        if total_movement >= self.steam_threshold and len(unique_books) >= 3:
            strength = 1
            if total_movement >= 1.0 and len(unique_books) >= 5:
                strength = 3
            elif total_movement >= 0.75 and len(unique_books) >= 4:
                strength = 2
            
            description = f"Steam: {total_movement:.1f}pt move across {len(unique_books)} books"
            
            return SharpIndicator(
                flag_type="Steam",
                strength=strength,
                description=description,
                detected_at=datetime.now(),
                confidence=min(0.9, strength * 0.3)
            )
        
        return None
    
    def detect_sharp_money_split(
        self, 
        public_data: PublicBettingData
    ) -> Optional[SharpIndicator]:
        """
        Detect sharp money through handle vs ticket split.
        
        Args:
            public_data: Public betting data
            
        Returns:
            SharpIndicator if sharp money detected, None otherwise
        """
        # Sharp money indicator: money % significantly higher than bet %
        if public_data.split_difference >= self.split_threshold:
            strength = 1
            if public_data.split_difference >= 20:
                strength = 3
            elif public_data.split_difference >= 15:
                strength = 2
            
            description = f"Sharp $: {public_data.money_percentage:.1f}% handle vs {public_data.bets_percentage:.1f}% tickets"
            
            return SharpIndicator(
                flag_type="Sharp $",
                strength=strength,
                description=description,
                detected_at=datetime.now(),
                confidence=min(0.9, strength * 0.3)
            )
        
        return None
    
    def detect_consensus_shift(
        self, 
        consensus_data: Dict[str, float]
    ) -> Optional[SharpIndicator]:
        """
        Detect consensus line shifts across multiple books.
        
        Args:
            consensus_data: Dict of {book_name: current_line}
            
        Returns:
            SharpIndicator if consensus shift detected, None otherwise
        """
        if len(consensus_data) < self.consensus_threshold:
            return None
        
        lines = list(consensus_data.values())
        line_range = max(lines) - min(lines)
        
        # Strong consensus if all books within tight range
        if line_range <= 0.5:  # Tight consensus
            avg_line = sum(lines) / len(lines)
            strength = 2 if len(consensus_data) >= 5 else 1
            
            description = f"Consensus: {len(consensus_data)} books at {avg_line:.1f} ±{line_range:.1f}"
            
            return SharpIndicator(
                flag_type="Consensus",
                strength=strength,
                description=description,
                detected_at=datetime.now(),
                confidence=0.6
            )
        
        return None
    
    def analyze_manual_input(
        self, 
        manual_data: Dict[str, Any]
    ) -> List[SharpIndicator]:
        """
        Analyze manually input betting data for sharp indicators.
        
        Args:
            manual_data: Dict containing manual input data
            
        Returns:
            List of detected sharp indicators
        """
        indicators = []
        
        # Parse manual input
        if "line_movement" in manual_data:
            line_info = manual_data["line_movement"]
            line_movement = LineMovement(
                open_line=line_info.get("open", 0),
                current_line=line_info.get("current", 0),
                movement_direction="up" if line_info.get("current", 0) > line_info.get("open", 0) else "down",
                movement_size=abs(line_info.get("current", 0) - line_info.get("open", 0)),
                timestamp=datetime.now(),
                books_moved=line_info.get("books", [])
            )
            
            if "public_data" in manual_data:
                public_info = manual_data["public_data"]
                public_data = PublicBettingData(
                    bets_percentage=public_info.get("bets_pct", 50),
                    money_percentage=public_info.get("money_pct", 50),
                    split_difference=public_info.get("money_pct", 50) - public_info.get("bets_pct", 50)
                )
                
                # Check for RLM
                rlm_indicator = self.detect_reverse_line_movement(line_movement, public_data)
                if rlm_indicator:
                    indicators.append(rlm_indicator)
                
                # Check for sharp money split
                sharp_money_indicator = self.detect_sharp_money_split(public_data)
                if sharp_money_indicator:
                    indicators.append(sharp_money_indicator)
        
        # Check for steam if multiple movements provided
        if "steam_data" in manual_data:
            steam_info = manual_data["steam_data"]
            movements = []
            for movement in steam_info:
                movements.append(LineMovement(
                    open_line=movement.get("from", 0),
                    current_line=movement.get("to", 0),
                    movement_direction="up" if movement.get("to", 0) > movement.get("from", 0) else "down",
                    movement_size=abs(movement.get("to", 0) - movement.get("from", 0)),
                    timestamp=datetime.now(),
                    books_moved=movement.get("books", [])
                ))
            
            steam_indicator = self.detect_steam_move(movements)
            if steam_indicator:
                indicators.append(steam_indicator)
        
        return indicators
    
    def get_flag_emojis(self, indicators: List[SharpIndicator]) -> Dict[str, str]:
        """
        Get emoji flags for display.
        
        Args:
            indicators: List of sharp indicators
            
        Returns:
            Dict mapping flag types to emojis
        """
        flag_map = {
            "RLM": "📉",
            "Steam": "🔥", 
            "Sharp $": "💸",
            "Consensus": "⚖️"
        }
        
        result = {}
        for indicator in indicators:
            if indicator.flag_type in flag_map:
                result[indicator.flag_type] = flag_map[indicator.flag_type]
        
        return result
    
    def calculate_sharp_score(self, indicators: List[SharpIndicator]) -> float:
        """
        Calculate overall sharp score from indicators.
        
        Args:
            indicators: List of sharp indicators
            
        Returns:
            Sharp score (0-10)
        """
        if not indicators:
            return 0.0
        
        # Weight by strength and confidence
        total_score = 0.0
        for indicator in indicators:
            weighted_score = indicator.strength * indicator.confidence * 2
            total_score += weighted_score
        
        return min(10.0, total_score)


# Example usage functions for manual input
def create_manual_rlm_input(
    open_line: float,
    current_line: float, 
    public_bets_pct: float,
    public_money_pct: float
) -> Dict[str, Any]:
    """Helper to create manual RLM input data."""
    return {
        "line_movement": {
            "open": open_line,
            "current": current_line,
            "books": ["DraftKings", "FanDuel", "BetMGM"]
        },
        "public_data": {
            "bets_pct": public_bets_pct,
            "money_pct": public_money_pct
        }
    }


def create_manual_steam_input(movements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Helper to create manual steam input data."""
    return {
        "steam_data": movements
    }