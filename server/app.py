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

        isSafe = 1
        try:
            isSafe = predict(url, html)
        except Exception as e:
            print(e)
            return jsonify({"url": url, "isError": 1, "error": type(e).__name__}), 200

        print("isSafe", isSafe)

        return jsonify({"url": url, "isSafe": isSafe}), 200
    else:
        return jsonify({'error': 'Invalid request method'}), 400


if __name__ == '__main__':
    app.run(debug=True)

# Test link that works
# http://127.0.0.1:5000/-/@/r/r/r/?a=b--b-//ramshyamharitigerinepalnepalnepalnepalnepal
# https://steep-fairies-phishing-https-http-test-test-test.surge.sh/

# From the phishing task data that are categorized as phishing.
# https://rewardarium.com/?z=5904237&p=5904254&ipp=5904249&var=zd_5944655&ar=1&ymid=680876102878769605&source=18885836&ret={var_4}
# https://melbet-np.com/en?tag=d_2009167m_59741c_%5B%5DMS%5B%5Dnull%5B%5Dnull%5B%5Dgeneral%5B%5D1506747-3039366168-0_d87056_l91182_clickunder
# https://secur.52-31-115-142.cprapid.com/login.html
# https://onlineatacadaocupom.com/loginjsf.php?27309=2612b016dfcee6730a3106c47f61e68b&amp;amp;27309
# https://atacadaoresgateagoracred.com/loginjsf.php?18390=f9c2241916e0819565191ba8c95c96ac&amp
# http://bit.ly/areaCliente24
# https://dofus-mmorpg.fr/fr/mmorpg/actualites/news/cave-leviathan/
# https://lwa.uloadeeksurvey.space/finance-survey.html?utm_content=zd_public_v2
# https://www.bitmart.com/en-US?jumpcodebm=1

# Test Link not working
# https://confirm.95urbehxy2dh.top/eb430691fe30d16070b5a144c3d3303c/4e732ced3463d06de0ca9a15b6153677/
