import os
import glob
import hdf5_getters
import json

FEATURES = [
    ("artist_mbid", "the musicbrainz.org ID for this artists is db9..."),
    ("artist_mbtags", "this artist received 4 tags on musicbrainz.org"),
    ("artist_mbtags_count", "raw tag count of the 4 tags this artist received on musicbrainz.org"),
    ("artist_name", "artist name"),
    ("artist_terms", "this artist has 12 terms (tags) from The Echo Nest"),
    ("artist_terms_freq", "frequency of the 12 terms from The Echo Nest (number between 0 and 1)"),
    ("artist_terms_weight", "weight of the 12 terms from The Echo Nest (number between 0 and 1)"),
    ("danceability", "danceability measure of this song according to The Echo Nest (between 0 and 1, 0 => not analyzed)"),
    ("duration", "duration of the track in seconds"),
    ("release", "album name from which the track was taken, some songs / tracks can come from many albums, we give only one"),
    #("similar_artists", "a list of 100 artists (their Echo Nest ID) similar to Rick Astley according to The Echo Nest"),
    ("song_hotttnesss", "according to The Echo Nest, when downloaded (in December 2010), this song had a 'hotttnesss' of 0.8 (on a scale of 0 and 1)"),
    ("song_id", "The Echo Nest song ID, note that a song can be associated with many tracks (with very slight audio differences)"),
    ("title", "song title"),
    ("track_7digitalid", "the ID of this song on the service 7digital.com"),
    ("track_id", "The Echo Nest ID of this particular track on which the analysis was done"),
    ("year", "year when this song was released, according to musicbrainz.org"),
]


def H5FileIterator(basedir):
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root, '*' + '.h5'))
        for file in files:
            yield file


def process_file(path):
    d = {}
    with hdf5_getters.open_h5_file_read(path) as h5:
        for feature, _ in FEATURES:
            transformer = getattr(hdf5_getters, f"get_{feature}")
            d[feature] = transformer(h5)
    return d


class defaultdict(dict):
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return lambda x: str(x)


TYPES_FORMATTERS = defaultdict()
TYPES_FORMATTERS['bytes_'] = lambda x: x.decode('UTF-8')
TYPES_FORMATTERS['ndarray'] = lambda x: [TYPES_FORMATTERS[type(v).__name__](v) for v in x]


def jsonify(dic):
    for k, v in dic.items():
        tf = TYPES_FORMATTERS[type(v).__name__]
        # print(type(v).__name__)
        dic[k] = tf(v)
    return json.dumps(dic)


with open("data_set.json", "w") as out:
    for file in H5FileIterator("../data/MillionSongSubset/data/"):
        out.write(jsonify(process_file(file)))
        out.write("\n")
