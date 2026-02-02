"""
Weather Controller/Router for HeatWise
API endpoints for weather and air pollution data
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.weather import get_weather_service, WeatherService


# Response Models
class WeatherResponse(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature")
    humidity: float = Field(..., description="Humidity percentage")
    pressure: float = Field(..., description="Atmospheric pressure in hPa")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_deg: int = Field(..., description="Wind direction in degrees")
    clouds: int = Field(..., description="Cloudiness percentage")
    visibility: int = Field(..., description="Visibility in meters")
    weather_main: str = Field(..., description="Weather condition group")
    weather_description: str = Field(..., description="Weather condition description")
    weather_icon: str = Field(..., description="Weather icon code")
    city_name: str = Field(..., description="City name")
    country: str = Field(..., description="Country code")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    dt: int = Field(..., description="Data calculation time (Unix timestamp)")
    sunrise: int = Field(..., description="Sunrise time (Unix timestamp)")
    sunset: int = Field(..., description="Sunset time (Unix timestamp)")


class AirPollutionResponse(BaseModel):
    aqi: int = Field(..., description="Air Quality Index (1-5)")
    aqi_label: str = Field(..., description="AQI label (Good, Fair, Moderate, Poor, Very Poor)")
    co: float = Field(..., description="Carbon Monoxide (μg/m³)")
    no: float = Field(..., description="Nitrogen Monoxide (μg/m³)")
    no2: float = Field(..., description="Nitrogen Dioxide (μg/m³)")
    o3: float = Field(..., description="Ozone (μg/m³)")
    so2: float = Field(..., description="Sulphur Dioxide (μg/m³)")
    pm2_5: float = Field(..., description="Fine particles PM2.5 (μg/m³)")
    pm10: float = Field(..., description="Coarse particles PM10 (μg/m³)")
    nh3: float = Field(..., description="Ammonia (μg/m³)")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    dt: int = Field(..., description="Data timestamp")


class CombinedHeatData(BaseModel):
    temperature: float
    humidity: float
    aqi: int
    pm2_5: float
    pm10: float
    heat_risk: str


class CompleteWeatherResponse(BaseModel):
    weather: Optional[WeatherResponse] = None
    air_pollution: Optional[AirPollutionResponse] = None
    combined: Optional[CombinedHeatData] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ForecastItem(BaseModel):
    dt: int
    dt_txt: str
    temperature: float
    feels_like: float
    humidity: float
    pressure: float
    weather_main: str
    weather_description: str
    weather_icon: str
    wind_speed: float
    clouds: int
    pop: float = Field(..., description="Probability of precipitation")


class ForecastResponse(BaseModel):
    forecasts: List[ForecastItem]
    city: str
    country: str
    lat: float
    lon: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MultiCityWeatherItem(BaseModel):
    city_id: str
    city_name: str
    weather: Optional[WeatherResponse] = None
    air_pollution: Optional[AirPollutionResponse] = None
    heat_risk: Optional[str] = None
    error: Optional[str] = None


class MultiCityWeatherResponse(BaseModel):
    cities: List[MultiCityWeatherItem]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Jakarta/Jabodetabek cities coordinates
JABODETABEK_CITIES = [
    {"id": "central-jakarta", "name": "Jakarta Pusat", "lat": -6.1862, "lon": 106.8456},
    {"id": "south-jakarta", "name": "Jakarta Selatan", "lat": -6.2615, "lon": 106.8106},
    {"id": "north-jakarta", "name": "Jakarta Utara", "lat": -6.1389, "lon": 106.8639},
    {"id": "east-jakarta", "name": "Jakarta Timur", "lat": -6.2250, "lon": 106.9004},
    {"id": "west-jakarta", "name": "Jakarta Barat", "lat": -6.1681, "lon": 106.7658},
    {"id": "tangerang", "name": "Tangerang", "lat": -6.1783, "lon": 106.6319},
    {"id": "tangerang-selatan", "name": "Tangerang Selatan", "lat": -6.3137, "lon": 106.6891},
    {"id": "bekasi", "name": "Bekasi", "lat": -6.2383, "lon": 106.9756},
    {"id": "depok", "name": "Depok", "lat": -6.4025, "lon": 106.7942},
    {"id": "bogor", "name": "Bogor", "lat": -6.5971, "lon": 106.8060},
]


# Create router
router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    units: str = Query("metric", description="Units (metric, imperial, standard)")
):
    """
    Get current weather data for a specific location
    """
    try:
        service = get_weather_service()
        weather = await service.get_current_weather(lat, lon, units)
        
        if not weather:
            raise HTTPException(status_code=404, detail="Weather data not found for this location")
        
        return WeatherResponse(
            temperature=weather.temperature,
            feels_like=weather.feels_like,
            humidity=weather.humidity,
            pressure=weather.pressure,
            wind_speed=weather.wind_speed,
            wind_deg=weather.wind_deg,
            clouds=weather.clouds,
            visibility=weather.visibility,
            weather_main=weather.weather_main,
            weather_description=weather.weather_description,
            weather_icon=weather.weather_icon,
            city_name=weather.city_name,
            country=weather.country,
            lat=weather.lat,
            lon=weather.lon,
            dt=weather.dt,
            sunrise=weather.sunrise,
            sunset=weather.sunset
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")


@router.get("/city/{city_name}", response_model=WeatherResponse)
async def get_weather_by_city(
    city_name: str,
    country_code: str = Query("", description="ISO 3166 country code"),
    units: str = Query("metric", description="Units (metric, imperial, standard)")
):
    """
    Get current weather data by city name
    """
    try:
        service = get_weather_service()
        weather = await service.get_weather_by_city(city_name, country_code, units)
        
        if not weather:
            raise HTTPException(status_code=404, detail=f"Weather data not found for city: {city_name}")
        
        return WeatherResponse(
            temperature=weather.temperature,
            feels_like=weather.feels_like,
            humidity=weather.humidity,
            pressure=weather.pressure,
            wind_speed=weather.wind_speed,
            wind_deg=weather.wind_deg,
            clouds=weather.clouds,
            visibility=weather.visibility,
            weather_main=weather.weather_main,
            weather_description=weather.weather_description,
            weather_icon=weather.weather_icon,
            city_name=weather.city_name,
            country=weather.country,
            lat=weather.lat,
            lon=weather.lon,
            dt=weather.dt,
            sunrise=weather.sunrise,
            sunset=weather.sunset
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")


@router.get("/air-pollution", response_model=AirPollutionResponse)
async def get_air_pollution(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180)
):
    """
    Get current air pollution data for a specific location
    """
    try:
        service = get_weather_service()
        pollution = await service.get_air_pollution(lat, lon)
        
        if not pollution:
            raise HTTPException(status_code=404, detail="Air pollution data not found for this location")
        
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        
        return AirPollutionResponse(
            aqi=pollution.aqi,
            aqi_label=aqi_labels.get(pollution.aqi, "Unknown"),
            co=pollution.co,
            no=pollution.no,
            no2=pollution.no2,
            o3=pollution.o3,
            so2=pollution.so2,
            pm2_5=pollution.pm2_5,
            pm10=pollution.pm10,
            nh3=pollution.nh3,
            lat=pollution.lat,
            lon=pollution.lon,
            dt=pollution.dt
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch air pollution data: {str(e)}")


@router.get("/complete", response_model=CompleteWeatherResponse)
async def get_complete_weather(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    units: str = Query("metric", description="Units (metric, imperial, standard)")
):
    """
    Get complete weather data including current weather, air pollution, and heat risk
    """
    try:
        service = get_weather_service()
        data = await service.get_complete_weather_data(lat, lon, units)
        
        response = CompleteWeatherResponse()
        
        if data["weather"]:
            response.weather = WeatherResponse(**data["weather"])
        
        if data["air_pollution"]:
            response.air_pollution = AirPollutionResponse(**data["air_pollution"])
        
        if data["combined"]:
            response.combined = CombinedHeatData(**data["combined"])
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch complete weather data: {str(e)}")


@router.get("/forecast", response_model=ForecastResponse)
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    units: str = Query("metric", description="Units (metric, imperial, standard)")
):
    """
    Get 5-day weather forecast (3-hour intervals)
    """
    try:
        service = get_weather_service()
        forecasts = await service.get_forecast(lat, lon, units)
        
        if not forecasts:
            raise HTTPException(status_code=404, detail="Forecast data not found for this location")
        
        # Get city info from first forecast
        weather = await service.get_current_weather(lat, lon, units)
        city_name = weather.city_name if weather else "Unknown"
        country = weather.country if weather else "Unknown"
        
        return ForecastResponse(
            forecasts=[ForecastItem(**f) for f in forecasts],
            city=city_name,
            country=country,
            lat=lat,
            lon=lon
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecast data: {str(e)}")


@router.get("/jabodetabek", response_model=MultiCityWeatherResponse)
async def get_jabodetabek_weather():
    """
    Get weather data for all Jabodetabek cities
    """
    try:
        service = get_weather_service()
        cities_data = []
        
        for city in JABODETABEK_CITIES:
            try:
                data = await service.get_complete_weather_data(city["lat"], city["lon"])
                
                item = MultiCityWeatherItem(
                    city_id=city["id"],
                    city_name=city["name"]
                )
                
                if data["weather"]:
                    item.weather = WeatherResponse(**data["weather"])
                
                if data["air_pollution"]:
                    item.air_pollution = AirPollutionResponse(**data["air_pollution"])
                
                if data["combined"]:
                    item.heat_risk = data["combined"]["heat_risk"]
                
                cities_data.append(item)
                
            except Exception as e:
                cities_data.append(MultiCityWeatherItem(
                    city_id=city["id"],
                    city_name=city["name"],
                    error=str(e)
                ))
        
        return MultiCityWeatherResponse(cities=cities_data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Jabodetabek weather data: {str(e)}")


@router.get("/jakarta", response_model=CompleteWeatherResponse)
async def get_jakarta_weather():
    """
    Get current weather data for Jakarta (Central Jakarta)
    """
    # Central Jakarta coordinates
    lat = -6.1862
    lon = 106.8456
    
    try:
        service = get_weather_service()
        data = await service.get_complete_weather_data(lat, lon)
        
        response = CompleteWeatherResponse()
        
        if data["weather"]:
            response.weather = WeatherResponse(**data["weather"])
        
        if data["air_pollution"]:
            response.air_pollution = AirPollutionResponse(**data["air_pollution"])
        
        if data["combined"]:
            response.combined = CombinedHeatData(**data["combined"])
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Jakarta weather data: {str(e)}")
