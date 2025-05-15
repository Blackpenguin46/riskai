import React, { useState, useEffect, useRef, useCallback } from 'react';
import type { NextPage } from 'next';

// --- Type Definitions (align with backend api.py) ---
interface CompanyProfile {
  name?: string;
  industry: string;
  size: string;
  tech_adoption: string;
  security_controls: string;
  risk_posture: string;
  emerging_technologies: string[];
}

interface RiskQuestion {
  id: string;
  question_text: string;
  category_name: string;
  helper_text?: string;
  scoring_focus: string;
}

interface RiskAnswer {
  question_id: string;
  answer: string;
}

interface RiskTableRow {
  id: string;
  category: string;
  definition: string;
  scoring_focus: string;
  score: number;
  max_score: number;
  weight: number;
  explanation: string;
}

interface RiskAssessmentResult {
  overall_weighted_score: number;
  risk_table: RiskTableRow[];
  recommendations: string[];
  resources: { title: string; url: string }[];
  data_insights: string[];
  raw_llm_output?: string;
}

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text?: string;
  data?: RiskAssessmentResult; // Changed from any to RiskAssessmentResult | undefined (implicitly)
  type: 'text' | 'question' | 'assessment_result' | 'error';
  question_id?: string; // For AI questions
}

const initialCompanyProfileQuestions = [
  { id: 'industry', label: 'What is your company\'s industry?' },
  { id: 'size', label: 'What is the size of your company (e.g., Startup, SME, Large Enterprise)?' },
  { id: 'tech_adoption', label: 'How would you describe your company\'s typical level of technology adoption (e.g., Early Adopter, Mainstream, Laggard)?' },
  { id: 'security_controls', label: 'Briefly describe your company\'s current security controls.' },
  { id: 'risk_posture', label: 'Briefly describe your company\'s general risk posture.' },
  { id: 'emerging_technologies', label: 'Which emerging technologies are you most interested in assessing (comma-separated, e.g., AI, Blockchain, Quantum Computing)?' },
];

