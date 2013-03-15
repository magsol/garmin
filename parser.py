import sys
import xml.parsers.expat
import matplotlib.pyplot as plot
import numpy as np
from datetime import datetime
import time
from scipy import stats

class GCFileParser:

    def __init__(self, filename, sport = 'Running'):
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.buffer_text = True
        self.parser.StartElementHandler = self._startElement
        self.parser.EndElementHandler = self._endElement
        self.parser.CharacterDataHandler = self._characterData

        self.filename = filename
        self.isSport = False
        self.wrongSport = False
        self.isDistance = False
        self.isTime = False
        self.isTrack = False
        self.isId = False
        self.splits = []
        self.times = []
        self.timestamp = None

        self.sport = sport

    def parse(self):
        # Read the TCX file and parse it.
        f = open(self.filename)
        self.parser.ParseFile(f)
        f.close()

        # All done!
        if self.wrongSport is True:
            return [None, None, None]
        return [self.timestamp, np.array(self.splits), np.array(self.times)]

    def _startElement(self, name, attrs):
        if name == 'Activity':
            if attrs['Sport'] != self.sport:
                self.wrongSport = True
            else:
                self.isSport = True
        elif self.isSport and name == 'TotalTimeSeconds':
            self.isTime = True
        elif self.isSport and name == 'DistanceMeters':
            self.isDistance = True
        elif self.isSport and name == 'Track':
            self.isTrack = True
        elif self.isSport and name == 'Id':
            self.isId = True

    def _endElement(self, name):
        if name == 'Activity' and self.isSport:
            # Clean up.
            self.isSport = False
        elif name == 'TotalTimeSeconds':
            self.isTime = False
        elif name == 'DistanceMeters':
            self.isDistance = False
        elif name == 'Track':
            self.isTrack = False
        elif name == 'Id':
            self.isId = False

    def _characterData(self, data):
        if self.isTime:
            self.times.append(float(data))
        elif self.isDistance and not self.isTrack:
            self.splits.append(float(data))
        elif self.isId:
            self.timestamp = int(time.mktime(datetime.strptime(data, "%Y-%m-%dT%H:%M:%S.000Z").timetuple()))

if __name__ == '__main__':
    analyze = GCFileParser(sys.argv[1])
    ts, distances, times = analyze.parse()
    print distances
    print times
    print ts
