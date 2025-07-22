import React from 'react';

interface QuestionNavigationProps {
  sections: any[];
  currentSection: string;
  currentQuestion: string;
  responses: Record<string, Record<string, any>>;
  onNavigateToQuestion: (sectionId: string, questionId: string) => void;
  disabled?: boolean;
}

const QuestionNavigation: React.FC<QuestionNavigationProps> = ({
  sections,
  currentSection,
  currentQuestion,
  responses,
  onNavigateToQuestion,
  disabled = false
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  const getQuestionStatus = (sectionId: string, questionId: string) => {
    const sectionResponses = responses[sectionId] || {};
    const hasResponse = questionId in sectionResponses && 
                       sectionResponses[questionId] !== null && 
                       sectionResponses[questionId] !== undefined && 
                       sectionResponses[questionId] !== '';
    
    const isCurrent = sectionId === currentSection && questionId === currentQuestion;
    
    if (isCurrent) return 'current';
    if (hasResponse) return 'completed';
    return 'pending';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'current':
        return 'bg-blue-500 text-white border-blue-600';
      case 'completed':
        return 'bg-green-500 text-white border-green-600';
      case 'pending':
        return 'bg-gray-200 text-gray-600 border-gray-300';
      default:
        return 'bg-gray-200 text-gray-600 border-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'current':
        return '▶';
      case 'completed':
        return '✓';
      case 'pending':
        return '○';
      default:
        return '○';
    }
  };

  if (!isExpanded) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
        <button
          onClick={() => setIsExpanded(true)}
          className="w-full flex items-center justify-between text-left"
          disabled={disabled}
        >
          <span className="text-lg font-semibold text-gray-900">
            Question Navigation
          </span>
          <span className="text-gray-500">
            Click to expand ▼
          </span>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Question Navigation
        </h3>
        <button
          onClick={() => setIsExpanded(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          Collapse ▲
        </button>
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {sections.map((section, sectionIndex) => {
          const sectionResponses = responses[section.id] || {};
          const completedQuestions = Object.keys(sectionResponses).filter(
            qId => sectionResponses[qId] !== null && 
                   sectionResponses[qId] !== undefined && 
                   sectionResponses[qId] !== ''
          ).length;
          
          return (
            <div key={section.id} className="border rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-800 text-sm">
                  {sectionIndex + 1}. {section.name}
                </h4>
                <span className="text-xs text-gray-500">
                  {completedQuestions}/{section.questions.length}
                </span>
              </div>
              
              <div className="grid grid-cols-5 gap-1">
                {section.questions.map((question: any, questionIndex: number) => {
                  const status = getQuestionStatus(section.id, question.id);
                  const statusColor = getStatusColor(status);
                  const statusIcon = getStatusIcon(status);
                  
                  return (
                    <button
                      key={question.id}
                      onClick={() => onNavigateToQuestion(section.id, question.id)}
                      disabled={disabled}
                      className={`
                        w-8 h-8 text-xs rounded border-2 transition-all
                        hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-500
                        ${statusColor}
                        ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
                      `}
                      title={`Question ${sectionIndex * 10 + questionIndex + 1}: ${question.text.substring(0, 50)}...`}
                    >
                      <span className="sr-only">
                        Question {sectionIndex * 10 + questionIndex + 1}
                      </span>
                      {statusIcon}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-center space-x-6 text-xs text-gray-600">
          <div className="flex items-center space-x-1">
            <div className="w-4 h-4 bg-blue-500 rounded border-2 border-blue-600 flex items-center justify-center text-white text-xs">
              ▶
            </div>
            <span>Current</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-4 h-4 bg-green-500 rounded border-2 border-green-600 flex items-center justify-center text-white text-xs">
              ✓
            </div>
            <span>Completed</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-4 h-4 bg-gray-200 rounded border-2 border-gray-300 flex items-center justify-center text-gray-600 text-xs">
              ○
            </div>
            <span>Pending</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionNavigation;