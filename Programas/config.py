import configparser

class Config:
    def __init__(self, path='dryermon.ini'):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(path)

    def get(self, sec, key, default=None):
        try:
            return self.cfg.get(sec, key)
        except:
            return default

    def geti(self, sec, key, default=0):
        try:
            return self.cfg.getint(sec, key)
        except:
            return default

    def getf(self, sec, key, default=0.0):
        try:
            return self.cfg.getfloat(sec, key)
        except:
            return default

    def get_ports(self):
        if not self.cfg.has_section('ports'):
            return []
        return [v for _, v in self.cfg.items('ports') if v]
