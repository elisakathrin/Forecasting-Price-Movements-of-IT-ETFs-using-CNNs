import numpy as np
import pandas as pd

def generate_SMA_signals(sma_s,sma_l, data):
    """
    sma_s = Number of days for Simple Moving Average short period
    sma_l = Number of days for Simple Moving Average long period
    data = Price data of asset
    """
    # Calculate SMAs
    if sma_s < sma_l:
        data[f"SMA_{sma_s}_days"] = data.close.rolling(sma_s).mean()
        data[f"SMA_{sma_l}_days"] = data.close.rolling(sma_l).mean()

        # Check crossovers and determine positions
        data["position"] = np.where(data[f"SMA_{sma_s}_days"] > data[f"SMA_{sma_l}_days"], 1, -1)
        return data
    
    else:
        print("Simple Moving Average short period (sms_s) needs to be smaller than Simple Moving Average long period (sms_l)")
        
        
def sma_evaluation_short(data, sma_s, sma_l, short_limit_factor = 0.2):    
    """
    data: Dataframe with price data
    Assumption for short-selling: short positions need to be exited at end of observation period
    """
    data = generate_SMA_signals(sma_s,sma_l, data)
    available_capital_lst =  [10000]
    available_capital = 10000
    transaction_fee = 5
    fee_sum = 0
    execution_price = 0
    investment_sum = 0
    nr_shares_purchased = 0
    nr_shares_sold = 0
    nr_shares_held = [0]
    nr_shares_shorted = [0]
    transaction_list = [0]

    
    for i, position in enumerate(data.position):
        if position == transaction_list[-1]:
            transaction_list.append(position)
            pass

        # If position = 1: go long and exit any short positions
        elif position == 1 and available_capital_lst[-1] > 0:
            #Determine exeuction price --> Closing price of observation day
            execution_price = data.close.iloc[i]
            
            #Determine total sum available for investment --> Total available capital - transaction fee
            investment_sum = available_capital_lst[-1] - transaction_fee
            
            #Adjust most recent entry in available capital list: last entry minus investment sum and transaction fee
            available_capital_lst.append(available_capital_lst[-1] - investment_sum - transaction_fee)
            
            # Determine number of shares purchased --> total investment sum divided by execution price
            nr_shares_purchased = investment_sum / execution_price
            
            # Determine number of shares held --> Total number of shares purchased minus any short position if applicable
            nr_shares_held.append(nr_shares_held[-1] + nr_shares_purchased - nr_shares_shorted[-1])
            
            # Track transactions in the list --> add "Long" entry
            transaction_list.append(position)
            
            # Generate output
            # a) if there was short position: print that short position was closed and that long position was built
            if nr_shares_shorted[-1] > 0:
                print(f"Day {i}:") 
                print(f"Short position closed: repurchase of {nr_shares_shorted[-1]} shares.")
                print(f"Long position built: {round(nr_shares_held[-1],2)} units. Total value: {round(nr_shares_held[-1] * execution_price,2)} euros")
                nr_shares_shorted.append(0)
            else:
                print(f"Day {i}: purchase of {round(nr_shares_purchased,2)} units for total of {round(investment_sum,2)} euros")
            fee_sum += transaction_fee
            print("")

        
        elif position == -1 and nr_shares_held[-1] > 0:
            execution_price = data.close.iloc[i]
            
            #Set number of shares of long position that is being closed
            long_position_closed = round(nr_shares_held[-1],2)
            
            #Set base capital for calculation of short limit based on closed long position
            short_limit_base = long_position_closed * execution_price
                      
            #Find number of units shorted based on short_limit_base and factor:
            nr_shares_shorted.append(round(short_limit_base * short_limit_factor / execution_price,2))
            
            #Find total number of unit solds --> Sum of closed long position and shorted units
            nr_shares_sold = long_position_closed + nr_shares_shorted[-1]
            nr_shares_held.append(0)
            sale_sum = nr_shares_sold * execution_price - transaction_fee
            available_capital_lst.append(sale_sum)
            transaction_list.append(position)
            
            print(f"Day {i}:")
            print(f"Total sale:{round(nr_shares_sold,2)} units for total of {round(sale_sum,2)} euros")
            print(f"Closed long position: {long_position_closed} units")
            print(f"New short position: {nr_shares_shorted[-1]} units")
            print("")
            fee_sum += transaction_fee
                      
        if i == (len(data) - 1):
            # At end of observation period, short positions need to be closed
            closing_sum = nr_shares_shorted[-1] * data.close.iloc[i]
            available_capital_lst.append(available_capital_lst[-1] - closing_sum)
            print("End of observation period")
            print(f"Short position of {nr_shares_shorted[-1]} units closed for {closing_sum} euros.")
            nr_shares_shorted.append(0)
            
                      
        

    total_final_capital = available_capital_lst[-1] + nr_shares_held[-1] * data.close.iloc[-1]
    total_return = total_final_capital / available_capital_lst[0] - 1

    print("")
    print(f"End capital on day {len(data)}: {round(total_final_capital,2)} euros")
    print(f"Total return: {round(total_return*100,2)}%")
    print(f"Shares held at end of period: {round(nr_shares_held[-1],2)}")
    print(f"Total fee spending: {fee_sum}")
    
    return total_return, total_final_capital
    
    
