
export interface ChunkAnalysis {
  chunkSummary: string;
  relevanceToQueries: string; // e.g., "High", "Medium", "Low"
  suggestedImprovements: string[];
}

export interface AnalysisResults {
  embeddingRelevanceScore: number; // 0-100
  semanticDensityScore: number; // 0-100
  machineValidatedAuthorityScore: number; // 0-100
  chunkAnalysis: ChunkAnalysis[];
  semanticGaps: string[];
  overallRecommendations: string[];
}

export interface ScoreData {
  name: string;
  score: number;
}

// Example of a default structure if Gemini fails or for initial state
export const initialAnalysisResults: AnalysisResults = {
  embeddingRelevanceScore: 0,
  semanticDensityScore: 0,
  machineValidatedAuthorityScore: 0,
  chunkAnalysis: [],
  semanticGaps: [],
  overallRecommendations: [],
};
