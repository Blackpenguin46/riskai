import React, { useState, useEffect, useRef } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  suggestions?: string[];
}

const ChatPage: NextPage = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const router = useRouter();
  const chatEndRef = useRef<HTMLDivElement>(null);

  const goBackToDashboard = () => {
    router.push('/');
  };

  const startChatSession = async () => {
    try {
      setIsLoading(true);
      // For now, we'll use a mock assessment result
      const mockAssessmentResult = {
        overall_weighted_score: 75.5,
        risk_table: [
          { category: 'Access Management', score: 6 },
          { category: 'Data Protection', score: 8 },
          { category: 'Governance', score: 7 }
        ]
      };

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/chat/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assessment_id: 'demo_assessment',
          assessment_results: mockAssessmentResult
        })
      });

      if (!response.ok) {
        throw new Error('Failed to start chat session');
      }

      const data = await response.json();
      setSessionId(data.session_id);
      
      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.message || 'Hello! I\'m here to help you with risk mitigation strategies. How can I assist you today?',
        timestamp: new Date().toISOString(),
        suggestions: data.suggestions || []
      };
      
      setMessages([welcomeMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start chat session');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (message: string) => {
    if (!sessionId) {
      setError('No active chat session');
      return;
    }

    try {
      setIsLoading(true);
      
      // Add user message
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/chat/${sessionId}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      // Add AI response
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        timestamp: new Date().toISOString(),
        suggestions: data.suggestions || []
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || isLoading) return;

    const message = userInput;
    setUserInput('');
    await sendMessage(message);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setUserInput(suggestion);
  };

  useEffect(() => {
    startChatSession();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      <header className="p-4 bg-gray-900/80 backdrop-blur-md shadow-lg sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <button
            onClick={goBackToDashboard}
            className="text-indigo-400 hover:text-indigo-300 transition flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold text-center bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent">
            Risk Mitigation Chat
          </h1>
          <div className="w-32"></div>
        </div>
      </header>

      <main className="flex-grow p-4 space-y-4 overflow-y-auto" style={{maxHeight: 'calc(100vh - 160px)'}}>
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xl lg:max-w-2xl px-4 py-3 rounded-2xl shadow-md ${
              msg.role === 'user' ? 'bg-indigo-600' : 'bg-gray-700'
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.suggestions && msg.suggestions.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {msg.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="px-3 py-1 bg-indigo-800 hover:bg-indigo-700 rounded-lg text-sm transition"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </main>

      <footer className="p-4 bg-gray-900/80 backdrop-blur-md sticky bottom-0 z-10">
        {error && (
          <div className="text-red-400 text-center mb-2 p-2 bg-red-900/50 rounded">
            Error: {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder={isLoading ? "AI is thinking..." : "Type your message..."}
            className="flex-grow p-3 rounded-xl bg-gray-800 border border-gray-700 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition disabled:opacity-50"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold shadow-lg hover:from-indigo-600 hover:to-purple-700 transition disabled:opacity-50"
            disabled={isLoading || !userInput.trim()}
          >
            Send
          </button>
        </form>
      </footer>
    </div>
  );
};

export default ChatPage;