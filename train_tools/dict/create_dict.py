#
# 챗봇에서 사용하는 사전 파일 생성
#
from utils.Preprocess import Preprocess
from keras import preprocessing # 원래 from tensorflow.keras import preprocessing이나, 라이브러리 import 문제로 tensorflow.keras가 아닌 keras만 사용함. preprocessing만 사용할 것이므로 괜찮지 않을까 생각 중
import pickle

# 말뭉치 데이터 읽어오기
def read_corpus_data(filename):
    with open(filename, 'r') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
    return data

# 말뭉치 데이터 가져오기
corpus_data = read_corpus_data('./corpus.txt')

# 말뭉치 데이터에서 키워드만 추출해서 사전 리스트 생성
p = Preprocess()
dict = []
for c in corpus_data:
    pos = p.pos(c[1])
    for k in pos:
        dict.append(k[0])

# 사전에 사용될 word2index 생성
# 사전의 첫 번째 인덱스에는 OOV 사용
tokenizer = preprocessing.text.Tokenizer(oov_token='OOV')
tokenizer.fit_on_texts(dict)
word_index = tokenizer.word_index

# 사전 파일 생성
f = open("chatbot_dict.bin", "wb")
try:
    pickle.dump(word_index, f)
except Exception as e:
    print(e)
finally:
    f.close()