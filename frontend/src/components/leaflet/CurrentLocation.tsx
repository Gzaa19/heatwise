'use client';

import { useEffect, useState } from 'react';
import { useMap, CircleMarker, Popup } from 'react-leaflet';
import { Button } from '@/components/ui/button';
import { Navigation, Loader2 } from 'lucide-react';

interface CurrentLocationProps {
    onLocationFound?: (lat: number, lng: number) => void;
    showButton?: boolean;
    autoLocate?: boolean;
    flyToLocation?: boolean;
}

interface LocationState {
    lat: number;
    lng: number;
    accuracy: number;
}

function LocationMarker({ location }: { location: LocationState }) {
    return (
        <CircleMarker
            center={[location.lat, location.lng]}
            radius={10}
            pathOptions={{
                color: '#3B82F6',
                fillColor: '#3B82F6',
                fillOpacity: 0.8,
                weight: 3
            }}
        >
            <Popup>
                <div className="text-center p-2">
                    <p className="font-semibold">Your Location</p>
                    <p className="text-xs text-gray-500">
                        {location.lat.toFixed(6)}, {location.lng.toFixed(6)}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                        Accuracy: ±{Math.round(location.accuracy)}m
                    </p>
                </div>
            </Popup>
        </CircleMarker>
    );
}

function LocateButton({
    onLocate,
    loading
}: {
    onLocate: () => void;
    loading: boolean;
}) {
    return (
        <Button
            size="sm"
            variant="secondary"
            className="absolute bottom-4 left-4 z-[1000] shadow-lg"
            onClick={onLocate}
            disabled={loading}
        >
            {loading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
                <Navigation className="h-4 w-4 mr-2" />
            )}
            {loading ? 'Locating...' : 'My Location'}
        </Button>
    );
}

export default function CurrentLocation({
    onLocationFound,
    showButton = true,
    autoLocate = false,
    flyToLocation = true
}: CurrentLocationProps) {
    const map = useMap();
    const [location, setLocation] = useState<LocationState | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const locateUser = () => {
        if (!navigator.geolocation) {
            setError('Geolocation is not supported by your browser');
            return;
        }

        setLoading(true);
        setError(null);

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude, accuracy } = position.coords;

                setLocation({
                    lat: latitude,
                    lng: longitude,
                    accuracy: accuracy
                });

                if (flyToLocation) {
                    map.flyTo([latitude, longitude], 15, {
                        duration: 1.5
                    });
                }

                if (onLocationFound) {
                    onLocationFound(latitude, longitude);
                }

                setLoading(false);
            },
            (err) => {
                setError(err.message);
                setLoading(false);
                console.error('Geolocation error:', err);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    };

    useEffect(() => {
        if (autoLocate) {
            locateUser();
        }
    }, [autoLocate]);

    return (
        <>
            {location && <LocationMarker location={location} />}
            {showButton && <LocateButton onLocate={locateUser} loading={loading} />}
        </>
    );
}

export { LocationMarker };
