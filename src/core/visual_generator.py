"""
Visual Flashcard Generator Module
Converts structured content into visual learning materials
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import graphviz
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import base64
import io
from dataclasses import dataclass
import json

@dataclass
class VisualCard:
    """Data structure for visual flashcard content"""
    title: str
    content_type: str  # 'diagram', 'table', 'mindmap', 'chart'
    data: Dict[str, Any]
    image_base64: str
    metadata: Dict[str, Any]

class VisualFlashcardGenerator:
    """Advanced visual content generator for educational materials"""
    
    def __init__(self):
        self.style_config = {
            'colors': {
                'primary': '#2563eb',
                'secondary': '#7c3aed',
                'accent': '#059669',
                'warning': '#d97706',
                'error': '#dc2626',
                'background': '#f8fafc',
                'text': '#1e293b'
            },
            'fonts': {
                'title': {'size': 16, 'weight': 'bold'},
                'body': {'size': 12, 'weight': 'normal'},
                'caption': {'size': 10, 'weight': 'normal'}
            }
        }
    
    def generate_process_diagram(self, steps: List[str], title: str = "Process Flow") -> VisualCard:
        """Generate a process flow diagram"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, len(steps) + 1)
        
        # Draw process steps
        for i, step in enumerate(steps):
            y_pos = len(steps) - i
            
            # Draw rectangle for step
            rect = FancyBboxPatch(
                (1, y_pos - 0.3), 8, 0.6,
                boxstyle="round,pad=0.1",
                facecolor=self.style_config['colors']['primary'],
                edgecolor='white',
                linewidth=2
            )
            ax.add_patch(rect)
            
            # Add step text
            ax.text(5, y_pos, f"{i+1}. {step}", 
                   ha='center', va='center', 
                   color='white', fontsize=12, fontweight='bold')
            
            # Draw arrow to next step
            if i < len(steps) - 1:
                ax.arrow(5, y_pos - 0.4, 0, -0.3, 
                        head_width=0.2, head_length=0.1, 
                        fc=self.style_config['colors']['accent'], 
                        ec=self.style_config['colors']['accent'])
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return VisualCard(
            title=title,
            content_type='diagram',
            data={'steps': steps},
            image_base64=img_base64,
            metadata={'step_count': len(steps), 'diagram_type': 'process'}
        )
    
    def generate_comparison_table(self, data: Dict[str, List[str]], title: str = "Comparison") -> VisualCard:
        """Generate a visual comparison table"""
        df = pd.DataFrame(data)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create table
        table = ax.table(cellText=df.values, colLabels=df.columns,
                        cellLoc='center', loc='center',
                        colWidths=[0.3] * len(df.columns))
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2)
        
        # Header styling
        for i in range(len(df.columns)):
            table[(0, i)].set_facecolor(self.style_config['colors']['primary'])
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternate row colors
        for i in range(1, len(df) + 1):
            for j in range(len(df.columns)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#f1f5f9')
                else:
                    table[(i, j)].set_facecolor('white')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return VisualCard(
            title=title,
            content_type='table',
            data=data,
            image_base64=img_base64,
            metadata={'rows': len(df), 'columns': len(df.columns)}
        )
    
    def generate_mindmap(self, central_topic: str, branches: Dict[str, List[str]], 
                        title: str = "Concept Map") -> VisualCard:
        """Generate an interactive mindmap"""
        G = nx.Graph()
        
        # Add central node
        G.add_node(central_topic, node_type='central')
        
        # Add branch nodes and connections
        for branch, sub_items in branches.items():
            G.add_node(branch, node_type='branch')
            G.add_edge(central_topic, branch)
            
            for item in sub_items:
                G.add_node(item, node_type='leaf')
                G.add_edge(branch, item)
        
        # Create layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Draw nodes with different colors based on type
        node_colors = []
        node_sizes = []
        for node in G.nodes():
            node_type = G.nodes[node].get('node_type', 'leaf')
            if node_type == 'central':
                node_colors.append(self.style_config['colors']['primary'])
                node_sizes.append(3000)
            elif node_type == 'branch':
                node_colors.append(self.style_config['colors']['secondary'])
                node_sizes.append(2000)
            else:
                node_colors.append(self.style_config['colors']['accent'])
                node_sizes.append(1000)
        
        # Draw the graph
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                              width=2, alpha=0.6, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, 
                               font_weight='bold', ax=ax)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return VisualCard(
            title=title,
            content_type='mindmap',
            data={'central_topic': central_topic, 'branches': branches},
            image_base64=img_base64,
            metadata={'total_nodes': len(G.nodes()), 'total_edges': len(G.edges())}
        )
    
    def generate_interactive_chart(self, data: Dict[str, Any], chart_type: str = 'bar') -> str:
        """Generate interactive Plotly charts"""
        if chart_type == 'bar':
            fig = px.bar(
                x=list(data.keys()), 
                y=list(data.values()),
                title="Data Visualization",
                color_discrete_sequence=[self.style_config['colors']['primary']]
            )
        elif chart_type == 'pie':
            fig = px.pie(
                values=list(data.values()), 
                names=list(data.keys()),
                title="Distribution Chart"
            )
        elif chart_type == 'line':
            fig = px.line(
                x=list(data.keys()), 
                y=list(data.values()),
                title="Trend Analysis"
            )
        
        fig.update_layout(
            font=dict(size=12),
            title_font_size=16,
            showlegend=True
        )
        
        return fig.to_html(include_plotlyjs='cdn')

