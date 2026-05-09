'use client';

import dynamic from 'next/dynamic';

const WISEAIChatbot = dynamic(() => import('@/components/WISEAIChatbot'), {
    ssr: false,
    loading: () => (
        <div className="flex-1 flex items-center justify-center bg-background">
            <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-heatwise-primary mx-auto mb-4"></div>
                <p className="text-muted-foreground text-sm">Initializing WISE-AI...</p>
            </div>
        </div>
    )
});

export default function ChatPage() {
    return (
        <div className="fixed inset-0 lg:left-64 flex flex-col overflow-hidden">
            <WISEAIChatbot className="flex-1 min-h-0" />
        </div>
    );
}
