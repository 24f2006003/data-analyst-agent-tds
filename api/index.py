import os
import json
import math
import re
import io
import base64
import matplotlib.pyplot as plt
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/openai/gpt-oss-20b"

app = Flask(__name__)

def call_llm(prompt):
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": f"### Instruction:\n{prompt}\n\n### Response:",
        "parameters": {"max_new_tokens": 400, "temperature": 0.1}
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data[0]["generated_text"]
    else:
        return f"result = {{'error': 'HF API Error: {response.text}'}}"

def simple_plot_to_base64(x, y, title="Plot", x_label="X", y_label="Y", regression=False):
    fig, ax = plt.subplots()
    ax.scatter(x, y, color="blue")
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if regression and len(x) > 1:
        n = len(x)
        sum_x, sum_y = sum(x), sum(y)
        sum_xy = sum(a * b for a, b in zip(x, y))
        sum_x2 = sum(a * a for a in x)
        denom = n * sum_x2 - sum_x ** 2
        slope = (n * sum_xy - sum_x * sum_y) / denom if denom else 0
        intercept = (sum_y - slope * sum_x) / n
        x_vals = [min(x), max(x)]
        y_vals = [slope * xi + intercept for xi in x_vals]
        ax.plot(x_vals, y_vals, color="red", linestyle="--")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    return "data:image/png;base64," + img_base64

def execute_code(code):
    if "```" in code:
        code = code.split("```")[1]
    code = code.strip()

    globs = {
        'json': json, 're': re, 'math': math,
        'range': range, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list,
        'dict': dict, 'sum': sum, 'max': max, 'min': min, 'sorted': sorted, 'enumerate': enumerate,
        'simple_plot_to_base64': simple_plot_to_base64
    }

    try:
        exec(code, globs)
        return jsonify(globs.get('result', {"error": "No result variable found"}))
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/')
def home():
    return jsonify({"message": "Data Analyst Agent", "usage": "POST /api/ with task"})

@app.route('/api/', methods=['POST'])
def analyze():
    try:
        task = ''
        if request.is_json:
            task = request.get_json().get('task', '')
        elif 'file' in request.files:
            task = request.files['file'].read().decode('utf-8')
        else:
            task = request.get_data(as_text=True)

        if not task.strip():
            return jsonify({"error": "No task provided"})

        prompt = f"""Task: {task}

Write Python code. Use: json, re, math, simple_plot_to_base64

Check for regex match exists before .group(), handle missing data.

Correlation:
def correlation(x, y):
    n = len(x)
    if n < 2: return 0
    sum_x, sum_y = sum(x), sum(y)
    sum_xy = sum(a*b for a,b in zip(x,y))
    sum_x2 = sum(a*a for a in x)
    sum_y2 = sum(b*b for b in y)
    num = n*sum_xy - sum_x*sum_y
    den = ((n*sum_x2 - sum_x**2)*(n*sum_y2 - sum_y**2))**0.5
    return num/den if den else 0

Plots: simple_plot_to_base64(x, y, 'Title', 'X', 'Y', regression=True)

End with: result = [answer1, answer2, plot_base64]"""

        code = call_llm(prompt)
        return execute_code(code)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