class ContentAnalyzer:
    """Analyzes content to determine optimal visual representation"""
    
    def __init__(self):
        self.visual_generator = VisualFlashcardGenerator()
    
    def analyze_and_generate(self, content: str, content_type: str = None) -> List[VisualCard]:
        """Analyze content and generate appropriate visuals"""
        visuals = []
        
        # Detect content patterns
        if self._contains_process_steps(content):
            steps = self._extract_process_steps(content)
            visual = self.visual_generator.generate_process_diagram(steps)
            visuals.append(visual)
        
        if self._contains_comparison_data(content):
            comparison_data = self._extract_comparison_data(content)
            visual = self.visual_generator.generate_comparison_table(comparison_data)
            visuals.append(visual)
        
        if self._contains_hierarchical_info(content):
            central_topic, branches = self._extract_hierarchical_info(content)
            visual = self.visual_generator.generate_mindmap(central_topic, branches)
            visuals.append(visual)
        
        return visuals
    
    def _contains_process_steps(self, content: str) -> bool:
        """Check if content contains process steps"""
        step_indicators = ['step', 'first', 'second', 'then', 'next', 'finally', 'process']
        return any(indicator in content.lower() for indicator in step_indicators)
    
    def _extract_process_steps(self, content: str) -> List[str]:
        """Extract process steps from content"""
        # Simplified extraction - in production, use NLP
        lines = content.split('\n')
        steps = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                        'step' in line.lower()):
                steps.append(line)
        return steps[:6]  # Limit to 6 steps for visual clarity
    
    def _contains_comparison_data(self, content: str) -> bool:
        """Check if content contains comparison data"""
        comparison_indicators = ['vs', 'versus', 'compared to', 'difference', 'similarity']
        return any(indicator in content.lower() for indicator in comparison_indicators)
    
    def _extract_comparison_data(self, content: str) -> Dict[str, List[str]]:
        """Extract comparison data from content"""
        # Simplified extraction - in production, use advanced NLP
        return {
            'Feature': ['Feature 1', 'Feature 2', 'Feature 3'],
            'Option A': ['Value A1', 'Value A2', 'Value A3'],
            'Option B': ['Value B1', 'Value B2', 'Value B3']
        }
    
    def _contains_hierarchical_info(self, content: str) -> bool:
        """Check if content contains hierarchical information"""
        hierarchy_indicators = ['category', 'type', 'classification', 'branch', 'subtopic']
        return any(indicator in content.lower() for indicator in hierarchy_indicators)
    
    def _extract_hierarchical_info(self, content: str) -> tuple:
        """Extract hierarchical information from content"""
        # Simplified extraction - in production, use advanced NLP
        central_topic = "Main Topic"
        branches = {
            'Branch 1': ['Sub-item 1', 'Sub-item 2'],
            'Branch 2': ['Sub-item 3', 'Sub-item 4'],
            'Branch 3': ['Sub-item 5', 'Sub-item 6']
        }
        return central_topic, branches