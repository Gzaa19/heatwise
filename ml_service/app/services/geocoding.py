"""
Geocoding Service for HeatWise
Integrates with OpenCage API for converting addresses/locations to coordinates
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class GeocodingResult:
    """Geocoding result structure"""
    lat: float
    lng: float
    formatted: str
    city: str
    state: str
    country: str
    country_code: str
    confidence: int
    bounds: Optional[Dict[str, float]] = None


class GeocodingService:
    """Service to geocode locations using OpenCage API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENCAGE_API_KEY")
        self.base_url = "https://api.opencagedata.com/geocode/v1/json"
        
        if not self.api_key:
            print("WARNING: OPENCAGE_API_KEY is not set. Geocoding will use mock data.")
    
    async def geocode(
        self, 
        query: str,
        country_code: str = "",
        limit: int = 5
    ) -> List[GeocodingResult]:
        """
        Convert address/location to coordinates
        """
        if not self.api_key:
            # Mock response
            print(f"Mock geocoding for: {query}")
            return [GeocodingResult(
                lat=-6.2088,
                lng=106.8456,
                formatted=f"Mock Address for {query}",
                city="Jakarta",
                state="DKI Jakarta",
                country="Indonesia",
                country_code="ID",
                confidence=10
            )]

        params = {
            "q": query,
            "key": self.api_key,
            "limit": limit,
            "no_annotations": 0
        }
        
        if country_code:
            params["countrycode"] = country_code
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for result in data.get("results", []):
                    geometry = result.get("geometry", {})
                    components = result.get("components", {})
                    
                    bounds = None
                    if "bounds" in result:
                        bounds = {
                            "northeast_lat": result["bounds"]["northeast"]["lat"],
                            "northeast_lng": result["bounds"]["northeast"]["lng"],
                            "southwest_lat": result["bounds"]["southwest"]["lat"],
                            "southwest_lng": result["bounds"]["southwest"]["lng"]
                        }
                    
                    results.append(GeocodingResult(
                        lat=geometry.get("lat", 0),
                        lng=geometry.get("lng", 0),
                        formatted=result.get("formatted", ""),
                        city=components.get("city", components.get("town", components.get("village", ""))),
                        state=components.get("state", ""),
                        country=components.get("country", ""),
                        country_code=components.get("country_code", "").upper(),
                        confidence=result.get("confidence", 0),
                        bounds=bounds
                    ))
                
                return results
        except httpx.HTTPError as e:
            print(f"HTTP error during geocoding: {e}")
            return []
        except Exception as e:
            print(f"Error during geocoding: {e}")
            return []
    
    async def reverse_geocode(
        self,
        lat: float,
        lng: float
    ) -> Optional[GeocodingResult]:
        """
        Convert coordinates to address
        """
        if not self.api_key:
            # Mock response
            return GeocodingResult(
                lat=lat,
                lng=lng,
                formatted="Mock Location",
                city="Unknown City",
                state="Mock State",
                country="Indonesia",
                country_code="ID",
                confidence=5
            )

        params = {
            "q": f"{lat},{lng}",
            "key": self.api_key,
            "no_annotations": 0
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                if not results:
                    return None
                
                result = results[0]
                geometry = result.get("geometry", {})
                components = result.get("components", {})
                
                bounds = None
                if "bounds" in result:
                    bounds = {
                        "northeast_lat": result["bounds"]["northeast"]["lat"],
                        "northeast_lng": result["bounds"]["northeast"]["lng"],
                        "southwest_lat": result["bounds"]["southwest"]["lat"],
                        "southwest_lng": result["bounds"]["southwest"]["lng"]
                    }
                
                return GeocodingResult(
                    lat=geometry.get("lat", lat),
                    lng=geometry.get("lng", lng),
                    formatted=result.get("formatted", ""),
                    city=components.get("city", components.get("town", components.get("village", ""))),
                    state=components.get("state", ""),
                    country=components.get("country", ""),
                    country_code=components.get("country_code", "").upper(),
                    confidence=result.get("confidence", 0),
                    bounds=bounds
                )
        except httpx.HTTPError as e:
            print(f"HTTP error during reverse geocoding: {e}")
            return None
        except Exception as e:
            print(f"Error during reverse geocoding: {e}")
            return None
    
    async def geocode_batch(
        self,
        queries: List[str],
        country_code: str = ""
    ) -> Dict[str, List[GeocodingResult]]:
        """
        Geocode multiple locations
        """
        results = {}
        for query in queries:
            results[query] = await self.geocode(query, country_code)
        return results


# Singleton instance
_geocoding_service: Optional[GeocodingService] = None


def get_geocoding_service() -> GeocodingService:
    """Get or create the geocoding service singleton"""
    global _geocoding_service
    if _geocoding_service is None:
        _geocoding_service = GeocodingService()
    return _geocoding_service
