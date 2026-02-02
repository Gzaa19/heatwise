"""
Geocoding Controller/Router for HeatWise
API endpoints for geocoding and reverse geocoding
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.geocoding import get_geocoding_service


# Response Models
class GeocodingResultResponse(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    formatted: str = Field(..., description="Formatted address")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State/Province")
    country: str = Field(..., description="Country name")
    country_code: str = Field(..., description="Country code")
    confidence: int = Field(..., description="Confidence score (1-10)")


class GeocodeResponse(BaseModel):
    query: str
    results: List[GeocodingResultResponse]
    count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReverseGeocodeResponse(BaseModel):
    lat: float
    lng: float
    result: Optional[GeocodingResultResponse] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchGeocodeRequest(BaseModel):
    queries: List[str] = Field(..., description="List of locations to geocode")
    country_code: str = Field("", description="Country code to restrict results")


class BatchGeocodeResponse(BaseModel):
    results: dict
    total_queries: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Create router
router = APIRouter(prefix="/api/geocode", tags=["Geocoding"])


@router.get("/search", response_model=GeocodeResponse)
async def geocode_location(
    q: str = Query(..., description="Location or address to search"),
    country: str = Query("", description="Country code (e.g., ID for Indonesia)"),
    limit: int = Query(5, description="Maximum results", ge=1, le=10)
):
    """
    Geocode a location/address to get coordinates
    """
    try:
        service = get_geocoding_service()
        results = await service.geocode(q, country, limit)
        
        return GeocodeResponse(
            query=q,
            results=[
                GeocodingResultResponse(
                    lat=r.lat,
                    lng=r.lng,
                    formatted=r.formatted,
                    city=r.city,
                    state=r.state,
                    country=r.country,
                    country_code=r.country_code,
                    confidence=r.confidence
                ) for r in results
            ],
            count=len(results)
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {str(e)}")


@router.get("/reverse", response_model=ReverseGeocodeResponse)
async def reverse_geocode(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lng: float = Query(..., description="Longitude", ge=-180, le=180)
):
    """
    Reverse geocode coordinates to get location information
    """
    try:
        service = get_geocoding_service()
        result = await service.reverse_geocode(lat, lng)
        
        response = ReverseGeocodeResponse(lat=lat, lng=lng)
        
        if result:
            response.result = GeocodingResultResponse(
                lat=result.lat,
                lng=result.lng,
                formatted=result.formatted,
                city=result.city,
                state=result.state,
                country=result.country,
                country_code=result.country_code,
                confidence=result.confidence
            )
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reverse geocoding failed: {str(e)}")


@router.post("/batch", response_model=BatchGeocodeResponse)
async def batch_geocode(request: BatchGeocodeRequest):
    """
    Geocode multiple locations at once
    """
    if len(request.queries) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 queries per batch")
    
    try:
        service = get_geocoding_service()
        results = await service.geocode_batch(request.queries, request.country_code)
        
        formatted_results = {}
        for query, geocode_results in results.items():
            formatted_results[query] = [
                {
                    "lat": r.lat,
                    "lng": r.lng,
                    "formatted": r.formatted,
                    "city": r.city,
                    "country": r.country,
                    "confidence": r.confidence
                } for r in geocode_results
            ]
        
        return BatchGeocodeResponse(
            results=formatted_results,
            total_queries=len(request.queries)
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch geocoding failed: {str(e)}")


@router.get("/jakarta-areas")
async def get_jakarta_areas():
    """
    Get predefined Jakarta/Jabodetabek areas with coordinates
    """
    areas = [
        {"id": "central-jakarta", "name": "Jakarta Pusat", "lat": -6.1862, "lng": 106.8456},
        {"id": "south-jakarta", "name": "Jakarta Selatan", "lat": -6.2615, "lng": 106.8106},
        {"id": "north-jakarta", "name": "Jakarta Utara", "lat": -6.1389, "lng": 106.8639},
        {"id": "east-jakarta", "name": "Jakarta Timur", "lat": -6.2250, "lng": 106.9004},
        {"id": "west-jakarta", "name": "Jakarta Barat", "lat": -6.1681, "lng": 106.7658},
        {"id": "tangerang", "name": "Tangerang", "lat": -6.1783, "lng": 106.6319},
        {"id": "tangerang-selatan", "name": "Tangerang Selatan", "lat": -6.3137, "lng": 106.6891},
        {"id": "bekasi", "name": "Bekasi", "lat": -6.2383, "lng": 106.9756},
        {"id": "depok", "name": "Depok", "lat": -6.4025, "lng": 106.7942},
        {"id": "bogor", "name": "Bogor", "lat": -6.5971, "lng": 106.8060},
    ]
    
    return {
        "areas": areas,
        "count": len(areas),
        "region": "Jabodetabek"
    }
