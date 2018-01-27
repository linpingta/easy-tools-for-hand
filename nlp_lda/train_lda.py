#-*- coding: utf-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import logging
import argparse
import operator
from six import iteritems
from gensim.models import LdaModel, LdaMulticore
from gensim.corpora import Dictionary
from gensim import corpora


class LDACorpus(object):
    def __init__(self, word_file, dictionary):
        self.word_file = word_file
        self.dictionary = dictionary

    def __iter__(self):
        for line in open(self.word_file):
            yield self.dictionary.doc2bow(line.split(' '))

        

class LDATrainer(object):
    def __init__(self, conf):
        # train method
        self.do_train = conf.get("do_train", 0)

        # file related
        self.word_file = conf.get("word_file", "")
        self.save_file = conf.get("save_file", "")
        self.save_dict_file = conf.get("save_dict_file", "")
        self.stop_word_file = conf.get("stop_word_file", "")

        # lda setting
        self.eval_every = conf.get("eval_every", 0)
        self.topic_num = conf.get("topic_num", 10)
        self.core_num = conf.get("core_num", 4)

    def _load_stop_wordset(self):
        self.stop_wordset = set([])
        with open(self.stop_word_file, 'r') as fp:
            while 1:
                line = fp.readline()
                if not line.strip():
                    break
                if line.strip() not in self.stop_wordset:
                    self.stop_wordset.add(line.strip()) 

    def _prepare_dataset(self):
        if not self.word_file:
            print "word file empty"
            return

        self._load_stop_wordset()

        texts = []
        with open(self.word_file) as fp:
            while 1:
                line = fp.readline()
                line = line.strip()
                if not line:
                    break
                texts.append([ word for word in line.split(' ') if word not in self.stop_wordset ])
        dictionary = Dictionary(texts)
        print "dictionary size ", dictionary
        corpus = [ dictionary.doc2bow(line) for line in texts ]
        return (corpus, dictionary)
                
    def _prepare_dataset_v2(self):
        if not self.word_file:
            print "word file empty"
            return

        self._load_stop_wordset()

        dictionary = corpora.Dictionary(line.split(' ') for line in open(self.word_file, 'r'))
        stop_ids = [ dictionary.token2id[stopword] for stopword in self.stop_wordset if stopword in dictionary.token2id ]
        once_ids = [ tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == -1 ]
        print "stop_ids len: %s, once_ids len: %s" % (len(stop_ids), len(once_ids))
        dictionary.filter_tokens(stop_ids + once_ids)
        dictionary.compactify()
        print "dictionary size ", dictionary
        corpus = LDACorpus(self.word_file, dictionary)
        return (corpus, dictionary)

    def _train(self, mm, dictionary):
        #lda = LdaModel(corpus=mm, id2word=dictionary, num_topics=self.topic_num)
        lda = LdaMulticore(corpus=mm, id2word=dictionary, num_topics=self.topic_num, workers=self.core_num, eval_every=self.eval_every)
        return lda

    def _load_model(self):
        return (LdaModel.load(self.save_file), Dictionary.load(self.save_dict_file))

    def _save_model(self, lda, dictionary):
        lda.save(self.save_file)
        dictionary.save(self.save_dict_file)
            
    def run(self):
        if self.do_train:
            print "prepare dataset..."
            (mm, dictionary) = self._prepare_dataset_v2()

            print "begin to train..."
            lda = self._train(mm, dictionary)
            print "save model..."
            self._save_model(lda, dictionary)
        else:
            print "load model..."
            (lda, dictionary) = self._load_model()

        print "show result..."
        result = lda.print_topics(self.topic_num)
        for (topic_num, top_words) in result:
            print topic_num, top_words.encode("utf-8")

        print "test result..."
        test_line = "这是 一个 测试 案例".split(" ")
        test_doc = dictionary.doc2bow(test_line)
        print "test_line ", ' '.join(test_line)
        print "topic in reverse ", sorted(lda[test_doc], key=operator.itemgetter(1), reverse=True)


def main():
    parser = argparse.ArgumentParser(description="parse argument")
    parser.add_argument("--do_train", default=1, help="whether to train model", type=int)
    parser.add_argument("--topic_num", default=10, help="topic num in lda result", type=int)
    parser.add_argument("--core_num", default=4, help="core num to use in lda train", type=int)
    parser.add_argument("--eval_every", default=0, help="eval every document num", type=int)
    parser.add_argument("--word_file", default="", help="input words file for lda train", type=str, required=True)
    parser.add_argument("--save_file", default="lda_saved_model", help="file for lda model save", type=str)
    parser.add_argument("--save_dict_file", default="lda_saved_dictionary", help="file for lda dict save", type=str)
    parser.add_argument("--stop_word_file", default="stopwords_h", help="stop words file for lda filter", type=str)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    conf = {
        "do_train" : args.do_train,
        "save_file" : args.save_file,
        "save_dict_file" : args.save_dict_file,
        "word_file" : args.word_file,
        "stop_word_file" : args.stop_word_file,
        "topic_num" : args.topic_num,
        "core_num" : args.core_num,
        "eval_every" : args.eval_every
    }
    lda_trainer = LDATrainer(conf)
    try:
        lda_trainer.run()
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    main()
