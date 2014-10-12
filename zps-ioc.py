#!/usr/bin/python

import os
#
#os.environ["EPICS_CA_REPEATER_PORT"] = "20000"
#os.environ["EPICS_CA_SERVER_PORT"] = "20001"

from pcaspy import Driver, SimpleServer, Severity
import random
import math
import thread
import serial
from SockConn import SockConn
import socket
import time
import sys
from termcolor import colored
from setup import *

alive=True


global ps_relee, ps1, ps2, ps3, ps4, ps5, ps6, ps7, ps8, ps9
#global q1, q2, q3, q4, q5, q6, q7, d1, d2


ps_to_magnet = {
    ps1 : 'q1',
    ps2 : 'q2',
    ps3 : 'q3',
    ps4 : 'q4',
    ps5 : 'q5',
    ps6 : 'q6',
    ps7 : 'q7',
    ps8 : 'd1',
    ps9 : 'd2',
}

prefix_to_ps = {
    'zps:1'    : ps1,
    'zps:2'    : ps2,
    'zps:3'    : ps3,
    'zps:4'    : ps4,
    'zps:5'    : ps5,
    'zps:6'    : ps6,
    'zps:7'    : ps7,
    'zps:8'    : ps8,
    'zps:9'    : ps9,
}

ps_to_prefix = {}
for key in prefix_to_ps: ps_to_prefix[prefix_to_ps[key]]=key

record_to_ps = {}
for key in prefix_to_ps:
    record_to_ps['%s:volt'%key] = prefix_to_ps[key]
    record_to_ps['%s:curr'%key] = prefix_to_ps[key]

#global zps_lock, zps_conn
zps_lock = thread.allocate_lock()
zps_conn = False

active_ps_list = []
ps_list = [ps1,ps2,ps3,ps4,ps5,ps6,ps7,ps8,ps9]

relee_sign = -1.0    # plus and minus
relee_plus = 0.0    # V
relee_minus = 24.0    #V

prefix = 'shicane:'
pvdb={
    'demag': {},
    'demag:steps': {
        'type' : 'int'
    },
    'demag:sleep': {
        'type' : 'float',
        'prec' : 3,'unit' : 'seconds'
    },

    'zps:relee:sign': {
        'type' : 'enum',
        'enums': ['-', '+']
    },

    'zps:relee:volt': {
        'prec' : 3,'unit' : 'V'
    },

    'zps:relee:curr': {
        'prec' : 3,'unit' : 'A',
        'asg'  : 'readonly'
    },
    'ps_volt_all' : {
           'type' : 'char',
            'count' : 100,
            'unit' : 'C',
            'asg'  : 'readonly'
    },
    'ps_curr_all' : {
           'type' : 'char',
            'count' : 100,
            'unit' : 'C',
            'asg'  : 'readonly'
    },
}
for name in prefix_to_ps:
    pvdb['%s:volt'%name] = {'prec' : 3,'unit' : 'V',
                    'lolim': 0, 'hilim': 60,
                    'lolo': -1, 'low':-5,
                    'hihi': 55, 'high': 50}
    pvdb['%s:curr'%name] = {'prec' : 3,'unit' : 'A',
                    'lolim': 0, 'hilim': 6,
                    'lolo': -1, 'low':-5,
                    'hihi': 5.7, 'high': 5.5}

for name in ['q1','q2','q3','q4','q5','q6','q7','d1','d2']:
    pvdb['%s:volt'%name] = {'prec' : 3,'unit' : 'V', 'asg'  : 'readonly'}
    pvdb['%s:curr'%name] = {'prec' : 3,'unit' : 'A', 'asg'  : 'readonly'}


