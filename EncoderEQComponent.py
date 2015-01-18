# http://remotescripts.blogspot.com
"""
Customized APC40 control surface script
Copyright (C) 2010 Hanz Petrov <hanz.petrov@gmail.com>
Additional modification for Ableton Live 9 - Fabrizio Poce 2013 - <http://www.fabriziopoce.com/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# emacs-mode: -*- python-*-
# http://remotescripts.blogspot.com

import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.MixerComponent import MixerComponent 

from _Generic.Devices import *
EQ_DEVICES = {'Eq8': {'Gains': [ ('%i Gain A' % (index + 1)) for index in range(8) ],
                      'Cuts': [ ('%i Filter On A' % (index + 1)) for index in range(8) ]},
              'FilterEQ3': {'Gains': ['GainLo','GainMid','GainHi'],
                            'Cuts': ['LowOn','MidOn','HighOn']},
              'AudioEffectGroupDevice': {'Gains': [('Macro %i' % (index + 2)) for index in range(3) ], #last 3 buttons of top row
                                         'Cuts': [('Macro %i' % (index + 6)) for index in range(3) ]} #last 3 buttons of bottom row
              }
FILTER_DEVICES = {'AutoFilter': {'Frequency': 'Frequency',
                                 'Resonance': 'Resonance'},
                  'Operator': {'Frequency': 'Filter Freq',
                               'Resonance': 'Filter Res'},
                  'OriginalSimpler': {'Frequency': 'Filter Freq',
                                      'Resonance': 'Filter Res'},
                  'MultiSampler': {'Frequency': 'Filter Freq',
                                   'Resonance': 'Filter Res'},
                  'UltraAnalog': {'Frequency': 'F1 Freq',
                                  'Resonance': 'F1 Resonance'},
                  'StringStudio': {'Frequency': 'Filter Freq',
                                   'Resonance': 'Filter Reso'},
                  'AudioEffectGroupDevice': {'Frequency': 'Macro 1',
                                             'Resonance': 'Macro 5'}}#,
                  #'FilterEQ3': {'Frequency': 'FreqLo',
                                #'Resonance': 'FreqHi'}}

class TrackEQComponent(ControlSurfaceComponent):
    """ Class representing a track's EQ, it attaches to the last EQ device in the track """

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._track = None
        self._device = None
        self._gain_controls = None
        self._cut_buttons = None
        return

    def disconnect(self):
        if self._gain_controls != None:
            for control in self._gain_controls:
                control.release_parameter()

            self._gain_controls = None
        if self._cut_buttons != None:
            for button in self._cut_buttons:
                button.remove_value_listener(self._cut_value)

        self._cut_buttons = None
        if self._track != None:
            self._track.remove_devices_listener(self._on_devices_changed)
            self._track = None
        self._device = None
        if self._device != None:
            device_dict = EQ_DEVICES[self._device.class_name]
            if 'Cuts' in device_dict.keys():
                cut_names = device_dict['Cuts']
                for cut_name in cut_names:
                    parameter = get_parameter_by_name(self._device, cut_name)
                    if parameter != None and parameter.value_has_listener(self._on_cut_changed):
                        parameter.remove_value_listener(self._on_cut_changed)

        return

    def on_enabled_changed(self):
        self.update()

    def set_track(self, track):
        if not (track == None or isinstance(track, Live.Track.Track)):
            raise AssertionError
            if self._track != None:
                self._track.remove_devices_listener(self._on_devices_changed)
                if self._gain_controls != None and self._device != None:
                    for control in self._gain_controls:
                        control.release_parameter()

            self._track = track
            self._track != None and self._track.add_devices_listener(self._on_devices_changed)
        self._on_devices_changed()
        return

    def set_cut_buttons(self, buttons):
        if not (buttons == None or isinstance(buttons, tuple)):
            raise AssertionError
            if buttons != self._cut_buttons and self._cut_buttons != None:
                for button in self._cut_buttons:
                    button.remove_value_listener(self._cut_value)

            self._cut_buttons = buttons
            if self._cut_buttons != None:
                for button in self._cut_buttons:
                    button.add_value_listener(self._cut_value, identify_sender=True)

            self.update()
        return

    def set_gain_controls(self, controls):
        raise controls != None or AssertionError
        raise isinstance(controls, tuple) or AssertionError
        if self._device != None and self._gain_controls != None:
            for control in self._gain_controls:
                control.release_parameter()

        for control in controls:
            raise control != None or AssertionError
            raise isinstance(control, EncoderElement) or AssertionError

        self._gain_controls = controls
        self.update()
        return

    def update(self):
        super(TrackEQComponent, self).update()
        if self.is_enabled() and self._device != None:
            device_dict = EQ_DEVICES[self._device.class_name]
            if self._gain_controls != None:
                gain_names = device_dict['Gains']
                for index in range(len(self._gain_controls)):
                    self._gain_controls[index].release_parameter()
                    if len(gain_names) > index:
                        parameter = get_parameter_by_name(self._device, gain_names[index])
                        if parameter != None:
                            self._gain_controls[index].connect_to(parameter)

            if self._cut_buttons != None and 'Cuts' in device_dict.keys():
                cut_names = device_dict['Cuts']
                for index in range(len(self._cut_buttons)):
                    self._cut_buttons[index].turn_off()
                    if len(cut_names) > index:
                        parameter = get_parameter_by_name(self._device, cut_names[index])
                        if parameter != None:
                            if parameter.value == 0.0:
                                self._cut_buttons[index].turn_on()
                            if not parameter.value_has_listener(self._on_cut_changed):
                                parameter.add_value_listener(self._on_cut_changed)

        else:
            if self._cut_buttons != None:
                for button in self._cut_buttons:
                    if button != None:
                        button.turn_off()

            if self._gain_controls != None:
                for control in self._gain_controls:
                    control.release_parameter()

        return

    def _cut_value(self, value, sender):
        if not sender in self._cut_buttons:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self.is_enabled() and self._device != None:
                    if not sender.is_momentary() or value is not 0:
                        device_dict = EQ_DEVICES[self._device.class_name]
                        if 'Cuts' in device_dict.keys():
                            cut_names = device_dict['Cuts']
                            index = list(self._cut_buttons).index(sender)
                            parameter = index in range(len(cut_names)) and get_parameter_by_name(self._device, cut_names[index])
                            parameter.value = parameter != None and parameter.is_enabled and float(int(parameter.value + 1) % 2)
        return

    def _on_devices_changed(self):
        if self._device != None:
            device_dict = EQ_DEVICES[self._device.class_name]
            if 'Cuts' in device_dict.keys():
                cut_names = device_dict['Cuts']
                for cut_name in cut_names:
                    parameter = get_parameter_by_name(self._device, cut_name)
                    if parameter != None and parameter.value_has_listener(self._on_cut_changed):
                        parameter.remove_value_listener(self._on_cut_changed)

        self._device = None
        if self._track != None:
            for index in range(len(self._track.devices)):
                device = self._track.devices[-1 * (index + 1)]
                if device.class_name in EQ_DEVICES.keys():
                    self._device = device
                    break

        self.update()
        return

    def _on_cut_changed(self):
        if not self._device != None:
            raise AssertionError
            raise 'Cuts' in EQ_DEVICES[self._device.class_name].keys() or AssertionError
            cut_names = self.is_enabled() and self._cut_buttons != None and EQ_DEVICES[self._device.class_name]['Cuts']
            for index in range(len(self._cut_buttons)):
                self._cut_buttons[index].turn_off()
                if len(cut_names) > index:
                    parameter = get_parameter_by_name(self._device, cut_names[index])
                    if parameter != None and parameter.value == 0.0:
                        self._cut_buttons[index].turn_on()

        return

