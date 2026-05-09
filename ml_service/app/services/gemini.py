"""
Google Gemini AI Service for HeatWise
Provides intelligent analysis and chatbot capabilities
Using the new google-genai package with multiple model fallbacks
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("WARNING: google-genai not installed. Run: pip install google-genai")

# Model priority list - try these in order (use full model path)
GEMINI_MODELS = [
    "models/gemini-flash-latest",      # Latest flash - works!
    "models/gemini-2.0-flash-lite",    # Lite version
    "models/gemini-2.0-flash",         # Standard 2.0 flash
    "models/gemini-pro-latest",        # Pro latest
    "models/gemma-3-27b-it",           # Gemma fallback
]


class GeminiService:
    """Service for Google Gemini AI integration"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.client = None
        self.current_model = GEMINI_MODELS[0]
        self.last_error = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("Gemini AI service initialized successfully!")
            except Exception as e:
                print(f"WARNING: Failed to initialize Gemini: {e}")
                self.last_error = str(e)
        else:
            if not GEMINI_AVAILABLE:
                print("WARNING: Gemini library not available")
            if not self.api_key:
                print("WARNING: GOOGLE_API_KEY not set")
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.client is not None
    
    async def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Generate content with model fallback and retry logic"""
        if not self.is_available():
            return None
        
        for model in GEMINI_MODELS:
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    self.current_model = model
                    self.last_error = None
                    return response.text
                    
                except Exception as e:
                    error_str = str(e)
                    self.last_error = error_str
                    
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        # Quota exceeded - try next model
                        print(f"Quota exceeded for {model}, trying next model...")
                        break  # Move to next model
                    elif "400" in error_str or "INVALID" in error_str:
                        # Invalid request - try next model
                        print(f"Invalid request for {model}: {e}")
                        break
                    else:
                        # Other error - retry with delay
                        print(f"Attempt {attempt + 1} failed for {model}: {e}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    async def generate_urban_heat_analysis(
        self,
        place_name: str,
        temperature: float,
        humidity: float,
        feels_like: float,
        aqi: int,
        aqi_label: str,
        pm25: float,
        pm10: float,
        soil_moisture: float,
        soil_temperature: float
    ) -> Dict[str, Any]:
        """
        Generate comprehensive urban heat island analysis using Gemini AI
        """
        if not self.is_available():
            return self._generate_fallback_analysis(
                temperature, humidity, aqi, soil_moisture, place_name
            )
        
        prompt = f"""You are an expert urban planner and environmental scientist specializing in Urban Heat Island (UHI) mitigation and green city development in Southeast Asia, particularly Indonesia.

Based on the following real-time environmental data for {place_name}, provide a comprehensive analysis in JSON format:

## Current Environmental Data:
- Location: {place_name}
- Air Temperature: {temperature}°C
- Feels Like: {feels_like}°C  
- Humidity: {humidity}%
- Air Quality Index: {aqi} ({aqi_label})
- PM2.5: {pm25} μg/m³
- PM10: {pm10} μg/m³
- Soil Moisture: {soil_moisture:.4f}
- Soil Temperature: {soil_temperature}°C

## Analysis Required:

Please provide analysis in the following JSON structure:
{{
    "current_green_canopy": <estimated current green canopy percentage based on data indicators>,
    "target_green_canopy": <recommended target based on WHO/Singapore green city standards>,
    "green_deficit": <difference>,
    "uhi_intensity": "<classification: Minimal/Mild/Moderate/Severe with temperature difference estimate>",
    "trees_to_plant": <realistic number based on urban area calculation>,
    "recommended_species": [
        {{
            "name": "<Indonesian/Latin tree name>",
            "cooling_effect": "<Low/Medium/High/Very High>",
            "canopy_size": "<Small/Medium/Large/Very Large>",
            "growth_rate": "<Slow/Medium/Fast/Very Fast>"
        }}
    ],
    "planting_priority_zones": ["<zone 1>", "<zone 2>", ...],
    "short_term_plan": {{
        "timeframe": "1-2 Years",
        "actions": ["<action 1>", "<action 2>", ...]
    }},
    "medium_term_plan": {{
        "timeframe": "2-3 Years", 
        "actions": ["<action 1>", "<action 2>", ...]
    }},
    "long_term_plan": {{
        "timeframe": "3-5+ Years",
        "actions": ["<action 1>", "<action 2>", ...]
    }},
    "estimated_temperature_reduction": <degrees Celsius>,
    "estimated_aqi_improvement": <number of AQI levels>,
    "estimated_energy_savings": "<percentage range and description>",
    "estimated_health_benefits": "<description of health improvements>",
    "health_risk_analysis": {{
        "respiratory_risk": "<Low/Moderate/High description>",
        "heat_stress_risk": "<Low/Moderate/High description>",
        "vulnerable_groups_advice": "<Specific advice for children/elderly>",
        "long_term_exposure_impact": "<Potential long term health effects based on current data>"
    }},
    "total_investment_estimate": "<cost estimate in USD>",
    "carbon_sequestration_potential": "<tonnes CO2 per year>"
}}

