import sys
import joblib
import warnings
import numpy as np

import features_extraction

MODEL_PATH = './models/random_forest.pkl'


def predict(test_url, html):
    features_test = features_extraction.extractFeature(test_url,html)
    features_test_data = np.array(features_test).reshape((1, -1))

    # TODO: Add .pkl model file inside the models folder and replace model path

    clf = joblib.load(MODEL_PATH)

    pred = clf.predict(features_test_data)
    print("---------------------------------")
    print(test_url)
    print(pred)
    prediction = int(pred[0])
    if prediction == 1:
        print("SAFE")
        return 1
    else:
        print("PHISHING")
        return 0
