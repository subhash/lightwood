import torch
from lightwood.encoders.text.helpers.rnn_helpers import Lang
import numpy as np
from lightwood.encoders.encoder_base import BaseEncoder

UNCOMMON_WORD = '<UNCOMMON>'
UNCOMMON_TOKEN = 0


class OneHotEncoder(BaseEncoder):

    def __init__(self, is_target=False):
        super().__init__(is_target)
        self._lang = None

    def prepare_encoder(self, priming_data, max_dimensions=20000):
        if self._prepared:
            raise Exception('You can only call "prepare_encoder" once for a given encoder.')

        self._lang = Lang('default')
        self._lang.index2word = {UNCOMMON_TOKEN: UNCOMMON_WORD}
        self._lang.word2index = {UNCOMMON_WORD: UNCOMMON_TOKEN}
        self._lang.word2count[UNCOMMON_WORD] = 0
        self._lang.n_words = 1
        for category in priming_data:
            if category is not None:
                self._lang.addWord(str(category))

        while self._lang.n_words > max_dimensions:
            necessary_words = UNCOMMON_WORD
            least_occuring_words = self._lang.getLeastOccurring(n=len(necessary_words) + 1)

            word_to_remove = None
            for word in least_occuring_words:
                if word not in necessary_words:
                    word_to_remove = word
                    break

            self._lang.removeWord(word_to_remove)

        self._prepared = True

    def encode(self, column_data):
        if not self._prepared:
            raise Exception('You need to call "prepare_encoder" before calling "encode" or "decode".')
        ret = []
        v_len = self._lang.n_words

        for word in column_data:
            encoded_word = [0] * v_len
            if word is not None:
                word = str(word)
                index = self._lang.word2index[word] if word in self._lang.word2index else UNCOMMON_TOKEN
                encoded_word[index] = 1

            ret.append(encoded_word)

        return self._pytorch_wrapper(ret)

    def decode(self, encoded_data):
        encoded_data_list = encoded_data.tolist()
        ret = []

        for vector in encoded_data_list:
            ohe_index = np.argmax(vector)

            ret.append(self._lang.index2word[ohe_index])
        return ret
