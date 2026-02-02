// Leaflet Components Index
// Export all leaflet components for easy imports

export { default as BasicMap } from './BasicMap';
export { default as CurrentLocation, LocationMarker } from './CurrentLocation';
export { default as ClickToAnalyze, clickedLocationIcon } from './ClickToAnalyze';
export { osmProviders, defaultMapSettings, getTileProvider, heatRiskColors } from './osm-providers';

// Types
export type { TileProvider } from './osm-providers';
export type { ClickedLocation } from './ClickToAnalyze';
