import json
import time
import traceback as tb
import urllib 
from types import SimpleNamespace
import functools

# https://stackoverflow.com/a/31174427

def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)

def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

class idomaarThingy():  
    def __init__(self, rType, rId, rTimeStamp, rProps, rLinked):
        self.type = rType
        self.id = rId
        self.timestamp = rTimeStamp
        
        if rProps is None:
            self.properties = None
        else:
            self.properties = SimpleNamespace()
            for key, value in rProps.items():
                self._rsettr("properties", key, value)
        if rLinked is None:
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
                val = [idomaarThingy.from_dict(x) for x in val]
            rsetattr(self, '.'.join([prefix, name]), val)


class idomaarEntity(idomaarThingy):
    pass

class idomaarRelationship(idomaarThingy):
    pass


class idomaarReader():
    def __init__(self, path):
        self.path = path
        
    @classmethod
    def _make_record(cls, line):
        t, i, ts, p, le = (line.split() + ["",] * 5)[:5]
        ts = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(int(ts)))
        if le: le = json.loads(urllib.parse.unquote(le))
        if p: p = json.loads(urllib.parse.unquote(p))
        return idomaarEntity(t, i, ts, p, le)
    
    def __enter__(self):
        self._f = open(self.path, "r")
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self._f.close()
    
    def __iter__(self):
        return self
        
    def __next__(self):
        line = self._f.readline()
        if line is None: raise StopIteration()
        return idomaarReader._make_record(line)