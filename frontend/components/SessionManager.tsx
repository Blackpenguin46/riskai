import React, { useState, useEffect } from 'react';
import { getResumableSessions, resumeSession } from '../lib/session-api';

interface SessionManagerProps {
  userId?: string;
  onSessionSelected: (sessionData: any) => void;
  onNewSession: () => void;
}

const SessionManager: React.FC<SessionManagerProps> = ({ userId, onSessionSelected, onNewSession }) => {
  const [resumableSessions, setResumableSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadResumableSessions();
  }, [userId]);

  const loadResumableSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await getResumableSessions(userId);
      setResumableSessions(result.sessions || []);
    } catch (err) {
      setError('Failed to load resumable sessions');
      console.error('Error loading resumable sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResumeSession = async (sessionId: string) => {
    try {
      setLoading(true);
      const sessionData = await resumeSession(sessionId);
      onSessionSelected(sessionData);
    } catch (err) {
      setError('Failed to resume session');
      console.error('Error resuming session:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="p-4 bg-gray-800 rounded-lg shadow-lg">
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-4 py-1">
            <div className="h-4 bg-gray-700 rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-700 rounded"></div>
              <div className="h-4 bg-gray-700 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-900/30 border border-red-500 rounded-lg">
        <p className="text-red-300">{error}</p>
        <button 
          onClick={loadResumableSessions}
          className="mt-2 px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded-lg"
        >
          Retry
        </button>
      </div>
    );
  }

  if (resumableSessions.length === 0) {
    return (
      <div className="p-6 bg-gray-800 rounded-lg shadow-lg">
        <h3 className="text-xl font-semibold mb-4">Start New Assessment</h3>
        <p className="text-gray-300 mb-4">You don't have any in-progress assessments.</p>
        <button
          onClick={onNewSession}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition"
        >
          Start New Assessment
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-800 rounded-lg shadow-lg">
      <h3 className="text-xl font-semibold mb-4">Resume Assessment</h3>
      <p className="text-gray-300 mb-4">You have {resumableSessions.length} in-progress assessment(s):</p>
      
      <div className="space-y-4 mb-6">
        {resumableSessions.map((session) => (
          <div 
            key={session.session_id}
            className="p-4 bg-gray-700 hover:bg-gray-600 rounded-lg cursor-pointer transition"
            onClick={() => handleResumeSession(session.session_id)}
          >
            <div className="flex justify-between items-center">
              <h4 className="font-medium text-lg">{session.assessment_name}</h4>
              <span className="px-2 py-1 bg-indigo-600 text-white text-xs rounded-full">
                {session.completion_percentage.toFixed(0)}% Complete
              </span>
            </div>
            <div className="mt-2 text-sm text-gray-400">
              <p>Started: {formatDate(session.start_time)}</p>
              <p>Last activity: {formatDate(session.last_activity)}</p>
              <p>Sections completed: {session.sections_completed} of {session.total_sections}</p>
            </div>
          </div>
        ))}
      </div>
      
      <div className="border-t border-gray-700 pt-4">
        <button
          onClick={onNewSession}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition"
        >
          Start New Assessment
        </button>
      </div>
    </div>
  );
};

export default SessionManager;