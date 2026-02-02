"""
Weather Service for HeatWise
Integrates with OpenWeatherMap API to fetch real-time weather and air pollution data
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class WeatherData:
    """Weather data structure"""
    temperature: float
    feels_like: float
    humidity: float
    pressure: float
    wind_speed: float
    wind_deg: int
    clouds: int
    visibility: int
    weather_main: str
    weather_description: str
    weather_icon: str
    dt: int
    sunrise: int
    sunset: int
    city_name: str
    country: str
    lat: float
    lon: float


@dataclass
class AirPollutionData:
    """Air pollution data structure"""
    aqi: int  # Air Quality Index (1-5)
    co: float  # Carbon Monoxide
    no: float  # Nitrogen Monoxide
    no2: float  # Nitrogen Dioxide
    o3: float  # Ozone
    so2: float  # Sulphur Dioxide
    pm2_5: float  # Fine particles
    pm10: float  # Coarse particles
    nh3: float  # Ammonia
    dt: int
    lat: float
    lon: float


class WeatherService:
    """Service to fetch weather and air pollution data from OpenWeatherMap"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")
        
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY is not set in environment variables")
    
    async def get_current_weather(
        self, 
        lat: float, 
        lon: float,
        units: str = "metric",
        lang: str = "en"
    ) -> Optional[WeatherData]:
        """
        Get current weather data for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            units: Temperature units (metric, imperial, standard)
            lang: Language for weather descriptions
            
        Returns:
            WeatherData object or None if request fails
        """
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": units,
            "lang": lang
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                return WeatherData(
                    temperature=data["main"]["temp"],
                    feels_like=data["main"]["feels_like"],
                    humidity=data["main"]["humidity"],
                    pressure=data["main"]["pressure"],
                    wind_speed=data["wind"]["speed"],
                    wind_deg=data["wind"].get("deg", 0),
                    clouds=data["clouds"]["all"],
                    visibility=data.get("visibility", 10000),
                    weather_main=data["weather"][0]["main"],
                    weather_description=data["weather"][0]["description"],
                    weather_icon=data["weather"][0]["icon"],
                    dt=data["dt"],
                    sunrise=data["sys"]["sunrise"],
                    sunset=data["sys"]["sunset"],
                    city_name=data["name"],
                    country=data["sys"]["country"],
                    lat=data["coord"]["lat"],
                    lon=data["coord"]["lon"]
                )
        except httpx.HTTPError as e:
            print(f"HTTP error fetching weather: {e}")
            return None
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
    
    async def get_air_pollution(
        self,
        lat: float,
        lon: float
    ) -> Optional[AirPollutionData]:
        """
        Get current air pollution data for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            AirPollutionData object or None if request fails
        """
        url = f"{self.base_url}/air_pollution"
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
                
                pollution = data["list"][0]
                components = pollution["components"]
                
                return AirPollutionData(
                    aqi=pollution["main"]["aqi"],
                    co=components["co"],
                    no=components["no"],
                    no2=components["no2"],
                    o3=components["o3"],
                    so2=components["so2"],
                    pm2_5=components["pm2_5"],
                    pm10=components["pm10"],
                    nh3=components["nh3"],
                    dt=pollution["dt"],
                    lat=data["coord"]["lat"],
                    lon=data["coord"]["lon"]
                )
        except httpx.HTTPError as e:
            print(f"HTTP error fetching air pollution: {e}")
            return None
        except Exception as e:
            print(f"Error fetching air pollution: {e}")
            return None
    
    async def get_weather_by_city(
        self,
        city_name: str,
        country_code: str = "",
        units: str = "metric",
        lang: str = "en"
    ) -> Optional[WeatherData]:
        """
        Get current weather data by city name
        
        Args:
            city_name: Name of the city
            country_code: ISO 3166 country code (optional)
            units: Temperature units
            lang: Language
            
        Returns:
            WeatherData object or None if request fails
        """
        url = f"{self.base_url}/weather"
        q = f"{city_name},{country_code}" if country_code else city_name
        params = {
            "q": q,
            "appid": self.api_key,
            "units": units,
            "lang": lang
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                return WeatherData(
                    temperature=data["main"]["temp"],
                    feels_like=data["main"]["feels_like"],
                    humidity=data["main"]["humidity"],
                    pressure=data["main"]["pressure"],
                    wind_speed=data["wind"]["speed"],
                    wind_deg=data["wind"].get("deg", 0),
                    clouds=data["clouds"]["all"],
                    visibility=data.get("visibility", 10000),
                    weather_main=data["weather"][0]["main"],
                    weather_description=data["weather"][0]["description"],
                    weather_icon=data["weather"][0]["icon"],
                    dt=data["dt"],
                    sunrise=data["sys"]["sunrise"],
                    sunset=data["sys"]["sunset"],
                    city_name=data["name"],
                    country=data["sys"]["country"],
                    lat=data["coord"]["lat"],
                    lon=data["coord"]["lon"]
                )
        except httpx.HTTPError as e:
            print(f"HTTP error fetching weather by city: {e}")
            return None
        except Exception as e:
            print(f"Error fetching weather by city: {e}")
            return None
    
    async def get_forecast(
        self,
        lat: float,
        lon: float,
        units: str = "metric",
        lang: str = "en"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get 5-day weather forecast (3-hour intervals)
        
        Args:
            lat: Latitude
            lon: Longitude
            units: Temperature units
            lang: Language
            
        Returns:
            List of forecast data or None if request fails
        """
        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": units,
            "lang": lang
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                forecasts = []
                for item in data["list"]:
                    forecasts.append({
                        "dt": item["dt"],
                        "dt_txt": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "feels_like": item["main"]["feels_like"],
                        "humidity": item["main"]["humidity"],
                        "pressure": item["main"]["pressure"],
                        "weather_main": item["weather"][0]["main"],
                        "weather_description": item["weather"][0]["description"],
                        "weather_icon": item["weather"][0]["icon"],
                        "wind_speed": item["wind"]["speed"],
                        "clouds": item["clouds"]["all"],
                        "pop": item.get("pop", 0)  # Probability of precipitation
                    })
                
                return forecasts
        except httpx.HTTPError as e:
            print(f"HTTP error fetching forecast: {e}")
            return None
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None
    
    async def get_complete_weather_data(
        self,
        lat: float,
        lon: float,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        Get complete weather data including current weather and air pollution
        
        Args:
            lat: Latitude
            lon: Longitude
            units: Temperature units
            
        Returns:
            Dictionary with weather and air pollution data
        """
        weather = await self.get_current_weather(lat, lon, units)
        air_pollution = await self.get_air_pollution(lat, lon)
        
        result = {
            "weather": None,
            "air_pollution": None,
            "combined": None
        }
        
        if weather:
            result["weather"] = {
                "temperature": weather.temperature,
                "feels_like": weather.feels_like,
                "humidity": weather.humidity,
                "pressure": weather.pressure,
                "wind_speed": weather.wind_speed,
                "wind_deg": weather.wind_deg,
                "clouds": weather.clouds,
                "visibility": weather.visibility,
                "weather_main": weather.weather_main,
                "weather_description": weather.weather_description,
                "weather_icon": weather.weather_icon,
                "city_name": weather.city_name,
                "country": weather.country,
                "lat": weather.lat,
                "lon": weather.lon,
                "dt": weather.dt,
                "sunrise": weather.sunrise,
                "sunset": weather.sunset
            }
        
        if air_pollution:
            result["air_pollution"] = {
                "aqi": air_pollution.aqi,
                "aqi_label": self._get_aqi_label(air_pollution.aqi),
                "co": air_pollution.co,
                "no": air_pollution.no,
                "no2": air_pollution.no2,
                "o3": air_pollution.o3,
                "so2": air_pollution.so2,
                "pm2_5": air_pollution.pm2_5,
                "pm10": air_pollution.pm10,
                "nh3": air_pollution.nh3,
                "lat": air_pollution.lat,
                "lon": air_pollution.lon,
                "dt": air_pollution.dt
            }
        
        # Combine for heat risk calculation
        if weather and air_pollution:
            result["combined"] = {
                "temperature": weather.temperature,
                "humidity": weather.humidity,
                "aqi": air_pollution.aqi,
                "pm2_5": air_pollution.pm2_5,
                "pm10": air_pollution.pm10,
                "heat_risk": self._calculate_heat_risk(weather.temperature, weather.humidity, air_pollution.aqi)
            }
        
        return result
    
    def _get_aqi_label(self, aqi: int) -> str:
        """Convert AQI number to descriptive label"""
        labels = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        return labels.get(aqi, "Unknown")
    
    def _calculate_heat_risk(self, temperature: float, humidity: float, aqi: int) -> str:
        """Calculate heat risk level based on temperature, humidity, and AQI"""
        # Heat index calculation (simplified)
        heat_index = temperature + 0.5 * humidity / 10
        
        # Adjust for air quality
        if aqi >= 4:
            heat_index += 3
        elif aqi >= 3:
            heat_index += 1.5
        
        if heat_index >= 42:
            return "Extreme"
        elif heat_index >= 38:
            return "High"
        elif heat_index >= 34:
            return "Medium"
        else:
            return "Low"


# Singleton instance
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Get or create the weather service singleton"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
