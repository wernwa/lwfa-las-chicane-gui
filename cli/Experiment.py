#
#   This file is imported from all other python files. It contains all EPICs PVs
#   for the experiment. It also defines some functions for the cli interface
#
#   author: Watler Werner
#   email: wernwa@gmail.com


import sys
sys.path.insert(0, './')
from epics import PV
from epics_device import PowerSupply
from Magnet import Magnet
from PV_CONN import PV_CONN
import json
from time import sleep
from time import strftime
from init_vars import *
import numpy

relee_sign = PV_CONN('chicane:zps:relee:sign', auto_monitor=True )
relee =PowerSupply(prefix='chicane:zps:', nr='relee:')
ps1 =  PowerSupply(prefix='chicane:zps:', nr='1:',   )
ps2 =  PowerSupply(prefix='chicane:zps:', nr='2:',   )
ps3 =  PowerSupply(prefix='chicane:zps:', nr='3:',   )
ps4 =  PowerSupply(prefix='chicane:zps:', nr='4:',   )
ps5 =  PowerSupply(prefix='chicane:zps:', nr='5:',   )
ps6 =  PowerSupply(prefix='chicane:zps:', nr='6:',   )
ps7 =  PowerSupply(prefix='chicane:zps:', nr='7:',   )
ps8 =  PowerSupply(prefix='chicane:zps:', nr='8:',   )
ps9 =  PowerSupply(prefix='chicane:zps:', nr='9:',   )

q1_temp = PV_CONN('chicane:q1:temp', auto_monitor=True )
q2_temp = PV_CONN('chicane:q2:temp', auto_monitor=True )
q3_temp = PV_CONN('chicane:q3:temp', auto_monitor=True )
q4_temp = PV_CONN('chicane:q4:temp', auto_monitor=True )
q5_temp = PV_CONN('chicane:q5:temp', auto_monitor=True )
q6_temp = PV_CONN('chicane:q6:temp', auto_monitor=True )
q7_temp = PV_CONN('chicane:q7:temp', auto_monitor=True )
d1_temp = PV_CONN('chicane:d1:temp', auto_monitor=True )
d2_temp = PV_CONN('chicane:d2:temp', auto_monitor=True )
temp_all = PV_CONN('chicane:temp_all', auto_monitor=True )
switchbox = PV_CONN('chicane:zps:switchbox', auto_monitor=True )

q1_volt = PV_CONN('chicane:q1:volt', auto_monitor=True )
q2_volt = PV_CONN('chicane:q2:volt', auto_monitor=True )
q3_volt = PV_CONN('chicane:q3:volt', auto_monitor=True )
q4_volt = PV_CONN('chicane:q4:volt', auto_monitor=True )
q5_volt = PV_CONN('chicane:q5:volt', auto_monitor=True )
q6_volt = PV_CONN('chicane:q6:volt', auto_monitor=True )
q7_volt = PV_CONN('chicane:q7:volt', auto_monitor=True )
d1_volt = PV_CONN('chicane:d1:volt', auto_monitor=True )
d2_volt = PV_CONN('chicane:d2:volt', auto_monitor=True )
magn_volt_all = PV_CONN('chicane:magn_volt_all', auto_monitor=True )

q1_curr = PV_CONN('chicane:q1:curr', auto_monitor=True )
q2_curr = PV_CONN('chicane:q2:curr', auto_monitor=True )
q3_curr = PV_CONN('chicane:q3:curr', auto_monitor=True )
q4_curr = PV_CONN('chicane:q4:curr', auto_monitor=True )
q5_curr = PV_CONN('chicane:q5:curr', auto_monitor=True )
q6_curr = PV_CONN('chicane:q6:curr', auto_monitor=True )
q7_curr = PV_CONN('chicane:q7:curr', auto_monitor=True )
d1_curr = PV_CONN('chicane:d1:curr', auto_monitor=True )
d2_curr = PV_CONN('chicane:d2:curr', auto_monitor=True )
magn_curr_all = PV_CONN('chicane:magn_curr_all', auto_monitor=True )


np_q1_temp =  numpy.array([2,3,1,0])

quad1 = {q1_volt.pvname:q1_volt, q1_curr.pvname:q1_curr,q1_temp.pvname:q1_temp,
            ps1.Volt.pvname:ps1.Volt, ps1.Curr.pvname:ps1.Curr }
quad2 = {q2_volt.pvname:q2_volt, q2_curr.pvname:q2_curr,q2_temp.pvname:q2_temp,
            ps2.Volt.pvname:ps2.Volt, ps2.Curr.pvname:ps2.Curr }
