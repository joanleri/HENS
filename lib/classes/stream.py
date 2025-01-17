# Stream Class
# A stream in the problems of interest is defined by:
# 1. An inlet temperature Tin
# 2. An outlet temperature Tout
# 3. A flow rate - heat capacity product FCp
from process_stream import Process_Stream

class Stream(Process_Stream):


    def __init__(self, Tin, Tout, FCp):
        Process_Stream.__init__(self, Tin, Tout)
        self.FCp = FCp
        self.heat = abs((Tout - Tin) * FCp)
