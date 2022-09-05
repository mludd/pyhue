#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-


import wx
from hue import Clipv2, Room, Light
from worker import Response, Request, Worker
from queue import Queue
from time import time_ns


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "PyHue", size=(600, 1200))
        panel = wx.Panel(self)
        self._notebook = wx.Notebook(panel)

        # Add tabs here
        self.hue = Clipv2()
        rooms = self.hue.list_rooms()
        lights = self.hue.list_lights()

        # Load room tabs
        for room_id, room in rooms.items():
            room_panel = Room(self._notebook, room, lights)
            self._notebook.AddPage(room_panel, room_panel.name)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()

        self.Show()

        # Worker thread setup
        self.request_queue = Queue()
        self.thread = Worker(self.request_queue)
        self.thread.start()

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

        for tab in self._notebook.GetChildren():
            for light_panel in tab.panels:
                if light_panel.new_state:
                    self.thread.request_queue.put(Request('set_light_state', light_panel.new_state, light_panel.light_id))
                    light_panel.new_state = {}
                    light_panel.expected_updates += 1

        while not self.thread.response_queue.empty():
            response = self.thread.response_queue.get()
            if response.light_id and response.payload:
                light_panel = self.get_light_panel_with_id(response.light_id)
                if light_panel:
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
        for tab in self._notebook.GetChildren():
            for light_panel in tab.panels:
                if light_panel.light_id == light_id:
                    return light_panel
            return None


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
