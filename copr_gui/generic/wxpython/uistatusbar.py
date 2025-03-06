#uistatusbar.py
import wx
import time
import threading
import wx.richtext
import datetime

def error(label, window, parent=None):
    dlg = wx.MessageDialog(parent, label, window, wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

class WindowFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

    def SetIconFromPath(self, path):
        self.SetIcon(wx.Icon(path, wx.BITMAP_TYPE_ICO))

def Frame(parent, title=""):
    return WindowFrame(parent, title=title)
   # frame.SetIconFromPath = lambda path: frame.SetIcon(wx.Icon(path, wx.BITMAP_TYPE_ICO))

def wx_datetime_to_date(wx_dt):
    if isinstance(wx_dt, datetime.date):
        return wx_dt
    elif isinstance(wx_dt, int):
        return datetime.date.fromtimestamp(wx_dt)
    elif isinstance(wx_dt, datetime.datetime):
        return wx_dt.date()

    year = wx_dt.GetYear()
    month = wx_dt.GetMonth() + 1
    day = wx_dt.GetDay()
    return datetime.date(year, month, day)

def wx_datetime_to_time(wx_dt):
    if isinstance(wx_dt, datetime.time):
        return wx_dt
    elif isinstance(wx_dt, int):
        return datetime.datetime.fromtimestamp(wx_dt).time()
    elif isinstance(wx_dt, datetime.datetime):
        return wx_dt.time()

    hour = wx_dt.GetHour()
    minute = wx_dt.GetMinute()
    second = wx_dt.GetSecond()
    microsecond = wx_dt.GetMillisecond() * 1000
    return datetime.time(hour, minute, second, microsecond)

def date_to_wx_datetime(py_date):
    if isinstance(py_date, wx.DateTime):
        return py_date
    elif isinstance(py_date, int):
        return wx.DateTime.FromTimeT(py_date)
    elif isinstance(py_date, datetime.datetime):
        return wx.DateTime(py_date.day, py_date.month - 1, py_date.year)

    wx_dt = wx.DateTime()
    wx_dt.Set(py_date.day, py_date.month - 1, py_date.year)
    return wx_dt

def time_to_wx_datetime(py_time):
    if isinstance(py_time, wx.DateTime):
        return py_time
    elif isinstance(py_time, int):
        return wx.DateTime.FromTimeT(py_time)
    elif isinstance(py_time, datetime.datetime):
        return wx.DateTime(0, 0, 0, py_time.hour, py_time.minute, py_time.second, py_time.microsecond // 1000)

    wx_dt = wx.DateTime()
    wx_dt.SetHour(py_time.hour)
    wx_dt.SetMinute(py_time.minute)
    wx_dt.SetSecond(py_time.second)
    wx_dt.SetMillisecond(py_time.microsecond // 1000)
    return wx_dt

def CreateApp():
    return wx.App()

def InitApp(app):
    return app.MainLoop()
    
def browser(url):
    wx.LaunchDefaultBrowser(url)

def show_text_frame(text, title="Text Frame", parent=None):
    frame = wx.Frame(parent, title=title, size=(400, 300))
    text_ctrl = wx.richtext.RichTextCtrl(frame, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
    text_ctrl.SetValue(text)
    frame.Show()

def question(label, window, parent=None):
    dlg = wx.MessageDialog(parent, label, window, wx.YES_NO | wx.ICON_QUESTION)
    answer = dlg.ShowModal()
    dlg.Destroy()
    return answer == wx.ID_YES

class ProgressThread(threading.Thread):
    def __init__(self, generator, progress_dialog):
        super().__init__()
        self.stop_req = False
        self.generator = generator
        self.progress_dialog = progress_dialog

    def stop(self):
        self.stop_req = True

    def run(self):
        i = 0
        for item in self.generator:
            if self.stop_req:
                return
            i += 1
            wx.CallAfter(self.progress_dialog.Update, i)
            
        wx.CallAfter(self.progress_dialog.CloseCall)

class ProgressDialog(wx.ProgressDialog):
    def __init__(self, parent, title, message, label, maximum, close):
        super().__init__(title, message, maximum=maximum, parent=parent, style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
        self.label = label
        self.close = close
        self.Bind(wx.EVT_CLOSE, self.Close)

    def Update(self, value):
        try:
            super().Update(value, self.label)
        except RuntimeError:
            pass
                
    def CloseCall(self):
        close = self.close
        if callable(close):
            close()
        elif close:
            self.Close()
            
    def Close(self, event=None):
        if hasattr(self, 'thread'): 
            self.thread.stop()
        super().Destroy()
    close=Close

def job_generator(data, function):
    for i in data:
        yield function(i)

def execute_data_with_progress(data, job, label, window, close=True):
    return execute_with_progress(job_generator(data, job), len(data), label, window, close)

def execute_with_progress(generator, length, label, window, close=True):
    dialog = ProgressDialog(None, window, label, label, length, close)
    thread = ProgressThread(generator, dialog)
    dialog.thread = thread
    thread.start()
    dialog.ShowModal()
    return dialog

if __name__ == '__main__':
    def job_function(ev):
        time.sleep(1)
        print(ev)
    class MainWindow(wx.Frame):
        def __init__(self):
            super().__init__(None, title="Main Window")
            panel = wx.Panel(self)
            sizer = wx.BoxSizer(wx.VERTICAL)
            panel.SetSizer(sizer)

            button = wx.Button(panel, label="Start Job")
            sizer.Add(button, 0, wx.ALL, 10)

            button.Bind(wx.EVT_BUTTON, lambda a: execute_data_with_progress(job=job_function, data=[1, 2, 3, 4, 5, 6, 7, 8], label="Points", window="Progress Window"))
    app = wx.App()
    frame = MainWindow()
    frame.Show()
    app.MainLoop()
    
