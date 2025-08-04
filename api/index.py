from flask import Flask, request, jsonify
import os
import tempfile

# Fix matplotlib cache directory issue in serverless environments
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

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
import re
from bs4 import BeautifulSoup
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# Configure OpenAI client for AI Pipe
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_BASE_URL', 'https://aipipe.org/openai/v1')

class DataAnalyst:
    def __init__(self):
        pass
        
    def analyze_task(self, task_description):
        """Main method to analyze a data task and return only the requested answer"""
        try:
            # Use LLM to understand the task and generate code
            code = self._generate_analysis_code(task_description)
            
            # Execute the generated code safely
            result = self._execute_code(code)
            
            return result
            
        except Exception as e:
            return {"error": str(e), "traceback": traceback.format_exc()}
    
    def _generate_analysis_code(self, task_description):
        """Generate Python code to solve the analysis task"""
        prompt = f"""
You are a Python data analyst. Generate ONLY executable Python code that directly answers the task.

Available imports:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import base64
import io
from sklearn.linear_model import LinearRegression
import json
import re

Task: {task_description}

Requirements:
1. Write code that directly produces the final answer
2. If the task asks for multiple answers, return them as a JSON array
3. For plots, save as base64 data URI: "data:image/png;base64,..."
4. Keep plots under 100KB by using plt.figure(figsize=(8,6), dpi=72)
5. End with: result = [answer1, answer2, ...]
6. NO explanations, NO print statements, ONLY code

Example for multiple answers:
result = [count, "movie_name", correlation_value, "data:image/png;base64,iVBORw0..."]
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    def _execute_code(self, code):
        """Safely execute the generated code and return result"""
        # Create a safe execution environment
        safe_globals = {
            '__builtins__': __builtins__,
            'pd': pd,
            'np': np,
            'plt': plt,
            'requests': requests,
            'BeautifulSoup': BeautifulSoup,
            'base64': base64,
            'io': io,
            'LinearRegression': LinearRegression,
            'json': json,
            're': re,
            'range': range,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'enumerate': enumerate,
            'zip': zip,
            'max': max,
            'min': min,
            'sum': sum,
            'sorted': sorted,
        }
        
        safe_locals = {}
        
        # Execute the code
        exec(code, safe_globals, safe_locals)
        
        # Return the result
        return safe_locals.get('result', 'No result variable found')
    
# Initialize the data analyst
analyst = DataAnalyst()

@app.route('/')
def home():
    return jsonify({
        "message": "Data Analyst Agent API",
        "version": "2.0.0",
        "endpoints": {
            "POST /api/": "Submit data analysis task",
            "GET /": "API information"
        },
        "usage": "Send POST request with task description. Returns direct answer only."
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
            return jsonify({"error": "No task description provided"}), 400
        
        # Perform analysis and get direct result
        result = analyst.analyze_task(task_description)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/about')
def about():
    return jsonify({
        "name": "Data Analyst Agent",
        "description": "AI-powered data analysis API that returns direct answers only",
        "model": "gpt-3.5-turbo",
        "response_format": "Direct answer only - no metadata or process details"
    })

if __name__ == '__main__':
    app.run(debug=True)