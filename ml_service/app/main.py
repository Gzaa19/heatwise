import os
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime
import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.schemas import EnvironmentalData, PredictionResult, WeatherPredictionRequest
from app.schemas import HeatDataResponse, AnalyticsResponse, ChatMessage, ChatResponse
from app.services.predictor import HeatWisePredictor
from app.controllers.weather import router as weather_router
from app.controllers.geocoding import router as geocoding_router
from app.controllers.analysis import router as analysis_router
from app.controllers.chatbot import router as chatbot_router

load_dotenv()

predictor: Optional[HeatWisePredictor] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor
    print("\n" + "=" * 60)
    print("HeatWise ML Service - Starting Up")
    print("=" * 60 + "\n")
    
    predictor = HeatWisePredictor()
    
    if predictor.is_ready():
        print("\nService is ready to accept predictions!")
    else:
        print("\nService started but model is not available.")
        print("   Run 'python train_model.py' to generate the model.")
    
    print("\n" + "=" * 60 + "\n")
    
    yield
    
    print("\nHeatWise ML Service - Shutting Down\n")


app = FastAPI(
    title="HeatWise ML Service",
    description="Air Quality Index (AQI) Prediction Microservice for HeatWise using TensorFlow",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5000",
        os.getenv("BACKEND_URL", ""),
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather_router)
app.include_router(geocoding_router)
app.include_router(analysis_router)
app.include_router(chatbot_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "HeatWise ML Service",
        "version": "1.0.0",
        "status": "healthy",
        "model_ready": predictor.is_ready() if predictor else False
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": predictor.is_ready() if predictor else False,
        "endpoints": [
            "/", "/health", "/predict", "/predict/weather",
            "/api/weather/current", "/api/weather/city/{city_name}",
            "/api/weather/air-pollution", "/api/weather/complete",
            "/api/weather/forecast", "/api/weather/jabodetabek", "/api/weather/jakarta"
        ]
    }


@app.post("/predict", response_model=PredictionResult, tags=["Prediction"])
async def predict_aqi(data: EnvironmentalData):
    global predictor
    
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Service is not initialized. Please restart the service."
        )
    
    if not predictor.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please run 'python train_model.py' to train and save the model."
        )
    
    try:
        result = predictor.predict(data)
        return PredictionResult(**result)
        
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/weather", response_model=PredictionResult, tags=["Prediction"])
async def predict_from_weather_data(request: WeatherPredictionRequest):
    global predictor
    
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Service is not initialized. Please restart the service."
        )
    
    if not predictor.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please run 'python train_model.py' to train and save the model."
        )
    
    try:
        air_pollution = request.air_pollution
        weather = request.weather
        
        env_data = EnvironmentalData(
            temperature=weather.get('temperature', 25.0),
            humidity=weather.get('humidity', 50.0),
            co=air_pollution.get('co', 0.0),
            no2=air_pollution.get('no2', 0.0),
            o3=air_pollution.get('o3', 0.0),
            pm2_5=air_pollution.get('pm2_5', air_pollution.get('pm25', 0.0)),
            pm10=air_pollution.get('pm10', 0.0)
        )
        
        result = predictor.predict(env_data)
        return PredictionResult(**result)
        
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# Mock data generation functions
def generate_mock_heat_data():
    """Generate mock heat data for Jakarta districts"""
    districts = [
        {"name": "Central Jakarta", "lat": -6.2088, "lon": 106.8456, "population": 1000000},
        {"name": "North Jakarta", "lat": -6.1214, "lon": 106.9069, "population": 1500000},
        {"name": "West Jakarta", "lat": -6.1702, "lon": 106.7903, "population": 2200000},
        {"name": "South Jakarta", "lat": -6.2615, "lon": 106.8106, "population": 2800000},
        {"name": "East Jakarta", "lat": -6.2349, "lon": 106.9251, "population": 3000000},
        {"name": "Thousand Islands", "lat": -5.3333, "lon": 106.5833, "population": 20000}
    ]
    
    data = []
    risk_levels = ["Low", "Medium", "High", "Extreme"]
    
    for district in districts:
        temp = random.uniform(28.0, 38.0)
        risk_level = "Low"
        if temp >= 35:
            risk_level = "Extreme"
        elif temp >= 33:
            risk_level = "High"
        elif temp >= 30:
            risk_level = "Medium"
        
        data.append({
            "district": district["name"],
            "lat": district["lat"],
            "lon": district["lon"],
            "temperature": round(temp, 1),
            "risk_level": risk_level,
            "aqi": round(random.uniform(30, 150), 1),
            "population": district["population"],
            "green_coverage": round(random.uniform(15, 45), 1),
            "humidity": round(random.uniform(60, 85), 1),
            "wind_speed": round(random.uniform(5, 15), 1)
        })
    
    return data

