'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import ReactMarkdown from 'react-markdown';
import { 
  Send, 
  User, 
  Brain, 
  Sparkles,
  Thermometer,
  Leaf,
  Shield,
  Zap,
  ChevronRight
} from 'lucide-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isTyping?: boolean;
}

interface WISEAIChatbotProps {
  className?: string;
}

const mockAIResponses = [
  "Based on current temperature data, I recommend increasing green coverage in Central Jakarta by 15% to reduce urban heat island effect.",
  "The heat risk level in your area is currently HIGH. Consider implementing cool roof technologies and increasing tree planting in residential areas.",
  "I suggest installing 50 smart irrigation systems in high-risk districts. This could reduce local temperatures by 2-3°C during peak hours.",
  "Analysis shows that areas with >30% green coverage have 4°C lower temperatures. Focus on vertical gardens and rooftop planting.",
];

function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 py-2">
      <div className="flex items-center gap-1">
        <div className="w-1.5 h-1.5 bg-heatwise-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-1.5 h-1.5 bg-heatwise-primary/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-1.5 h-1.5 bg-heatwise-primary/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
      <span className="text-xs text-muted-foreground italic">Analyzing your query...</span>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isAI = message.sender === 'ai';
  
  return (
    <div className={`flex gap-3 ${isAI ? 'justify-start' : 'justify-end'}`}>
      {isAI && (
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-heatwise-deep to-heatwise-primary flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
          <Brain className="w-4 h-4 text-white" />
        </div>
      )}
      
      <div className={`${isAI ? 'max-w-[85%]' : 'max-w-[70%]'}`}>
        <div className={`rounded-2xl px-4 py-3 ${
          isAI 
            ? 'bg-white border border-border shadow-sm rounded-tl-sm' 
            : 'bg-gradient-to-br from-heatwise-deep to-heatwise-primary text-white shadow-md rounded-tr-sm'
        }`}>
          {message.isTyping ? (
            <TypingIndicator />
          ) : isAI ? (
            <div className="prose prose-sm max-w-none text-foreground leading-relaxed
              prose-headings:text-foreground prose-headings:font-semibold prose-headings:tracking-tight
              prose-h3:text-sm prose-h3:mt-3 prose-h3:mb-1.5
              prose-h4:text-sm prose-h4:mt-2.5 prose-h4:mb-1
              prose-p:my-1.5 prose-p:text-[13px] prose-p:leading-[1.7]
              prose-ul:my-1.5 prose-ul:pl-4 prose-ol:my-1.5 prose-ol:pl-4
              prose-li:my-0.5 prose-li:text-[13px] prose-li:leading-[1.6]
              prose-strong:text-foreground prose-strong:font-semibold
              prose-code:text-xs prose-code:bg-muted prose-code:text-foreground prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:font-mono
            ">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-sm text-white leading-relaxed">
              {message.content}
            </p>
          )}
        </div>
        <p className={`text-[10px] text-muted-foreground mt-1 ${isAI ? 'pl-1' : 'pr-1 text-right'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
      
      {!isAI && (
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-heatwise-primary to-heatwise-secondary flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
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
      content: "Welcome to **WISE-AI**. I am your urban heat analysis assistant.\n\nI can help you with:\n- **Temperature pattern analysis** across Jakarta metropolitan area\n- **Cooling strategy recommendations** based on real-time environmental data\n- **Risk area identification** and mitigation planning\n- **Green infrastructure** planning and species selection\n\nWhat would you like to analyze?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addAIMessage = (content: string) => {
    const typingMsg: Message = {
      id: Date.now().toString() + '-typing',
      content: '',
      sender: 'ai',
      timestamp: new Date(),
      isTyping: true
    };

    setMessages(prev => [...prev, typingMsg]);

    setTimeout(() => {
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== typingMsg.id);
        return [...filtered, {
          id: Date.now().toString(),
          content: content,
          sender: 'ai',
          timestamp: new Date()
        }];
      });
      setIsTyping(false);
    }, 1200);
  };

  const callChatAPI = async (userMessage: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          context: { timestamp: new Date().toISOString() }
        })
      });

      if (!response.ok) throw new Error('API error');
      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Chat API error:', error);
      return null;
    }
  };

  const sendMessage = async (text: string) => {
    if (!text.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString() + '-user',
      content: text.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    const aiResponse = await callChatAPI(text.trim());
    addAIMessage(aiResponse || mockAIResponses[Math.floor(Math.random() * mockAIResponses.length)]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  const quickActions = [
    { text: "Analyze Jakarta heat distribution", icon: Thermometer },
    { text: "Suggest cooling strategies", icon: Leaf },
    { text: "Identify high-risk UHI zones", icon: Shield },
    { text: "Green infrastructure plan", icon: Zap }
  ];

  return (
    <div className={`flex flex-col ${className}`}>
      {/* Header — uses same gradient as sidebar */}
      <div className="flex items-center gap-3 px-5 py-3.5 bg-gradient-to-r from-heatwise-deep to-heatwise-primary flex-shrink-0">
        <div className="w-10 h-10 rounded-xl bg-white/15 backdrop-blur flex items-center justify-center border border-white/10">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-sm text-white">WISE-AI Assistant</h3>
          <div className="flex items-center gap-1.5 mt-0.5">
            <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></div>
            <span className="text-[11px] text-white/60 font-medium">Online — Powered by Gemini AI</span>
          </div>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/10 border border-white/10">
          <Sparkles className="w-3.5 h-3.5 text-white/80" />
          <span className="text-[11px] text-white/70 font-medium">v2.0</span>
        </div>
      </div>

      {/* Scrollable Chat Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-5 space-y-5 min-h-0 bg-background">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-5 py-2.5 bg-background border-t border-border flex-shrink-0">
        <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold mb-2">Suggested Queries</p>
        <div className="flex gap-2 overflow-x-auto pb-1">
          {quickActions.map((action, index) => {
            const IconComponent = action.icon;
            return (
              <button
                key={index}
                className="flex items-center gap-1.5 flex-shrink-0 text-xs px-3 py-2 rounded-lg border border-border bg-background text-foreground/70 
                  hover:bg-heatwise-primary hover:text-white hover:border-heatwise-primary 
                  transition-all duration-200 disabled:opacity-40 group"
                onClick={() => sendMessage(action.text)}
                disabled={isTyping}
              >
                <IconComponent className="w-3.5 h-3.5 group-hover:text-white transition-colors" />
                <span className="whitespace-nowrap">{action.text}</span>
                <ChevronRight className="w-3 h-3 opacity-40 group-hover:opacity-100 transition-opacity" />
              </button>
            );
          })}
        </div>
      </div>

      {/* Input Area — pinned at absolute bottom */}
      <div className="px-5 py-3 bg-background border-t border-border flex-shrink-0">
        <div className="flex gap-2.5 items-center">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about urban heat, air quality, or mitigation strategies..."
            className="flex-1 rounded-xl bg-muted border-border focus-visible:ring-1 focus-visible:ring-heatwise-primary focus-visible:border-heatwise-primary px-4 h-11 text-sm"
            disabled={isTyping}
          />
          <Button 
            onClick={() => sendMessage(inputValue)} 
            disabled={!inputValue.trim() || isTyping}
            className="rounded-xl w-11 h-11 p-0 bg-heatwise-primary hover:bg-heatwise-primary/90 disabled:bg-muted transition-all shadow-sm"
          >
            <Send className="w-4 h-4 text-white" />
          </Button>
        </div>
      </div>
    </div>
  );
}