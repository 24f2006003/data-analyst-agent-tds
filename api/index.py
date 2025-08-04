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
    response = requests.post(
        f"{OPENAI_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
    )
    return response.json()["choices"][0]["message"]["content"]

def execute_code(code):
    globals_dict = {
        'requests': requests, 'json': json, 'base64': base64, 'io': io, 'plt': plt,
        'range': range, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list,
        'dict': dict, 'sum': sum, 'max': max, 'min': min, 'sorted': sorted, 'enumerate': enumerate
    }
    locals_dict = {}
    exec(code, globals_dict, locals_dict)
    return locals_dict.get('result', 'No result')

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
        
        code = call_llm(f"""Generate Python code to solve: {task}

Available: requests, json, base64, io, plt (matplotlib.pyplot)

For plots: 
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=72, bbox_inches='tight')
buffer.seek(0)
img = base64.b64encode(buffer.read()).decode()
plt.close()

End with: result = your_answer
Single answer: result = 42
Multiple: result = [1, "name", 0.85, "data:image/png;base64,"+img]

Code only:""")
        
        result = execute_code(code)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)