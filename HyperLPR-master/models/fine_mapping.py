# models/fine_mapping.py

from keras.models import Model
from keras.layers import Input, Conv2D, Activation, MaxPool2D, Flatten, Dense

def build_finemapping_model():
    input = Input(shape=[16, 66, 3])
    x = Conv2D(10, (3, 3), strides=1, padding='valid')(input)
    x = Activation("relu")(x)
    x = MaxPool2D(pool_size=2)(x)
    x = Conv2D(16, (3, 3), strides=1, padding='valid')(x)
    x = Activation("relu")(x)
    x = Conv2D(32, (3, 3), strides=1, padding='valid')(x)
    x = Activation("relu")(x)
    x = Flatten()(x)
    x = Dense(2)(x)
    output = Activation("relu")(x)
    return Model(input, output)
