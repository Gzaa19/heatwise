import os
import json
import numpy as np
from typing import Optional, Tuple

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.schemas import EnvironmentalData


class HeatWisePredictor:
    def __init__(self, model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        self.model: Optional[keras.Model] = None
        self.model_loaded: bool = False
        self.scaler_mean: Optional[np.ndarray] = None
        self.scaler_scale: Optional[np.ndarray] = None
        
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            # Try different model file formats
            keras_path = os.path.join(base_dir, 'artifacts', 'heat_wise_model.keras')
            h5_path = os.path.join(base_dir, 'artifacts', 'heat_wise_model.h5')
            savedmodel_path = os.path.join(base_dir, 'artifacts', 'heat_wise_saved_model')
            
            # Prioritize new .keras format, then SavedModel, then legacy .h5
            if os.path.exists(keras_path):
                model_path = keras_path
            elif os.path.exists(savedmodel_path):
                model_path = savedmodel_path
            elif os.path.exists(h5_path):
                model_path = h5_path
            else:
                model_path = keras_path  # Will show not found error
                
            scaler_path = os.path.join(base_dir, 'artifacts', 'scaler_params.json')
        
        self._load_model(model_path)
        self._load_scaler(scaler_path)
    
    def _load_model(self, model_path: str) -> None:
        try:
            if not os.path.exists(model_path):
                print(f"WARNING: Model file not found at '{model_path}'")
                print("   Please run 'python train_model.py' first to generate the model.")
                return
            
            print(f"Loading model from: {model_path}")
            
            # Try loading with compile=False to avoid metric serialization issues
            try:
                self.model = keras.models.load_model(model_path, compile=False)
                # Recompile the model
                self.model.compile(
                    optimizer='adam',
                    loss='mse',
                    metrics=['mae']
                )
            except Exception:
                # Fallback: try normal load
                self.model = keras.models.load_model(model_path)
            
            self.model_loaded = True
            print("Model loaded successfully!")
            
        except Exception as e:
            print(f"WARNING: Failed to load model: {str(e)}")
    
    def _load_scaler(self, scaler_path: str) -> None:
        try:
            if scaler_path and os.path.exists(scaler_path):
                with open(scaler_path, 'r') as f:
                    params = json.load(f)
                    self.scaler_mean = np.array(params['mean'])
                    self.scaler_scale = np.array(params['scale'])
                print("Scaler params loaded successfully!")
        except Exception as e:
            print(f"WARNING: Failed to load scaler: {str(e)}")
    
    def _get_risk_level(self, aqi: float) -> Tuple[str, str]:
        """Get EPA-based AQI risk level and health message"""
        if aqi <= 50:
            return (
                "Good",
                "Air quality is considered satisfactory, and air pollution poses little or no risk."
            )
        elif aqi <= 100:
            return (
                "Moderate",
                "Air quality is acceptable; however, there may be some health concern for a very small number of people who are unusually sensitive to air pollution."
            )
        elif aqi <= 150:
            return (
                "Unhealthy for Sensitive Groups",
                "Members of sensitive groups may experience health effects. The general public is not likely to be affected."
            )
        elif aqi <= 200:
            return (
                "Unhealthy",
                "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects."
            )
        elif aqi <= 300:
            return (
                "Very Unhealthy",
                "Health alert: everyone may experience more serious health effects."
            )
        else:
            return (
                "Hazardous",
                "Health warnings of emergency conditions. The entire population is more likely to be affected."
            )
    
    def _get_dominant_pollutant(self, data: EnvironmentalData) -> str:
        """Determine dominant pollutant based on AQI breakpoint thresholds"""
        pollutants = {
            'pm2_5': data.pm2_5 / 35.4 * 100 if data.pm2_5 else 0,
            'pm10': data.pm10 / 154 * 100 if data.pm10 else 0,
            'co': data.co / 9400 * 100 if data.co else 0,
            'no2': data.no2 / 80 * 100 if data.no2 else 0,
            'o3': data.o3 / 120 * 100 if data.o3 else 0,
        }
        return max(pollutants, key=pollutants.get)
    
    def predict(self, data: EnvironmentalData) -> dict:
        """Make AQI prediction from environmental data"""
        if not self.model_loaded or self.model is None:
            raise RuntimeError(
                "Model is not loaded. Please run 'python train_model.py' to train and save the model."
            )
        
        input_array = np.array([[
            data.temperature,
            data.humidity,
            data.co,
            data.no2,
            data.o3,
            data.pm2_5,
            data.pm10
        ]], dtype=np.float32)
        
        if self.scaler_mean is not None and self.scaler_scale is not None:
            input_array = (input_array - self.scaler_mean) / self.scaler_scale
        
        prediction = self.model.predict(input_array, verbose=0)
        predicted_aqi = float(prediction[0][0])
        predicted_aqi = max(0, min(500, predicted_aqi))
        
        risk_level, message = self._get_risk_level(predicted_aqi)
        dominant_pollutant = self._get_dominant_pollutant(data)
        
        return {
            'predicted_aqi': round(predicted_aqi, 2),
            'risk_level': risk_level,
            'message': message,
            'dominant_pollutant': dominant_pollutant
        }
    
    def is_ready(self) -> bool:
        """Check if predictor is ready for predictions"""
        return self.model_loaded and self.model is not None
