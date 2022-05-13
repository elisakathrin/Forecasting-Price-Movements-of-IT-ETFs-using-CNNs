"""
Library: https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html

-> Hull Moving Average missing, but Marc's code did not work either
-> Up for Discussion: which windows for which variables 

"""

from ta.trend import *
from ta.volatility import *
from ta.momentum import *
from ta.volume import *
from ta.others import *
import numpy as np
import pandas as pd

# Class setup indicators with ta library:
class TechnicalIndicator():
    def __init__(self, df):
        self.df = df
    
    def create_features(self):
        
        self.get_dr() # daily return
        
        self.get_ppo(col_name="close") # Percentage Price Oscillator, https://www.investopedia.com/terms/p/ppo.asp
        self.get_ppo(col_name="open") # https://www.investopedia.com/terms/p/ppo.asp
        self.get_MACD() # https://www.investopedia.com/terms/m/macd.asp
        
        self.get_kst() # KST Oscillator
        
        for window in range(2,31):
            self.get_roc(window=window)
            self.get_rsi(window=window)
            self.get_mfi(window=window)
            self.get_cmf(window=window)
            self.get_dpo(window=window)
            self.get_adx(window=window)
            self.get_fi(window=window)
            self.get_emv(window=window)
            self.get_bb(window=window)
            self.get_atr(window=window)
            self.get_williamR(look_back=window)
            self.get_sma(window=window)
            self.get_ema(window=window)
            self.get_wma(window=window)
            self.get_trix(window=window)
            self.get_CCI(window=window)
            self.get_so(window=window)
            self.get_kc(window=window)
            
        
        self.get_CMO(intervals=np.arange(2,31))
        
        
    def get_dr(self, close: str = "close"):  
        """
        Daily Return
        """
        self.df['daily_return'] = DailyReturnIndicator(self.df[close]).daily_return()


    def get_roc(self, col_name: str = "close", window: int = 12):
        """
        The Rate-of-Change (ROC) indicator, which is also referred to as simply Momentum, is a pure momentum oscillator 
        that measures the percent change in price from one period to the next. The ROC calculation compares the current 
        price with the price “n” periods ago.
        """
        self.df['roc_{}'.format(window)] = ROCIndicator(self.df[col_name], window).roc()
        

    def get_ppo(self, col_name: str = "close"):
        """
        The Percentage Price Oscillator (PPO) is a momentum oscillator that measures the difference between two moving 
        averages as a percentage of the larger moving average.
        """
        ppo_indicator = PercentagePriceOscillator(close=self.df[col_name], window_slow=26, window_fast=12, window_sign=9, fillna=False)
        self.df['ppo'] = ppo_indicator.ppo()
        
        
    def get_rsi(self, col_name: str = "close", window: int = 14):
        """
        The Relative Strength Index RSI) is a momentum indicator used in technical analysis that measures the magnitude 
        of recent price changes to evaluate overbought or oversold conditions in the price of a stock or other asset. 
        """
        self.df['rsi_{}'.format(window)] = RSIIndicator(self.df[col_name], window).rsi()

        
    def get_mfi(self, high: str = "high", low: str = "low", close: str = "close", volume: str = "volume", window: int = 14):
        """
        Money Flow Index* (MFI) uses both price and volume to measure buying and selling pressure.
        """
        indicator_mfi = MFIIndicator(self.df[high], self.df[low], self.df[close], self.df[volume], window)
        self.df['mfi_{}'.format(window)] = indicator_mfi.money_flow_index()

        
    def get_cmf(self, high: str = "high", low: str = "low", close: str = "close", volume: str = "volume", window: int = 14):
        """
        Chaikin Money Flow (CMF) it measures the amount of Money Flow Volume over a specific period.
        """
        indicator_cmf = ChaikinMoneyFlowIndicator(self.df[high], self.df[low], self.df[close], self.df[volume], window)
        self.df['cmf_{}'.format(window)] = indicator_cmf.chaikin_money_flow()

        
    def get_dpo(self, close: str = "close", window: int = 20):
        """
        Detrended Price Oscillator (DPO) Is an indicator designed to remove trend from price and make it easier to identify cycles.
        """
        indicator_dpo = DPOIndicator(self.df[close], window)
        self.df['dpo_{}'.format(window)] = indicator_dpo.dpo()

        
    def get_kst(self, close: str = "close", roc1: int = 10, roc2: int = 15, roc3: int = 20, roc4: int = 30, 
                window1: int = 10, window2: int = 10, window3: int = 10, window4: int = 15, nsig: int= 9, fillna: bool = False):  
        """
        KST Oscillator (KST) is useful to identify major stock market cycle junctures because its formula is weighed 
        to be more greatly influenced by the longer and more dominant time spans, in order to better reflect the primary 
        swings of stock market cycle.
        """
        indicator_kst = KSTIndicator(self.df[close], roc1, roc2, roc3, roc4, window1, window2, window3, window4, nsig, fillna)
        self.df['kst'] = indicator_kst.kst()

        
    def get_adx(self, high: str = "high", low: str = "low", close: str = "close", window: int = 14):
        """
        Average Directional Movement Index (ADX)
        """
        indicator_adx = ADXIndicator(self.df[high], self.df[low], self.df[close], window)
        self.df['adx_{}'.format(window)] = indicator_adx.adx()

        
    def get_fi(self, close: str = "close", volume: str = "volume", window: int = 13):
        """
        Force Index (FI) it illustrates how strong the actual buying or selling pressure is. High positive values mean 
        there is a strong rising trend, and low values signify a strong downward trend.
        """
        indicator_fi = ForceIndexIndicator(self.df[close], self.df[volume], window)
        self.df['fi_{}'.format(window)] = indicator_fi.force_index()

        
    def get_emv(self, high: str = "high", low: str = "low", volume: str = "volume", window: int = 14):
        """
        Ease of movement (EoM, EMV) it relate an asset’s price change to its volume and is particularly useful for assessing the strength of a trend.
        """
        indicator_emv = EaseOfMovementIndicator(self.df[high], self.df[low], self.df[volume], window)
        self.df['emv_{}'.format(window)] = indicator_emv.ease_of_movement()

        
    def get_bb(self, close: str = "close", window: int = 20):
        """
        Bollinger Bands are envelopes plotted at a standard deviation level above and below a simple moving average of the price. 
        Bollinger bands help determine whether prices are high or low on a relative basis.
        """
        indicator_bb = BollingerBands(self.df[close], window)
        #self.df['bb_bbm_{}'.format(window)] = indicator_bb.bollinger_mavg()
        self.df['bb_bbh_{}'.format(window)] = indicator_bb.bollinger_hband()
        self.df['bb_bbl_{}'.format(window)] = indicator_bb.bollinger_lband()
        #self.df['bb_bbhi_{}'.format(window)] = indicator_bb.bollinger_hband_indicator()
        #self.df['bb_bbli_{}'.format(window)] = indicator_bb.bollinger_lband_indicator()
        #self.df['bb_bbhi_{}'.format(window)] = indicator_bb.bollinger_hband()
        #self.df['bb_bbw_{}'.format(window)] = indicator_bb.bollinger_wband()
        #self.df['bb_bbp_{}'.format(window)] = indicator_bb.bollinger_pband()

        
    def get_atr(self, high: str = "high", low: str = "low", close: str = "close", window: int = 14):
        """
        Average True Range indicator provide an indication of the degree of price volatility. 
        Strong moves, in either direction, are often accompanied by large ranges, or large True Ranges.
        """
        indicator_atr = AverageTrueRange(self.df[high], self.df[low], self.df[close], window)
        self.df['atr_{}'.format(window)] = indicator_atr.average_true_range()

        
    def get_williamR(self, high: str = "high", low: str = "low", close: str = "close", look_back: int = 14):
        """
        The Williams Percent Range is a type of momentum indicator that moves between 0 and -100 and measures overbought and oversold levels. 
        """
        self.df["wr_" + str(look_back)] = WilliamsRIndicator(self.df[high], self.df[low], self.df[close], look_back, fillna=True).williams_r()

    
    def get_MACD(self, close: str = "close"):
        """
        Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages of prices.
        """
        macd_ind = MACD(self.df[close], window_slow=26, window_fast=12, window_sign=9, fillna=False)
        self.df["macd"] = macd_ind.macd()


    def get_sma(self, col_name: str = "close", window: int = 14):
        """
        Simple Moving Average
        """
        sma_indicator = SMAIndicator(close = self.df[col_name], window = window, fillna = False)
        self.df['sma_{}'.format(window)] = sma_indicator.sma_indicator()


    def get_ema(self, col_name: str = "close", window: int = 14): 
        """
        Exponential Moving Average
        """
        ema_indicator = EMAIndicator(close = self.df[col_name], window = window, fillna = False)
        self.df['ema_{}'.format(window)] = ema_indicator.ema_indicator()

                
    def get_wma(self, col_name: str = "close", window: int = 9):
        """
        Weighted Moving Average
        """
        indicator_wma = WMAIndicator(self.df[col_name], window)
        self.df['wma_{}'.format(window)] = indicator_wma.wma()
    
        
    def get_trix(self, col_name: str = "close", window: int = 15):
        """
        Trix shows the percent rate of change of a triple exponentially smoothed moving average.
        """
        indicator_trix = TRIXIndicator(self.df[col_name], window)
        self.df['trix_{}'.format(window)] = indicator_trix.trix()


    def get_CCI(self, high: str = "high", low: str = "low", close: str = "close", window: int = 20):
        """
        Commodity Channel Index(CCI) measures the difference between a security’s price change and its average price change. 
        High positive readings indicate that prices are well above their average, which is a show of strength. 
        Low negative readings indicate that prices are well below their average, which is a show of weakness.
        """
        cci_inidcator = CCIIndicator(high=self.df[high], low=self.df[high], close=self.df[close], window=window, constant=0.015, fillna=False)
        self.df['cci_{}'.format(window)] = cci_inidcator.cci()

        
    def get_CMO(self,  intervals: int, col_name: str = "close"):
        """
        Chande Momentum Oscillator is created by calculating the difference between the sum of all recent higher closes 
        and the sum of all recent lower closes and then dividing the result by the sum of all price movement over a given time period. 
        
        As per https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo

        CMO = 100 * ((Sum(ups) - Sum(downs))/ ( (Sum(ups) + Sum(downs) ) )
        range = +100 to -100

        params: df -> dataframe with financial instrument history
                col_name -> column name for which CMO is to be calculated
                intervals -> list of periods for which to calculated

        return: None (adds the result in a column)
        """
        
        def calculate_CMO(series, period):
            # num_gains = (series >= 0).sum()
            # num_losses = (series < 0).sum()
            sum_gains = series[series >= 0].sum()
            sum_losses = np.abs(series[series < 0].sum())
            cmo = 100 * ((sum_gains - sum_losses) / (sum_gains + sum_losses))
            return np.round(cmo, 3)

        diff = self.df[col_name].diff()[1:]  # skip na
        for period in intervals:
            self.df['cmo_' + str(period)] = np.nan
            res = diff.rolling(period).apply(calculate_CMO, args=(period,), raw=False)
            self.df['cmo_' + str(period)][1:] = res
            
            
    def get_so(self, window: int=14):
        """
        Stochastic Oscillator
        """
        indicator_so=StochasticOscillator(high=self.df["high"], low=self.df["low"], close=self.df["close"], window=window)
        self.df['stoch_{}'.format(window)] = indicator_so.stoch()
        self.df['stoch_signal_{}'.format(window)] = indicator_so.stoch_signal()
    
    def get_kc(self, window: int=10, window_atr: int=5):
        """
        Keltner Channels
        """
        indicator_kc=KeltnerChannel(high=self.df["high"], low=self.df["low"], close=self.df["close"], window=window, window_atr=window_atr, original_version=False)
        self.df['kc_hband_{}'.format(window)] = indicator_kc.keltner_channel_hband()
        #self.df['kc_hband_ind_{}'.format(window)] = indicator_kc.keltner_channel_hband_indicator()
        self.df['kc_lband_{}'.format(window)] = indicator_kc.keltner_channel_lband()
        #self.df['kc_lband_ind_{}'.format(window)] = indicator_kc.keltner_channel_lband_indicator()
        self.df['kc_mband_{}'.format(window)] = indicator_kc.keltner_channel_mband()
        #self.df['kc_pband_{}'.format(window)] = indicator_kc.keltner_channel_pband()
        #self.df['kc_wband_{}'.format(window)] = indicator_kc.keltner_channel_wband()
        
        
