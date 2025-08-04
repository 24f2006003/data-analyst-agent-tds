from flask import Flask, request, jsonify
import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

import requests
import json
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import traceback

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

def execute_code(code):
    # Clean the code - remove markdown formatting if present
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    
    code = code.strip()
    
    # Import numpy if needed
    import numpy as np
    
    globals_dict = {
        'requests': requests, 'json': json, 'base64': base64, 'io': io, 'plt': plt,
        'range': range, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list,
        'dict': dict, 'sum': sum, 'max': max, 'min': min, 'sorted': sorted, 'enumerate': enumerate,
        're': __import__('re'), 'BeautifulSoup': None, 'np': np
    }
    
    # Try to import BeautifulSoup if needed
    if 'BeautifulSoup' in code:
        try:
            from bs4 import BeautifulSoup
            globals_dict['BeautifulSoup'] = BeautifulSoup
        except:
            pass
    
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

Write Python code. Available: requests, json, base64, io, plt, re, np (numpy)

For web scraping, use requests + regex or string parsing (no BeautifulSoup). 
For correlations, use: correlation = np.corrcoef(x, y)[0, 1]
For plots:
```
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=72, bbox_inches='tight')
buffer.seek(0)
img = base64.b64encode(buffer.read()).decode()
plt.close()
```

Important: Check if lists are not empty before using them. Handle missing data.
End with: result = [answer1, answer2, ...]

Only Python code:""")
        
        result = execute_code(code)
        
        # If result is an error dict, return it as is for debugging
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 500
        
        # Return the direct result without wrapping
        return result
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)