quad3 = {q3_volt.pvname:q3_volt, q3_curr.pvname:q3_curr,q3_temp.pvname:q3_temp,
            ps3.Volt.pvname:ps3.Volt, ps3.Curr.pvname:ps3.Curr }
quad4 = {q4_volt.pvname:q4_volt, q4_curr.pvname:q4_curr,q4_temp.pvname:q4_temp,
            ps4.Volt.pvname:ps4.Volt, ps4.Curr.pvname:ps4.Curr }
quad5 = {q5_volt.pvname:q5_volt, q5_curr.pvname:q5_curr,q5_temp.pvname:q5_temp,
            ps5.Volt.pvname:ps5.Volt, ps5.Curr.pvname:ps5.Curr }
quad6 = {q6_volt.pvname:q6_volt, q6_curr.pvname:q6_curr,q6_temp.pvname:q6_temp,
            ps6.Volt.pvname:ps6.Volt, ps6.Curr.pvname:ps6.Curr }
quad7 = {q7_volt.pvname:q7_volt, q7_curr.pvname:q7_curr,q7_temp.pvname:q7_temp,
            ps7.Volt.pvname:ps7.Volt, ps7.Curr.pvname:ps7.Curr }
dipol1 = {d1_volt.pvname:d1_volt, d1_curr.pvname:d1_curr,d1_temp.pvname:d1_temp,
            ps8.Volt.pvname:ps8.Volt, ps8.Curr.pvname:ps8.Curr }
dipol2 = {d2_volt.pvname:d2_volt, d2_curr.pvname:d2_curr,d2_temp.pvname:d2_temp,
            ps9.Volt.pvname:ps9.Volt, ps9.Curr.pvname:ps9.Curr }

mquad1 = Magnet(ps=ps1, pv_volt=q1_volt, pv_curr=q1_curr, pv_temp=q1_temp)
mquad2 = Magnet(ps=ps2, pv_volt=q2_volt, pv_curr=q2_curr, pv_temp=q2_temp)
mquad3 = Magnet(ps=ps3, pv_volt=q3_volt, pv_curr=q3_curr, pv_temp=q3_temp)
mquad4 = Magnet(ps=ps4, pv_volt=q4_volt, pv_curr=q4_curr, pv_temp=q4_temp)
mquad5 = Magnet(ps=ps5, pv_volt=q5_volt, pv_curr=q5_curr, pv_temp=q5_temp)
mquad6 = Magnet(ps=ps6, pv_volt=q6_volt, pv_curr=q6_curr, pv_temp=q6_temp)
mquad7 = Magnet(ps=ps7, pv_volt=q7_volt, pv_curr=q7_curr, pv_temp=q7_temp)
mdipol1 = Magnet(ps=ps8, pv_volt=d1_volt, pv_curr=d1_curr, pv_temp=d1_temp, magn_type='dipol')
mdipol2 = Magnet(ps=ps9, pv_volt=d2_volt, pv_curr=d2_curr, pv_temp=d2_temp, magn_type='dipol')


mquad1.load_data('magnet-data/q1-k-I.data')
mquad2.load_data('magnet-data/q2-k-I.data')
mquad3.load_data('magnet-data/q3-k-I.data')
mquad4.load_data('magnet-data/q4-k-I.data')
mquad5.load_data('magnet-data/q5-k-I.data')
mquad6.load_data('magnet-data/q6-k-I.data')
mquad7.load_data('magnet-data/q7-k-I.data')
mdipol1.load_data('magnet-data/d1-alpha-I.data')
mdipol2.load_data('magnet-data/d2-alpha-I.data')


ps = []         # alias for powersupply
ps.append(relee)# 0
ps.append(ps1) # 1
ps.append(ps2) # 2
ps.append(ps3) # 3
ps.append(ps4) # 4
ps.append(ps5) # 5
ps.append(ps6) # 6
ps.append(ps7) # 7
ps.append(ps8)
ps.append(ps9) # 9

powersupply = ps
magn = []

data_conf = None
def load_data_conf():
    global data_conf
    with open('config.json', 'rb') as fp:
        data_conf = json.load(fp)

    #data_conf = json.load(fp)

