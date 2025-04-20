'''


i have the following code. how can i add feauture to copy element with ctrl+c?
```
#'''
import wx
from .uistatusbar import WindowFrame
import wx.grid as gridlib
import datetime
from copr_gui.static.spec_types import getName, getId, getType

class ContextMenu(wx.Menu):
    def __init__(self, parent, menus):
        super().__init__()
        self.parent = parent
        for i in menus:
            nameid = getId(i)
            name = getName(i)
            item = self.Append(wx.ID_ANY, name)
            setattr(self, nameid, item)
            nameid = f'on_{nameid}_option'
            if hasattr(self, nameid):
                self.Bind(wx.EVT_MENU, getattr(self, nameid), item)

class TableModel(gridlib.GridTableBase):
    def __getattr__(self, name):
        if name == 'column_names':
            func = getName
        elif name == 'column_ids':
            func = getId
        elif name == 'column_types':
            func = lambda item, default='str': getType(item, default)
        else:
            raise AttributeError(name)
        try:
            return self.__data[name]
        except KeyError: 
            data = self.__data[name] = [func(i) for i in self.columns]
            return data
            
    def __init__(self, columns, data=None):
        super().__init__()
        self.__data = dict()
        self.columns = [{'id': 'check_state', 'name': '', 'type': 'bool'}] + columns
      #  self.column_names = [''] + [getName(i) for i in column_names]
      #  self.types = ['bool'] + [getType(i, 'str') for i in column_names]
        data = self.data = [] if data is None else data
        self.sort_col = None
        all=True
        for i in data:
            if not data[0]:
                all=False
                break
        self.all = all
        self.sort_reverse = False
        
    def DropItems(self, items):
        oldlen = len(self.data)
        data = self.data = [i for i in self.data if not i in items]
        newlen = len(data)
        msg = gridlib.GridTableMessage(self, 
            gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, 0, oldlen-newlen)
        view = self.GetView()
        view.ProcessTableMessage(msg)
        view.ForceRefresh()
        
    def DropByCheck(self, check=False):
        oldlen = len(self.data)
        data = self.data = self.GetItemsByCheck(check)
        newlen = len(data)
        msg = gridlib.GridTableMessage(self, 
            gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, 0, oldlen-newlen)
        view = self.GetView()
        view.ProcessTableMessage(msg)
        view.ForceRefresh()

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.column_names)

    def IsEmptyCell(self, row, col):
        return False

    def GetRowItem(self, rowid):
        return self.data[rowid]

    def GetItemsByCheck(self, check=True):
        return [i for i in self.data if bool(i[0]) == check ]

    def GetValue(self, row, col):
        return self.data[row][col]

    def SetValue(self, row, col, value):
        if col == 0:
            if not value:
                self.all=False
        self.data[row][col] = value

    def GetColLabelValue(self, col):
        return self.column_names[col]

    def Clear(self):
        row_count = self.GetNumberRows()
        self.data = list()
        self.all = True
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, 0, row_count)
        view = self.GetView()
        view.ProcessTableMessage(msg)
        view.ForceRefresh()

    def AllChecked(self):
        return self.all

    def CheckAll(self, check=True):
        data=self.data
        if not data:
            return
        for row in data:
            row[0] = '1' if check else ''
        self.all = bool(check)
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        view = self.GetView()
        view.ProcessTableMessage(msg)

    def AppendRow(self, *row_data):
        self.data.extend(row_data)
        for i in row_data:
            if not i[0]:
                self.all=False
                break
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, len(row_data))
        view = self.GetView()
        view.ProcessTableMessage(msg)
        view.ForceRefresh()

    def GetAttr(self, row, col, kind):
        attr = gridlib.GridCellAttr()
        type = self.column_types[col]
        if type == 'bool':
            attr.SetEditor(gridlib.GridCellBoolEditor())
            attr.SetRenderer(gridlib.GridCellBoolRenderer())
        elif type == 'date':
            attr.SetRenderer(DateCellRenderer())
        else:#elif type == 'str':
            attr.SetReadOnly(True)
        return attr

    def RestoreLastSort(self):
        self.data.sort(key=lambda x: x[self.sort_col], reverse=self.sort_reverse)
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        view = self.GetView()
        view.ProcessTableMessage(msg)

    def SortByColumn(self, col):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = col
            self.sort_reverse = False
        self.RestoreLastSort()

