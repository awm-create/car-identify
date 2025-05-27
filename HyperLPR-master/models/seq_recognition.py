# models/seq_recognition.py

from keras.models import Model
from keras.layers import Input, Conv2D, BatchNormalization, Activation, MaxPooling2D, Reshape, Dense, GRU, add, concatenate, Dropout
from config.constants import chars

def build_seq_recognition_model(model_path):
    width, height, n_len, n_class = 164, 48, 7, len(chars) + 1
    rnn_size = 256
    input_tensor = Input((width, height, 3))
    x = input_tensor
    for i in range(3):
        x = Conv2D(32 * (2 ** i), (3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Reshape(target_shape=(int(x.shape[1]), int(x.shape[2] * x.shape[3])))(x)
    x = Dense(32)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    gru_1 = GRU(rnn_size, return_sequences=True, reset_after=False)(x)
    gru_1b = GRU(rnn_size, return_sequences=True, go_backwards=True, reset_after=False)(x)
    gru1_merged = add([gru_1, gru_1b])
    gru_2 = GRU(rnn_size, return_sequences=True, reset_after=False)(gru1_merged)
    gru_2b = GRU(rnn_size, return_sequences=True, go_backwards=True, reset_after=False)(gru1_merged)
    x = concatenate([gru_2, gru_2b])
    x = Dropout(0.25)(x)
    x = Dense(n_class, activation='softmax')(x)

    model = Model(inputs=input_tensor, outputs=x)
    model.load_weights(model_path)
    return model
