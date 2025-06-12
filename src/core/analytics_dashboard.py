"""
Real-time Analytics Dashboard
Provides comprehensive learning analytics and insights
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import json

@dataclass
class LearningMetrics:
    total_cards_generated: int
    total_cards_reviewed: int
    average_accuracy: float
    study_streak: int
    total_study_time: int  # minutes
    weak_areas: List[str]
    strong_areas: List[str]
    improvement_rate: float

@dataclass
class SessionAnalytics:
    session_id: str
    date: datetime
    duration: int  # minutes
    cards_reviewed: int
    accuracy: float
    mode: str
    topics_covered: List[str]
    difficulty_distribution: Dict[str, int]

class LearningAnalytics:
    """Comprehensive learning analytics engine"""
    
    def __init__(self):
        self.user_data = defaultdict(list)
        self.session_data = defaultdict(list)
        self.topic_performance = defaultdict(lambda: defaultdict(list))
    
    def record_session(self, user_id: str, session_data: Dict[str, Any]):
        """Record a completed study session"""
        session_analytics = SessionAnalytics(
            session_id=session_data['session_id'],
            date=datetime.fromisoformat(session_data['date']),
            duration=session_data['duration'],
            cards_reviewed=session_data['cards_reviewed'],
            accuracy=session_data['accuracy'],
            mode=session_data['mode'],
            topics_covered=session_data['topics_covered'],
            difficulty_distribution=session_data['difficulty_distribution']
        )
        
        self.session_data[user_id].append(session_analytics)
        
        # Update topic performance
        for topic in session_data['topics_covered']:
            self.topic_performance[user_id][topic].append({
                'date': session_analytics.date,
                'accuracy': session_data.get('topic_accuracies', {}).get(topic, session_analytics.accuracy),
                'cards_count': session_data.get('topic_card_counts', {}).get(topic, 1)
            })
    
    def generate_user_metrics(self, user_id: str) -> LearningMetrics:
        """Generate comprehensive metrics for a user"""
        sessions = self.session_data[user_id]
        
        if not sessions:
            return LearningMetrics(0, 0, 0.0, 0, 0, [], [], 0.0)
        
        # Calculate basic metrics
        total_cards_reviewed = sum(s.cards_reviewed for s in sessions)
        total_study_time = sum(s.duration for s in sessions)
        average_accuracy = np.mean([s.accuracy for s in sessions])
        
        # Calculate study streak
        study_streak = self._calculate_study_streak(sessions)
        
        # Identify weak and strong areas
        weak_areas, strong_areas = self._identify_performance_areas(user_id)
        
        # Calculate improvement rate
        improvement_rate = self._calculate_improvement_rate(sessions)
        
        return LearningMetrics(
            total_cards_generated=total_cards_reviewed,  # Simplified
            total_cards_reviewed=total_cards_reviewed,
            average_accuracy=average_accuracy,
            study_streak=study_streak,
            total_study_time=total_study_time,
            weak_areas=weak_areas,
            strong_areas=strong_areas,
            improvement_rate=improvement_rate
        )
    
    def _calculate_study_streak(self, sessions: List[SessionAnalytics]) -> int:
        """Calculate current study streak in days"""
        if not sessions:
            return 0
        
        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda x: x.date, reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        for session in sorted_sessions:
            session_date = session.date.date()
            
            if session_date == current_date or session_date == current_date - timedelta(days=streak):
                if session_date == current_date - timedelta(days=streak):
                    streak += 1
                current_date = session_date
            else:
                break
        
        return streak
    
    def _identify_performance_areas(self, user_id: str) -> Tuple[List[str], List[str]]:
        """Identify weak and strong performance areas"""
        topic_performance = self.topic_performance[user_id]
        
        topic_averages = {}
        for topic, performances in topic_performance.items():
            if performances:
                avg_accuracy = np.mean([p['accuracy'] for p in performances])
                topic_averages[topic] = avg_accuracy
        
        if not topic_averages:
            return [], []
        
        overall_average = np.mean(list(topic_averages.values()))
        
        weak_areas = [topic for topic, avg in topic_averages.items() 
                     if avg < overall_average - 0.1]
        strong_areas = [topic for topic, avg in topic_averages.items() 
                       if avg > overall_average + 0.1]
        
        return weak_areas[:5], strong_areas[:5]  # Limit to top 5
    
    def _calculate_improvement_rate(self, sessions: List[SessionAnalytics]) -> float:
        """Calculate improvement rate over time"""
        if len(sessions) < 2:
            return 0.0
        
        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda x: x.date)
        
        # Calculate trend using simple linear regression
        x = np.arange(len(sorted_sessions))
        y = np.array([s.accuracy for s in sorted_sessions])
        
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            return float(slope * 100)  # Convert to percentage
        
        return 0.0

class VisualizationEngine:
    """Creates interactive visualizations for learning analytics"""
    
    def __init__(self):
        self.color_palette = {
            'primary': '#2563eb',
            'secondary': '#7c3aed', 
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'info': '#06b6d4'
        }
    
    def create_performance_overview(self, metrics: LearningMetrics) -> str:
        """Create performance overview dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Study Progress', 'Accuracy Trend', 'Time Distribution', 'Topic Performance'),
            specs=[[{"type": "indicator"}, {"type": "scatter"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Study progress indicator
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=metrics.average_accuracy * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Accuracy (%)"},
                delta={'reference': 80},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self.color_palette['primary']},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=1
        )
        
        # Mock accuracy trend (in production, use real historical data)
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        accuracy_trend = np.random.normal(metrics.average_accuracy, 0.1, 30)
        accuracy_trend = np.clip(accuracy_trend, 0, 1)
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=accuracy_trend * 100,
                mode='lines+markers',
                name='Accuracy Trend',
                line=dict(color=self.color_palette['success'])
            ),
            row=1, col=2
        )
        
        # Time distribution pie chart
        time_distribution = {
            'Study Time': metrics.total_study_time,
            'Break Time': metrics.total_study_time * 0.2,
            'Review Time': metrics.total_study_time * 0.3
        }
        
        fig.add_trace(
            go.Pie(
                labels=list(time_distribution.keys()),
                values=list(time_distribution.values()),
                hole=0.3
            ),
            row=2, col=1
        )
        
        # Topic performance bar chart
        all_areas = metrics.weak_areas + metrics.strong_areas
        if all_areas:
            # Mock performance scores
            performance_scores = [60 + np.random.randint(-20, 40) for _ in all_areas]
            colors = ['red' if area in metrics.weak_areas else 'green' for area in all_areas]
            
            fig.add_trace(
                go.Bar(
                    x=all_areas,
                    y=performance_scores,
                    marker_color=colors,
                    name='Topic Performance'
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Learning Analytics Dashboard",
            title_x=0.5
        )
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_study_heatmap(self, user_id: str, sessions: List[SessionAnalytics]) -> str:
        """Create study activity heatmap"""
        if not sessions:
            return "<p>No study data available</p>"
        
        # Create date range for last 90 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=89)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create activity matrix
        activity_data = defaultdict(int)
        for session in sessions:
            session_date = session.date.date()
            if start_date <= session_date <= end_date:
                activity_data[session_date] += session.duration
        
        # Prepare data for heatmap
        weeks = []
        days = []
        values = []
        
        for date in date_range:
            week = date.isocalendar()[1]
            day = date.weekday()
            value = activity_data.get(date.date(), 0)
            
            weeks.append(week)
            days.append(day)
            values.append(value)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            x=weeks,
            y=days,
            z=values,
            colorscale='Greens',
            hoverongaps=False,
            hovertemplate='Week: %{x}<br>Day: %{y}<br>Study Time: %{z} min<extra></extra>'
        ))
        
        fig.update_layout(
            title='Study Activity Heatmap (Last 90 Days)',
            xaxis_title='Week of Year',
            yaxis_title='Day of Week',
            yaxis=dict(
                tickmode='array',
                tickvals=[0, 1, 2, 3, 4, 5, 6],
                ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_progress_timeline(self, sessions: List[SessionAnalytics]) -> str:
        """Create progress timeline visualization"""
        if not sessions:
            return "<p>No session data available</p>"
        
        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda x: x.date)
        
        dates = [s.date for s in sorted_sessions]
        accuracies = [s.accuracy * 100 for s in sorted_sessions]
        study_times = [s.duration for s in sorted_sessions]
        
        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add accuracy line
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=accuracies,
                mode='lines+markers',
                name='Accuracy (%)',
                line=dict(color=self.color_palette['primary'], width=3),
                marker=dict(size=8)
            ),
            secondary_y=False,
        )
        
        # Add study time bars
        fig.add_trace(
            go.Bar(
                x=dates,
                y=study_times,
                name='Study Time (min)',
                opacity=0.6,
                marker_color=self.color_palette['secondary']
            ),
            secondary_y=True,
        )
        
        # Update axes
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Accuracy (%)", secondary_y=False)
        fig.update_yaxes(title_text="Study Time (minutes)", secondary_y=True)
        
        fig.update_layout(
            title='Learning Progress Timeline',
            hovermode='x unified'
        )
        
        return fig.to_html(include_plotlyjs='cdn')