class TrackFilterComponent(ControlSurfaceComponent):
    """ Class representing a track's filter, attaches to the last filter in the track """

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._track = None
        self._device = None
        self._freq_control = None
        self._reso_control = None
        return

    def disconnect(self):
        if self._freq_control != None:
            self._freq_control.release_parameter()
            self._freq_control = None
        if self._reso_control != None:
            self._reso_control.release_parameter()
            self._reso_control = None
        if self._track != None:
            self._track.remove_devices_listener(self._on_devices_changed)
            self._track = None
        self._device = None
        return

    def on_enabled_changed(self):
        self.update()

    def set_track(self, track):
        if not (track == None or isinstance(track, Live.Track.Track)):
            raise AssertionError
            if self._track != None:
                self._track.remove_devices_listener(self._on_devices_changed)
                if self._device != None:
                    if self._freq_control != None:
                        self._freq_control.release_parameter()
                    if self._reso_control != None:
                        self._reso_control.release_parameter()
            self._track = track
            self._track != None and self._track.add_devices_listener(self._on_devices_changed)
        self._on_devices_changed()
        return

    def set_filter_controls(self, freq, reso):
        if not isinstance(freq, EncoderElement):
            raise AssertionError
            if not isinstance(freq, EncoderElement):
                raise AssertionError
                if self._device != None:
                    self._freq_control != None and self._freq_control.release_parameter()
                self._reso_control != None and self._reso_control.release_parameter()
        self._freq_control = freq
        self._reso_control = reso
        self.update()
        return

    def update(self):
        super(TrackFilterComponent, self).update()
        if self.is_enabled() and self._device != None:
            device_dict = FILTER_DEVICES[self._device.class_name]
            if self._freq_control != None:
                self._freq_control.release_parameter()
                parameter = get_parameter_by_name(self._device, device_dict['Frequency'])
                if parameter != None:
                    self._freq_control.connect_to(parameter)
            if self._reso_control != None:
                self._reso_control.release_parameter()
                parameter = get_parameter_by_name(self._device, device_dict['Resonance'])
                if parameter != None:
                    self._reso_control.connect_to(parameter)
        return

    def _on_devices_changed(self):
        self._device = None
        if self._track != None:
            for index in range(len(self._track.devices)):
                device = self._track.devices[-1 * (index + 1)]
                if device.class_name in FILTER_DEVICES.keys():
                    self._device = device
                    break

        self.update()
        return

