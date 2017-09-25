#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import MeCab
import collections
from gensim import models
from gensim.models.doc2vec import LabeledSentence
import json

INPUT_DOC_DIR = './aozora/'
OUTPUT_MODEL = 'doc2vec.model'
PASSING_PRECISION = 93

# 全てのファイルのリストを取得
def get_all_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

# ファイルから文章を返す
def read_document(path):
    with open(path, 'r', encoding='sjis', errors='ignore') as f:
        return f.read()

# 青空文庫ファイルから作品部分のみ抜き出す
def trim_doc(doc):
    lines = doc.splitlines()
    valid_lines = []
    is_valid = False
    horizontal_rule_cnt = 0
    break_cnt = 0
    for line in lines:
        if horizontal_rule_cnt < 2 and '-----' in line:
            horizontal_rule_cnt += 1
            is_valid = horizontal_rule_cnt == 2
            continue
        if not(is_valid):
            continue
        if line == '':
            break_cnt += 1
            is_valid = break_cnt != 3
            continue
        break_cnt = 0
        valid_lines.append(line)
    return ''.join(valid_lines)

# 文章から単語に分解して返す
def split_into_words(doc):
    mecab = MeCab.Tagger("-Ochasen")
    valid_doc = trim_doc(doc)
    lines = mecab.parse(doc).splitlines()
    words = []
    for line in lines:
        chunks = line.split('\t')
        if len(chunks) > 3 and (chunks[3].startswith('動詞') or chunks[3].startswith('形容詞') or (chunks[3].startswith('名詞') and not chunks[3].startswith('名詞-数'))):
            words.append(chunks[0])
    return LabeledSentence(words=words, tags=["tweet"])

# ファイルから単語のリストを取得
def corpus_to_sentences(words_list):
    #docs = [read_document(x) for x in corpus]
    for idx, doc in enumerate(words_list):
        sys.stdout.write('\r前処理中 {} / {}'.format(idx, len(words_list)))
        yield split_into_words(doc)

# 学習
def train(sentences):
    model = models.Doc2Vec(size=400, alpha=0.0015, sample=1e-4, min_count=1, workers=4)
    model.build_vocab(sentences)
    for x in range(30):
        print(x)
        model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)
        ranks = []
        for doc_id in range(100):
            inferred_vector = model.infer_vector(sentences[doc_id].words)
            sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
            rank = [docid for docid, sim in sims].index(sentences[doc_id].tags[0])
            ranks.append(rank)
        print(collections.Counter(ranks))
        if collections.Counter(ranks)[0] >= PASSING_PRECISION:
            break
    return model

if __name__ == '__main__':
    f = open("tweet_data.json","r")
    json_str = f.read()
    f.close()
    json_obj = json.loads(json_str)
    words_list = []
    for json_obj_c in json_obj:
        words_list.extend(list(json_obj_c.values()))
    #corpus = #list(get_all_files(INPUT_DOC_DIR))
    sentences = list(corpus_to_sentences(words_list))
    print()
    model = train(sentences)
    model.save(OUTPUT_MODEL)
