'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    Map,
    MapPin,
    Layers,
    Filter,
    Download,
    RefreshCw
} from 'lucide-react';
import dynamic from 'next/dynamic';

// Dynamically import HeatMap to avoid SSR issues with react-leaflet
const HeatMap = dynamic(() => import('@/components/HeatMap'), {
    ssr: false,
    loading: () => (
        <Card className="p-6">
            <div className="h-[600px] flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Loading heat map...</p>
                </div>
            </div>
        </Card>
    )
});

export default function HeatMapPage() {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Heat Map</h1>
                    <p className="text-gray-600 mt-1">
                        Visualisasi sebaran suhu dan urban heat island di Jakarta
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                        <Filter className="h-4 w-4 mr-2" />
                        Filter
                    </Button>
                    <Button variant="outline" size="sm">
                        <Layers className="h-4 w-4 mr-2" />
                        Layers
                    </Button>
                    <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Export
                    </Button>
                    <Button variant="default" size="sm">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                    </Button>
                </div>
            </div>



            {/* Main Heat Map */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle>Jakarta Urban Heat Island Map</CardTitle>
                            <CardDescription>
                                Real-time temperature distribution across Jakarta metropolitan area
                            </CardDescription>
                        </div>
                        <Badge variant="outline" className="text-sm">
                            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                            Live Data
                        </Badge>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="h-[600px]">
                        <HeatMap />
                    </div>
                </CardContent>
            </Card>


        </div>
    );
}