class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()

        self.setParam('demag', 0)
        self.setParam('demag:sleep', 1)
        self.setParam('demag:steps', 20)

        # check connection to the power supplies
        global active_ps_list
        try:
            s = SockConn(HOST, PORT)
            #active_ps_list.append(ps_relee)
            s.command('INST:NSEL %d\nOUTP:STAT ON'%ps_relee.NR)
            print '%s powersupplyNR %d [connection '%('zps:relee',ps_relee.NR), colored('OK', 'green'),']'
        except socket.error, msg:
            print colored('Error: ', 'red'),"main LAN zps powersupply does not respond! %s"%msg
            sys.exit(-1)


        for ps in ps_to_prefix:
            try:
                idn = s.question('INST:NSEL %d\n*IDN?\n'%ps.NR,timeout=0.3)
                #print idn
                active_ps_list.append(ps)
                print '%s powersupplyNR %d [connection '%(ps_to_magnet[ps],ps.NR), colored('OK', 'green'),']'
                s.command('INST:NSEL %d\nOUTP:STAT ON'%ps.NR)
            except socket.timeout:
                print '%s powersupplyNR %d ['%(ps_to_prefix[ps],ps.NR),colored('disconnect', 'red'),']'

        if len(active_ps_list)==0:
            print colored('Error: ', 'red'),'no powersupplies discovered!'
            sys.exit(-1)

        s.__del__()


        #start polling
        self.tid = thread.start_new_thread(self.continues_polling,())
        print '----------------------------------------------------------'
        print '%d ps up. Start polling with %0.3f seconds (CTRL+C -> end).'%(len(active_ps_list)+1,zps_poling_time)
        print '----------------------------------------------------------'


    def read(self, reason):


        return self.getParam(reason)

