import json
import time
import traceback as tb
import urllib.parse
from types import SimpleNamespace
import functools
import logging
import re

logger = logging.getLogger(__name__)

########## Helpers ##########

# https://stackoverflow.com/a/31174427

def rsetattr(obj, attr, val):
    if type(val) == str:
        val =  urllib.parse.unquote_plus(val)
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)

def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

########## idomaar ##########

class idomaarThingy():  
    def __init__(self, rType, rId, rTimeStamp, rProps, rLinked):
        self.type = rType
        self.id = rId
        self.timestamp = rTimeStamp
        
        if rProps is None or rProps == '':
            self.properties = None
        else:
            self.properties = SimpleNamespace()
            for key, value in rProps.items():
                self._rsettr("properties", key, value)
                
        if rLinked is None or rLinked == '':
            self.linked = None
        else:
            self.linked = SimpleNamespace()
            for key, value in rLinked.items():
                self._rsettr("linked", key, value)
        
    def __str__(self):
        return "{} {}".format(self.type, self.id)
    
    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def from_dict(cls, d):
        # If we're loading a song, then check if we can add some metadata to it.
        if d.get('type') == 'track' and idomaarReader.tracks_artists is not None:
            d['artist_id'] = idomaarReader.tracks_artists[d.get('id')]
        return idomaarThingy(d.get('type'),
                            d.get('id'),
                            d.get('timestamp'),
                            {k:v for k,v in d.items() if k not in ['type','id','timestamp','linked']},
                            d.get('linked'))
    
    def _rsettr(self, prefix, name, val):
        if type(val) == 'dict':
            setattr(self, prefix+'.'+val, SimpleNamespace())
            for key, value in val.items():
                self._rsettr(prefix+'.'+val, key, value)
        else:
            if name == 'objects' and type(val) == list:
                val = [idomaarThingy.from_dict(x) for x in val if type(x) == dict]
            rsetattr(self, '.'.join([prefix, name]), val)


class idomaarEntity(idomaarThingy):
    pass

class idomaarRelationship(idomaarThingy):
    pass


class idomaarReader():
    tracks_artists = None
    def __init__(self, path, tracks_file = None, tolerant=False):
        self.path = path
        self.tolerant = tolerant
        self.tracks_file = tracks_file
        self.use_metadata = self.tracks_file is not None
        if self.use_metadata:
            self.load_tracks_data()
        # for having _len_ and being able to use progressbar
        with open(self.path, 'rb') as f:
            self.total = sum(line != '' for line in f)
    def load_tracks_data(self):
        # check if already loaded
        if idomaarReader.tracks_artists is not None:
            return
        # Not all values in range 0-numlines are used, but it's pretty close.
        # Also, using a vector uses 58% of the memory that a dict would use.
        tracks_artists = [0] * 5675143
        with open("../data/ThirtyMusic/entities/tracks.idomaar") as tracks_data:
            line = tracks_data.readline()
            i = 0
            while line:
                # we don't use album data because only ~38% of songs and ~48% of
                # plays have album data.
                objtype, track_id, track_len, track_data, metadata = line.split("\t")
                metadata = json.loads(metadata)
                artist_id = metadata["artists"][0]["id"]
                tracks_artists[int(track_id)] = artist_id

                line = tracks_data.readline()
                if i%1000000 == 0:
                    logger.info("Loading track data: {}%".format(i/5675143*100))
                i+=1
        logger.info("100%")
        # Save it on static attribute
        idomaarReader.tracks_artists = tracks_artists

    @classmethod
    def _make_record(cls, line, tolerant = False):
        try:
            t, i, ts, p, le = (line.split('\t') + ["",] * 5)[:5]
            try:
                ts = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(int(ts)))
            except:
                ts = None
            if le:
                le = json.loads(le)
            if p:
                if t == "playlist":
                    # Some title properties contain unescaped sequences,
                    # e.g. {"title": "this "is" unescaped"}
                    # or invalid escape sequences (e.g. Gothic\Rock)
                    match = re.findall(
                        pattern = '\"Title\"\:\"(.+)?\",\"numtracks\"',
                        string = p)
                    p = p.replace(match[0], match[0].replace("\"", ""))
                    p = p.replace("\\", "/")
                elif t == "event.session":
                    # Sometimes columns are not separated by tabs but
                    # by one space only. This causes a json parser
                    # error, so we fix it here.
                    if "} {" in p:
                        p, le = p.split("} {")
                        p += "}"
                        le = json.loads("{"+le)
                p = json.loads(p)


            return idomaarEntity(t, i, ts, p, le)
        except Exception as e:
            logger.error(f"{e}\n Offending line: {line}")
            if tolerant:
                return None
            else:
                raise

    def __enter__(self):
        self._f = open(self.path, "r")
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self._f.close()
    
    def __len__(self):
        return self.total
    
    def __iter__(self):
        return self
        
    def __next__(self):
        retval = None
        try:
            while retval is None:
                line = next(self._f)
                while line == '':
                    line = next(self._f)
                retval = idomaarReader._make_record(line, self.tolerant)
            return retval
        except StopIteration:
            raise StopIteration()
