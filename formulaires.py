#!/usr/bin/env python

# license : GPL 3.0
# copyright : Franck Barbenoire (franck@barbenoi.re)

from jinja2 import Environment, FileSystemLoader
import os
from tempfile import NamedTemporaryFile
import webbrowser
import wx
from wx.lib.pubsub import pub

import formules

from wx.adv import AboutDialogInfo, AboutBox
wx.EmptyImage = wx.Image  # EmptyImage has been removed in phoenix.


class InputField:

    def __init__(self, parent, label, value, process, min_max=None):
        self.static_text = wx.StaticText(parent, -1, label),
        self.text_ctrl = wx.TextCtrl(parent, -1, str(value))
        self.text_ctrl.Bind(wx.EVT_TEXT, self.check_value)
        self.label = label
        self.process = process
        self.min_max = min_max
        self.value = float(value)
        self.error = False

    def get_widgets(self):
        return self.static_text, self.text_ctrl

    def check_value(self, ctrl):
        try:
            value = float(self.text_ctrl.GetValue())
            if value <= 0:
                raise ValueError("Negative or null value")
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

    def get_label(self):
        return self.label

    def get_value(self):
        return self.value if not self.error else -1


class OutputField:

    def __init__(self, parent, label):
        self.static_text_label = wx.StaticText(parent, -1, label)
        self.static_text_value = wx.StaticText(parent, -1)
        self.label = label
        self.value = -1

    def get_widgets(self):
        return self.static_text_label, self.static_text_value

    def set_value(self, value):
        self.value = value
        self.static_text_value.SetLabel(str(value))

    def get_label(self):
        return self.label

    def get_value(self):
        return self.value