#    def demag(self):
#        print 'demag hier'

    def demag(self):
        global active_ps_list, relee_sign, relee_plus, relee_minus
        print 'starting demagnetesization of all active magnets'
        ps_heightV = []
        for ps in active_ps_list:
            ps_heightV.append( float(self.getParam('%s:volt'%ps_to_prefix[ps])) )

        ''' do demag in steps '''
        sleep_sec = self.getParam('demag:sleep')
        steps = self.getParam('demag:steps')
        zps_lock.acquire()
        for count in range(1,steps):
            s = SockConn(HOST, PORT)
            if count%2 > 0:
                self.setParam('zps:relee:sign', 0)    # minus
                s.command('INST:NSEL %d\n:VOLT %0.3f'%(ps_relee.NR,relee_minus))
                volt_all = '%s '%relee_minus
                #ps_relee.setVolt(relee_minus)
                self.setParam('zps:relee:volt', relee_minus)
                relee_sign=-1.0
            else:
                self.setParam('zps:relee:sign', 1)    # plus
                s.command('INST:NSEL %d\n:VOLT %0.3f'%(ps_relee.NR,relee_plus))
                volt_all = '%s '%relee_plus
                #ps_relee.setVolt(relee_plus)
                self.setParam('zps:relee:volt', relee_plus)
                relee_sign=1.0

            for i in range(0,len(active_ps_list)):
                volts = round(ps_heightV[i]-count*ps_heightV[i]/steps,3)
                ps = active_ps_list[i]
                s.command('INST:NSEL %d\n:VOLT %0.3f'%(ps.NR,volts))
                #ps.setVolt(volts)
                #print '%d %f (ps:%d %f)' %(count,volts,i,ps_heightV[i])
                self.setParam('%s:volt'%ps_to_prefix[ps], volts)
                self.setParam('%s:volt'%ps_to_magnet[ps], ps.magn_sign*relee_sign*volts)
                curr = s.question(':measure:current?')
                self.setParam('%s:curr'%ps_to_prefix[ps], curr )
                self.setParam('%s:curr'%ps_to_magnet[ps], ps.magn_sign*relee_sign*float(curr) )

            # refresh ps_all_volt and ps_all_curr
            curr = s.question('INST:NSEL %d\n:measure:current?'%ps_relee.NR)
            curr_all = '%s '%curr
            for ps in ps_list:
                if ps == ps_relee: continue
                if ps in active_ps_list:
                    volt_all += '%s '%self.getParam('%s:volt'%ps_to_prefix[ps])
                    curr_all += '%s '%self.getParam('%s:curr'%ps_to_prefix[ps])
                else:
                    volt_all += 'None '
                    curr_all += 'None '
            volt_all += '\n'
            curr_all += '\n'
            self.setParam('ps_volt_all',volt_all)
            self.setParam('ps_curr_all',curr_all)

            s.__del__()
            self.updatePVs()
            time.sleep(sleep_sec)

        s = SockConn(HOST, PORT)
        ''' set all ps to 0 '''
        for ps in active_ps_list:
            s.command('INST:NSEL %d\n:VOLT 0'%ps.NR)
            #ps.setVolt(0)
            #print '%d %f (ps:%d %f)' %(count,volts,i,ps_heightV[i])

        ''' set relee to 0 '''
        s.command('INST:NSEL %d\n:VOLT 0'%ps_relee.NR)
        #ps_relee.setVolt(0)

        s.__del__()
        zps_lock.release()
        self.setParam('demag',0)
        self.updatePVs()


    def write(self, reason, value):
        global relee_plus, relee_minus, relee_sign
        #TODO read status
        status = True
        ps = None

        if reason=='demag':
            self.thred_demag_id = thread.start_new_thread(self.demag,())
            return True

        if 'relee' in reason : ps = ps_relee
        elif reason in record_to_ps: ps = record_to_ps[reason]
        if ps==None: return False

        zps_lock.acquire()
        if ps == ps_relee and reason == 'zps:relee:volt':
            if float(value) == relee_plus:
                self.setParam('zps:relee:sign', 1)    # plus
                ps.setVolt(relee_plus)
                self.setParam(reason, relee_plus)
                relee_sign=1.0
                #print 'PLUS'
                status=True
            elif float(value) == relee_minus:
                self.setParam('zps:relee:sign', 0)    # minus
                ps.setVolt(relee_minus)
                self.setParam(reason, relee_minus)
                relee_sign=-1.0
                #print 'MINUS'
                status=True
            else:
                status=False
            # update all magnet signs
            for ps in ps_to_magnet:
                self.setParam('%s:volt'%ps_to_magnet[ps], ps.magn_sign*relee_sign*abs(self.getParam('%s:volt'%ps_to_magnet[ps])))
                self.setParam('%s:curr'%ps_to_magnet[ps], ps.magn_sign*relee_sign*abs(self.getParam('%s:curr'%ps_to_magnet[ps])))
            zps_lock.release()
            return status
        else:
            if 'volt' in reason: ps.setVolt(value)
            elif 'curr' in reason: ps.setCurr(value)
            zps_lock.release()

        if status:
            self.setParam(reason, value)

        # update magnet record
        if ps in ps_to_magnet:
            if 'volt' in reason: self.setParam('%s:volt'%ps_to_magnet[ps], ps.magn_sign*relee_sign*value)
            elif 'curr' in reason: self.setParam('%s:curr'%ps_to_magnet[ps], ps.magn_sign*relee_sign*value)
        return status

    def continues_polling(self):
        global alive, ps_list, active_ps_list, relee_sign, relee_plus, relee_minus
        while alive:
            try:
                s = SockConn(HOST, PORT)
                zps_lock.acquire()
                #while zps_conn == True: time.sleep(0.1)
                # poll relee
                volt = s.question('INST:NSEL %d\n:measure:voltage?'%ps_relee.NR)
                volt_all = '%s '%volt
                self.setParam('zps:relee:volt', volt)
                curr = s.question(':measure:current?')
                curr_all = '%s '%curr
                self.setParam('zps:relee:curr', curr)
                if (round(float(volt))==relee_plus): relee_sign=1.0
                elif (round(float(volt))==relee_minus): relee_sign=-1.0
                # poll other ps
                for ps in active_ps_list:
                    volt = s.question('INST:NSEL %d\n:measure:voltage?'%ps.NR)
                    #volt_all += '%s '%volt
                    self.setParam('%s:volt'%ps_to_prefix[ps], volt)
                    self.setParam('%s:volt'%ps_to_magnet[ps], ps.magn_sign*relee_sign*float(volt))

                    curr = s.question(':measure:current?')
                    #curr_all += '%s '%curr
                    self.setParam('%s:curr'%ps_to_prefix[ps], curr)
                    self.setParam('%s:curr'%ps_to_magnet[ps], ps.magn_sign*relee_sign*float(curr))

                # refresh ps_all_volt and ps_all_curr
                for ps in ps_list:
                    if ps == ps_relee: continue
                    if ps in active_ps_list:
                        volt_all += '%s '%self.getParam('%s:volt'%ps_to_prefix[ps])
                        curr_all += '%s '%self.getParam('%s:curr'%ps_to_prefix[ps])
                    else:
                        volt_all += 'None '
                        curr_all += 'None '
                volt_all += '\n'
                curr_all += '\n'
                self.setParam('ps_volt_all',volt_all)
                self.setParam('ps_curr_all',curr_all)

                s.__del__()
                zps_lock.release()
            except Exception as e:
                print 'Err',e
                alive=False

            self.updatePVs()
            time.sleep(zps_poling_time)


if __name__ == '__main__':


    server= SimpleServer()
    server.initAccessSecurityFile('security.as', P=prefix)
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while alive:
        try:
            server.process(0.1)
        except KeyboardInterrupt:
            print " Bye"
            sys.exit()
