import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any
import pandas as pd

def create_similarity_heatmap(similarity_matrix: List[List[float]], 
                            chunks: List[str], queries: List[str]) -> go.Figure:
    """
    Create a heatmap showing similarity between content chunks and queries
    """
    if not similarity_matrix or not chunks or not queries:
        return go.Figure().add_annotation(
            text="No similarity data available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=16
        )
    
    # Truncate labels for better display
    chunk_labels = [f"Chunk {i+1}: {chunk[:50]}..." if len(chunk) > 50 
                   else f"Chunk {i+1}: {chunk}" for i, chunk in enumerate(chunks)]
    query_labels = [f"Query: {query[:30]}..." if len(query) > 30 
                   else f"Query: {query}" for query in queries]
    
    fig = go.Figure(data=go.Heatmap(
        z=similarity_matrix,
        x=query_labels,
        y=chunk_labels,
        colorscale='RdYlBu_r',
        hoverongaps=False,
        colorbar=dict(title="Similarity Score")
    ))
    
    fig.update_layout(
        title="Content-Query Similarity Matrix",
        xaxis_title="Target Queries",
        yaxis_title="Content Chunks",
        height=max(400, len(chunks) * 50),
        paper_bgcolor='rgba(30, 41, 59, 0.8)',
        plot_bgcolor='rgba(30, 41, 59, 0.8)',
        font={'color': 'white'},
        title_font={'color': 'white', 'size': 18}
    )
    
    return fig

def create_semantic_map(semantic_map_data: Dict[str, Any]) -> go.Figure:
    """
    Create a 2D semantic similarity map using UMAP projections
    """
    if not semantic_map_data or 'points' not in semantic_map_data:
        return go.Figure().add_annotation(
            text="No semantic map data available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=16
        )
    
    points = semantic_map_data['points']
    
    # Separate chunks and queries
    chunk_points = [p for p in points if p['type'] == 'chunk']
    query_points = [p for p in points if p['type'] == 'query']
    
    fig = go.Figure()
    
    # Add content chunks
    if chunk_points:
        fig.add_trace(go.Scatter(
            x=[p['x'] for p in chunk_points],
            y=[p['y'] for p in chunk_points],
            mode='markers',
            marker=dict(
                size=12,
                color='#ff8c42',
                opacity=0.8,
                line=dict(width=2, color='white')
            ),
            text=[p['label'] for p in chunk_points],
            hovertemplate='<b>%{text}</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>',
            name='Content Chunks'
        ))
    
    # Add queries
    if query_points:
        fig.add_trace(go.Scatter(
            x=[p['x'] for p in query_points],
            y=[p['y'] for p in query_points],
            mode='markers',
            marker=dict(
                size=16,
                color='#8b9dc3',
                symbol='diamond',
                opacity=0.9,
                line=dict(width=2, color='white')
            ),
            text=[p['label'] for p in query_points],
            hovertemplate='<b>%{text}</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>',
            name='Target Queries'
        ))
    
    fig.update_layout(
        title="Semantic Similarity Map (2D Projection)",
        xaxis_title="UMAP Dimension 1",
        yaxis_title="UMAP Dimension 2",
        height=500,
        paper_bgcolor='rgba(30, 41, 59, 0.8)',
        plot_bgcolor='rgba(30, 41, 59, 0.8)',
        font={'color': 'white'},
        title_font={'color': 'white', 'size': 18},
        showlegend=True,
        legend=dict(
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='white',
            borderwidth=1
        )
    )
    
    return fig

def create_topic_cluster_chart(topic_clusters: Dict[str, Any]) -> go.Figure:
    """
    Create visualization for topic clusters
    """
    if not topic_clusters or 'clusters' not in topic_clusters:
        return go.Figure().add_annotation(
            text="No topic clustering data available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=16
        )
    
    clusters = topic_clusters['clusters']
    
    if not clusters:
        return go.Figure().add_annotation(
            text="No distinct topic clusters found",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=16
        )
    
    # Create sunburst chart for topic clusters
    labels = []
    parents = []
    values = []
    colors = []
    
    # Color palette for clusters
    cluster_colors = ['#ff8c42', '#8b9dc3', '#313856', '#2c5f2d', '#97bc62', '#d4a574']
    
    # Root
    labels.append("Content Topics")
    parents.append("")
    values.append(sum(len(chunks) for chunks in clusters.values()))
    colors.append('#2c3e50')
    
    # Clusters
    for i, (cluster_name, chunks) in enumerate(clusters.items()):
        cluster_label = f"Topic {i+1}"
        labels.append(cluster_label)
        parents.append("Content Topics")
        values.append(len(chunks))
        colors.append(cluster_colors[i % len(cluster_colors)])
        
        # Individual chunks (limit to top 3 per cluster for readability)
        for j, chunk in enumerate(chunks[:3]):
            chunk_text = chunk['text'][:50] + "..." if len(chunk['text']) > 50 else chunk['text']
            labels.append(f"Chunk {chunk['chunk_id']}")
            parents.append(cluster_label)
            values.append(1)
            colors.append(cluster_colors[i % len(cluster_colors)])
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colors=colors),
        hovertemplate='<b>%{label}</b><br>Chunks: %{value}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"Topic Clusters ({len(clusters)} clusters found)",
        height=500,
        paper_bgcolor='rgba(30, 41, 59, 0.8)',
        font={'color': 'white'},
        title_font={'color': 'white', 'size': 18}
    )
    
    return fig

