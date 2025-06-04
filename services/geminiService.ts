
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { AnalysisResults, initialAnalysisResults } from '../types';

// IMPORTANT: API key is sourced from environment variable `process.env.API_KEY`
// This variable MUST be set in the build/runtime environment for the application to work.
// For client-side applications, this usually means it's replaced at build time (e.g., by Vite, Webpack).
// If `process.env.API_KEY` is undefined, the API call will fail.
const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  console.warn(
    "Gemini API Key is not configured. Please set the API_KEY environment variable." +
    "The application will likely fail to fetch analysis from the AI."
  );
}

const ai = new GoogleGenAI({ apiKey: API_KEY! }); // Use non-null assertion as per instructions assumption
const model = 'gemini-2.5-flash-preview-04-17';

export const analyzeContentWithGemini = async (content: string, queries: string[]): Promise<AnalysisResults> => {
  if (!API_KEY) {
    // Simulate an error or return empty results if API key is not available client-side without proper build setup.
    // This matches the behavior if the API call itself fails due to missing key.
    throw new Error("API Key for Gemini not configured. Cannot perform analysis.");
  }

  const queryListString = queries.map(q => `- ${q}`).join('\n');

  const prompt = `
    You are a Semantic Optimization Assistant. Analyze the provided content based on the target queries.
    Return your analysis STRICTLY in JSON format. Do not include any explanatory text before or after the JSON block.
    If you cannot perform a full analysis, return the JSON structure with scores set to 0 and empty arrays for lists.

    Content:
    """
    ${content}
    """

    Target Queries:
    """
    ${queryListString}
    """

    Provide an analysis in the following JSON structure:
    {
      "embeddingRelevanceScore": number, // Score (0-100) for semantic similarity between content and queries.
      "semanticDensityScore": number, // Score (0-100) for topic term concentration and entity spread relevant to queries.
      "machineValidatedAuthorityScore": number, // Score (0-100) evaluating perceived authoritativeness and factual alignment (general knowledge, not specific fact-checking).
      "chunkAnalysis": [ // Array of objects, analyzing content by conceptual chunks.
        {
          "chunkSummary": "string", // Brief summary of the chunk's main topic.
          "relevanceToQueries": "string", // e.g., "High", "Medium", "Low", "Not Applicable"
          "suggestedImprovements": ["string"] // Array of specific, actionable suggestions for this chunk.
        }
      ],
      "semanticGaps": ["string"], // Array of topics/entities underrepresented or missing in content relative to queries.
      "overallRecommendations": ["string"] // Array of general, actionable recommendations for content improvement.
    }

    Guidelines for scores:
    - embeddingRelevanceScore: Higher if content directly and comprehensively addresses the queries.
    - semanticDensityScore: Higher if content is rich in relevant topics/entities related to queries, well-distributed.
    - machineValidatedAuthorityScore: Higher if content appears well-structured, coherent, and aligns with generally accepted knowledge principles for reliable information. This is a qualitative assessment of perceived authority, not a deep fact-check.

    Be concise and actionable in your text descriptions and recommendations.
    Focus on SEO and content professionals' needs.
    Ensure all scores are numbers between 0 and 100.
    If content is too short or irrelevant for some analysis, provide default/empty values within the JSON structure.
    Make sure the 'chunkAnalysis' array provides distinct conceptual chunks. If the content is very short, it might be a single chunk.
  `;

  try {
    const response: GenerateContentResponse = await ai.models.generateContent({
      model: model,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        // Omitting thinkingConfig to default to enabled thinking for higher quality analysis.
      },
    });

    let jsonStr = response.text.trim();
    
    // Remove Markdown code fences if present
    const fenceRegex = /^```(\w*)?\s*\n?(.*?)\n?\s*```$/s;
    const match = jsonStr.match(fenceRegex);
    if (match && match[2]) {
      jsonStr = match[2].trim();
    }

    // Validate the JSON structure before returning
    try {
        const parsedData = JSON.parse(jsonStr);
        // Basic validation for key fields. More thorough validation could be added.
        if (
            typeof parsedData.embeddingRelevanceScore !== 'number' ||
            typeof parsedData.semanticDensityScore !== 'number' ||
            typeof parsedData.machineValidatedAuthorityScore !== 'number' ||
            !Array.isArray(parsedData.chunkAnalysis) ||
            !Array.isArray(parsedData.semanticGaps) ||
            !Array.isArray(parsedData.overallRecommendations)
        ) {
            console.error("Parsed JSON has unexpected structure:", parsedData);
            throw new Error("AI response has an unexpected structure. Displaying default results.");
        }
        return parsedData as AnalysisResults;
    } catch (parseError) {
        console.error("Failed to parse JSON response from AI:", parseError);
        console.error("Received string for parsing:", jsonStr); // Log the string that failed to parse
        // Return a default structure or re-throw a more specific error
        // This helps the UI display something sensible instead of crashing.
        return { 
            ...initialAnalysisResults, 
            overallRecommendations: ["Failed to parse AI response. Please check the console for details or try again."]
        };
    }

  } catch (error: any) {
    console.error("Error calling Gemini API:", error);
    // Handle specific API errors if needed, e.g., API key issues, rate limits
    if (error.message && error.message.includes('API key not valid')) {
        throw new Error("Invalid API Key. Please check your Gemini API key configuration.");
    }
    throw new Error(`AI analysis failed: ${error.message || 'Unknown error'}`);
  }
};
