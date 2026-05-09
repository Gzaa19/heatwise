'use client';

import { useState } from 'react';
import { Marker, Popup, useMapEvents } from 'react-leaflet';
import { Button } from '@/components/ui/button';
import { MapPin, ExternalLink, Loader2, X } from 'lucide-react';
import L from 'leaflet';

interface ClickedLocation {
    lat: number;
    lng: number;
    placeName?: string;
}

interface ClickToAnalyzeProps {
    onAnalyze?: (location: ClickedLocation) => void;
    apiBaseUrl?: string;
}

// Custom marker icon for clicked location
const clickedLocationIcon = L.divIcon({
    html: `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36">
      <path fill="#3B82F6" stroke="#fff" stroke-width="2" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
      <circle fill="#fff" cx="12" cy="9" r="3"/>
    </svg>
  `,
    className: 'clicked-location-icon',
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36]
});

function LocationMarkerContent({
    location,
    onClose,
    onAnalyze,
    isLoading,
    placeName
}: {
    location: ClickedLocation;
    onClose: () => void;
    onAnalyze: () => void;
    isLoading: boolean;
    placeName?: string;
}) {
    return (
        <div className="p-3 min-w-[240px]">
            <div className="flex items-center gap-2 mb-3">
                <MapPin className="h-5 w-5 text-blue-500" />
                <span className="font-semibold">Selected Location</span>
            </div>

            <div className="space-y-2 text-sm mb-4">
                <div className="flex justify-between">
                    <span className="text-gray-500">Place Name:</span>
                    <span className="font-medium">{placeName || 'Loading...'}</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-gray-500">Latitude:</span>
                    <span className="font-mono text-xs">{location.lat.toFixed(8)}</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-gray-500">Longitude:</span>
                    <span className="font-mono text-xs">{location.lng.toFixed(8)}</span>
                </div>
            </div>

            <Button
                className="w-full"
                onClick={onAnalyze}
                disabled={isLoading}
            >
                {isLoading ? (
                    <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Loading...
                    </>
                ) : (
                    <>
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Go to Map Description
                    </>
                )}
            </Button>
        </div>
    );
}

export default function ClickToAnalyze({
    onAnalyze,
    apiBaseUrl = 'http://localhost:8000'
}: ClickToAnalyzeProps) {
    const [clickedLocation, setClickedLocation] = useState<ClickedLocation | null>(null);
    const [placeName, setPlaceName] = useState<string | undefined>();
    const [isLoading, setIsLoading] = useState(false);

    // Handle map click events
    useMapEvents({
        click: async (e) => {
            const { lat, lng } = e.latlng;
            setClickedLocation({ lat, lng });
            setPlaceName(undefined);

            // Fetch place name from geocoding API
            try {
                const response = await fetch(
                    `${apiBaseUrl}/api/geocode/reverse?lat=${lat}&lng=${lng}`
                );
                if (response.ok) {
                    const data = await response.json();
                    if (data.result) {
                        setPlaceName(data.result.city || data.result.formatted || 'Unknown');
                    }
                }
            } catch (error) {
                console.error('Failed to fetch place name:', error);
                setPlaceName('Unknown Location');
            }
        }
    });

    const handleAnalyze = async () => {
        if (!clickedLocation) return;

        setIsLoading(true);

        // Navigate to analysis page with coordinates
        const params = new URLSearchParams({
            lat: clickedLocation.lat.toString(),
            lng: clickedLocation.lng.toString(),
            name: placeName || 'Unknown'
        });

        window.location.href = `/heatmap/analysis?${params.toString()}`;
    };

    const handleClose = () => {
        setClickedLocation(null);
        setPlaceName(undefined);
    };

    if (!clickedLocation) return null;

    return (
        <Marker
            position={[clickedLocation.lat, clickedLocation.lng]}
            icon={clickedLocationIcon}
        >
            <Popup>
                <LocationMarkerContent
                    location={clickedLocation}
                    onClose={handleClose}
                    onAnalyze={handleAnalyze}
                    isLoading={isLoading}
                    placeName={placeName}
                />
            </Popup>
        </Marker>
    );
}

export { clickedLocationIcon };
export type { ClickedLocation };
