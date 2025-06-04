import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def create_metrics_chart(embedding_score: float, density_score: float, authority_score: float):
    """
    Create a comprehensive metrics visualization chart
    
    Args:
        embedding_score: Embedding relevance score (0-100)
        density_score: Semantic density score (0-100)
        authority_score: Authority score (0-100)
        
    Returns:
        Plotly figure object
    """
    
    # Create subplots: 1 row, 2 columns (bar chart + radial gauge)
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Metric Scores", "Overall Performance"),
        specs=[[{"type": "bar"}, {"type": "indicator"}]],
        column_widths=[0.6, 0.4]
    )
    
    # Data for bar chart
    metrics = ['Embedding Relevance', 'Semantic Density', 'Authority Score']
    scores = [embedding_score, density_score, authority_score]
    colors = ['#ff8c42', '#8b9dc3', '#313856']
    
    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=metrics,
            y=scores,
            marker_color=colors,
            text=[f'{score:.0f}%' for score in scores],
            textposition='auto',
            name='Scores'
        ),
        row=1, col=1
    )
    
    # Calculate overall score (weighted average)
    overall_score = (embedding_score * 0.4 + density_score * 0.3 + authority_score * 0.3)
    
    # Add gauge chart for overall score
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=overall_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Score"},
            delta={'reference': 75, 'increasing': {'color': "#ff8c42"}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#ff8c42"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "#8b9dc3"},
                    {'range': [80, 100], 'color': "#313856"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': "Content Optimization Metrics",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'white'}
        },
        showlegend=False,
        height=400,
        paper_bgcolor='rgba(30, 41, 59, 0.8)',
        plot_bgcolor='rgba(30, 41, 59, 0.8)',
        font={'color': 'white'}
    )
    
    # Update bar chart axes
    fig.update_xaxes(
        title_text="Metrics",
        title_font_color='white',
        tickfont_color='white',
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Score (%)",
        title_font_color='white',
        tickfont_color='white',
        range=[0, 100],
        row=1, col=1
    )
    
    return fig

def create_score_comparison_chart(scores_history: list):
    """
    Create a line chart showing score trends over time
    
    Args:
        scores_history: List of score dictionaries with timestamps
        
    Returns:
        Plotly figure object
    """
    if not scores_history:
        return None
    
    fig = go.Figure()
    
    # Extract data
    timestamps = [entry['timestamp'] for entry in scores_history]
    embedding_scores = [entry['embedding_relevance_score'] for entry in scores_history]
    density_scores = [entry['semantic_density_score'] for entry in scores_history]
    authority_scores = [entry['authority_score'] for entry in scores_history]
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=embedding_scores,
        mode='lines+markers',
        name='Embedding Relevance',
        line=dict(color='#ff8c42', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=density_scores,
        mode='lines+markers',
        name='Semantic Density',
        line=dict(color='#8b9dc3', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=authority_scores,
        mode='lines+markers',
        name='Authority Score',
        line=dict(color='#313856', width=3),
        marker=dict(size=8)
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': "Score Trends Over Time",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': 'white'}
        },
        xaxis_title="Time",
        yaxis_title="Score (%)",
        paper_bgcolor='rgba(30, 41, 59, 0.8)',
        plot_bgcolor='rgba(30, 41, 59, 0.8)',
        font={'color': 'white'},
        legend=dict(
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='white',
            borderwidth=1
        )
    )
    
    fig.update_xaxes(
        title_font_color='white',
        tickfont_color='white',
        gridcolor='rgba(255, 255, 255, 0.2)'
    )
    fig.update_yaxes(
        title_font_color='white',
        tickfont_color='white',
        gridcolor='rgba(255, 255, 255, 0.2)',
        range=[0, 100]
    )
    
    return fig 