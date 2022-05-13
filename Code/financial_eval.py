def financial_performance_evaluation(prices, labels):    
    """
    Prices: dataframe with true prices
    Labels: labels predicted by model
    """
    available_capital_lst =  [10000]
    available_capital = 10000
    transaction_fee = 5
    fee_sum = 0
    execution_price = 0
    investment_sum = 0
    nr_shares_purchased = 0
    nr_shares_sold = 0
    nr_shares_held = [0]
    transaction_list = [0]

    
    for i, label in enumerate(labels):
        if label == 0 or label == transaction_list[-1]:
            pass

        elif label == 1 and available_capital_lst[-1] > 0:
            execution_price = prices.close.iloc[i]
            investment_sum = available_capital_lst[-1] - transaction_fee
            available_capital_lst.append(available_capital_lst[-1] - investment_sum)
            nr_shares_purchased = investment_sum / execution_price
            nr_shares_held.append(nr_shares_held[-1] + nr_shares_purchased)
            transaction_list.append(label)
            print(f"Day {i}: purchase of {round(nr_shares_purchased,2)} units for total of {round(investment_sum,2)} euros")
            fee_sum += transaction_fee

        elif label == -1 and nr_shares_held[-1] > 0:
            execution_price = prices.close.iloc[i]
            nr_shares_sold = nr_shares_held[-1]
            nr_shares_held.append(nr_shares_held[-1] - nr_shares_sold)
            sale_sum = nr_shares_sold * execution_price - transaction_fee
            available_capital_lst.append(sale_sum)
            transaction_list.append(label)
            print(f"Day {i}: sale of {round(nr_shares_sold,2)} units for total of {round(sale_sum,2)} euros")
            print(f"Return of transaction: {round((available_capital_lst[-1] / available_capital_lst[-3]-1)*100,2)}%")
            print("")
            fee_sum += transaction_fee

    total_final_capital = available_capital_lst[-1] + nr_shares_held[-1] * prices.close.iloc[-1]
    total_return = total_final_capital / available_capital_lst[0] - 1

    print("")
    print(f"End capital on day {len(prices)}: {round(total_final_capital,2)} euros")
    print(f"Total return: {round(total_return*100,2)}%")
    print(f"Shares held at end of period: {round(nr_shares_held[-1],2)}")
    print(f"Total fee spending: {fee_sum}")
    
    
    
def financial_performance_model_short(prices, labels, short_limit_factor = 0.2):    
    """
    Prices: dataframe with true prices
    Labels: labels predicted by model
    Assumption for short-selling: short positions need to be exited at end of observation period
    """
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

    
    for i, label in enumerate(labels):
        if label == 0 or label == transaction_list[-1]:
            pass

        # If label = 1: go long and exit any short positions
        elif label == 1 and available_capital_lst[-1] > 0:
            #Determine exeuction price --> Closing price of observation day
            execution_price = prices.close.iloc[i]
            
            #Determine total sum available for investment --> Total available capital - transaction fee
            investment_sum = available_capital_lst[-1] - transaction_fee
            
            #Adjust most recent entry in available capital list: last entry minus investment sum and transaction fee
            available_capital_lst.append(available_capital_lst[-1] - investment_sum - transaction_fee)
            
            # Determine number of shares purchased --> total investment sum divided by execution price
            nr_shares_purchased = investment_sum / execution_price
            
            # Determine number of shares held --> Total number of shares purchased minus any short position if applicable
            nr_shares_held.append(nr_shares_held[-1] + nr_shares_purchased - nr_shares_shorted[-1])
            
            # Track transactions in the list --> add "Long" entry
            transaction_list.append(label)
            
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

        
        elif label == -1 and nr_shares_held[-1] > 0:
            execution_price = prices.close.iloc[i]
            
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
            transaction_list.append(label)
            
            print(f"Day {i}:")
            print(f"Total sale:{round(nr_shares_sold,2)} units for total of {round(sale_sum,2)} euros")
            print(f"Closed long position: {long_position_closed} units")
            print(f"New short position: {nr_shares_shorted[-1]} units")
            print("")
            fee_sum += transaction_fee
                      
        if i == (len(labels) - 1):
            # At end of observation period, short positions need to be closed
            closing_sum = round(nr_shares_shorted[-1] * prices.close.iloc[i],2)
            available_capital_lst.append(available_capital_lst[-1] - closing_sum)
            print(f"End of observation period.")
            print(f"Short position of {nr_shares_shorted[-1]} units closed for {closing_sum} euros.")
            nr_shares_shorted.append(0)
            
                      
        

    total_final_capital = available_capital_lst[-1] + nr_shares_held[-1] * prices.close.iloc[-1]
    total_return = total_final_capital / available_capital_lst[0] - 1

    print("")
    print(f"End capital on day {len(prices)}: {round(total_final_capital,2)} euros")
    print(f"Total return: {round(total_return*100,2)}%")
    print(f"Shares held at end of period: {round(nr_shares_held[-1],2)}")
    print(f"Total fee spending: {fee_sum}")
    

def buy_hold_evaluation(data):
    start_capital = 10000
    nr_shares_purchased = start_capital / data.close.iloc[0]
    end_capital = round(nr_shares_purchased * data.close.iloc[-1],2)
    total_return = round(end_capital / start_capital - 1,2)
    print(f"End capital: {end_capital} euros")
    print(f"Total return through Buy & Hold: {total_return*100}%")
    return total_return, end_capital