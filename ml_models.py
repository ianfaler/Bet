#!/usr/bin/env python3
"""
Machine Learning Models for Universal Betting Dashboard

This module contains ML models trained on historical data for:
1. MLB prediction models using SportsData.io historical data
2. Soccer prediction models using FootyStats historical data

Features:
- Ensemble models combining multiple algorithms
- Feature engineering from historical data
- Real-time prediction capabilities
- Model performance tracking
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass

# ML Libraries
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("⚠️  ML libraries not available. Install with: pip install scikit-learn xgboost")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path("data")
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

@dataclass
class ModelPrediction:
    """Model prediction result."""
    home_win_prob: float
    away_win_prob: float
    draw_prob: float = 0.0  # For soccer
    home_score_pred: float = 0.0
    away_score_pred: float = 0.0
    confidence: float = 0.0
    model_features: Dict[str, float] = None

class MLBPredictor:
    """MLB prediction model using historical data."""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.is_trained = False
        
        # Auto-load existing models if available
        self._load_models()
        
    def load_historical_data(self) -> pd.DataFrame:
        """Load processed MLB historical data."""
        
        try:
            data_file = PROCESSED_DATA_DIR / "mlb_ml_dataset.csv"
            
            if not data_file.exists():
                logger.warning("⚠️  MLB historical data not found. Run data_manager.py first.")
                return self._generate_sample_mlb_data()
            
            df = pd.read_csv(data_file)
            logger.info(f"✅ Loaded MLB data: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load MLB data: {e}")
            return self._generate_sample_mlb_data()
    
    def _generate_sample_mlb_data(self) -> pd.DataFrame:
        """Generate sample MLB data for testing."""
        
        logger.info("🎲 Generating sample MLB data for model training...")
        
        import random
        
        # Generate realistic MLB game data
        teams = [
            "New York Yankees", "Boston Red Sox", "Houston Astros", "Los Angeles Dodgers",
            "Atlanta Braves", "Seattle Mariners", "Colorado Rockies", "Milwaukee Brewers",
            "Pittsburgh Pirates", "San Francisco Giants", "Texas Rangers", "Oakland Athletics"
        ]
        
        data = []
        for i in range(1000):  # 1000 sample games
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            # Team strength factors
            home_strength = random.uniform(0.4, 0.6)
            away_strength = random.uniform(0.4, 0.6)
            
            # Game context
            home_runs = np.random.poisson(4.5 * home_strength)
            away_runs = np.random.poisson(4.5 * away_strength)
            
            game = {
                'Date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
                'HomeTeam': home_team,
                'AwayTeam': away_team,
                'HomeRuns': home_runs,
                'AwayRuns': away_runs,
                'HomeWin': 1 if home_runs > away_runs else 0,
                'TotalRuns': home_runs + away_runs,
                'RunDifferential': home_runs - away_runs,
                'DayOfWeek': random.randint(0, 6),
                'Month': random.randint(4, 10),  # Baseball season
                'HomeTeamERA': random.uniform(3.0, 5.5),
                'AwayTeamERA': random.uniform(3.0, 5.5),
                'HomeTeamOPS': random.uniform(0.650, 0.850),
                'AwayTeamOPS': random.uniform(0.650, 0.850),
                'Temperature': random.randint(60, 95),
                'WindSpeed': random.randint(0, 20),
                'Attendance': random.randint(15000, 50000)
            }
            data.append(game)
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        logger.info(f"✅ Generated {len(df)} sample MLB games")
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for MLB prediction."""
        
        try:
            logger.info("🔧 Engineering MLB features...")
            
            # Date features
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df['DayOfWeek'] = df['Date'].dt.dayofweek
                df['Month'] = df['Date'].dt.month
                df['Year'] = df['Date'].dt.year
            
            # Team performance features
            if 'HomeTeamERA' in df.columns:
                df['ERA_Advantage'] = df['AwayTeamERA'] - df['HomeTeamERA']  # Lower ERA is better
            
            if 'HomeTeamOPS' in df.columns:
                df['OPS_Advantage'] = df['HomeTeamOPS'] - df['AwayTeamOPS']  # Higher OPS is better
            
            # Weather impact (if available)
            if 'Temperature' in df.columns:
                df['Hot_Weather'] = (df['Temperature'] > 85).astype(int)
                df['Cold_Weather'] = (df['Temperature'] < 65).astype(int)
            
            if 'WindSpeed' in df.columns:
                df['Windy_Conditions'] = (df['WindSpeed'] > 15).astype(int)
            
            # Historical performance (rolling averages - simplified)
            if 'HomeRuns' in df.columns and 'AwayRuns' in df.columns:
                df['Home_Scoring_Avg'] = df['HomeRuns'].rolling(window=10, min_periods=1).mean()
                df['Away_Scoring_Avg'] = df['AwayRuns'].rolling(window=10, min_periods=1).mean()
            
            # Home field advantage
            df['HomeField_Advantage'] = 1  # Always 1 for home team
            
            logger.info(f"✅ Feature engineering complete: {len(df.columns)} features")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to engineer MLB features: {e}")
            return df
    
    def train_models(self, df: pd.DataFrame) -> bool:
        """Train MLB prediction models."""
        
        if not ML_AVAILABLE:
            logger.error("❌ ML libraries not available")
            return False
        
        try:
            logger.info("🏀 Training MLB prediction models...")
            
            # Engineer features
            df = self.engineer_features(df)
            
            # Define feature columns (exclude target and identifier columns)
            exclude_cols = ['Date', 'HomeTeam', 'AwayTeam', 'HomeRuns', 'AwayRuns', 'HomeWin', 'TotalRuns', 'RunDifferential']
            self.feature_columns = [col for col in df.columns if col not in exclude_cols]
            
            # Prepare features and targets
            X = df[self.feature_columns].fillna(0)
            
            # Multiple prediction targets
            y_home_win = df['HomeWin'] if 'HomeWin' in df.columns else (df['HomeRuns'] > df['AwayRuns']).astype(int)
            y_total_runs = df['TotalRuns'] if 'TotalRuns' in df.columns else df['HomeRuns'] + df['AwayRuns']
            y_home_runs = df['HomeRuns'] if 'HomeRuns' in df.columns else np.random.poisson(4.5, len(df))
            y_away_runs = df['AwayRuns'] if 'AwayRuns' in df.columns else np.random.poisson(4.5, len(df))
            
            # Scale features
            self.scalers['features'] = StandardScaler()
            X_scaled = self.scalers['features'].fit_transform(X)
            
            # Train multiple models
            models_to_train = {
                'home_win': (LogisticRegression(random_state=42), y_home_win),
                'total_runs': (RandomForestRegressor(n_estimators=100, random_state=42), y_total_runs),
                'home_runs': (GradientBoostingRegressor(random_state=42), y_home_runs),
                'away_runs': (GradientBoostingRegressor(random_state=42), y_away_runs)
            }
            
            for model_name, (model, target) in models_to_train.items():
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, target, test_size=0.2, random_state=42
                )
                
                # Train model
                model.fit(X_train, y_train)
                
                # Evaluate
                score = model.score(X_test, y_test)
                logger.info(f"✅ {model_name} model trained - Score: {score:.3f}")
                
                # Store model
                self.models[model_name] = model
            
            self.is_trained = True
            
            # Save models
            self._save_models()
            
            logger.info("✅ MLB models training complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to train MLB models: {e}")
            return False
    
    def predict(self, game_features: Dict[str, Any]) -> ModelPrediction:
        """Make prediction for an MLB game."""
        
        if not self.is_trained:
            self._load_models()
        
        try:
            # Prepare features
            feature_vector = np.zeros(len(self.feature_columns))
            
            for i, col in enumerate(self.feature_columns):
                if col in game_features:
                    feature_vector[i] = game_features[col]
            
            # Scale features
            if 'features' in self.scalers:
                feature_vector = self.scalers['features'].transform([feature_vector])[0]
            
            # Make predictions
            home_win_prob = self.models['home_win'].predict_proba([feature_vector])[0][1] if 'home_win' in self.models else 0.5
            home_runs = self.models['home_runs'].predict([feature_vector])[0] if 'home_runs' in self.models else 4.5
            away_runs = self.models['away_runs'].predict([feature_vector])[0] if 'away_runs' in self.models else 4.5
            
            # Calculate away win probability
            away_win_prob = 1 - home_win_prob
            
            # Calculate confidence based on prediction certainty
            confidence = abs(home_win_prob - 0.5) * 2  # 0 to 1 scale
            
            return ModelPrediction(
                home_win_prob=home_win_prob,
                away_win_prob=away_win_prob,
                home_score_pred=home_runs,
                away_score_pred=away_runs,
                confidence=confidence,
                model_features=game_features
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to make MLB prediction: {e}")
            return ModelPrediction(home_win_prob=0.5, away_win_prob=0.5)
    
    def _save_models(self):
        """Save trained models to disk."""
        
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'feature_columns': self.feature_columns,
                'is_trained': self.is_trained,
                'trained_at': datetime.now().isoformat()
            }
            
            with open(MODELS_DIR / "mlb_models.pkl", 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info("✅ MLB models saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to save MLB models: {e}")
    
    def _load_models(self):
        """Load trained models from disk."""
        
        try:
            model_file = MODELS_DIR / "mlb_models.pkl"
            
            if not model_file.exists():
                logger.warning("⚠️  No trained MLB models found")
                return False
            
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.feature_columns = model_data['feature_columns']
            self.is_trained = model_data['is_trained']
            
            logger.info("✅ MLB models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load MLB models: {e}")
            return False

class SoccerPredictor:
    """Soccer prediction model using FootyStats historical data."""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.is_trained = False
        
        # Auto-load existing models if available
        self._load_models()
    
    def load_historical_data(self) -> pd.DataFrame:
        """Load processed soccer historical data."""
        
        try:
            data_file = PROCESSED_DATA_DIR / "soccer_ml_dataset.csv"
            
            if not data_file.exists():
                logger.warning("⚠️  Soccer historical data not found. Run data_manager.py first.")
                return self._generate_sample_soccer_data()
            
            df = pd.read_csv(data_file)
            logger.info(f"✅ Loaded soccer data: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load soccer data: {e}")
            return self._generate_sample_soccer_data()
    
    def _generate_sample_soccer_data(self) -> pd.DataFrame:
        """Generate sample soccer data for testing."""
        
        logger.info("🎲 Generating sample soccer data for model training...")
        
        import random
        
        # Generate realistic soccer match data
        teams = ["Team A", "Team B", "Team C", "Team D", "Team E", "Team F", "Team G", "Team H"]
        leagues = ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
        
        data = []
        for i in range(1500):  # 1500 sample matches
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            league = random.choice(leagues)
            
            # Team strength factors
            home_strength = random.uniform(0.8, 2.5)
            away_strength = random.uniform(0.8, 2.5)
            
            # Generate realistic xG and goals
            home_xg = np.random.gamma(2, home_strength/2)
            away_xg = np.random.gamma(2, away_strength/2)
            
            home_goals = np.random.poisson(home_xg)
            away_goals = np.random.poisson(away_xg)
            
            # Result
            if home_goals > away_goals:
                result = "home_win"
            elif away_goals > home_goals:
                result = "away_win"
            else:
                result = "draw"
            
            match = {
                'date': (datetime.now() - timedelta(days=random.randint(1, 730))).strftime('%Y-%m-%d'),
                'league_name': league,
                'country': "Sample Country",
                'home_team': home_team,
                'away_team': away_team,
                'home_goals': home_goals,
                'away_goals': away_goals,
                'home_xg': round(home_xg, 2),
                'away_xg': round(away_xg, 2),
                'total_goals': home_goals + away_goals,
                'goal_difference': home_goals - away_goals,
                'total_xg': round(home_xg + away_xg, 2),
                'xg_difference': round(home_xg - away_xg, 2),
                'result': result,
                'day_of_week': random.randint(0, 6),
                'month': random.randint(1, 12),
                'possession_home': random.randint(30, 70),
                'possession_away': random.randint(30, 70),
                'shots_home': random.randint(5, 25),
                'shots_away': random.randint(5, 25)
            }
            data.append(match)
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        logger.info(f"✅ Generated {len(df)} sample soccer matches")
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for soccer prediction."""
        
        try:
            logger.info("🔧 Engineering soccer features...")
            
            # Date features
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df['day_of_week'] = df['date'].dt.dayofweek
                df['month'] = df['date'].dt.month
                df['year'] = df['date'].dt.year
                df['weekend'] = (df['day_of_week'] >= 5).astype(int)
            
            # League strength encoding
            if 'league_name' in df.columns:
                # Encode leagues by priority/strength
                league_strength = {
                    'Premier League': 5, 'La Liga': 5, 'Bundesliga': 5, 'Serie A': 5, 'Ligue 1': 4,
                    'Championship': 3, 'Eredivisie': 3, 'Liga MX': 3
                }
                df['league_strength'] = df['league_name'].map(league_strength).fillna(2)
            
            # Goal scoring features
            if 'home_goals' in df.columns and 'away_goals' in df.columns:
                df['high_scoring'] = ((df['home_goals'] + df['away_goals']) > 2.5).astype(int)
                df['home_dominant'] = (df['home_goals'] > df['away_goals'] + 1).astype(int)
                df['away_dominant'] = (df['away_goals'] > df['home_goals'] + 1).astype(int)
            
            # xG efficiency
            if 'home_xg' in df.columns and 'away_xg' in df.columns:
                df['home_xg_efficiency'] = np.where(df['home_xg'] > 0, df['home_goals'] / df['home_xg'], 0)
                df['away_xg_efficiency'] = np.where(df['away_xg'] > 0, df['away_goals'] / df['away_xg'], 0)
                df['xg_ratio'] = np.where(df['away_xg'] > 0, df['home_xg'] / df['away_xg'], 1)
            
            # Possession and shots efficiency
            if 'possession_home' in df.columns:
                df['possession_advantage'] = df['possession_home'] - df['possession_away']
            
            if 'shots_home' in df.columns:
                df['shots_ratio'] = np.where(df['shots_away'] > 0, df['shots_home'] / df['shots_away'], 1)
                df['shot_accuracy_home'] = np.where(df['shots_home'] > 0, df['home_goals'] / df['shots_home'], 0)
                df['shot_accuracy_away'] = np.where(df['shots_away'] > 0, df['away_goals'] / df['shots_away'], 0)
            
            # Team form features (simplified rolling averages)
            df = df.sort_values('date')
            for team_col in ['home_team', 'away_team']:
                if team_col in df.columns:
                    # Recent form (last 5 games)
                    df[f'{team_col}_recent_goals'] = df.groupby(team_col)['home_goals' if 'home' in team_col else 'away_goals'].rolling(window=5, min_periods=1).mean().reset_index(0, drop=True)
            
            logger.info(f"✅ Soccer feature engineering complete: {len(df.columns)} features")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to engineer soccer features: {e}")
            return df
    
    def train_models(self, df: pd.DataFrame) -> bool:
        """Train soccer prediction models."""
        
        if not ML_AVAILABLE:
            logger.error("❌ ML libraries not available")
            return False
        
        try:
            logger.info("⚽ Training soccer prediction models...")
            
            # Engineer features
            df = self.engineer_features(df)
            
            # Define feature columns
            exclude_cols = ['date', 'home_team', 'away_team', 'league_name', 'country', 'result', 
                          'home_goals', 'away_goals', 'total_goals', 'goal_difference']
            self.feature_columns = [col for col in df.columns if col not in exclude_cols]
            
            # Prepare features and targets
            X = df[self.feature_columns].fillna(0)
            
            # Encode result for classification
            self.encoders['result'] = LabelEncoder()
            y_result = self.encoders['result'].fit_transform(df['result'])
            
            # Regression targets
            y_total_goals = df['total_goals'] if 'total_goals' in df.columns else df['home_goals'] + df['away_goals']
            y_home_goals = df['home_goals'] if 'home_goals' in df.columns else np.random.poisson(1.5, len(df))
            y_away_goals = df['away_goals'] if 'away_goals' in df.columns else np.random.poisson(1.3, len(df))
            
            # Scale features
            self.scalers['features'] = StandardScaler()
            X_scaled = self.scalers['features'].fit_transform(X)
            
            # Train multiple models
            models_to_train = {
                'match_result': (RandomForestRegressor(n_estimators=100, random_state=42), y_result),
                'total_goals': (GradientBoostingRegressor(random_state=42), y_total_goals),
                'home_goals': (RandomForestRegressor(n_estimators=50, random_state=42), y_home_goals),
                'away_goals': (RandomForestRegressor(n_estimators=50, random_state=42), y_away_goals)
            }
            
            for model_name, (model, target) in models_to_train.items():
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, target, test_size=0.2, random_state=42
                )
                
                # Train model
                model.fit(X_train, y_train)
                
                # Evaluate
                score = model.score(X_test, y_test)
                logger.info(f"✅ {model_name} model trained - Score: {score:.3f}")
                
                # Store model
                self.models[model_name] = model
            
            self.is_trained = True
            
            # Save models
            self._save_models()
            
            logger.info("✅ Soccer models training complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to train soccer models: {e}")
            return False
    
    def predict(self, match_features: Dict[str, Any]) -> ModelPrediction:
        """Make prediction for a soccer match."""
        
        if not self.is_trained:
            self._load_models()
        
        try:
            # Prepare features
            feature_vector = np.zeros(len(self.feature_columns))
            
            for i, col in enumerate(self.feature_columns):
                if col in match_features:
                    feature_vector[i] = match_features[col]
            
            # Scale features
            if 'features' in self.scalers:
                feature_vector = self.scalers['features'].transform([feature_vector])[0]
            
            # Make predictions
            result_pred = self.models['match_result'].predict([feature_vector])[0] if 'match_result' in self.models else 1
            home_goals = self.models['home_goals'].predict([feature_vector])[0] if 'home_goals' in self.models else 1.5
            away_goals = self.models['away_goals'].predict([feature_vector])[0] if 'away_goals' in self.models else 1.3
            
            # Convert result prediction to probabilities
            # Simplified probability calculation based on predicted scores
            if home_goals > away_goals + 0.5:
                home_win_prob = 0.6
                draw_prob = 0.2
                away_win_prob = 0.2
            elif away_goals > home_goals + 0.5:
                home_win_prob = 0.2
                draw_prob = 0.2
                away_win_prob = 0.6
            else:
                home_win_prob = 0.3
                draw_prob = 0.4
                away_win_prob = 0.3
            
            # Calculate confidence
            score_diff = abs(home_goals - away_goals)
            confidence = min(score_diff / 2, 1.0)  # 0 to 1 scale
            
            return ModelPrediction(
                home_win_prob=home_win_prob,
                away_win_prob=away_win_prob,
                draw_prob=draw_prob,
                home_score_pred=home_goals,
                away_score_pred=away_goals,
                confidence=confidence,
                model_features=match_features
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to make soccer prediction: {e}")
            return ModelPrediction(home_win_prob=0.33, away_win_prob=0.33, draw_prob=0.34)
    
    def _save_models(self):
        """Save trained models to disk."""
        
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'encoders': self.encoders,
                'feature_columns': self.feature_columns,
                'is_trained': self.is_trained,
                'trained_at': datetime.now().isoformat()
            }
            
            with open(MODELS_DIR / "soccer_models.pkl", 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info("✅ Soccer models saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to save soccer models: {e}")
    
    def _load_models(self):
        """Load trained models from disk."""
        
        try:
            model_file = MODELS_DIR / "soccer_models.pkl"
            
            if not model_file.exists():
                logger.warning("⚠️  No trained soccer models found")
                return False
            
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.encoders = model_data.get('encoders', {})
            self.feature_columns = model_data['feature_columns']
            self.is_trained = model_data['is_trained']
            
            logger.info("✅ Soccer models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load soccer models: {e}")
            return False

class MLModelManager:
    """Manager for all ML models."""
    
    def __init__(self):
        self.mlb_predictor = MLBPredictor()
        self.soccer_predictor = SoccerPredictor()
        
    def train_all_models(self) -> Dict[str, bool]:
        """Train all ML models using historical data."""
        
        logger.info("🚀 Training all ML models...")
        
        results = {
            'mlb_trained': False,
            'soccer_trained': False
        }
        
        try:
            # Train MLB models
            mlb_data = self.mlb_predictor.load_historical_data()
            if len(mlb_data) > 0:
                results['mlb_trained'] = self.mlb_predictor.train_models(mlb_data)
            
            # Train Soccer models
            soccer_data = self.soccer_predictor.load_historical_data()
            if len(soccer_data) > 0:
                results['soccer_trained'] = self.soccer_predictor.train_models(soccer_data)
            
            logger.info(f"✅ Model training complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to train models: {e}")
            return results
    
    def get_enhanced_prediction(self, sport: str, game_data: Dict[str, Any]) -> Optional[ModelPrediction]:
        """Get enhanced prediction using ML models."""
        
        try:
            if sport.upper() == 'MLB' and self.mlb_predictor.is_trained:
                return self.mlb_predictor.predict(game_data)
            
            elif sport.upper() == 'SOCCER' and self.soccer_predictor.is_trained:
                return self.soccer_predictor.predict(game_data)
            
            else:
                logger.warning(f"⚠️  No trained model available for {sport}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get enhanced prediction for {sport}: {e}")
            return None
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all ML models."""
        
        status = {
            'ml_available': ML_AVAILABLE,
            'models': {
                'mlb': {
                    'trained': self.mlb_predictor.is_trained,
                    'model_file_exists': (MODELS_DIR / "mlb_models.pkl").exists()
                },
                'soccer': {
                    'trained': self.soccer_predictor.is_trained,
                    'model_file_exists': (MODELS_DIR / "soccer_models.pkl").exists()
                }
            },
            'last_checked': datetime.now().isoformat()
        }
        
        return status

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main CLI interface for ML model management."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="ML Models for Universal Betting Dashboard")
    parser.add_argument("--action", choices=["train", "status", "predict"], 
                       default="status", help="Action to perform")
    parser.add_argument("--sport", choices=["mlb", "soccer"], help="Sport for prediction")
    
    args = parser.parse_args()
    
    model_manager = MLModelManager()
    
    if args.action == "train":
        print("🚀 Training all ML models...")
        results = model_manager.train_all_models()
        print(f"Results: {results}")
    
    elif args.action == "status":
        print("📊 Checking ML model status...")
        status = model_manager.get_model_status()
        print(json.dumps(status, indent=2))
    
    elif args.action == "predict":
        if not args.sport:
            print("❌ Please specify --sport for prediction")
            return
        
        print(f"🔮 Making sample prediction for {args.sport}...")
        sample_data = {"home_team": "Sample Home", "away_team": "Sample Away"}
        prediction = model_manager.get_enhanced_prediction(args.sport, sample_data)
        
        if prediction:
            print(f"Home Win: {prediction.home_win_prob:.2f}")
            print(f"Away Win: {prediction.away_win_prob:.2f}")
            if prediction.draw_prob > 0:
                print(f"Draw: {prediction.draw_prob:.2f}")
            print(f"Confidence: {prediction.confidence:.2f}")
        else:
            print("❌ No prediction available")

if __name__ == "__main__":
    main()