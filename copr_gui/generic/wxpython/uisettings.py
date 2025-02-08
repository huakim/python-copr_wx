import wx
from wx.lib import expando
from wx.adv import DatePickerCtrl, TimePickerCtrl
import wx.stc
from bidict import bidict
from collections import OrderedDict
from collections.abc import Iterable

ExpandoTextCtrl = expando.ExpandoTextCtrl

class TextFieldDict(OrderedDict):
    def __init__(self, panel, sizer):
        self.panel = panel
        self.sizer = sizer
    def set_array(self, array):
        self.set_size(len(array))
        it = iter(array)
        for index, text in enumerate(self.values()):
            text.SetValue(next(it) or '')
    def set_size(self, size):
        l = len(self)
        if l > size:
            l -= size
            array = []
            for i in self.values():
                array.append(i)
                l -= 1
                if l == 0:
                    break
            for i in array:
                self.delete_item(i)
        elif l == size:
            return
        else:
            size -= l
            while size > 0:
                size -= 1
                self.add_new()
    def delete_item(self, text_ctrl):
        self.panel.on_minus_button_click(
            self.sizer, text_ctrl.sizer, self, text_ctrl)
    def add_new(self):
        self.panel.on_add_button_click(self.sizer, self)



class SettingsScrolledWindow(wx.ScrolledWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().SetScrollRate(10, 10)

field_padding=5

class UiSettingsPanel(wx.Panel):
    def startInit(self):
        self.vertical_layout = self.createVerticalLayout()
        self.form_sizer = form_sizer = self.createVerticalLayout()

    def addList(self):
        list_panel = wx.Panel(self.scrolled_window)
        list_sizer = wx.BoxSizer(wx.VERTICAL)
        list_panel.SetSizer(list_sizer)
        self.form_sizer.Add(list_panel, 0, wx.EXPAND | wx.ALL, 0)
        fields=TextFieldDict(self, list_sizer)
        return fields

    def addTabWidget(self):
        notebook = wx.Notebook(self.scrolled_window)
        self.form_sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 0)
        return notebook

    def incTabWidget(self, notebook, checkbox, value):
        notebook.AddPage(checkbox, value)
        checkbox.Bind(wx.EVT_SIZE, self.on_resized_event)

    @staticmethod
    def incList(fields):
        fields.add_new()


    def addLabelPlusButton(self, field_name):
        scrolled_window = self.scrolled_window
        form_sizer = self.form_sizer
        list_panel = wx.Panel(scrolled_window)
        list_sizer = wx.BoxSizer(wx.HORIZONTAL)
        list_panel.SetSizer(list_sizer)
        form_sizer.Add(list_panel, 0, wx.EXPAND | wx.ALL, field_padding)
        label = wx.StaticText(list_panel, label=f'\t{field_name}')
        add_button = wx.Button(list_panel, label='+')
        add_button.SetMaxSize((50, -1))
        list_sizer.Add(add_button, 0, wx.ALL, 0)
        list_sizer.Add(label, 0, wx.ALL | wx.CENTER | wx.LEFT)
        return add_button

    def addText(self):
        text_ctrl = ExpandoTextCtrl(self.scrolled_window)
        self.form_sizer.Add(text_ctrl, 0, wx.EXPAND | wx.ALL, field_padding)
        func = self.on_resized_event_text(text_ctrl)
        text_ctrl.Bind(wx.EVT_CHAR, func)
        text_ctrl.Bind(wx.EVT_TEXT, func)
        return text_ctrl

    @staticmethod
    def bindCheckBox(checkbox, func):
        checkbox.Bind(wx.EVT_CHECKBOX, func)

    @staticmethod
    def bindButton(checkbox, func):
        checkbox.Bind(wx.EVT_BUTTON, func)

    def addButton(self, field_name):
        checkbox = wx.Button(self.scrolled_window, label=field_name)
        self.form_sizer.Add(checkbox, 0, wx.EXPAND | wx.ALL, field_padding)
        return checkbox

    def addCheckBox(self, field_name):
        checkbox = wx.CheckBox(self.scrolled_window, label=field_name)
        self.form_sizer.Add(checkbox, 0, wx.EXPAND | wx.ALL, field_padding)
        return checkbox

    def addHorBox(self):
        panel = SimplePanel(self.scrolled_window)
        self.form_sizer.Add(panel, 0, wx.EXPAND | wx.ALL, field_padding)
        return panel

    def addLine(self):
        text_ctrl = wx.TextCtrl(self.scrolled_window, style=wx.TE_PROCESS_ENTER)
        self.form_sizer.Add(text_ctrl, 0, wx.EXPAND | wx.ALL, field_padding)
        return text_ctrl

    def addDate(self):
        text_ctrl = DatePickerCtrl(self.scrolled_window)
        self.form_sizer.Add(text_ctrl, 0, wx.EXPAND | wx.ALL, field_padding)
        return text_ctrl

    def addTime(self):
        text_ctrl = TimePickerCtrl(self.scrolled_window)
        self.form_sizer.Add(text_ctrl, 0, wx.EXPAND | wx.ALL, field_padding)
        return text_ctrl

    @staticmethod
    def bindComboBox(combobox, func):
        combobox.Bind(wx.EVT_COMBOBOX, func)

    def addComboBox(self, values):
        combobox = wx.ComboBox(self.scrolled_window,
                style=wx.CB_DROPDOWN|wx.CB_READONLY, choices=values)
        self.form_sizer.Add(combobox, 0, wx.EXPAND | wx.ALL, field_padding)
        combobox.SetSelection(0)
        return combobox

    def addLabel(self, field_name):
        label = wx.StaticText(self.scrolled_window, label=f'\t{field_name}')
        self.form_sizer.Add(label, 0, wx.ALL, field_padding)

    @staticmethod
    def createVerticalLayout():
        return wx.BoxSizer(wx.VERTICAL)

    def on_add_button_click(self, sizer, fields):
        panel = sizer.GetContainingWindow()

        field_sizer = wx.BoxSizer(wx.HORIZONTAL)

        text_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        minus_button = wx.Button(panel, label="-")
        minus_button.SetMaxSize(wx.Size(50, -1))
        text_delete_func =  (
            lambda *event: fields.delete_item(text_ctrl) )
        minus_button.Bind(wx.EVT_BUTTON, text_delete_func)
        text_ctrl.sizer = field_sizer
        i = id(text_ctrl)
        fields[i] = text_ctrl

        field_sizer.Add(minus_button, 0, wx.ALL, 5)
        field_sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(field_sizer, 0, wx.EXPAND)

        self.on_resized()

  #  @staticmethod
    def create_panel(self, parent):
        panel = wx.Panel(parent)
  #      panel.Bind(EVT_REFRESHED,
  #          lambda event: [p////////////'), self.on_resized_event(event)])
        panel.Bind(wx.EVT_SIZE, self.on_resized_event)
        return panel

    def on_resized_event_text(self, text):
        lines = -1
        def resized_event(event):
            nonlocal lines
            new_lines = text.GetNumberOfLines()
            if new_lines != lines:
                lines = new_lines
                self.on_resized()
                self.on_resized()
            event.Skip()
        return resized_event

    def on_resized_event(self, event):
        self.on_resized()
        event.Skip()

    def on_resized(self):
        self.Layout()
        self.Refresh()
        self.Update()

    def addCheckBoxPanel(self):
        panel=WrapCheckBoxPanel(self)
        self.form_sizer.Add(panel, 0, wx.ALL, field_padding)
        return panel

    def addButtonPanel(self):
        panel=WrapButtonPanel(self)
        self.form_sizer.Add(panel, 0, wx.ALL, field_padding)
        return panel

    def Init(self):
        scrolled_window = self.scrolled_window
        scrolled_window.SetSizer(self.form_sizer)
        vertical_layout=self.vertical_layout
        vertical_layout.Add(scrolled_window, 1, wx.EXPAND)
        self.SetSizer(vertical_layout)

    def on_minus_button_click(self, sizer, field_sizer, fields, text_ctrl):
        panel = sizer.GetContainingWindow()
        field_sizer.Clear(True)
        del fields[id(text_ctrl)]
        sizer.Remove(field_sizer)
        self.on_resized()

    @staticmethod
    def SetTextValue(widget, value):
        widget.SetValue(value)

    SetLineValue = SetTextValue
    SetDateValue = SetTextValue
    SetTimeValue = SetTextValue
    SetCheckBoxValue = SetTextValue


    @staticmethod
    def SetListValue(widget, value):
        widget.set_array(value)

    @staticmethod
    def SetComboBoxSelection(widget, value):
        widget.SetSelection(value)

    SetTabWidgetSelection = SetComboBoxSelection



    @staticmethod
    def GetTextValue(widget):
        return widget.GetValue()

    GetLineValue = GetTextValue
    GetDateValue = GetTextValue
    GetTimeValue = GetTextValue
    GetCheckBoxValue = GetTextValue


    @staticmethod
    def GetListValue(widget):
        return [i.GetValue() for i in widget.values()]

    @staticmethod
    def GetComboBoxSelection(widget):
        return widget.GetSelection()

    GetTabWidgetSelection = GetComboBoxSelection


class WrapPanel(wx.WrapSizer):
    def __init__(self, parent):
        wx.WrapSizer.__init__(self, wx.HORIZONTAL)
        self.form_sizer = self
        self.scrolled_window=parent.scrolled_window

class WrapCheckBoxPanel(WrapPanel):
    __init__=WrapPanel.__init__
    add=UiSettingsPanel.addCheckBox
    bind=UiSettingsPanel.bindCheckBox

class WrapButtonPanel(WrapPanel):
    __init__=WrapPanel.__init__
    add=UiSettingsPanel.addButton
    bind=UiSettingsPanel.bindButton
