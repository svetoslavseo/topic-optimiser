import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import logging
import json
import spacy
import networkx as nx
from collections import Counter, defaultdict
import re
# Import textstat with fallback
try:
    import textstat
except ImportError as e:
    logger.warning(f"textstat import failed: {e}. Using fallback.")
    
    # Create a simple fallback textstat class
    class TextStatFallback:
        @staticmethod
        def flesch_kincaid():
            class FleschKincaid:
                @staticmethod
                def flesch_kincaid(text):
                    # Simple fallback calculation
                    return len(text.split()) / 10  # Rough approximation
            return FleschKincaid()
    
    textstat = TextStatFallback()
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# ML and embeddings with fallbacks
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"sentence_transformers import failed: {e}")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import PCA
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"sklearn import failed: {e}")
    SKLEARN_AVAILABLE = False

try:
    import umap.umap_ as umap
    UMAP_AVAILABLE = True
except ImportError as e:
    logger.warning(f"umap import failed: {e}")
    UMAP_AVAILABLE = False

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"hdbscan import failed: {e}")
    HDBSCAN_AVAILABLE = False

# NLP
import nltk
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# APIs
import cohere
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChunkAnalysis:
    chunk_id: int
    text: str
    summary: str
    embedding: List[float]
    relevance_scores: Dict[str, float]  # query -> relevance score
    semantic_density: float
    authority_indicators: Dict[str, Any]
    suggested_improvements: List[str]

@dataclass 
class SemanticGap:
    gap_type: str  # 'missing_topic', 'weak_coverage', 'semantic_disconnect'
    description: str
    affected_queries: List[str]
    severity: float  # 0-1
    recommendations: List[str]

@dataclass
class AuthoritySignal:
    signal_type: str
    confidence: float
    description: str
    impact_score: float

@dataclass
class AdvancedAnalysisResults:
    # Core scores
    embedding_relevance_score: float
    semantic_density_score: float  
    authority_score: float
    
    # Detailed analysis
    chunk_analysis: List[ChunkAnalysis]
    semantic_gaps: List[SemanticGap]
    authority_signals: List[AuthoritySignal]
    recommendations: List[str]
    
    # Visualization data
    similarity_matrix: List[List[float]]
    topic_clusters: Dict[str, Any]
    semantic_map_data: Dict[str, Any]
    
    # Metadata
    content_source: str = ""
    processing_time: float = 0.0

