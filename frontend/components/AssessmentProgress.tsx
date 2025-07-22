import React from 'react';

interface ProgressProps {
  currentSection: string;
  currentQuestion: string;
  sections: any[];
  responses: Record<string, Record<string, any>>;
}

const AssessmentProgress: React.FC<ProgressProps> = ({
  currentSection,
  currentQuestion,
  sections,
  responses
}) => {
  const getCurrentSectionProgress = () => {
    if (!currentSection) return { completed: 0, total: 0, percentage: 0 };
    
    const section = sections.find(s => s.id === currentSection);
    if (!section) return { completed: 0, total: 0, percentage: 0 };
    
    const sectionResponses = responses[currentSection] || {};
    const completed = Object.keys(sectionResponses).length;
    const total = section.questions.length;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    return { completed, total, percentage };
  };

  const getOverallProgress = () => {
    const totalQuestions = sections.reduce((sum, section) => sum + section.questions.length, 0);
    const answeredQuestions = Object.values(responses).reduce(
      (sum, sectionResponses) => sum + Object.keys(sectionResponses || {}).length, 
      0
    );
    
    const percentage = totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;
    
    return { 
      answered: answeredQuestions,
      total: totalQuestions,
      percentage
    };
  };

  const getCurrentQuestionNumber = () => {
    let questionNumber = 0;
    
    for (const section of sections) {
      if (section.id === currentSection) {
        const questionIndex = section.questions.findIndex((q: any) => q.id === currentQuestion);
        questionNumber += questionIndex + 1;
        break;
      } else {
        questionNumber += section.questions.length;
      }
    }
    
    return questionNumber;
  };

  const sectionProgress = getCurrentSectionProgress();
  const overallProgress = getOverallProgress();
  const currentSectionObj = sections.find(s => s.id === currentSection);
  const questionNumber = getCurrentQuestionNumber();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-gray-900">
          {currentSectionObj?.name || 'Assessment'}
        </h1>
        <div className="text-sm text-gray-600">
          Question {questionNumber} of 120
        </div>
      </div>
      
      {/* Overall Progress */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Overall Progress</span>
          <span>{overallProgress.percentage}% ({overallProgress.answered}/{overallProgress.total})</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-blue-600 h-3 rounded-full transition-all duration-300 relative"
            style={{ width: `${overallProgress.percentage}%` }}
          >
            <div className="absolute right-0 top-0 h-full w-1 bg-blue-800 rounded-r-full"></div>
          </div>
        </div>
      </div>
      
      {/* Section Progress */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Section Progress</span>
          <span>{sectionProgress.percentage}% ({sectionProgress.completed}/{sectionProgress.total})</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-green-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${sectionProgress.percentage}%` }}
          />
        </div>
      </div>

      {/* Section Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2 mt-4">
        {sections.map((section, index) => {
          const sectionResponses = responses[section.id] || {};
          const sectionCompleted = Object.keys(sectionResponses).length;
          const sectionTotal = section.questions.length;
          const sectionPercentage = sectionTotal > 0 ? (sectionCompleted / sectionTotal) * 100 : 0;
          const isCurrentSection = section.id === currentSection;
          
          return (
            <div
              key={section.id}
              className={`p-2 rounded-lg text-xs text-center transition-all ${
                isCurrentSection 
                  ? 'bg-blue-100 border-2 border-blue-500 text-blue-800' 
                  : sectionPercentage === 100
                  ? 'bg-green-100 text-green-800'
                  : sectionPercentage > 0
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              <div className="font-medium truncate" title={section.name}>
                {section.name.split(' ')[0]}
              </div>
              <div className="text-xs mt-1">
                {sectionCompleted}/{sectionTotal}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                <div 
                  className={`h-1 rounded-full transition-all duration-300 ${
                    isCurrentSection ? 'bg-blue-600' :
                    sectionPercentage === 100 ? 'bg-green-600' :
                    sectionPercentage > 0 ? 'bg-yellow-600' : 'bg-gray-400'
                  }`}
                  style={{ width: `${sectionPercentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AssessmentProgress;