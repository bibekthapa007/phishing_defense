from flask import Flask, request, jsonify, render_template

from predict import predict
from features_extraction import extractFeature

app = Flask(__name__)


@app.route('/')
def index():
    return "Phishing defense api"


@app.route('/-/@/r/r/r/')
def phishing():
    return render_template('phishing.html')


@app.route('/check', methods=['POST'])
def check():
    if request.method == 'POST':
        data = request.get_json()
        url = data['url']
        html = data['html']

        if url is None or html is None:
            return jsonify({'error': 'Missing url or html parameter'}), 400

        print("Checking url:", url)

        isSafe = predict(url, html)

        print("isSafe", isSafe)

        return jsonify({"url": url, "isSafe": isSafe}), 200
    else:
        return jsonify({'error': 'Invalid request method'}), 400


if __name__ == '__main__':
    app.run(debug=True)

# Test link that works
# http://127.0.0.1:5000/-/@/r/r/r/?a=b--b-//ramshyamharitigerinepalnepalnepalnepalnepal
# https://steep-fairies-phishing-https-http-test-test-test.surge.sh/

# Test Link not working
# https://confirm.95urbehxy2dh.top/eb430691fe30d16070b5a144c3d3303c/4e732ced3463d06de0ca9a15b6153677/