# Custom renderer class to format date integers as dates
class DateCellRenderer(gridlib.PyGridCellRenderer):
    def __init__(self):
        gridlib.PyGridCellRenderer.__init__(self)

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = grid.GetTable().GetValue(row, col)
        # Format the datetime object as a string
        formatted_date = value.strftime('%Y-%m-%d_%T')
        # Draw the formatted date string
#        self.DrawTextRectangle(grid, attr, dc, rect, formatted_date, isSelected)
        dc.DrawText(formatted_date, rect.x + 2, rect.y + 2)
        
    def Clone(self):
        return DateCellRenderer()

class CustomTable(gridlib.Grid):
    def __init__(self, parent, column_names):
        super().__init__(parent)
   #     print(column_names)
        self.table_model = TableModel(column_names)
        self.SetTable(self.table_model)
        self.SetRowLabelSize(60)
        self.SetColSize(0, 35)  # Set the width of the first column (Check column)
        for col in range(1, self.GetNumberCols()):
            label = self.table_model.GetColLabelValue(col)
            width = self.GetTextExtent(label)[0] + 40  # Calculate the width based on the label
            self.SetColSize(col, width)  # Set the width of the column

        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)

    def OnChar(self, event):
        if event.ControlDown() and event.GetKeyCode() == ord('C'):  # Ctrl+C
            self.Copy()
        else:
            event.Skip()
            
    def Copy(self):
        selection = self.GetSelection()
        if selection:
            start_row, start_col, end_row, end_col = selection
            data = []
            for row in range(start_row, end_row + 1):
                row_data = []
                for col in range(start_col, end_col + 1):
                    value = self.table_model.GetValue(row, col)
                    row_data.append(str(value))
                data.append(row_data)
            text = '\n'.join(['\t'.join(row) for row in data])
            clipboard.Open()
            clipboard.SetData(wx.TextDataObject(text))
            clipboard.Close()
            
    def OnLabelLeftClick(self, event):
        col = event.GetCol()
        self.table_model.SortByColumn(col)
        self.ForceRefresh()

class MonitorFrame(WindowFrame):
    def __init__(self, parent, button_names, column_names, title=""):
        super().__init__(parent, title=title, size=(1000, 600))
        self.panel = wx.Panel(self)
        self.vertical_layout = wx.BoxSizer(wx.VERTICAL)
        self.button_layout = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = []  # List to store custom buttons
        self.addCustomButton("All")

        for name in button_names:
            self.addCustomButton(name)

        self.vertical_layout.Add(self.button_layout, 0, wx.ALIGN_LEFT)
        table = self.custom_table = CustomTable(self.panel, column_names)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellDoubleClick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.model = table.table_model
        self.vertical_layout.Add(self.custom_table, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(self.vertical_layout)
        self.Centre()
        self.Show()
    
    def addCustomButton(self, label):
        label_text = getName(label)
        label = getId(label)
        button = wx.Button(self.panel, label=label_text)
        self.button_layout.Add(button, 0, wx.ALL, 5)
        label=f'button_{label}'
        setattr(self, label, button)
        label=f'{label}_clicked'
        if hasattr(self, label):
            button.Bind(wx.EVT_BUTTON, getattr(self, label))

    def button_all_clicked(self, event):
        model = self.model
        model.CheckAll(not model.AllChecked())
        self.custom_table.ForceRefresh()

if __name__ == '__main__':
    app = wx.App()

    button_names = ['Button 1', 'Button 2', 'Button 3']
    column_names = ['Column 1', 'Column 2', 'Column 3']

    frame = MonitorFrame(None, button_names, column_names)

    # Add rows to the custom table
    frame.model.AppendRow(
    ['1', 'Value 1', 'Value 2', 'Value 3'],
    ['', 'Value 4', 'Value 5', 'Value 6'],
    ['', 'Value 5', 'Value 2', 'Value 4'],
    ['', 'Value 4', 'Value 5', 'Value 6'])

    app.MainLoop()
