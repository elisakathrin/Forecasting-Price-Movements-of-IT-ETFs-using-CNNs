# Method 1: Using daily adjusted barriers based on daily volatility 

# Label creation if only using daily data
import pandas as pd
def get_daily_volatility(df,span0=20):
    # simple percentage returns
    df0 = df.close.pct_change()
    # 20 days, a month EWM's std as boundary
    df0=df0.ewm(span=span0).std().to_frame("volatility")
    df_clean = df0.dropna()
    return df0, df_clean

def adjust_data(df, volatilities_raw):
    df_clean = df[volatilities_raw.isna()['volatility'] == False]
    return df_clean

def get_barriers(df, volatilities, upper_lower_multipliers):
    barriers = df[['close','high','low']].copy()
    barriers['volatility'] = volatilities['volatility']
    top_barrier = [0]
    bottom_barrier = [0]
    for i in range(len(barriers)-1):
        vol = volatilities.volatility.iloc[i]
        if upper_lower_multipliers[0] > 0:
            top_barrier.append(barriers.close.iloc[i] + barriers.close.iloc[i] * upper_lower_multipliers[0] * vol)
        else:
            #set it to NaNs
            top_barrier = pd.Series(index=prices.index)
        #set the bottom barrier

        if upper_lower_multipliers[1] > 0:
            bottom_barrier.append(barriers.close.iloc[i] - barriers.close.iloc[i] * upper_lower_multipliers[1] * vol)                  
        else: 
            #set it to NaNs
            bottom_barrier = pd.Series(index=prices.index)
    barriers['top_barrier'] = top_barrier
    barriers['bottom_barrier'] = bottom_barrier
    return barriers

def get_labels_daily(df, upper_lower_multipliers):
    """
    top_barrier: profit taking limit
    bottom_barrier:stop loss limit
    daily_volatiliy: average daily volatility based on 20-day moving average
    barriers_df: DataFrame containing top and bottom barriers on a per-day base
    """
    daily_volatility_raw, daily_volatility_clean = get_daily_volatility(df)
    df = adjust_data(df, daily_volatility_raw)
    barriers_df = get_barriers(df = df, volatilities = daily_volatility_clean, upper_lower_multipliers = upper_lower_multipliers)
    labels = []
    nr_double_labels = 0
    for i in range(len(barriers_df.index)-1):
        if barriers_df.high.iloc[i+1] >= barriers_df.top_barrier.iloc[i+1]: 
            labels.append(1)
        elif barriers_df.low.iloc[i+1] <= barriers_df.bottom_barrier.iloc[i+1]: 
            labels.append(-1)  
        else: 
            labels.append(0)

        if barriers_df.high.iloc[i+1] >= barriers_df.top_barrier.iloc[i+1] and barriers_df.low.iloc[i+1] <= barriers_df.bottom_barrier.iloc[i+1]:
            nr_double_labels += 1

    labels.append(0)
    perc_double_labels = round(nr_double_labels / len(df),4)
    barriers_df['label'] = labels
    return barriers_df, barriers_df.label, perc_double_labels 