class TabCommon(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.init_ui(parent)
        self.init_html()

    def init_ui(self, parent):
        sizer_top = wx.BoxSizer(wx.HORIZONTAL)

        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.set_fields()

        # entrées
        sizer_entrees = wx.BoxSizer(wx.VERTICAL)

        label_entrees = wx.StaticText(self, -1, "Données")
        label_entrees.SetFont(font)

        grid_sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        widgets = []
        for inp in self.inputs:
            widgets.extend(inp.get_widgets())
        grid_sizer.AddMany(widgets)

        sizer_entrees.Add(label_entrees, 0, wx.BOTTOM | wx.LEFT | wx.TOP, 10)
        sizer_entrees.Add(grid_sizer, 0, wx.LEFT, 10)

        # resultats
        sizer_resultats = wx.BoxSizer(wx.VERTICAL)

        label_resultats = wx.StaticText(self, -1, "Résultats")
        label_resultats.SetFont(font)

        grid_sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        widgets = []
        for out in self.outputs:
            widgets.extend(out.get_widgets())
        grid_sizer.AddMany(widgets)

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

    def init_html(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.env = Environment(
            autoescape=True,
            loader=FileSystemLoader(os.path.join(path, 'templates'))
        )

    def to_html(self, title):
        context = {
            "title": title,
            "fields": {
                "inputs": self.inputs,
                "outputs": self.outputs
            }
        }
        return(self.env.get_template("double-columns.html").render(context))


class TabPoidsLevainImpose(TabCommon):

    def __init__(self, parent):
        self.result = False
        super(TabPoidsLevainImpose, self).__init__(parent)

    def set_fields(self):
        self.poids_levain = InputField(self, "Poids du levain", 150, self.update)
        self.th_pate = InputField(self, "Taux d'hydratation de la pâte", 60, self.update, min_max=(1, 100))
        self.th_levain = InputField(self, "Taux d'hydratation du levain", 100, self.update, min_max=(1, 100))
        self.taux_levain_farine = InputField(self, "Taux levain farine", 30, self.update, min_max=(1, 100))
        self.inputs = [
            self.poids_levain, self.th_pate, self.th_levain, self.taux_levain_farine
        ]

        self.poids_farine = OutputField(self, "Poids de la farine")
        self.poids_eau = OutputField(self, "Poids de l'eau")
        self.poids_pate = OutputField(self, "Poids de la pâte")
        self.poids_sel = OutputField(self, "Poids du sel")
        self.outputs = [
            self.poids_farine, self.poids_eau, self.poids_pate, self.poids_sel
        ]

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
                self.poids_farine.set_value(pf)
                self.poids_eau.set_value(pe)
                self.poids_pate.set_value(ptp)
                self.poids_sel.set_value(ps)

                self.result = True
                pub.sendMessage("change_statusbar", msg="")
            else:
                self.poids_farine.set_value("")
                self.poids_eau.set_value("")
                self.poids_pate.set_value("")
                self.poids_sel.set_value("")

                self.result = False
                pub.sendMessage("change_statusbar", msg="Données d'entrée incorrectes")


class TabPoidsPateImpose(TabCommon):

    def __init__(self, parent):
        self.result = False
        super(TabPoidsPateImpose, self).__init__(parent)

    def set_fields(self):
        self.poids_pate = InputField(self, "Poids de la pâte", 1000, self.update)
        self.th_pate = InputField(self, "Taux d'hydratation de la pâte", 60, self.update, min_max=(1, 100))
        self.th_levain = InputField(self, "Taux d'hydratation du levain", 100, self.update, min_max=(1, 100))
        self.taux_levain_farine = InputField(self, "Taux levain farine", 30, self.update, min_max=(1, 100))
        self.inputs = [
            self.poids_pate, self.th_pate, self.th_levain, self.taux_levain_farine
        ]

        self.poids_farine = OutputField(self, "Poids de la farine")
        self.poids_eau = OutputField(self, "Poids de l'eau")
        self.poids_levain = OutputField(self, "Poids de levain")
        self.poids_sel = OutputField(self, "Poids du self")
        self.outputs = [
            self.poids_farine, self.poids_eau, self.poids_levain, self.poids_sel
        ]

    def update(self):
        ptp = self.poids_pate.get_value()
        thp = self.th_pate.get_value()
        thl = self.th_levain.get_value()
        tlf = self.taux_levain_farine.get_value()

        if ptp != -1 and thp != -1 and thl != -1 and tlf != -1:
            pf, pe, pl, ps = formules.calcul_eau_farine_levain(
                ptp, thp / 100.0, thl / 100.0, tlf / 100.0
            )
            if pf > 0 and pe > 0:
                self.poids_farine.set_value(pf)
                self.poids_eau.set_value(pe)
                self.poids_levain.set_value(pl)
                self.poids_sel.set_value(ps)

                self.result = True
                pub.sendMessage("change_statusbar", msg="")
            else:
                self.poids_farine.set_value("")
                self.poids_eau.set_value("")
                self.poids_levain.set_value("")
                self.poids_sel.set_value("")

                self.result = False
                pub.sendMessage("change_statusbar", msg="Données d'entrée incorrectes")


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title=u"Formulaires de boulangerie", size=(550, 350))
        self.create_menu_bar()

        panel = wx.Panel(self)

        self.notebook = wx.Notebook(panel)
        tab1 = TabPoidsLevainImpose(self.notebook)
        self.notebook.AddPage(tab1, "Poids du levain imposé")
        tab2 = TabPoidsPateImpose(self.notebook)
        self.notebook.AddPage(tab2, "Poids de la pâte imposé")
        self.tabs = [tab1, tab2]

        sizer = wx.BoxSizer()
        sizer.Add(self.notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetForegroundColour("RED")

        self.CenterOnScreen()

        pub.subscribe(self.change_statusbar, 'change_statusbar')

    def create_menu_bar(self):
        menubar = wx.MenuBar()

        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_PRINT, "Imprimer\tCtrl+I")
        self.Bind(wx.EVT_MENU, self.on_print, id=wx.ID_PRINT)
        fileMenu.Append(wx.ID_EXIT, "Quitter\tCtrl+Q")
        self.Bind(wx.EVT_MENU, lambda x: self.Destroy(), id=wx.ID_EXIT)

        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ABOUT, "A propos de Formulaires")
        self.Bind(wx.EVT_MENU, self.on_show_about, id=wx.ID_ABOUT)

        menubar.SetMenus([
            (fileMenu, "Fichier"),
            (helpMenu, "Help")
        ])
        self.SetMenuBar(menubar)

    def on_print(self, evt):
        idx = self.notebook.GetSelection()
        if idx != wx.NOT_FOUND:
            page = self.tabs[idx]
            if page.result:
                title = self.notebook.GetPageText(idx)
                self.display(page.to_html(title))

    def display(self, html):
        with NamedTemporaryFile(delete=False, encoding="utf-8", mode="w") as f:
            f.write(html)
            url = "file://" + f.name
        webbrowser.open(url, new=2)

    def on_show_about(self, evt):
        info = AboutDialogInfo()
        info.SetVersion("1.0")
        info.SetName("Formulaires")
        info.SetDescription("Formulaires de boulangerie")
        info.SetCopyright(u"Franck Barbenoire (2017)")
        AboutBox(info)

    def change_statusbar(self, msg):
        self.statusbar.SetStatusText(msg)


class TestApp(wx.App):
    def OnInit(self):
        frame = Frame()
        frame.Show()
        frame.Layout()
        return True


if __name__ == "__main__":
    app = TestApp()
    app.MainLoop()
