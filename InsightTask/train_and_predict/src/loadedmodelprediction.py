"""
This takes the last five days CSV extracted by the script in coindesk_api and applies it to the
model trained at plotprediction
"""
import os
import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
# Disables the tensorflow cpu usage warning
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

""""
testset_file_path = os.path.join(ROOT_DIR, '../../python-coindesk-api-master/last_five_days.csv')
testset_complete = pd.read_csv(testset_file_path)
testset_processed = testset_complete.iloc[:, 1:2].values
print(testset_processed)

features_set = []
labels = []
features_set.append(testset_processed[0-5:, 0])
labels.append(testset_processed[0, 0])
"""
scaler = MinMaxScaler(feature_range = (0, 1))

trainset_file_path = os.path.join(ROOT_DIR, '../../python-coindesk-api-master/last_five_days.csv')

trainset = pd.read_csv(trainset_file_path)
trainset_processed = trainset.iloc[:, 1:2].values

# data scaling for model
test_inputs = trainset_processed.reshape(-1, 1)
print(test_inputs)
test_inputs = scaler.fit_transform(test_inputs)

test_features = []
for i in range(5, 6):
    test_features.append(test_inputs[i-5:i, 0])

# convert to 3d format

test_features = np.array(test_features)
test_features = np.reshape(test_features, (test_features.shape[0], test_features.shape[1], 1))

model = load_model('bitcoin_model.h5')


yhat = model.predict(test_features, verbose=0)
yhat = scaler.inverse_transform(yhat)
print("prediction based on sample:")
print(yhat)
