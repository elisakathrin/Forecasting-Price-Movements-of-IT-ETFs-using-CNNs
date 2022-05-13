import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from statsmodels.tsa.stattools import adfuller
from mpl_toolkits.axes_grid1 import ImageGrid


def data_loader(path="../../DATA/VGT_historical data_2005.csv"):  
    data = pd.read_csv(path, names=["date", "close", "open", "high", "low", "volume", "change%"], skiprows=1)
    data['date']= pd.to_datetime(data['date'])
    data['vol_unit'] = data['volume'].str[-1]
    data['volume'] = data['volume'].str[:-1]
    data['volume'] = pd.to_numeric(data['volume'])
    data['volume'] = np.where((data['vol_unit']=="K"), data["volume"]*1000, data["volume"]*1000000)
    data.drop("vol_unit", axis = 1, inplace = True)
    data['change%'] = data['change%'].str[:-1]
    data['change%'] = pd.to_numeric(data['change%'])
    data.set_index("date", inplace=True) 
    data.sort_index(inplace=True)
    return data


def append_var_to_data(data, var_name, path):
    df = pd.read_csv(path, usecols=["Date", "Price"])
    df.rename({"Price": var_name}, axis=1, inplace=True)
    df['Date']= pd.to_datetime(df['Date'])
    df.set_index("Date", inplace=True) 
    df.sort_index(inplace=True)
    data = data.merge(df, how= "left", left_on=data.index, right_on=df.index, copy=False )
    data.set_index("key_0", inplace=True)
    return data

def augmented_dickey_fuller_test(time_series):
    
    # Augmented Dickey-Fuller Test
    # https://www.machinelearningplus.com/time-series/augmented-dickey-fuller-test/
    # The presence of a unit root means the time series is non-stationary. 

    # H0: There is a unit root, 
    # H1: There is no unit root. 
    # If the pvalue is above a critical size, then we cannot reject that there is a unit root.
    # Significance Level: 0.05 -> if p above 0.05 we have non-stationarity


    dickey_fuller = adfuller(time_series, maxlag=None, regression='c', autolag='AIC', store=False, regresults=False)

    print('ADF Statistic: %f' % dickey_fuller[0])

    print('p-value: %f' % dickey_fuller[1])

    print('Critical Values:')

    for key, value in dickey_fuller[4].items():
        print('\t%s: %.3f' % (key, value))
    if dickey_fuller[0] < dickey_fuller[4]["5%"]:
        print ("Reject Ho - Time Series is Stationary")
    else:
        print ("Failed to Reject Ho - Time Series is Non-Stationary. Action required!")

        
def plot_autocorr(time_series, lags=30):
    plt.title("Autocorrelation Plot")
    plt.xlabel("Lags")
    plt.acorr(time_series, maxlags = 30)
    plt.grid(True)
    plt.show()
    
    
def create_labels(df, col_name, window_size=5):  
    """
    Data is labeled as per the logic in research paper
    Label code : BUY => 1, SELL => 0, HOLD => 2
    params :
        df => Dataframe with data
        col_name => name of column which should be used to determine strategy
    returns : numpy array with integer codes for labels with
              size = total-(window_size)+1
    """

    print("creating label with bazel's strategy")
    counter_row = 0
    number_of_days_in_File = len(df)
    labels = np.zeros(number_of_days_in_File)
    labels[:] = np.nan
    print("Calculating labels")
    pbar = tqdm(total=number_of_days_in_File)

    while counter_row < number_of_days_in_File:
        counter_row += 1
        if counter_row > window_size:
            window_begin_index = counter_row - window_size
            window_end_index = window_begin_index + window_size - 1
            window_middle_index = int((window_begin_index + window_end_index) / 2)

            min_ = np.inf
            min_index = -1
            max_ = -np.inf
            max_index = -1
            for i in range(window_begin_index, window_end_index + 1):
                number = df.iloc[i][col_name]  # number is the price
                if number < min_:
                    min_ = number
                    min_index = i
                if number > max_:
                    max_ = number
                    max_index = i

            if max_index == window_middle_index:
                labels[window_middle_index] = 0  # SELL
            elif min_index == window_middle_index:
                labels[window_middle_index] = 1  # BUY
            else:
                labels[window_middle_index] = 2  # HOLD

        pbar.update(1)

    pbar.close()
    return labels


def plot_gaf(datapoint, gasf, gadf, mtf, features):
        
    for f in features:
        sum_field=gasf[datapoint,:,:,f]
        dif_field=gadf[datapoint,:,:,f]
        trans_fiels=mtf[datapoint,:,:,f]
        
        fig = plt.figure(figsize=(15, 5))
        grid = ImageGrid(fig, 111, nrows_ncols=(1, 3),
                         axes_pad=0.15,
                         share_all=True,
                         cbar_location="left",
                        cbar_mode="single",
                         cbar_size="7%",
                         cbar_pad=0.3,
                         )
        images = [sum_field, dif_field, trans_fiels]
        titles = ['Gramian Angular Summation Fields', 'Gramian Angular Difference Field', "Markov Transition Field"]
        for image, title, ax in zip(images, titles, grid):
            im = ax.imshow(image, cmap='binary', origin='lower')
            ax.set_title(title, fontdict={'fontsize': 12})
        ax.cax.colorbar(im)
        ax.cax.toggle_label(True)
        plt.suptitle("Representation for component {}".format(f), y=0.98, fontsize=16)
        plt.show()
        print("\n")
    
    