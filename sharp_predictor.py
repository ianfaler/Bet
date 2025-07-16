"""
Sharp Betting Predictor - Main Analysis Engine

Integrates all components to identify sharp betting opportunities:
- Sharp detection (RLM, Steam, Sharp Money, Consensus)
- Fair value calculation
- EV analysis with risk factors
- Confidence scoring (1-10)
- Comprehensive output for UI display

This is the main coordinator that brings together all the individual modules.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
import logging

# Import our custom modules
from sharp_detector import SharpDetector, SharpIndicator
from fair_value_calculator import FairValueCalculator, FairValueResult
from ev_engine import EVEngine, EVCalculation, RiskFactor
from confidence_scorer import ConfidenceScorer, ConfidenceBreakdown, ConfidenceInput
from data_input_manager import DataInputManager, GameData


@dataclass
class BettingOpportunity:
    """Complete betting opportunity analysis."""
    game_id: str
    sport: str
    matchup: str
    bet_type: str
    bet_side: str
    market_odds: int
    fair_odds: int
    edge_percentage: float
    expected_value: float
    recommended_stake: float
    confidence_score: int
    confidence_tier: str
    sharp_flags: List[str]
    flag_emojis: str
    value_rating: str
    rationale: str
    key_factors: List[str]
    best_book: str
    timestamp: datetime
    risk_factors: List[str]
    ev_calculation: EVCalculation
    fair_value_result: FairValueResult
    confidence_breakdown: ConfidenceBreakdown
    sharp_indicators: List[SharpIndicator]


@dataclass
class SharpPredictorResults:
    """Complete results from sharp predictor analysis."""
    timestamp: datetime
    total_opportunities: int
    qualified_opportunities: int
    high_confidence_count: int
    best_opportunities: List[BettingOpportunity]
    summary_stats: Dict[str, Any]
    execution_time: float
    filters_applied: Dict[str, Any]


class SharpPredictor:
    """Main Sharp Betting Predictor system."""
    
    def __init__(self, bankroll: float = 10000.0, min_ev: float = 3.0, min_confidence: int = 7):
        # Initialize all components
        self.sharp_detector = SharpDetector()
        self.fair_value_calculator = FairValueCalculator()
        self.ev_engine = EVEngine(bankroll=bankroll)
        self.confidence_scorer = ConfidenceScorer()
        self.data_manager = DataInputManager()
        
        # Configuration
        self.bankroll = bankroll
        self.min_ev_threshold = min_ev
        self.min_confidence_threshold = min_confidence
        self.max_opportunities = 50  # Limit output size
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def analyze_game(
        self, 
        game_data: GameData, 
        model_predictions: Optional[Dict[str, Any]] = None
    ) -> List[BettingOpportunity]:
        """
        Analyze a single game for betting opportunities.
        
        Args:
            game_data: Game data to analyze
            model_predictions: Optional model predictions
            
        Returns:
            List of betting opportunities
        """
        opportunities = []
        
        try:
            # Extract betting lines and public data
            odds_data = game_data.odds_data
            public_data = game_data.public_betting_data
            line_movements = game_data.line_movement_data
            
            # Use provided model predictions or fallback to game data
            predictions = model_predictions or game_data.model_predictions or {}
            
            # Analyze each bet type
            for bet_type in ["moneyline", "spread", "total"]:
                if bet_type in odds_data:
                    bet_opportunities = self._analyze_bet_type(
                        game_data, bet_type, odds_data[bet_type], 
                        public_data.get(bet_type, {}), line_movements, predictions
                    )
                    opportunities.extend(bet_opportunities)
            
        except Exception as e:
            self.logger.error(f"Error analyzing game {game_data.game_id}: {str(e)}")
        
        return opportunities
    
    def _analyze_bet_type(
        self,
        game_data: GameData,
        bet_type: str,
        odds_info: Dict[str, Any],
        public_info: Dict[str, Any],
        line_movements: List[Dict[str, Any]],
        predictions: Dict[str, Any]
    ) -> List[BettingOpportunity]:
        """Analyze a specific bet type for opportunities."""
        opportunities = []
        
        # Get sides to analyze based on bet type
        if bet_type == "moneyline":
            sides = [("home", "home"), ("away", "away")]
        elif bet_type == "spread":
            sides = [("favorite", "home"), ("underdog", "away")]  # Simplified mapping
        elif bet_type == "total":
            sides = [("over", "over"), ("under", "under")]
        else:
            return opportunities
        
        for side_key, side_display in sides:
            try:
                opportunity = self._create_betting_opportunity(
                    game_data, bet_type, side_key, side_display,
                    odds_info, public_info, line_movements, predictions
                )
                
                if opportunity and self._passes_filters(opportunity):
                    opportunities.append(opportunity)
                    
            except Exception as e:
                self.logger.error(f"Error analyzing {bet_type} {side_key}: {str(e)}")
        
        return opportunities
    
    def _create_betting_opportunity(
        self,
        game_data: GameData,
        bet_type: str,
        side_key: str,
        side_display: str,
        odds_info: Dict[str, Any],
        public_info: Dict[str, Any],
        line_movements: List[Dict[str, Any]],
        predictions: Dict[str, Any]
    ) -> Optional[BettingOpportunity]:
        """Create a complete betting opportunity analysis."""
        
        # Get market odds
        market_odds = self._extract_odds(odds_info, side_key)
        if market_odds is None:
            return None
        
        # Get model probability
        model_prob = self._extract_model_probability(predictions, bet_type, side_key)
        if model_prob is None:
            model_prob = 0.5  # Default if no model prediction
        
        # 1. Sharp Detection
        sharp_data = self._prepare_sharp_detection_data(
            game_data, bet_type, side_key, odds_info, public_info, line_movements
        )
        sharp_indicators = self.sharp_detector.analyze_manual_input(sharp_data)
        
        # 2. Fair Value Calculation
        fair_value_data = self._prepare_fair_value_data(
            bet_type, model_prob, market_odds, odds_info
        )
        fair_value_results = self.fair_value_calculator.analyze_manual_input(fair_value_data)
        fair_value_result = fair_value_results[0] if fair_value_results else None
        
        if fair_value_result is None:
            return None
        
        # 3. EV Calculation
        risk_factors = self._identify_risk_factors(game_data, predictions)
        ev_data = self._prepare_ev_data(model_prob, market_odds, 100, risk_factors)  # $100 base stake
        ev_calculations = self.ev_engine.analyze_manual_input(ev_data)
        ev_calculation = ev_calculations[0] if ev_calculations else None
        
        if ev_calculation is None:
            return None
        
        # 4. Confidence Scoring
        confidence_data = self._prepare_confidence_data(
            sharp_indicators, fair_value_result.edge_percentage, 
            model_prob, game_data, risk_factors
        )
        confidence_breakdown = self.confidence_scorer.analyze_manual_input(confidence_data)
        
        # 5. Create comprehensive opportunity
        opportunity = BettingOpportunity(
            game_id=game_data.game_id,
            sport=game_data.sport,
            matchup=f"{game_data.away_team} @ {game_data.home_team}",
            bet_type=bet_type.title(),
            bet_side=side_display.title(),
            market_odds=market_odds,
            fair_odds=fair_value_result.fair_american_odds,
            edge_percentage=fair_value_result.edge_percentage,
            expected_value=ev_calculation.expected_value,
            recommended_stake=ev_calculation.recommended_stake,
            confidence_score=confidence_breakdown.final_score,
            confidence_tier=self._get_confidence_tier(confidence_breakdown.final_score),
            sharp_flags=[ind.flag_type for ind in sharp_indicators],
            flag_emojis=self._get_flag_emojis(sharp_indicators),
            value_rating=fair_value_result.value_rating,
            rationale=self._generate_rationale(
                fair_value_result, ev_calculation, confidence_breakdown, sharp_indicators
            ),
            key_factors=confidence_breakdown.key_factors,
            best_book=odds_info.get("book", "Manual"),
            timestamp=datetime.now(),
            risk_factors=[rf["description"] for rf in risk_factors] if risk_factors else [],
            ev_calculation=ev_calculation,
            fair_value_result=fair_value_result,
            confidence_breakdown=confidence_breakdown,
            sharp_indicators=sharp_indicators
        )
        
        return opportunity
    
    def _extract_odds(self, odds_info: Dict[str, Any], side_key: str) -> Optional[int]:
        """Extract odds for a specific side."""
        if side_key == "home":
            return odds_info.get("home")
        elif side_key == "away":
            return odds_info.get("away")
        elif side_key == "favorite":
            return odds_info.get("home_odds", odds_info.get("favorite_odds", -110))
        elif side_key == "underdog":
            return odds_info.get("away_odds", odds_info.get("underdog_odds", -110))
        elif side_key == "over":
            return odds_info.get("over_odds", -110)
        elif side_key == "under":
            return odds_info.get("under_odds", -110)
        return None
    
    def _extract_model_probability(
        self, 
        predictions: Dict[str, Any], 
        bet_type: str, 
        side_key: str
    ) -> Optional[float]:
        """Extract model probability for a specific outcome."""
        if not predictions:
            return None
        
        prob_key = f"{bet_type}_{side_key}_prob"
        if prob_key in predictions:
            return predictions[prob_key]
        
        # Fallback patterns
        if bet_type == "moneyline":
            if side_key == "home":
                return predictions.get("home_win_prob", 0.5)
            elif side_key == "away":
                return predictions.get("away_win_prob", 0.5)
        
        return None
    
    def _prepare_sharp_detection_data(
        self,
        game_data: GameData,
        bet_type: str,
        side_key: str,
        odds_info: Dict[str, Any],
        public_info: Dict[str, Any],
        line_movements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare data for sharp detection analysis."""
        
        # Find relevant line movements
        relevant_movements = [
            lm for lm in line_movements 
            if lm.get("bet_type", "").lower() == bet_type.lower()
        ]
        
        sharp_data = {}
        
        # Line movement data
        if "line" in odds_info and len(relevant_movements) > 0:
            # Use the first movement as example
            movement = relevant_movements[0]
            sharp_data["line_movement"] = {
                "open": movement.get("from_line", 0),
                "current": movement.get("to_line", 0),
                "books": [movement.get("book", "Unknown")]
            }
        
        # Public betting data
        if public_info:
            bets_pct = public_info.get(f"{side_key}_bets_pct", 50)
            money_pct = public_info.get(f"{side_key}_money_pct", 50)
            
            sharp_data["public_data"] = {
                "bets_pct": bets_pct,
                "money_pct": money_pct
            }
        
        # Steam data if multiple movements
        if len(relevant_movements) > 1:
            sharp_data["steam_data"] = [
                {
                    "from": movement.get("from_line", 0),
                    "to": movement.get("to_line", 0),
                    "books": [movement.get("book", "Unknown")]
                }
                for movement in relevant_movements[:3]  # Limit to first 3
            ]
        
        return sharp_data
    
    def _prepare_fair_value_data(
        self,
        bet_type: str,
        model_prob: float,
        market_odds: int,
        odds_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare data for fair value calculation."""
        
        if bet_type == "moneyline":
            return {
                "moneyline": {
                    "home_prob": model_prob,
                    "away_prob": 1 - model_prob,
                    "home_odds": market_odds if "home" in str(odds_info) else -110,
                    "away_odds": -110,  # Simplified
                    "book": odds_info.get("book", "Manual")
                }
            }
        elif bet_type == "spread":
            return {
                "spread": {
                    "favorite_prob": model_prob,
                    "underdog_prob": 1 - model_prob,
                    "line": odds_info.get("line", -3.5),
                    "favorite_odds": market_odds,
                    "underdog_odds": -110,
                    "book": odds_info.get("book", "Manual")
                }
            }
        elif bet_type == "total":
            return {
                "total": {
                    "over_prob": model_prob,
                    "under_prob": 1 - model_prob,
                    "line": odds_info.get("line", 8.5),
                    "over_odds": market_odds,
                    "under_odds": -110,
                    "book": odds_info.get("book", "Manual")
                }
            }
        
        return {}
    
    def _prepare_ev_data(
        self,
        model_prob: float,
        market_odds: int,
        stake: float,
        risk_factors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare data for EV calculation."""
        return {
            "single_bet": {
                "win_probability": model_prob,
                "odds": market_odds,
                "stake": stake,
                "risk_factors": risk_factors
            }
        }
    
    def _prepare_confidence_data(
        self,
        sharp_indicators: List[SharpIndicator],
        edge_percentage: float,
        model_prob: float,
        game_data: GameData,
        risk_factors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare data for confidence scoring."""
        
        # Extract volatility factors
        volatility_factors = []
        if risk_factors:
            volatility_factors = [rf.get("type", "unknown") for rf in risk_factors]
        
        return {
            "sharp_indicators": [ind.flag_type for ind in sharp_indicators],
            "ev_percentage": edge_percentage,
            "model_confidence": 0.8,  # Default model confidence
            "market_stability": 0.8,  # Default market stability
            "data_quality": 0.8,     # Default data quality
            "volatility_factors": volatility_factors
        }
    
    def _identify_risk_factors(
        self, 
        game_data: GameData, 
        predictions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify risk factors for the game."""
        risk_factors = []
        
        # Check metadata for risk indicators
        metadata = game_data.metadata or {}
        
        if "weather" in metadata:
            weather = metadata["weather"]
            if weather.get("condition") in ["rain", "snow", "wind"]:
                risk_factors.append({
                    "type": "weather",
                    "impact": -0.1,  # 10% negative impact
                    "description": f"Weather: {weather.get('condition', 'adverse')}",
                    "confidence": 0.8
                })
        
        if "injuries" in metadata:
            injuries = metadata["injuries"]
            if injuries.get("key_players"):
                risk_factors.append({
                    "type": "injury",
                    "impact": -0.15,  # 15% negative impact
                    "description": f"Key injuries: {injuries.get('count', 'multiple')}",
                    "confidence": 0.9
                })
        
        # Check for high variance games
        if predictions and "variance" in predictions:
            if predictions["variance"] > 0.2:
                risk_factors.append({
                    "type": "variance",
                    "impact": -0.05,
                    "description": "High variance matchup",
                    "confidence": 0.7
                })
        
        return risk_factors
    
    def _passes_filters(self, opportunity: BettingOpportunity) -> bool:
        """Check if opportunity passes minimum thresholds."""
        return (
            opportunity.edge_percentage >= self.min_ev_threshold and
            opportunity.confidence_score >= self.min_confidence_threshold
        )
    
    def _get_confidence_tier(self, confidence_score: int) -> str:
        """Get confidence tier description."""
        if confidence_score >= 9:
            return "Exceptional"
        elif confidence_score >= 8:
            return "High"
        elif confidence_score >= 7:
            return "Good"
        elif confidence_score >= 6:
            return "Fair"
        else:
            return "Low"
    
    def _get_flag_emojis(self, sharp_indicators: List[SharpIndicator]) -> str:
        """Get emoji flags for sharp indicators."""
        emoji_map = {
            "RLM": "📉",
            "Steam": "🔥",
            "Sharp $": "💸",
            "Consensus": "⚖️"
        }
        
        emojis = []
        for indicator in sharp_indicators:
            if indicator.flag_type in emoji_map:
                emojis.append(emoji_map[indicator.flag_type])
        
        return " ".join(emojis)
    
    def _generate_rationale(
        self,
        fair_value: FairValueResult,
        ev_calc: EVCalculation,
        confidence: ConfidenceBreakdown,
        sharp_indicators: List[SharpIndicator]
    ) -> str:
        """Generate human-readable rationale for the opportunity."""
        
        rationale_parts = []
        
        # Edge description
        if fair_value.edge_percentage >= 10:
            rationale_parts.append(f"Excellent {fair_value.edge_percentage:.1f}% edge")
        elif fair_value.edge_percentage >= 6:
            rationale_parts.append(f"Good {fair_value.edge_percentage:.1f}% edge")
        else:
            rationale_parts.append(f"Fair {fair_value.edge_percentage:.1f}% edge")
        
        # Sharp indicators
        if sharp_indicators:
            sharp_types = [ind.flag_type for ind in sharp_indicators]
            rationale_parts.append(f"Sharp signals: {', '.join(sharp_types)}")
        
        # Confidence factors
        if confidence.final_score >= 8:
            rationale_parts.append("High confidence setup")
        
        # Model vs market
        model_prob = fair_value.model_probability * 100
        market_prob = fair_value.market_odds.implied_probability * 100
        rationale_parts.append(f"Model {model_prob:.0f}% vs Market {market_prob:.0f}%")
        
        return " | ".join(rationale_parts)
    
    def analyze_multiple_games(
        self, 
        games: List[GameData],
        model_predictions: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> SharpPredictorResults:
        """
        Analyze multiple games for betting opportunities.
        
        Args:
            games: List of games to analyze
            model_predictions: Optional dict of {game_id: predictions}
            
        Returns:
            SharpPredictorResults with comprehensive analysis
        """
        start_time = datetime.now()
        all_opportunities = []
        
        for game in games:
            game_predictions = None
            if model_predictions and game.game_id in model_predictions:
                game_predictions = model_predictions[game.game_id]
            
            opportunities = self.analyze_game(game, game_predictions)
            all_opportunities.extend(opportunities)
        
        # Filter and sort opportunities
        qualified_opportunities = [
            opp for opp in all_opportunities 
            if self._passes_filters(opp)
        ]
        
        # Sort by combination of edge and confidence
        qualified_opportunities.sort(
            key=lambda x: (x.edge_percentage * x.confidence_score / 10), 
            reverse=True
        )
        
        # Limit results
        best_opportunities = qualified_opportunities[:self.max_opportunities]
        
        # Calculate summary stats
        execution_time = (datetime.now() - start_time).total_seconds()
        
        summary_stats = self._calculate_summary_stats(all_opportunities, qualified_opportunities)
        
        filters_applied = {
            "min_ev_threshold": self.min_ev_threshold,
            "min_confidence_threshold": self.min_confidence_threshold,
            "max_opportunities": self.max_opportunities
        }
        
        return SharpPredictorResults(
            timestamp=start_time,
            total_opportunities=len(all_opportunities),
            qualified_opportunities=len(qualified_opportunities),
            high_confidence_count=len([o for o in qualified_opportunities if o.confidence_score >= 8]),
            best_opportunities=best_opportunities,
            summary_stats=summary_stats,
            execution_time=execution_time,
            filters_applied=filters_applied
        )
    
    def _calculate_summary_stats(
        self, 
        all_opportunities: List[BettingOpportunity],
        qualified_opportunities: List[BettingOpportunity]
    ) -> Dict[str, Any]:
        """Calculate summary statistics."""
        
        if not qualified_opportunities:
            return {
                "avg_edge": 0.0,
                "avg_confidence": 0.0,
                "total_recommended_stake": 0.0,
                "bankroll_utilization": 0.0,
                "sharp_flag_distribution": {},
                "sport_distribution": {},
                "value_rating_distribution": {}
            }
        
        # Calculate averages
        avg_edge = sum(o.edge_percentage for o in qualified_opportunities) / len(qualified_opportunities)
        avg_confidence = sum(o.confidence_score for o in qualified_opportunities) / len(qualified_opportunities)
        total_stake = sum(o.recommended_stake for o in qualified_opportunities)
        bankroll_utilization = (total_stake / self.bankroll) * 100
        
        # Distributions
        sharp_flags = {}
        sports = {}
        value_ratings = {}
        
        for opp in qualified_opportunities:
            # Sharp flags
            for flag in opp.sharp_flags:
                sharp_flags[flag] = sharp_flags.get(flag, 0) + 1
            
            # Sports
            sports[opp.sport] = sports.get(opp.sport, 0) + 1
            
            # Value ratings
            value_ratings[opp.value_rating] = value_ratings.get(opp.value_rating, 0) + 1
        
        return {
            "avg_edge": avg_edge,
            "avg_confidence": avg_confidence,
            "total_recommended_stake": total_stake,
            "bankroll_utilization": bankroll_utilization,
            "sharp_flag_distribution": sharp_flags,
            "sport_distribution": sports,
            "value_rating_distribution": value_ratings
        }
    
    def to_json(self, results: SharpPredictorResults) -> str:
        """Convert results to JSON for API/UI consumption."""
        # Convert to serializable format
        serializable_results = {
            "timestamp": results.timestamp.isoformat(),
            "total_opportunities": results.total_opportunities,
            "qualified_opportunities": results.qualified_opportunities,
            "high_confidence_count": results.high_confidence_count,
            "execution_time": results.execution_time,
            "filters_applied": results.filters_applied,
            "summary_stats": results.summary_stats,
            "opportunities": []
        }
        
        # Convert opportunities
        for opp in results.best_opportunities:
            opp_dict = {
                "game_id": opp.game_id,
                "sport": opp.sport,
                "matchup": opp.matchup,
                "bet_type": opp.bet_type,
                "bet_side": opp.bet_side,
                "market_odds": opp.market_odds,
                "fair_odds": opp.fair_odds,
                "edge_percentage": opp.edge_percentage,
                "expected_value": opp.expected_value,
                "recommended_stake": opp.recommended_stake,
                "confidence_score": opp.confidence_score,
                "confidence_tier": opp.confidence_tier,
                "sharp_flags": opp.sharp_flags,
                "flag_emojis": opp.flag_emojis,
                "value_rating": opp.value_rating,
                "rationale": opp.rationale,
                "key_factors": opp.key_factors,
                "best_book": opp.best_book,
                "timestamp": opp.timestamp.isoformat(),
                "risk_factors": opp.risk_factors
            }
            serializable_results["opportunities"].append(opp_dict)
        
        return json.dumps(serializable_results, indent=2)


# Helper function for easy usage
def create_demo_analysis() -> SharpPredictorResults:
    """Create a demo analysis with sample data."""
    predictor = SharpPredictor()
    
    # Create sample game data
    from data_input_manager import create_odds_data, create_public_betting_data
    
    sample_odds = create_odds_data(
        moneyline_home=-150,
        moneyline_away=+130,
        spread_line=-2.5,
        total_line=8.5
    )
    
    sample_public = create_public_betting_data(
        moneyline_home_bets=65.0,
        moneyline_home_money=72.0,
        spread_favorite_bets=58.0,
        spread_favorite_money=68.0,
        total_over_bets=52.0,
        total_over_money=48.0
    )
    
    sample_game = predictor.data_manager.create_manual_game_entry(
        sport="MLB",
        home_team="Yankees",
        away_team="Red Sox",
        game_date="2025-01-15 19:00",
        odds_data=sample_odds,
        public_data=sample_public,
        model_predictions={
            "moneyline_home_prob": 0.58,
            "moneyline_away_prob": 0.42,
            "spread_favorite_prob": 0.52,
            "total_over_prob": 0.48
        }
    )
    
    return predictor.analyze_multiple_games([sample_game])