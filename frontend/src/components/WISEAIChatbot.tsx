'use client';

import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { 
  Send, 
  Bot, 
  User, 
  Brain, 
  Sparkles,
  Thermometer,
  Leaf,
  Shield,
  Zap
} from 'lucide-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isTyping?: boolean;
  recommendations?: string[];
  confidence?: number;
  sources?: string[];
}

interface WISEAIChatbotProps {
  className?: string;
}

const mockAIResponses = [
  "Based on current temperature data, I recommend increasing green coverage in Central Jakarta by 15% to reduce urban heat island effect.",
  "The heat risk level in your area is currently HIGH. Consider implementing cool roof technologies and increasing tree planting in residential areas.",
  "I suggest installing 50 smart irrigation systems in high-risk districts. This could reduce local temperatures by 2-3°C during peak hours.",
  "Analysis shows that areas with >30% green coverage have 4°C lower temperatures. Focus on vertical gardens and rooftop planting.",
  "Consider implementing heat-reflective pavement materials in high-traffic areas. This could reduce surface temperatures by 5-8°C.",
  "Based on population density and heat exposure, prioritize cooling centers in South Jakarta and East Jakarta districts.",
  "I recommend establishing 25 new community gardens in high-risk areas. This will provide both cooling and social benefits.",
  "Smart building design with proper insulation and ventilation could reduce indoor temperatures by 3-5°C without additional energy consumption."
];

const typingResponses = [
  "Analyzing temperature data...",
  "Processing heat patterns...",
  "Calculating optimal solutions...",
  "Evaluating mitigation strategies...",
  "Generating AI insights...",
  "Assessing environmental impact..."
];

function TypingIndicator() {
  return (
    <div className="flex items-center space-x-1 text-sm text-muted-foreground">
      <div className="w-2 h-2 bg-heatwise-primary rounded-full animate-bounce"></div>
      <div className="w-2 h-2 bg-heatwise-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
      <div className="w-2 h-2 bg-heatwise-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isAI = message.sender === 'ai';
  
  return (
    <div className={`flex gap-3 ${isAI ? 'justify-start' : 'justify-end'}`}>
      {isAI && (
        <div className="w-8 h-8 rounded-full bg-heatwise-primary/10 flex items-center justify-center flex-shrink-0">
          <Brain className="w-4 h-4 text-heatwise-primary" />
        </div>
      )}
      
      <div className={`max-w-[80%] ${isAI ? 'order-1' : 'order-2'}`}>
        <div className={`rounded-lg p-3 ${
          isAI 
            ? 'bg-heatwise-primary/5 border border-heatwise-primary/20' 
            : 'bg-heatwise-primary text-white'
        }`}>
          {message.isTyping ? (
            <TypingIndicator />
          ) : (
            <p className={`text-sm ${isAI ? 'text-foreground' : 'text-white'}`}>
              {message.content}
            </p>
          )}
        </div>
        <p className="text-xs text-muted-foreground mt-1 px-1">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
      
      {!isAI && (
        <div className="w-8 h-8 rounded-full bg-heatwise-primary flex items-center justify-center flex-shrink-0 order-3">
          <User className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
}

export default function WISEAIChatbot({ className = '' }: WISEAIChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hello! I'm WISE-AI, your intelligent assistant for urban heat mitigation. I can help you analyze temperature patterns, suggest cooling strategies, and provide data-driven recommendations. How can I help you today?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollAreaRef.current?.scrollTo({ top: scrollAreaRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const simulateTyping = (finalMessage: string) => {
    const typingMessage = typingResponses[Math.floor(Math.random() * typingResponses.length)];
    const typingMsg: Message = {
      id: Date.now().toString() + '-typing',
      content: typingMessage,
      sender: 'ai',
      timestamp: new Date(),
      isTyping: true
    };

    setMessages(prev => [...prev, typingMsg]);

    // Simulate typing delay
    setTimeout(() => {
      setMessages(prev => prev.filter(msg => msg.id !== typingMsg.id));
      
      const finalMsg: Message = {
        id: Date.now().toString(),
        content: finalMessage,
        sender: 'ai',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, finalMsg]);
      setIsTyping(false);
    }, 2000 + Math.random() * 1000);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString() + '-user',
      content: inputValue.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Call the FastAPI chat endpoint
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue.trim(),
          context: {
            timestamp: new Date().toISOString(),
            userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'unknown'
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get AI response');
      }

      const data = await response.json();
      
      // Simulate typing delay for better UX
      setTimeout(() => {
        simulateTyping(data.response);
      }, 1000);
      
    } catch (error) {
      console.error('Chat API error:', error);
      // Fallback to mock responses if API fails
      setTimeout(() => {
        const response = mockAIResponses[Math.floor(Math.random() * mockAIResponses.length)];
        simulateTyping(response);
      }, 1000);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickActions = [
    { text: "Show heat map", icon: Thermometer },
    { text: "Suggest cooling strategies", icon: Leaf },
    { text: "Analyze risk areas", icon: Shield },
    { text: "Recommend green solutions", icon: Zap }
  ];

  const handleQuickAction = async (action: string) => {
    if (isTyping) return;
    
    const userMessage: Message = {
      id: Date.now().toString() + '-user',
      content: action,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Call the FastAPI chat endpoint
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: action,
          context: {
            action: action,
            timestamp: new Date().toISOString(),
            userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'unknown'
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get AI response');
      }

      const data = await response.json();
      
      // Simulate typing delay for better UX
      setTimeout(() => {
        simulateTyping(data.response);
      }, 1000);
      
    } catch (error) {
      console.error('Chat API error:', error);
      // Fallback to mock responses if API fails
      setTimeout(() => {
        const response = mockAIResponses[Math.floor(Math.random() * mockAIResponses.length)];
        simulateTyping(response);
      }, 1000);
    }
  };

  return (
    <Card className={`flex flex-col h-[600px] ${className}`}>
      {/* Header */}
      <div className="p-4 border-b bg-gradient-to-r from-heatwise-primary/10 to-heatwise-secondary/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-heatwise-primary flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">WISE-AI Assistant</h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-muted-foreground">Online</span>
              </div>
            </div>
          </div>
          <Sparkles className="w-5 h-5 text-heatwise-primary" />
        </div>
      </div>

      {/* Chat Area */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </div>
      </ScrollArea>

      {/* Quick Actions */}
      <div className="p-4 border-t bg-muted/50">
        <p className="text-sm text-muted-foreground mb-2">Quick Actions:</p>
        <div className="grid grid-cols-2 gap-2">
          {quickActions.map((action, index) => {
            const IconComponent = action.icon;
            return (
              <Button
                key={index}
                variant="outline"
                size="sm"
                className="justify-start"
                onClick={() => handleQuickAction(action.text)}
                disabled={isTyping}
              >
                <IconComponent className="w-3 h-3 mr-2" />
                <span className="text-xs">{action.text}</span>
              </Button>
            );
          })}
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 border-t">
        <div className="flex space-x-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about heat mitigation, cooling strategies, or environmental data..."
            className="flex-1"
            disabled={isTyping}
          />
          <Button 
            onClick={handleSendMessage} 
            disabled={!inputValue.trim() || isTyping}
            className="px-3"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
}