'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {

  Map,
  MessageSquare,
  Leaf,
} from 'lucide-react';

const sidebarItems = [

  {
    title: 'Heat Map',
    href: '/heatmap',
    icon: Map,
  },
  {
    title: 'AI Assistant',
    href: '/chat',
    icon: MessageSquare,
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div className={cn("flex flex-col h-full bg-gradient-to-b from-heatwise-deep to-heatwise-primary text-white", className)}>
      {/* Logo Section */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-10 h-10 bg-white/20 rounded-xl">
            <Leaf className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold">HeatWise</h1>
            <p className="text-xs text-white/70">Smart City AI</p>
          </div>
        </div>
      </div>

      {/* Navigation Items */}
      <ScrollArea className="flex-1 px-3 py-4">
        <div className="space-y-2">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Button
                key={item.href}
                asChild
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start text-left font-medium transition-all duration-200",
                  isActive
                    ? "bg-white/20 text-white shadow-lg"
                    : "text-white/80 hover:bg-white/10 hover:text-white"
                )}
              >
                <Link href={item.href}>
                  <Icon className="mr-3 h-5 w-5" />
                  {item.title}
                </Link>
              </Button>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}