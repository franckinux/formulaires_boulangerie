#!/usr/bin/env python
# -*- coding: utf-8 -*-


import wx
from wx.lib.pubsub import pub

import formules

if "phoenix" in wx.version():
    from wx.adv import AboutDialogInfo, AboutBox
    wx.EmptyImage = wx.Image  # EmptyImage has been removed in phoenix.
else:
    from wx import AboutDialogInfo, AboutBox


class InputField:

    def __init__(self, parent, label, value, process, min_max=None):
        self.static_text = wx.StaticText(parent, -1, label),
        self.text_ctrl = wx.TextCtrl(parent, -1, str(value))
        self.text_ctrl.Bind(wx.EVT_TEXT, self.check_value)
        self.label = label
        self.process = process
        self.min_max = min_max
        self.value = value
        self.error = False

    def get_widgets(self):
        return self.static_text, self.text_ctrl

    def check_value(self, ctrl):
        try:
            value = float(self.text_ctrl.GetValue())
            if value <= 0:
                raise ValueError("Negative value")
            if self.min_max and not self.min_max[0] <= value <= self.min_max[1]:
                raise ValueError("Out of range")
            self.value = value
        except:
            self.error = True
            self.text_ctrl.SetBackgroundColour("CORAL")
            pub.sendMessage("change_statusbar", msg=self.label + " incorrect")
        else:
            if self.error:
                self.text_ctrl.SetBackgroundColour("WHITE")
                pub.sendMessage("change_statusbar", msg="")
                self.error = False

        if not self.error:
            self.process()

    def get_value(self):
        return self.value if not self.error else -1


class TabPoidsLevainImpose(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        sizer_top = wx.BoxSizer(wx.HORIZONTAL)

        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        # entrées
        sizer_entrees = wx.BoxSizer(wx.VERTICAL)

        label_entrees = wx.StaticText(self, -1, "Données")
        label_entrees.SetFont(font)

        self.poids_levain = InputField(self, "Poids du levain", 150, self.update)
        self.th_pate = InputField(self, "Taux d'hydratation de la pâte", 60, self.update, min_max=(1, 100))
        self.th_levain = InputField(self, "Taux d'hydratation du levain", 100, self.update, min_max=(1, 100))
        self.taux_levain_farine = InputField(self, "Taux levain farine", 30, self.update, min_max=(1, 100))
        inputs = [
            self.poids_levain, self.th_pate, self.th_levain, self.taux_levain_farine
        ]

        grid_sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        widgets = []
        for inp in inputs:
            widgets.extend(inp.get_widgets())

        grid_sizer.AddMany(widgets)

        sizer_entrees.Add(label_entrees, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 10)
        sizer_entrees.Add(grid_sizer, 0, wx.LEFT, 10)

        # resultats
        sizer_resultats = wx.BoxSizer(wx.VERTICAL)

        label_resultats = wx.StaticText(self, -1, "Résultats")
        label_resultats.SetFont(font)

        self.label_poids_farine = wx.StaticText(self, -1)
        self.label_poids_eau = wx.StaticText(self, -1)
        self.label_poids_pate = wx.StaticText(self, -1)
        self.label_poids_sel = wx.StaticText(self, -1)

        grid_sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        grid_sizer.AddMany(
            [
                wx.StaticText(self, -1, "Poids de la farine"),
                self.label_poids_farine,
                wx.StaticText(self, -1, "Poids de l'eau"),
                self.label_poids_eau,
                wx.StaticText(self, -1, "Poids de la pâte"),
                self.label_poids_pate,
                wx.StaticText(self, -1, "Poids du sel"),
                self.label_poids_sel
            ]
        )

        sizer_resultats.Add(label_resultats, 0, wx.BOTTOM | wx.TOP, 10)
        sizer_resultats.Add(grid_sizer)

        # top sizer
        sizer_top.Add(sizer_entrees)
        sizer_top.Add(
            wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALL, 5
        )
        sizer_top.Add(sizer_resultats)
        self.SetSizerAndFit(sizer_top)

        self.update()

    def update(self):
        pl = self.poids_levain.get_value()
        thp = self.th_pate.get_value()
        thl = self.th_levain.get_value()
        tlf = self.taux_levain_farine.get_value()

        if pl != -1 and thp != -1 and thl != -1 and tlf != -1:
            pf, pe, ptp, ps = formules.calcul_eau_farine_pate(
                pl, thp / 100.0, thl / 100.0, tlf / 100.0
            )
            if pf > 0 and pe > 0:
                self.label_poids_farine.SetLabel(str(pf))
                self.label_poids_eau.SetLabel(str(pe))
                self.label_poids_pate.SetLabel(str(ptp))
                self.label_poids_sel.SetLabel(str(ps))
                pub.sendMessage("change_statusbar", msg="")
            else:
                self.label_poids_farine.SetLabel("")
                self.label_poids_eau.SetLabel("")
                self.label_poids_pate.SetLabel("")
                self.label_poids_sel.SetLabel("")
                pub.sendMessage("change_statusbar", msg="Données d'entrée incorrectes")


class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title=u"Formulaires de boulangerie", size=(500, 300))
        self.createMenuBar()

        panel = wx.Panel(self)

        notebook = wx.Notebook(panel)
        tab1 = TabPoidsLevainImpose(notebook)
        notebook.AddPage(tab1, "Poids du levain imposé")

        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetForegroundColour("RED")

        self.CenterOnScreen()

        pub.subscribe(self.change_statusbar, 'change_statusbar')

    def createMenuBar(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_EXIT, "Quitter\tCtrl+Q")
        self.Bind(wx.EVT_MENU, lambda x: self.Destroy(), id=wx.ID_EXIT)
        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ABOUT, "A propos de Production")
        self.Bind(wx.EVT_MENU, self.onShowAbout, id=wx.ID_ABOUT)
        menubar.SetMenus([(fileMenu, "Fichier"), (helpMenu, "Help")])
        self.SetMenuBar(menubar)

    def change_statusbar(self, msg):
        self.statusbar.SetStatusText(msg)

    def onShowAbout(self, evt):
        info = AboutDialogInfo()
        info.SetVersion("1.0")
        info.SetName("Production")
        info.SetDescription("Formuliares de boulanboub")
        info.SetCopyright(u"Franck Barbenoire (2017)")
        AboutBox(info)


class TestApp(wx.App):
    def OnInit(self):
        frame = TestFrame()
        frame.Show()
        frame.Layout()
        return True


if __name__ == "__main__":
    app = TestApp()
    app.MainLoop()
