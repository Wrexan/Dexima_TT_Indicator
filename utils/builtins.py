from datetime import datetime

import pandas as pd


class TradeView:
    def __init__(self, dataframe: pd.DataFrame):
        """Creates TradeView's Pive Script builtins emulation interface,
         that contains methods close to original."""
        self.dataframe = dataframe
        self._bar_index: int = 0
        self.last_idx: int = len(dataframe) - 1

        self.curr_datetime = datetime.strptime(self.bar_date(), '%Y-%m-%d')
        self.last_cycle_date = self.curr_datetime

    def security(self, symbol: str, resolution: str, expression, bar_idx_in_past):
        curr_datetime = datetime.strptime(self.bar_date(), '%Y-%m-%d')
        if resolution == 'D':
            if datetime.strptime(self.bar_date(self._bar_index - 1), '%Y-%m-%d').day != curr_datetime.day:
                self.last_cycle_date = curr_datetime
                return expression(bar_idx_in_past)

    @property
    def step_forward(self):
        """Increments _bar_index counter to the next bar. Returns True, if next bar exist."""
        if self._bar_index < self.last_idx:
            self._bar_index += 1
            return True

    def bar_index(self, bar_idx_in_past: int = 0):
        """Returns index of previous bar at bar_idx_in_past steps before current.
         Returns current bar index, if bar_idx_in_past==0."""
        return self._do_relative_past_idx_to_idx(bar_idx_in_past)

    def bar_date(self, bar_idx: int = 0):
        """Returns date of bar index."""
        return self.dataframe.iloc[self._do_valid_absolute_idx(bar_idx)]['date']

    def _do_relative_past_idx_to_idx(self, bar_idx_in_past: int = 0):
        """Returns valid bar index, relative to current.
         Positive bar_idx_in_past will return index in the past."""
        return self._do_valid_absolute_idx(self._bar_index - bar_idx_in_past)

    def _do_valid_absolute_idx(self, bar_idx: int):
        """Returns valid bar index, that will allways be inside the dataframes bounds"""
        if bar_idx > self.last_idx:
            return self.last_idx
        elif bar_idx < 0:
            return 0
        return bar_idx

    def close(self, bar_idx_in_past: int = 0):
        """Returns close price value of bar at bar_idx_in_past bars in the past.
         Without args returns current bar close price value.
         Positive bar_idx_in_past will return value of bar in the past."""
        return self.dataframe.iloc[self._do_relative_past_idx_to_idx(bar_idx_in_past)]['close']

    def open(self, bar_idx_in_past: int = 0):
        """Returns open price value of bar at bar_idx_in_past bars in the past.
         Without args returns current bar open price value.
         Positive bar_idx_in_past will return value of bar in the past."""
        return self.dataframe.iloc[self._do_relative_past_idx_to_idx(bar_idx_in_past)]['open']

    def low(self, bar_idx_in_past: int = 0):
        """Returns low price value of bar at bar_idx_in_past bars in the past.
         Without args returns current bar low price value.
         Positive bar_idx_in_past will return value of bar in the past."""
        return self.dataframe.iloc[self._do_relative_past_idx_to_idx(bar_idx_in_past)]['low']

    def high(self, bar_idx_in_past: int = 0):
        """Returns high price value of bar at bar_idx_in_past bars in the past.
         Without args returns current bar high price value.
         Positive bar_idx_in_past will return value of bar in the past."""
        return self.dataframe.iloc[self._do_relative_past_idx_to_idx(bar_idx_in_past)]['high']

    def lowest(self, source: float = None, length: int = 1, bar_idx_in_past: int = 0):
        """Returns the lowest price value of last few bars from bar_idx_in_past to length in the past from current bar.
         Without bar_idx_in_past returns lowest from bars before current bar.
         Positive bar_idx_in_past will give bars before current bar."""
        segment = self.dataframe.iloc[
                  self._do_relative_past_idx_to_idx(bar_idx_in_past + length):
                  self._do_relative_past_idx_to_idx(bar_idx_in_past - 1)
                  ]['low']
        return min(segment, default=source)

    def highest(self, source: float = None, length: int = 1, bar_idx_in_past: int = 0):
        """Returns the highest price value of last few bars from bar_idx_in_past to length in the past from current bar.
         Without bar_idx_in_past returns highest from bars before current bar.
         Positive bar_idx_in_past will give bars before current bar."""
        segment = self.dataframe.iloc[
                  self._do_relative_past_idx_to_idx(bar_idx_in_past + length):
                  self._do_relative_past_idx_to_idx(bar_idx_in_past - 1)
                  ]['high']
        return max(segment, default=source)

    @staticmethod
    def crossunder(x, y):
        """Returns True if current bar crossed under.
         This means that result of x() lesser than result of y(), but was bigger in the last bar.
         One or both args must be builtins: low(), high(), open(), close(). One of args can be the float."""
        if isinstance(y, float):
            if x() < y < x(1):
                return True
        elif isinstance(x, float):
            if y() > x > y(1):
                return True
        else:
            if x() < y() and x(1) > y(1):
                return True

    # def calculate_sma(self, data: pd.DataFrame, period: int = 50):
    #     def avg(d: pd.DataFrame):
    #         return d['close'].mean()
    #
    #     result = []
    #     for i in range(period - 1, len(data)):
    #         val = avg(data.iloc[i - period + 1:i])
    #         result.append({'time': data.iloc[i]['date'], f'SMA {period}': val})
    #     return pd.DataFrame(result)

    def new_box(self, x0: int, x1: int, y0: float, y1: float, xref: str = 'x', yref: str = 'y', line_width: int = 1,
                fillcolor: str = 'rgb(100, 120, 120)'):
        """Creates instance of visual box shape to draw squares on plotly canvas.
        To use: figure.add_shape(this.shape)"""
        return self.Box(self, x0, x1, y0, y1, xref, yref, line_width, fillcolor)

    def new_line(self, x0: int, x1: int, y0: float, y1: float, xref: str = 'x', yref: str = 'y',
                 color: str = 'rgb(100, 120, 120)', width: int = 1):
        """Creates instance of visual box shape to draw squares on plotly canvas.
        To use: figure.add_shape(this.shape)"""
        return self.Line(self, x0, x1, y0, y1, xref, yref, color, width)

    class Box:
        """Shape class to handle squares on plotly canvas. Don't use it, use TradeView.new_box(args) to create one."""
        def __init__(self, tv, x0, x1, y0, y1, xref, yref, line_width, fillcolor):
            self.tv = tv
            self.x0 = x0
            self.x1 = x1
            self.y0 = y0
            self.y1 = y1
            self.xref = xref
            self.yref = yref
            self.line_width = line_width
            self.fillcolor = fillcolor

        @property
        def get_top(self):
            """Returns top value float()"""
            return self.y1

        @property
        def get_bottom(self):
            """Returns bottom value float()"""
            return self.y0

        @property
        def get_left(self):
            """Returns left bar index int()"""
            return self.x0

        @property
        def shape(self):
            """Returns dict() to draw plotly shape.
             Use as figure.add_shape(this.shape)"""
            return {
                'x0': self.tv.bar_date(self.x0), 'x1': self.tv.bar_date(self.x1),
                'y0': self.y0, 'y1': self.y1,
                'xref': self.xref, 'yref': self.yref,
                'line_width': self.line_width,
                'fillcolor': self.fillcolor,
            }

    class Line:
        """Shape class to handle lines on plotly canvas.
         Don't use it, use TradeView.new_line(args) to create one."""
        def __init__(self, tv, x0, x1, y0, y1, xref, yref, color, width):
            self.tv = tv
            self.x0 = x0
            self.x1 = x1
            self.y0 = y0
            self.y1 = y1
            self.xref = xref
            self.yref = yref
            self.color = color
            self.width = width

        @property
        def shape(self):
            """Returns dict() to draw plotly shape.
             Use as figure.add_shape(this.shape)"""
            return {
                'type': 'line',
                'x0': self.tv.bar_date(self.x0), 'x1': self.tv.bar_date(self.x1),
                'y0': self.y0, 'y1': self.y1,
                'xref': self.xref, 'yref': self.yref,
                'line': {
                    'color': self.color,
                    'width': self.width,
                }
            }
