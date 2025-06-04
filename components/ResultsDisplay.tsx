
import React, { useState, useEffect } from 'react';
import { AnalysisResults, ScoreData } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { CheckCircle, AlertCircle, Sliders, ListChecks, Lightbulb, FileText } from 'lucide-react';

interface ResultsDisplayProps {
  results: AnalysisResults;
}

const ScoreBarChart: React.FC<{ data: ScoreData[] }> = ({ data }) => {
  const colors = ['#38bdf8', '#818cf8', '#a78bfa']; // sky, indigo, violet

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
        <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" tick={{ fill: '#cbd5e1' }} />
        <YAxis dataKey="name" type="category" stroke="#94a3b8" width={150} tick={{ fill: '#cbd5e1', fontSize: 12 }} />
        <Tooltip
          cursor={{ fill: 'rgba(71, 85, 105, 0.5)' }}
          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
          labelStyle={{ color: '#e2e8f0', fontWeight: 'bold' }}
          itemStyle={{ color: '#cbd5e1' }}
        />
        <Legend wrapperStyle={{ color: '#cbd5e1', paddingTop: '10px' }} />
        <Bar dataKey="score" name="Score (0-100)" barSize={30}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

const SectionCard: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode }> = ({ title, icon, children }) => (
  <div className="bg-slate-700 bg-opacity-50 p-5 rounded-lg shadow-lg border border-slate-600">
    <h3 className="text-xl font-semibold text-sky-300 mb-3 flex items-center gap-2">
      {icon} {title}
    </h3>
    {children}
  </div>
);

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    // Set mounted to true after a short delay to allow transition to occur
    const timer = setTimeout(() => setIsMounted(true), 50); 
    return () => clearTimeout(timer);
  }, []);

  const scoreData: ScoreData[] = [
    { name: 'Embedding Relevance', score: results.embeddingRelevanceScore },
    { name: 'Semantic Density', score: results.semanticDensityScore },
    { name: 'Authority Score', score: results.machineValidatedAuthorityScore },
  ];

  return (
    <div className={`space-y-6 transition-all duration-500 ease-in-out ${isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2.5'}`}>
      <h2 className="text-3xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-500 mb-6">
        Analysis Report
      </h2>

      <SectionCard title="Key Metrics" icon={<Sliders size={22} />}>
        <ScoreBarChart data={scoreData} />
      </SectionCard>

      {results.chunkAnalysis && results.chunkAnalysis.length > 0 && (
        <SectionCard title="Chunk-level Analysis & Suggestions" icon={<FileText size={22} />}>
          <div className="space-y-4 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
            {results.chunkAnalysis.map((chunk, index) => (
              <details key={index} className="bg-slate-600 bg-opacity-70 p-4 rounded-md group">
                <summary className="font-medium text-slate-200 cursor-pointer list-none flex justify-between items-center hover:text-sky-300 transition-colors">
                  <span className="truncate pr-2">Chunk: {chunk.chunkSummary}</span>
                  <span className="text-xs text-slate-400 ml-2 group-open:rotate-90 transform transition-transform duration-200">&#9656;</span>
                </summary>
                <div className="mt-3 text-sm text-slate-300 space-y-2">
                  <p><strong className="text-slate-100">Relevance:</strong> {chunk.relevanceToQueries}</p>
                  {chunk.suggestedImprovements.length > 0 && (
                    <div>
                      <strong className="text-slate-100">Improvements:</strong>
                      <ul className="list-disc list-inside ml-4 mt-1 space-y-1">
                        {chunk.suggestedImprovements.map((imp, i) => <li key={i}>{imp}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              </details>
            ))}
          </div>
        </SectionCard>
      )}

      {results.semanticGaps && results.semanticGaps.length > 0 && (
        <SectionCard title="Semantic Gaps Identified" icon={<AlertCircle size={22} className="text-amber-400" />}>
          <ul className="list-disc list-inside text-slate-300 space-y-1 pl-2">
            {results.semanticGaps.map((gap, index) => (
              <li key={index}>{gap}</li>
            ))}
          </ul>
        </SectionCard>
      )}

      {results.overallRecommendations && results.overallRecommendations.length > 0 && (
        <SectionCard title="Overall Recommendations" icon={<Lightbulb size={22} className="text-green-400" />}>
          <ul className="list-disc list-inside text-slate-300 space-y-1 pl-2">
            {results.overallRecommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </SectionCard>
      )}
      
      {(results.chunkAnalysis.length === 0 && results.semanticGaps.length === 0 && results.overallRecommendations.length === 0 && 
       results.embeddingRelevanceScore === 0 && results.semanticDensityScore === 0 && results.machineValidatedAuthorityScore === 0) && (
        <div className="text-center py-10">
          <CheckCircle size={48} className="text-slate-500 mx-auto mb-4" />
          <p className="text-slate-400">No specific recommendations or gaps identified based on the provided input, or there was an issue processing.</p>
          <p className="text-slate-500 text-sm">Consider refining your content or queries for a more detailed analysis.</p>
        </div>
      )}
      {/* Custom scrollbar styling for chunk analysis section can be added globally in index.html if needed, or use Tailwind plugins if available */}
      {/* For now, it will use default browser scrollbars or Tailwind's scrollbar utilities if configured */}
    </div>
  );
};
