import gensim
from idomaar import *
import progressbar
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class PlaylistIterator():
    def __init__(self):
        self.path = "../data/ThirtyMusic/relations/sessions.idomaar"
    
    def __iter__(self):
        with idomaarReader(self.path) as ier:
            for thingy in progressbar.progressbar(ier):
                try:
                    yield [str(x.id) for x in thingy.linked.objects]
                except Exception as e:
                    print(e)
                    print(thingy)
                    raise
                    
playliterator = PlaylistIterator()
model = gensim.models.Word2Vec(playliterator, size=100, min_count=1, workers=4)
model.save("cheap.w2v")