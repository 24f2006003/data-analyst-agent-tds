from flask import Flask, request, jsonify
import os
import tempfile
import requests
import json
import base64
import io
import traceback
import re
import math

app = Flask(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://aipipe.org/openai/v1')

def call_llm(prompt):
    try:
        response = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1},
            timeout=60
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"# Error calling LLM: {e}\nresult = 'LLM Error'"

def simple_plot_to_base64(x_data, y_data, title="Plot", x_label="X", y_label="Y", regression=False):
    """Create a simple SVG plot and convert to base64"""
    if not x_data or not y_data or len(x_data) != len(y_data):
        return "data:image/svg+xml;base64," + base64.b64encode(b'<svg><text>No data</text></svg>').decode()
    
    # Simple SVG plot
    width, height = 400, 300
    margin = 50
    
    x_min, x_max = min(x_data), max(x_data)
    y_min, y_max = min(y_data), max(y_data)
    
    # Scale data to fit in plot area
    def scale_x(x): return margin + (x - x_min) / (x_max - x_min) * (width - 2*margin) if x_max != x_min else margin
    def scale_y(y): return height - margin - (y - y_min) / (y_max - y_min) * (height - 2*margin) if y_max != y_min else height - margin
    
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<rect width="{width}" height="{height}" fill="white"/>'
    
    # Plot points
    for x, y in zip(x_data, y_data):
        sx, sy = scale_x(x), scale_y(y)
        svg += f'<circle cx="{sx}" cy="{sy}" r="3" fill="blue"/>'
    
    # Regression line if requested
    if regression and len(x_data) > 1:
        # Simple linear regression
        n = len(x_data)
        sum_x = sum(x_data)
        sum_y = sum(y_data)
        sum_xy = sum(x*y for x, y in zip(x_data, y_data))
        sum_x2 = sum(x*x for x in x_data)
        
        slope = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x*sum_x) if (n*sum_x2 - sum_x*sum_x) != 0 else 0
        intercept = (sum_y - slope*sum_x) / n
        
        x1, x2 = x_min, x_max
        y1, y2 = slope*x1 + intercept, slope*x2 + intercept
        
        sx1, sy1 = scale_x(x1), scale_y(y1)
        sx2, sy2 = scale_x(x2), scale_y(y2)
        
        svg += f'<line x1="{sx1}" y1="{sy1}" x2="{sx2}" y2="{sy2}" stroke="red" stroke-dasharray="5,5"/>'
    
    svg += '</svg>'
    
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def execute_code(code):
    # Clean the code
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    
    code = code.strip()
    
    globals_dict = {
        'requests': requests, 'json': json, 'base64': base64, 'io': io, 're': re,
        'range': range, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list,
        'dict': dict, 'sum': sum, 'max': max, 'min': min, 'sorted': sorted, 'enumerate': enumerate,
        'math': math, 'simple_plot_to_base64': simple_plot_to_base64
    }
    
    locals_dict = {}
    
    try:
        exec(code, globals_dict, locals_dict)
        return locals_dict.get('result', 'No result variable found')
    except Exception as e:
        return {"error": f"Code execution failed: {str(e)}", "code": code}

@app.route('/')
def home():
    return jsonify({"message": "Data Analyst Agent", "usage": "POST /api/ with task"})

@app.route('/api/', methods=['POST'])
def analyze():
    try:
        if request.is_json:
            task = request.get_json().get('task', '')
        else:
            if 'file' in request.files:
                task = request.files['file'].read().decode('utf-8')
            else:
                task = request.get_data(as_text=True)
        
        if not task.strip():
            return jsonify({"error": "No task provided"}), 400
        
        code = call_llm(f"""Task: {task}

Write Python code. Available: requests, json, base64, io, re, math, simple_plot_to_base64

For web scraping: use requests + regex/string parsing
For correlation: calculate manually or use math functions
For plots: use simple_plot_to_base64(x_data, y_data, title, x_label, y_label, regression=True/False)

Example plot usage:
x_data = [1, 2, 3, 4, 5]
y_data = [2, 4, 1, 5, 3]
plot_img = simple_plot_to_base64(x_data, y_data, "Scatter Plot", "X", "Y", regression=True)

End with: result = [answer1, answer2, plot_img, ...]

Only Python code:""")
        
        result = execute_code(code)
        
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 500
        
        return result
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)