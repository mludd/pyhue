# -*- coding: utf-8 -*-
import wx
from wx.lib.expando import ExpandoTextCtrl
from .clipv2 import Clipv2


class Light(wx.Panel):
    def __init__(self, *args, light_id, light_state, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwargs)

        # First we set up our controls
        self.name_ctrl = self.get_new_name_control()
        self.toggle_button = self.get_new_toggle_button()
        self.brightness_slider = self.get_new_brightness_slider()
        self.color_slider = self.get_new_color_slider()

        # Set up our data
        self.light_id = light_id
        self.state = None
        self.waiting_on_update = False
        self.new_state = {}
        self.name = ''
        self.set_state(light_state)

        # Layout
        self.sizer_flexi = wx.FlexGridSizer(3, 1, 0, 0)
        self.SetSizer(self.sizer_flexi)
        self.SetSize((800, 200))
        self.sizer_flexi.Fit(self)
        self.sizer_flexi.AddGrowableRow(1)
        self.sizer_flexi.AddGrowableCol(0)
        self.sizer_flexi.Add(self.name_ctrl)
        self.sizer_flexi.Add(self.toggle_button)
        self.sizer_flexi.Add(self.brightness_slider)
        self.Layout()

    def get_new_name_control(self):
        """
        Creates the name label text control
        :return:
        """
        control = ExpandoTextCtrl(self, wx.ID_ANY, "",
                                  style=wx.BORDER_NONE | wx.TE_CENTRE | wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
        control.SetMinSize((550, 40))
        control.SetPosition((0, 0))
        return control

    def get_new_toggle_button(self):
        """
        Creates the toggle button control
        :return:
        """
        button = wx.Button(self, wx.ID_ANY, "")
        button.Bind(wx.EVT_BUTTON, self.toggle)
        button.SetMinSize((100, 40))
        button.SetPosition((200, 0))
        return button

    def get_new_brightness_slider(self):
        """
        Creates the brightness slider
        :return:
        """
        slider = wx.Slider(self, wx.ID_ANY, 1, 1, 100, style=wx.TE_CENTRE)
        slider.SetMinSize((200, 40))
        slider.Bind(wx.EVT_SLIDER, self.set_brightness)
        return slider

    def get_new_color_slider(self):
        """
        Todo: Creates color slider
        :return:
        """
        return False

    def set_state(self, state):
        self.state = state
        self.brightness_slider.SetValue(int(state['dimming']['brightness']))
        self.brightness_slider.SetMin(int(state['dimming']['min_dim_level']))
        self.brightness_slider.Enable(self.is_on())
        self.name = state['metadata']['name']
        self.name_ctrl.SetValue(self.name)
        self.toggle_button.SetLabelText("Turn off" if self.is_on() else "Turn on")

    def __set_properties(self):
        self.name_ctrl.SetMinSize((400, -1))
        self.name_ctrl.SetMaxSize((400, -1))
        self.name_ctrl.SetPosition((10, 0))
        self.toggle_button.SetMinSize((100, 40))
        self.toggle_button.SetPosition((420, 0))
        self.brightness_slider.SetSize((400, 20))
        self.brightness_slider.SetPosition((10, 90))

    def toggle(self, event):
        if self.is_on():
            # h.turn_off_light(self.light_id)
            self.new_state['on'] = {
                'on': False
            }
        else:
            # h.turn_on_light(self.light_id)
            self.new_state['on'] = {
                'on': True
            }

        # state = h.get_light_state(self.light_id)
        # self.set_state(state)

    def set_brightness(self, event):
        """
        Queues up a brightness change
        :param event:
        :return:
        """
        slider_value = self.brightness_slider.GetValue()
        if slider_value < self.state['dimming']['min_dim_level'] or slider_value > 100:
            return

        self.new_state['dimming'] = {
            'brightness': slider_value
        }

    def is_on(self):
        """
        Gets the light's on status
        :return:
        """
        return self.state['on']['on']

    def set_id(self, light_id):
        """
        Sets the light's light_id
        :param light_id:
        :return:
        """
        self.light_id = light_id

    def set_text(self, text):
        """
        Updates the light's name in the panel
        :param text:
        :return:
        """
        self.name_ctrl.SetValue(text)
        self.sizer_flexi.Add(self.name_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        self.Layout()

    def get_button_label(self):
        """
        :return:
        """
        return 'Turn off' if self.is_on() else 'Turn on'

    def set_button(self):
        """
        Updates the state of the button
        :return:
        """
        self.toggle_button.SetLabel(self.get_button_label())
        self.toggle_button.Bind(wx.EVT_BUTTON, self.toggle)
        self.sizer_flexi.Add(self.toggle_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        self.Layout()
