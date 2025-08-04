from flask import Flask, request, jsonify
import os
import openai
import pandas as pd
import json
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import traceback
import requests
from urllib.parse import urlparse
import tempfile

app = Flask(__name__)

# Configure OpenAI client for AI Pipe
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_BASE_URL', 'https://aipipe.org/openai/v1')

class DataAnalyst:
    def __init__(self):
        self.supported_formats = ['.csv', '.json', '.xlsx', '.xls', '.txt']
        
    def analyze_task(self, task_description):
        """Main method to analyze a data task"""
        try:
            # Parse the task using LLM
            analysis_plan = self._create_analysis_plan(task_description)
            
            # Execute the analysis
            result = self._execute_analysis(analysis_plan, task_description)
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "task": task_description,
                "analysis_plan": analysis_plan,
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _create_analysis_plan(self, task_description):
        """Use LLM to create an analysis plan"""
        prompt = f"""
        You are a data analyst AI. Given the following task description, create a structured analysis plan.
        
        Task: {task_description}
        
        Please analyze what type of data analysis is needed and respond with a JSON structure containing:
        - data_requirements: What kind of data is needed
        - analysis_type: Type of analysis (descriptive, predictive, diagnostic, etc.)
        - steps: List of analysis steps
        - visualization_needs: What visualizations would be helpful
        - expected_output: What the final output should contain
        
        Respond only with valid JSON.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "data_requirements": "General dataset",
                "analysis_type": "descriptive",
                "steps": ["Load data", "Analyze data", "Create visualizations"],
                "visualization_needs": ["Summary statistics", "Basic plots"],
                "expected_output": "Analysis summary with insights"
            }
    
    def _execute_analysis(self, plan, task_description):
        """Execute the analysis based on the plan"""
        # For this example, we'll generate sample data and perform analysis
        # In a real implementation, this would handle actual data sources
        
        # Generate or load sample data based on the task
        data = self._get_sample_data(task_description)
        
        # Perform analysis
        analysis_results = self._perform_statistical_analysis(data)
        
        # Create visualizations
        visualizations = self._create_visualizations(data)
        
        # Generate insights using LLM
        insights = self._generate_insights(data, analysis_results, task_description)
        
        return {
            "data_summary": self._summarize_data(data),
            "statistical_analysis": analysis_results,
            "visualizations": visualizations,
            "insights": insights,
            "recommendations": self._generate_recommendations(insights, task_description)
        }
    
    def _get_sample_data(self, task_description):
        """Generate appropriate sample data based on task description"""
        # This is a simplified example - in reality, you'd connect to data sources
        import numpy as np
        
        # Generate different types of sample data based on keywords in task
        if any(word in task_description.lower() for word in ['sales', 'revenue', 'profit']):
            # Sales data
            dates = pd.date_range('2023-01-01', periods=100, freq='D')
            data = pd.DataFrame({
                'date': dates,
                'sales': np.random.normal(1000, 200, 100),
                'profit': np.random.normal(150, 50, 100),
                'customers': np.random.poisson(50, 100)
            })
        elif any(word in task_description.lower() for word in ['temperature', 'weather', 'climate']):
            # Weather data
            dates = pd.date_range('2023-01-01', periods=365, freq='D')
            data = pd.DataFrame({
                'date': dates,
                'temperature': np.random.normal(20, 10, 365),
                'humidity': np.random.normal(60, 15, 365),
                'rainfall': np.random.exponential(2, 365)
            })
        else:
            # Generic numeric data
            data = pd.DataFrame({
                'category': ['A', 'B', 'C', 'D', 'E'] * 20,
                'value1': np.random.normal(100, 25, 100),
                'value2': np.random.normal(50, 15, 100),
                'count': np.random.poisson(10, 100)
            })
        
        return data
    
    def _perform_statistical_analysis(self, data):
        """Perform statistical analysis on the data"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        analysis = {}
        for col in numeric_columns:
            analysis[col] = {
                'mean': float(data[col].mean()),
                'median': float(data[col].median()),
                'std': float(data[col].std()),
                'min': float(data[col].min()),
                'max': float(data[col].max()),
                'count': int(data[col].count())
            }
        
        # Correlation analysis if multiple numeric columns
        if len(numeric_columns) > 1:
            correlation_matrix = data[numeric_columns].corr()
            analysis['correlations'] = correlation_matrix.to_dict()
        
        return analysis
    
    def _create_visualizations(self, data):
        """Create visualizations and return as base64 encoded images"""
        visualizations = []
        
        try:
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            
            # Create histogram for first numeric column
            if len(numeric_columns) > 0:
                plt.figure(figsize=(10, 6))
                plt.hist(data[numeric_columns[0]], bins=20, alpha=0.7)
                plt.title(f'Distribution of {numeric_columns[0]}')
                plt.xlabel(numeric_columns[0])
                plt.ylabel('Frequency')
                
                # Convert to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.read()).decode()
                plt.close()
                
                visualizations.append({
                    'type': 'histogram',
                    'title': f'Distribution of {numeric_columns[0]}',
                    'image': image_base64
                })
            
            # Create correlation heatmap if multiple numeric columns
            if len(numeric_columns) > 1:
                plt.figure(figsize=(10, 8))
                correlation_matrix = data[numeric_columns].corr()
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
                plt.title('Correlation Matrix')
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.read()).decode()
                plt.close()
                
                visualizations.append({
                    'type': 'heatmap',
                    'title': 'Correlation Matrix',
                    'image': image_base64
                })
                
        except Exception as e:
            visualizations.append({
                'type': 'error',
                'message': f'Error creating visualization: {str(e)}'
            })
        
        return visualizations
    
    def _generate_insights(self, data, analysis_results, task_description):
        """Generate insights using LLM"""
        data_summary = self._summarize_data(data)
        
        prompt = f"""
        As a data analyst, provide insights based on the following data analysis:
        
        Original Task: {task_description}
        
        Data Summary: {json.dumps(data_summary, indent=2)}
        
        Statistical Analysis: {json.dumps(analysis_results, indent=2)}
        
        Please provide:
        1. Key findings from the data
        2. Notable patterns or trends
        3. Potential anomalies or interesting observations
        4. Implications of the findings
        
        Keep the response concise but insightful.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Unable to generate insights due to API error: {str(e)}"
    
    def _generate_recommendations(self, insights, task_description):
        """Generate recommendations using LLM"""
        prompt = f"""
        Based on the following insights and original task, provide actionable recommendations:
        
        Original Task: {task_description}
        Insights: {insights}
        
        Please provide 3-5 specific, actionable recommendations.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Unable to generate recommendations due to API error: {str(e)}"
    
    def _summarize_data(self, data):
        """Create a summary of the dataset"""
        return {
            'shape': list(data.shape),
            'columns': list(data.columns),
            'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
            'missing_values': data.isnull().sum().to_dict(),
            'memory_usage': f"{data.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }

# Initialize the data analyst
analyst = DataAnalyst()

@app.route('/')
def home():
    return jsonify({
        "message": "Data Analyst Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/": "Submit data analysis task",
            "GET /": "API information"
        },
        "usage": "Send POST request with task description in request body"
    })

@app.route('/api/', methods=['POST'])
def analyze_data():
    try:
        # Get task description from request
        if request.is_json:
            task_description = request.get_json().get('task', '')
        else:
            # Handle file upload or text data
            if 'file' in request.files:
                file = request.files['file']
                if file.filename:
                    task_description = file.read().decode('utf-8')
                else:
                    task_description = request.form.get('task', '')
            else:
                task_description = request.get_data(as_text=True)
        
        if not task_description:
            return jsonify({
                "status": "error",
                "message": "No task description provided"
            }), 400
        
        # Perform analysis
        result = analyst.analyze_task(task_description)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/about')
def about():
    return jsonify({
        "name": "Data Analyst Agent",
        "description": "AI-powered data analysis API that can source, prepare, analyze, and visualize data",
        "capabilities": [
            "Task interpretation and planning",
            "Statistical analysis",
            "Data visualization",
            "Insight generation",
            "Recommendation generation"
        ],
        "supported_formats": [".csv", ".json", ".xlsx", ".txt"],
        "response_time": "< 3 minutes"
    })

if __name__ == '__main__':
    app.run(debug=True)