def generate_mean_reversion_signals(sma, std_dev, data):
    data[f"SMA_{sma}_days"] = data.close.rolling(sma).mean()
    data["distance"] = data.close - data[f"SMA_{sma}_days"]
    data[f"Lower_Bollinger"] = data[f"SMA_{sma}_days"] - data.close.rolling(sma).std() * std_dev
    data[f"Upper_Bollinger"] = data[f"SMA_{sma}_days"] + data.close.rolling(sma).std() * std_dev
    
    #If closing price < Lower Bollinger Band --> asset is oversold, go long --> position = 1
    data["position"] = np.where(data.close < data.Lower_Bollinger, 1, np.nan)
    
    #If closing price > Upper Bollinger Band --> asset is overbought, go short --> position = -1
    data["position"] = np.where(data.close > data.Upper_Bollinger, -1, data["position"])
    
    #If price crosses SMA: Go neutral
    data["position"] = np.where(data.distance * data.distance.shift(1) < 0, 0, data["position"])
    
    #If none of the previous conditions is met: Hold previous position
    data["position"] = data.position.ffill().fillna(0)
    return data
    
    
def mean_rev_evaluation(sma, std_dev, data, short_limit_factor = 0.2):
    """
    data: Dataframe with price data
    Assumption for short-selling: short positions need to be exited at end of observation period
    """
    data = generate_mean_reversion_signals(sma, std_dev, data)
    available_capital_lst =  [10000]
    available_capital = 10000
    transaction_fee = 5
    fee_sum = 0
    execution_price = 0
    investment_sum = 0
    nr_shares_purchased = 0
    nr_shares_sold = 0
    nr_shares_held = [0]
    nr_shares_shorted = [0]
    transaction_list = [0]

    
    for i, position in enumerate(data.position):
        if position == transaction_list[-1]:
            transaction_list.append(position)
            pass

        # If position = 1: go long and exit any short positions
        elif position == 1 and available_capital_lst[-1] > 0:
            #Determine exeuction price --> Closing price of observation day
            execution_price = data.close.iloc[i]
            
            #Determine total sum available for investment --> Total available capital - transaction fee
            investment_sum = available_capital_lst[-1] - transaction_fee
            
            #Adjust most recent entry in available capital list: last entry minus investment sum and transaction fee
            available_capital_lst.append(available_capital_lst[-1] - investment_sum - transaction_fee)
            
            # Determine number of shares purchased --> total investment sum divided by execution price
            nr_shares_purchased = investment_sum / execution_price
            
            # Determine number of shares held --> Total number of shares purchased minus any short position if applicable
            nr_shares_held.append(nr_shares_held[-1] + nr_shares_purchased - nr_shares_shorted[-1])
            
            # Track transactions in the list --> add "Long" entry
            transaction_list.append(position)
            
            # Generate output
            # a) if there was short position: print that short position was closed and that long position was built
            if nr_shares_shorted[-1] > 0:
                print(f"Day {i}:") 
                print(f"Short position closed: repurchase of {nr_shares_shorted[-1]} shares.")
                print(f"Long position built: {round(nr_shares_held[-1],2)} units. Total value: {round(nr_shares_held[-1] * execution_price,2)} euros")
                nr_shares_shorted.append(0)
            else:
                print(f"Day {i}: purchase of {round(nr_shares_purchased,2)} units for total of {round(investment_sum,2)} euros")
            fee_sum += transaction_fee
            print("")

        
        elif position == -1 and nr_shares_held[-1] > 0:
            execution_price = data.close.iloc[i]
            
            #Set number of shares of long position that is being closed
            long_position_closed = round(nr_shares_held[-1],2)
            
            #Set base capital for calculation of short limit based on closed long position
            short_limit_base = long_position_closed * execution_price
                      
            #Find number of units shorted based on short_limit_base and factor:
            nr_shares_shorted.append(round(short_limit_base * short_limit_factor / execution_price,2))
            
            #Find total number of unit solds --> Sum of closed long position and shorted units
            nr_shares_sold = long_position_closed + nr_shares_shorted[-1]
            nr_shares_held.append(0)
            sale_sum = nr_shares_sold * execution_price - transaction_fee
            available_capital_lst.append(sale_sum)
            transaction_list.append(position)
            
            print(f"Day {i}:")
            print(f"Total sale:{round(nr_shares_sold,2)} units for total of {round(sale_sum,2)} euros")
            print(f"Closed long position: {long_position_closed} units")
            print(f"New short position: {nr_shares_shorted[-1]} units")
            print("")
            fee_sum += transaction_fee
                      
        # If position = 0: Close any short and long positions
        elif position == 0:
            if nr_shares_held[-1] > 0:
                sale_sum = nr_shares_held[-1] * data.close.iloc[i] - transaction_fee
                available_capital_lst.append(available_capital_lst[-1] + sale_sum)
                fee_sum += transaction_fee
                print(f"Day {i}:")
                print(f"Went neutral. Long position closed - sold {round(nr_shares_held[-1],2)} units for {round(sale_sum,2)} euros.")
                print("")
                nr_shares_held.append(0)
                transaction_list.append(0)
                
            elif nr_shares_shorted[-1] > 0:
                buy_sum = nr_shares_shorted[-1] * data.close.iloc[i]
                available_capital_lst.append(available_capital_lst[-1] - buy_sum)
                fee_sum += transaction_fee
                print(f"Day {i}:")
                print(f"Went neutral. Short position closed - bought {round(nr_shares_shorted[-1],2)} units for {round(buy_sum,2)} euros.")
                print("")
                nr_shares_held.append(0)
                transaction_list.append(0)
                
                
        if i == (len(data) - 1) and nr_shares_shorted[-1] > 0:
            # At end of observation period, short positions need to be closed
            closing_sum = nr_shares_shorted[-1] * data.close.iloc[i]
            available_capital_lst.append(available_capital_lst[-1] - closing_sum)
            print("End of observation period")
            print(f"Short position of {nr_shares_shorted[-1]} units closed for {closing_sum} euros.")
            nr_shares_shorted.append(0)
            
                      
        

    total_final_capital = available_capital_lst[-1] + nr_shares_held[-1] * data.close.iloc[-1]
    total_return = total_final_capital / available_capital_lst[0] - 1

    print("")
    print(f"End capital on day {len(data)}: {round(total_final_capital,2)} euros")
    print(f"Total return: {round(total_return*100,2)}%")
    print(f"Shares held at end of period: {round(nr_shares_held[-1],2)}")
    print(f"Total fee spending: {fee_sum}")
    
    return total_return, total_final_capital



    
    