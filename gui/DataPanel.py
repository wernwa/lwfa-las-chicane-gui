# -*- coding: utf-8 -*-
#
#   DataPanel class. A panel for displaying the current pvs of all magnets
#
#
#   author: Watler Werner
#   email: wernwa@gmail.com


import wx
import wx.lib.newevent
from epics import PV
import epics
from Experiment import *
import threading
import time
import traceback
import numpy

chicane_type=None





class DataPanel(wx.Panel):

    q1_volt='##.##'
    q2_volt='##.##'
    q3_volt='##.##'
    q4_volt='##.##'
    q5_volt='##.##'
    q6_volt='##.##'
    q7_volt='##.##'
    d1_volt='##.##'
    d2_volt='##.##'

    q1_curr='##.##'
    q2_curr='##.##'
    q3_curr='##.##'
    q4_curr='##.##'
    q5_curr='##.##'
    q6_curr='##.##'
    q7_curr='##.##'
    d1_curr='##.##'
    d2_curr='##.##'

    q1_temp='##.##'
    q2_temp='##.##'
    q3_temp='##.##'
    q4_temp='##.##'
    q5_temp='##.##'
    q6_temp='##.##'
    q7_temp='##.##'
    d1_temp='##.##'
    d2_temp='##.##'

    st_quad1 = None
    b_demag = None

    ##
    ##  Constructor
    ##
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        #panel2 = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)

        self.start_app_time = time.time()
        panel = self

        #hbox = wx.BoxSizer(wx.HORIZONTAL)


        ##imageFile = 'pics/schikane_alpha.png'
        #imageFile = 'pics/Quadruplett_2_pos_scaled.png'
        #image = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)
        ##image = image.Scale(0.5,0.5)
        #png = image.ConvertToBitmap()
        #imagewx = wx.StaticBitmap(self, -1, png, (5, 5), (png.GetWidth(), png.GetHeight()))
        #hbox.Add(imagewx, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        dy=10
        qy=20

        self.lpos_triplett = {
            'q1': {'x':50,'y':qy},
            'q2': {'x':150,'y':qy},
            'q3': {'x':250,'y':qy},
            'd1': {'x':350,'y':dy},
            'q4': {'x':450,'y':qy},
            'q5': {'x':550,'y':qy},
            'q6': {'x':650,'y':qy},
            'd2': {'x':750,'y':dy},
            'q7': {'x':850,'y':qy},
        }
        self.lpos_quadruplett = {
            'q1': {'x':50,'y':qy},
            'q2': {'x':150,'y':qy},
            'q3': {'x':250,'y':qy},
            'q4': {'x':350,'y':qy},
            'd1': {'x':450,'y':dy},
            'q5': {'x':550,'y':qy},
            'q6': {'x':650,'y':qy},
            'q7': {'x':750,'y':qy},
            'd2': {'x':850,'y':dy},
        }
        global chicane_type
        chicane_type = sys.argv[1]
        if chicane_type=='quadruplett':
            lpos = self.lpos_quadruplett
        elif chicane_type=='triplett':
            lpos = self.lpos_triplett
        else:
            print 'TODO'
            exit(0)

        text_color_quad = (50,30,30)
        text_color_dipol = (10,10,120)

        self.text_color_normal = (50,30,30)
        self.text_color_heigh = (200,30,30)
        self.text_color_hihi = (255,30,30)


        self.font_bold = wx.Font(10, wx.DEFAULT,  wx.NORMAL, wx.BOLD)
        self.font_normal = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

        def magnet_selected(event,title,magn,st):
            parent.nb.SetSelection(1)
            #print 'notebook tab 1 selection %s'%title
            #st = event.GetEventObject()
            if self.st_selected != None:
                self.st_selected.SetFont(self.font_normal)
            st.SetFont(self.font_bold)
            self.st_selected = st
            parent.tabMagnProperties.magnet_selected(event,title,magn)

        image_disconn = wx.Image('pics/disconnected.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        image_green = wx.Image('pics/green-status.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        image_gray = wx.Image('pics/gray-status.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        self.image_thermo_0 = wx.Image('pics/thermometer_0.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.image_thermo_20 = wx.Image('pics/thermometer_20.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.image_thermo_50 = wx.Image('pics/thermometer_50.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.image_thermo_70 = wx.Image('pics/thermometer_70.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.image_thermo_100 = wx.Image('pics/thermometer_100.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        # toggle power supply output on/off
        def ps_onoff(event,magnet,button,magn_name):
            if magnet.ps.online.conn==False:
                button.SetBitmapLabel(image_disconn)
                return

            #online = magnet.ps.online.get()
            online = magnet.ps.online.value
            if online == 0: return

            #output = magnet.ps.output.get()
            output = magnet.ps.output.value
            nr = magnet.ps.NR
            info = 'magnet '+magn_name+'\n'+'power supply Nr '+nr+'\n'

            if output == 0:
                dlg = wx.MessageDialog(self, info+'Do you want to turn the output on?', 'TURN OUTPUT ON?',
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

                if dlg.ShowModal() == wx.ID_YES:
                    magnet.ps.output.put(1)
                    #button.SetBitmapLabel(image_green)
                    #button.Refresh()

            elif output == 1:
                dlg = wx.MessageDialog(self, info+'Do you want to turn the output off?', 'TURN OUTPUT OFF?',
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

                if dlg.ShowModal() == wx.ID_YES:
                    magnet.ps.output.put(0)
                    #button.SetBitmapLabel(image_gray)
                    #button.Refresh()

        def ps_online(magnet,button):
            if magnet.ps.online.conn==False:
                button.SetBitmapLabel(image_disconn)
                return
            #online = magnet.ps.online.get()
            online = magnet.ps.online.value
            if online == 0:
                button.SetBitmapLabel(image_disconn)
            elif online == 1:
                #output = magnet.ps.output.get()
                output = magnet.ps.output.value
                if output == 0: button.SetBitmapLabel(image_gray)
                elif output == 1: button.SetBitmapLabel(image_green)
		button.Refresh()


        # there are min 9 magnets gui elements to initialize
        # this function returns a wx.StaticText and wx.BitmapButton
        def init_magnet_labels(magnet, magn_name=None, position=None):
            static_text = wx.StaticText(label="%s\n#.##V\n#.##A\n##°C"%magn_name,  parent=panel, pos=wx.Point(position[0],position[1]))
            static_text.Bind(wx.EVT_LEFT_DOWN, lambda event: magnet_selected(event, magn_name, magnet, static_text))
            static_text.SetForegroundColour(text_color_quad)
            button_ps = wx.BitmapButton(panel, id=-1, bitmap=image_disconn,
                    pos=wx.Point(position[0]+20,position[1]+90), size =(image_disconn.GetWidth()+10, image_disconn.GetHeight()+10))
            thermo = wx.StaticBitmap(panel, wx.ID_ANY,
                    self.image_thermo_0,
                    pos=wx.Point(position[0]+50,position[1]+90),
                    size =(self.image_thermo_0.GetWidth(), self.image_thermo_0.GetHeight()))
            button_ps.Bind(wx.EVT_BUTTON, lambda event: ps_onoff(event,magnet,button_ps,magn_name))
            # tmp comment until the error is found
            magnet.ps.online.add_callback(lambda **kw: ps_online(magnet,button_ps))
            magnet.ps.output.add_callback(lambda **kw: ps_online(magnet,button_ps))
            magnet.ps.online.connection_callbacks.append(lambda **kw: ps_online(magnet,button_ps))
            magnet.ps.output.connection_callbacks.append(lambda **kw: ps_online(magnet,button_ps))
            ps_online(magnet,button_ps)

            return static_text, button_ps, thermo

        # init magnet labels
        self.st_quad1, self.bsp_quad1, self.thermo_quad1= init_magnet_labels(mquad1,magn_name='Quadrupol 1',position=(lpos['q1']['x'],lpos['q1']['y']))
        self.st_quad2, self.bsp_quad2, self.thermo_quad2= init_magnet_labels(mquad2,magn_name='Quadrupol 2',position=(lpos['q2']['x'],lpos['q2']['y']))
        self.st_quad3, self.bsp_quad3, self.thermo_quad3= init_magnet_labels(mquad3,magn_name='Quadrupol 3',position=(lpos['q3']['x'],lpos['q3']['y']))
        self.st_quad4, self.bsp_quad4, self.thermo_quad4= init_magnet_labels(mquad4,magn_name='Quadrupol 4',position=(lpos['q4']['x'],lpos['q4']['y']))
        self.st_quad5, self.bsp_quad5, self.thermo_quad5= init_magnet_labels(mquad5,magn_name='Quadrupol 5',position=(lpos['q5']['x'],lpos['q5']['y']))
        self.st_quad6, self.bsp_quad6, self.thermo_quad6= init_magnet_labels(mquad6,magn_name='Quadrupol 6',position=(lpos['q6']['x'],lpos['q6']['y']))

        self.st_quad7=None
        self.thermo_quad7=None
        if chicane_type=='quadruplett':
            self.st_quad7, self.bsp_quad7, self.thermo_quad7 = init_magnet_labels(mquad7,magn_name='Quadrupol 7',position=(lpos['q7']['x'],lpos['q7']['y']))

        self.st_dipol1, self.bsp_dipol1, self.thermo_dipol1 = init_magnet_labels(mdipol1,magn_name='Dipol 1',position=(lpos['d1']['x'],lpos['d1']['y']))
        self.st_dipol2, self.bsp_dipol2, self.thermo_dipol2 = init_magnet_labels(mdipol2,magn_name='Dipol 2',position=(lpos['d2']['x'],lpos['d2']['y']))

        ##
        ## switchbox
        ##
        def switchbox_onoff(event,button):
            if switchbox.conn==False: return
            output = switchbox.get()
            #output = switchbox.value
            if output == 0:
                info='Please note, that the powersupplies can have hight current in memory.\n'
                info+='By turning on the switchbox, all powersupplies are switched on at once.\n\n'
                dlg = wx.MessageDialog(self, info+'Do you want to turn the switchbox on?', 'TURN SWITHBOX ON?',
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

                if dlg.ShowModal() == wx.ID_YES:
                    switchbox.put(1)
                    button.SetBitmapLabel(image_green)
                    button.Refresh()

            elif output == 1:
                info = 'Attention! Without cycling, turning off all of the powersupplies at once can damage the magnets!\n'
                info += 'Click yes if you know what you are doing.\n\n'
                dlg = wx.MessageDialog(self, info+'Do you realy want to turn the switchbox off?', 'TURN SWITCHBOX OFF?',
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

                if dlg.ShowModal() == wx.ID_YES:
                    switchbox.put(0)
                    button.SetBitmapLabel(image_gray)
                    button.Refresh()

        def switchbox_online(button):
            if switchbox.conn == False:
                button.SetBitmapLabel(image_disconn)
                button.Refresh()
            else:
                output = switchbox.get()
                #output = switchbox.value
                if output == 0: button.SetBitmapLabel(image_gray)
                elif output == 1: button.SetBitmapLabel(image_green)
                button.Refresh()

        static_text = wx.StaticText(label="switchbox",  parent=panel, pos=wx.Point(lpos['d2']['x']+100,lpos['d2']['y']))
        button_ps = wx.BitmapButton(panel, id=-1, bitmap=image_disconn,
                    pos=wx.Point(lpos['d2']['x']+100,lpos['d2']['y']+20), size =(image_disconn.GetWidth()+10, image_disconn.GetHeight()+10))
        button_ps.Bind(wx.EVT_BUTTON, lambda event: switchbox_onoff(event,button_ps))
        switchbox.add_callback(lambda **kw: switchbox_online(button_ps))
        switchbox.connection_callbacks.append(lambda **kw: switchbox_online(button_ps))
        switchbox_online(button_ps)


        ##
        ## relee
        ##
        def relee_plus_minus(event,button):
            if relee_sign.conn==False: return

            sign = relee_sign.get()

            #print 'current sign',sign
            relee_volt = 0
            if sign == 1: relee_volt = 24

            if sign==1: sign_str='+'
            else: sign_str = '-'

            # maybe start demag here ??

            #print 'setting relee to %s'%sign_str
            relee.Volt.put(relee_volt)



        def relee_state(button):
            if relee_sign.conn == False:
                button.SetLabel('?')
                button.Refresh()
            else:
                sign = relee_sign.get()
                if sign == 0: button.SetLabel('-')
                elif sign == 1: button.SetLabel('+')
                button.Refresh()

        relee_label = '+'
        if relee_sign.conn==True:
            sign = relee_sign.get()
            if sign==0: relee_label = '-'
        static_text = wx.StaticText(label="relee",  parent=panel, pos=wx.Point(lpos['d2']['x']+100,lpos['d2']['y']+50))
        button_relee = wx.Button(self, id=-1, label=relee_label,pos=wx.Point(lpos['d2']['x']+100,lpos['d2']['y']+70), size=(30, 30))
        button_relee.Bind(wx.EVT_BUTTON, lambda event: relee_plus_minus(event,button_relee))
        relee_sign.add_callback(lambda **kw: relee_state(button_relee))
        relee_sign.connection_callbacks.append(lambda **kw: relee_state(button_relee))
        relee_state(button_relee)



        self.st_selected = self.st_quad1
        self.st_selected.SetFont(self.font_bold)



        self.st_arr = [self.st_quad1, self.st_quad2, self.st_quad3, self.st_quad4, self.st_quad5, self.st_quad6, self.st_quad7, self.st_dipol1, self.st_dipol2]
        self.thermo_arr = [self.thermo_quad1, self.thermo_quad2, self.thermo_quad3, self.thermo_quad4, self.thermo_quad5, self.thermo_quad6, self.thermo_quad7, self.thermo_dipol1, self.thermo_dipol2]

        if chicane_type=='quadruplett':
            self.st_text_color_arr = [text_color_quad, text_color_quad, text_color_quad, text_color_quad,
                            text_color_dipol,
                            text_color_quad, text_color_quad, text_color_quad,
                            text_color_dipol]
        else:
            self.st_text_color_arr = [text_color_quad, text_color_quad, text_color_quad, text_color_quad,
                        text_color_dipol,
                        text_color_quad, text_color_quad, text_color_quad,
                        text_color_dipol]

        #self.b_demag = wx.Button(parent=panel, pos=wx.Point(50, 490), label="Demag")
        #self.b_demag.Bind(wx.EVT_BUTTON, self.OnDemag)
        #panel.SetSizer(hbox)

        #value = magn_volt_all.get()
        if magn_volt_all.conn==True:
            value = magn_volt_all.get()
            arr = value.tostring().split(' ')
            self.q1_volt=self.get_num_or_dash(arr[0])
            self.q2_volt=self.get_num_or_dash(arr[1])
            self.q3_volt=self.get_num_or_dash(arr[2])
            self.q4_volt=self.get_num_or_dash(arr[3])
            self.q5_volt=self.get_num_or_dash(arr[4])
            self.q6_volt=self.get_num_or_dash(arr[5])
            self.q7_volt=self.get_num_or_dash(arr[6])
            self.d1_volt=self.get_num_or_dash(arr[7])
            self.d2_volt=self.get_num_or_dash(arr[8])
        else:
            self.q1_volt='##.##'
            self.q2_volt='##.##'
            self.q3_volt='##.##'
            self.q4_volt='##.##'
            self.q5_volt='##.##'
            self.q6_volt='##.##'
            self.q7_volt='##.##'
            self.d1_volt='##.##'
            self.d2_volt='##.##'


        #value = magn_curr_all.get()
        if magn_curr_all.conn==True:
            value = magn_curr_all.get()
            arr = value.tostring().split(' ')
            self.q1_curr=self.get_num_or_dash(arr[0])
            self.q2_curr=self.get_num_or_dash(arr[1])
            self.q3_curr=self.get_num_or_dash(arr[2])
            self.q4_curr=self.get_num_or_dash(arr[3])
            self.q5_curr=self.get_num_or_dash(arr[4])
            self.q6_curr=self.get_num_or_dash(arr[5])
            self.q7_curr=self.get_num_or_dash(arr[6])
            self.d1_curr=self.get_num_or_dash(arr[7])
            self.d2_curr=self.get_num_or_dash(arr[8])
        else:
            self.q1_curr='##.##'
            self.q2_curr='##.##'
            self.q3_curr='##.##'
            self.q4_curr='##.##'
            self.q5_curr='##.##'
            self.q6_curr='##.##'
            self.q7_curr='##.##'
            self.d1_curr='##.##'
            self.d2_curr='##.##'

        self.q1_k=self.get_num_of_k_or_dash(mquad1,self.q1_curr)
        self.q2_k=self.get_num_of_k_or_dash(mquad2,self.q2_curr)
        self.q3_k=self.get_num_of_k_or_dash(mquad3,self.q3_curr)
        self.q4_k=self.get_num_of_k_or_dash(mquad4,self.q4_curr)
        self.q5_k=self.get_num_of_k_or_dash(mquad5,self.q5_curr)
        self.q6_k=self.get_num_of_k_or_dash(mquad6,self.q6_curr)
        self.q7_k=self.get_num_of_k_or_dash(mquad7,self.q7_curr)
        self.d1_alpha=self.get_num_of_k_or_dash(mdipol1,self.d1_curr)
        self.d2_alpha=self.get_num_of_k_or_dash(mdipol2,self.d2_curr)


        #value = temp_all.get()
        if temp_all.conn==True:
            value = temp_all.get()
            arr = value.tostring().split(' ')
            self.q1_temp=self.get_num_or_dash(arr[0])
            self.q2_temp=self.get_num_or_dash(arr[1])
            self.q3_temp=self.get_num_or_dash(arr[2])
            self.q4_temp=self.get_num_or_dash(arr[3])
            self.q5_temp=self.get_num_or_dash(arr[4])
            self.q6_temp=self.get_num_or_dash(arr[5])
            self.q7_temp=self.get_num_or_dash(arr[6])
            self.d1_temp=self.get_num_or_dash(arr[7])
            self.d2_temp=self.get_num_or_dash(arr[8])
        else:
            self.q1_temp='##.##'
            self.q2_temp='##.##'
            self.q3_temp='##.##'
            self.q4_temp='##.##'
            self.q5_temp='##.##'
            self.q6_temp='##.##'
            self.q7_temp='##.##'
            self.d1_temp='##.##'
            self.d2_temp='##.##'

        self.temp_all_arr = [self.q1_temp,self.q3_temp,self.q3_temp,self.q4_temp,self.q5_temp,self.q6_temp,self.q7_temp,self.d1_temp,self.d2_temp]
        self.temp_heigh = 70
        self.temp_hihi = 95
        self.temp_cnt = 9


        # refresh labels
        self.alive=True
        def refresh_labels():
            # TODO Thread beim beenden beenden
            while self.alive:
                #self.call_routine_over_event( self.changeLables )
                self.call_routine_over_event( self.labels_update )
                time.sleep(0.5)
        thread=threading.Thread(target=refresh_labels,args=())
        thread.start()

        time.sleep(0.1)
        temp_all.add_callback(self.onPVChanges)
        magn_curr_all.add_callback(self.onPVChanges)
        magn_volt_all.add_callback(self.onPVChanges)

        temp_all.connection_callbacks.append(self.onConnectionChange)
        magn_curr_all.connection_callbacks.append(self.onConnectionChange)
        magn_volt_all.connection_callbacks.append(self.onConnectionChange)

    ##
    ##  if a connection of a pv changes, display it
    ##
    def onConnectionChange(self, pvname=None, conn= None, **kws):
        #sys.stdout.write('PV connection status changed: %s %s\n' % (pvname,  repr(conn)))
        #sys.stdout.flush()

        if conn==True: return

        if temp_all.pvname==pvname:
            self.q1_temp='##.##'
            self.q2_temp='##.##'
            self.q3_temp='##.##'
            self.q4_temp='##.##'
            self.q5_temp='##.##'
            self.q6_temp='##.##'
            self.q7_temp='##.##'
            self.d1_temp='##.##'
            self.d2_temp='##.##'
        elif magn_volt_all.pvname==pvname:
            self.q1_volt='##.##'
            self.q2_volt='##.##'
            self.q3_volt='##.##'
            self.q4_volt='##.##'
            self.q5_volt='##.##'
            self.q6_volt='##.##'
            self.q7_volt='##.##'
            self.d1_volt='##.##'
            self.d2_volt='##.##'
        elif magn_curr_all.pvname==pvname:
            self.q1_curr='##.##'
            self.q2_curr='##.##'
            self.q3_curr='##.##'
            self.q4_curr='##.##'
            self.q5_curr='##.##'
            self.q6_curr='##.##'
            self.q7_curr='##.##'
            self.d1_curr='##.##'
            self.d2_curr='##.##'
            self.q1_k='##.##'
            self.q2_k='##.##'
            self.q3_k='##.##'
            self.q4_k='##.##'
            self.q5_k='##.##'
            self.q6_k='##.##'
            self.q7_k='##.##'
            self.d1_k='##.##'
            self.d2_k='##.##'


    def __del__(self):
        self.alive=False
        time.sleep(0.5)

    def OnDemag(self, event):
        def demagThread():
            self.b_demag.Enable(False)
            demag()
            self.b_demag.Enable(True)

        thread = threading.Thread(target=demagThread, args=())
        thread.start()


    ##
    ##  updatets the gui labes called over the call_routine_over_event method
    ##
    def labels_update(self,evt):

        # test for heigh temperature
        for i in range(0,self.temp_cnt):
            if self.st_arr[i]==None or self.temp_all_arr[i]==None:
                continue
            t_unknown = self.temp_all_arr[i]
            if t_unknown==None or t_unknown=='##.##':
                self.thermo_arr[i].SetBitmap(self.image_thermo_0)
                continue

            t = float(t_unknown)

            # StaticText Background
            if t < self.temp_heigh:
                self.st_arr[i].SetForegroundColour(self.text_color_normal)
            if self.temp_heigh <= t and t < self.temp_hihi:
                #print self.st_arr[i]
                self.st_arr[i].SetForegroundColour(self.text_color_heigh)
                #print 'temperature heigh %0.3f q%d'%(t,(i+1))
            elif t >= self.temp_hihi:
                #print 'temperature too heigh for q%d, please start demag!!!'%(i+1)
                self.st_arr[i].SetForegroundColour(self.text_color_hihi)

            #StaticBitmap Thermometer
            if t < 20: self.thermo_arr[i].SetBitmap(self.image_thermo_20)
            elif t < 50: self.thermo_arr[i].SetBitmap(self.image_thermo_50)
            elif t < 70: self.thermo_arr[i].SetBitmap(self.image_thermo_70)
            elif t >= 70: self.thermo_arr[i].SetBitmap(self.image_thermo_100)



        global chicane_type, mquad1, mquad2, mquad3, mquad4, mquad5, mquad6, mquad7, mdipol1, mdipol2
        self.st_quad1.SetLabel("Quadrupol 1\n%s V \n%s A\n%s [1/m]\n%s °C" %(self.q1_volt,self.q1_curr,self.q1_k,self.q1_temp))
        self.st_quad2.SetLabel("Quadrupol 2\n%s V \n%s A\n%s [1/m]\n%s °C" %(self.q2_volt,self.q2_curr,self.q2_k,self.q2_temp))
        self.st_quad3.SetLabel("Quadrupol 3\n%s V \n%s A\n%s [1/m]\n%s °C" %(self.q3_volt,self.q3_curr,self.q3_k,self.q3_temp))
        self.st_quad4.SetLabel("Quadrupol 4\n%s V \n%s A\n%s [1/m]\n%s °C" %(self.q4_volt,self.q4_curr,self.q4_k,self.q4_temp))
        self.st_quad5.SetLabel("Quadrupol 5\n%s V \n%s A\n%s [1/m]\n%s °C" %(self.q5_volt,self.q5_curr,self.q5_k,self.q5_temp))
        self.st_quad6.SetLabel("Quadrupol 6\n%s V \n%s A\n%s [1/m]\n%s °C" %(self.q6_volt,self.q6_curr,self.q6_k,self.q6_temp))
        if chicane_type=='quadruplett':
            self.st_quad7.SetLabel("Quadrupol 7\n%s V \n%s A\n%s [1/m]\n%s °C" %(self.q7_volt,self.q7_curr,self.q7_k,self.q7_temp))
        self.st_dipol1.SetLabel("Dipol 1\n%s V \n%s A\n%s [mrad]\n%s °C" %(self.d1_volt,self.d1_curr,self.d1_alpha,self.d1_temp))
        self.st_dipol2.SetLabel("Dipol 2\n%s V \n%s A\n%s [mrad]\n%s °C" %(self.d2_volt,self.d2_curr,self.d2_alpha,self.d2_temp))


    ##
    ## for the convertion from pv-array,
    ## display a number or if None the dashes
    ##
    def get_num_or_dash(self,obj):
        if obj == 'None' or obj == None: return '##.##'
        else:
            try:
                num = float(obj)
            except Exception as e:
                print traceback.format_exc()

            return num
    ##
    ## for spline interpolation
    ## display a number or if spline out of range
    ##
    def get_num_of_k_or_dash(self,magn,curr):
        if type(curr)==float:
            try:
                num = magn.get_k(curr)
            except Exception as e:
                #print traceback.format_exc()
                num = '##.##'
        else: num = '##.##'

        return num


    ##
    ## save changes of pv to variables
    ##
    def onPVChanges(self, pvname=None, value=None, timestamp=None, **kw):

        global mquad1, mquad2, mquad3, mquad4, mquad5, mquad6, mquad7, mdipol1, mdipol2

        marr = [mquad1, mquad2, mquad3, mquad4, mquad5, mquad6, mquad7, mdipol1, mdipol2]
        q_volt_arr = [self.q1_volt, self.q2_volt, self.q3_volt, self.q4_volt, self.q5_volt, self.q6_volt, self.q7_volt,
                    self.d1_volt, self.d2_volt ]

        if 'online' in pvname:
            print pvname

        if pvname==temp_all.pvname:
            arr = value.tostring().split(' ')
            self.temp_all_arr = arr[:self.temp_cnt]
            try:
                self.q1_temp=self.get_num_or_dash(arr[0])
                self.q2_temp=self.get_num_or_dash(arr[1])
                self.q3_temp=self.get_num_or_dash(arr[2])
                self.q4_temp=self.get_num_or_dash(arr[3])
                self.q5_temp=self.get_num_or_dash(arr[4])
                self.q6_temp=self.get_num_or_dash(arr[5])
                self.q7_temp=self.get_num_or_dash(arr[6])
                self.d1_temp=self.get_num_or_dash(arr[7])
                self.d2_temp=self.get_num_or_dash(arr[8])


                # fill in the numpy arrays for StripChart visualisation
                for i in range(0,len(marr)):
                    if arr[i]=='None': continue
                    marr[i].strip_chart_temp.append(float(arr[i]))
                    #print 'start_app_time',type(self.start_app_time)
                    #print 'temp_all',type(temp_all)
                    # strange Error for temp_all.timestamp=NoneType
                    #marr[i].strip_chart_temp_time.append(temp_all.timestamp-self.start_app_time)
                    #marr[i].strip_chart_temp_time.append(time.time()-self.start_app_time)
                    marr[i].strip_chart_temp_time.append(time.time())


            except Exception as e:
                #print 'temp_all: ',e
                print traceback.format_exc()

        elif pvname==magn_volt_all.pvname:
            #print type(value)
            arr = value.tostring().split(' ')
            #print 'volt arr',arr
            try:
                self.q1_volt=self.get_num_or_dash(arr[0])
                self.q2_volt=self.get_num_or_dash(arr[1])
                self.q3_volt=self.get_num_or_dash(arr[2])
                self.q4_volt=self.get_num_or_dash(arr[3])
                self.q5_volt=self.get_num_or_dash(arr[4])
                self.q6_volt=self.get_num_or_dash(arr[5])
                self.q7_volt=self.get_num_or_dash(arr[6])
                self.d1_volt=self.get_num_or_dash(arr[7])
                self.d2_volt=self.get_num_or_dash(arr[8])

                # fill in the numpy arrays for StripChart visualisation
                for i in range(0,len(marr)):
                    if arr[i]=='None': continue
                    marr[i].strip_chart_volt.append(float(arr[i]))
                    marr[i].strip_chart_volt_time.append(time.time()-self.start_app_time)

            except Exception as e:
                #print 'volt_all:',e
                print traceback.format_exc()

        elif pvname==magn_curr_all.pvname:
            arr = value.tostring().split(' ')
            try:
                self.q1_curr=self.get_num_or_dash(arr[0])
                self.q2_curr=self.get_num_or_dash(arr[1])
                self.q3_curr=self.get_num_or_dash(arr[2])
                self.q4_curr=self.get_num_or_dash(arr[3])
                self.q5_curr=self.get_num_or_dash(arr[4])
                self.q6_curr=self.get_num_or_dash(arr[5])
                self.q7_curr=self.get_num_or_dash(arr[6])
                self.d1_curr=self.get_num_or_dash(arr[7])
                self.d2_curr=self.get_num_or_dash(arr[8])


                self.q1_k=self.get_num_of_k_or_dash(mquad1,self.q1_curr)
                self.q2_k=self.get_num_of_k_or_dash(mquad2,self.q2_curr)
                self.q3_k=self.get_num_of_k_or_dash(mquad3,self.q3_curr)
                self.q4_k=self.get_num_of_k_or_dash(mquad4,self.q4_curr)
                self.q5_k=self.get_num_of_k_or_dash(mquad5,self.q5_curr)
                self.q6_k=self.get_num_of_k_or_dash(mquad6,self.q6_curr)
                self.q7_k=self.get_num_of_k_or_dash(mquad7,self.q7_curr)
                self.d1_alpha=self.get_num_of_k_or_dash(mdipol1,self.d1_curr)
                self.d2_alpha=self.get_num_of_k_or_dash(mdipol2,self.d2_curr)


                # fill in the numpy arrays for StripChart visualisation
                for i in range(0,len(marr)):
                    if arr[i]=='None': continue
                    marr[i].strip_chart_curr.append(float(arr[i]))
                    marr[i].strip_chart_curr_time.append(time.time()-self.start_app_time)

            except Exception as e:
                #print 'temp_all:',e
                print traceback.format_exc()

    ##
    ## call the main thread throgh messaging for painting the gui
    ##
    SomeNewEvent=None
    def call_routine_over_event(self, handler):

        if self.SomeNewEvent==None:
            self.SomeNewEvent, self.EVT_SOME_NEW_EVENT = wx.lib.newevent.NewEvent()
            self.Bind(self.EVT_SOME_NEW_EVENT, handler)

            # Create the event
            self.evt = self.SomeNewEvent()


        # Post the event
        wx.PostEvent(self, self.evt)


    def OnChangeEnergy(self,energy):
        global E
        E=energy
        self.q1_k=self.get_num_of_k_or_dash(mquad1,self.q1_curr)
        self.q2_k=self.get_num_of_k_or_dash(mquad2,self.q2_curr)
        self.q3_k=self.get_num_of_k_or_dash(mquad3,self.q3_curr)
        self.q4_k=self.get_num_of_k_or_dash(mquad4,self.q4_curr)
        self.q5_k=self.get_num_of_k_or_dash(mquad5,self.q5_curr)
        self.q6_k=self.get_num_of_k_or_dash(mquad6,self.q6_curr)
        self.q7_k=self.get_num_of_k_or_dash(mquad7,self.q7_curr)
        self.d1_alpha=self.get_num_of_k_or_dash(mdipol1,self.d1_curr)
        self.d2_alpha=self.get_num_of_k_or_dash(mdipol2,self.d2_curr)

        self.call_routine_over_event( self.labels_update )
