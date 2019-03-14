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

class idomaarEntity():
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
        return idomaarEntity(d.get('type'),
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
            if type(val) == list:
                val = [idomaarRegistry.find_or_create_from_dict(x.get("type"), x.get("id"), x)
                        for x in val if type(x) == dict]
            rsetattr(self, '.'.join([prefix, name]), val)

class idomaarRegistry:
    registry = dict()
    # In practice we want to analyse relationships without having to preload
    # all entities. Linked objects in relationships will automatically cascade
    # create referred objects, unless they are already in the registry.
    # For example, we'd like to analyse user song sessions, and though we do
    # preload songs, we don't want to preload.
    @classmethod
    def in_registry(cls, entity_type, entity_id):
        if entity_type not in idomaarRegistry.registry:
            idomaarRegistry.registry[entity_type] = dict()
        return entity_id in idomaarRegistry.registry[entity_type]

    @classmethod
    def find_or_add(cls, entity_type, entity_id, entity):
        if not cls.in_registry(entity_type, entity_id):
            idomaarRegistry.registry[entity_type][entity_id] = entity

        return idomaarRegistry.registry[entity_type][entity_id]

    @classmethod
    def find_or_create_from_dict(cls, entity_type, entity_id, data_dict):
        if not cls.in_registry(entity_type, entity_id):
            idomaarRegistry.registry[entity_type][entity_id] = idomaarEntity.from_dict(data_dict)

        return idomaarRegistry.registry[entity_type][entity_id]

class idomaarReader():
    def __init__(self, path, tolerant=False):
        self.path = path
        self.tolerant = tolerant
        # for having _len_ and being able to use progressbar
        with open(self.path, 'rb') as f:
            self.total = sum(line != '' for line in f)

    def preload_entities(self, filename, expected_number = 0):
        # Preloads entities and saves them on the static idomaarRegistry.
        # If you know the number of lines beforehand, setting
        # expected_number will give you progress updates.
        with open(filename) as entity_file:
            line = entity_file.readline()
            lines_processed = 0
            while line:
                try:
                    t, i, ts, p, le = idomaarReader._parse_line(line, self.tolerant)
                    entity = idomaarEntity(t, i, ts, p, le)
                    # Add entity to registry to be used later
                    idomaarRegistry.find_or_add(t, i, entity)
                except Exception as e:
                    logger.error(f"{e}\n Offending line: {line}")
                    if not self.tolerant:
                        raise
                lines_processed+=1
                if expected_number > 0 and lines_processed % 1e5 == 0:
                    logger.info("Loading entity data: {}%".format(lines_processed/expected_number*100))
                line = entity_file.readline()

        logger.info("Loading entity data: 100%")

    @classmethod
    def _parse_line(cls, line, tolerant = False):
        t, i, ts, p, le = (line.split('\t') + ["",] * 5)[:5]
        i = int(i)
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
        return t, i, ts, p, le
    @classmethod
    def _make_record(cls, line, tolerant = False):
        try:
            t, i, ts, p, le = idomaarReader._parse_line(line, tolerant)
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
