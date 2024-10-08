# -*- coding: utf-8 -*-
import wx
from wx.lib.expando import ExpandoTextCtrl


class Light(wx.Panel):
    def __init__(self, *args, light_id, light_state, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwargs)

        # First we set up our controls
        self.name_ctrl = self.get_new_name_control()
        self.toggle_button = self.get_new_toggle_button()
        self.slider_box = wx.GridSizer(cols=2, gap=wx.Size(2, 2))
        self.brightness_slider_label = self.get_new_label('Brightness')
        self.brightness_slider = self.get_new_brightness_slider()
        self.slider_box.Add(self.brightness_slider_label, 0, wx.ALIGN_RIGHT)
        self.slider_box.Add(self.brightness_slider, 0, wx.ALIGN_LEFT)
        self.color_slider_label = self.get_new_label('Color temperature')
        self.color_slider = self.get_new_color_slider()
        self.slider_box.Add(self.color_slider_label, 0, wx.ALIGN_RIGHT)
        self.slider_box.Add(self.color_slider, 0, wx.ALIGN_LEFT)

        # Set up our data
        self.light_id = light_id
        self.state = None
        self.expected_updates = 0
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
        self.sizer_flexi.Add(self.slider_box)
        self.Layout()

    def get_new_label(self, text):
        """
        Generates a new label
        :param text:
        :return:
        """
        control = wx.StaticText(self, wx.ID_ANY, text)
        return control

    def get_new_name_control(self):
        """
        Creates the name label text control
        :return:
        """
        control = wx.StaticText(self, wx.ID_ANY, "")
        font = control.GetFont()
        font.SetPointSize(18)
        control.SetFont(font)
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
        Creates color slider
        :return:
        """
        slider = wx.Slider(self, wx.ID_ANY, 1, 1, 100, style=wx.TE_CENTRE)
        slider.SetMinSize((200, 40))
        slider.Bind(wx.EVT_SLIDER, self.set_color_temperature)
        return slider

    def set_state(self, state):
        """
        Update the panel's state using supplied state from the Clipv2 API
        :param state:
        :return:
        """
        self.state = state
        self.brightness_slider.SetValue(int(state['dimming']['brightness']))
        self.brightness_slider.SetMin(int(state['dimming']['min_dim_level']))
        self.brightness_slider.Enable(self.is_on())

        self.color_slider.SetMin(int(state['color_temperature']['mirek_schema']['mirek_minimum']))
        self.color_slider.SetMax(int(state['color_temperature']['mirek_schema']['mirek_maximum']))
        self.color_slider.SetValue(int(state['color_temperature']['mirek']))
        self.color_slider.Enable(self.is_on())

        self.name = state['metadata']['name']
        self.name_ctrl.SetLabel(self.name)
        self.toggle_button.SetLabelText("Turn off" if self.is_on() else "Turn on")

    def __set_properties(self):
        """
        Set panel properties
        :return:
        """
        self.name_ctrl.SetMinSize((400, -1))
        self.name_ctrl.SetMaxSize((400, -1))
        self.name_ctrl.SetPosition((10, 0))
        self.toggle_button.SetMinSize((100, 40))
        self.toggle_button.SetPosition((420, 0))
        self.brightness_slider.SetSize((400, 20))
        self.brightness_slider.SetPosition((10, 90))

    def toggle(self, event):
        """
        Toggle light on state
        :param event:
        :return:
        """
        if self.is_on():
            self.new_state['on'] = {
                'on': False
            }
        else:
            self.new_state['on'] = {
                'on': True
            }

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

    def set_color_temperature(self, event):
        """
        Queues up a color temperature change
        :param event:
        :return:
        """
        slider_value = self.color_slider.GetValue()
        if slider_value < self.state['color_temperature']['mirek_schema']['mirek_minimum']\
                or slider_value > self.state['color_temperature']['mirek_schema']['mirek_maximum']:
            return

        self.new_state['color_temperature'] = {
            'mirek': slider_value
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
        self.name_ctrl.SetLabel(text)
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
