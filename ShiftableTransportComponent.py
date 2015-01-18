# http://remotescripts.blogspot.com

# partial --== Decompile ==-- with fixes
import Live
from CustomTransportComponent import CustomTransportComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement

class ShiftableTransportComponent(CustomTransportComponent):
    __doc__ = ' CustomTransportComponent that only uses certain buttons if a shift button is pressed '
    def __init__(self):
        CustomTransportComponent.__init__(self)
        self._shift_button = None
        self._quant_toggle_button = None
        self._shift_pressed = False
        self._last_quant_value = Live.Song.RecordingQuantization.rec_q_eight
        self.song().add_midi_recording_quantization_listener(self._on_quantisation_changed)
        self._on_quantisation_changed()
        self._undo_button = None 
        self._redo_button = None 
        self._bts_button = None 
        self._tempo_encoder_control = None
        return None

    def disconnect(self):
        CustomTransportComponent.disconnect(self)
        if self._shift_button != None:
            self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = None
        if self._quant_toggle_button != None:
            self._quant_toggle_button.remove_value_listener(self._quant_toggle_value)
            self._quant_toggle_button = None
        self.song().remove_midi_recording_quantization_listener(self._on_quantisation_changed)
        if (self._undo_button != None): 
            self._undo_button.remove_value_listener(self._undo_value)
            self._undo_button = None
        if (self._redo_button != None): 
            self._redo_button.remove_value_listener(self._redo_value)
            self._redo_button = None
        if (self._bts_button != None): 
            self._bts_button.remove_value_listener(self._bts_value)
            self._bts_button = None
        if (self._tempo_encoder_control != None):
            self._tempo_encoder_control.remove_value_listener(self._tempo_encoder_value)
            self._tempo_encoder_control = None
        return None

    def set_shift_button(self, button):
        if not(button == None or isinstance(button, ButtonElement) and button.is_momentary()):
            isinstance(button, ButtonElement)
            raise AssertionError
        if self._shift_button != button:
            if self._shift_button != None:
                self._shift_button.remove_value_listener(self._shift_value)
            self._shift_button = button
            if self._shift_button != None:
                self._shift_button.add_value_listener(self._shift_value)
            self.update()
        return None

    def set_quant_toggle_button(self, button):
        if not(button == None or isinstance(button, ButtonElement) and button.is_momentary()):
            isinstance(button, ButtonElement)
            raise AssertionError
        if self._quant_toggle_button != button:
            if self._quant_toggle_button != None:
                self._quant_toggle_button.remove_value_listener(self._quant_toggle_value)
            self._quant_toggle_button = button
            if self._quant_toggle_button != None:
                self._quant_toggle_button.add_value_listener(self._quant_toggle_value)
            self.update()
        return None

    def update(self):
        self._on_metronome_changed()
        self._on_overdub_changed()
        self._on_quantisation_changed()
        self._on_nudge_up_changed() 
        self._on_nudge_down_changed 

    def _shift_value(self, value):
        if not self._shift_button != None:
            raise AssertionError
        if not value in range(128):
            raise AssertionError
        self._shift_pressed = value != 0
        if self.is_enabled():
            self.is_enabled()
            self.update()
        else:
            self.is_enabled()
        return None

    def _metronome_value(self, value):
        if not self._shift_pressed:
            CustomTransportComponent._metronome_value(self, value)


    def _overdub_value(self, value):
        if not self._shift_pressed:
            CustomTransportComponent._overdub_value(self, value)


    def _nudge_up_value(self, value): 
        if not self._shift_pressed:
            CustomTransportComponent._nudge_up_value(self, value)
            

    def _nudge_down_value(self, value): 
        if not self._shift_pressed:
            CustomTransportComponent._nudge_down_value(self, value)            
            
            
    def _tap_tempo_value(self, value): 
        if not self._shift_pressed:
            CustomTransportComponent._tap_tempo_value(self, value)


    def _quant_toggle_value(self, value):
        assert (self._quant_toggle_button != None)
        assert (value in range(128))
        assert (self._last_quant_value != Live.Song.RecordingQuantization.rec_q_no_q)
        if (self.is_enabled() and (not self._shift_pressed)):
            if ((value != 0) or (not self._quant_toggle_button.is_momentary())):
                quant_value = self.song().midi_recording_quantization
                if (quant_value != Live.Song.RecordingQuantization.rec_q_no_q):
                    self._last_quant_value = quant_value
                    self.song().midi_recording_quantization = Live.Song.RecordingQuantization.rec_q_no_q
                else:
                    self.song().midi_recording_quantization = self._last_quant_value


    def _on_metronome_changed(self):
        if not self._shift_pressed:
            CustomTransportComponent._on_metronome_changed(self)


    def _on_overdub_changed(self):
        if not self._shift_pressed:
            CustomTransportComponent._on_overdub_changed(self)


    def _on_nudge_up_changed(self): 
        if not self._shift_pressed:
            CustomTransportComponent._on_nudge_up_changed(self)


    def _on_nudge_down_changed(self): 
        if not self._shift_pressed:
            CustomTransportComponent._on_nudge_down_changed(self)


    def _on_quantisation_changed(self):
        if self.is_enabled():
            quant_value = self.song().midi_recording_quantization
            quant_on = (quant_value != Live.Song.RecordingQuantization.rec_q_no_q)
            if quant_on:
                self._last_quant_value = quant_value
            if ((not self._shift_pressed) and (self._quant_toggle_button != None)):
                if quant_on:
                    self._quant_toggle_button.turn_on()
                else:
                    self._quant_toggle_button.turn_off()

    """ from OpenLabs module SpecialCustomTransportComponent """
    
    def set_undo_button(self, undo_button):
        assert isinstance(undo_button, (ButtonElement,
                                        type(None)))
        if (undo_button != self._undo_button):
            if (self._undo_button != None):
                self._undo_button.remove_value_listener(self._undo_value)
            self._undo_button = undo_button
            if (self._undo_button != None):
                self._undo_button.add_value_listener(self._undo_value)
            self.update()



    def set_redo_button(self, redo_button):
        assert isinstance(redo_button, (ButtonElement,
                                        type(None)))
        if (redo_button != self._redo_button):
            if (self._redo_button != None):
                self._redo_button.remove_value_listener(self._redo_value)
            self._redo_button = redo_button
            if (self._redo_button != None):
                self._redo_button.add_value_listener(self._redo_value)
            self.update()


    def set_bts_button(self, bts_button): 
        assert isinstance(bts_button, (ButtonElement,
                                       type(None)))
        if (bts_button != self._bts_button):
            if (self._bts_button != None):
                self._bts_button.remove_value_listener(self._bts_value)
            self._bts_button = bts_button
            if (self._bts_button != None):
                self._bts_button.add_value_listener(self._bts_value)
            self.update()


    def _undo_value(self, value):
        if self._shift_pressed: 
            assert (self._undo_button != None)
            assert (value in range(128))
            if self.is_enabled():
                if ((value != 0) or (not self._undo_button.is_momentary())):
                    if self.song().can_undo:
                        self.song().undo()


    def _redo_value(self, value):
        if self._shift_pressed: 
            assert (self._redo_button != None)
            assert (value in range(128))
            if self.is_enabled():
                if ((value != 0) or (not self._redo_button.is_momentary())):
                    if self.song().can_redo:
                        self.song().redo()


    def _bts_value(self, value):
        assert (self._bts_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if ((value != 0) or (not self._bts_button.is_momentary())):
                self.song().current_song_time = 0.0
     
        
    def _tempo_encoder_value(self, value):
        if self._shift_pressed:
            assert (self._tempo_encoder_control != None)
            assert (value in range(128))
            backwards = (value >= 64)
            step = 0.1 
            if backwards:
                amount = (value - 128)
            else:
                amount = value
            tempo = max(20, min(999, (self.song().tempo + (amount * step))))
            self.song().tempo = tempo

            
        
    def set_tempo_encoder(self, control):
        assert ((control == None) or (isinstance(control, EncoderElement) and (control.message_map_mode() is Live.MidiMap.MapMode.relative_two_compliment)))
        if (self._tempo_encoder_control != None):
            self._tempo_encoder_control.remove_value_listener(self._tempo_encoder_value)
        self._tempo_encoder_control = control
        if (self._tempo_encoder_control != None):
            self._tempo_encoder_control.add_value_listener(self._tempo_encoder_value)
        self.update()