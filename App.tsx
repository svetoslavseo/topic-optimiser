
import React, { useState, useCallback } from 'react';
import { AnalysisResults, initialAnalysisResults } from './types';
import { ContentInput } from './components/ContentInput';
import { QueryInput } from './components/QueryInput';
import { UrlInput } from './components/UrlInput';
import { ResultsDisplay } from './components/ResultsDisplay';
import { LoadingSpinner } from './components/LoadingSpinner';
import { analyzeContentWithGemini } from './services/geminiService';
import { AlertTriangle, Zap, FileText, Globe } from 'lucide-react'; // Using lucide-react for icons

const App: React.FC = () => {
  const [content, setContent] = useState<string>('');
  const [queries, setQueries] = useState<string>(''); // Store as single string, split later
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [inputMode, setInputMode] = useState<'manual' | 'url'>('manual');
  const [contentSource, setContentSource] = useState<string>('');

  // Get API keys from environment or you can set them here
  const firecrawlApiKey = (import.meta as any).env?.VITE_FIRECRAWL_API_KEY;

  const handleContentCrawled = useCallback((crawledContent: string, title?: string, url?: string) => {
    setContent(crawledContent);
    setContentSource(url ? `Crawled from: ${url}${title ? ` (${title})` : ''}` : '');
    setError(null);
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!content.trim() || !queries.trim()) {
      setError('Please provide both content and queries to analyze.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setAnalysisResults(null);

    const queryList = queries.split('\n').map(q => q.trim()).filter(q => q.length > 0);
    if (queryList.length === 0) {
        setError('Please provide at least one valid query.');
        setIsLoading(false);
        return;
    }

    try {
      const results = await analyzeContentWithGemini(content, queryList);
      setAnalysisResults(results);
    } catch (e: any) {
      console.error("Error during analysis:", e);
      setError(e.message || 'Failed to analyze content. Please check your API key and network.');
      setAnalysisResults(initialAnalysisResults); // Show structure with 0 scores on error
    } finally {
      setIsLoading(false);
    }
  }, [content, queries]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 text-slate-100 p-4 sm:p-8 flex flex-col items-center" style={{background: 'linear-gradient(to bottom right, #1e293b, #374151, #313856)'}}>
      <header className="w-full max-w-5xl mb-8 text-center">
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-2">
          AI-Powered Topic Optimizer
        </h1>
        <p className="text-slate-400 text-lg">
          Elevate your content's AI readiness.
        </p>
      </header>

      <main className="w-full max-w-5xl">
        <div className="bg-slate-800 p-6 rounded-xl shadow-2xl space-y-6 border border-slate-700">
          {/* Input Mode Toggle */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setInputMode('manual')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                inputMode === 'manual'
                  ? 'text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
              style={inputMode === 'manual' ? {backgroundColor: '#313856'} : {}}
            >
              <FileText size={16} />
              Manual Input
            </button>
            <button
              onClick={() => setInputMode('url')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                inputMode === 'url'
                  ? 'text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
              style={inputMode === 'url' ? {backgroundColor: '#313856'} : {}}
            >
              <Globe size={16} />
              Crawl URL
            </button>
          </div>

          {inputMode === 'manual' ? (
            <ContentInput content={content} setContent={setContent} />
          ) : (
            <UrlInput onContentCrawled={handleContentCrawled} firecrawlApiKey={firecrawlApiKey} />
          )}

          {contentSource && (
            <div className="p-3 rounded-lg" style={{backgroundColor: 'rgba(49, 56, 86, 0.3)', borderColor: '#313856', borderWidth: '1px'}}>
              <p className="text-sm" style={{color: '#8b9dc3'}}>{contentSource}</p>
            </div>
          )}

          <QueryInput queries={queries} setQueries={setQueries} />
          <button
            onClick={handleAnalyze}
            disabled={isLoading || !content.trim() || !queries.trim()}
            className="w-full flex items-center justify-center gap-2 disabled:bg-slate-600 text-white font-semibold py-3 px-4 rounded-lg shadow-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-opacity-75"
            style={{
              backgroundColor: isLoading || !content.trim() || !queries.trim() ? '#475569' : '#ff8c42',
              boxShadow: `0 0 0 2px rgba(255, 140, 66, 0.4)`
            }}
            onMouseEnter={(e) => {
              if (!isLoading && content.trim() && queries.trim()) {
                (e.target as HTMLButtonElement).style.backgroundColor = '#ff7a28';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading && content.trim() && queries.trim()) {
                (e.target as HTMLButtonElement).style.backgroundColor = '#ff8c42';
              }
            }}
          >
            {isLoading ? (
              <>
                <LoadingSpinner /> Analyzing...
              </>
            ) : (
              <>
                <Zap size={20} /> Analyze Content
              </>
            )}
          </button>
          {error && (
            <div className="mt-4 p-3 bg-red-700 bg-opacity-50 text-red-300 border border-red-600 rounded-lg flex items-center gap-2">
              <AlertTriangle size={20} /> 
              <p>{error}</p>
            </div>
          )}
        </div>

        {/* Analysis Results Section */}
        {(isLoading || analysisResults || error) && (
          <div className="mt-8 bg-slate-800 p-6 rounded-xl shadow-2xl border border-slate-700">
            <div className="flex items-center gap-2 mb-6">
              <Zap size={20} style={{color: '#ff8c42'}} />
              <h2 className="text-xl font-semibold text-slate-200">Analysis Results</h2>
            </div>
            
            {isLoading && !analysisResults && (
              <div className="flex flex-col items-center justify-center py-12">
                <LoadingSpinner size="large" />
                <p className="mt-4 text-slate-400">Generating insights...</p>
              </div>
            )}
            
            {!isLoading && analysisResults && (
              <ResultsDisplay results={analysisResults} />
            )}
            
            {!isLoading && !analysisResults && !error && (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Zap size={48} className="text-slate-600 mb-4" />
                <h2 className="text-2xl font-semibold text-slate-400">Ready to Optimize?</h2>
                <p className="text-slate-500">Enter your content and queries, then click "Analyze Content".</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Metrics Explanation Section */}
      <section className="w-full max-w-5xl mt-16 mb-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-4">Algorithm Implementation Details</h2>
          <p className="text-slate-400 text-lg">Detailed computational methods and mathematical formulations used in our scoring algorithms</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Embedding Relevance Score */}
          <div className="bg-slate-800 p-6 rounded-xl shadow-xl border border-slate-700 text-center">
            <div className="mb-4">
              <div className="w-16 h-16 mx-auto rounded-full flex items-center justify-center" style={{backgroundColor: 'rgba(255, 140, 66, 0.2)'}}>
                <Zap size={28} style={{color: '#ff8c42'}} />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Embedding Relevance</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              <strong>Technical Implementation:</strong> Content is intelligently chunked into 512-token segments with 50-token overlap to maintain context. Each chunk and query is processed through SentenceTransformer (all-MiniLM-L6-v2) generating 384-dimensional semantic embeddings. We compute a full similarity matrix between all content chunks and query embeddings using cosine similarity, then apply weighted averaging where chunk importance is determined by maximum query relevance with TF-IDF boosting for high-value content sections.
            </p>
          </div>

          {/* Semantic Density Score */}
          <div className="bg-slate-800 p-6 rounded-xl shadow-xl border border-slate-700 text-center">
            <div className="mb-4">
              <div className="w-16 h-16 mx-auto rounded-full flex items-center justify-center" style={{backgroundColor: 'rgba(139, 157, 195, 0.2)'}}>
                <Globe size={28} style={{color: '#8b9dc3'}} />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Semantic Density</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              <strong>Multi-Layered Analysis:</strong> Entity density calculated via spaCy NLP parsing extracting named entities normalized by token count. K-means clustering performed on chunk embeddings with silhouette score quality assessment measuring intra-cluster cohesion. TF-IDF term diversity analysis evaluating vocabulary richness and distribution. Final semantic density score computed as: (cluster_quality×0.4 + entity_density×0.3 + term_diversity×0.3) × 100, providing comprehensive topic coverage assessment.
            </p>
          </div>

          {/* Machine Validated Authority Score */}
          <div className="bg-slate-800 p-6 rounded-xl shadow-xl border border-slate-700 text-center">
            <div className="mb-4">
              <div className="w-16 h-16 mx-auto rounded-full flex items-center justify-center" style={{backgroundColor: 'rgba(49, 56, 86, 0.3)'}}>
                <FileText size={28} style={{color: '#313856'}} />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Authority Score</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              <strong>Four-Component Assessment:</strong> Linguistic complexity analysis using Flesch-Kincaid readability metrics combined with sentence structure evaluation. Citation pattern detection through regex matching identifying academic references, URLs, and formal citations. Technical terminology density measurement counting domain-specific vocabulary frequency. Authority embedding similarity comparing content against pre-loaded authoritative patterns. Final authority score: (complexity×0.25 + citations×0.30 + technical×0.20 + similarity×0.25) × 100.
            </p>
          </div>
        </div>
      </section>

      <footer className="w-full max-w-5xl mt-12 text-center text-slate-500 text-sm">
        <p>&copy; {new Date().getFullYear()} AI-Powered Topic Optimizer. Powered by <a href="https://storyhawk.io/" target="_blank" rel="noopener noreferrer" className="transition-colors" style={{color: '#8b9dc3'}} onMouseEnter={(e) => (e.target as HTMLAnchorElement).style.color = '#a5b4d3'} onMouseLeave={(e) => (e.target as HTMLAnchorElement).style.color = '#8b9dc3'}>StoryHawk</a>.</p>
      </footer>
    </div>
  );
};

export default App;
