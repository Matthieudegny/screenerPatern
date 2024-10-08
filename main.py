# Import pandas library for data manipulation and analysis
import pandas as pd
# Import pandas_ta library for technical analysis indicators
import pandas_ta as ta
# Import numpy library for numerical operations
import numpy as np
# Import plotly.graph_objects for interactive plotting
import plotly.graph_objects as go
# Import scipy.stats for statistical functions
from scipy import stats

# Read the CSV file containing EURUSD candlestick data
df = pd.read_csv("EURUSD.csv")
# Remove rows where volume is zero
df = df[df['volume'] != 0]
# Reset the index of the dataframe after removing rows
df.reset_index(drop=True, inplace=True)

# Calculate the Exponential Moving Average (EMA) with a period of 150
df['EMA'] = ta.ema(df.close, length=150)

# Display the last few rows of the dataframe
df.tail()

print(f"\nFinal dataframe shape: {df.shape}")
# Limit the dataframe to the first 10,000 rows
df = df[0:10000]


def isPivot(candle, window):
    """
    function that detects if a candle is a pivot/fractal point
    args: candle index, window before and after candle to test if pivot
    returns: 1 if pivot high, 2 if pivot low, 3 if both and 0 default
    """
    # Check if the window extends beyond the dataframe boundaries
    if candle-window < 0 or candle+window >= len(df):
        return 0
    
    # Initialize pivot flags
    pivotHigh = 1
    pivotLow = 2
    # Iterate through the window around the candle
    for i in range(candle-window, candle+window+1):
        # Check if the current candle's low is higher than any in the window
        if df.iloc[candle].low > df.iloc[i].low:
            pivotLow=0
        # Check if the current candle's high is lower than any in the window
        if df.iloc[candle].high < df.iloc[i].high:
            pivotHigh=0
    # Return 3 if both pivot high and low
    if (pivotHigh and pivotLow):
        return 3
    # Return 1 if only pivot high
    elif pivotHigh:
        return pivotHigh
    # Return 2 if only pivot low
    elif pivotLow:
        return pivotLow
    # Return 0 if not a pivot point
    else:
        return 0


window=10
# apply lopp
df['isPivot'] = df.apply(lambda x: isPivot(x.name,window), axis=1)

def pointpos(x):
    if x['isPivot']==2:
        return x['low']-1e-3
    elif x['isPivot']==1:
        return x['high']+1e-3
    else:
        return np.nan
df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)

dfpl = df[7800:8000]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['open'],
                high=dfpl['high'],
                low=dfpl['low'],
                close=dfpl['close'])])

fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                marker=dict(size=5, color="MediumPurple"),
                name="pivot")
fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()

def detect_structure(candle, backcandles, window):
    """
    Attention! window should always be greater than the pivot window! to avoid look ahead bias
    """
    if (candle <= (backcandles+window)) or (candle+window+1 >= len(df)):
        return 0
    
    localdf = df.iloc[candle-backcandles-window:candle-window] #window must be greater than pivot window to avoid look ahead bias
    highs = localdf[localdf['isPivot'] == 1].high.tail(3).values
    lows = localdf[localdf['isPivot'] == 2].low.tail(3).values
    levelbreak = 0
    zone_width = 0.001
    if len(lows)==3:
        support_condition = True
        mean_low = lows.mean()
        for low in lows:
            if abs(low-mean_low)>zone_width:
                support_condition = False
                break
        if support_condition and (mean_low - df.loc[candle].close)>zone_width*2:
            levelbreak = 1

    if len(highs)==3:
        resistance_condition = True
        mean_high = highs.mean()
        for high in highs:
            if abs(high-mean_high)>zone_width:
                resistance_condition = False
                break
        if resistance_condition and (df.loc[candle].close-mean_high)>zone_width*2:
            levelbreak = 2
    return levelbreak

#df['pattern_detected'] = df.index.map(lambda x: detect_structure(x, backcandles=40, window=15))
df['pattern_detected'] = df.apply(lambda row: detect_structure(row.name, backcandles=60, window=11), axis=1)

df[df['pattern_detected']!=0]