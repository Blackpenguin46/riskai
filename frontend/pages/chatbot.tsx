import React, { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { FiSend, FiMessageCircle, FiUser, FiRefreshCw, FiArrowLeft, FiCpu } from 'react-icons/fi';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatSuggestion {
  text: string;
  category: string;
}

const ChatbotPage: React.FC = () => {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load chat suggestions on component mount
    fetchSuggestions();
    
    // Add welcome message
    const welcomeMessage: ChatMessage = {
      role: 'assistant',
      content: `Hi! I'm your cybersecurity AI consultant. I can help you with:

• **Security Planning** - Creating comprehensive cybersecurity strategies
• **Risk Assessment Guidance** - Understanding and prioritizing security risks  
• **Compliance Questions** - GDPR, HIPAA, SOC 2, and other regulatory requirements
• **Incident Response** - Planning and responding to security incidents
• **Implementation Advice** - Best practices for security controls and tools
• **Employee Training** - Building security awareness programs

What would you like to discuss today?`,
      timestamp: new Date().toISOString()
    };
    setMessages([welcomeMessage]);
  }, []);

  const fetchSuggestions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/chatbot/suggestions');
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const sendMessage = async (messageText?: string) => {
    const messageToSend = messageText || inputMessage.trim();
    if (!messageToSend) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: messageToSend,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chatbot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageToSend,
          conversation_history: messages.slice(-10) // Send last 10 messages for context
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again. If the problem persists, the AI service may need to be configured.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearConversation = () => {
    const welcomeMessage: ChatMessage = {
      role: 'assistant',
      content: `Hi! I'm your cybersecurity AI consultant. I can help you with security planning, risk assessment guidance, compliance questions, incident response, implementation advice, and employee training.

What would you like to discuss today?`,
      timestamp: new Date().toISOString()
    };
    setMessages([welcomeMessage]);
  };

  return (
    <>
      <Head>
        <title>AI Cybersecurity Consultant - RiskAI</title>
        <meta name="description" content="Get expert cybersecurity advice and planning assistance from our AI consultant" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => router.push('/')}
                  className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <FiArrowLeft size={20} />
                </button>
                <FiMessageCircle className="text-blue-600 text-2xl" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">AI Cybersecurity Consultant</h1>
                  <p className="text-sm text-gray-600">Get expert advice on security planning and risk management</p>
                </div>
              </div>
              <button
                onClick={clearConversation}
                className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <FiRefreshCw size={16} />
                <span>New Chat</span>
              </button>
            </div>
          </div>
        </div>

        <div className="max-w-4xl mx-auto p-4">
          <div className="bg-white rounded-xl shadow-lg h-[calc(100vh-200px)] flex flex-col">
            
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex space-x-3 max-w-3xl ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      message.role === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {message.role === 'user' ? <FiUser size={16} /> : <FiCpu size={16} />}
                    </div>
                    <div className={`rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      <div className="whitespace-pre-wrap text-sm leading-relaxed">
                        {message.content}
                      </div>
                      <div className={`text-xs mt-2 ${
                        message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex space-x-3 max-w-3xl">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                      <FiCpu size={16} />
                    </div>
                    <div className="bg-gray-100 rounded-2xl px-4 py-3">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Suggestions (show only when conversation is empty) */}
            {messages.length <= 1 && suggestions.length > 0 && (
              <div className="px-6 py-4 border-t bg-gray-50">
                <p className="text-sm font-medium text-gray-700 mb-3">Try asking about:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {suggestions.slice(0, 6).map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => sendMessage(suggestion)}
                      className="text-left p-3 text-sm bg-white hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input Area */}
            <div className="p-6 border-t">
              <div className="flex space-x-3">
                <div className="flex-1 relative">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything about cybersecurity planning, risk assessment, compliance, or security best practices..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows={3}
                    disabled={isLoading}
                  />
                </div>
                <button
                  onClick={() => sendMessage()}
                  disabled={!inputMessage.trim() || isLoading}
                  className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <FiSend size={20} />
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Press Enter to send, Shift+Enter for new line
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ChatbotPage;