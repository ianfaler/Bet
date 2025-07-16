"""
Enhanced Expected Value (EV) Engine

Calculates Expected Value for betting opportunities with:
- Standard EV calculation
- Kelly Criterion staking
- Manual overrides and annotations
- Risk adjustments
- Environmental factors (weather, injuries, etc.)
- Multiple payout scenarios
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import math
from datetime import datetime


@dataclass
class EVCalculation:
    """Expected Value calculation result."""
    bet_description: str
    stake: float
    win_probability: float
    lose_probability: float
    win_payout: float
    lose_amount: float
    expected_value: float
    ev_percentage: float
    kelly_fraction: float
    recommended_stake: float
    roi_projection: float
    calculation_timestamp: datetime


@dataclass
class RiskFactor:
    """Risk adjustment factor for EV calculation."""
    factor_type: str  # "weather", "injury", "lineup", "variance"
    impact: float  # -1 to +1 (negative = risk, positive = edge)
    description: str
    confidence: float  # 0-1


@dataclass
class EVOverride:
    """Manual override for EV calculation."""
    override_type: str  # "probability", "stake", "disable"
    original_value: float
    override_value: float
    reason: str
    applied_by: str
    timestamp: datetime


class EVEngine:
    """Enhanced Expected Value calculation engine."""
    
    def __init__(self, bankroll: float = 10000.0):
        self.bankroll = bankroll
        self.max_stake_percentage = 0.05  # Max 5% of bankroll per bet
        self.min_ev_threshold = 3.0  # Minimum EV% to consider
        self.kelly_multiplier = 0.25  # Quarter Kelly for safety
        self.risk_adjustment_max = 0.20  # Max 20% risk adjustment
    
    def calculate_basic_ev(
        self, 
        win_probability: float, 
        odds: int, 
        stake: float
    ) -> EVCalculation:
        """
        Calculate basic Expected Value.
        
        Args:
            win_probability: Probability of winning (0-1)
            odds: American odds
            stake: Bet amount
            
        Returns:
            EVCalculation with basic EV result
        """
        lose_probability = 1 - win_probability
        
        # Calculate payout for win
        if odds > 0:
            win_payout = stake * (odds / 100)
        else:
            win_payout = stake * (100 / abs(odds))
        
        lose_amount = stake
        
        # EV = (probability of win * profit) - (probability of loss * loss)
        expected_value = (win_probability * win_payout) - (lose_probability * lose_amount)
        
        # EV percentage relative to stake
        ev_percentage = (expected_value / stake) * 100
        
        # Kelly Criterion calculation
        # Kelly = (bp - q) / b, where b = decimal odds - 1, p = win prob, q = lose prob
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        b = decimal_odds - 1
        kelly_fraction = ((win_probability * b) - lose_probability) / b
        
        # Apply Kelly multiplier for safety
        adjusted_kelly = kelly_fraction * self.kelly_multiplier
        
        # Calculate recommended stake
        recommended_stake = min(
            self.bankroll * adjusted_kelly,
            self.bankroll * self.max_stake_percentage,
            stake  # Don't exceed intended stake
        )
        
        # Ensure positive recommended stake
        recommended_stake = max(0, recommended_stake)
        
        # ROI projection (annualized estimate)
        roi_projection = ev_percentage if ev_percentage > 0 else 0
        
        return EVCalculation(
            bet_description=f"American odds {odds:+d}",
            stake=stake,
            win_probability=win_probability,
            lose_probability=lose_probability,
            win_payout=win_payout,
            lose_amount=lose_amount,
            expected_value=expected_value,
            ev_percentage=ev_percentage,
            kelly_fraction=kelly_fraction,
            recommended_stake=recommended_stake,
            roi_projection=roi_projection,
            calculation_timestamp=datetime.now()
        )
    
    def calculate_ev_with_risk_factors(
        self, 
        win_probability: float, 
        odds: int, 
        stake: float,
        risk_factors: List[RiskFactor]
    ) -> EVCalculation:
        """
        Calculate EV with risk factor adjustments.
        
        Args:
            win_probability: Base win probability
            odds: American odds
            stake: Bet amount  
            risk_factors: List of risk adjustments
            
        Returns:
            EVCalculation with risk-adjusted result
        """
        # Calculate base EV
        base_ev = self.calculate_basic_ev(win_probability, odds, stake)
        
        # Apply risk adjustments
        adjusted_probability = win_probability
        total_risk_impact = 0.0
        
        for risk_factor in risk_factors:
            # Apply risk factor to probability
            risk_adjustment = risk_factor.impact * risk_factor.confidence
            total_risk_impact += risk_adjustment
            
            # Cap total risk adjustment
            capped_adjustment = max(-self.risk_adjustment_max, 
                                  min(self.risk_adjustment_max, risk_adjustment))
            
            adjusted_probability += capped_adjustment * win_probability
        
        # Ensure probability stays in valid range
        adjusted_probability = max(0.01, min(0.99, adjusted_probability))
        
        # Recalculate with adjusted probability
        risk_adjusted_ev = self.calculate_basic_ev(adjusted_probability, odds, stake)
        
        # Update description to include risk factors
        risk_descriptions = [f"{rf.factor_type}({rf.impact:+.2f})" for rf in risk_factors]
        risk_adjusted_ev.bet_description = f"{base_ev.bet_description} | Risk: {', '.join(risk_descriptions)}"
        
        return risk_adjusted_ev
    
    def apply_manual_override(
        self, 
        base_ev: EVCalculation, 
        override: EVOverride
    ) -> EVCalculation:
        """
        Apply manual override to EV calculation.
        
        Args:
            base_ev: Base EV calculation
            override: Manual override to apply
            
        Returns:
            Modified EVCalculation
        """
        if override.override_type == "probability":
            # Recalculate with new probability
            return self.calculate_basic_ev(
                win_probability=override.override_value,
                odds=self._extract_odds_from_description(base_ev.bet_description),
                stake=base_ev.stake
            )
        
        elif override.override_type == "stake":
            # Update stake and recalculate
            modified_ev = self.calculate_basic_ev(
                win_probability=base_ev.win_probability,
                odds=self._extract_odds_from_description(base_ev.bet_description),
                stake=override.override_value
            )
            modified_ev.bet_description += f" | Override: {override.reason}"
            return modified_ev
        
        elif override.override_type == "disable":
            # Set EV to negative to disable bet
            base_ev.expected_value = -abs(base_ev.expected_value)
            base_ev.ev_percentage = -abs(base_ev.ev_percentage)
            base_ev.recommended_stake = 0.0
            base_ev.bet_description += f" | DISABLED: {override.reason}"
            return base_ev
        
        return base_ev
    
    def _extract_odds_from_description(self, description: str) -> int:
        """Extract odds from bet description (helper method)."""
        # Simple extraction - in practice, would store odds separately
        try:
            if "odds " in description:
                odds_str = description.split("odds ")[1].split()[0]
                return int(odds_str)
        except:
            pass
        return -110  # Default
    
    def calculate_multi_outcome_ev(
        self, 
        outcomes: List[Tuple[float, int, float]]  # (probability, odds, stake)
    ) -> List[EVCalculation]:
        """
        Calculate EV for multiple related outcomes.
        
        Args:
            outcomes: List of (probability, odds, stake) tuples
            
        Returns:
            List of EVCalculation results
        """
        results = []
        
        for i, (probability, odds, stake) in enumerate(outcomes):
            ev_calc = self.calculate_basic_ev(probability, odds, stake)
            ev_calc.bet_description = f"Outcome {i+1}: {ev_calc.bet_description}"
            results.append(ev_calc)
        
        return results
    
    def calculate_parlay_ev(
        self, 
        leg_probabilities: List[float], 
        leg_odds: List[int], 
        stake: float
    ) -> EVCalculation:
        """
        Calculate EV for parlay bet.
        
        Args:
            leg_probabilities: Win probabilities for each leg
            leg_odds: Odds for each leg (for payout calculation)
            stake: Total parlay stake
            
        Returns:
            EVCalculation for parlay
        """
        # Calculate combined probability (all legs must win)
        combined_probability = 1.0
        for prob in leg_probabilities:
            combined_probability *= prob
        
        # Calculate parlay payout (multiply all odds)
        total_decimal_odds = 1.0
        for odds in leg_odds:
            if odds > 0:
                decimal_odds = (odds / 100) + 1
            else:
                decimal_odds = (100 / abs(odds)) + 1
            total_decimal_odds *= decimal_odds
        
        # Convert back to American odds for calculation
        if total_decimal_odds >= 2.0:
            parlay_american_odds = round((total_decimal_odds - 1) * 100)
        else:
            parlay_american_odds = round(-100 / (total_decimal_odds - 1))
        
        # Calculate parlay EV
        parlay_ev = self.calculate_basic_ev(combined_probability, parlay_american_odds, stake)
        parlay_ev.bet_description = f"Parlay ({len(leg_probabilities)} legs): {parlay_american_odds:+d}"
        
        return parlay_ev
    
    def analyze_bet_sizing(
        self, 
        ev_calculations: List[EVCalculation]
    ) -> Dict[str, Any]:
        """
        Analyze optimal bet sizing across multiple opportunities.
        
        Args:
            ev_calculations: List of EV calculations to analyze
            
        Returns:
            Dict with sizing recommendations
        """
        positive_ev_bets = [ev for ev in ev_calculations if ev.expected_value > 0]
        
        if not positive_ev_bets:
            return {
                "total_recommended_stake": 0.0,
                "bankroll_allocation": 0.0,
                "bet_count": 0,
                "avg_ev": 0.0,
                "risk_assessment": "No positive EV opportunities"
            }
        
        total_recommended_stake = sum(ev.recommended_stake for ev in positive_ev_bets)
        bankroll_allocation = (total_recommended_stake / self.bankroll) * 100
        avg_ev = sum(ev.ev_percentage for ev in positive_ev_bets) / len(positive_ev_bets)
        
        # Risk assessment
        if bankroll_allocation > 15:
            risk_level = "High"
        elif bankroll_allocation > 8:
            risk_level = "Moderate"
        else:
            risk_level = "Conservative"
        
        return {
            "total_recommended_stake": total_recommended_stake,
            "bankroll_allocation": bankroll_allocation,
            "bet_count": len(positive_ev_bets),
            "avg_ev": avg_ev,
            "risk_assessment": risk_level,
            "individual_stakes": [ev.recommended_stake for ev in positive_ev_bets]
        }
    
    def calculate_expected_profit(
        self, 
        ev_calculations: List[EVCalculation], 
        number_of_bets: int = 1
    ) -> Dict[str, float]:
        """
        Calculate expected profit over multiple bets.
        
        Args:
            ev_calculations: EV calculations
            number_of_bets: Number of times to place these bets
            
        Returns:
            Dict with profit projections
        """
        total_ev = sum(ev.expected_value for ev in ev_calculations)
        total_stake = sum(ev.recommended_stake for ev in ev_calculations)
        
        expected_profit = total_ev * number_of_bets
        total_risk = total_stake * number_of_bets
        
        if total_risk > 0:
            roi_percentage = (expected_profit / total_risk) * 100
        else:
            roi_percentage = 0.0
        
        return {
            "expected_profit": expected_profit,
            "total_risk": total_risk,
            "roi_percentage": roi_percentage,
            "profit_per_bet": expected_profit / max(1, number_of_bets),
            "break_even_probability": total_risk / (total_risk + expected_profit) if expected_profit > 0 else 1.0
        }
    
    def analyze_manual_input(self, manual_data: Dict[str, Any]) -> List[EVCalculation]:
        """
        Analyze manually input EV data.
        
        Args:
            manual_data: Dict containing manual EV data
            
        Returns:
            List of EV calculations
        """
        results = []
        
        if "single_bet" in manual_data:
            bet_data = manual_data["single_bet"]
            
            # Create risk factors if provided
            risk_factors = []
            if "risk_factors" in bet_data:
                for rf_data in bet_data["risk_factors"]:
                    risk_factors.append(RiskFactor(
                        factor_type=rf_data.get("type", "unknown"),
                        impact=rf_data.get("impact", 0.0),
                        description=rf_data.get("description", ""),
                        confidence=rf_data.get("confidence", 1.0)
                    ))
            
            # Calculate EV with or without risk factors
            if risk_factors:
                ev_calc = self.calculate_ev_with_risk_factors(
                    win_probability=bet_data.get("win_probability", 0.5),
                    odds=bet_data.get("odds", -110),
                    stake=bet_data.get("stake", 100),
                    risk_factors=risk_factors
                )
            else:
                ev_calc = self.calculate_basic_ev(
                    win_probability=bet_data.get("win_probability", 0.5),
                    odds=bet_data.get("odds", -110),
                    stake=bet_data.get("stake", 100)
                )
            
            # Apply override if provided
            if "override" in bet_data:
                override_data = bet_data["override"]
                override = EVOverride(
                    override_type=override_data.get("type", "probability"),
                    original_value=0.0,  # Will be set properly in apply_override
                    override_value=override_data.get("value", 0.0),
                    reason=override_data.get("reason", "Manual override"),
                    applied_by=override_data.get("user", "System"),
                    timestamp=datetime.now()
                )
                ev_calc = self.apply_manual_override(ev_calc, override)
            
            results.append(ev_calc)
        
        if "parlay" in manual_data:
            parlay_data = manual_data["parlay"]
            parlay_calc = self.calculate_parlay_ev(
                leg_probabilities=parlay_data.get("probabilities", [0.5, 0.5]),
                leg_odds=parlay_data.get("odds", [-110, -110]),
                stake=parlay_data.get("stake", 100)
            )
            results.append(parlay_calc)
        
        return results


# Helper functions for manual input
def create_manual_ev_input(
    win_probability: float,
    odds: int,
    stake: float,
    risk_factors: Optional[List[Dict[str, Any]]] = None,
    override: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Helper to create manual EV input."""
    bet_data = {
        "win_probability": win_probability,
        "odds": odds,
        "stake": stake
    }
    
    if risk_factors:
        bet_data["risk_factors"] = risk_factors
    
    if override:
        bet_data["override"] = override
    
    return {"single_bet": bet_data}


def create_parlay_input(
    probabilities: List[float],
    odds: List[int],
    stake: float
) -> Dict[str, Any]:
    """Helper to create parlay input."""
    return {
        "parlay": {
            "probabilities": probabilities,
            "odds": odds,
            "stake": stake
        }
    }


def create_risk_factor(
    factor_type: str,
    impact: float,
    description: str,
    confidence: float = 1.0
) -> Dict[str, Any]:
    """Helper to create risk factor."""
    return {
        "type": factor_type,
        "impact": impact,
        "description": description,
        "confidence": confidence
    }