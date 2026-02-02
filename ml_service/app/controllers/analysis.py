"""
Location Analysis Controller for HeatWise
Comprehensive analysis endpoint with SOP-based recommendations
Based on WHO AQI Guidelines, EPA Heat Index, and Green City Standards
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
import math

from app.services.weather import get_weather_service
from app.services.geocoding import get_geocoding_service
from app.services.agromonitoring import get_agromonitoring_service
from app.services.gemini import get_gemini_service


# ============================================
# SOP-BASED STANDARDS (WHO, EPA, Green City)
# ============================================

# WHO Air Quality Index Guidelines (AQI 1-5 scale from OpenWeatherMap)
WHO_AQI_STANDARDS = {
    1: {
        "level": "Good",
        "pm25_range": "0-12 μg/m³",
        "health_implications": "Air quality is satisfactory, and air pollution poses little or no risk.",
        "cautionary_statement": "None required.",
        "outdoor_activity": "Ideal for all outdoor activities."
    },
    2: {
        "level": "Fair",
        "pm25_range": "12-35 μg/m³",
        "health_implications": "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.",
        "cautionary_statement": "Unusually sensitive people should consider reducing prolonged outdoor exertion.",
        "outdoor_activity": "Suitable for most outdoor activities."
    },
    3: {
        "level": "Moderate",
        "pm25_range": "35-55 μg/m³",
        "health_implications": "Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
        "cautionary_statement": "Active children and adults, and people with respiratory disease, should limit prolonged outdoor exertion.",
        "outdoor_activity": "Reduce prolonged outdoor activities for sensitive groups."
    },
    4: {
        "level": "Poor",
        "pm25_range": "55-150 μg/m³",
        "health_implications": "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.",
        "cautionary_statement": "Active children and adults, and people with respiratory disease, should avoid prolonged outdoor exertion; everyone else should limit prolonged outdoor exertion.",
        "outdoor_activity": "Limit all outdoor activities. Wear N95 mask if necessary."
    },
    5: {
        "level": "Very Poor",
        "pm25_range": ">150 μg/m³",
        "health_implications": "Health warnings of emergency conditions. The entire population is more likely to be affected.",
        "cautionary_statement": "Everyone should avoid all outdoor exertion.",
        "outdoor_activity": "Avoid all outdoor activities. Stay indoors with air purification."
    }
}

# EPA Heat Index Categories (°C)
EPA_HEAT_INDEX = {
    "extreme_danger": {"min": 54, "label": "Extreme Danger", "risk": "Heat stroke highly likely"},
    "danger": {"min": 41, "label": "Danger", "risk": "Heat cramps and heat exhaustion likely; heat stroke possible with prolonged exposure"},
    "extreme_caution": {"min": 32, "label": "Extreme Caution", "risk": "Heat cramps and heat exhaustion possible with prolonged exposure"},
    "caution": {"min": 27, "label": "Caution", "risk": "Fatigue possible with prolonged exposure"},
    "safe": {"min": 0, "label": "Safe", "risk": "No significant risk from heat"}
}

# Urban Green Coverage Standards (from various city planning guidelines)
GREEN_COVERAGE_STANDARDS = {
    "minimum": 15,  # WHO minimum urban green space
    "target": 25,   # European Environment Agency target
    "optimal": 30,  # Singapore green city standard
    "exemplary": 40 # Leading green cities (Vienna, Singapore)
}

# Tree species database for Indonesia/Southeast Asia
TREE_SPECIES_DATABASE = {
    "tropical_hot_dry": [
        {"name": "Trembesi (Samanea saman)", "cooling_effect": "Very High", "canopy_size": "Large", "growth_rate": "Fast"},
        {"name": "Mahoni (Swietenia macrophylla)", "cooling_effect": "High", "canopy_size": "Large", "growth_rate": "Medium"},
        {"name": "Flamboyan (Delonix regia)", "cooling_effect": "High", "canopy_size": "Large", "growth_rate": "Fast"},
        {"name": "Ketapang (Terminalia catappa)", "cooling_effect": "High", "canopy_size": "Large", "growth_rate": "Fast"},
        {"name": "Angsana (Pterocarpus indicus)", "cooling_effect": "Very High", "canopy_size": "Very Large", "growth_rate": "Medium"}
    ],
    "tropical_hot_humid": [
        {"name": "Beringin (Ficus benjamina)", "cooling_effect": "Very High", "canopy_size": "Very Large", "growth_rate": "Fast"},
        {"name": "Kenari (Canarium commune)", "cooling_effect": "High", "canopy_size": "Large", "growth_rate": "Medium"},
        {"name": "Kiara Payung (Filicium decipiens)", "cooling_effect": "High", "canopy_size": "Medium", "growth_rate": "Slow"},
        {"name": "Tanjung (Mimusops elengi)", "cooling_effect": "Medium", "canopy_size": "Medium", "growth_rate": "Slow"},
        {"name": "Kersen (Muntingia calabura)", "cooling_effect": "Medium", "canopy_size": "Small", "growth_rate": "Very Fast"}
    ],
    "moderate": [
        {"name": "Tabebuya (Tabebuia rosea)", "cooling_effect": "Medium", "canopy_size": "Medium", "growth_rate": "Fast"},
        {"name": "Glodogan (Polyalthia longifolia)", "cooling_effect": "Medium", "canopy_size": "Medium", "growth_rate": "Medium"},
        {"name": "Bungur (Lagerstroemia speciosa)", "cooling_effect": "Medium", "canopy_size": "Medium", "growth_rate": "Medium"},
        {"name": "Sengon (Paraserianthes falcataria)", "cooling_effect": "High", "canopy_size": "Large", "growth_rate": "Very Fast"},
        {"name": "Akasia (Acacia auriculiformis)", "cooling_effect": "Medium", "canopy_size": "Medium", "growth_rate": "Fast"}
    ]
}


# Request/Response Models
class LocationAnalysisRequest(BaseModel):
    lat: float = Field(..., description="Latitude", ge=-90, le=90)
    lon: float = Field(..., description="Longitude", ge=-180, le=180)


class WeatherInfo(BaseModel):
    city_name: str
    temperature: float
    feels_like: float
    humidity: float
    description: str
    wind_speed: float
    pressure: float
    visibility: int
    clouds: int
    sunrise: int
    sunset: int


class AirPollutionInfo(BaseModel):
    aqi: int
    aqi_label: str
    dominant_pollutant: str
    category: str
    co: float
    no: float
    no2: float
    o3: float
    so2: float
    pm2_5: float
    pm10: float
    nh3: float


class SoilInfo(BaseModel):
    moisture: float
    temperature: float


class HealthRecommendation(BaseModel):
    """WHO/EPA based health recommendations"""
    air_quality_level: str
    air_quality_implications: str
    air_quality_cautionary: str
    outdoor_activity_advice: str
    heat_index_level: str
    heat_risk: str
    overall_risk: str
    sensitive_groups_advice: str


class TreeSpecies(BaseModel):
    name: str
    cooling_effect: str
    canopy_size: str
    growth_rate: str


class InfrastructurePlan(BaseModel):
    timeframe: str
    actions: List[str]


class AIAnalysisResult(BaseModel):
    """Comprehensive AI-based urban heat mitigation analysis"""
    # Current Situation
    current_green_canopy: float
    target_green_canopy: float
    green_deficit: float
    uhi_intensity: str  # Urban Heat Island intensity
    
    # Tree Planting Plan
    trees_to_plant: int
    recommended_species: List[TreeSpecies]
    planting_priority_zones: List[str]
    estimated_canopy_increase: float
    
    # Infrastructure Development Plans
    short_term_plan: InfrastructurePlan  # 1-2 years
    medium_term_plan: InfrastructurePlan  # 2-3 years
    long_term_plan: InfrastructurePlan  # 3-5+ years
    
    # Expected Benefits
    estimated_temperature_reduction: float
    estimated_aqi_improvement: int
    estimated_energy_savings: str
    estimated_health_benefits: str
    
    # Implementation
    total_investment_estimate: str
    carbon_sequestration_potential: str


class LocationAnalysisResponse(BaseModel):
    lat: float
    lon: float
    place_name: str
    formatted_address: str
    weather: Optional[WeatherInfo] = None
    air_pollution: Optional[AirPollutionInfo] = None
    soil: Optional[SoilInfo] = None
    health_recommendation: Optional[HealthRecommendation] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Create router
router = APIRouter(prefix="/api/analysis", tags=["Location Analysis"])


def calculate_heat_index(temperature: float, humidity: float) -> float:
    """
    Calculate Heat Index using Steadman's formula (simplified)
    Based on NOAA/NWS Heat Index calculation
    """
    T = temperature
    R = humidity
    
    # Simple approximation for Heat Index
    HI = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094))
    
    if HI >= 27:
        # Rothfusz regression equation
        HI = (-8.78469475556 + 
              1.61139411 * T + 
              2.33854883889 * R - 
              0.14611605 * T * R - 
              0.012308094 * T**2 - 
              0.0164248277778 * R**2 + 
              0.002211732 * T**2 * R + 
              0.00072546 * T * R**2 - 
              0.000003582 * T**2 * R**2)
    
    return round(HI, 1)


def get_heat_index_category(heat_index: float) -> Dict[str, str]:
    """Get EPA Heat Index category"""
    if heat_index >= 54:
        return {"level": "Extreme Danger", "risk": "Heat stroke highly likely. Avoid all outdoor exposure."}
    elif heat_index >= 41:
        return {"level": "Danger", "risk": "Heat cramps and heat exhaustion likely; heat stroke possible with prolonged exposure."}
    elif heat_index >= 32:
        return {"level": "Extreme Caution", "risk": "Heat cramps and heat exhaustion possible. Limit outdoor activities."}
    elif heat_index >= 27:
        return {"level": "Caution", "risk": "Fatigue possible with prolonged exposure. Stay hydrated."}
    else:
        return {"level": "Safe", "risk": "No significant heat-related health risk."}


def get_who_aqi_recommendation(aqi: int) -> Dict[str, str]:
    """Get WHO-based AQI health recommendations"""
    return WHO_AQI_STANDARDS.get(aqi, WHO_AQI_STANDARDS[3])


def get_dominant_pollutant(pollution_data: dict) -> str:
    """Determine the dominant pollutant based on concentration thresholds"""
    pollutants = {
        "pm2_5": pollution_data.get("pm2_5", 0),
        "pm10": pollution_data.get("pm10", 0),
        "o3": pollution_data.get("o3", 0),
        "no2": pollution_data.get("no2", 0),
        "so2": pollution_data.get("so2", 0),
        "co": pollution_data.get("co", 0)
    }
    return max(pollutants, key=pollutants.get).upper()


def calculate_overall_risk(aqi: int, heat_index: float) -> str:
    """Calculate overall environmental health risk"""
    aqi_score = (aqi - 1) * 2  # 0-8 points
    
    heat_score = 0
    if heat_index >= 54:
        heat_score = 4
    elif heat_index >= 41:
        heat_score = 3
    elif heat_index >= 32:
        heat_score = 2
    elif heat_index >= 27:
        heat_score = 1
    
    total_score = aqi_score + heat_score
    
    if total_score >= 10:
        return "Extreme"
    elif total_score >= 7:
        return "High"
    elif total_score >= 4:
        return "Moderate"
    else:
        return "Low"


def generate_comprehensive_ai_analysis(
    temperature: float,
    humidity: float,
    aqi: int,
    soil_moisture: float,
    pm25: float,
    pm10: float,
    place_name: str
) -> AIAnalysisResult:
    """
    Generate comprehensive AI-based urban heat mitigation analysis
    Based on actual environmental data and urban planning standards
    """
    
    # Calculate Heat Index
    heat_index = calculate_heat_index(temperature, humidity)
    
    # Estimate current green canopy (based on temperature, humidity, AQI)
    # Lower temps and better AQI suggest more vegetation
    base_canopy = 20.0
    temp_adjustment = max(-10, min(10, (30 - temperature) * 0.5))
    aqi_adjustment = max(-5, (3 - aqi) * 2)
    humidity_adjustment = max(-3, min(3, (humidity - 60) * 0.1))
    moisture_adjustment = max(-5, min(5, (soil_moisture - 0.3) * 20))
    
    current_canopy = round(base_canopy + temp_adjustment + aqi_adjustment + humidity_adjustment + moisture_adjustment, 1)
    current_canopy = max(5, min(35, current_canopy))
    
    # Target based on green city standards
    if temperature > 35:
        target_canopy = GREEN_COVERAGE_STANDARDS["optimal"]  # 30%
    elif temperature > 30:
        target_canopy = GREEN_COVERAGE_STANDARDS["target"]  # 25%
    else:
        target_canopy = GREEN_COVERAGE_STANDARDS["minimum"]  # 15%
    
    # Ensure target is higher than current
    if target_canopy <= current_canopy:
        target_canopy = current_canopy + 5
    
    green_deficit = round(target_canopy - current_canopy, 1)
    
    # UHI Intensity classification
    if temperature > 35 and current_canopy < 15:
        uhi_intensity = "Severe (3-5°C above rural areas)"
    elif temperature > 32 and current_canopy < 20:
        uhi_intensity = "Moderate (2-3°C above rural areas)"
    elif temperature > 30:
        uhi_intensity = "Mild (1-2°C above rural areas)"
    else:
        uhi_intensity = "Minimal (<1°C above rural areas)"
    
    # Calculate trees needed
    # Standard: ~40 mature trees provide 1% canopy coverage per hectare
    # Assume urban area of 500 hectares
    area_hectares = 500
    trees_per_percent = 40 * area_hectares / 100
    trees_to_plant = int(green_deficit * trees_per_percent)
    
    # Select appropriate tree species
    if temperature > 35 and humidity < 60:
        climate_type = "tropical_hot_dry"
    elif temperature > 28:
        climate_type = "tropical_hot_humid"
    else:
        climate_type = "moderate"
    
    recommended_species = [
        TreeSpecies(**species) for species in TREE_SPECIES_DATABASE[climate_type][:5]
    ]
    
    # Priority zones for planting
    planting_priority_zones = []
    if aqi >= 3:
        planting_priority_zones.append("Industrial buffer zones and main road corridors")
    if temperature > 33:
        planting_priority_zones.append("Commercial districts and parking areas")
    if heat_index > 35:
        planting_priority_zones.append("School grounds and hospital surroundings")
    planting_priority_zones.extend([
        "Residential neighborhood streets",
        "Public parks and recreational areas",
        "Riverbank and water body corridors"
    ])
    
    # Infrastructure Development Plans
    short_term_plan = InfrastructurePlan(
        timeframe="1-2 Years",
        actions=[
            "Establish pocket parks and green corridors in high-temperature zones",
            "Implement cool pavement materials on priority roads to reduce heat absorption",
            "Install reflective/cool roof coatings on public buildings",
            "Deploy urban shade structures (pergolas, shade sails) in pedestrian areas",
            "Create green walls and vertical gardens on south-facing building facades",
            "Encourage public transportation, walking, and cycling to reduce emissions"
        ]
    )
    
    medium_term_plan = InfrastructurePlan(
        timeframe="2-3 Years",
        actions=[
            "Implement mandatory green building standards for new constructions",
            "Establish urban cooling centers in each sub-district",
            "Enhance urban waterways and water bodies for evaporative cooling",
            "Install district cooling systems in commercial areas",
            "Develop comprehensive urban heat mitigation strategy across all sectors",
            "Create urban forests in available land plots (minimum 2 hectares each)"
        ]
    )
    
    long_term_plan = InfrastructurePlan(
        timeframe="3-5+ Years",
        actions=[
            "Continue tree planting to achieve target canopy coverage",
            "Invest in R&D for innovative heat mitigation technologies",
            "Implement policies promoting sustainable urban development",
            "Develop integrated green-blue infrastructure networks",
            "Establish urban agriculture zones for local food production",
            "Create climate-resilient urban design guidelines for future development",
            "Monitor and evaluate UHI reduction through satellite thermal imaging"
        ]
    )
    
    # Expected Benefits Calculations
    # Each 10% increase in canopy = ~1°C temperature reduction
    temp_reduction = round(green_deficit * 0.1, 1)
    
    # AQI improvement estimate
    aqi_improvement = min(1, int(green_deficit / 10))
    
    # Energy savings estimate (AC usage reduction)
    if temp_reduction >= 2:
        energy_savings = "20-30% reduction in cooling energy demand"
    elif temp_reduction >= 1:
        energy_savings = "10-20% reduction in cooling energy demand"
    else:
        energy_savings = "5-10% reduction in cooling energy demand"
    
    # Health benefits based on improvements
    if green_deficit > 10:
        health_benefits = "Significant reduction in heat-related illnesses and respiratory issues"
    elif green_deficit > 5:
        health_benefits = "Moderate improvement in public health outcomes"
    else:
        health_benefits = "Incremental improvement in air quality and thermal comfort"
    
    # Investment estimate (rough calculation)
    # ~$50 per tree (including planting and 3-year maintenance)
    tree_investment = trees_to_plant * 50
    infrastructure_investment = area_hectares * 1000  # $1000/hectare for cool pavements etc
    total_investment = tree_investment + infrastructure_investment
    
    if total_investment > 10000000:
        investment_str = f"${total_investment/1000000:.1f} million (phased over 5 years)"
    else:
        investment_str = f"${total_investment/1000:.0f}K (phased over 3 years)"
    
    # Carbon sequestration
    # Average tree sequesters ~22kg CO2 per year
    annual_carbon = trees_to_plant * 22 / 1000  # tonnes
    carbon_str = f"{annual_carbon:.0f} tonnes CO2 sequestered annually at maturity"
    
    return AIAnalysisResult(
        current_green_canopy=current_canopy,
        target_green_canopy=target_canopy,
        green_deficit=green_deficit,
        uhi_intensity=uhi_intensity,
        trees_to_plant=trees_to_plant,
        recommended_species=recommended_species,
        planting_priority_zones=planting_priority_zones[:6],
        estimated_canopy_increase=green_deficit,
        short_term_plan=short_term_plan,
        medium_term_plan=medium_term_plan,
        long_term_plan=long_term_plan,
        estimated_temperature_reduction=temp_reduction,
        estimated_aqi_improvement=aqi_improvement,
        estimated_energy_savings=energy_savings,
        estimated_health_benefits=health_benefits,
        total_investment_estimate=investment_str,
        carbon_sequestration_potential=carbon_str
    )


@router.get("/location", response_model=LocationAnalysisResponse)
async def analyze_location(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180)
):
    """
    Get comprehensive analysis for a location
    Combines weather, air pollution, soil data with WHO/EPA-based recommendations
    """
    try:
        # Initialize services
        weather_service = get_weather_service()
        geocoding_service = get_geocoding_service()
        agro_service = get_agromonitoring_service()
        
        # Get place name from reverse geocoding
        geocode_result = await geocoding_service.reverse_geocode(lat, lon)
        place_name = "Unknown Location"
        formatted_address = f"{lat}, {lon}"
        
        if geocode_result:
            place_name = geocode_result.city or geocode_result.state or "Unknown"
            formatted_address = geocode_result.formatted
        
        # Get weather data
        weather_data = await weather_service.get_current_weather(lat, lon)
        weather_info = None
        if weather_data:
            weather_info = WeatherInfo(
                city_name=weather_data.city_name,
                temperature=weather_data.temperature,
                feels_like=weather_data.feels_like,
                humidity=weather_data.humidity,
                description=weather_data.weather_description,
                wind_speed=weather_data.wind_speed,
                pressure=weather_data.pressure,
                visibility=weather_data.visibility,
                clouds=weather_data.clouds,
                sunrise=weather_data.sunrise,
                sunset=weather_data.sunset
            )
        
        # Get air pollution data
        pollution_data = await weather_service.get_air_pollution(lat, lon)
        air_pollution_info = None
        if pollution_data:
            aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            pollution_dict = {
                "pm2_5": pollution_data.pm2_5,
                "pm10": pollution_data.pm10,
                "o3": pollution_data.o3,
                "no2": pollution_data.no2,
                "so2": pollution_data.so2,
                "co": pollution_data.co
            }
            
            air_pollution_info = AirPollutionInfo(
                aqi=pollution_data.aqi,
                aqi_label=aqi_labels.get(pollution_data.aqi, "Unknown"),
                dominant_pollutant=get_dominant_pollutant(pollution_dict),
                category=WHO_AQI_STANDARDS.get(pollution_data.aqi, {}).get("level", "Unknown"),
                co=pollution_data.co,
                no=pollution_data.no,
                no2=pollution_data.no2,
                o3=pollution_data.o3,
                so2=pollution_data.so2,
                pm2_5=pollution_data.pm2_5,
                pm10=pollution_data.pm10,
                nh3=pollution_data.nh3
            )
        
        # Get soil data
        soil_data = await agro_service.get_soil_data(lat, lon)
        soil_info = None
        if soil_data:
            soil_info = SoilInfo(
                moisture=round(soil_data.moisture, 4),
                temperature=soil_data.temperature_celsius
            )
        
        # Calculate WHO/EPA-based health recommendations
        health_rec = None
        if weather_data and pollution_data:
            heat_index = calculate_heat_index(weather_data.temperature, weather_data.humidity)
            heat_category = get_heat_index_category(heat_index)
            who_aqi = get_who_aqi_recommendation(pollution_data.aqi)
            overall_risk = calculate_overall_risk(pollution_data.aqi, heat_index)
            
            # Sensitive groups advice
            if overall_risk in ["High", "Extreme"]:
                sensitive_advice = "Children, elderly, pregnant women, and those with respiratory/cardiovascular conditions should remain indoors with air conditioning."
            elif overall_risk == "Moderate":
                sensitive_advice = "Sensitive individuals should limit outdoor exposure during peak heat hours (11AM-4PM)."
            else:
                sensitive_advice = "Normal outdoor activities are generally safe for all groups."
            
            health_rec = HealthRecommendation(
                air_quality_level=who_aqi["level"],
                air_quality_implications=who_aqi["health_implications"],
                air_quality_cautionary=who_aqi["cautionary_statement"],
                outdoor_activity_advice=who_aqi["outdoor_activity"],
                heat_index_level=heat_category["level"],
                heat_risk=heat_category["risk"],
                overall_risk=overall_risk,
                sensitive_groups_advice=sensitive_advice
            )
        
        return LocationAnalysisResponse(
            lat=lat,
            lon=lon,
            place_name=place_name,
            formatted_address=formatted_address,
            weather=weather_info,
            air_pollution=air_pollution_info,
            soil=soil_info,
            health_recommendation=health_rec
        )
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/generate")
async def generate_analysis(request: LocationAnalysisRequest):
    """
    Generate comprehensive AI-based green city analysis
    Uses Google Gemini AI for intelligent recommendations
    """
    try:
        weather_service = get_weather_service()
        agro_service = get_agromonitoring_service()
        gemini_service = get_gemini_service()
        
        # Get weather and pollution data
        weather = await weather_service.get_current_weather(request.lat, request.lon)
        pollution = await weather_service.get_air_pollution(request.lat, request.lon)
        soil = await agro_service.get_soil_data(request.lat, request.lon)
        
        if not weather or not pollution:
            raise HTTPException(status_code=404, detail="Could not fetch data for this location")
        
        # AQI labels
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        
        # Generate comprehensive analysis using Gemini AI
        analysis = await gemini_service.generate_urban_heat_analysis(
            place_name=weather.city_name,
            temperature=weather.temperature,
            humidity=weather.humidity,
            feels_like=weather.feels_like,
            aqi=pollution.aqi,
            aqi_label=aqi_labels.get(pollution.aqi, "Unknown"),
            pm25=pollution.pm2_5,
            pm10=pollution.pm10,
            soil_moisture=soil.moisture if soil else 0.3,
            soil_temperature=soil.temperature_celsius if soil else 25.0
        )
        
        return analysis
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis generation failed: {str(e)}")


@router.get("/quick")
async def quick_analysis(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180)
):
    """
    Quick analysis returning essential data only
    """
    try:
        weather_service = get_weather_service()
        geocoding_service = get_geocoding_service()
        
        # Get place name
        geocode = await geocoding_service.reverse_geocode(lat, lon)
        place_name = geocode.city if geocode else "Unknown"
        
        # Get weather
        weather = await weather_service.get_current_weather(lat, lon)
        pollution = await weather_service.get_air_pollution(lat, lon)
        
        return {
            "lat": lat,
            "lon": lon,
            "place_name": place_name,
            "temperature": weather.temperature if weather else None,
            "humidity": weather.humidity if weather else None,
            "aqi": pollution.aqi if pollution else None,
            "weather_description": weather.weather_description if weather else None,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")