Important considerations:
1. Use realistic calculations based on Indonesian urban context (dense population, tropical climate)
2. Recommend native Indonesian trees (Trembesi, Beringin, Mahoni, Angsana, Ketapang, Flamboyan, etc.)
3. Consider the current AQI and heat data when estimating green coverage
4. Base tree numbers on realistic urban area (assume 500 hectares for city area analysis)
5. Use WHO/Singapore green city standards (25-30% canopy coverage target)
6. High temperature + low soil moisture = lower current green coverage
7. High AQI = need for more pollution-absorbing trees

Return ONLY valid JSON, no markdown formatting or explanation."""

        try:
            result_text = await self._generate_with_retry(prompt)
            
            if result_text is None:
                print(f"All models failed. Last error: {self.last_error}")
                return self._generate_fallback_analysis(
                    temperature, humidity, aqi, soil_moisture, place_name
                )
            
            # Clean up response (remove markdown if present)
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            result["_generated_by"] = f"Gemini AI ({self.current_model})"
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gemini response: {e}")
            return self._generate_fallback_analysis(
                temperature, humidity, aqi, soil_moisture, place_name
            )
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_fallback_analysis(
                temperature, humidity, aqi, soil_moisture, place_name
            )
    
    async def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Chat with Gemini AI as an environmental expert assistant
        """
        if not self.is_available():
            return "I apologize, but the AI service is currently unavailable. Please try again later."
        
        system_prompt = """You are WISE-AI, the environmental assistant for HeatWise — an urban heat monitoring app for Indonesian cities.

Your expertise: Urban Heat Island (UHI) analysis, green infrastructure, air quality, climate adaptation, and public health in tropical cities.

RESPONSE RULES:
1. ALWAYS respond in English — never switch to Indonesian or any other language, regardless of the user's input language
2. Keep responses CONCISE — maximum 150-200 words
3. Use markdown formatting: **bold** for key terms, bullet points for lists, ### for section headers
4. Give specific, actionable advice — not generic essays
5. Focus on Indonesian/Southeast Asian context (Jakarta, Surabaya, Bandung, etc.)
6. Reference data standards (WHO, EPA) only when directly relevant
7. If asked about a specific topic, answer ONLY that topic — do not add unrelated information
8. End with ONE short follow-up question if appropriate

TONE: Professional but approachable. Like a knowledgeable urban planner talking to a city official."""

        # Add context if available
        context_str = ""
        if context:
            context_str = f"\\n\\nCurrent environmental context:\\n"
            if context.get("location"):
                context_str += f"- Location: {context['location']}\\n"
            if context.get("temperature"):
                context_str += f"- Temperature: {context['temperature']}°C\\n"
            if context.get("humidity"):
                context_str += f"- Humidity: {context['humidity']}%\\n"
            if context.get("aqi"):
                context_str += f"- Air Quality Index: {context['aqi']}\\n"
        
        full_prompt = f"{system_prompt}{context_str}\\n\\nUser: {message}"
        
        try:
            response = await self._generate_with_retry(full_prompt)
            
            if response is None:
                error_msg = "API quota exceeded" if "RESOURCE_EXHAUSTED" in (self.last_error or "") else "service error"
                return f"I apologize, but I'm currently experiencing {error_msg}. Please try again in a few minutes. In the meantime, I can tell you that HeatWise helps monitor urban heat islands and air quality to provide actionable insights for city planners and residents."
            
            return response
        except Exception as e:
            print(f"Gemini chat error: {e}")
            return f"I'm sorry, I encountered an error: {str(e)[:100]}. Please try again."
    
    def _generate_fallback_analysis(
        self,
        temperature: float,
        humidity: float,
        aqi: int,
        soil_moisture: float,
        place_name: str
    ) -> Dict[str, Any]:
        """
        Generate fallback analysis when Gemini is not available
        Uses improved heuristic calculations
        """
        # Estimate current green canopy based on environmental indicators
        base_canopy = 18.0
        
        # Temperature factor: above 30°C suggests less vegetation
        temp_factor = max(-8, min(5, (28 - temperature) * 0.4))
        
        # Humidity factor: higher humidity often correlates with more vegetation
        humidity_factor = max(-3, min(3, (humidity - 65) * 0.05))
        
        # AQI factor: better air quality suggests more trees
        aqi_factor = (3 - aqi) * 1.5
        
        # Soil moisture factor
        moisture_factor = max(-4, min(4, (soil_moisture - 0.25) * 15))
        
        current_canopy = base_canopy + temp_factor + humidity_factor + aqi_factor + moisture_factor
        current_canopy = round(max(8, min(32, current_canopy)), 1)
        
        # Target based on conditions
        if temperature > 33 or aqi >= 3:
            target_canopy = 30.0  # Singapore standard
        elif temperature > 30:
            target_canopy = 25.0  # European standard
        else:
            target_canopy = 20.0  # WHO minimum
        
        if target_canopy <= current_canopy:
            target_canopy = current_canopy + 5
        
        green_deficit = round(target_canopy - current_canopy, 1)
        
        # UHI intensity
        if temperature > 34 and current_canopy < 15:
            uhi_intensity = "Severe (3-5°C above rural areas)"
        elif temperature > 31 and current_canopy < 20:
            uhi_intensity = "Moderate (2-3°C above rural areas)"
        elif temperature > 29:
            uhi_intensity = "Mild (1-2°C above rural areas)"
        else:
            uhi_intensity = "Minimal (<1°C above rural areas)"
        
        # Calculate trees (40 trees per 1% canopy per 100 hectares, assume 500 hectares)
        trees_to_plant = int(green_deficit * 200)
        
        # Tree selection based on conditions
        if temperature > 33 and humidity < 65:
            species = [
                {"name": "Trembesi (Samanea saman)", "cooling_effect": "Very High", "canopy_size": "Very Large", "growth_rate": "Fast"},
                {"name": "Mahoni (Swietenia macrophylla)", "cooling_effect": "High", "canopy_size": "Large", "growth_rate": "Medium"},
                {"name": "Angsana (Pterocarpus indicus)", "cooling_effect": "Very High", "canopy_size": "Large", "growth_rate": "Medium"},
                {"name": "Flamboyan (Delonix regia)", "cooling_effect": "High", "canopy_size": "Large", "growth_rate": "Fast"},
                {"name": "Ketapang (Terminalia catappa)", "cooling_effect": "High", "canopy_size": "Large", "growth_rate": "Fast"}
            ]
        else:
            species = [
                {"name": "Beringin (Ficus benjamina)", "cooling_effect": "Very High", "canopy_size": "Very Large", "growth_rate": "Fast"},
                {"name": "Kenari (Canarium commune)", "cooling_effect": "High", "canopy_size": "Large", "growth_rate": "Medium"},
                {"name": "Kiara Payung (Filicium decipiens)", "cooling_effect": "High", "canopy_size": "Medium", "growth_rate": "Slow"},
                {"name": "Tanjung (Mimusops elengi)", "cooling_effect": "Medium", "canopy_size": "Medium", "growth_rate": "Slow"},
                {"name": "Kersen (Muntingia calabura)", "cooling_effect": "Medium", "canopy_size": "Small", "growth_rate": "Very Fast"}
            ]
        
        temp_reduction = round(green_deficit * 0.12, 1)
        aqi_improvement = min(1, int(green_deficit / 8))
        
        return {
            "current_green_canopy": f"{current_canopy}%",
            "target_green_canopy": f"{target_canopy}%",
            "green_deficit": f"{green_deficit}%",
            "uhi_intensity": uhi_intensity,
            "trees_to_plant": trees_to_plant,
            "recommended_species": species,
            "planting_priority_zones": [
                "Industrial buffer zones along major roads",
                "Commercial districts and parking areas",
                "School grounds and hospital surroundings",
                "Residential neighborhood streets",
                "Public parks and recreational areas",
                "Riverbank and water body corridors"
            ],
            "short_term_plan": {
                "timeframe": "1-2 Years",
                "actions": [
                    "Establish pocket parks in high-temperature urban zones",
                    "Implement cool pavement materials on priority roads",
                    "Install reflective/cool roof coatings on public buildings",
                    "Deploy urban shade structures in pedestrian areas",
                    "Create green walls on south-facing building facades",
                    "Promote public transportation to reduce emissions"
                ]
            },
            "medium_term_plan": {
                "timeframe": "2-3 Years",
                "actions": [
                    "Mandate green building standards for new constructions",
                    "Establish urban cooling centers in each district",
                    "Enhance waterways for evaporative cooling",
                    "Install district cooling systems in commercial areas",
                    "Develop comprehensive UHI mitigation strategy",
                    "Create urban forests (2+ hectares each)"
                ]
            },
            "long_term_plan": {
                "timeframe": "3-5+ Years",
                "actions": [
                    "Achieve target canopy coverage through continued planting",
                    "Invest in innovative heat mitigation R&D",
                    "Implement sustainable urban development policies",
                    "Develop green-blue infrastructure networks",
                    "Establish urban agriculture zones",
                    "Create climate-resilient urban design guidelines",
                    "Monitor UHI via satellite thermal imaging"
                ]
            },
            "estimated_temperature_reduction": temp_reduction,
            "estimated_aqi_improvement": aqi_improvement,
            "estimated_energy_savings": f"{int(temp_reduction * 8)}-{int(temp_reduction * 12)}% reduction in cooling energy",
            "estimated_health_benefits": "Reduced heat-related illness risk and improved respiratory health",
            "health_risk_analysis": {
                "respiratory_risk": "Moderate - reduce exposure during peak hours",
                "heat_stress_risk": "Moderate - ensure hydration and shade access",
                "vulnerable_groups_advice": "Elderly and children should minimize outdoor activities at midday",
                "long_term_exposure_impact": "Potential for increased respiratory sensitivity and heart strain"
            },
            "total_investment_estimate": f"${trees_to_plant * 50 + 500000:,} (phased over 5 years)",
            "carbon_sequestration_potential": f"{int(trees_to_plant * 22 / 1000)} tonnes CO2/year at maturity"
        }


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
