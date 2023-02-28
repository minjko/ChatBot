# 필요한 모듈 임포트
import pandas as pd
import tensorflow as tf
from keras import preprocessing # 원래 from tensorflow.keras import preprocessing (라이브러리 import 문제로 변경함)
from tensorflow.python.keras.models import Model      # 원래 from tensorflow.keras.models import Model (라이브러리 import 문제로 변경함)
from tensorflow.python.keras.layers import Input, Embedding, Dense, Dropout, Conv1D, GlobalMaxPool1D, concatenate      # 원래 from tensorflow.keras.layers import ... (라이브러리 import 문제로 변경함)

# 데이터 읽어오기
train_file = "total_train_data.csv"
data = pd.read_csv(train_file, delimiter=',')
queries = data['query'].tolist()
intents = data['intent'].tolist()

from utils.Preprocess import Preprocess
p = Preprocess(word2index_dic='../../train_tools/dict/chatbot_dict.bin', userdic='../../utils/user_dic.tsv')

# 단어 시퀀스 생성
sequences = []
for sentence in queries:
	pos = p.pos(sentence)
	keywords = p.get_keywords(pos, without_tag=True)
	seq = p.get_wordidx_sequence(keywords)
	sequences.append(seq)

# 단어 인덱스 시퀀스 벡터 생성
# 단어 시퀀스 벡터 크기
from config.GlobalParams import MAX_SEQ_LEN
from keras_preprocessing.sequence import pad_sequences # 원래 line 4로 아래 코드 진행해야함
padded_seqs = pad_sequences(sequences, maxlen=MAX_SEQ_LEN, padding='post') # 원래 preprocessing.sequence.pad_sequences(...)

# 학습용, 검증용, 테스트용 데이터셋 생성
# 학습셋:검증셋:테스트셋 = 7:2:1
ds = tf.data.Dataset.from_tensor_slices((padded_seqs, intents))
ds = ds.shuffle(len(queries))

train_size = int(len(padded_seqs) * 0.7)
val_size = int(len(padded_seqs) * 0.2)
test_size = int(len(padded_seqs) * 0.1)

train_ds = ds.take(train_size).batch(20)
val_ds = ds.skip(train_size).take(val_size).batch(20)
test_ds = ds.skip(train_size+val_size).take(test_size).batch(20)

# 하이퍼파라미터 설정
dropout_prob = 0.5
EMB_SIZE = 128
EPOCH = 5
VOCAB_SIZE = len(p.word_index) + 1 # 전체 단어 수

# CNN 모델 정의
input_layer = Input(shape=(MAX_SEQ_LEN, ))
embedding_layer = Embedding(VOCAB_SIZE, EMB_SIZE, input_length=MAX_SEQ_LEN)(input_layer)
dropout_emb = Dropout(rate=dropout_prob)(embedding_layer)

conv1 = Conv1D(
	filters=128,
	kernel_size=3,
	padding='valid',
	activation=tf.nn.relu)(dropout_emb)
pool1 = GlobalMaxPool1D()(conv1)

conv2 = Conv1D(
	filters=128,
	kernel_size=4,
	padding='valid',
	activation=tf.nn.relu)(dropout_emb)
pool2 = GlobalMaxPool1D()(conv2)

conv3 = Conv1D(
	filters=128,
	kernel_size=5,
	padding='valid',
	activation=tf.nn.relu)(dropout_emb)
pool3 = GlobalMaxPool1D()(conv3)

# 3, 4, 5-gram 이후 합치기
concat = concatenate([pool1, pool2, pool3])

hidden = Dense(128, activation=tf.nn.relu)(concat)
dropout_hidden = Dropout(rate=dropout_prob)(hidden)
logits = Dense(5, name='logits')(dropout_hidden)
predictions = Dense(5, activation=tf.nn.softmax)(logits)

# 모델 생성
model = Model(inputs=input_layer, outputs=predictions)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 모델 학습
model.fit(train_ds, validation_data=val_ds, epochs=EPOCH, verbose=1)

# 모델 평가
loss, accuracy = model.evaluate(test_ds, verbose=1)
print('Accuracy: %f' % (accuracy * 100))
print('loss: %f' % (loss))

# 모델 저장
model.save('intent_model.h5')