def create_authority_signals_chart(authority_signals: List[Dict[str, Any]]) -> go.Figure:
    """
    Create radar chart for authority signals
    """
    if not authority_signals:
        return go.Figure().add_annotation(
            text="No authority signals data available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=16
        )
    
    # Prepare data for radar chart
    signal_types = [signal['signal_type'].replace('_', ' ').title() for signal in authority_signals]
    impact_scores = [signal['impact_score'] for signal in authority_signals]
    confidence_scores = [signal['confidence'] * 100 for signal in authority_signals]  # Convert to percentage
    
    fig = go.Figure()
    
    # Impact scores
    fig.add_trace(go.Scatterpolar(
        r=impact_scores,
        theta=signal_types,
        fill='toself',
        name='Impact Score',
        marker_color='#ff8c42',
        opacity=0.7
    ))
    
    # Confidence scores
    fig.add_trace(go.Scatterpolar(
        r=confidence_scores,
        theta=signal_types,
        fill='toself',
        name='Confidence %',
        marker_color='#8b9dc3',
        opacity=0.5
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont_color='white'
            ),
            angularaxis=dict(
                tickfont_color='white'
            )
        ),
        title="Authority Signals Analysis",
        height=500,
        paper_bgcolor='rgba(30, 41, 59, 0.8)',
        font={'color': 'white'},
        title_font={'color': 'white', 'size': 18},
        showlegend=True,
        legend=dict(
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='white',
            borderwidth=1
        )
    )
    
    return fig

def create_semantic_gaps_chart(semantic_gaps: List[Dict[str, Any]]) -> go.Figure:
    """
    Create visualization for semantic gaps
    """
    if not semantic_gaps:
        return go.Figure().add_annotation(
            text="No semantic gaps identified - content appears well-aligned!",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font_size=16, font_color='green'
        )
    
    # Prepare data
    gap_types = [gap['gap_type'].replace('_', ' ').title() for gap in semantic_gaps]
    severities = [gap['severity'] * 100 for gap in semantic_gaps]  # Convert to percentage
    descriptions = [gap['description'] for gap in semantic_gaps]
    
    # Color mapping for gap types
    color_map = {
        'Missing Topic': '#ff4444',
        'Weak Coverage': '#ffaa44', 
        'Semantic Disconnect': '#ff8844'
    }
    colors = [color_map.get(gap_type, '#ff8c42') for gap_type in gap_types]
    
    fig = go.Figure(data=[
        go.Bar(
            x=gap_types,
            y=severities,
            marker_color=colors,
            text=[f"{sev:.1f}%" for sev in severities],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Severity: %{y:.1f}%<br>%{customdata}<extra></extra>',
            customdata=descriptions
        )
    ])
    
    fig.update_layout(
        title="Identified Semantic Gaps",
        xaxis_title="Gap Type",
        yaxis_title="Severity (%)",
        height=400,
        paper_bgcolor='rgba(30, 41, 59, 0.8)',
        plot_bgcolor='rgba(30, 41, 59, 0.8)',
        font={'color': 'white'},
        title_font={'color': 'white', 'size': 18},
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def create_processing_metrics_chart(processing_time: float, 
                                  n_chunks: int, 
                                  n_queries: int,
                                  embedding_score: float,
                                  density_score: float,
                                  authority_score: float) -> go.Figure:
    """
    Create summary metrics chart with processing information
    """
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Processing Metrics", "Content Analysis", "Score Distribution", "Performance Summary"),
        specs=[[{"type": "indicator"}, {"type": "bar"}],
               [{"type": "pie"}, {"type": "table"}]]
    )
    
    # Processing time indicator
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=processing_time,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Processing Time (s)"},
            gauge={
                'axis': {'range': [None, 10]},
                'bar': {'color': "#ff8c42"},
                'steps': [
                    {'range': [0, 2], 'color': "lightgray"},
                    {'range': [2, 5], 'color': "#8b9dc3"},
                    {'range': [5, 10], 'color': "#313856"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 8
                }
            }
        ),
        row=1, col=1
    )
    
    # Content analysis bar chart
    fig.add_trace(
        go.Bar(
            x=["Chunks", "Queries"],
            y=[n_chunks, n_queries],
            marker_color=['#ff8c42', '#8b9dc3'],
            text=[str(n_chunks), str(n_queries)],
            textposition='auto'
        ),
        row=1, col=2
    )
    
    # Score distribution pie chart
    scores = [embedding_score, density_score, authority_score]
    labels = ['Embedding Relevance', 'Semantic Density', 'Authority Score']
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=scores,
            marker_colors=['#ff8c42', '#8b9dc3', '#313856']
        ),
        row=2, col=1
    )
    
    # Performance summary table
    fig.add_trace(
        go.Table(
            header=dict(values=['Metric', 'Value'], fill_color='#2c3e50'),
            cells=dict(values=[
                ['Processing Time', 'Content Chunks', 'Target Queries', 'Avg Score'],
                [f"{processing_time:.2f}s", str(n_chunks), str(n_queries), f"{np.mean(scores):.1f}"]
            ], fill_color='#34495e')
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        paper_bgcolor='rgba(30, 41, 59, 0.8)',
        font={'color': 'white'},
        title_text="Advanced Analysis Summary",
        title_font={'color': 'white', 'size': 20},
        showlegend=False
    )
    
    return fig 