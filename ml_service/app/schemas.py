from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class EnvironmentalData(BaseModel):
    temperature: float = Field(..., description="Ambient temperature in Celsius")
    humidity: float = Field(..., description="Relative humidity percentage (0-100)")
    co: float = Field(..., description="Carbon monoxide level in μg/m³")
    no2: float = Field(default=0.0, description="Nitrogen dioxide level in μg/m³")
    o3: float = Field(default=0.0, description="Ozone level in μg/m³")
    pm2_5: float = Field(default=0.0, description="PM2.5 particulate matter in μg/m³")
    pm10: float = Field(default=0.0, description="PM10 particulate matter in μg/m³")

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 28.5,
                "humidity": 65.0,
                "co": 250.34,
                "no2": 15.5,
                "o3": 45.2,
                "pm2_5": 35.0,
                "pm10": 50.0
            }
        }


class PredictionResult(BaseModel):
    predicted_aqi: float = Field(..., description="Predicted Air Quality Index value (0-500)")
    risk_level: str = Field(..., description="Risk level: Good, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Very Unhealthy, Hazardous")
    message: str = Field(..., description="Health recommendation message")
    dominant_pollutant: str = Field(..., description="The pollutant contributing most to AQI")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_aqi": 75.5,
                "risk_level": "Moderate",
                "message": "Air quality is acceptable; however, there may be some health concern for a very small number of people.",
                "dominant_pollutant": "pm2_5"
            }
        }


class WeatherPredictionRequest(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")
    weather: dict = Field(..., description="Weather data from OpenWeatherMap")
    air_pollution: dict = Field(..., description="Air pollution components")

    class Config:
        json_schema_extra = {
            "example": {
                "lat": -6.2088,
                "lon": 106.8456,
                "weather": {
                    "temperature": 28.5,
                    "humidity": 65.0
                },
                "air_pollution": {
                    "co": 250.34,
                    "no2": 15.5,
                    "o3": 45.2,
                    "pm2_5": 35.0,
                    "pm10": 50.0
                }
            }
        }


class HeatDataPoint(BaseModel):
    district: str = Field(..., description="Jakarta district name")
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")
    temperature: float = Field(..., description="Current temperature in Celsius")
    risk_level: str = Field(..., description="Heat risk level: Low, Medium, High, Extreme")
    aqi: float = Field(..., description="Air Quality Index")
    population: int = Field(..., description="Population count")
    green_coverage: float = Field(..., description="Green coverage percentage (0-100)")
    humidity: float = Field(..., description="Relative humidity percentage")
    wind_speed: float = Field(..., description="Wind speed in km/h")

    class Config:
        json_schema_extra = {
            "example": {
                "district": "Central Jakarta",
                "lat": -6.2088,
                "lon": 106.8456,
                "temperature": 32.5,
                "risk_level": "High",
                "aqi": 85.0,
                "population": 1000000,
                "green_coverage": 25.0,
                "humidity": 65.0,
                "wind_speed": 8.5
            }
        }


class HeatDataResponse(BaseModel):
    data: List[HeatDataPoint] = Field(..., description="List of heat data points")
    summary: Dict[str, int] = Field(..., description="Summary of risk levels")
    last_updated: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "district": "Central Jakarta",
                        "lat": -6.2088,
                        "lon": 106.8456,
                        "temperature": 32.5,
                        "risk_level": "High",
                        "aqi": 85.0,
                        "population": 1000000,
                        "green_coverage": 25.0,
                        "humidity": 65.0,
                        "wind_speed": 8.5
                    }
                ],
                "summary": {
                    "Low": 2,
                    "Medium": 3,
                    "High": 2,
                    "Extreme": 1
                },
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }


class AnalyticsResponse(BaseModel):
    total_districts: int = Field(..., description="Total number of districts")
    high_risk_areas: int = Field(..., description="Number of high risk areas")
    average_temperature: float = Field(..., description="Average temperature across all areas")
    average_aqi: float = Field(..., description="Average AQI across all areas")
    total_population_at_risk: int = Field(..., description="Total population in high risk areas")
    recommendations: List[str] = Field(..., description="List of AI-generated recommendations")
    trends: Dict[str, float] = Field(..., description="Temperature and AQI trends")

    class Config:
        json_schema_extra = {
            "example": {
                "total_districts": 6,
                "high_risk_areas": 2,
                "average_temperature": 31.2,
                "average_aqi": 78.5,
                "total_population_at_risk": 2500000,
                "recommendations": [
                    "Increase green coverage in Central Jakarta by 15%",
                    "Implement cool roof technologies in high-risk areas",
                    "Install smart irrigation systems in residential zones"
                ],
                "trends": {
                    "temperature_change_24h": 2.1,
                    "aqi_change_24h": -5.2
                }
            }
        }


class ChatMessage(BaseModel):
    message: str = Field(..., description="User message content")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context data")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What are the best cooling strategies for Central Jakarta?",
                "context": {
                    "location": "Central Jakarta",
                    "temperature": 32.5
                }
            }
        }


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response content")
    recommendations: List[str] = Field(default=[], description="List of recommendations")
    confidence: float = Field(..., description="Confidence score (0-1)")
    sources: List[str] = Field(default=[], description="Data sources used")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Based on current temperature data, I recommend increasing green coverage in Central Jakarta by 15% to reduce urban heat island effect. Consider implementing vertical gardens and rooftop planting initiatives.",
                "recommendations": [
                    "Increase green coverage by 15%",
                    "Install vertical gardens",
                    "Implement rooftop planting"
                ],
                "confidence": 0.85,
                "sources": [
                    "Jakarta Environmental Agency",
                    "Urban Heat Island Study 2024"
                ]
            }
        }
