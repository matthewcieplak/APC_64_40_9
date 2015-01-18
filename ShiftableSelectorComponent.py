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

import Live
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.DeviceComponent import DeviceComponent 
from _Framework.SessionZoomingComponent import SessionZoomingComponent #added
from EncoderUserModesComponent import EncoderUserModesComponent #added
from PedaledSessionComponent import PedaledSessionComponent #added

class ShiftableSelectorComponent(ModeSelectorComponent):
    """ SelectorComponent that assigns buttons to functions based on the shift button """

    def __init__(self, parent, select_buttons, master_button, stop_buttons, stop_all_button, mute_buttons, solo_buttons, arm_buttons, scene_buttons, matrix, session, zooming, mixer, slider_modes, matrix_modes, sequencer):
        assert len(select_buttons) == 8
        assert len(arm_buttons) == 8
        ModeSelectorComponent.__init__(self)
        self._toggle_pressed = False
        self._note_mode_active = False
        self._invert_assignment = False
        self._select_buttons = select_buttons
        self._master_button = master_button
        self._slider_modes = slider_modes
        self._matrix_modes = matrix_modes #added new 
        self._stop_buttons = stop_buttons
        self._stop_all_button = stop_all_button
        self._mute_buttons = mute_buttons
        self._solo_buttons = solo_buttons
        self._arm_buttons = arm_buttons
        self._scene_launch_buttons = scene_buttons
        # self._transport = transport
        self._session = session
        self._zooming = zooming
        self._matrix = matrix
        self._mixer = mixer
        # self._mode_callback = mode_callback
        self._parent = parent #use this to call methods of parent class
        self._sequencer = sequencer
        self._sequencer.set_enabled(False)
        self._master_button.add_value_listener(self._master_value)
        self._step_sequencer_active = False # temporary!!!!

    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        # self._master_button.remove_value_listener(self._master_value)
        self._select_buttons = None
        self._master_button = None
        self._slider_modes = None
        self._matrix_modes = None #added
        self._stop_buttons = None
        self._stop_all_button = None
        self._mute_buttons = None
        self._solo_buttons = None
        self._arm_buttons = None
        #self._transport = None
        self._session = None
        self._zooming = None
        self._matrix = None
        self._mixer = None
        self._parent = None #added
        # self._mode_callback = None

    def set_mode_toggle(self, button):
        ModeSelectorComponent.set_mode_toggle(self, button)
        self.set_mode(0)

    def invert_assignment(self):
        self._invert_assignment = True
        self._recalculate_mode()

    def number_of_modes(self):
        return 2

    def update(self):
        if self.is_enabled():
            if self._mode_index == 0: #shift released #int(self._invert_assignment):
                self._slider_modes.set_mode_buttons(None)
                if not self._step_sequencer_active:
                    for index in range(len(self._mute_buttons)):
                        self._mixer.channel_strip(index).set_mute_button(self._mute_buttons[index])
                    for index in range(len(self._solo_buttons)):
                        self._mixer.channel_strip(index).set_solo_button(self._solo_buttons[index])                        
                    for index in range(len(self._arm_buttons)): #was: for index in range(len(self._select_buttons)):
                        self._mixer.channel_strip(index).set_arm_button(self._arm_buttons[index])
                    self._matrix_modes.set_mode_buttons(None)
                    for index in range(len(self._select_buttons)):
                        self._mixer.channel_strip(index).set_select_button(self._select_buttons[index])
                    self._mixer.master_strip().set_select_button(self._master_button) #enable master select if shift is released
            else: #if shift pressed
                for index in range(len(self._mute_buttons)):
                    self._mixer.channel_strip(index).set_mute_button(None)
                for index in range(len(self._solo_buttons)):
                    self._mixer.channel_strip(index).set_solo_button(None)                
                for index in range(len(self._arm_buttons)): #was: for index in range(len(self._select_buttons)):
                    self._mixer.channel_strip(index).set_arm_button(None)
                if not self._step_sequencer_active:
                    for index in range(len(self._select_buttons)):
                        self._mixer.channel_strip(index).set_select_button(None)
                    self._matrix_modes.set_mode_buttons(self._select_buttons)
                    self._slider_modes.set_mode_buttons(self._arm_buttons)
                self._mixer.master_strip().set_select_button(None) #disable master select while shift is held down

    def _partial_refresh(self, value):
        for component in self._parent.components: #this is needed to force a refresh when manual mappings exist
            if isinstance(component, PedaledSessionComponent) or isinstance(component, SessionZoomingComponent):
                component.update()

    def _toggle_value(self, value):
        assert self._mode_toggle != None
        assert value in range(128)
        self._toggle_pressed = value > 0
        self._recalculate_mode()
        if value < 1 and self._matrix_modes._last_mode > 1: #refresh on Shift button release, and if previous mode was Note Mode
            self._parent.schedule_message(2, self._partial_refresh, value)

    def _recalculate_mode(self):
        self.set_mode((int(self._toggle_pressed) + int(self._invert_assignment)) % self.number_of_modes())

    def _master_value(self, value): #this is the master_button value_listener, i.e. called when the master_button is pressed
        if not self._master_button != None:
            raise AssertionError
        if not value in range(128):
            raise AssertionError
        if self.is_enabled() and self._toggle_pressed:
            if not self._master_button.is_momentary() or value > 0: #if the master button is pressed:
                if not self._step_sequencer_active: #if sequencer is not active, then make it active            
                    for button in self._select_buttons:
                        button.turn_off()
                    for button in self._stop_buttons:
                        button.turn_off()
                        button.use_default_message()
                        button.set_enabled(True)
                    for button in self._scene_launch_buttons:
                        button.turn_off()
                    for scene_index in range(5): #turn off clip launch grid LEDs and reset note & channel values to default (for Note Mode compatibility)
                        for track_index in range(8):                
                            button = self._matrix.get_button(track_index, scene_index)
                            button.turn_off()
                            button.use_default_message()
                            button.set_enabled(True)
                    self._zooming.set_enabled(False)
                    self._matrix_modes.set_enabled(False)
                    self._session.set_enabled(False)
                    self._master_button.turn_on()
                    self._session.set_show_highlight(True)
                    self._sequencer._is_active = True
                    self._sequencer.set_enabled(True)
                else: #if sequencer is active, then turn it off and turn other modes back on
                    self._sequencer._is_active = False
                    self._sequencer.set_enabled(False)
                    self._master_button.turn_off()
                    self._session.set_enabled(True)
                    self._matrix_modes.set_enabled(True)
                    self._matrix_modes._set_modes()
                self._step_sequencer_active = not self._step_sequencer_active

    def _on_note_mode_changed(self):
        if not self._master_button != None:
            raise AssertionError
            if self.is_enabled() and self._invert_assignment == self._toggle_pressed:
                self._note_mode_active and self._master_button.turn_on()
            else:
                self._master_button.turn_off()