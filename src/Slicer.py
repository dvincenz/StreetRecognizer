from keras.models import Sequential
from keras.layers import Dense
import numpy
# fix random seed for reproducibility
numpy.random.seed(10)

import pandas as pd

data_set_url = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv'
HEADER = [
    # from https://github.com/jbrownlee/Datasets/blob/master/pima-indians-diabetes.names
    'Number of times pregnant',
    'Glucosse level',
    'blood pressure',
    'skin fold thickness',
    'insulin',
    'BMI',
    'Diabetes pedigree function',
    'Age',
    'Class variable',
]
df = pd.read_csv(data_set_url, names=HEADER)
df.tail()

# result to be explained ("Output variable")
out_variable = df['Class variable']

# explaining variables ("Input variable")
input_matrix = df.loc[:, 'Number of times pregnant':'Age']
# .values = numpy array

input_matrix.head()

out_variable.head()

# normalize explaining variables

input_matrix_normalized = input_matrix.div(df.sum(axis=1), axis=0)
input_matrix_normalized.head()

# use numpy array for statistically use variables X (input) and Y (output)
X = input_matrix_normalized.values
Y = out_variable.values

# create model
model = Sequential()
model.add(Dense(12, input_dim=8, activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
# Compile model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Fit the model
# model.fit(X, Y, epochs=150, batch_size=1000, callbacks=[tensor_board_callback])
# use verbose=0 to suppress output
# model.fit(X, Y, epochs=150, batch_size=1000, callbacks=[tensor_board_callback], verbose=0)
model.fit(X, Y, epochs=10, batch_size=100)

# evaluate the model
scores = model.evaluate(X, Y)
print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))