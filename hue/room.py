# -*- coding: utf-8 -*-
import wx
from .light import Light


class Room(wx.Panel):
    def __init__(self, parent, room_state, lights={}):
        wx.Panel.__init__(self, parent=parent)
        colors = ["red", "blue", "gray", "yellow", "green"]
        self.room_id = room_state['id']
        self.name = room_state['metadata']['name']
        print("Creating room "+self.room_id+" ("+self.name+")")
        self.lights = {}
        self.panels = []
        self.state = room_state
        for light_id, light in lights.items():
            for child in self.state['children']:
                if child['rid'] == light['owner']['rid']:
                    self.lights[child['rid']] = light
                    self.panels.append(Light(self, wx.ID_ANY, light_id=light_id, light_state=light))

        t = wx.BoxSizer(wx.VERTICAL)
        t = wx.FlexGridSizer(len(self.panels), 1, 0, 0)
        for panel in self.panels:
            t.Add(panel, wx.ALL, 2)

        self.SetSizer(t)
        self.Layout()
