'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Thermometer, AlertTriangle, CheckCircle, MapPin, RefreshCw, MousePointer } from 'lucide-react';
import BasicMap from './leaflet/BasicMap';
import ClickToAnalyze from './leaflet/ClickToAnalyze';
import CurrentLocation from './leaflet/CurrentLocation';
import { heatRiskColors, defaultMapSettings } from './leaflet/osm-providers';
import 'leaflet/dist/leaflet.css';

interface HeatMapProps {
  className?: string;
  showControls?: boolean;
  showLegend?: boolean;
  showLocationButton?: boolean;
}

export default function HeatMap({
  className = '',
  showControls = true,
  showLegend = true,
  showLocationButton = true
}: HeatMapProps) {
  const [isClient, setIsClient] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };

  if (!isClient) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="h-[500px] flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading Heat Map...</p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`p-4 ${className}`}>
      {showControls && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-heatwise-primary" />
              <h2 className="text-xl font-bold">Urban Heat Map</h2>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2 p-3 bg-heatwise-primary/10 rounded-lg text-sm text-heatwise-primary">
            <MousePointer className="h-4 w-4" />
            <span>Click anywhere on the map to analyze that location</span>
          </div>
        </div>
      )}

      <div className="relative h-[500px] rounded-lg overflow-hidden border">
        <BasicMap
          center={defaultMapSettings.center}
          zoom={defaultMapSettings.zoom}
          provider="cartoLight"
        >
          <ClickToAnalyze apiBaseUrl="http://localhost:8000" />
          {showLocationButton && <CurrentLocation showButton={true} />}
        </BasicMap>

        {showLegend && (
          <div className="absolute bottom-4 right-4 bg-background/95 backdrop-blur-sm p-3 rounded-lg border shadow-lg z-[1000]">
            <h4 className="font-semibold mb-2 text-sm flex items-center gap-2">
              <MousePointer className="h-4 w-4" />
              How to Use
            </h4>
            <div className="space-y-1.5 text-xs text-muted-foreground">
              <p>1. Click on any location on the map</p>
              <p>2. View the pin popup with coordinates</p>
              <p>3. Click "Go to Map Description"</p>
              <p>4. Get detailed analysis & AI recommendations</p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 text-xs text-muted-foreground">
        <p>• Click anywhere on the map to place a pin and analyze that location</p>
        <p>• Analysis includes weather, air pollution, soil data, and AI recommendations</p>
      </div>
    </Card>
  );
}