def generate_mock_analytics():
    """Generate mock analytics data"""
    heat_data = generate_mock_heat_data()
    
    high_risk_count = sum(1 for d in heat_data if d["risk_level"] in ["High", "Extreme"])
    avg_temp = sum(d["temperature"] for d in heat_data) / len(heat_data)
    avg_aqi = sum(d["aqi"] for d in heat_data) / len(heat_data)
    population_at_risk = sum(d["population"] for d in heat_data if d["risk_level"] in ["High", "Extreme"])
    
    recommendations = [
        "Increase green coverage in Central Jakarta by 15%",
        "Implement cool roof technologies in high-risk areas",
        "Install smart irrigation systems in residential zones",
        "Establish cooling centers in South and East Jakarta",
        "Promote vertical gardens in dense urban areas"
    ]
    
    return {
        "total_districts": len(heat_data),
        "high_risk_areas": high_risk_count,
        "average_temperature": round(avg_temp, 1),
        "average_aqi": round(avg_aqi, 1),
        "total_population_at_risk": population_at_risk,
        "recommendations": random.sample(recommendations, 3),
        "trends": {
            "temperature_change_24h": round(random.uniform(-2, 3), 1),
            "aqi_change_24h": round(random.uniform(-10, 10), 1)
        }
    }

def generate_mock_chat_response(message: str, context: dict = None):
    """Generate mock AI chat responses"""
    responses = [
        "Based on current temperature data, I recommend increasing green coverage in Central Jakarta by 15% to reduce urban heat island effect.",
        "The heat risk level in your area is currently HIGH. Consider implementing cool roof technologies and increasing tree planting in residential areas.",
        "I suggest installing 50 smart irrigation systems in high-risk districts. This could reduce local temperatures by 2-3°C during peak hours.",
        "Analysis shows that areas with >30% green coverage have 4°C lower temperatures. Focus on vertical gardens and rooftop planting.",
        "Consider implementing heat-reflective pavement materials in high-traffic areas. This could reduce surface temperatures by 5-8°C.",
        "Based on population density and heat exposure, prioritize cooling centers in South Jakarta and East Jakarta districts.",
        "I recommend establishing 25 new community gardens in high-risk areas. This will provide both cooling and social benefits.",
        "Smart building design with proper insulation and ventilation could reduce indoor temperatures by 3-5°C without additional energy consumption."
    ]
    
    recommendations = [
        "Increase green coverage by 15%",
        "Install vertical gardens",
        "Implement rooftop planting",
        "Use cool roof technologies",
        "Establish community gardens",
        "Install smart irrigation systems",
        "Implement heat-reflective materials",
        "Create cooling centers"
    ]
    
    sources = [
        "Jakarta Environmental Agency",
        "Urban Heat Island Study 2024",
        "WHO Guidelines",
        "Local Climate Data",
        "Satellite Temperature Analysis"
    ]
    
    return {
        "response": random.choice(responses),
        "recommendations": random.sample(recommendations, 3),
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "sources": random.sample(sources, 2)
    }


# New endpoints for HeatWise platform
@app.get("/api/heat-data", response_model=HeatDataResponse, tags=["Heat Data"])
async def get_heat_data():
    """Get heat data for all Jakarta districts"""
    try:
        data = generate_mock_heat_data()
        
        # Calculate summary
        summary = {}
        for risk_level in ["Low", "Medium", "High", "Extreme"]:
            summary[risk_level] = sum(1 for d in data if d["risk_level"] == risk_level)
        
        return HeatDataResponse(
            data=data,
            summary=summary,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate heat data: {str(e)}")


@app.get("/api/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_analytics():
    """Get analytics data for dashboard"""
    try:
        analytics = generate_mock_analytics()
        return AnalyticsResponse(**analytics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_ai(chat_message: ChatMessage):
    """Chat with WISE-AI assistant (Legacy endpoint - use /api/chat/message instead)"""
    from app.services.gemini import get_gemini_service
    
    try:
        gemini_service = get_gemini_service()
        
        if gemini_service.is_available():
            # Use Gemini AI
            response = await gemini_service.chat(
                message=chat_message.message,
                context=chat_message.context
            )
            return ChatResponse(
                response=response,
                recommendations=[],
                confidence=0.95,
                sources=["Google Gemini AI", "Environmental Data"]
            )
        else:
            # Fallback to mock
            response_data = generate_mock_chat_response(chat_message.message, chat_message.context)
            return ChatResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.get("/api/health", tags=["Health"])
async def api_health_check():
    """Health check endpoint for the API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "ml_model": predictor.is_ready() if predictor else False,
            "data_generation": True,
            "chat_service": True
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("ML_SERVICE_PORT", 8000))
    host = os.getenv("ML_SERVICE_HOST", "0.0.0.0")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