def init_devices():
    global ps, relee, ps1, ps2, ps3, ps4, ps5, ps6, ps7, ps8, ps9, ps10

    if (len(ps)==0):
        ps.append(None) # avoid 0 index
        ps.append(relee)# 1
        ps.append(None) # 2
        ps.append(None) # 3
        ps.append(None) # 4
        ps.append(None) # 5
        ps.append(None) # 6
        ps.append(None) # 7
        ps.append(ps8)
        ps.append(None) # 9
        ps.append(None) # 10

    ''' initialize powersupplies  '''
    global data_conf
    if data_conf==None:
        load_data_conf()

    ps_conf = data_conf['powersupplies']
    for i in range(len(ps)):
        if ps[i] == None:
            continue
        ps[i].setVolt(ps_conf['ps%d'%i])
        print 'init ps%d'%i


    global magn
    if (len(magn)==0):
        magn.append(None) # avoid 0 index
        magn.append(Magnet(ps[8]))# 1
        magn.append(None) # 2
        magn.append(None) # 3
        magn.append(None) # 4
        magn.append(None) # 5
        magn.append(None) # 6
        magn.append(None) # 7

demag_pv = PV('chicane:demag')
demag_steps_pv = PV('chicane:demag:steps')
demag_sleep_pv = PV('chicane:demag:sleep')

def demag():
    demag_steps_pv.put(5)
    #print demag_steps_pv.get()
    demag_sleep_pv.put(2)
    #print demag_sleep_pv.get()
    demag_pv.put(1)


def demag_client_depr():
    relee_val = 24
    ps_heightV = []
    ps_heightV.append(None) # avoid 0 index
    ps_heightV.append(ps1.Volt.get())# 1
    ps_heightV.append(ps2.Volt.get()) # 2
    ps_heightV.append(ps3.Volt.get()) # 3
    ps_heightV.append(ps4.Volt.get()) # 4
    ps_heightV.append(ps5.Volt.get()) # 5
    ps_heightV.append(ps6.Volt.get()) # 6
    ps_heightV.append(ps7.Volt.get()) # 7
    ps_heightV.append(ps8.Volt.get())
    ps_heightV.append(ps9.Volt.get()) # 9
    ps_heightV.append(ps10.Volt.get()) # 10

    print 'starting to demagnetize'

    ''' do demag in steps '''
    steps = 10
    for count in range(1,steps):
        if count%2 > 0:
            relee.Volt.put(relee_val)
        else:
            relee.Volt.put(0)

        for i in range(2,len(ps)):
            if ps[i] == None:
                continue
            volts = ps_heightV[i]-count*ps_heightV[i]/steps
            ps[i].setVolt(volts)
            #print '%d %f (ps:%d %f)' %(count,volts,i,ps_heightV[i])
        sleep(1)


    ''' set all ps to 0 '''
    for i in range(2,len(ps)):
        if ps[i] == None:
            continue
        volts = 0
        ps[i].setVolt(volts)
        #print '%d %f (ps:%d %f)' %(count,volts,i,ps_heightV[i])

    ''' set relee to 0 '''
    relee.setVolt(0)


log_pvs = None


def log_on_change(pvname=None, value=None, char_value=None, **kw):
    print 'PV Changed! %s %0.3f' %(pvname, value)
    fo = open("log.txt", "a")
    string = '%s' %strftime("%Y-%m-%H:%M:%S_%s")
    for i in range(0,len(log_pvs)):
        string += ' %s' %log_pvs[i].get()
    string += '\n';
    fo.write(string)
    fo.close()


def onChanges(pvname=None, value=None, char_value=None, **kw):
    print 'PV Changed! %s %0.3f' %(pvname, value)

write = sys.stdout.write
def onConnectionChange(pvname=None, conn= None, **kws):
    write('PV connection status changed: %s %s\n' % (pvname,  repr(conn)))
    sys.stdout.flush()

def monitor_temp(t):
    t.add_callback(onChanges)

def monitor_ps(powersupply):
    powersupply.Volt.add_callback(onChanges)
    powersupply.Curr.add_callback(onChanges)

def help():
    print '''
------------------------------------------------
    help()          print this info
    init_devices()  initializes the devices with standard values from the config.json file
    ps1 - ps10      global objects to the PowerSupply class. Methods:
                        getVolt(), setVolt(),
                        getCurr(), setCurr()
                    ps1 - ps10 are initialized after calling init_devices()
    demag()         demagnetezising all Magnets at once
    monitor_ps(ps)  Print ampare and volt changes of the given powersupply
    monitor_temp(t) Print temperature changes of the given temp-sensor
------------------------------------------------
    '''



if __name__ == "__main__":
    print 'Initializing Devices'
    load_data_conf()
    help()
    #init_devices()

    #ps[8].setterVolt.add_callback(onChanges)
    #relee.setterVolt.add_callback(onChanges)

