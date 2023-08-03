import pandas as pd
from utils.builtins import TradeView


class CustomTradeIndicator:
    def __init__(self, figure, dataframe: pd.DataFrame):
        self.fig = figure
        self.df = dataframe
        self.tv = TradeView(dataframe)

        self.candle_range = 15  # candle_range if candle_range in args['candle_range'] or 15
        self.show_PD = False
        self.show_bearish_BOS = False
        self.show_bullish_BOS = False
        self.bearish_OB_colour = 'rgba(255,0,0,0.14)'
        self.bullish_OB_colour = 'rgba(0,255,0,0.14)'
        self.BOS_candle_colour = 'yellow'
        self.bullish_trend_color = 'lime'
        self.bearish_trend_colour = 'red'

        # candle colouring
        self.candle_colour_mode: int = 0
        self.bos_candle: bool = False

        # tracking for entries
        self.last_down_index: int = 0
        self.last_down: float = 0
        self.last_low: float = 0

        self.last_up_index: int = 0
        self.last_up: float = 0
        self.last_up_low: float = 0
        self.last_up_open: float = 0
        self.last_high: float = 0
        self.last_bull_break_low: float = 0

        # structure
        self.structure_low_index: int = 0
        self.structure_low: float = 1000000

        # order block drawing arrays
        self.long_boxes = []
        self.short_boxes = []
        self.bos_lines = []
        self.PDH_line = None
        self.PDL_line = None

        self.last_long_index: int = 0
        self.last_short_index: int = 0

    def structure_low_index_pointer(self, length):
        min_value = self.tv.highest(self.tv.high(), self.candle_range, 1)
        min_index = self.tv.bar_index()
        for i in range(1, length + 1):
            if self.tv.low(i) < min_value:
                min_value = self.tv.low(i)
                min_index = self.tv.bar_index(i)
        return min_index

    def draw_indicator(self, candle_range: int = None, extras: list = None):
        self.candle_range = candle_range or self.candle_range
        if extras:
            self.show_PD = 'showPD' in extras
            self.show_bearish_BOS = 'showBearishBOS' in extras
            self.show_bullish_BOS = 'showBullishBOS' in extras

        # Main logic cycle. Calculates Plotly graphic shapes from trading dataframe, then filters it.
        while True:
            bar_index = self.tv.bar_index()
            low_ = self.tv.low()
            high_ = self.tv.high()
            close_ = self.tv.close()
            open_ = self.tv.open()

            if self.show_PD:
                # check only the last bars to speed up
                if bar_index >= self.tv.last_idx - 20:
                    PDH = self.tv.security('', 'D', self.tv.high, 1)
                    PDL = self.tv.security('', 'D', self.tv.low, 1)
                    if PDH:
                        del self.PDH_line
                        del self.PDL_line

                        self.PDH_line = self.tv.new_line(
                            x0=0,
                            x1=bar_index,
                            y0=PDH,
                            y1=PDH,
                            xref='x',
                            yref='y',
                            color="LightBlue",
                            width=1
                        )
                        self.PDL_line = self.tv.new_line(
                            x0=0,
                            x1=bar_index,
                            y0=PDL,
                            y1=PDL,
                            xref='x',
                            yref='y',
                            color="LightBlue",
                            width=1
                        )




            # get the lowest point in the range
            self.structure_low = self.tv.lowest(low_, self.candle_range, 1)
            self.structure_low_index = self.structure_low_index_pointer(self.candle_range)
            # bearish break of structure
            if self.tv.crossunder(self.tv.low, self.structure_low):
                if (bar_index - self.last_up_index) < 1000:
                    # add bear order block
                    self.short_boxes.append(
                        self.tv.new_box(
                            x0=self.last_up_index,
                            x1=self.tv.last_idx,
                            y0=self.last_up_low,
                            y1=self.last_high,
                            xref='x',
                            yref='y',
                            line_width=0,
                            fillcolor=self.bearish_OB_colour
                        )
                    )
                    # add bearish bos line
                    if self.show_bearish_BOS:
                        self.bos_lines.append(
                            self.tv.new_line(
                                x0=self.structure_low_index,
                                x1=bar_index,
                                y0=self.structure_low,
                                y1=self.structure_low,
                                xref='x',
                                yref='y',
                                color="Red",
                                width=2
                            )
                        )

                    # show bos candle
                    self.bos_candle = True
                    # color mode bear
                    self.candle_colour_mode = 0
                    self.last_short_index = self.last_up_index

            # bullish break of structure?
            if self.short_boxes:
                for i in range(len(self.short_boxes) - 1, 0, -1):
                    box = self.short_boxes[i]
                    top = box.get_top
                    left = box.get_left
                    if close_ > top:
                        # remove the short box
                        del self.short_boxes[i]
                        # ok to draw?
                        if (bar_index - self.last_down_index) < 1000 and bar_index > self.last_long_index:
                            # add bullish order block
                            self.long_boxes.append(
                                self.tv.new_box(
                                    x0=self.last_down_index,
                                    x1=self.tv.last_idx,
                                    y0=self.last_low,
                                    y1=self.last_down,
                                    xref='x',
                                    yref='y',
                                    line_width=0,
                                    fillcolor=self.bullish_OB_colour
                                )
                            )
                            if self.show_bullish_BOS:
                                self.bos_lines.append(
                                    self.tv.new_line(
                                        x0=left,
                                        x1=bar_index,
                                        y0=top,
                                        y1=top,
                                        xref='x',
                                        yref='y',
                                        color="Green",
                                        width=2
                                    )
                                )
                            # show bos candle
                            self.bos_candle = True
                            # color mode bullish
                            self.candle_colour_mode = 1
                            # record last bull bar index to prevent duplication
                            self.last_long_index = bar_index
                            self.last_bull_break_low = low_

            # remove LL if close below
            if self.long_boxes:
                for i in range(len(self.long_boxes) - 1, 0, -1):
                    lbox = self.long_boxes[i]
                    bottom = lbox.get_bottom
                    if close_ < bottom:
                        del self.long_boxes[i]

            candle_color = self.bullish_trend_color if self.candle_colour_mode else self.bearish_trend_colour
            candle_color = self.BOS_candle_colour if self.bos_candle else candle_color
            self.fig.data[0].increasing.fillcolor = candle_color

            # record last up and down candles
            if close_ < open_:
                self.last_down = high_
                self.last_down_index = bar_index
                self.last_low = low_

            if close_ > open_:
                self.last_up = close_
                self.last_up_index = bar_index
                self.last_up_open = open_
                self.last_up_low = low_
                self.last_high = high_

            # update last high / low for more accurate order block placements
            if high_ > self.last_high:
                self.last_high = high_
            if low_ < self.last_low:
                self.last_low = low_

            # if there's no bars to handle - exit cycle
            if not self.tv.step_forward:
                break

        elements_to_render = [
            *self.short_boxes,
            *self.long_boxes,
            *self.bos_lines,
        ]
        if self.PDH_line:
            elements_to_render.append(self.PDH_line)
            elements_to_render.append(self.PDL_line)
        # draw filtered shapes
        for element in elements_to_render:
            self.fig.add_shape(element.shape)