const ConversationalAssessmentPage: NextPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [conversationState, setConversationState] = useState<'initial_greeting' | 'collecting_profile' | 'asking_risk_questions' | 'submitting_answers' | 'showing_results' | 'error_state'>('initial_greeting');
  const [currentProfileQuestionIndex, setCurrentProfileQuestionIndex] = useState(0);
  const [companyProfileData, setCompanyProfileData] = useState<Partial<CompanyProfile>>({});
  const [riskQuestions, setRiskQuestions] = useState<RiskQuestion[]>([]);
  const [currentRiskQuestionIndex, setCurrentRiskQuestionIndex] = useState(0);
  const [riskAnswers, setRiskAnswers] = useState<RiskAnswer[]>([]);
  
  const chatEndRef = useRef<null | HTMLDivElement>(null);

  const addMessage = useCallback((sender: 'user' | 'ai', text: string, type: Message['type'] = 'text', question_id?: string, data?: RiskAssessmentResult) => {
    setMessages((prev: Message[]) => [...prev, { id: Date.now().toString() + Math.random().toString(), sender, text, type, question_id, data }]);
  }, []);

  const addAiMessage = useCallback((text: string, type: Message['type'] = 'text', question_id?: string, helper_text?: string, data?: RiskAssessmentResult) => {
    const fullText = helper_text ? `${text}\n\n*Helper: ${helper_text}*` : text;
    addMessage('ai', fullText, type, question_id, data);
  }, [addMessage]);

  const submitCompanyProfile = useCallback(async () => {
    setIsLoading(true);
    addAiMessage("Thank you for the company details. Fetching relevant risk questions for you...");
    try {
      const profileToSend: CompanyProfile = {
        industry: companyProfileData.industry || '',
        size: companyProfileData.size || '',
        tech_adoption: companyProfileData.tech_adoption || '',
        security_controls: companyProfileData.security_controls || '',
        risk_posture: companyProfileData.risk_posture || '',
        emerging_technologies: (companyProfileData.emerging_technologies as string[] || []),
        name: companyProfileData.name || 'Unnamed Company'
      };
      console.log("Submitting company profile:", profileToSend);

      const res = await fetch('http://localhost:8000/initialize-assessment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileToSend),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: `Server error: ${res.status}` }));
        if (res.status === 503) {
          addAiMessage("The AI service is still initializing. Please wait a moment and try again.", 'error');
          setError("Service not ready. Please try again in a few moments.");
        } else {
          throw new Error(errorData.detail || `Server error: ${res.status}`);
        }
        setConversationState('error_state');
        return;
      }

      const fetchedQuestions: RiskQuestion[] = await res.json();
      console.log("Fetched risk questions:", fetchedQuestions);
      if (fetchedQuestions && fetchedQuestions.length > 0) {
        setRiskQuestions(fetchedQuestions);
        addAiMessage("Great! Now I have some specific questions to understand your risk posture better.");
        setConversationState('asking_risk_questions');
        setCurrentRiskQuestionIndex(0);
      } else {
        addAiMessage("No specific risk questions were generated. This might be due to a service issue.", 'error');
        setError("Failed to generate assessment questions. Please try again.");
        setConversationState('error_state');
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      addAiMessage(`Error fetching risk questions: ${errorMessage}. Please try again in a few moments.`, 'error');
      setError(`Failed to initialize assessment: ${errorMessage}`);
      setConversationState('error_state');
    }
    setIsLoading(false);
  }, [addAiMessage, companyProfileData]);

  const submitRiskAnswers = useCallback(async () => {
    setIsLoading(true);
    console.log("Submitting riskAnswers:", riskAnswers);
    console.log("Current riskQuestions:", riskQuestions);
    try {
      const res = await fetch('http://localhost:8000/submit-answers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: riskAnswers }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: `Server error: ${res.status}` }));
        if (res.status === 503) {
          addAiMessage("The AI service is still initializing. Please wait a moment and try again.", 'error');
          setError("Service not ready. Please try again in a few moments.");
        } else {
          throw new Error(errorData.detail || `Server error: ${res.status}`);
        }
        setConversationState('error_state');
        return;
      }

      const resultData: RiskAssessmentResult = await res.json();
      if (!resultData.recommendations || !resultData.risk_table) {
        throw new Error("Received incomplete assessment result");
      }
      addAiMessage("Here is your risk assessment result:", 'assessment_result', undefined, undefined, resultData);
      setConversationState('showing_results');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      addAiMessage(`Error submitting answers: ${errorMessage}. Please try again in a few moments.`, 'error');
      setError(`Failed to get assessment: ${errorMessage}`);
      setConversationState('error_state');
    }
    setIsLoading(false);
  }, [addAiMessage, riskAnswers, riskQuestions]);

  // Add a retry mechanism for error states
  const handleRetry = useCallback(() => {
    setError(null);
    if (conversationState === 'error_state') {
      if (currentProfileQuestionIndex >= initialCompanyProfileQuestions.length) {
        submitCompanyProfile();
      } else if (currentRiskQuestionIndex >= riskQuestions.length && riskQuestions.length > 0) {
        submitRiskAnswers();
      } else {
        setConversationState('initial_greeting');
      }
    }
  }, [conversationState, currentProfileQuestionIndex, currentRiskQuestionIndex, riskQuestions.length, submitCompanyProfile, submitRiskAnswers]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (conversationState === 'initial_greeting') {
      addAiMessage("Hello! I'm RiskIQ-AI, here to help you assess your company's risk profile for emerging technologies. Let's start by gathering some basic information about your company.");
      setConversationState('collecting_profile');
    }
  }, [conversationState, addAiMessage]);

  useEffect(() => {
    if (conversationState === 'collecting_profile' && currentProfileQuestionIndex < initialCompanyProfileQuestions.length) {
      const question = initialCompanyProfileQuestions[currentProfileQuestionIndex];
      addAiMessage(question.label, 'question', question.id);
    } else if (conversationState === 'collecting_profile' && currentProfileQuestionIndex >= initialCompanyProfileQuestions.length) {
      submitCompanyProfile();
    }
  }, [conversationState, currentProfileQuestionIndex, addAiMessage, submitCompanyProfile]);

  useEffect(() => {
    if (conversationState === 'asking_risk_questions' && currentRiskQuestionIndex < riskQuestions.length) {
      const question = riskQuestions[currentRiskQuestionIndex];
      addAiMessage(question.question_text, 'question', question.id, question.helper_text);
    } else if (conversationState === 'asking_risk_questions' && currentRiskQuestionIndex >= riskQuestions.length && riskQuestions.length > 0) {
      addAiMessage("Thanks for answering all the questions! I'm now analyzing your responses to generate the risk assessment...");
      setConversationState('submitting_answers');
      submitRiskAnswers();
    }
  }, [conversationState, currentRiskQuestionIndex, riskQuestions, addAiMessage, submitRiskAnswers]);

  const handleUserInput = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || isLoading) return;

    const userText = userInput;
    addMessage('user', userText);
    setUserInput('');
    setIsLoading(true);
    setError(null);

    if (conversationState === 'collecting_profile') {
      const currentQuestion = initialCompanyProfileQuestions[currentProfileQuestionIndex];
      let value: string | string[] = userText;
      if (currentQuestion.id === 'emerging_technologies') {
        value = userText.split(',').map((s: string) => s.trim()).filter((s: string) => s);
      }
      setCompanyProfileData((prev: Partial<CompanyProfile>) => ({ ...prev, [currentQuestion.id]: value }));
      setCurrentProfileQuestionIndex((prev: number) => prev + 1);
    } else if (conversationState === 'asking_risk_questions') {
      const currentQuestion = riskQuestions[currentRiskQuestionIndex];
      setRiskAnswers((prev: RiskAnswer[]) => [...prev, { question_id: currentQuestion.id, answer: userText }]);
      setCurrentRiskQuestionIndex((prev: number) => prev + 1);
    }
    setIsLoading(false);
  };

  const renderMessageContent = (msg: Message) => {
    if (msg.type === 'assessment_result' && msg.data) {
      const result = msg.data; // Already typed as RiskAssessmentResult | undefined
      return (
        <div className="p-4 bg-gray-800 rounded-lg shadow-md my-2">
          <h3 className="text-xl font-bold text-indigo-300 mb-3">Risk Assessment Summary</h3>
          <p className="mb-2 text-lg"><strong>Overall Weighted Score:</strong> <span className={`font-bold ${result.overall_weighted_score < 50 ? 'text-red-400' : result.overall_weighted_score < 75 ? 'text-yellow-400' : 'text-green-400'}`}>{result.overall_weighted_score.toFixed(2)} / 100</span></p>
          
          <h4 className="text-lg font-semibold text-indigo-400 mt-4 mb-2">Risk Breakdown:</h4>
          <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
            {result.risk_table.map(row => (
              <div key={row.id} className="p-3 bg-gray-700 rounded">
                <p><strong>{row.category} (Weight: {(row.weight * 100).toFixed(0)}%):</strong> <span className={`font-semibold ${row.score < (row.max_score / 2) ? 'text-red-400' : row.score < (row.max_score * 0.75) ? 'text-yellow-400' : 'text-green-400'}`}>{row.score} / {row.max_score}</span></p>
                <p className="text-sm text-gray-400"><em>{row.explanation}</em></p>
              </div>
            ))}
          </div>

          <h4 className="text-lg font-semibold text-indigo-400 mt-4 mb-2">Recommendations:</h4>
          <ul className="list-disc list-inside space-y-1 pl-4">
            {result.recommendations.map((rec, i) => <li key={i}>{rec}</li>)}
          </ul>

          {result.resources && result.resources.length > 0 && (
            <>
              <h4 className="text-lg font-semibold text-indigo-400 mt-4 mb-2">Helpful Resources:</h4>
              <ul className="list-disc list-inside space-y-1 pl-4">
                {result.resources.map((res, i) => <li key={i}><a href={res.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">{res.title}</a></li>)}
              </ul>
            </>
          )}
        </div>
      );
    }
    return msg.text?.split('\n').map((line, index) => (
        <React.Fragment key={index}>
            {line.startsWith('*Helper:') ? <em className="text-sm text-gray-400">{line}</em> : line}
            {index < (msg.text?.split('\n').length || 0) - 1 && <br />}
        </React.Fragment>
    ));
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      <header className="p-4 bg-gray-900/80 backdrop-blur-md shadow-lg sticky top-0 z-10">
        <h1 className="text-2xl font-bold text-center bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent">
          RiskIQ-AI Assessment
        </h1>
      </header>

      <main className="flex-grow p-4 space-y-4 overflow-y-auto" style={{maxHeight: 'calc(100vh - 160px)'}}>
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xl lg:max-w-2xl px-4 py-3 rounded-2xl shadow-md ${msg.type === 'error' ? 'bg-red-900/50' : msg.sender === 'user' ? 'bg-indigo-600' : 'bg-gray-700'}`}>
              {renderMessageContent(msg)}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </main>

      <footer className="p-4 bg-gray-900/80 backdrop-blur-md sticky bottom-0 z-10">
        {error && (
          <div className="text-red-400 text-center mb-2 p-2 bg-red-900/50 rounded flex items-center justify-center gap-2">
            <span>Error: {error}</span>
            <button
              onClick={handleRetry}
              className="px-3 py-1 rounded bg-red-800 hover:bg-red-700 transition"
            >
              Retry
            </button>
          </div>
        )}
        <form onSubmit={handleUserInput} className="flex gap-3">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder={isLoading ? "Thinking..." : (conversationState === 'collecting_profile' || conversationState === 'asking_risk_questions' ? "Type your answer..." : "Conversation ended.")}
            className="flex-grow p-3 rounded-xl bg-gray-800 border border-gray-700 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition disabled:opacity-50"
            disabled={isLoading || !['collecting_profile', 'asking_risk_questions'].includes(conversationState)}
          />
          <button
            type="submit"
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold shadow-lg hover:from-indigo-600 hover:to-purple-700 transition disabled:opacity-50"
            disabled={isLoading || !userInput.trim() || !['collecting_profile', 'asking_risk_questions'].includes(conversationState)}
          >
            Send
          </button>
        </form>
      </footer>
    </div>
  );
};

export default ConversationalAssessmentPage;


