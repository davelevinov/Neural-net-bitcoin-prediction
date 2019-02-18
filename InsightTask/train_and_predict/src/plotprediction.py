"""
this is a training project starting 2010-07-17 till 60 days before today.
time steps used are 5 days each to correlate with given data afterwards.
plot graph used to demonstrate the correlation to reality.
The model is saved after training and then loaded using another file to execute as a prediction to 5 given days.
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
# Disables the tensorflow cpu usage warning
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from sklearn.preprocessing import MinMaxScaler

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


trainset_file_path = os.path.join(ROOT_DIR, 'data_without_two_months.csv')
bitcoin_training_complete = pd.read_csv(trainset_file_path)

bitcoin_training_processed = bitcoin_training_complete.iloc[:, 1:2].values

scaler = MinMaxScaler(feature_range = (0, 1))

bitcoin_training_scaled = scaler.fit_transform(bitcoin_training_processed)
features_set = []
labels = []
for i in range(5, 3078):
    features_set.append(bitcoin_training_scaled[i-5:i, 0])
    labels.append(bitcoin_training_scaled[i, 0])

features_set, labels = np.array(features_set), np.array(labels)
features_set = np.reshape(features_set, (features_set.shape[0], features_set.shape[1], 1))

model = Sequential()

model.add(LSTM(units=50, return_sequences=True, input_shape=(features_set.shape[1], 1)))

model.add(Dropout(0.2))

model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))

model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))

model.add(LSTM(units=50))
model.add(Dropout(0.2))

model.add(Dense(units = 1))

model.compile(optimizer = 'adam', loss = 'mean_squared_error')

model.fit(features_set, labels, epochs = 50, batch_size = 32)

# saves model for use by other file
model.save('bitcoin_model.h5')

testset_file_path = os.path.join(ROOT_DIR, 'last_two_months.csv')

bitcoin_testing_complete = pd.read_csv(testset_file_path)
bitcoin_testing_processed = bitcoin_testing_complete.iloc[:, 1:2].values

bitcoin_total = pd.concat((bitcoin_training_complete['USD'], bitcoin_testing_complete['USD']), axis=0)

test_inputs = bitcoin_total[len(bitcoin_total) - len(bitcoin_testing_complete) - 5:].values


# data scaling
test_inputs = test_inputs.reshape(-1, 1)
test_inputs = scaler.transform(test_inputs)

#prepare data points
test_features = []
for i in range(5, 65):
    test_features.append(test_inputs[i-5:i, 0])

# convert to 3d format

test_features = np.array(test_features)
test_features = np.reshape(test_features, (test_features.shape[0], test_features.shape[1], 1))
predictions = model.predict(test_features)
predictions = scaler.inverse_transform(predictions)



plt.figure(figsize=(10,6))
plt.plot(bitcoin_testing_processed, color='blue', label='Actual Bitcoin Price')
plt.plot(predictions , color='red', label='Predicted BitCoin Price')
plt.title('Bitcoin Price Prediction')
plt.xlabel('Date')
plt.ylabel('Bitcoin Price')
plt.legend()
plt.show()