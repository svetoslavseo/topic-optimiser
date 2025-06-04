
import React from 'react';
import { Search } from 'lucide-react';

interface QueryInputProps {
  queries: string;
  setQueries: (value: string) => void;
}

export const QueryInput: React.FC<QueryInputProps> = ({ queries, setQueries }) => {
  return (
    <div>
      <label htmlFor="query-input" className="flex items-center gap-2 text-xl font-semibold text-slate-300 mb-2">
        <Search size={24} className="text-sky-400" />
        Target Queries
      </label>
      <textarea
        id="query-input"
        value={queries}
        onChange={(e) => setQueries(e.target.value)}
        placeholder="Enter target queries or keywords, one per line. e.g.,&#10;What are semantic embeddings?&#10;AI content optimization tips"
        className="w-full h-32 p-3 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow resize-y"
      />
      <p className="text-xs text-slate-500 mt-1">List keywords or questions your content should rank for.</p>
    </div>
  );
};
