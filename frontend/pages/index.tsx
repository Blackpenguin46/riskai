import React, { useState } from "react";

type BusinessOverview = {
  industry: string;
  core_services: string;
  critical_technologies: string;
};

type RiskQuestion = {
  id: string;
  question: string;
  category: string;
};

type RiskAnswers = { [id: string]: string };

type AssessmentResult = {
  riskScore: number;
  riskLevel: string;
  mitigationGuidance: string;
  techIntegrationTips: string;
  roadmap: { shortTerm: string; mediumTerm: string; longTerm: string };
  freeform: string;
};

export default function Assessment() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [overview, setOverview] = useState<BusinessOverview>({
    industry: "",
    core_services: "",
    critical_technologies: "",
  });
  const [questions, setQuestions] = useState<RiskQuestion[]>([]);
  const [answers, setAnswers] = useState<RiskAnswers>({});
  const [result, setResult] = useState<AssessmentResult | null>(null);

  // Step 1: Submit business overview
  const handleOverviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/company-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(overview),
      });
      const data = await res.json();
      console.log("Backend returned:", data); // Debugging line
      if (Array.isArray(data)) {
        setQuestions(data);
        setStep(2);
      } else if (data.questions && Array.isArray(data.questions)) {
        setQuestions(data.questions);
        setStep(2);
      } else {
        setError("Backend did not return a list of questions.");
        setLoading(false);
        return;
      }
    } catch (err) {
      setError("Failed to fetch risk questions.");
    }
    setLoading(false);
  };

  // Step 2: Submit risk answers
  const handleAnswersSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/risk-assessment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers }),
      });
      const data = await res.json();
      setResult(data);
      setStep(3);
    } catch (err) {
      setError("Failed to fetch risk assessment.");
    }
    setLoading(false);
  };

  // Improved Stepper UI
  const stepper = (
    <div className="flex items-center justify-center w-full max-w-lg mb-10">
      {[1, 2, 3].map((s, i) => (
        <React.Fragment key={s}>
          <div className={`w-10 h-10 flex items-center justify-center rounded-full font-bold text-lg border-2 transition-all duration-300
            ${step === s
              ? "bg-gradient-to-r from-indigo-500 to-purple-500 text-white border-indigo-400 shadow-lg scale-110"
              : step > s
              ? "bg-gradient-to-r from-green-400 to-blue-400 text-white border-green-400"
              : "bg-gray-900 text-gray-400 border-gray-700"}
          `}>
            {s}
          </div>
          {i < 2 && (
            <div className={`flex-1 h-1 mx-2 rounded-full transition-all duration-300
              ${step > s ? "bg-gradient-to-r from-indigo-500 to-purple-500" : "bg-gray-800"}`}></div>
          )}
        </React.Fragment>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-950 to-gray-900 px-4 py-10">
      {stepper}

      {/* Step 1: Business Overview */}
      {step === 1 && (
        <div className="w-full max-w-lg bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/10 p-10 flex flex-col items-center animate-fade-in">
          <h2 className="text-3xl font-extrabold mb-8 text-center bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent drop-shadow-lg">
            Business Overview
          </h2>
          <form onSubmit={handleOverviewSubmit} className="w-full flex flex-col gap-7">
            <input
              className="p-4 rounded-xl bg-white/20 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 border border-transparent focus:border-indigo-400 transition shadow"
              placeholder="Industry (e.g., Healthcare)"
              value={overview.industry}
              onChange={e => setOverview({ ...overview, industry: e.target.value })}
              required
            />
            <input
              className="p-4 rounded-xl bg-white/20 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 border border-transparent focus:border-indigo-400 transition shadow"
              placeholder="Core Services"
              value={overview.core_services}
              onChange={e => setOverview({ ...overview, core_services: e.target.value })}
              required
            />
            <input
              className="p-4 rounded-xl bg-white/20 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 border border-transparent focus:border-indigo-400 transition shadow"
              placeholder="Critical Technologies"
              value={overview.critical_technologies}
              onChange={e => setOverview({ ...overview, critical_technologies: e.target.value })}
              required
            />
            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold shadow-lg hover:from-indigo-600 hover:to-purple-700 transition-all text-lg mt-2"
              disabled={loading}
            >
              {loading ? "Loading..." : "Next"}
            </button>
            {error && <div className="text-red-400 text-center">{error}</div>}
          </form>
        </div>
      )}

      {/* Step 2: Dynamic Risk Questions */}
      {step === 2 && (
        <div className="w-full max-w-lg bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/10 p-10 flex flex-col items-center animate-fade-in">
          <h2 className="text-3xl font-extrabold mb-8 text-center bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent drop-shadow-lg">
            Risk Questions
          </h2>
          <form onSubmit={handleAnswersSubmit} className="w-full flex flex-col gap-7">
            {questions.map(q => (
              <div key={q.id} className="flex flex-col gap-2">
                <label className="font-semibold text-white/90 mb-1">{q.question}</label>
                <input
                  className="p-3 rounded-xl bg-white/20 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 border border-transparent focus:border-indigo-400 transition shadow"
                  value={answers[q.id] || ""}
                  onChange={e => setAnswers({ ...answers, [q.id]: e.target.value })}
                  required
                />
              </div>
            ))}
            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold shadow-lg hover:from-indigo-600 hover:to-purple-700 transition-all text-lg mt-2"
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Get Assessment"}
            </button>
            {error && <div className="text-red-400 text-center">{error}</div>}
          </form>
        </div>
      )}

      {/* Step 3: Results */}
      {step === 3 && result && (
        <div className="w-full max-w-2xl bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/10 p-10 flex flex-col gap-8 animate-fade-in">
          <h2 className="text-3xl font-extrabold mb-8 text-center bg-gradient-to-r from-indigo-300 to-purple-300 bg-clip-text text-transparent drop-shadow-lg">
            Risk Assessment Results
          </h2>
          <div className="flex flex-col items-center gap-4">
            <div className="text-4xl font-extrabold">
              {result.riskLevel === "Critical" && <span className="text-red-400">🔥 Critical</span>}
              {result.riskLevel === "At Risk" && <span className="text-yellow-400">⚠️ At Risk</span>}
              {result.riskLevel === "Low Risk" && <span className="text-green-400">✅ Low Risk</span>}
            </div>
            <div className="w-full bg-gray-800 rounded-full h-6 relative overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700`}
                style={{
                  width: `${result.riskScore}%`,
                  background: result.riskLevel === "Critical"
                    ? "linear-gradient(to right, #ef4444, #f59e42)"
                    : result.riskLevel === "At Risk"
                    ? "linear-gradient(to right, #f59e42, #fbbf24)"
                    : "linear-gradient(to right, #22c55e, #3b82f6)"
                }}
              ></div>
              <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 font-bold text-white">{result.riskScore}/100</span>
            </div>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-r from-indigo-900/80 to-purple-900/80 rounded-xl p-6 shadow border border-white/10">
              <h3 className="text-lg font-bold text-indigo-200 mb-2">Mitigation Guidance</h3>
              <div className="whitespace-pre-line">{result.mitigationGuidance}</div>
            </div>
            <div className="bg-gradient-to-r from-indigo-900/80 to-purple-900/80 rounded-xl p-6 shadow border border-white/10">
              <h3 className="text-lg font-bold text-purple-200 mb-2">Tech Integration Tips</h3>
              <div className="whitespace-pre-line">{result.techIntegrationTips}</div>
            </div>
            <div className="bg-gradient-to-r from-indigo-900/80 to-purple-900/80 rounded-xl p-6 shadow border border-white/10 col-span-2">
              <h3 className="text-lg font-bold text-green-200 mb-2">GRC Roadmap</h3>
              <div>
                <b>Short Term:</b> {result.roadmap.shortTerm}<br />
                <b>Medium Term:</b> {result.roadmap.mediumTerm}<br />
                <b>Long Term:</b> {result.roadmap.longTerm}
              </div>
            </div>
            <div className="bg-gradient-to-r from-indigo-900/80 to-purple-900/80 rounded-xl p-6 shadow border border-white/10 col-span-2">
              <h3 className="text-lg font-bold text-pink-200 mb-2">AI's Freeform Advice</h3>
              <div className="whitespace-pre-line">{result.freeform}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}