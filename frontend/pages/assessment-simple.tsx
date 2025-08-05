import React from 'react';

const AssessmentSimple: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            Assessment Page
          </h1>
          <p className="text-gray-600 mb-4">
            This is a simplified assessment page for the research demo.
          </p>
          <div className="text-center">
            <a
              href="/research-demo"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Go to Research Demo
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssessmentSimple;