'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
    ArrowLeft,
    Thermometer,
    Droplets,
    Wind,
    Cloud,
    AlertTriangle,
    Loader2,
    TreePine,
    Factory,
    Heart,
    Sprout,
    Sparkles,
    Sun,
    Leaf,
    Building,
    Clock,
    DollarSign,
    TrendingDown
} from 'lucide-react';

interface WeatherInfo {
    city_name: string;
    temperature: number;
    feels_like: number;
    humidity: number;
    description: string;
    wind_speed: number;
    pressure: number;
    visibility: number;
    clouds: number;
}

interface AirPollutionInfo {
    aqi: number;
    aqi_label: string;
    dominant_pollutant: string;
    category: string;
    co: number;
    no: number;
    no2: number;
    o3: number;
    so2: number;
    pm2_5: number;
    pm10: number;
    nh3: number;
}

interface SoilInfo {
    moisture: number;
    temperature: number;
}

interface HealthRecommendation {
    air_quality_level: string;
    air_quality_implications: string;
    air_quality_cautionary: string;
    outdoor_activity_advice: string;
    heat_index_level: string;
    heat_risk: string;
    overall_risk: string;
    sensitive_groups_advice: string;
}

interface TreeSpecies {
    name: string;
    cooling_effect: string;
    canopy_size: string;
    growth_rate: string;
}

interface InfrastructurePlan {
    timeframe: string;
    actions: string[];
}

interface AIAnalysis {
    current_green_canopy: number;
    target_green_canopy: number;
    green_deficit: number;
    uhi_intensity: string;
    trees_to_plant: number;
    recommended_species: TreeSpecies[];
    planting_priority_zones: string[];
    estimated_canopy_increase: number;
    short_term_plan: InfrastructurePlan;
    medium_term_plan: InfrastructurePlan;
    long_term_plan: InfrastructurePlan;
    estimated_temperature_reduction: number;
    estimated_aqi_improvement: number;
    estimated_energy_savings: string;
    estimated_health_benefits: string;
    total_investment_estimate: string;
    carbon_sequestration_potential: string;
}

interface AnalysisData {
    lat: number;
    lon: number;
    place_name: string;
    formatted_address: string;
    weather: WeatherInfo | null;
    air_pollution: AirPollutionInfo | null;
    soil: SoilInfo | null;
    health_recommendation: HealthRecommendation | null;
}

