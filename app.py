import logging
from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION ---
NEWS_API_KEY = '6cf399304bc249118d5d70b43950d33b'
GEMINI_API_KEY = 'AIzaSyBwYG8mNIrR_qMdZkQVzec03NizwpMvR5I'

NEWS_URL = 'https://newsapi.org/v2/everything'

# FIXED: Updated model name from gemini-1.5-flash to gemini-2.0-flash
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

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
    """Summarizes using a direct HTTP request to Gemini."""
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": (
                        "Summarize the following news article into exactly 3 to 4 concise bullet points. "
                        "Do not use asterisks or dashes. Return sentences separated by newlines.\n\n"
                        f"Article: {text_content}"
                    )
                }]
            }]
        }

        headers = {'Content-Type': 'application/json'}

        response = requests.post(GEMINI_URL, json=payload, headers=headers)

        if response.status_code != 200:
            logging.error(f"Gemini Error: {response.text}")
            return [f"Error {response.status_code}: {response.text}"]

        data = response.json()

        try:
            generated_text = data['candidates'][0]['content']['parts'][0]['text']
            summary_points = [line.strip() for line in generated_text.split('\n') if line.strip()]
            return summary_points
        except (KeyError, IndexError):
            return ["AI returned an empty or unexpected response."]

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

    return render_template('index.html', articles=articles,
                           last_topic=topic, last_date=date_filter, last_country=country_filter)

@app.route('/summarize', methods=['POST'])
def summarize_endpoint():
    data = request.json
    text_content = data.get('text')

    if not text_content:
        return jsonify({'error': 'No text provided'}), 400

    summary_points = generate_ai_summary(text_content)

    return jsonify({'summary': summary_points})

if __name__ == '__main__':
    app.run(debug=True)