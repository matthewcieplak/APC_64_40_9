"""
New Class to emulate APC20 ShiftableZoomingComponent
Required to be able to shift on Session Zooming.

Customized APC40 control surface script
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
from _Framework.SessionZoomingComponent import * 
from _Framework.ButtonElement import ButtonElement

class ShiftableZoomingComponent(DeprecatedSessionZoomingComponent):
    """ Special ZoomingComponent that uses clip stop buttons for stop all when zoomed """

    def __init__(self, session, stop_buttons):
        DeprecatedSessionZoomingComponent.__init__(self, session)
        self._stop_buttons = stop_buttons
        self._ignore_buttons = False
        for button in self._stop_buttons:
            assert isinstance(button, ButtonElement)
            button.add_value_listener(self._stop_value, identify_sender=True)

    def disconnect(self):
        DeprecatedSessionZoomingComponent.disconnect(self)
        for button in self._stop_buttons:
            button.remove_value_listener(self._stop_value)

    def set_ignore_buttons(self, ignore):
        assert isinstance(ignore, type(False))
        if self._ignore_buttons != ignore:
            self._ignore_buttons = ignore
            self._is_zoomed_out or self._session.set_enabled(not ignore)
        self.update()

    def update(self):
        if not self._ignore_buttons:
            DeprecatedSessionZoomingComponent.update(self)
        elif self.is_enabled():
            if self._scene_bank_buttons != None:
                for button in self._scene_bank_buttons:
                    button.turn_off()

    def _stop_value(self, value, sender):
        if not value in range(128):
            raise AssertionError
            if not sender != None:
                raise AssertionError
                self.is_enabled() and not self._ignore_buttons and self._is_zoomed_out and (value != 0 or not sender.is_momentary()) and self.song().stop_all_clips()

    def _zoom_value(self, value):
        if not self._zoom_button != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                if self.is_enabled():
                    if self._zoom_button.is_momentary():
                        self._is_zoomed_out = value > 0
                    else:
                        self._is_zoomed_out = not self._is_zoomed_out
                    if not self._ignore_buttons:
                        self._scene_bank_index = self._is_zoomed_out and int(self._session.scene_offset() / self._session.height() / self._buttons.height())
                    else:
                        self._scene_bank_index = 0
                    self._session.set_enabled(not self._is_zoomed_out)
                    self._is_zoomed_out and self.update()

    def _matrix_value(self, value, x, y, is_momentary):
        if not self._ignore_buttons:
            DeprecatedSessionZoomingComponent._matrix_value(self, value, x, y, is_momentary)

    def _nav_up_value(self, value):
        if not self._ignore_buttons:
            DeprecatedSessionZoomingComponent._nav_up_value(self, value)

    def _nav_down_value(self, value):
        if not self._ignore_buttons:
            DeprecatedSessionZoomingComponent._nav_down_value(self, value)

    def _nav_left_value(self, value):
        if not self._ignore_buttons:
            DeprecatedSessionZoomingComponent._nav_left_value(self, value)

    def _nav_right_value(self, value):
        if not self._ignore_buttons:
            DeprecatedSessionZoomingComponent._nav_right_value(self, value)

    def _scene_bank_value(self, value, sender):
        if not self._ignore_buttons:
            DeprecatedSessionZoomingComponent._scene_bank_value(self, value, sender)