class SpecialTrackEQComponent(TrackEQComponent): #added to override _cut_value

    def __init__(self, parent):
        TrackEQComponent.__init__(self)
        self._ignore_cut_buttons = False
        self._parent = parent

    def _cut_value(self, value, sender):
        assert (sender in self._cut_buttons)
        assert (value in range(128))
        if self._ignore_cut_buttons == False: #added
            if (self.is_enabled() and (self._device != None)):
                if ((not sender.is_momentary()) or (value is not 0)):
                    device_dict = EQ_DEVICES[self._device.class_name]
                    if ('Cuts' in device_dict.keys()):
                        cut_names = device_dict['Cuts']
                        index = list(self._cut_buttons).index(sender)
                        if (index in range(len(cut_names))):
                            parameter = get_parameter_by_name(self._device, cut_names[index])
                            if (parameter != None):
                                if parameter.value > 0:
                                    parameter.value = 0
                                else:
                                    parameter.value = 1
                                if self._device.class_name == 'AudioEffectGroupDevice':
                                    parameter.value = parameter.value * 127



    def update(self):
        if (self.is_enabled() and (self._device != None)):
            device_dict = EQ_DEVICES[self._device.class_name]
            if (self._gain_controls != None):
                gain_names = device_dict['Gains']
                for index in range(len(self._gain_controls)):
                    self._gain_controls[index].release_parameter()
                    if (len(gain_names) > index):
                        parameter = get_parameter_by_name(self._device, gain_names[index])
                        if (parameter != None):
                            self._gain_controls[index].connect_to(parameter)

            if ((self._cut_buttons != None) and ('Cuts' in device_dict.keys())):
                cut_names = device_dict['Cuts']
                for index in range(len(self._cut_buttons)):
                    self._cut_buttons[index].turn_off()
                    if (len(cut_names) > index):
                        parameter = get_parameter_by_name(self._device, cut_names[index])
                        if (parameter != None):
                            if self._device.class_name == 'FilterEQ3':
                                if (parameter.value == 0.0):
                                    self._cut_buttons[index].turn_on()
                            else:
                                if (parameter.value > 0.0):
                                    self._cut_buttons[index].turn_on()
                            if (not parameter.value_has_listener(self._on_cut_changed)):
                                parameter.add_value_listener(self._on_cut_changed)

        else:
            if (self._cut_buttons != None):
                for button in self._cut_buttons:
                    if (button != None):
                        button.turn_off()

            if (self._gain_controls != None):
                for control in self._gain_controls:
                    control.release_parameter()

        #self._rebuild_callback()

    def _on_cut_changed(self):
        assert (self._device != None)
        assert ('Cuts' in EQ_DEVICES[self._device.class_name].keys())
        if (self.is_enabled() and (self._cut_buttons != None)):
            cut_names = EQ_DEVICES[self._device.class_name]['Cuts']
            for index in range(len(self._cut_buttons)):
                self._cut_buttons[index].turn_off()
                if (len(cut_names) > index):
                    parameter = get_parameter_by_name(self._device, cut_names[index])
                    if (parameter != None):
                        if self._device.class_name == 'FilterEQ3':
                            if (parameter.value == 0.0):
                                self._cut_buttons[index].turn_on()
                        else:
                            if (parameter.value > 0.0):
                                self._cut_buttons[index].turn_on()

    def _on_devices_changed(self):
        if (self._device != None):
            device_dict = EQ_DEVICES[self._device.class_name]
            if ('Cuts' in device_dict.keys()):
                cut_names = device_dict['Cuts']
                for cut_name in cut_names:
                    parameter = get_parameter_by_name(self._device, cut_name)
                    if ((parameter != None) and parameter.value_has_listener(self._on_cut_changed)):
                        parameter.remove_value_listener(self._on_cut_changed)

        self._device = None
        if (self._track != None):
            for index in range(len(self._track.devices)):
                device = self._track.devices[(-1 * (index + 1))]
                if (device.class_name in EQ_DEVICES.keys()):
                    self._device = device
                    break

        self.update()