function AnalysisContent() {
    const searchParams = useSearchParams();
    const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
    const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isGeneratingAI, setIsGeneratingAI] = useState(false);

    const lat = searchParams.get('lat');
    const lng = searchParams.get('lng');

    useEffect(() => {
        const fetchAnalysis = async () => {
            if (!lat || !lng) {
                setError('Missing coordinates');
                setIsLoading(false);
                return;
            }

            try {
                const response = await fetch(
                    `http://localhost:8000/api/analysis/location?lat=${lat}&lon=${lng}`
                );

                if (!response.ok) {
                    throw new Error('Failed to fetch analysis data');
                }

                const data = await response.json();
                setAnalysisData(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'An error occurred');
            } finally {
                setIsLoading(false);
            }
        };

        fetchAnalysis();
    }, [lat, lng]);

    const handleGenerateAI = async () => {
        if (!lat || !lng) return;

        setIsGeneratingAI(true);
        try {
            const response = await fetch(
                `http://localhost:8000/api/analysis/generate`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ lat: parseFloat(lat), lon: parseFloat(lng) })
                }
            );

            if (response.ok) {
                const data = await response.json();
                setAiAnalysis(data);
            }
        } catch (err) {
            console.error('Failed to generate AI analysis:', err);
        } finally {
            setIsGeneratingAI(false);
        }
    };

    const getRiskColor = (risk: string) => {
        switch (risk.toLowerCase()) {
            case 'extreme': case 'extreme danger': return 'bg-red-500 text-white';
            case 'high': case 'danger': case 'poor': return 'bg-orange-500 text-white';
            case 'moderate': case 'extreme caution': case 'fair': return 'bg-yellow-500 text-black';
            case 'low': case 'caution': case 'safe': case 'good': return 'bg-green-500 text-white';
            default: return 'bg-gray-500 text-white';
        }
    };

    const getAQIColor = (aqi: number) => {
        switch (aqi) {
            case 1: return 'text-green-600 bg-green-50 border-green-200';
            case 2: return 'text-yellow-600 bg-yellow-50 border-yellow-200';
            case 3: return 'text-orange-600 bg-orange-50 border-orange-200';
            case 4: return 'text-red-600 bg-red-50 border-red-200';
            case 5: return 'text-purple-600 bg-purple-50 border-purple-200';
            default: return 'text-gray-600 bg-gray-50 border-gray-200';
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-heatwise-primary mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading analysis data...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Card className="w-full max-w-md">
                    <CardContent className="pt-6 text-center">
                        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                        <h2 className="text-xl font-semibold mb-2">Error</h2>
                        <p className="text-muted-foreground mb-4">{error}</p>
                        <Button onClick={() => window.history.back()}>
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            Go Back
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="container mx-auto py-6 px-4 max-w-4xl">
            {/* Header */}
            <div className="mb-6">
                <Button
                    variant="ghost"
                    onClick={() => window.history.back()}
                    className="mb-4"
                >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Map
                </Button>

                <div className="text-center">
                    <h1 className="text-3xl font-bold mb-2">Description Page</h1>
                    <Separator className="my-4" />
                    <div className="flex justify-center gap-8 text-sm">
                        <div>
                            <span className="text-muted-foreground">Latitude: </span>
                            <span className="font-mono">{lat}</span>
                        </div>
                        <div>
                            <span className="text-muted-foreground">Longitude: </span>
                            <span className="font-mono">{lng}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Weather Information */}
            {analysisData?.weather && (
                <Card className="mb-6">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-xl text-heatwise-primary flex items-center gap-2">
                            <Cloud className="h-5 w-5" />
                            Weather Information
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <h3 className="text-2xl font-bold text-center mb-4">
                            {analysisData.weather.city_name || analysisData.place_name}
                        </h3>
                        <Separator className="mb-4" />

                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded">
                                <span className="text-muted-foreground flex items-center gap-2">
                                    <Thermometer className="h-4 w-4" /> Temperature
                                </span>
                                <span className="font-semibold">{analysisData.weather.temperature}°C</span>
                            </div>
                            <div className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded">
                                <span className="text-muted-foreground flex items-center gap-2">
                                    <Droplets className="h-4 w-4" /> Humidity
                                </span>
                                <span className="font-semibold">{analysisData.weather.humidity}%</span>
                            </div>
                            <div className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded">
                                <span className="text-muted-foreground flex items-center gap-2">
                                    <Cloud className="h-4 w-4" /> Description
                                </span>
                                <span className="font-semibold capitalize">{analysisData.weather.description}</span>
                            </div>
                            <div className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded">
                                <span className="text-muted-foreground flex items-center gap-2">
                                    <Wind className="h-4 w-4" /> Wind Speed
                                </span>
                                <span className="font-semibold">{analysisData.weather.wind_speed} m/s</span>
                            </div>
                            <div className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded">
                                <span className="text-muted-foreground">Feels Like</span>
                                <span className="font-semibold">{analysisData.weather.feels_like}°C</span>
                            </div>
                            <div className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded">
                                <span className="text-muted-foreground">Pressure</span>
                                <span className="font-semibold">{analysisData.weather.pressure} hPa</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Air Pollution Information */}
            {analysisData?.air_pollution && (
                <Card className="mb-6">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-xl text-heatwise-primary flex items-center gap-2">
                            <Factory className="h-5 w-5" />
                            Air Pollution Information
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center mb-4">
                            <div className={`inline-block px-6 py-3 rounded-full border-2 ${getAQIColor(analysisData.air_pollution.aqi)}`}>
                                <span className="font-bold text-lg">AQI: {analysisData.air_pollution.aqi}</span>
                                <span className="ml-2">({analysisData.air_pollution.aqi_label})</span>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-sm">
                            <div className="flex justify-between px-3 py-2 bg-gray-50 rounded">
                                <span className="text-muted-foreground">Dominant Pollutant</span>
                                <span className="font-medium">{analysisData.air_pollution.dominant_pollutant}</span>
                            </div>
                            <div className="flex justify-between px-3 py-2 bg-gray-50 rounded">
                                <span className="text-muted-foreground">Category</span>
                                <span className="font-medium">{analysisData.air_pollution.category}</span>
                            </div>
                            <div className="flex justify-between px-3 py-2">
                                <span className="text-muted-foreground">CO</span>
                                <span className="font-medium">{analysisData.air_pollution.co.toFixed(2)} μg/m³</span>
                            </div>
                            <div className="flex justify-between px-3 py-2">
                                <span className="text-muted-foreground">NO</span>
                                <span className="font-medium">{analysisData.air_pollution.no.toFixed(2)} μg/m³</span>
                            </div>
                            <div className="flex justify-between px-3 py-2">
                                <span className="text-muted-foreground">NO₂</span>
                                <span className="font-medium">{analysisData.air_pollution.no2.toFixed(2)} μg/m³</span>
                            </div>
                            <div className="flex justify-between px-3 py-2">
                                <span className="text-muted-foreground">O₃</span>
                                <span className="font-medium">{analysisData.air_pollution.o3.toFixed(2)} μg/m³</span>
                            </div>
                            <div className="flex justify-between px-3 py-2">
                                <span className="text-muted-foreground">SO₂</span>
                                <span className="font-medium">{analysisData.air_pollution.so2.toFixed(2)} μg/m³</span>
                            </div>
                            <div className="flex justify-between px-3 py-2">
                                <span className="text-muted-foreground">PM2.5</span>
                                <span className="font-medium">{analysisData.air_pollution.pm2_5.toFixed(2)} μg/m³</span>
                            </div>
                            <div className="flex justify-between px-3 py-2">
                                <span className="text-muted-foreground">PM10</span>
                                <span className="font-medium">{analysisData.air_pollution.pm10.toFixed(2)} μg/m³</span>
                            </div>
                            <div className="flex justify-between px-3 py-2">
                                <span className="text-muted-foreground">NH₃</span>
                                <span className="font-medium">{analysisData.air_pollution.nh3.toFixed(2)} μg/m³</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Health Recommendation (WHO/EPA Based) */}
            {analysisData?.health_recommendation && (
                <Card className="mb-6 border-l-4 border-l-green-500">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-xl text-green-600 flex items-center gap-2">
                            <Heart className="h-5 w-5" />
                            Health Recommendation
                            <Badge variant="outline" className="ml-2 text-xs">WHO/EPA Standards</Badge>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {/* Overall Risk */}
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="font-medium">Overall Risk Level:</span>
                            <Badge className={getRiskColor(analysisData.health_recommendation.overall_risk)}>
                                {analysisData.health_recommendation.overall_risk}
                            </Badge>
                        </div>

                        {/* Air Quality */}
                        <div className="p-4 bg-blue-50 rounded-lg">
                            <h4 className="font-semibold text-blue-800 mb-2">Air Quality Assessment</h4>
                            <p className="text-sm text-gray-700 mb-2">
                                <strong>Level:</strong> {analysisData.health_recommendation.air_quality_level}
                            </p>
                            <p className="text-sm text-gray-600 mb-2">
                                <strong>Health Implications:</strong> {analysisData.health_recommendation.air_quality_implications}
                            </p>
                            <p className="text-sm text-gray-600">
                                <strong>Outdoor Activity:</strong> {analysisData.health_recommendation.outdoor_activity_advice}
                            </p>
                        </div>

                        {/* Heat Risk */}
                        <div className="p-4 bg-orange-50 rounded-lg">
                            <h4 className="font-semibold text-orange-800 mb-2">Heat Index Assessment</h4>
                            <p className="text-sm text-gray-700 mb-2">
                                <strong>Level:</strong> {analysisData.health_recommendation.heat_index_level}
                            </p>
                            <p className="text-sm text-gray-600">
                                <strong>Risk:</strong> {analysisData.health_recommendation.heat_risk}
                            </p>
                        </div>

                        {/* Sensitive Groups */}
                        <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                            <h4 className="font-semibold text-yellow-800 mb-2 flex items-center gap-2">
                                <AlertTriangle className="h-4 w-4" />
                                Sensitive Groups Advisory
                            </h4>
                            <p className="text-sm text-gray-700">
                                {analysisData.health_recommendation.sensitive_groups_advice}
                            </p>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Soil Data */}
            {analysisData?.soil && (
                <Card className="mb-6">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-xl text-amber-600 flex items-center gap-2">
                            <Sprout className="h-5 w-5" />
                            Soil Data
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 bg-amber-50 rounded-lg text-center">
                                <Droplets className="h-8 w-8 text-amber-600 mx-auto mb-2" />
                                <p className="text-sm text-muted-foreground">Moisture</p>
                                <p className="text-2xl font-bold">{analysisData.soil.moisture.toFixed(4)}</p>
                            </div>
                            <div className="p-4 bg-orange-50 rounded-lg text-center">
                                <Thermometer className="h-8 w-8 text-orange-600 mx-auto mb-2" />
                                <p className="text-sm text-muted-foreground">Temperature</p>
                                <p className="text-2xl font-bold">{analysisData.soil.temperature.toFixed(1)}°C</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* AI Analysis Section */}
            <Card className="mb-6">
                <CardHeader className="pb-3">
                    <CardTitle className="text-xl flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-purple-500" />
                        Google Generative AI Analysis
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {!aiAnalysis ? (
                        <div className="text-center py-8">
                            <p className="text-muted-foreground mb-4">
                                Generate comprehensive urban heat mitigation analysis based on current environmental data
                            </p>
                            <Button
                                size="lg"
                                onClick={handleGenerateAI}
                                disabled={isGeneratingAI}
                                className="bg-heatwise-primary hover:bg-heatwise-primary/90"
                            >
                                {isGeneratingAI ? (
                                    <>
                                        <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                                        Generating Analysis...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="h-5 w-5 mr-2" />
                                        Generate Analysis
                                    </>
                                )}
                            </Button>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            <div className="text-center">
                                <h3 className="text-2xl font-bold mb-2">Analysis Results</h3>
                                <Separator />
                            </div>

                            {/* Current Green Situation */}
                            <div className="bg-gray-50 rounded-lg p-5">
                                <h4 className="font-bold text-lg text-center mb-4 flex items-center justify-center gap-2">
                                    <Leaf className="h-5 w-5 text-green-600" />
                                    Current Green Situation
                                </h4>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                                    <div className="p-3 bg-white rounded-lg shadow-sm">
                                        <p className="text-xs text-muted-foreground">Current Canopy</p>
                                        <p className="text-xl font-bold text-green-600">{aiAnalysis.current_green_canopy}%</p>
                                    </div>
                                    <div className="p-3 bg-white rounded-lg shadow-sm">
                                        <p className="text-xs text-muted-foreground">Target Canopy</p>
                                        <p className="text-xl font-bold text-blue-600">{aiAnalysis.target_green_canopy}%</p>
                                    </div>
                                    <div className="p-3 bg-white rounded-lg shadow-sm">
                                        <p className="text-xs text-muted-foreground">Green Deficit</p>
                                        <p className="text-xl font-bold text-red-600">{aiAnalysis.green_deficit}%</p>
                                    </div>
                                    <div className="p-3 bg-white rounded-lg shadow-sm">
                                        <p className="text-xs text-muted-foreground">UHI Intensity</p>
                                        <p className="text-sm font-medium">{aiAnalysis.uhi_intensity}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Tree Planting Plan */}
                            <div className="bg-green-50 rounded-lg p-5">
                                <h4 className="font-bold text-lg text-center mb-4 flex items-center justify-center gap-2">
                                    <TreePine className="h-5 w-5 text-green-700" />
                                    Tree Planting Plan
                                </h4>
                                <Separator className="my-3" />

                                <div className="text-center mb-4">
                                    <p className="text-sm text-muted-foreground">Trees to be planted:</p>
                                    <p className="text-3xl font-bold text-green-700">{aiAnalysis.trees_to_plant.toLocaleString()}</p>
                                </div>

                                <div className="mb-4">
                                    <p className="font-medium mb-2">Recommended Species (Southeast Asia Native):</p>
                                    <div className="grid gap-2">
                                        {aiAnalysis.recommended_species.map((species, idx) => (
                                            <div key={idx} className="flex items-center justify-between p-2 bg-white rounded text-sm">
                                                <span className="font-medium">{species.name}</span>
                                                <div className="flex gap-2 text-xs">
                                                    <Badge variant="outline">{species.cooling_effect}</Badge>
                                                    <Badge variant="secondary">{species.growth_rate}</Badge>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <p className="font-medium mb-2">Priority Planting Zones:</p>
                                    <ul className="space-y-1 text-sm text-muted-foreground">
                                        {aiAnalysis.planting_priority_zones.map((zone, idx) => (
                                            <li key={idx}>• {zone}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {/* Infrastructure Development Plans */}
                            <div className="space-y-4">
                                {/* Short Term */}
                                <div className="bg-blue-50 rounded-lg p-5">
                                    <h4 className="font-bold text-lg mb-3 flex items-center gap-2">
                                        <Clock className="h-5 w-5 text-blue-600" />
                                        {aiAnalysis.short_term_plan.timeframe} Infrastructural Development Plan
                                    </h4>
                                    <Separator className="mb-3" />
                                    <ul className="space-y-2 text-sm">
                                        {aiAnalysis.short_term_plan.actions.map((action, idx) => (
                                            <li key={idx} className="flex items-start gap-2">
                                                <span className="text-blue-600">•</span>
                                                <span>{action}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Medium Term */}
                                <div className="bg-indigo-50 rounded-lg p-5">
                                    <h4 className="font-bold text-lg mb-3 flex items-center gap-2">
                                        <Building className="h-5 w-5 text-indigo-600" />
                                        {aiAnalysis.medium_term_plan.timeframe} Infrastructural Development Plan
                                    </h4>
                                    <Separator className="mb-3" />
                                    <ul className="space-y-2 text-sm">
                                        {aiAnalysis.medium_term_plan.actions.map((action, idx) => (
                                            <li key={idx} className="flex items-start gap-2">
                                                <span className="text-indigo-600">•</span>
                                                <span>{action}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Long Term */}
                                <div className="bg-purple-50 rounded-lg p-5">
                                    <h4 className="font-bold text-lg mb-3 flex items-center gap-2">
                                        <Sun className="h-5 w-5 text-purple-600" />
                                        {aiAnalysis.long_term_plan.timeframe} Long-Term Plan
                                    </h4>
                                    <Separator className="mb-3" />
                                    <ul className="space-y-2 text-sm">
                                        {aiAnalysis.long_term_plan.actions.map((action, idx) => (
                                            <li key={idx} className="flex items-start gap-2">
                                                <span className="text-purple-600">•</span>
                                                <span>{action}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {/* Expected Benefits */}
                            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-5">
                                <h4 className="font-bold text-lg text-center mb-4 flex items-center justify-center gap-2">
                                    <TrendingDown className="h-5 w-5 text-green-600" />
                                    Expected Benefits
                                </h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="p-3 bg-white rounded-lg text-center">
                                        <Thermometer className="h-6 w-6 text-red-500 mx-auto mb-1" />
                                        <p className="text-xs text-muted-foreground">Temperature Reduction</p>
                                        <p className="text-lg font-bold">{aiAnalysis.estimated_temperature_reduction}°C</p>
                                    </div>
                                    <div className="p-3 bg-white rounded-lg text-center">
                                        <Factory className="h-6 w-6 text-blue-500 mx-auto mb-1" />
                                        <p className="text-xs text-muted-foreground">AQI Improvement</p>
                                        <p className="text-lg font-bold">{aiAnalysis.estimated_aqi_improvement} level(s)</p>
                                    </div>
                                    <div className="p-3 bg-white rounded-lg text-center col-span-2">
                                        <Leaf className="h-6 w-6 text-green-500 mx-auto mb-1" />
                                        <p className="text-xs text-muted-foreground">Carbon Sequestration</p>
                                        <p className="text-sm font-bold">{aiAnalysis.carbon_sequestration_potential}</p>
                                    </div>
                                </div>
                                <div className="mt-4 p-3 bg-white rounded-lg">
                                    <p className="text-sm"><strong>Energy Savings:</strong> {aiAnalysis.estimated_energy_savings}</p>
                                    <p className="text-sm mt-1"><strong>Health Benefits:</strong> {aiAnalysis.estimated_health_benefits}</p>
                                </div>
                            </div>

                            {/* Investment */}
                            <div className="bg-amber-50 rounded-lg p-5 text-center">
                                <h4 className="font-bold text-lg mb-2 flex items-center justify-center gap-2">
                                    <DollarSign className="h-5 w-5 text-amber-600" />
                                    Estimated Investment
                                </h4>
                                <p className="text-2xl font-bold text-amber-700">{aiAnalysis.total_investment_estimate}</p>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

export default function AnalysisPage() {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-heatwise-primary mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading...</p>
                </div>
            </div>
        }>
            <AnalysisContent />
        </Suspense>
    );
}
