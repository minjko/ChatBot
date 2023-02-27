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