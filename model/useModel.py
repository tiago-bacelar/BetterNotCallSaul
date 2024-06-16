from gensim.models import Word2Vec

def findWord(model,word):
    if word in model.wv:
        return model.wv[word]
    else:
        return None

if __name__ == '__main__':
    w2v_model = Word2Vec.load('model.model')
    while True:
        w = input('word: ')
        r=findWord(w2v_model,w)
        print(r)
        if r is not None:
            print(w2v_model.wv.most_similar(w))
