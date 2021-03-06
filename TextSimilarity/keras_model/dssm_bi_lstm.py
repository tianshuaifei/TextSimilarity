from __future__ import absolute_import
from __future__ import print_function

import keras
from keras.layers import Input, LSTM, Dense,Embedding,Bidirectional
from keras.models import Model

from MaYi import data_feature as data_provider

print("Loading data...")
train_query, train_doc, train_label = data_provider.load_train_dataset()
valid_query, valid_doc, valid_label = data_provider.load_valid_dataset()
test_query, test_doc, test_label = data_provider.load_pre_dataset()
print(len(train_query), 'train sequences')

timesteps = 30
num_classes = 2
max_features=2300

tweet_a = Input(shape=(timesteps,))
tweet_b = Input(shape=(timesteps,))


# tweet_a_emb = Embedding(output_dim=512, input_dim=max_features, input_length=20)(tweet_a)
# tweet_b_emb= Embedding(output_dim=512, input_dim=max_features, input_length=20)(tweet_b)
# This layer can take as input a matrix
# and will return a vector of size 64
shared_emb=Embedding(output_dim=512, input_dim=max_features, input_length=20)

shared_lstm = Bidirectional(LSTM(64,return_sequences=True))
shared_lstm_1 = Bidirectional(LSTM(64,return_sequences=True))
shared_lstm_2 = Bidirectional(LSTM(64))
# When we reuse the same layer instance
# multiple times, the weights of the layer
# are also being reused
# (it is effectively *the same* layer)
tweet_a_emb=shared_emb(tweet_a)
tweet_b_emb=shared_emb(tweet_b)

encoded_a = shared_lstm(tweet_a_emb)
encoded_b = shared_lstm(tweet_b_emb)

encoded_a_1 = shared_lstm_1(encoded_a)
encoded_b_1 = shared_lstm_1(encoded_b)

encoded_a_2 = shared_lstm_2(encoded_a_1)
encoded_b_2 = shared_lstm_2(encoded_b_1)

# We can then concatenate the two vectors:
# merged_vector =Cosine([encoded_a, encoded_b])
# merged_vector_em=Reshape(2)
#merged_vector = keras.layers.concatenate([encoded_a, encoded_b], axis=-1)
merged_vector = keras.layers.dot([encoded_a_2, encoded_b_2],axes=-1)
# And add a logistic regression on top
predictions = Dense(num_classes, activation='softmax')(merged_vector)

# We define a trainable model linking the
# tweet inputs to the predictions
model = Model(inputs=[tweet_a, tweet_b], outputs=predictions)

model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['accuracy'])
model.fit([train_query, train_doc], train_label, epochs=10,validation_data=([valid_query, valid_doc], valid_label))
pre=model.predict([test_query, test_doc])
print(pre)
model.save('dssm_bilstm_3_model.h5')