class AdvancedAnalysisService:
    """Advanced content analysis using real embeddings, NLP, and ML techniques"""
    
    def __init__(self, gemini_api_key: str, cohere_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        self.cohere_api_key = cohere_api_key
        
        # Initialize models
        self._initialize_models()
        self._download_nltk_data()
        
        # Authority knowledge base (in production, load from database)
        self.authority_embeddings = self._load_authority_embeddings()
        
    def _initialize_models(self):
        """Initialize all required models"""
        try:
            # Sentence transformer for embeddings
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model")
            else:
                self.embedding_model = None
                logger.warning("Sentence transformers not available")
            
            # Cohere client (optional)
            if self.cohere_api_key:
                try:
                    self.cohere_client = cohere.Client(self.cohere_api_key)
                    logger.info("Initialized Cohere client")
                except Exception as e:
                    logger.warning(f"Could not initialize Cohere: {e}")
                    self.cohere_client = None
            
            # Gemini for additional analysis
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            
            # SpaCy for NLP
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("SpaCy model not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
                
            # TF-IDF vectorizer
            if SKLEARN_AVAILABLE:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 3)
                )
            else:
                self.tfidf_vectorizer = None
                logger.warning("Sklearn not available - TF-IDF disabled")
            
            # Lemmatizer
            try:
                self.lemmatizer = WordNetLemmatizer()
            except Exception as e:
                logger.warning(f"Could not initialize lemmatizer: {e}")
                self.lemmatizer = None
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            logger.warning(f"Error downloading NLTK data: {e}")
    
    def _load_authority_embeddings(self) -> Dict[str, np.ndarray]:
        """Load pre-computed embeddings of authoritative content"""
        # In production, this would load from a database
        # For now, we'll create some sample authority patterns
        authority_texts = [
            "Comprehensive research methodology with peer-reviewed sources and statistical validation",
            "Expert analysis backed by extensive field experience and academic credentials",
            "Data-driven insights with transparent methodology and verifiable results",
            "Systematic literature review with meta-analysis and confidence intervals",
            "Industry best practices documented through empirical studies and case analyses"
        ]
        
        try:
            authority_embeddings = self.embedding_model.encode(authority_texts)
            return {f"authority_{i}": emb for i, emb in enumerate(authority_embeddings)}
        except Exception as e:
            logger.warning(f"Could not generate authority embeddings: {e}")
            return {}
    
    def analyze_content(self, content: str, queries: List[str]) -> AdvancedAnalysisResults:
        """
        Perform comprehensive content analysis using advanced NLP and ML techniques
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Starting advanced analysis for {len(content)} characters of content")
            
            # Step 1: Text preprocessing and chunking
            chunks = self._intelligent_chunking(content)
            logger.info(f"Created {len(chunks)} intelligent chunks")
            
            # Step 2: Generate embeddings
            content_embeddings = self._generate_embeddings(chunks)
            query_embeddings = self._generate_embeddings(queries)
            
            # Step 3: Calculate embedding relevance scores
            embedding_relevance_score = self._calculate_embedding_relevance(
                content_embeddings, query_embeddings, queries
            )
            
            # Step 4: Analyze semantic density
            semantic_density_score = self._calculate_semantic_density(content, chunks)
            
            # Step 5: Calculate authority score
            authority_score, authority_signals = self._calculate_authority_score(
                content, content_embeddings
            )
            
            # Step 6: Perform chunk analysis
            chunk_analysis = self._analyze_chunks(
                chunks, content_embeddings, query_embeddings, queries
            )
            
            # Step 7: Identify semantic gaps
            semantic_gaps = self._identify_semantic_gaps(
                content, queries, content_embeddings, query_embeddings
            )
            
            # Step 8: Generate similarity matrix and visualizations
            similarity_matrix = self._create_similarity_matrix(content_embeddings, query_embeddings)
            topic_clusters = self._perform_topic_clustering(chunks, content_embeddings)
            semantic_map_data = self._create_semantic_map_data(
                content_embeddings, query_embeddings, chunks, queries
            )
            
            # Step 9: Generate recommendations
            recommendations = self._generate_advanced_recommendations(
                embedding_relevance_score, semantic_density_score, authority_score,
                semantic_gaps, chunk_analysis
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Analysis completed in {processing_time:.2f} seconds")
            
            return AdvancedAnalysisResults(
                embedding_relevance_score=embedding_relevance_score,
                semantic_density_score=semantic_density_score,
                authority_score=authority_score,
                chunk_analysis=chunk_analysis,
                semantic_gaps=semantic_gaps,
                authority_signals=authority_signals,
                recommendations=recommendations,
                similarity_matrix=similarity_matrix,
                topic_clusters=topic_clusters,
                semantic_map_data=semantic_map_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in advanced analysis: {e}")
            # Return basic results with error info
            return AdvancedAnalysisResults(
                embedding_relevance_score=0,
                semantic_density_score=0,
                authority_score=0,
                chunk_analysis=[],
                semantic_gaps=[],
                authority_signals=[],
                recommendations=[f"Analysis failed: {str(e)}"],
                similarity_matrix=[],
                topic_clusters={},
                semantic_map_data={},
                processing_time=time.time() - start_time
            )
    
    def _intelligent_chunking(self, content: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Create intelligent chunks based on semantic boundaries
        """
        if not content.strip():
            return []
        
        # First, split by sentences for better semantic boundaries
        sentences = sent_tokenize(content)
        
        chunks = []
        current_chunk = ""
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            # If adding this sentence would exceed chunk size and we have content
            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                if overlap > 0:
                    words = current_chunk.split()
                    overlap_text = " ".join(words[-overlap:]) if len(words) > overlap else current_chunk
                    current_chunk = overlap_text + " " + sentence
                    current_length = len(current_chunk.split())
                else:
                    current_chunk = sentence
                    current_length = sentence_length
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_length += sentence_length
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        if not texts:
            return np.array([])
        
        if not self.embedding_model:
            logger.warning("Embedding model not available, returning zero embeddings")
            return np.zeros((len(texts), 384))
        
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(texts), 384))
    
    def _calculate_embedding_relevance(self, content_embeddings: np.ndarray, 
                                     query_embeddings: np.ndarray, queries: List[str]) -> float:
        """
        Calculate embedding relevance score using cosine similarity
        """
        if content_embeddings.size == 0 or query_embeddings.size == 0:
            return 0.0
        
        try:
            if not SKLEARN_AVAILABLE:
                logger.warning("Sklearn not available, using simple dot product similarity")
                # Fallback to simple dot product similarity
                content_norm = np.linalg.norm(content_embeddings, axis=1, keepdims=True)
                query_norm = np.linalg.norm(query_embeddings, axis=1, keepdims=True)
                similarities = np.dot(content_embeddings / content_norm, (query_embeddings / query_norm).T)
            else:
                # Compute similarity matrix
                similarities = cosine_similarity(content_embeddings, query_embeddings)
            
            # Calculate weighted average similarity
            max_similarities = np.max(similarities, axis=0)  # Best match for each query
            avg_similarity = np.mean(max_similarities)
            
            # Apply TF-IDF weighting for content chunks
            if len(similarities) > 1:
                chunk_importance = np.mean(similarities, axis=1)
                weighted_avg = np.average(np.max(similarities, axis=1), weights=chunk_importance)
                final_score = (avg_similarity + weighted_avg) / 2
            else:
                final_score = avg_similarity
            
            # Convert to 0-100 scale
            return min(100, max(0, final_score * 100))
            
        except Exception as e:
            logger.error(f"Error calculating embedding relevance: {e}")
            return 0.0
    
    def _calculate_semantic_density(self, content: str, chunks: List[str]) -> float:
        """
        Calculate semantic density using topic clustering and entity analysis
        """
        try:
            if not chunks:
                return 0.0
            
            # Generate embeddings for chunks
            chunk_embeddings = self._generate_embeddings(chunks)
            
            if chunk_embeddings.size == 0:
                return 0.0
            
            # Perform clustering to identify topic clusters
            if len(chunks) >= 3 and SKLEARN_AVAILABLE:
                n_clusters = min(5, len(chunks) // 2)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(chunk_embeddings)
                
                # Calculate silhouette score for cluster quality
                if len(set(cluster_labels)) > 1:
                    silhouette_avg = silhouette_score(chunk_embeddings, cluster_labels)
                    cluster_quality = max(0, silhouette_avg)
                else:
                    cluster_quality = 0.5
            else:
                cluster_quality = 0.5
            
            # Entity density analysis using spaCy (if available)
            entity_density = 0.0
            if self.nlp:
                doc = self.nlp(content[:1000000])  # Limit for processing
                entities = [ent.label_ for ent in doc.ents]
                unique_entity_types = len(set(entities))
                entity_density = min(1.0, unique_entity_types / 20)  # Normalize to 0-1
            
            # Topic coherence using TF-IDF
            if self.tfidf_vectorizer:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(chunks)
                feature_names = self.tfidf_vectorizer.get_feature_names_out()
                
                # Calculate term diversity
                term_scores = np.mean(tfidf_matrix.toarray(), axis=0)
                top_terms = np.argsort(term_scores)[-20:]  # Top 20 terms
                term_diversity = len(set(feature_names[top_terms])) / 20
            else:
                term_diversity = 0.5  # Default value
            
            # Combine metrics
            final_score = (
                cluster_quality * 0.4 +
                entity_density * 0.3 +
                term_diversity * 0.3
            ) * 100
            
            return min(100, max(0, final_score))
            
        except Exception as e:
            logger.error(f"Error calculating semantic density: {e}")
            return 50.0
    
    def _calculate_authority_score(self, content: str, content_embeddings: np.ndarray) -> Tuple[float, List[AuthoritySignal]]:
        """
        Calculate authority score using multiple signals
        """
        authority_signals = []
        score_components = []
        
        try:
            # 1. Linguistic complexity indicators
            complexity_score = self._analyze_linguistic_complexity(content)
            authority_signals.append(AuthoritySignal(
                signal_type="linguistic_complexity",
                confidence=0.7,
                description=f"Linguistic complexity analysis",
                impact_score=complexity_score
            ))
            score_components.append(complexity_score * 0.25)
            
            # 2. Citation and reference patterns
            citation_score = self._analyze_citation_patterns(content)
            authority_signals.append(AuthoritySignal(
                signal_type="citation_patterns",
                confidence=0.8,
                description="Citation and reference analysis",
                impact_score=citation_score
            ))
            score_components.append(citation_score * 0.30)
            
            # 3. Technical terminology frequency
            technical_score = self._analyze_technical_terminology(content)
            authority_signals.append(AuthoritySignal(
                signal_type="technical_terminology",
                confidence=0.6,
                description="Technical vocabulary analysis",
                impact_score=technical_score
            ))
            score_components.append(technical_score * 0.20)
            
            # 4. Authority embedding similarity
            if self.authority_embeddings and content_embeddings.size > 0:
                authority_sim_score = self._compare_to_authority_embeddings(content_embeddings)
                authority_signals.append(AuthoritySignal(
                    signal_type="authority_similarity",
                    confidence=0.75,
                    description="Similarity to authoritative content patterns",
                    impact_score=authority_sim_score
                ))
                score_components.append(authority_sim_score * 0.25)
            
            # Calculate final score
            final_score = sum(score_components) if score_components else 50.0
            return min(100, max(0, final_score)), authority_signals
            
        except Exception as e:
            logger.error(f"Error calculating authority score: {e}")
            return 50.0, []
    
    def _analyze_linguistic_complexity(self, content: str) -> float:
        """Analyze linguistic complexity indicators"""
        try:
            # Flesch-Kincaid Grade Level
            fk_grade = textstat.flesch_kincaid().flesch_kincaid(content)
            
            # Average sentence length
            sentences = sent_tokenize(content)
            if sentences:
                avg_sentence_length = sum(len(word_tokenize(s)) for s in sentences) / len(sentences)
            else:
                avg_sentence_length = 0
            
            # Vocabulary richness (Type-Token Ratio)
            words = word_tokenize(content.lower())
            if words:
                ttr = len(set(words)) / len(words)
            else:
                ttr = 0
            
            # Normalize and combine scores
            fk_normalized = min(1.0, fk_grade / 15)  # Grade 15+ is quite complex
            length_normalized = min(1.0, avg_sentence_length / 25)  # 25+ words is complex
            ttr_normalized = min(1.0, ttr * 2)  # TTR of 0.5+ indicates good vocabulary
            
            return (fk_normalized + length_normalized + ttr_normalized) / 3 * 100
            
        except Exception as e:
            logger.error(f"Error in linguistic complexity analysis: {e}")
            return 50.0
    
    def _analyze_citation_patterns(self, content: str) -> float:
        """Analyze citation and reference patterns"""
        try:
            # Look for citation patterns
            citation_patterns = [
                r'\([^)]*\d{4}[^)]*\)',  # (Author, 2023)
                r'\[\d+\]',              # [1]
                r'doi:\s*10\.\d+',       # DOI references
                r'https?://[^\s]+',      # URLs
                r'et al\.',              # Et al.
                r'\b(according to|research shows|studies indicate)\b'  # Authority phrases
            ]
            
            citation_count = 0
            for pattern in citation_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                citation_count += len(matches)
            
            # Normalize by content length
            words = len(word_tokenize(content))
            if words > 0:
                citation_density = (citation_count / words) * 1000  # Per 1000 words
                return min(100, citation_density * 20)  # Scale to 0-100
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in citation analysis: {e}")
            return 0.0
    
    def _analyze_technical_terminology(self, content: str) -> float:
        """Analyze technical terminology frequency"""
        try:
            # Technical terminology patterns
            technical_patterns = [
                r'\b\w+ology\b',         # -ology terms
                r'\b\w+ism\b',           # -ism terms  
                r'\b\w+tion\b',          # -tion terms
                r'\b(analysis|methodology|framework|paradigm|hypothesis)\b',
                r'\b(statistical|empirical|quantitative|qualitative)\b',
                r'\b(correlation|regression|coefficient|variance)\b'
            ]
            
            technical_count = 0
            for pattern in technical_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                technical_count += len(matches)
            
            # Normalize by content length
            words = len(word_tokenize(content))
            if words > 0:
                technical_density = (technical_count / words) * 100
                return min(100, technical_density * 10)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in technical terminology analysis: {e}")
            return 0.0
    
    def _compare_to_authority_embeddings(self, content_embeddings: np.ndarray) -> float:
        """Compare content embeddings to authority patterns"""
        try:
            if not self.authority_embeddings:
                return 50.0
            
            authority_embs = np.array(list(self.authority_embeddings.values()))
            
            # Calculate similarities to each authority pattern
            similarities = []
            for content_emb in content_embeddings:
                content_emb = content_emb.reshape(1, -1)
                sims = cosine_similarity(content_emb, authority_embs)
                similarities.append(np.max(sims))
            
            # Return average similarity * 100
            avg_similarity = np.mean(similarities) if similarities else 0
            return min(100, max(0, avg_similarity * 100))
            
        except Exception as e:
            logger.error(f"Error comparing to authority embeddings: {e}")
            return 50.0
    
    def _analyze_chunks(self, chunks: List[str], content_embeddings: np.ndarray,
                       query_embeddings: np.ndarray, queries: List[str]) -> List[ChunkAnalysis]:
        """Analyze each chunk individually"""
        chunk_analyses = []
        
        try:
            for i, chunk in enumerate(chunks):
                if i >= len(content_embeddings):
                    break
                
                chunk_emb = content_embeddings[i].reshape(1, -1)
                
                # Calculate relevance to each query
                relevance_scores = {}
                if query_embeddings.size > 0:
                    similarities = cosine_similarity(chunk_emb, query_embeddings)
                    for j, query in enumerate(queries):
                        relevance_scores[query] = float(similarities[0][j])
                
                # Calculate chunk-level semantic density
                chunk_density = self._calculate_chunk_semantic_density(chunk)
                
                # Authority indicators for this chunk
                auth_indicators = {
                    'technical_terms': self._count_technical_terms(chunk),
                    'complexity_score': textstat.flesch_kincaid().flesch_kincaid(chunk),
                    'citation_count': len(re.findall(r'\([^)]*\d{4}[^)]*\)', chunk))
                }
                
                # Generate improvements using AI
                improvements = self._generate_chunk_improvements(chunk, queries)
                
                chunk_analyses.append(ChunkAnalysis(
                    chunk_id=i,
                    text=chunk,
                    summary=self._summarize_chunk(chunk),
                    embedding=content_embeddings[i].tolist(),
                    relevance_scores=relevance_scores,
                    semantic_density=chunk_density,
                    authority_indicators=auth_indicators,
                    suggested_improvements=improvements
                ))
                
        except Exception as e:
            logger.error(f"Error analyzing chunks: {e}")
        
        return chunk_analyses
    
    def _calculate_chunk_semantic_density(self, chunk: str) -> float:
        """Calculate semantic density for a single chunk"""
        try:
            words = word_tokenize(chunk.lower())
            if not words:
                return 0.0
            
            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            filtered_words = [w for w in words if w not in stop_words and w.isalpha()]
            
            if not filtered_words:
                return 0.0
            
            # Calculate lexical diversity
            unique_words = len(set(filtered_words))
            total_words = len(filtered_words)
            lexical_diversity = unique_words / total_words
            
            # Entity density (if spaCy available)
            entity_score = 0.0
            if self.nlp:
                doc = self.nlp(chunk)
                entities = len(doc.ents)
                entity_score = min(1.0, entities / 10)  # Normalize
            
            return (lexical_diversity * 0.7 + entity_score * 0.3) * 100
            
        except Exception as e:
            logger.error(f"Error calculating chunk semantic density: {e}")
            return 50.0
    
    def _count_technical_terms(self, text: str) -> int:
        """Count technical terms in text"""
        technical_patterns = [
            r'\b\w+ology\b', r'\b\w+ism\b', r'\b\w+tion\b',
            r'\b(analysis|methodology|framework)\b'
        ]
        
        count = 0
        for pattern in technical_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count
    
    def _summarize_chunk(self, chunk: str) -> str:
        """Generate a brief summary of the chunk"""
        # Simple extractive summary - take first sentence or first 100 chars
        sentences = sent_tokenize(chunk)
        if sentences:
            return sentences[0][:100] + "..." if len(sentences[0]) > 100 else sentences[0]
        return chunk[:100] + "..." if len(chunk) > 100 else chunk
    
    def _generate_chunk_improvements(self, chunk: str, queries: List[str]) -> List[str]:
        """Generate improvement suggestions for a chunk"""
        try:
            # Use Gemini for contextual suggestions
            query_text = ", ".join(queries)
            prompt = f"""
            Analyze this content chunk and provide 2-3 specific, actionable improvements 
            to better align with target queries: {query_text}
            
            Chunk: {chunk[:500]}
            
            Focus on:
            1. Missing relevant keywords or concepts
            2. Opportunities to add semantic depth
            3. Ways to improve authority signals
            
            Provide only the improvements as a simple list.
            """
            
            response = self.gemini_model.generate_content(prompt)
            if response and response.text:
                # Parse improvements from response
                improvements = []
                lines = response.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and len(line) > 10:
                        # Clean up formatting
                        line = re.sub(r'^\d+\.?\s*', '', line)  # Remove numbering
                        line = re.sub(r'^-\s*', '', line)       # Remove dashes
                        improvements.append(line)
                
                return improvements[:3]  # Limit to 3 suggestions
            
        except Exception as e:
            logger.warning(f"Could not generate chunk improvements: {e}")
        
        # Fallback suggestions
        return [
            "Consider adding more specific examples or case studies",
            "Include relevant technical terminology for the topic",
            "Add supporting evidence or authoritative references"
        ]
    
    def _identify_semantic_gaps(self, content: str, queries: List[str],
                               content_embeddings: np.ndarray, query_embeddings: np.ndarray) -> List[SemanticGap]:
        """Identify semantic gaps using embedding analysis"""
        gaps = []
        
        try:
            if content_embeddings.size == 0 or query_embeddings.size == 0:
                return gaps
            
            # Calculate query coverage
            similarities = cosine_similarity(content_embeddings, query_embeddings)
            
            for i, query in enumerate(queries):
                max_sim = np.max(similarities[:, i])
                avg_sim = np.mean(similarities[:, i])
                
                # Identify different types of gaps
                if max_sim < 0.3:  # Very low similarity
                    gaps.append(SemanticGap(
                        gap_type="missing_topic",
                        description=f"Content lacks coverage of: {query}",
                        affected_queries=[query],
                        severity=1.0 - max_sim,
                        recommendations=[
                            f"Add dedicated section covering {query}",
                            f"Include specific examples related to {query}",
                            f"Define key terms related to {query}"
                        ]
                    ))
                elif avg_sim < 0.5:  # Inconsistent coverage
                    gaps.append(SemanticGap(
                        gap_type="weak_coverage",
                        description=f"Inconsistent coverage of: {query}",
                        affected_queries=[query],
                        severity=0.5 - avg_sim,
                        recommendations=[
                            f"Strengthen existing mentions of {query}",
                            f"Add more context around {query}",
                            f"Connect {query} to main topic more clearly"
                        ]
                    ))
            
            # Look for semantic disconnects between high-similarity pairs
            query_query_sim = cosine_similarity(query_embeddings, query_embeddings)
            for i in range(len(queries)):
                for j in range(i+1, len(queries)):
                    if query_query_sim[i][j] > 0.7:  # Queries are similar
                        content_sim_diff = abs(
                            np.mean(similarities[:, i]) - np.mean(similarities[:, j])
                        )
                        if content_sim_diff > 0.3:  # But content treats them differently
                            gaps.append(SemanticGap(
                                gap_type="semantic_disconnect",
                                description=f"Disconnect between related concepts: {queries[i]} and {queries[j]}",
                                affected_queries=[queries[i], queries[j]],
                                severity=content_sim_diff,
                                recommendations=[
                                    f"Better integrate discussion of {queries[i]} and {queries[j]}",
                                    "Explain the relationship between these concepts",
                                    "Use consistent terminology across related topics"
                                ]
                            ))
            
        except Exception as e:
            logger.error(f"Error identifying semantic gaps: {e}")
        
        return gaps
    
    def _create_similarity_matrix(self, content_embeddings: np.ndarray, 
                                 query_embeddings: np.ndarray) -> List[List[float]]:
        """Create similarity matrix for visualization"""
        try:
            if content_embeddings.size == 0 or query_embeddings.size == 0:
                return []
            
            similarities = cosine_similarity(content_embeddings, query_embeddings)
            return similarities.tolist()
            
        except Exception as e:
            logger.error(f"Error creating similarity matrix: {e}")
            return []
    
    def _perform_topic_clustering(self, chunks: List[str], embeddings: np.ndarray) -> Dict[str, Any]:
        """Perform topic clustering and return cluster information"""
        try:
            if len(chunks) < 2 or embeddings.size == 0:
                return {"clusters": [], "n_clusters": 0}
            
            # Use HDBSCAN for better cluster identification
            clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
            cluster_labels = clusterer.fit_predict(embeddings)
            
            # Organize clusters
            clusters = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                if label >= 0:  # -1 is noise in HDBSCAN
                    clusters[f"cluster_{label}"].append({
                        "chunk_id": i,
                        "text": chunks[i][:100] + "..." if len(chunks[i]) > 100 else chunks[i]
                    })
            
            return {
                "clusters": dict(clusters),
                "n_clusters": len(clusters),
                "cluster_labels": cluster_labels.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error in topic clustering: {e}")
            return {"clusters": [], "n_clusters": 0}
    
    def _create_semantic_map_data(self, content_embeddings: np.ndarray, query_embeddings: np.ndarray,
                                 chunks: List[str], queries: List[str]) -> Dict[str, Any]:
        """Create data for semantic similarity visualization"""
        try:
            if content_embeddings.size == 0:
                return {}
            
            # Combine all embeddings for dimensionality reduction
            all_embeddings = np.vstack([content_embeddings, query_embeddings])
            all_labels = [f"Chunk {i}" for i in range(len(chunks))] + [f"Query: {q}" for q in queries]
            
            # Use UMAP for 2D projection
            if len(all_embeddings) >= 2:
                reducer = umap.UMAP(n_components=2, random_state=42)
                reduced_embeddings = reducer.fit_transform(all_embeddings)
                
                return {
                    "points": [{
                        "x": float(reduced_embeddings[i][0]),
                        "y": float(reduced_embeddings[i][1]),
                        "label": all_labels[i],
                        "type": "chunk" if i < len(chunks) else "query"
                    } for i in range(len(all_embeddings))],
                    "similarities": cosine_similarity(content_embeddings, query_embeddings).tolist()
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error creating semantic map data: {e}")
            return {}
    
    def _generate_advanced_recommendations(self, embedding_score: float, density_score: float,
                                         authority_score: float, semantic_gaps: List[SemanticGap],
                                         chunk_analysis: List[ChunkAnalysis]) -> List[str]:
        """Generate comprehensive recommendations based on analysis"""
        recommendations = []
        
        try:
            # Score-based recommendations
            if embedding_score < 70:
                recommendations.append(
                    f"Improve semantic alignment with target queries (current score: {embedding_score:.1f}/100)"
                )
                
            if density_score < 60:
                recommendations.append(
                    f"Increase content semantic density by adding more relevant topics and entities (current score: {density_score:.1f}/100)"
                )
                
            if authority_score < 70:
                recommendations.append(
                    f"Strengthen authority signals through citations, technical terminology, and expertise indicators (current score: {authority_score:.1f}/100)"
                )
            
            # Gap-based recommendations
            high_severity_gaps = [gap for gap in semantic_gaps if gap.severity > 0.7]
            for gap in high_severity_gaps[:3]:  # Top 3 gaps
                recommendations.extend(gap.recommendations[:2])  # Top 2 recommendations per gap
            
            # Chunk-specific recommendations
            low_performing_chunks = [chunk for chunk in chunk_analysis 
                                   if max(chunk.relevance_scores.values(), default=0) < 0.5]
            if low_performing_chunks:
                recommendations.append(
                    f"Revise {len(low_performing_chunks)} content sections with low query relevance"
                )
            
            # General recommendations
            if len(recommendations) == 0:
                recommendations.extend([
                    "Content shows good semantic alignment with target queries",
                    "Consider adding more specific examples to strengthen authority",
                    "Monitor performance and update content based on query evolution"
                ])
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations = ["Analysis completed with limited recommendation generation"]
        
        return recommendations[:8]  # Limit to 8 recommendations 