"""
Agromonitoring Service for HeatWise
Integrates with Agromonitoring API for soil and agricultural data
"""

import os
import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SoilData:
    """Soil data structure"""
    moisture: float
    temperature: float  # Kelvin
    temperature_celsius: float
    dt: int
    lat: float
    lon: float


@dataclass
class SatelliteData:
    """Satellite imagery data"""
    dt: int
    type: str
    dc: float  # Data coverage
    cl: float  # Cloud coverage
    sun_azimuth: float
    sun_elevation: float
    image_url: Optional[str] = None
    stats_url: Optional[str] = None


class AgromonitoringService:
    """Service to fetch agricultural and soil data from Agromonitoring API"""
    
    def __init__(self):
        self.api_key = os.getenv("AGROMONITORING_API_KEY")
        self.base_url = "https://api.agromonitoring.com/agro/1.0"
        
        if not self.api_key:
            print("WARNING: AGROMONITORING_API_KEY is not set. Soil data will not be available.")
    
    def is_available(self) -> bool:
        """Check if the service is available (API key is set)"""
        return self.api_key is not None
    
    async def get_soil_data(
        self,
        lat: float,
        lon: float
    ) -> Optional[SoilData]:
        """
        Get current soil data for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            SoilData object or None if request fails
        """
        if not self.is_available():
            return None
            
        url = f"{self.base_url}/soil"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # Convert temperature from Kelvin to Celsius
                temp_kelvin = data.get("t0", 273.15)
                temp_celsius = temp_kelvin - 273.15
                
                return SoilData(
                    moisture=data.get("moisture", 0),
                    temperature=temp_kelvin,
                    temperature_celsius=round(temp_celsius, 2),
                    dt=data.get("dt", 0),
                    lat=lat,
                    lon=lon
                )
        except httpx.HTTPError as e:
            print(f"HTTP error fetching soil data: {e}")
            return None
        except Exception as e:
            print(f"Error fetching soil data: {e}")
            return None
    
    async def get_uvi(
        self,
        lat: float,
        lon: float
    ) -> Optional[Dict[str, Any]]:
        """
        Get UV Index data for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            UV Index data or None if request fails
        """
        if not self.is_available():
            return None
            
        url = f"{self.base_url}/uvi"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "uvi": data.get("uvi", 0),
                    "dt": data.get("dt", 0),
                    "lat": lat,
                    "lon": lon
                }
        except httpx.HTTPError as e:
            print(f"HTTP error fetching UVI data: {e}")
            return None
        except Exception as e:
            print(f"Error fetching UVI data: {e}")
            return None
    
    async def get_ndvi_history(
        self,
        polygon_id: str,
        start: int,
        end: int
    ) -> Optional[list]:
        """
        Get NDVI (vegetation index) history for a polygon
        
        Args:
            polygon_id: ID of the polygon
            start: Start timestamp
            end: End timestamp
            
        Returns:
            List of NDVI data points or None
        """
        if not self.is_available():
            return None
            
        url = f"{self.base_url}/ndvi/history"
        params = {
            "polyid": polygon_id,
            "start": start,
            "end": end,
            "appid": self.api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error fetching NDVI history: {e}")
            return None
        except Exception as e:
            print(f"Error fetching NDVI history: {e}")
            return None
    
    def calculate_health_recommendation(
        self,
        aqi: int,
        temperature: float,
        humidity: float,
        soil_moisture: float
    ) -> Dict[str, Any]:
        """
        Calculate health and environmental recommendations
        
        Args:
            aqi: Air Quality Index (1-5 scale)
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            soil_moisture: Soil moisture value
            
        Returns:
            Dictionary with recommendations
        """
        # AQI level and recommendation
        aqi_levels = {
            1: ("Good", "Air quality is considered satisfactory, and air pollution poses little or no risk."),
            2: ("Fair", "Air quality is acceptable. However, there may be a risk for some people."),
            3: ("Moderate", "Members of sensitive groups may experience health effects."),
            4: ("Poor", "Everyone may begin to experience health effects."),
            5: ("Very Poor", "Health warnings of emergency conditions. Everyone is more likely to be affected.")
        }
        
        aqi_level, aqi_recommendation = aqi_levels.get(aqi, ("Unknown", "No data available"))
        
        # Heat stress level
        if temperature >= 40:
            heat_level = "Extreme"
            heat_recommendation = "Avoid outdoor activities. Stay in air-conditioned spaces."
        elif temperature >= 35:
            heat_level = "High"
            heat_recommendation = "Limit outdoor activities. Stay hydrated and seek shade."
        elif temperature >= 30:
            heat_level = "Moderate"
            heat_recommendation = "Take precautions during outdoor activities."
        else:
            heat_level = "Low"
            heat_recommendation = "Comfortable conditions for outdoor activities."
        
        # Vegetation recommendation based on soil moisture
        if soil_moisture < 0.1:
            vegetation_status = "Very Dry"
            vegetation_recommendation = "Urgent irrigation needed. Consider drought-resistant plants."
        elif soil_moisture < 0.3:
            vegetation_status = "Dry"
            vegetation_recommendation = "Regular watering recommended. Good for xerophytic plants."
        elif soil_moisture < 0.5:
            vegetation_status = "Moderate"
            vegetation_recommendation = "Suitable for most vegetation. Optimal planting conditions."
        else:
            vegetation_status = "Moist"
            vegetation_recommendation = "Good moisture levels. Ideal for green coverage expansion."
        
        return {
            "air_quality": {
                "level": aqi_level,
                "recommendation": aqi_recommendation
            },
            "heat_stress": {
                "level": heat_level,
                "recommendation": heat_recommendation
            },
            "vegetation": {
                "status": vegetation_status,
                "recommendation": vegetation_recommendation
            },
            "overall_risk": self._calculate_overall_risk(aqi, temperature, humidity)
        }
    
    def _calculate_overall_risk(
        self,
        aqi: int,
        temperature: float,
        humidity: float
    ) -> str:
        """Calculate overall environmental risk level"""
        risk_score = 0
        
        # AQI contribution
        risk_score += (aqi - 1) * 2
        
        # Temperature contribution
        if temperature >= 40:
            risk_score += 4
        elif temperature >= 35:
            risk_score += 3
        elif temperature >= 30:
            risk_score += 2
        elif temperature >= 25:
            risk_score += 1
        
        # Humidity contribution (extreme values are bad)
        if humidity < 30 or humidity > 80:
            risk_score += 2
        elif humidity < 40 or humidity > 70:
            risk_score += 1
        
        if risk_score >= 8:
            return "Extreme"
        elif risk_score >= 6:
            return "High"
        elif risk_score >= 4:
            return "Medium"
        else:
            return "Low"


# Singleton instance
_agromonitoring_service: Optional[AgromonitoringService] = None


def get_agromonitoring_service() -> AgromonitoringService:
    """Get or create the agromonitoring service singleton"""
    global _agromonitoring_service
    if _agromonitoring_service is None:
        _agromonitoring_service = AgromonitoringService()
    return _agromonitoring_service
