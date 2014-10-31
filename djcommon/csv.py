# encoding: utf-8

import csv


class UnicodeDictReader(csv.DictReader):
    """Used to convert each line to the specified encoding"""

    def __init__(self, file, encoding='utf-8', *args, **kw):
        self.encoding = encoding
        csv.DictReader.__init__(self, file, *args, **kw)

    def next(self):
        line = csv.DictReader.next(self)
        line = dict(zip(
            line.keys(),
            map(lambda v: v.decode(self.encoding), line.values())))
        return line