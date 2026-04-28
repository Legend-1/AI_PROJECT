import logging
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
# app.py (add CORS support)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# ... rest of your code remains the same


def load_env_file(env_path):
    """Loads KEY=VALUE pairs from a .env file into process environment."""
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file(Path(__file__).with_name('.env'))

# --- CONFIGURATION ---
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
LOCAL_LLM_URL = os.getenv('LOCAL_LLM_URL', 'http://127.0.0.1:11434')
LOCAL_LLM_MODEL = os.getenv('LOCAL_LLM_MODEL', 'gemma3')
LOCAL_LLM_FALLBACK_MODEL = os.getenv('LOCAL_LLM_FALLBACK_MODEL', 'tinyllama:latest')

NEWS_URL = 'https://newsapi.org/v2/everything'

logging.basicConfig(level=logging.INFO)

# --- HELPER FUNCTIONS ---

def fetch_news(query, from_date=None, country=None):
    params = {
        'q': query,
        'apiKey': NEWS_API_KEY,
        'sortBy': 'publishedAt',
        'language': 'en',
    }
    if from_date:
        params['from'] = from_date
    if country:
        params['q'] += f" AND {country}"

    try:
        response = requests.get(NEWS_URL, params=params)
        response.raise_for_status()
        return response.json().get('articles', [])
    except Exception as e:
        logging.error(f"News API Error: {e}")
        return None

def generate_ai_summary(text_content):
    """Summarizes using a local LLM endpoint (Ollama + Gemma 3)."""
    try:
        prompt = (
            "Summarize the following news article into exactly 3 to 4 concise bullet points. "
            "Do not use asterisks or dashes. Return one point per line.\n\n"
            f"Article: {text_content}"
        )

        headers = {'Content-Type': 'application/json'}

        models_to_try = [LOCAL_LLM_MODEL]
        if LOCAL_LLM_FALLBACK_MODEL and LOCAL_LLM_FALLBACK_MODEL != LOCAL_LLM_MODEL:
            models_to_try.append(LOCAL_LLM_FALLBACK_MODEL)

        response = None
        for model in models_to_try:
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': False,
            }
            response = requests.post(f"{LOCAL_LLM_URL}/api/generate", json=payload, headers=headers, timeout=120)
            if response.status_code == 200:
                break

            error_text = response.text.lower()
            if 'system memory' in error_text and model != models_to_try[-1]:
                logging.warning("Model %s could not load due to memory. Trying fallback model.", model)
                continue
            break

        if response.status_code != 200:
            logging.error(f"Local LLM Error: {response.text}")
            return [f"Error {response.status_code}: {response.text}"]

        data = response.json()

        try:
            generated_text = data.get('response', '')
            summary_points = []
            for raw_line in generated_text.split('\n'):
                cleaned = raw_line.strip(' -*\t')
                if not cleaned:
                    continue
                lowered = cleaned.lower()
                if (
                    lowered.startswith('here is')
                    or lowered.startswith("here's")
                    or lowered.startswith('summary:')
                    or ('summary' in lowered and ':' in lowered)
                ):
                    continue
                summary_points.append(cleaned)
            if not summary_points:
                return ["Local model returned an empty summary."]
            if len(summary_points) > 4:
                summary_points = summary_points[:4]
            return summary_points
        except (KeyError, IndexError):
            return ["Local AI returned an empty or unexpected response."]

    except Exception as e:
        logging.error(f"Summary Connection Error: {e}")
        return [f"Connection Error: {str(e)}"]

# --- ROUTES ---

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', today=today)

@app.route('/search', methods=['POST'])
def search():
    topic = request.form.get('topic')
    date_filter = request.form.get('date')
    country_filter = request.form.get('country')

    if not topic:
        return render_template('index.html', error="Please enter a topic.")

    articles = fetch_news(topic, date_filter, country_filter)

    if articles is None:
        return render_template('index.html', error="Failed to fetch news.")

    if not articles:
        return render_template('index.html', error="No articles found.")

    return render_template('index.html', articles=articles, last_topic=topic, last_date=date_filter, last_country=country_filter)

@app.route('/summarize', methods=['POST'])
def summarize_endpoint():
    data = request.json
    text_content = data.get('text')

    if not text_content:
        return jsonify({'error': 'No text provided'}), 400

    summary_points = generate_ai_summary(text_content)

    return jsonify({'summary': summary_points})

# Add this to your app.py

@app.route('/api/search', methods=['GET'])
def api_search():
    """API endpoint for React frontend"""
    topic = request.args.get('topic')
    date_filter = request.args.get('date')
    country_filter = request.args.get('country')

    if not topic:
        return jsonify({'error': 'Please enter a topic'}), 400

    articles = fetch_news(topic, date_filter, country_filter)

    if articles is None:
        return jsonify({'error': 'Failed to fetch news'}), 500

    if not articles:
        return jsonify({'error': 'No articles found'}), 404

    return jsonify({'articles': articles})

if __name__ == '__main__':
    app.run(debug=True)
