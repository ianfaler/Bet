"""
Fair Value Calculator

Calculates fair odds from model probabilities and compares to market odds
to determine betting edge and value opportunities.

Supports:
- Model probability input (manual or automated)
- Fair odds calculation
- Edge calculation vs market
- No-vig probability calculation
- Multiple bet types (ML, spread, totals)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import math


@dataclass
class ModelProbability:
    """Model probability for a specific outcome."""
    outcome: str  # e.g., "home_win", "away_win", "over", "under"
    probability: float  # 0-1
    confidence: float  # 0-1, confidence in the model
    model_name: str = "Manual"
    timestamp: Optional[str] = None


@dataclass
class MarketOdds:
    """Market odds from sportsbooks."""
    outcome: str
    american_odds: int  # e.g., -110, +150
    decimal_odds: float
    implied_probability: float
    book: str
    timestamp: Optional[str] = None


@dataclass
class FairValueResult:
    """Result of fair value calculation."""
    outcome: str
    model_probability: float
    fair_american_odds: int
    fair_decimal_odds: float
    market_odds: MarketOdds
    edge_percentage: float
    edge_description: str
    is_positive_ev: bool
    value_rating: str  # "Excellent", "Good", "Fair", "Poor"


class FairValueCalculator:
    """Calculate fair values and betting edges."""
    
    def __init__(self):
        self.min_edge_threshold = 3.0  # Minimum edge % to consider
        self.excellent_edge_threshold = 10.0
        self.good_edge_threshold = 6.0
        self.fair_edge_threshold = 3.0
    
    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal odds."""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American odds."""
        if decimal_odds >= 2.0:
            return round((decimal_odds - 1) * 100)
        else:
            return round(-100 / (decimal_odds - 1))
    
    def probability_to_american_odds(self, probability: float) -> int:
        """Convert probability to American odds."""
        if probability <= 0 or probability >= 1:
            raise ValueError("Probability must be between 0 and 1")
        
        decimal_odds = 1 / probability
        return self.decimal_to_american(decimal_odds)
    
    def american_odds_to_probability(self, american_odds: int) -> float:
        """Convert American odds to implied probability."""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def remove_vig(self, odds_list: List[int]) -> List[float]:
        """
        Remove vig from a set of odds to get true probabilities.
        
        Args:
            odds_list: List of American odds for all outcomes
            
        Returns:
            List of no-vig probabilities
        """
        # Convert to implied probabilities
        implied_probs = [self.american_odds_to_probability(odds) for odds in odds_list]
        
        # Calculate overround (vig)
        total_prob = sum(implied_probs)
        
        if total_prob <= 1.0:
            return implied_probs  # No vig detected
        
        # Remove vig proportionally
        no_vig_probs = [prob / total_prob for prob in implied_probs]
        
        return no_vig_probs
    
    def calculate_fair_value(
        self, 
        model_prob: ModelProbability, 
        market_odds: MarketOdds
    ) -> FairValueResult:
        """
        Calculate fair value and edge for a specific bet.
        
        Args:
            model_prob: Model probability for the outcome
            market_odds: Market odds for the outcome
            
        Returns:
            FairValueResult with calculated edge and value
        """
        # Calculate fair odds from model probability
        fair_american = self.probability_to_american_odds(model_prob.probability)
        fair_decimal = self.american_to_decimal(fair_american)
        
        # Calculate edge
        market_implied_prob = market_odds.implied_probability
        edge_percentage = ((model_prob.probability - market_implied_prob) / market_implied_prob) * 100
        
        # Determine if positive EV
        is_positive_ev = edge_percentage > 0
        
        # Create edge description
        if edge_percentage > 0:
            edge_description = f"+{edge_percentage:.1f}% edge (Model: {model_prob.probability:.1%}, Market: {market_implied_prob:.1%})"
        else:
            edge_description = f"{edge_percentage:.1f}% edge (Overvalued by market)"
        
        # Determine value rating
        if edge_percentage >= self.excellent_edge_threshold:
            value_rating = "Excellent"
        elif edge_percentage >= self.good_edge_threshold:
            value_rating = "Good"
        elif edge_percentage >= self.fair_edge_threshold:
            value_rating = "Fair"
        else:
            value_rating = "Poor"
        
        return FairValueResult(
            outcome=model_prob.outcome,
            model_probability=model_prob.probability,
            fair_american_odds=fair_american,
            fair_decimal_odds=fair_decimal,
            market_odds=market_odds,
            edge_percentage=edge_percentage,
            edge_description=edge_description,
            is_positive_ev=is_positive_ev,
            value_rating=value_rating
        )
    
    def calculate_moneyline_fair_value(
        self, 
        home_prob: float, 
        away_prob: float,
        home_odds: int, 
        away_odds: int,
        home_book: str = "Manual",
        away_book: str = "Manual"
    ) -> Tuple[FairValueResult, FairValueResult]:
        """
        Calculate fair value for both sides of a moneyline bet.
        
        Args:
            home_prob: Model probability for home team
            away_prob: Model probability for away team  
            home_odds: Market odds for home team
            away_odds: Market odds for away team
            home_book: Sportsbook for home odds
            away_book: Sportsbook for away odds
            
        Returns:
            Tuple of (home_result, away_result)
        """
        # Normalize probabilities to sum to 1
        total_prob = home_prob + away_prob
        if total_prob != 1.0:
            home_prob = home_prob / total_prob
            away_prob = away_prob / total_prob
        
        # Create model probability objects
        home_model_prob = ModelProbability(
            outcome="home_win",
            probability=home_prob,
            confidence=0.8  # Default confidence
        )
        
        away_model_prob = ModelProbability(
            outcome="away_win", 
            probability=away_prob,
            confidence=0.8
        )
        
        # Create market odds objects
        home_market_odds = MarketOdds(
            outcome="home_win",
            american_odds=home_odds,
            decimal_odds=self.american_to_decimal(home_odds),
            implied_probability=self.american_odds_to_probability(home_odds),
            book=home_book
        )
        
        away_market_odds = MarketOdds(
            outcome="away_win",
            american_odds=away_odds,
            decimal_odds=self.american_to_decimal(away_odds),
            implied_probability=self.american_odds_to_probability(away_odds),
            book=away_book
        )
        
        # Calculate fair values
        home_result = self.calculate_fair_value(home_model_prob, home_market_odds)
        away_result = self.calculate_fair_value(away_model_prob, away_market_odds)
        
        return home_result, away_result
    
    def calculate_spread_fair_value(
        self, 
        favorite_prob: float,
        underdog_prob: float,
        spread_line: float,
        favorite_odds: int = -110,
        underdog_odds: int = -110,
        book: str = "Manual"
    ) -> Tuple[FairValueResult, FairValueResult]:
        """
        Calculate fair value for spread bets.
        
        Args:
            favorite_prob: Model probability for favorite covering
            underdog_prob: Model probability for underdog covering
            spread_line: The spread (e.g., -3.5)
            favorite_odds: Odds for favorite covering
            underdog_odds: Odds for underdog covering
            book: Sportsbook name
            
        Returns:
            Tuple of (favorite_result, underdog_result)
        """
        # Normalize probabilities
        total_prob = favorite_prob + underdog_prob
        if total_prob != 1.0:
            favorite_prob = favorite_prob / total_prob
            underdog_prob = underdog_prob / total_prob
        
        # Create model probabilities
        favorite_model_prob = ModelProbability(
            outcome=f"favorite_{spread_line}",
            probability=favorite_prob,
            confidence=0.8
        )
        
        underdog_model_prob = ModelProbability(
            outcome=f"underdog_+{abs(spread_line)}",
            probability=underdog_prob,
            confidence=0.8
        )
        
        # Create market odds
        favorite_market_odds = MarketOdds(
            outcome=f"favorite_{spread_line}",
            american_odds=favorite_odds,
            decimal_odds=self.american_to_decimal(favorite_odds),
            implied_probability=self.american_odds_to_probability(favorite_odds),
            book=book
        )
        
        underdog_market_odds = MarketOdds(
            outcome=f"underdog_+{abs(spread_line)}",
            american_odds=underdog_odds,
            decimal_odds=self.american_to_decimal(underdog_odds),
            implied_probability=self.american_odds_to_probability(underdog_odds),
            book=book
        )
        
        # Calculate fair values
        favorite_result = self.calculate_fair_value(favorite_model_prob, favorite_market_odds)
        underdog_result = self.calculate_fair_value(underdog_model_prob, underdog_market_odds)
        
        return favorite_result, underdog_result
    
    def calculate_total_fair_value(
        self, 
        over_prob: float,
        under_prob: float, 
        total_line: float,
        over_odds: int = -110,
        under_odds: int = -110,
        book: str = "Manual"
    ) -> Tuple[FairValueResult, FairValueResult]:
        """
        Calculate fair value for totals (over/under) bets.
        
        Args:
            over_prob: Model probability for over
            under_prob: Model probability for under
            total_line: The total line (e.g., 8.5)
            over_odds: Odds for over
            under_odds: Odds for under
            book: Sportsbook name
            
        Returns:
            Tuple of (over_result, under_result)
        """
        # Normalize probabilities
        total_prob = over_prob + under_prob
        if total_prob != 1.0:
            over_prob = over_prob / total_prob
            under_prob = under_prob / total_prob
        
        # Create model probabilities
        over_model_prob = ModelProbability(
            outcome=f"over_{total_line}",
            probability=over_prob,
            confidence=0.8
        )
        
        under_model_prob = ModelProbability(
            outcome=f"under_{total_line}",
            probability=under_prob,
            confidence=0.8
        )
        
        # Create market odds
        over_market_odds = MarketOdds(
            outcome=f"over_{total_line}",
            american_odds=over_odds,
            decimal_odds=self.american_to_decimal(over_odds),
            implied_probability=self.american_odds_to_probability(over_odds),
            book=book
        )
        
        under_market_odds = MarketOdds(
            outcome=f"under_{total_line}",
            american_odds=under_odds,
            decimal_odds=self.american_to_decimal(under_odds),
            implied_probability=self.american_odds_to_probability(under_odds),
            book=book
        )
        
        # Calculate fair values
        over_result = self.calculate_fair_value(over_model_prob, over_market_odds)
        under_result = self.calculate_fair_value(under_model_prob, under_market_odds)
        
        return over_result, under_result
    
    def analyze_manual_input(self, manual_data: Dict[str, Any]) -> List[FairValueResult]:
        """
        Analyze manually input fair value data.
        
        Args:
            manual_data: Dict containing manual input data
            
        Returns:
            List of fair value results
        """
        results = []
        
        if "moneyline" in manual_data:
            ml_data = manual_data["moneyline"]
            home_result, away_result = self.calculate_moneyline_fair_value(
                home_prob=ml_data.get("home_prob", 0.5),
                away_prob=ml_data.get("away_prob", 0.5),
                home_odds=ml_data.get("home_odds", -110),
                away_odds=ml_data.get("away_odds", -110),
                home_book=ml_data.get("book", "Manual"),
                away_book=ml_data.get("book", "Manual")
            )
            results.extend([home_result, away_result])
        
        if "spread" in manual_data:
            spread_data = manual_data["spread"]
            fav_result, dog_result = self.calculate_spread_fair_value(
                favorite_prob=spread_data.get("favorite_prob", 0.5),
                underdog_prob=spread_data.get("underdog_prob", 0.5),
                spread_line=spread_data.get("line", -3.5),
                favorite_odds=spread_data.get("favorite_odds", -110),
                underdog_odds=spread_data.get("underdog_odds", -110),
                book=spread_data.get("book", "Manual")
            )
            results.extend([fav_result, dog_result])
        
        if "total" in manual_data:
            total_data = manual_data["total"]
            over_result, under_result = self.calculate_total_fair_value(
                over_prob=total_data.get("over_prob", 0.5),
                under_prob=total_data.get("under_prob", 0.5),
                total_line=total_data.get("line", 8.5),
                over_odds=total_data.get("over_odds", -110),
                under_odds=total_data.get("under_odds", -110),
                book=total_data.get("book", "Manual")
            )
            results.extend([over_result, under_result])
        
        return results
    
    def get_best_value_bets(
        self, 
        results: List[FairValueResult], 
        min_edge: float = None
    ) -> List[FairValueResult]:
        """
        Filter and sort results to show best value bets.
        
        Args:
            results: List of fair value results
            min_edge: Minimum edge threshold (uses class default if None)
            
        Returns:
            Sorted list of positive EV bets
        """
        if min_edge is None:
            min_edge = self.min_edge_threshold
        
        # Filter for positive EV bets above threshold
        value_bets = [
            result for result in results 
            if result.is_positive_ev and result.edge_percentage >= min_edge
        ]
        
        # Sort by edge percentage (highest first)
        value_bets.sort(key=lambda x: x.edge_percentage, reverse=True)
        
        return value_bets


# Helper functions for manual input
def create_manual_moneyline_input(
    home_prob: float,
    away_prob: float,
    home_odds: int,
    away_odds: int,
    book: str = "Manual"
) -> Dict[str, Any]:
    """Helper to create manual moneyline input."""
    return {
        "moneyline": {
            "home_prob": home_prob,
            "away_prob": away_prob,
            "home_odds": home_odds,
            "away_odds": away_odds,
            "book": book
        }
    }


def create_manual_spread_input(
    favorite_prob: float,
    underdog_prob: float,
    spread_line: float,
    favorite_odds: int = -110,
    underdog_odds: int = -110,
    book: str = "Manual"
) -> Dict[str, Any]:
    """Helper to create manual spread input."""
    return {
        "spread": {
            "favorite_prob": favorite_prob,
            "underdog_prob": underdog_prob,
            "line": spread_line,
            "favorite_odds": favorite_odds,
            "underdog_odds": underdog_odds,
            "book": book
        }
    }


def create_manual_total_input(
    over_prob: float,
    under_prob: float,
    total_line: float,
    over_odds: int = -110,
    under_odds: int = -110,
    book: str = "Manual"
) -> Dict[str, Any]:
    """Helper to create manual total input."""
    return {
        "total": {
            "over_prob": over_prob,
            "under_prob": under_prob,
            "line": total_line,
            "over_odds": over_odds,
            "under_odds": under_odds,
            "book": book
        }
    }