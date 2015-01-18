# http://remotescripts.blogspot.com

# emacs-mode: -*- python-*-
# -*- coding: utf-8 -*-

from _Framework.ChannelStripComponent import ChannelStripComponent 
from _Framework.EncoderElement import EncoderElement # added
TRACK_FOLD_DELAY = 5
class SpecialChanStripComponent(ChannelStripComponent):
    ' Subclass of channel strip component using select button for (un)folding tracks '
    __module__ = __name__

    def __init__(self):
        ChannelStripComponent.__init__(self)
        self._toggle_fold_ticks_delay = -1
        self._register_timer_callback(self._on_timer)

    def disconnect(self):
        self._unregister_timer_callback(self._on_timer)
        ChannelStripComponent.disconnect(self)

    def set_send_controls(self, controls): # override with pre 8.2.5 code
        assert ((controls == None) or isinstance(controls, tuple))
        if (controls != self._send_controls):
            self._send_controls = controls
            self.update()

    def set_pan_control(self, control): # override with pre 8.2.5 code
        assert ((control == None) or isinstance(control, EncoderElement))
        self._pan_control = control

    def set_volume_control(self, control): # override with pre 8.2.5 code
        assert ((control == None) or isinstance(control, EncoderElement))
        if (control != self._volume_control):
            self._volume_control = control
            self.update()        
                
    def _select_value(self, value):
        ChannelStripComponent._select_value(self, value)
        if (self.is_enabled() and (self._track != None)):
            if (self._track.is_foldable and (self._select_button.is_momentary() and (value != 0))):
                self._toggle_fold_ticks_delay = TRACK_FOLD_DELAY
            else:
                self._toggle_fold_ticks_delay = -1

    def _on_timer(self):
        if (self.is_enabled() and (self._track != None)):
            if (self._toggle_fold_ticks_delay > -1):
                assert self._track.is_foldable
                if (self._toggle_fold_ticks_delay == 0):
                    self._track.fold_state = (not self._track.fold_state)
                self._toggle_fold_ticks_delay -= 1


# local variables:
# tab-width: 4