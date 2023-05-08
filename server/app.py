from flask import Flask, request, jsonify

from features_extraction import extractFeature

app = Flask(__name__)


@app.route('/')
def index():
    return "Phishing defense api"


@app.route('/check', methods=['POST'])
def check():
    if request.method == 'POST':
        data = request.get_json()
        url = data['url']
        html = data['html']

        if url is None or html is None:
            return jsonify({'error': 'Missing url or html parameter'}), 400

        features = extractFeature(url, html)

        # TODO: get result from ai model
        print(html, url)

        return jsonify({"url": url, "check": "true"}), 200
    else:
        return jsonify({'error': 'Invalid request method'}), 400


if __name__ == '__main__':
    app.run(debug=True)
