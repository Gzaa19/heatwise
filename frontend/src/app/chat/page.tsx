'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    MessageSquare,
    Lightbulb,
    Zap,
    BookOpen,
    HelpCircle
} from 'lucide-react';
import dynamic from 'next/dynamic';

// Dynamically import WISEAIChatbot to avoid SSR issues
const WISEAIChatbot = dynamic(() => import('@/components/WISEAIChatbot'), {
    ssr: false,
    loading: () => (
        <Card className="p-6">
            <div className="h-[600px] flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Loading AI assistant...</p>
                </div>
            </div>
        </Card>
    )
});

export default function ChatPage() {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">WISE-AI Assistant</h1>
                    <p className="text-gray-600 mt-1">
                        Asisten AI cerdas untuk analisis dan rekomendasi mitigasi panas urban
                    </p>
                </div>
                <Badge variant="outline" className="text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                    AI Online
                </Badge>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-50 rounded-lg">
                                <Lightbulb className="h-5 w-5 text-blue-500" />
                            </div>
                            <div>
                                <p className="text-sm font-medium">Get Recommendations</p>
                                <p className="text-xs text-gray-500">AI-powered suggestions</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-purple-50 rounded-lg">
                                <Zap className="h-5 w-5 text-purple-500" />
                            </div>
                            <div>
                                <p className="text-sm font-medium">Quick Analysis</p>
                                <p className="text-xs text-gray-500">Instant heat insights</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-green-50 rounded-lg">
                                <BookOpen className="h-5 w-5 text-green-500" />
                            </div>
                            <div>
                                <p className="text-sm font-medium">Learn More</p>
                                <p className="text-xs text-gray-500">UHI education</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-orange-50 rounded-lg">
                                <HelpCircle className="h-5 w-5 text-orange-500" />
                            </div>
                            <div>
                                <p className="text-sm font-medium">Get Help</p>
                                <p className="text-xs text-gray-500">Support & FAQ</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Main Chatbot */}
            <WISEAIChatbot />

            {/* Suggested Topics */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                        <MessageSquare className="h-5 w-5" />
                        Suggested Topics
                    </CardTitle>
                    <CardDescription>
                        Klik topik di bawah untuk memulai percakapan dengan AI
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-wrap gap-2">
                        {[
                            'Apa itu Urban Heat Island?',
                            'Bagaimana cara mengurangi suhu panas di kota?',
                            'Area mana yang paling panas di Jakarta?',
                            'Rekomendasi penghijauan untuk Jakarta Pusat',
                            'Dampak perubahan iklim terhadap suhu kota',
                            'Teknologi cooling untuk gedung',
                            'Prediksi suhu minggu depan',
                            'Strategi mitigasi panas jangka panjang',
                        ].map((topic, idx) => (
                            <Button key={idx} variant="outline" size="sm" className="text-xs">
                                {topic}
                            </Button>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