class SpecialTrackFilterComponent(TrackFilterComponent): #added to override _cut_value
    __module__ = __name__
    __doc__ = " Class representing a track's filter, attaches to the last filter in the track "

    def __init__(self, parent):
        TrackFilterComponent.__init__(self)
        self._parent = parent                        


    def update(self):
        if (self.is_enabled() and (self._device != None)):
            device_dict = FILTER_DEVICES[self._device.class_name]
            if (self._freq_control != None):
                self._freq_control.release_parameter()
                parameter = get_parameter_by_name(self._device, device_dict['Frequency'])
                if (parameter != None):
                    self._freq_control.connect_to(parameter)
            if (self._reso_control != None):
                self._reso_control.release_parameter()
                parameter = get_parameter_by_name(self._device, device_dict['Resonance'])
                if (parameter != None):
                    self._reso_control.connect_to(parameter)
        #self._rebuild_callback()


    def _on_devices_changed(self):
        self._device = None
        if (self._track != None):
            for index in range(len(self._track.devices)):
                device = self._track.devices[(-1 * (index + 1))]
                if (device.class_name in FILTER_DEVICES.keys()):
                    self._device = device
                    break

        self.update()        

class EncoderEQComponent(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = " Class representing encoder EQ component "

    def __init__(self, mixer, parent):
        ControlSurfaceComponent.__init__(self)
        assert isinstance(mixer, MixerComponent)
        self._param_controls = None
        self._mixer = mixer
        self._buttons = []
        self._param_controls = None
        self._lock_button = None
        self._last_mode = 0
        self._is_locked = False
        self._ignore_buttons = False
        self._track = None
        self._strip = None
        self._parent = parent
        self._track_eq = SpecialTrackEQComponent(parent)
        self._track_filter = SpecialTrackFilterComponent(parent)

    def disconnect(self):
        self._param_controls = None
        self._mixer = None
        self._buttons = None
        self._param_controls = None
        self._lock_button = None
        self._track = None
        self._strip = None
        self._parent = None
        self._track_eq = None
        self._track_filter = None

    def update(self):
        pass


    def set_controls_and_buttons(self, controls, buttons):
        assert ((controls == None) or (isinstance(controls, tuple) and (len(controls) == 8)))
        self._param_controls = controls
        assert ((buttons == None) or (isinstance(buttons, tuple)) or (len(buttons) == 4))
        self._buttons = buttons
        self.set_lock_button(self._buttons[0])
        self._update_controls_and_buttons()


    def _update_controls_and_buttons(self):
        #if self.is_enabled():
        if self._param_controls != None and self._buttons != None:
            if self._is_locked != True:
                self._track = self.song().view.selected_track
                self._track_eq.set_track(self._track)
                cut_buttons = [self._buttons[1], self._buttons[2], self._buttons[3]]
                self._track_eq.set_cut_buttons(tuple(cut_buttons))
                self._track_eq.set_gain_controls(tuple([self._param_controls[5], self._param_controls[6], self._param_controls[7]]))
                self._track_filter.set_track(self._track)
                self._track_filter.set_filter_controls(self._param_controls[0], self._param_controls[4])
                self._strip = self._mixer._selected_strip
                self._strip.set_send_controls(tuple([self._param_controls[1], self._param_controls[2], self._param_controls[3]]))         

            else:
                self._track_eq.set_track(self._track)
                cut_buttons = [self._buttons[1], self._buttons[2], self._buttons[3]]
                self._track_eq.set_cut_buttons(tuple(cut_buttons))
                self._track_eq.set_gain_controls(tuple([self._param_controls[5], self._param_controls[6], self._param_controls[7]]))
                self._track_filter.set_track(self._track)
                self._track_filter.set_filter_controls(self._param_controls[0], self._param_controls[4])
                ##self._strip = self._mixer._selected_strip
                self._strip.set_send_controls(tuple([self._param_controls[1], self._param_controls[2], self._param_controls[3]])) 
                ##pass               

        #self._rebuild_callback()


    def on_track_list_changed(self):
        self.on_selected_track_changed()


    def on_selected_track_changed(self):
        if self.is_enabled():
            if self._is_locked != True:
                self._update_controls_and_buttons()


    def on_enabled_changed(self):
        self.update()  

    def set_lock_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._lock_button != None):
            self._lock_button.remove_value_listener(self._lock_value)
            self._lock_button = None
        self._lock_button = button
        if (self._lock_button != None):
            self._lock_button.add_value_listener(self._lock_value)
            if self._is_locked:
                self._lock_button.turn_on()
            else:
                self._lock_button.turn_off()            


    def _lock_value(self, value):
        assert (self._lock_button != None)
        assert (value != None)
        assert isinstance(value, int)
        if ((not self._lock_button.is_momentary()) or (value is not 0)):
        #if (value is not 0):
            if self._ignore_buttons == False:
                if self._is_locked:
                    self._is_locked = False
                    self._mixer._is_locked = False
                    self._lock_button.turn_off()
                    self._mixer.on_selected_track_changed()
                    self.on_selected_track_changed()
                else:
                    self._is_locked = True
                    self._mixer._is_locked = True
                    self._lock_button.turn_on()



# local variables:
# tab-width: 4
