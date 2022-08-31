#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-

import wx
from hue import Clipv2, Light
from worker import Worker, Request
from queue import Queue
from time import time_ns


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetSize((600, 1200))

        # Worker thread setup
        self.request_queue = Queue()
        self.thread = Worker(self.request_queue)
        self.thread.start()

        # Load all lights from the API
        self._panels = []
        self.hue = Clipv2()
        lights = self.hue.list_lights()
        for light_id, light in lights.items():
            light_panel = Light(self, wx.ID_ANY, light_id=light_id, light_state=light, **kwargs)
            self._panels.append(light_panel)

        self.__do_layout()

        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Set up a timer to regularly poll the light states from the API
        self.busy = False
        self.timer = wx.Timer(self)
        self.last_full_update = time_ns()
        self.timer.Start(200)
        self.Bind(wx.EVT_TIMER, self.update_light_states)

    def on_close(self, event):
        """
        Executes every time the main frame closes
        :return:
        """
        self.Destroy()

    def update_light_states(self, event):
        """
        Update the light states
        :param event:
        :return:
        """
        if self.busy:
            return
        self.busy = True

        if time_ns() > self.last_full_update + 1000000000:
            self.request_queue.put(Request('list_lights'))
            self.last_full_update = time_ns()

        for light_panel in self._panels:
            if light_panel.new_state:
                self.thread.request_queue.put(Request('set_light_state', light_panel.new_state, light_panel.light_id))
                light_panel.new_state = {}
                light_panel.expected_updates += 1

        while not self.thread.response_queue.empty():
            response = self.thread.response_queue.get()
            if response.light_id and response.payload:
                light_panel = self.get_light_panel_with_id(response.light_id)
                if light_panel.expected_updates <= 1:
                    light_panel.set_state(response.payload)
                if light_panel.expected_updates > 0:
                    light_panel.expected_updates -= 1
            elif not response.light_id:
                self.set_light_states(response.payload)

        self.busy = False

    def set_light_states(self, lights):
        """
        Update all lights that are found in input as long as they aren't expecting state updates
        :param lights:
        :return:
        """
        for light_id, light in lights.items():
            light_panel = self.get_light_panel_with_id(light_id)
            if light_panel and light_panel.expected_updates == 0:
                light_panel.set_state(light)

    def get_light_panel_with_id(self, light_id):
        """
        Fetches the matching light panel or None if one can't be found
        :param light_id:
        :return:
        """
        for light_panel in self._panels:
            if light_panel.light_id == light_id:
                return light_panel
        return None

    def __do_layout(self):
        """
        Set up some layout stuff for the frame
        :return:
        """
        self.SetTitle("PyHue")

        # Create a wrap sizer:
        sizer_1 = wx.WrapSizer(wx.HORIZONTAL)

        # Add panels to the sizer:
        for light_panel in self._panels:
            sizer_1.Add(light_panel, 0, wx.ALL, 2)

        self.SetSizer(sizer_1)
        self.Layout()


class App(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = App(0)
    app.MainLoop()
