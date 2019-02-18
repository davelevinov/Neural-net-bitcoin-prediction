"""
univariate one step problem with lstm, train and predict with output.

This is the solution I believe is less good because of the difficulty to include confidence / correlation.
"""
import os
import numpy
# Disables the tensorflow cpu usage warning
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

from keras.layers import Dense
from keras.layers import LSTM
from keras.models import Sequential
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import model_from_json


trainset_file_path = os.path.join(ROOT_DIR, 'data_without_two_months.csv')
trainset = numpy.loadtxt(trainset_file_path, usecols=(1), delimiter=",", skiprows=1)

# reshape to [x, 1]
n_features = 1
series = trainset.reshape((len(trainset), n_features))
# define generator
n_input = 5
generator = TimeseriesGenerator(series, series, length=n_input, batch_size=1024)
# define model
model = Sequential()
model.add(LSTM(100, activation='relu', input_shape=(n_input, n_features)))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')
# fit model
model.fit_generator(generator, steps_per_epoch=1, epochs=500, verbose=0)

# make sample out of last five days data
sampleset_file_path = os.path.join(ROOT_DIR, '../../python-coindesk-api-master/last_five_days.csv')
sampleset = numpy.loadtxt(sampleset_file_path, usecols=(1), delimiter=",", skiprows=1)
print("current sample set is: ")
print(sampleset)

# make a one step prediction out of sample
x_input = sampleset.reshape((1, n_input, n_features))
yhat = model.predict(x_input, verbose=0)
print("prediction based on sample:")
print(yhat)
