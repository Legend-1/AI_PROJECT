import logging
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Common English stopwords for simple extractive summarization.
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'but', 'by', 'for',
    'from', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'i', 'in',
    'is', 'it', 'its', 'of', 'on', 'or', 'our', 'ours', 'she', 'that',
    'the', 'their', 'theirs', 'them', 'they', 'this', 'to', 'was', 'we',
    'were', 'will', 'with', 'you', 'your', 'yours'
}


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
        response = requests.get(NEWS_URL, params=params, timeout=20)
        response.raise_for_status()
        return response.json().get('articles', [])
    except Exception as e:
        logging.error(f"News API Error: {e}")
        return None


def sentence_split(text):
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p and p.strip()]


def tokenize(text):
    return re.findall(r"[A-Za-z']+", text.lower())


def generate_nlp_summary(text_content, min_points=3, max_points=4):
    """Simple extractive NLP summarizer based on term-frequency scoring."""
    try:
        sentences = sentence_split(text_content)
        if not sentences:
            return ["No content available to summarize."]

        if len(sentences) <= max_points:
            return [s[:260] for s in sentences]

        words = tokenize(text_content)
        filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
        if not filtered:
            return [s[:260] for s in sentences[:max_points]]

        freq = Counter(filtered)
        max_freq = max(freq.values()) if freq else 1
        for word in list(freq.keys()):
            freq[word] = freq[word] / max_freq

        scored = []
        for idx, sentence in enumerate(sentences):
            sent_words = tokenize(sentence)
            if not sent_words:
                continue

            score = 0.0
            for w in sent_words:
                if w in freq:
                    score += freq[w]

            # Normalize by sentence length to reduce long-sentence bias.
            score = score / max(len(sent_words), 1)
            scored.append((idx, sentence, score))

        if not scored:
            return [s[:260] for s in sentences[:max_points]]

        selected_count = max_points if len(sentences) >= max_points else len(sentences)
        selected_count = max(min_points, selected_count)
        selected_count = min(selected_count, len(scored))

        top = sorted(scored, key=lambda x: x[2], reverse=True)[:selected_count]
        top_in_order = sorted(top, key=lambda x: x[0])

        summary_points = []
        for _, sent, _ in top_in_order:
            cleaned = sent.strip(' -*\t')
            if cleaned:
                summary_points.append(cleaned[:260])

        if not summary_points:
            return ["Could not generate a summary from this article."]

        return summary_points[:max_points]

    except Exception as e:
        logging.error(f"NLP Summary Error: {e}")
        return [f"NLP Summary Error: {str(e)}"]


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
        return render_template('index.html', error='Please enter a topic.')

    articles = fetch_news(topic, date_filter, country_filter)

    if articles is None:
        return render_template('index.html', error='Failed to fetch news.')

    if not articles:
        return render_template('index.html', error='No articles found.')

    return render_template(
        'index.html',
        articles=articles,
        last_topic=topic,
        last_date=date_filter,
        last_country=country_filter,
    )


@app.route('/summarize', methods=['POST'])
def summarize_endpoint():
    data = request.json or {}
    text_content = data.get('text', '')

    if not text_content:
        return jsonify({'error': 'No text provided'}), 400

    summary_points = generate_nlp_summary(text_content)
    return jsonify({'summary': summary_points})


@app.route('/api/search', methods=['GET'])
def api_search():
    """API endpoint for React frontend."""
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