class SmartReviewScheduler:
    """Intelligent scheduling system for optimal review timing"""
    
    def __init__(self):
        self.spaced_repetition_intervals = [1, 3, 7, 14, 30, 90]  # days
    
    def calculate_next_review(self, card_id: str, performance_history: List[Dict[str, Any]]) -> datetime:
        """Calculate optimal next review time using spaced repetition"""
        if not performance_history:
            return datetime.now() + timedelta(days=1)
        
        # Get latest performance
        latest_performance = performance_history[-1]
        accuracy = latest_performance.get('accuracy', 0.5)
        
        # Determine interval based on performance
        if accuracy >= 0.9:
            interval_index = min(len(self.spaced_repetition_intervals) - 1, 
                               latest_performance.get('interval_index', 0) + 1)
        elif accuracy >= 0.7:
            interval_index = latest_performance.get('interval_index', 0)
        else:
            interval_index = max(0, latest_performance.get('interval_index', 0) - 1)
        
        interval_days = self.spaced_repetition_intervals[interval_index]
        
        # Add some randomization to avoid clustering
        randomization = np.random.randint(-1, 2)  # -1, 0, or 1 day
        final_interval = max(1, interval_days + randomization)
        
        return datetime.now() + timedelta(days=final_interval)
    
    def get_cards_due_for_review(self, user_id: str, all_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get cards that are due for review"""
        due_cards = []
        current_time = datetime.now()
        
        for card in all_cards:
            next_review = card.get('next_review')
            if next_review:
                next_review_time = datetime.fromisoformat(next_review)
                if next_review_time <= current_time:
                    due_cards.append(card)
            else:
                # New card, add to review
                due_cards.append(card)
        
        return due_cards
    
    def suggest_optimal_study_time(self, user_id: str, historical_performance: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest optimal study time based on user patterns"""
        if not historical_performance:
            return {
                'recommended_time': '09:00',
                'recommended_duration': 30,
                'confidence': 0.5,
                'reasoning': 'Default recommendation for new users'
            }
        
        # Analyze performance by time of day
        time_performance = defaultdict(list)
        for session in historical_performance:
            hour = datetime.fromisoformat(session['date']).hour
            time_performance[hour].append(session['accuracy'])
        
        # Find best performing time
        best_hour = 9  # default
        best_accuracy = 0
        
        for hour, accuracies in time_performance.items():
            avg_accuracy = np.mean(accuracies)
            if avg_accuracy > best_accuracy:
                best_accuracy = avg_accuracy
                best_hour = hour
        
        # Recommend duration based on historical patterns
        durations = [session['duration'] for session in historical_performance]
        recommended_duration = int(np.median(durations)) if durations else 30
        
        return {
            'recommended_time': f"{best_hour:02d}:00",
            'recommended_duration': recommended_duration,
            'confidence': min(0.9, len(historical_performance) / 10),
            'reasoning': f'Based on {len(historical_performance)} previous sessions'
        }