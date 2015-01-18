# http://remotescripts.blogspot.com
"""
64 Step Sequencer component originally designed for use with the APC40.
Copyright (C) 2010 Hanz Petrov <hanz.petrov@gmail.com>

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

Inspired in part by the LiveControl Sequencer module by ST8 <http://monome.q3f.org>
and by the CS Step Sequencer Live API example by Cycling '74 <http://www.cycling74.com>
"""

import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SessionComponent import SessionComponent
from _Framework.ButtonMatrixElement import ButtonMatrixElement
INITIAL_SCROLLING_DELAY = 4
INTERVAL_SCROLLING_DELAY = 1
OFF = 0
GREEN = 1
GREEN_BLINK = 2
RED = 3
RED_BLINK = 4
YELLOW = 5
YELLOW_BLINK = 6
class StepSequencerComponent(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = ' 64 Step Sequencer Component '

    def __init__(self, parent, session, matrix, playing_position_buttons):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
        self._session = session
        self._matrix = matrix
        self._playing_position_buttons = playing_position_buttons
        self._bank_buttons = None
        self._buttons = None
        self._follow_button = None
        self._shift_button = None
        self._shift_pressed = False
        self._velocity_buttons = None
        self._velocity_index = 5 #velocity index max range matches session width (0 to 7)
        self._velocity = 95 #range 0 to 127
        self._quantization = 0.25 #1/16th note in 4/4 time
        self._quantization_index = 2
        self._lane_mute_buttons = None
        self._loop_start_buttons = None
        self._loop_length_buttons = None
        self._loop_start_index = 0
        self._loop_end_index = 7
        self._loop_index_length = 0
        self._loop_length = None
        self._loop_start = None
        self._loop_end = None
        self._width = self._session.width()
        self._height = self._session.height()
        self._bank_index = 0 #bank index; range matches session width
        self._key_index = 36 #C1 Note
        self._is_following = False
        self._sequencer_clip = None
        self._clip_notes = []
        self._muted_lanes = []
        self._nav_up_button = None
        self._nav_down_button = None
        self._nav_left_button = None
        self._nav_right_button = None 
        self._scroll_up_ticks_delay = -1
        self._scroll_down_ticks_delay = -1
        self._scroll_right_ticks_delay = -1
        self._scroll_left_ticks_delay = -1
        self._is_active = False
        self._register_timer_callback(self._on_timer)

    def disconnect(self):
        self._parent = None
        self._session = None
        self._matrix = None
        self._playing_position_buttons = None
        self._bank_buttons = None
        self._buttons = None   
        self._follow_button = None
        self._shift_button = None
        self._velocity_buttons = None
        self._lane_mute_buttons = None
        self._loop_start_buttons = None
        self._loop_length_buttons = None
        self._nav_up_button = None
        self._nav_down_button = None
        self._nav_left_button = None
        self._nav_right_button = None
        self._sequencer_clip = None


    def update(self):
        if self._is_active:
            self.on_clip_slot_changed()
            self._update_bank_buttons()
            self._update_velocity_buttons()
            self._update_quantization_buttons()
            self._on_loop_changed()
            self._update_matrix()
            self._on_playing_status_changed()


    def _update_bank_buttons(self):
        if self._is_active:
            if (self._bank_buttons != None):
                for index in range(len(self._bank_buttons)):
                    if index == self._bank_index:
                        if not self._is_following: #invert on/offs for follow, since stop_all_clips button has no LED...
                            self._bank_buttons[index].turn_on()
                        else:
                            self._bank_buttons[index].turn_off()
                    else:
                        if not self._is_following:
                            self._bank_buttons[index].turn_off()
                        else:
                            self._bank_buttons[index].turn_on()

    def _update_velocity_buttons(self):
        if self._is_active:
            if (self._velocity_buttons != None):
                for index in range(len(self._velocity_buttons)):
                    if index <= self._velocity_index:
                        self._velocity_buttons[index].turn_on()
                        #self._velocity_buttons[(self._height - 1) - index].turn_on() #invert if using scene launch buttons
                    else:
                        self._velocity_buttons[index].turn_off()
                        #self._velocity_buttons[(self._height -1 ) - index].turn_off() #invert if using scene launch buttons

    def _update_loop_buttons(self):
        if self._is_active:
            if (self._loop_start_buttons != None):
                for index in range(len(self._loop_start_buttons)):
                    if index >= self._loop_start_index and index <= self._loop_end_index and self._loop_start_index != -1:
                        self._loop_start_buttons[index].turn_on()
                    else:
                        self._loop_start_buttons[index].turn_off()   

    def _update_loop_length_buttons(self):
        if self._is_active:
            if (self._loop_length_buttons != None):
                for index in range(len(self._loop_length_buttons)):
                    if index < self._loop_index_length:
                        self._loop_length_buttons[index].turn_on()
                    else:
                        self._loop_length_buttons[index].turn_off()


    def _update_quantization_buttons(self): #shifted lane mute buttons
        if self._is_active: # and not self._shift_pressed:
            if (self._lane_mute_buttons != None):
                for index in range(len(self._lane_mute_buttons)):
                    if index <= self._quantization_index:
                        #self._lane_mute_buttons[index].turn_on()
                        self._lane_mute_buttons[(self._height - 1) - index].turn_on() #invert if using scene launch buttons
                    else:
                        #self._lane_mute_buttons[index].turn_off()
                        self._lane_mute_buttons[(self._height -1 ) - index].turn_off() #invert if using scene launch buttons

    #def _update_follow_button(self): #not used: stop_all_clips button has no LED...
        #if self._is_active:
            #if (self._follow_button != None):
                #if self._is_following:
                    #self._follow_button.turn_on()
                #else:
                    #self._follow_button.turn_off()

    def on_enabled_changed(self):
        self.update()

    def on_selected_track_changed(self):
        self.update()

    def on_track_list_changed(self):
        self.update()

    def on_selected_scene_changed(self):
        self.update()

    def on_scene_list_changed(self):
        self.update()

    def on_clip_slot_changed(self):
        if self.is_enabled() and self._is_active:
            if self.song().view.highlighted_clip_slot != None:
                clip_slot = self.song().view.highlighted_clip_slot
                if clip_slot.has_clip: # and clip_slot.clip.is_midi_clip:
                    if self._sequencer_clip != clip_slot.clip:
                        if self._sequencer_clip != None:
                            if self._sequencer_clip.is_midi_clip:
                                if self._sequencer_clip.notes_has_listener(self._on_notes_changed):
                                    self._sequencer_clip.remove_notes_listener(self._on_notes_changed)
                            if self._sequencer_clip.playing_status_has_listener(self._on_playing_status_changed):
                                self._sequencer_clip.remove_playing_status_listener(self._on_playing_status_changed) 
                            if self._sequencer_clip.loop_start_has_listener(self._on_loop_changed):
                                self._sequencer_clip.remove_loop_start_listener(self._on_loop_changed) 
                            if self._sequencer_clip.loop_end_has_listener(self._on_loop_changed):
                                self._sequencer_clip.remove_loop_end_listener(self._on_loop_changed)                               
                        self._sequencer_clip = clip_slot.clip
                        self._loop_start = clip_slot.clip.loop_start
                        self._loop_end = clip_slot.clip.loop_end
                        self._loop_length = self._loop_end - self._loop_start  
                        self._update_notes()
                        self._on_loop_changed()
                        if clip_slot.clip.is_midi_clip:
                            self._sequencer_clip.add_notes_listener(self._on_notes_changed)          
                        self._sequencer_clip.add_playing_status_listener(self._on_playing_status_changed)
                        self._sequencer_clip.add_loop_start_listener(self._on_loop_changed)
                        self._sequencer_clip.add_loop_end_listener(self._on_loop_changed)


    def _on_loop_changed(self): #loop start/end listener
        if self.is_enabled() and self._is_active:
            if self._sequencer_clip != None:
                self._loop_start_index = int(self._sequencer_clip.loop_start / self._quantization / self._width)
                self._loop_end_index = int(self._sequencer_clip.loop_end / self._quantization / self._width) - 1 #round down to next button
                self._loop_length = self._sequencer_clip.loop_end - self._sequencer_clip.loop_start
                loop_index_length = self._loop_end_index - self._loop_start_index + 1
                if loop_index_length != self._loop_index_length:
                    self._loop_index_length = loop_index_length
                    #self._update_loop_length_buttons()
                if self._loop_start_index > (self._width -1):
                    self._loop_start_index = -1
                elif self._loop_start_index < 0:
                    self._loop_start_index = 0
                if self._loop_end_index > (self._width -1):
                    self._loop_end_index = (self._width -1)
                elif self._loop_end_index < 0:
                    self._loop_end_index = -1
                self._update_loop_buttons()
                self._update_loop_length_buttons()
             

    def _on_notes_changed(self): #notes changed listener
        self._parent.schedule_message(3, self._update_notes) #Live bug: delay is required to avoid blocking mouse drag operations in MIDI clip view


    def _update_notes(self):
        """LiveAPI clip.get_selected_notes returns a tuple of tuples where each inner tuple represents a note.
        The inner tuple contains pitch, time, duration, velocity, and mute state.
        e.g.: (46, 0.25, 0.25, 127, False)"""
        if self._sequencer_clip.is_midi_clip:
            self._sequencer_clip.select_all_notes()
            note_cache = self._sequencer_clip.get_selected_notes()
            self._sequencer_clip.deselect_all_notes()
            if self._clip_notes != note_cache:
                self._clip_notes = note_cache
                self._update_matrix()


    def _on_playing_status_changed(self): #playing status changed listener
        if self.is_enabled() and self._is_active:
            if self._sequencer_clip != None:
                if self._sequencer_clip.is_playing:
                    if self._sequencer_clip.playing_position_has_listener(self._on_playing_position_changed):
                        self._sequencer_clip.remove_playing_position_listener(self._on_playing_position_changed)
                    self._sequencer_clip.add_playing_position_listener(self._on_playing_position_changed)
                else:
                    if self._sequencer_clip.playing_position_has_listener(self._on_playing_position_changed):
                        self._sequencer_clip.remove_playing_position_listener(self._on_playing_position_changed)


    def _on_playing_position_changed(self): #playing position changed listener
        if self.is_enabled() and self._is_active:
            if self._playing_position_buttons != None:
                if self._sequencer_clip != None:
                    """LiveAPI clip.playing_position: Constant access to the current playing position of the clip.
                    The returned value is the position in beats for midi and warped audio clips,
                    or in seconds for unwarped audio clips. Stopped clips will return 0."""
                    position = self._sequencer_clip.playing_position #position in beats (1/4 notes in 4/4 time)
                    bank = int(position / self._quantization / self._width) # 0.25 for 16th notes;  0.5 for 8th notes
                    if self._is_following == True:
                        if self._bank_index != bank:
                            self._bank_index = bank
                            self._update_bank_buttons()
                            self._update_matrix()
                    grid_position = int(position / self._quantization) - (bank * self._width) #stepped postion
                    for index in range(self._width):
                        if index == grid_position and grid_position < self._width and self._bank_index == bank:
                            self._playing_position_buttons[index].turn_on()
                        else:
                            self._playing_position_buttons[index].turn_off()



    def _update_matrix(self): #step grid LEDs are updated here
        if self.is_enabled() and self._is_active:
            if self._sequencer_clip != None:# and self._sequencer_clip.is_midi_clip:
                self._matrix.reset()
                if self._sequencer_clip.is_midi_clip:
                    for note in self._clip_notes:
                        position = note[1] #position in beats; range is 0.x to 15.x for 4 measures in 4/4 time (equivalent to 1/4 notes)
                        bank = int(position / self._quantization / self._width) #at 1/16th resolution in 4/4 time, each bank is 1/2 measure wide
                        if bank == self._bank_index: #if note is in current bank, then update grid
                            grid_x_position = int(position / self._quantization) - (bank * self._width) #stepped postion at quantize resolution
                            key = note[0] #key: 0-127 MIDI note #
                            if key >= self._key_index and key < (self._key_index + self._height):
                                grid_y_position = self._key_index + self._height -1 - key #invert bottom to top, to match button order
                                velocity = note[3]
                                muted = note[4]
                                if note[3] > 100:
                                    if not muted:
                                        velocity = RED
                                    else:
                                        velocity = RED_BLINK
                                elif note[3] > 72:
                                    if not muted:
                                        velocity = YELLOW
                                    else:
                                        velocity = YELLOW_BLINK
                                else:
                                    if not muted:
                                        velocity = GREEN
                                    else:
                                        velocity = GREEN_BLINK
                                self._matrix.send_value(grid_x_position, grid_y_position, velocity)


    def _matrix_value(self, value, x, y, is_momentary): #matrix buttons listener
        assert (self._buttons != None)
        assert (value in range(128))
        assert (x in range(self._buttons.width()))
        assert (y in range(self._buttons.height()))
        assert isinstance(is_momentary, type(False))
        """(pitch, time, duration, velocity, mute state)
        e.g.: (46, 0.25, 0.25, 127, False)"""
        if self.is_enabled() and self._is_active:
            if self._sequencer_clip != None and self._sequencer_clip.is_midi_clip:
                if ((value != 0) or (not is_momentary)):
                    pitch = (self._key_index + self._height - 1) - y #invert top to bottom
                    time = (x + (self._bank_index * self._width)) * self._quantization #convert position to time in beats
                    velocity = self._velocity
                    duration = self._quantization # 0.25 = 1/16th note; 0.5 = 1/8th note
                    ##self._parent.log_message("Matrix button pressed; pitch: %s  time: %s  velocity: %s duration: %s" % (str(pitch), str(time), str(velocity), str(duration)))
                    note_cache = list(self._clip_notes)
                    for note in note_cache:
                        if pitch == note[0] and time == note[1]:
                            if not self._shift_pressed:
                                note_cache.remove(note)
                            else:
                                note_cache.append([note[0], note[1], note[2], note[3], not note[4]])
                            break
                    else:
                        note_cache.append([pitch, time, duration, velocity, self._shift_pressed])
                    self._sequencer_clip.select_all_notes()
                    self._sequencer_clip.replace_selected_notes(tuple(note_cache))


    def set_button_matrix(self, buttons):
        assert isinstance(buttons, (ButtonMatrixElement,
                                    type(None)))
        if (buttons != self._buttons):
            if (self._buttons != None):
                self._buttons.remove_value_listener(self._matrix_value)
            self._buttons = buttons
            if (self._buttons != None):
                self._buttons.add_value_listener(self._matrix_value)
            ##self._rebuild_callback()
            self.update()


    def set_bank_buttons(self, buttons):
        assert ((buttons == None) or (isinstance(buttons, tuple) and (len(buttons) == self._width)))
        if (self._bank_buttons != buttons):
            if (self._bank_buttons  != None):
                for button in self._bank_buttons :
                    button.remove_value_listener(self._bank_button_value)
            self._bank_buttons = buttons
            if (self._bank_buttons  != None):
                for button in self._bank_buttons :
                    assert isinstance(button, ButtonElement)
                    button.add_value_listener(self._bank_button_value, identify_sender=True)
            ##self._rebuild_callback()
            self._update_bank_buttons()


    def _bank_button_value(self, value, sender):
        assert (self._bank_buttons != None)
        assert (list(self._bank_buttons).count(sender) == 1)
        assert (value in range(128))
        if self.is_enabled() and self._is_active:
            if ((value is not 0) or (not sender.is_momentary())):
                bank = list(self._bank_buttons).index(sender)
                if self._bank_index != bank:
                    self._bank_index = bank
                    self._update_bank_buttons()
                    self._update_matrix()

    def set_follow_button(self, button):
        assert isinstance(button, (ButtonElement,
                                   type(None)))
        if (button != self._follow_button):
            if (self._follow_button != None):
                self._follow_button.remove_value_listener(self._follow_value)
            self._follow_button = button
            if (self._follow_button != None):
                self._follow_button.add_value_listener(self._follow_value)
            ##self._rebuild_callback()


    def _follow_value(self, value):
        assert (self._follow_button != None)
        assert (value in range(128))
        if self.is_enabled()and self._is_active and not self._shift_pressed:
            if ((value != 0) or (not self._follow_button.is_momentary())):
                self._is_following = (not self._is_following) 
                self._update_bank_buttons() #self._update_follow_button()


    def set_shift_button(self, button):
        assert isinstance(button, (ButtonElement,
                                   type(None)))
        if (button != self._shift_button):
            if (self._shift_button != None):
                self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = button
            if (self._shift_button != None):
                self._shift_button.add_value_listener(self._shift_value)
            ##self._rebuild_callback()


    def _shift_value(self, value):
        assert (self._shift_button != None)
        assert (value in range(128))
        if self.is_enabled()and self._is_active:
            if value > 0:
                self._shift_pressed = True
                for button in self._lane_mute_buttons:
                    button.turn_off()
            else:
                self._shift_pressed = False
                self._update_quantization_buttons()



    def set_velocity_buttons(self, buttons):
        assert ((buttons == None) or (isinstance(buttons, tuple) and (len(buttons) == self._width))) #height)))
        if (self._velocity_buttons != buttons):
            if (self._velocity_buttons  != None):
                for button in self._velocity_buttons :
                    button.remove_value_listener(self._velocity_button_value)
            self._velocity_buttons = buttons
            if (self._velocity_buttons  != None):
                for button in self._velocity_buttons :
                    assert isinstance(button, ButtonElement)
                    button.add_value_listener(self._velocity_button_value, identify_sender=True)
            ##self._rebuild_callback()
            self._update_velocity_buttons()


    def _velocity_button_value(self, value, sender):
        assert (self._velocity_buttons != None)
        assert (list(self._velocity_buttons).count(sender) == 1)
        assert (value in range(128))
        if self.is_enabled() and self._is_active:
            if ((value is not 0) or (not sender.is_momentary())):
                #velocity = (self._height - 1) - (list(self._velocity_buttons).index(sender)) #invert to get top to bottom index, if using scene launch buttons
                velocity = list(self._velocity_buttons).index(sender)
                if self._velocity_index != velocity:
                    self._velocity_index = velocity
                    self._velocity = int((128.0 / (len(self._velocity_buttons)) * (self._velocity_index + 1)) - 1)
                    self._update_velocity_buttons()             


    def set_loop_start_buttons(self, buttons):
        assert ((buttons == None) or (isinstance(buttons, tuple) and (len(buttons) == self._width))) #height)))
        if (self._loop_start_buttons != buttons):
            if (self._loop_start_buttons  != None):
                for button in self._loop_start_buttons :
                    button.remove_value_listener(self._loop_start_button_value)
            self._loop_start_buttons = buttons
            if (self._loop_start_buttons  != None):
                for button in self._loop_start_buttons :
                    assert isinstance(button, ButtonElement)
                    button.add_value_listener(self._loop_start_button_value, identify_sender=True)
            ##self._rebuild_callback()


    def _loop_start_button_value(self, value, sender):
        assert (self._loop_start_buttons != None)
        assert (list(self._loop_start_buttons).count(sender) == 1)
        assert (value in range(128))
        if self.is_enabled() and self._is_active:
            if self._sequencer_clip != None:
                if ((value is not 0) or (not sender.is_momentary())):
                    loop_index = list(self._loop_start_buttons).index(sender)
                    loop_length = self._sequencer_clip.loop_end - self._sequencer_clip.loop_start
                    loop_start = loop_index * self._width * self._quantization
                    if loop_start + loop_length >= self._sequencer_clip.loop_end:
                        self._sequencer_clip.loop_end = loop_start + loop_length
                        self._sequencer_clip.loop_start = loop_start
                    else:
                        self._sequencer_clip.loop_start = loop_start
                        self._sequencer_clip.loop_end = loop_start + loop_length



    def set_loop_length_buttons(self, buttons):
        assert ((buttons == None) or (isinstance(buttons, tuple) and (len(buttons) == self._width)))
        if (self._loop_length_buttons != buttons):
            if (self._loop_length_buttons  != None):
                for button in self._loop_length_buttons :
                    button.remove_value_listener(self._loop_length_button_value)
            self._loop_length_buttons = buttons
            if (self._loop_length_buttons  != None):
                for button in self._loop_length_buttons :
                    assert isinstance(button, ButtonElement)
                    button.add_value_listener(self._loop_length_button_value, identify_sender=True)
            ##self._rebuild_callback()


    def _loop_length_button_value(self, value, sender):
        assert (self._loop_length_buttons != None)
        assert (list(self._loop_length_buttons).count(sender) == 1)
        assert (value in range(128))
        if self.is_enabled() and self._is_active:
            if self._sequencer_clip != None:
                if ((value is not 0) or (not sender.is_momentary())):
                    loop_index_length = list(self._loop_length_buttons).index(sender) + 1
                    self._loop_end = self._sequencer_clip.loop_start + (loop_index_length * self._width * self._quantization)
                    self._sequencer_clip.loop_end = self._loop_end


    def set_lane_mute_buttons(self, buttons):
        assert ((buttons == None) or (isinstance(buttons, tuple) and (len(buttons) == self._height)))
        if (self._lane_mute_buttons != buttons):
            if (self._lane_mute_buttons  != None):
                for button in self._lane_mute_buttons :
                    button.remove_value_listener(self._lane_mute_button_value)
            self._lane_mute_buttons = buttons
            if (self._lane_mute_buttons  != None):
                for button in self._lane_mute_buttons :
                    assert isinstance(button, ButtonElement)
                    button.add_value_listener(self._lane_mute_button_value, identify_sender=True)
            ##self._rebuild_callback()


    def q_step(self, index):
        q_map = [0.0625, #1/64
                 0.125, #1/32nd
                 0.25, #1/16th
                 0.5, #1/8th
                 1.0,] #1/4 note
                #2.0] #1/2 note
        return q_map[index]


    def _lane_mute_button_value(self, value, sender):
        assert (self._lane_mute_buttons != None)
        assert (list(self._lane_mute_buttons).count(sender) == 1)
        assert (value in range(128))
        if self.is_enabled() and self._is_active:
            if not self._shift_pressed: #set quantization when shift pressed
                if ((value is not 0) or (not sender.is_momentary())):
                    sender.turn_on()
                    self._quantization_index = (self._height - 1) - (list(self._lane_mute_buttons).index(sender)) #invert to get top to bottom index; range 0 to 4
                    self._update_quantization_buttons()
                    self._quantization = self.q_step(self._quantization_index)
                    self.update()

            elif self._sequencer_clip != None:
                if ((value is not 0) or (not sender.is_momentary())):
                    sender.turn_on()
                    lane_to_mute = (self._height - 1) - (list(self._lane_mute_buttons).index(sender)) #invert to get top to bottom index
                    pitch_to_mute = self._key_index + lane_to_mute #invert top to bottom
                    note_cache = list(self._clip_notes)
                    for note in self._clip_notes:
                        if note[0] == pitch_to_mute:
                            mute = False
                            if note[4] == False:
                                mute = True
                            note_to_mute = note
                            note_cache.remove(note)
                            note_cache.append([note_to_mute[0], note_to_mute[1], note_to_mute[2], note_to_mute[3], mute])
                    self._sequencer_clip.select_all_notes()
                    self._sequencer_clip.replace_selected_notes(tuple(note_cache)) 
                else:
                    sender.turn_off() #turn LED off on button release



    def set_nav_buttons(self, up, down, left, right):
        assert isinstance(up, (ButtonElement,
                               type(None)))
        assert isinstance(down, (ButtonElement,
                                 type(None)))
        assert isinstance(left, (ButtonElement,
                                 type(None)))
        assert isinstance(right, (ButtonElement,
                                  type(None)))
        if (self._nav_up_button != None):
            self._nav_up_button.remove_value_listener(self._nav_up_value)
        self._nav_up_button = up
        if (self._nav_up_button != None):
            self._nav_up_button.add_value_listener(self._nav_up_value)
        if (self._nav_down_button != None):
            self._nav_down_button.remove_value_listener(self._nav_down_value)
        self._nav_down_button = down
        if (self._nav_down_button != None):
            self._nav_down_button.add_value_listener(self._nav_down_value)
        if (self._nav_left_button != None):
            self._nav_left_button.remove_value_listener(self._nav_left_value)
        self._nav_left_button = left
        if (self._nav_left_button != None):
            self._nav_left_button.add_value_listener(self._nav_left_value)
        if (self._nav_right_button != None):
            self._nav_right_button.remove_value_listener(self._nav_right_value)
        self._nav_right_button = right
        if (self._nav_right_button != None):
            self._nav_right_button.add_value_listener(self._nav_right_value)
        ##self._rebuild_callback()
        self.update()


    def _nav_up_value(self, value):
        assert (self._nav_up_button != None)
        assert (value in range(128))
        if self.is_enabled() and self._is_active:
            button_is_momentary = self._nav_up_button.is_momentary()
            if button_is_momentary:
                if (value != 0):
                    self._scroll_up_ticks_delay = INITIAL_SCROLLING_DELAY
                else:
                    self._scroll_up_ticks_delay = -1            
            if ((value != 0) or (not self._nav_up_button.is_momentary())):
                if self._key_index < (128 - self._height):
                    self._key_index += 1
                    self._update_matrix()


    def _nav_down_value(self, value):
        assert (self._nav_down_button != None)
        assert (value in range(128))
        if self.is_enabled() and self._is_active:
            button_is_momentary = self._nav_down_button.is_momentary()
            if button_is_momentary:
                if (value != 0):
                    self._scroll_down_ticks_delay = INITIAL_SCROLLING_DELAY
                else:
                    self._scroll_down_ticks_delay = -1            
            if ((value != 0) or (not self._nav_down_button.is_momentary())):
                if self._key_index > 0:
                    self._key_index -= 1
                    self._update_matrix()


    def _nav_left_value(self, value):
        assert (self._nav_left_button != None)
        assert (value in range(128))
        if self.is_enabled() and self._is_active:
            button_is_momentary = self._nav_left_button.is_momentary()
            if button_is_momentary:
                if (value != 0):
                    self._scroll_left_ticks_delay = INITIAL_SCROLLING_DELAY
                else:
                    self._scroll_left_ticks_delay = -1            
            if ((value != 0) or (not self._nav_left_button.is_momentary())):
                if self._bank_index > 0:
                    self._bank_index -= 1
                    self._update_bank_buttons()
                    self._update_matrix()


    def _nav_right_value(self, value):
        assert (self._nav_right_button != None)
        assert (value in range(128))
        if self.is_enabled() and self._is_active:
            button_is_momentary = self._nav_right_button.is_momentary()
            if button_is_momentary:
                if (value != 0):
                    self._scroll_right_ticks_delay = INITIAL_SCROLLING_DELAY
                else:
                    self._scroll_right_ticks_delay = -1            
            if ((value != 0) or (not self._nav_right_button.is_momentary())):
                if self._bank_index < (self._width - 1):
                    self._bank_index += 1
                    self._update_bank_buttons()
                    self._update_matrix()

    def _on_timer(self):
        if self.is_enabled() and self._is_active:
            scroll_delays = [self._scroll_up_ticks_delay,
                             self._scroll_down_ticks_delay,
                             self._scroll_right_ticks_delay,
                             self._scroll_left_ticks_delay]
            if (scroll_delays.count(-1) < 4):
                bank_increment = 0
                key_increment = 0
                if (self._scroll_right_ticks_delay > -1):
                    if self._is_scrolling():
                        bank_increment += 1
                        self._scroll_right_ticks_delay = INTERVAL_SCROLLING_DELAY
                    self._scroll_right_ticks_delay -= 1
                if (self._scroll_left_ticks_delay > -1):
                    if self._is_scrolling():
                        bank_increment -= 1
                        self._scroll_left_ticks_delay = INTERVAL_SCROLLING_DELAY
                    self._scroll_left_ticks_delay -= 1
                if (self._scroll_down_ticks_delay > -1):
                    if self._is_scrolling():
                        key_increment -= 1
                        self._scroll_down_ticks_delay = INTERVAL_SCROLLING_DELAY
                    self._scroll_down_ticks_delay -= 1
                if (self._scroll_up_ticks_delay > -1):
                    if self._is_scrolling():
                        key_increment += 1
                        self._scroll_up_ticks_delay = INTERVAL_SCROLLING_DELAY
                    self._scroll_up_ticks_delay -= 1
                if (self._bank_index + bank_increment) < self._width and (self._bank_index + bank_increment) >= 0:
                    if self._bank_index + bank_increment != self._bank_index:
                        self._bank_index = self._bank_index + bank_increment
                        self._update_bank_buttons()
                        self._update_matrix()
                if (self._key_index + key_increment) < (128 - self._height + 1) and (self._key_index + key_increment) >=0:
                    if self._key_index + key_increment != self._key_index:
                        self._key_index = self._key_index + key_increment
                        self._update_matrix()



    def _is_scrolling(self):
        return (0 in (self._scroll_up_ticks_delay,
                      self._scroll_down_ticks_delay,
                      self._scroll_right_ticks_delay,
                      self._scroll_left_ticks_delay))
