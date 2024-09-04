import pandas as pd
import pandas_ta as ta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

df = pd.read_csv("EURUSD_Candlestick_1_Hour_BID_04.05.2003-15.04.2023.csv")
df=df[df['volume']!=0]
df.reset_index(drop=True, inplace=True)

df['EMA'] = ta.ema(df.close, length=150)
df.tail()

df=df[0:10000]