'use client';

import { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import { osmProviders, defaultMapSettings, getTileProvider, type TileProvider } from './osm-providers';
import 'leaflet/dist/leaflet.css';

interface BasicMapProps {
    center?: [number, number];
    zoom?: number;
    provider?: string;
    className?: string;
    children?: React.ReactNode;
    scrollWheelZoom?: boolean;
    zoomControl?: boolean;
}

// Component to control map view - with safety check
function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
    const map = useMap();

    useEffect(() => {
        if (map && map.getContainer() && map.getContainer()._leaflet_pos !== undefined) {
            map.setView(center, zoom);
        }
    }, [center, zoom, map]);

    return null;
}

export default function BasicMap({
    center = defaultMapSettings.center,
    zoom = defaultMapSettings.zoom,
    provider = 'default',
    className = '',
    children,
    scrollWheelZoom = true,
    zoomControl = true
}: BasicMapProps) {
    const [isClient, setIsClient] = useState(false);
    const [currentProvider, setCurrentProvider] = useState<TileProvider>(getTileProvider(provider));
    const [mapKey, setMapKey] = useState(0);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        setIsClient(true);
        
        // Cleanup on unmount to prevent "container reused" error
        return () => {
            if (containerRef.current) {
                const container = containerRef.current.querySelector('.leaflet-container');
                if (container && (container as any)._leaflet_id) {
                    delete (container as any)._leaflet_id;
                }
            }
        };
    }, []);

    useEffect(() => {
        setCurrentProvider(getTileProvider(provider));
    }, [provider]);

    if (!isClient) {
        return (
            <div className={`h-full w-full flex items-center justify-center bg-gray-100 ${className}`}>
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Loading map...</p>
                </div>
            </div>
        );
    }

    return (
        <div ref={containerRef} className="h-full w-full">
            <MapContainer
                key={mapKey}
                center={center}
                zoom={zoom}
                scrollWheelZoom={scrollWheelZoom}
                zoomControl={zoomControl}
                className={`h-full w-full z-0 ${className}`}
                minZoom={defaultMapSettings.minZoom}
                maxZoom={defaultMapSettings.maxZoom}
            >
                <MapController center={center} zoom={zoom} />

                <TileLayer
                    url={currentProvider.url}
                    attribution={currentProvider.attribution}
                    maxZoom={currentProvider.maxZoom}
                    minZoom={currentProvider.minZoom}
                />

                {children}
            </MapContainer>
        </div>
    );
}

// Export map utilities
export { osmProviders, defaultMapSettings, getTileProvider };
