#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import wx
from wx.lib.expando import ExpandoTextCtrl, EVT_ETC_LAYOUT_NEEDED


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((690, 340))

        # Create 3 new panels:
        newPanel = TilePanel(self, wx.ID_ANY)
        newPanel.SetImage(wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MESSAGE_BOX, size=wx.Size(80, 80)))
        newPanel.SetText(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum fringilla justo ut ante laoreet consectetur. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.")
        newPanel.SetButton("View More...", callback=self.OnMyCustomHandler)

        newPanel2 = TilePanel(self, wx.ID_ANY)
        newPanel2.SetImage(wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_MESSAGE_BOX, size=wx.Size(80, 80)))
        newPanel2.SetText(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum fringilla justo ut ante laoreet consectetur. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.")
        newPanel2.SetButton("View More...", callback=self.OnMyCustomHandler)

        newPanel3 = TilePanel(self, wx.ID_ANY)
        newPanel3.SetImage(wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_MESSAGE_BOX, size=wx.Size(80, 80)))
        newPanel3.SetText(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum fringilla justo ut ante laoreet consectetur. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.")
        newPanel3.SetButton("View More...", callback=self.OnMyCustomHandler)

        self._panels = []
        self._panels.append(newPanel)
        self._panels.append(newPanel2)
        self._panels.append(newPanel3)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("frame")
        self.SetBackgroundColour(wx.Colour(220, 220, 220))

    def __do_layout(self):
        # Create a wrap sizer:
        sizer_1 = wx.WrapSizer(wx.HORIZONTAL)

        # Add panels to the sizer:
        for panel in self._panels:
            sizer_1.Add(panel, 0, wx.ALL, 2)

        self.SetSizer(sizer_1)
        self.Layout()

    def OnMyCustomHandler(self, event):
        print('{} has clicked'.format(event.GetEventObject().GetId()))

    # TilePanel Class


class TilePanel(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.text_ctrl_1 = ExpandoTextCtrl(self, wx.ID_ANY, "No text set",
                                           style=wx.BORDER_NONE | wx.TE_CENTRE | wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
        self.button_1 = wx.Button(self, wx.ID_ANY, "No button text")
        self.stBmp = wx.StaticBitmap(self, wx.ID_ANY)
        self.sizer_flexi = wx.FlexGridSizer(3, 1, 0, 0)
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.text_ctrl_1.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.text_ctrl_1.SetMinSize((200, -1))
        self.button_1.SetMinSize((100, 40))
        self.button_1.SetBackgroundColour(wx.Colour(255, 255, 255))

    def __do_layout(self):
        self.SetSizer(self.sizer_flexi)
        self.sizer_flexi.Fit(self)
        self.sizer_flexi.AddGrowableRow(1)
        self.sizer_flexi.AddGrowableCol(0)
        self.Layout()

    def SetImage(self, bmp):
        self.stBmp.SetBitmap(bmp)
        self.sizer_flexi.Add(self.stBmp, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.Layout()

    def SetText(self, text):
        self.text_ctrl_1.SetValue(text)
        self.sizer_flexi.Add(self.text_ctrl_1, 1, wx.EXPAND | wx.ALL, 10)
        self.Layout()

    def SetButton(self, btnTitle, callback):
        self.button_1.SetLabel(btnTitle)
        self.button_1.Bind(wx.EVT_BUTTON, callback)
        self.sizer_flexi.Add(self.button_1, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        self.Layout()


# end of class TilePanel


# Main App:
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()