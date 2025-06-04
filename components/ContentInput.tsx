
import React from 'react';
import { BookText } from 'lucide-react';

interface ContentInputProps {
  content: string;
  setContent: (value: string) => void;
}

export const ContentInput: React.FC<ContentInputProps> = ({ content, setContent }) => {
  return (
    <div>
      <label htmlFor="content-input" className="flex items-center gap-2 text-xl font-semibold text-slate-300 mb-2">
        <BookText size={24} className="text-sky-400" />
        Your Content
      </label>
      <textarea
        id="content-input"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Paste your article, blog post, or page content here..."
        className="w-full h-48 p-3 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-shadow resize-y"
      />
      <p className="text-xs text-slate-500 mt-1">Provide the full text content you want to analyze.</p>
    </div>
  );
};
