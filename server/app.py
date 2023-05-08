from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return "Phishing defense api"


@app.route('/check', methods=['POST'])
def check():
    if request.method == 'POST':
        # if 'url' not in request.form or 'html' not in request.form:
        #     return jsonify({'error': 'Missing form data'}), 400

        data = request.get_json()
        url = data['url']
        html = data['html']

        if url is None or html is None:
            return jsonify({'error': 'Missing url or html parameter'}), 400

        # TODO: extract the features
        # TODO: get result from ai model
        print(html, url)

        return jsonify({"url": url, "check": "true"}), 200
    else:
        return jsonify({'error': 'Invalid request method'}), 400


if __name__ == '__main__':
    app.run(debug=True)
