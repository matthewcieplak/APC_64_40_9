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
# -*- coding: utf-8 -*-

from _Framework.MixerComponent import MixerComponent
from SpecialChanStripComponent import SpecialChanStripComponent
from _Framework.ButtonElement import ButtonElement #added
from _Framework.EncoderElement import EncoderElement #added  

class SpecialMixerComponent(MixerComponent):
    """ Special mixer class that uses return tracks alongside midi and audio tracks """

    def __init__(self, parent, num_tracks):
        self._is_locked = False #added
        self._parent = parent #added
        MixerComponent.__init__(self, num_tracks)
        self._shift_button = None #added
        self._shift_pressed = False #added

    def disconnect(self): #added
        MixerComponent.disconnect(self)
        if (self._shift_button != None):
            self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = None

    def tracks_to_use(self):
        return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)

    def _create_strip(self):
        return SpecialChanStripComponent()

    def set_shift_button(self, button): #added
        assert ((button == None) or (isinstance(button, ButtonElement) and button.is_momentary()))
        if (self._shift_button != button):
            if (self._shift_button != None):
                self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = button
            if (self._shift_button != None):
                self._shift_button.add_value_listener(self._shift_value)
            self.update()

    def _shift_value(self, value): #added
        assert (self._shift_button != None)
        assert (value in range(128))
        self._shift_pressed = (value != 0)
        self.update()

    def on_selected_track_changed(self): #added override
        selected_track = self.song().view.selected_track
        if (self._selected_strip != None):
            if self._is_locked == False: #added
                self._selected_strip.set_track(selected_track)
        if self.is_enabled():
            if (self._next_track_button != None):
                if (selected_track != self.song().master_track):
                    self._next_track_button.turn_on()
                else:
                    self._next_track_button.turn_off()
            if (self._prev_track_button != None):
                if (selected_track != self.song().tracks[0]):
                    self._prev_track_button.turn_on()
                else:
                    self._prev_track_button.turn_off()        

    def update(self): #added override
        if self._allow_updates:
            master_track = self.song().master_track
            if self.is_enabled():
                if (self._prehear_volume_control != None):
                    #if self._shift_pressed: #added
                    if not self._shift_pressed: #added 
                        self._prehear_volume_control.connect_to(master_track.mixer_device.cue_volume)
                    else:
                        self._prehear_volume_control.release_parameter() #added        
                if (self._crossfader_control != None):
                    self._crossfader_control.connect_to(master_track.mixer_device.crossfader)
            else:
                if (self._prehear_volume_control != None):
                    self._prehear_volume_control.release_parameter()
                if (self._crossfader_control != None):
                    self._crossfader_control.release_parameter()
                if (self._bank_up_button != None):
                    self._bank_up_button.turn_off()
                if (self._bank_down_button != None):
                    self._bank_down_button.turn_off()
                if (self._next_track_button != None):
                    self._next_track_button.turn_off()
                if (self._prev_track_button != None):
                    self._prev_track_button.turn_off()
            ##self._rebuild_callback()
        else:
            self._update_requests += 1

    def set_track_offset(self, new_offset): #added override
        MixerComponent.set_track_offset(self, new_offset)
        if self._parent._slider_modes != None:
            self._parent._slider_modes.update()
        if self._parent._encoder_modes != None:
            self._parent._encoder_modes.update()          

    def on_track_list_changed(self): #added override
        MixerComponent.on_track_list_changed(self)
        if self._parent._slider_modes != None:
            self._parent._slider_modes.update()
        if self._parent._encoder_modes != None:
            self._parent._encoder_modes.update()

            
