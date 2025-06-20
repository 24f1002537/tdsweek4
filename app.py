from flask import Flask, request, Response
import urllib.parse
import httpx
from bs4 import BeautifulSoup
import flask_cors

app = Flask(__name__)
flask_cors.CORS(app)

def construct_wikipedia_url(country_name: str) -> str:
    encoded_country = urllib.parse.quote(country_name.replace(' ', '_'))
    url = f"https://en.wikipedia.org/wiki/{encoded_country}"
    return url

def fetch_html(url: str) -> str:
    response = httpx.get(url)
    return response.text if response.status_code == 200 else None

def extract_headings(html_content: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    headings_data = [(heading.name, heading.get_text(strip=True)) for heading in headings]
    return headings_data

def headings_to_markdown(headings_data):
    markdown_lines = ['## Contents']
    for tag, text in headings_data:
        level = int(tag[1])  # 'h2' -> 2
        markdown_line = f"{'#' * level} {text}"
        markdown_lines.append(markdown_line)
    return '\n'.join(markdown_lines)

@app.route('/api/outline')
def get_outline():
    country = request.args.get('country')
    if not country:
        return Response('Missing country parameter', status=400)
    url = construct_wikipedia_url(country)
    html_content = fetch_html(url)
    if not html_content:
        return Response('Page not found or error fetching content.', status=404)
    headings_data = extract_headings(html_content)
    markdown_text = headings_to_markdown(headings_data)
    return Response(markdown_text, mimetype='text/plain')

# To run the app locally, add:
if __name__ == '__main__':
     app.run()
