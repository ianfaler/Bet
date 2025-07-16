"""
Enhanced Confidence Scoring System

Calculates confidence scores (1-10) based on:
- Number of sharp indicators triggered
- EV tier and magnitude
- Market confidence and matchup edge
- Stability factors (lineup changes, weather, etc.)
- Model agreement and consensus
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import math


@dataclass
class ConfidenceInput:
    """Input data for confidence scoring."""
    sharp_indicators: List[str]  # ["RLM", "Steam", "Sharp $", "Consensus"]
    ev_percentage: float
    model_confidence: float  # 0-1
    market_stability: float  # 0-1 (1 = very stable)
    data_quality: float  # 0-1 (1 = high quality)
    matchup_edge: Optional[float] = None  # Specific matchup advantage
    consensus_strength: Optional[float] = None  # Agreement across models
    volatility_factors: Optional[List[str]] = None  # Risk factors


@dataclass
class ConfidenceBreakdown:
    """Detailed breakdown of confidence score components."""
    base_score: float
    sharp_indicators_bonus: float
    ev_tier_bonus: float
    model_confidence_bonus: float
    stability_bonus: float
    consensus_bonus: float
    volatility_penalty: float
    final_score: int  # 1-10
    explanation: str
    key_factors: List[str]


class ConfidenceScorer:
    """Enhanced confidence scoring system."""
    
    def __init__(self):
        # Base scoring parameters
        self.base_score = 5.0  # Starting point
        self.max_score = 10
        self.min_score = 1
        
        # Sharp indicator bonuses (max 3 points total)
        self.sharp_indicator_weights = {
            "RLM": 1.0,
            "Steam": 1.0, 
            "Sharp $": 0.8,
            "Consensus": 0.6
        }
        self.max_sharp_bonus = 3.0
        
        # EV tier bonuses (max 3 points)
        self.ev_tiers = {
            "excellent": (10.0, 3.0),  # >=10% EV = +3 points
            "good": (6.0, 2.0),        # 6-10% EV = +2 points  
            "fair": (3.0, 1.0),        # 3-6% EV = +1 point
            "poor": (0.0, 0.0)         # <3% EV = +0 points
        }
        
        # Stability and confidence bonuses (max 2 points each)
        self.max_model_confidence_bonus = 2.0
        self.max_stability_bonus = 2.0
        self.max_consensus_bonus = 1.0
        
        # Volatility penalties (max -2 points)
        self.volatility_penalties = {
            "weather": -0.5,
            "injury": -0.7,
            "lineup": -0.4,
            "variance": -0.3,
            "market_thin": -0.6
        }
        self.max_volatility_penalty = -2.0
    
    def calculate_confidence_score(self, confidence_input: ConfidenceInput) -> ConfidenceBreakdown:
        """
        Calculate comprehensive confidence score.
        
        Args:
            confidence_input: All input data for scoring
            
        Returns:
            ConfidenceBreakdown with detailed score components
        """
        # Start with base score
        score = self.base_score
        
        # Calculate sharp indicators bonus
        sharp_bonus = self._calculate_sharp_indicators_bonus(confidence_input.sharp_indicators)
        score += sharp_bonus
        
        # Calculate EV tier bonus
        ev_bonus = self._calculate_ev_tier_bonus(confidence_input.ev_percentage)
        score += ev_bonus
        
        # Calculate model confidence bonus
        model_bonus = self._calculate_model_confidence_bonus(confidence_input.model_confidence)
        score += model_bonus
        
        # Calculate stability bonus
        stability_bonus = self._calculate_stability_bonus(
            confidence_input.market_stability, 
            confidence_input.data_quality
        )
        score += stability_bonus
        
        # Calculate consensus bonus
        consensus_bonus = self._calculate_consensus_bonus(confidence_input.consensus_strength)
        score += consensus_bonus
        
        # Calculate volatility penalty
        volatility_penalty = self._calculate_volatility_penalty(confidence_input.volatility_factors)
        score += volatility_penalty  # This is negative
        
        # Ensure score is in valid range
        final_score = max(self.min_score, min(self.max_score, round(score)))
        
        # Generate explanation
        explanation = self._generate_explanation(
            sharp_bonus, ev_bonus, model_bonus, stability_bonus, 
            consensus_bonus, volatility_penalty, final_score
        )
        
        # Identify key factors
        key_factors = self._identify_key_factors(
            confidence_input, sharp_bonus, ev_bonus, volatility_penalty
        )
        
        return ConfidenceBreakdown(
            base_score=self.base_score,
            sharp_indicators_bonus=sharp_bonus,
            ev_tier_bonus=ev_bonus,
            model_confidence_bonus=model_bonus,
            stability_bonus=stability_bonus,
            consensus_bonus=consensus_bonus,
            volatility_penalty=volatility_penalty,
            final_score=final_score,
            explanation=explanation,
            key_factors=key_factors
        )
    
    def _calculate_sharp_indicators_bonus(self, indicators: List[str]) -> float:
        """Calculate bonus from sharp indicators (max 3 points)."""
        if not indicators:
            return 0.0
        
        total_weight = 0.0
        for indicator in indicators:
            if indicator in self.sharp_indicator_weights:
                total_weight += self.sharp_indicator_weights[indicator]
        
        # Scale to max bonus
        bonus = min(self.max_sharp_bonus, total_weight)
        return bonus
    
    def _calculate_ev_tier_bonus(self, ev_percentage: float) -> float:
        """Calculate bonus from EV tier (max 3 points)."""
        for tier, (threshold, bonus) in self.ev_tiers.items():
            if ev_percentage >= threshold:
                return bonus
        return 0.0
    
    def _calculate_model_confidence_bonus(self, model_confidence: float) -> float:
        """Calculate bonus from model confidence (max 2 points)."""
        if model_confidence is None:
            return 0.0
        
        # Linear scaling: 0.8+ confidence = max bonus
        normalized_confidence = max(0, (model_confidence - 0.5) / 0.3)
        bonus = min(self.max_model_confidence_bonus, normalized_confidence * self.max_model_confidence_bonus)
        return bonus
    
    def _calculate_stability_bonus(self, market_stability: float, data_quality: float) -> float:
        """Calculate bonus from market stability and data quality (max 2 points)."""
        if market_stability is None:
            market_stability = 0.5
        if data_quality is None:
            data_quality = 0.5
        
        # Combine stability and data quality
        combined_stability = (market_stability + data_quality) / 2
        
        # High stability (0.8+) gets max bonus
        normalized_stability = max(0, (combined_stability - 0.6) / 0.2)
        bonus = min(self.max_stability_bonus, normalized_stability * self.max_stability_bonus)
        return bonus
    
    def _calculate_consensus_bonus(self, consensus_strength: Optional[float]) -> float:
        """Calculate bonus from model consensus (max 1 point)."""
        if consensus_strength is None:
            return 0.0
        
        # High consensus (0.8+) gets bonus
        if consensus_strength >= 0.8:
            return self.max_consensus_bonus
        elif consensus_strength >= 0.6:
            return self.max_consensus_bonus * 0.5
        return 0.0
    
    def _calculate_volatility_penalty(self, volatility_factors: Optional[List[str]]) -> float:
        """Calculate penalty from volatility factors (max -2 points)."""
        if not volatility_factors:
            return 0.0
        
        total_penalty = 0.0
        for factor in volatility_factors:
            if factor in self.volatility_penalties:
                total_penalty += self.volatility_penalties[factor]
        
        # Cap at max penalty
        penalty = max(self.max_volatility_penalty, total_penalty)
        return penalty
    
    def _generate_explanation(
        self, 
        sharp_bonus: float, 
        ev_bonus: float, 
        model_bonus: float,
        stability_bonus: float,
        consensus_bonus: float,
        volatility_penalty: float,
        final_score: int
    ) -> str:
        """Generate human-readable explanation of confidence score."""
        explanations = []
        
        if sharp_bonus >= 2.0:
            explanations.append("Strong sharp indicators")
        elif sharp_bonus >= 1.0:
            explanations.append("Moderate sharp signals")
        
        if ev_bonus >= 2.0:
            explanations.append("Excellent EV")
        elif ev_bonus >= 1.0:
            explanations.append("Good EV")
        
        if model_bonus >= 1.0:
            explanations.append("High model confidence")
        
        if stability_bonus >= 1.0:
            explanations.append("Stable market")
        
        if consensus_bonus > 0:
            explanations.append("Model consensus")
        
        if volatility_penalty <= -1.0:
            explanations.append("Significant risk factors")
        elif volatility_penalty < 0:
            explanations.append("Minor risk factors")
        
        if not explanations:
            explanations.append("Standard confidence factors")
        
        base_explanation = f"Confidence {final_score}/10: " + ", ".join(explanations)
        
        # Add specific score breakdown
        breakdown = f" (Base: {self.base_score:.0f}"
        if sharp_bonus > 0:
            breakdown += f", Sharp: +{sharp_bonus:.1f}"
        if ev_bonus > 0:
            breakdown += f", EV: +{ev_bonus:.1f}"
        if model_bonus > 0:
            breakdown += f", Model: +{model_bonus:.1f}"
        if stability_bonus > 0:
            breakdown += f", Stability: +{stability_bonus:.1f}"
        if consensus_bonus > 0:
            breakdown += f", Consensus: +{consensus_bonus:.1f}"
        if volatility_penalty < 0:
            breakdown += f", Risk: {volatility_penalty:.1f}"
        breakdown += ")"
        
        return base_explanation + breakdown
    
    def _identify_key_factors(
        self, 
        confidence_input: ConfidenceInput,
        sharp_bonus: float,
        ev_bonus: float, 
        volatility_penalty: float
    ) -> List[str]:
        """Identify the most important factors affecting confidence."""
        factors = []
        
        # Sharp indicators
        if sharp_bonus >= 2.0:
            factors.append("🔥 Multiple sharp signals")
        elif confidence_input.sharp_indicators:
            factors.append(f"📈 {', '.join(confidence_input.sharp_indicators)}")
        
        # EV tier
        if ev_bonus >= 2.0:
            factors.append(f"💰 Excellent edge ({confidence_input.ev_percentage:.1f}%)")
        elif ev_bonus >= 1.0:
            factors.append(f"💵 Good edge ({confidence_input.ev_percentage:.1f}%)")
        
        # Model confidence
        if confidence_input.model_confidence and confidence_input.model_confidence >= 0.8:
            factors.append("🎯 High model confidence")
        
        # Volatility factors
        if volatility_penalty <= -1.0:
            factors.append(f"⚠️ Risk: {', '.join(confidence_input.volatility_factors or [])}")
        
        # Data quality
        if confidence_input.data_quality and confidence_input.data_quality >= 0.9:
            factors.append("📊 High data quality")
        
        return factors
    
    def calculate_batch_confidence(
        self, 
        confidence_inputs: List[ConfidenceInput]
    ) -> List[ConfidenceBreakdown]:
        """Calculate confidence scores for multiple bets."""
        return [self.calculate_confidence_score(input_data) for input_data in confidence_inputs]
    
    def analyze_confidence_distribution(
        self, 
        confidence_scores: List[ConfidenceBreakdown]
    ) -> Dict[str, Any]:
        """Analyze distribution of confidence scores."""
        if not confidence_scores:
            return {"error": "No confidence scores provided"}
        
        scores = [cs.final_score for cs in confidence_scores]
        
        return {
            "count": len(scores),
            "average": sum(scores) / len(scores),
            "median": sorted(scores)[len(scores) // 2],
            "min": min(scores),
            "max": max(scores),
            "high_confidence_count": len([s for s in scores if s >= 8]),
            "low_confidence_count": len([s for s in scores if s <= 4]),
            "distribution": {
                f"score_{i}": scores.count(i) for i in range(1, 11)
            }
        }
    
    def analyze_manual_input(self, manual_data: Dict[str, Any]) -> ConfidenceBreakdown:
        """
        Analyze manually input confidence data.
        
        Args:
            manual_data: Dict containing manual confidence input
            
        Returns:
            ConfidenceBreakdown result
        """
        # Extract data from manual input
        confidence_input = ConfidenceInput(
            sharp_indicators=manual_data.get("sharp_indicators", []),
            ev_percentage=manual_data.get("ev_percentage", 0.0),
            model_confidence=manual_data.get("model_confidence", 0.5),
            market_stability=manual_data.get("market_stability", 0.5),
            data_quality=manual_data.get("data_quality", 0.5),
            matchup_edge=manual_data.get("matchup_edge"),
            consensus_strength=manual_data.get("consensus_strength"),
            volatility_factors=manual_data.get("volatility_factors", [])
        )
        
        return self.calculate_confidence_score(confidence_input)


# Helper functions for manual input
def create_manual_confidence_input(
    sharp_indicators: List[str],
    ev_percentage: float,
    model_confidence: float = 0.8,
    market_stability: float = 0.8,
    data_quality: float = 0.8,
    volatility_factors: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Helper to create manual confidence input."""
    return {
        "sharp_indicators": sharp_indicators,
        "ev_percentage": ev_percentage,
        "model_confidence": model_confidence,
        "market_stability": market_stability,
        "data_quality": data_quality,
        "volatility_factors": volatility_factors or []
    }


def get_confidence_tier(confidence_score: int) -> str:
    """Get confidence tier description."""
    if confidence_score >= 9:
        return "Exceptional"
    elif confidence_score >= 8:
        return "High"
    elif confidence_score >= 7:
        return "Good"
    elif confidence_score >= 6:
        return "Fair"
    elif confidence_score >= 5:
        return "Average"
    elif confidence_score >= 4:
        return "Below Average"
    elif confidence_score >= 3:
        return "Low"
    elif confidence_score >= 2:
        return "Very Low"
    else:
        return "Minimal"