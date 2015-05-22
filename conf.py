import ConfigParser
import re

class ConfigFile():
    """
    Adapted from a helper method from Python Wiki.
    This class will hold a config file, and attempt to
    automatically convert values to ints or booleans.
    """
    def __init__(self, path):
        self.conf = ConfigParser.ConfigParser()
        self.conf.read(path)

    def getsection(self, section):
        """
        Returns an entire section in a dict.
        The dict's keys will be uppercase, as is normal
        for configs.
        """
        keys = {}
        try:
            options = self.conf.options(section)
        except Exception, ex:
            print(ex)
            return {}

        for opt in options:
            key = opt.upper()
            try:
                keys[key] = self.get(section, opt)
            except Exception, ex:
                print(ex)
                keys[key] = None
        return keys

    def get(self, section, opt):
        """
        Gets a config value. This value will automatically
        be converted to a boolean, float or int.
        """
        try:
            key = self.conf.get(section, opt)
            if key == 'True':
                return True
            elif key == 'False':
                return False
            elif re.match('^[0-9]+$', key):
                return self.conf.getint(section, opt)
            elif re.match('^[0-9]+\.[0-9]+$', key):
                return self.conf.getfloat(section, opt)
            else:
                return key
        except Exception, ex:
            print(ex)
            return None
