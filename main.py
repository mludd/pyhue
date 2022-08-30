#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-

import wx
from hue import Clipv2, Light
from worker import Worker, Request, Response
from queue import Queue


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        kwargs["style"] = kwargs.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetSize((600, 900))

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
        self.timer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.update_light_states)

    def on_close(self, event):
        """
        Executes every time the main frame closes
        :return:
        """
        self.thread.stop()
        self.thread.join()
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

        print("Putting list_lights request on queue")
        self.request_queue.put(Request('list_lights'))

        for light_panel in self._panels:
            if light_panel.new_state:
                self.thread.request_queue.put(Request('set_light_state', light_panel.new_state, light_panel.light_id))

        while not self.thread.response_queue.empty():
            response = self.thread.response_queue.get()
            print("Found response:")
            print(response)
            if response.light_id and response.payload:
                print("Updating state for individual light "+response.light_id)
                self.get_light_panel_with_id(response.light_id).set_state(response.payload)
            elif not response.light_id:
                print("Found complete state update, updating state for all lights")
                self.set_light_states(response.payload)

        self.busy = False

    def set_light_states(self, lights):
        for light_id, light in lights.items():
            light_panel =  self.get_light_panel_with_id(light_id)
            if light_panel:
                light_panel.set_state(light)

    def get_light_panel_with_id(self, light_id):
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