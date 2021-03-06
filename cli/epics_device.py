#
#   PowerSupply class. Contains all PVs for a power supply
#
#   author: Watler Werner
#   email: wernwa@gmail.com
#

from epics import PV
from PV_CONN import PV_CONN




class PowerSupply:

    def __init__(self, prefix=None, nr=None):

        self.prefix = prefix
        self.NR = nr

        self.Volt = PV_CONN(prefix+nr+'volt', auto_monitor=True)
        self.Curr = PV_CONN(prefix+nr+'curr', auto_monitor=True)
        # tmp comment till found the output error
        self.output = PV_CONN(prefix+nr+'output', auto_monitor=True)
        self.online = PV_CONN(prefix+nr+'online', auto_monitor=True)

    def getVolt(self):
        return self.Volt.get()

    def getCurr(self):
        return self.Curr.get()


    def setVolt(self, volt):
        self.Volt.put(volt)


    def setCurr(self, ampare):
        self.Curr.put(ampare)

