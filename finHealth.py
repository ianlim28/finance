import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import requests


## INCOME STATEMENT ##
####################################################################################
############# Income Statement compare across companies ############################
####################################################################################

def latestIncomeStatement(quote):
    r = requests.get(f"https://financialmodelingprep.com/api/v3/financials/income-statement/{quote}")
    r = r.json()
    incomeStatement = r['financials']
    incomeStatement = pd.DataFrame.from_dict(incomeStatement)
    incomeStatement = incomeStatement.T
    incomeStatement.columns = incomeStatement.iloc[0]
    incomeStatement.reset_index(inplace=True)
    incomeStatement = incomeStatement.iloc[:,0:2]
    incomeStatement = incomeStatement.rename(columns={incomeStatement.columns[1]:quote})

    cols = incomeStatement.columns.drop('index')
    incomeStatement[cols] = incomeStatement[cols].apply(pd.to_numeric, errors='coerce')
    incomeStatement = incomeStatement.iloc[1:,:]
    incomeStatement[quote] = incomeStatement[quote]/incomeStatement.iloc[0,1]
    incomeStatement[quote] = pd.Series(["{0:.2f}%".format(val*100) for val in incomeStatement[quote]],index=incomeStatement.index)
    return incomeStatement



# df = latestIncomeStatement('FB')

# listofstocks = ['AAPL','MSFT','GOOGL']

# for i in listofstocks:
#     y = latestIncomeStatement(i)
#     df = df.merge(y, on='index')

# df

####################################################################################
############# Income Statement History for one company #############################
####################################################################################


def incomeStatementHistorical(quote):
    r = requests.get(f"https://financialmodelingprep.com/api/v3/financials/income-statement/{quote}")
    r = r.json()
    incomeStatement = r['financials']
    incomeStatement = pd.DataFrame.from_dict(incomeStatement)
    incomeStatement = incomeStatement.T
    incomeStatement.columns = incomeStatement.iloc[0]
    incomeStatement.reset_index(inplace=True)
    incomeStatement = incomeStatement.iloc[1:,0:]
    #incomeStatement = incomeStatement.rename(columns={incomeStatement.columns[1]:quote})

    cols = incomeStatement.columns.drop('index')
    incomeStatement[cols] = incomeStatement[cols].apply(pd.to_numeric, errors='coerce')

    ####################################
    # Original Copy of Income Statement#
    ####################################
    ori_incomeStatement = incomeStatement.copy()


    ####################
    # percentage change#
    ####################
    incomeStatement[cols] = incomeStatement[cols].pct_change(-1, axis=1)
    incomeStatement[cols] = incomeStatement[cols].multiply(100)
    for col in cols:
        incomeStatement[col] = round(incomeStatement[col],2).astype(str) + '%'
    incomeStatement['index'] = incomeStatement['index'].apply(lambda x: "{}{}".format(x,' chg_prev'))
    chg_incomeStatement = incomeStatement.copy()
    
    ####################
    ## Combining both ##
    ####################
    df = pd.concat([ori_incomeStatement, chg_incomeStatement])
    df.sort_index(inplace=True)
    
    # Dropping columns not needed for now
    to_drop = ['Revenue Growth','Revenue Growth chg_prev','Net Income - Non-Controlling int chg_prev','Net Income - Non-Controlling int','Net Income - Discontinued ops','Net Income - Discontinued ops chg_prev','Weighted Average Shs Out chg_prev']
    df = df[~df['index'].isin(to_drop)]
    df.sort_values('index')
    df.reset_index(drop=True, inplace=True)
    
    return df


##### BALANCE SHEET ######
def balanceSheetHistorical(quote):

    r = requests.get(f"https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/{quote}")
    r = r.json()
    balanceSheet = r['financials']
    balanceSheet = pd.DataFrame.from_dict(balanceSheet)
    balanceSheet['Book Value'] = balanceSheet['Total assets'].astype('float32') - balanceSheet['Total liabilities'].astype('float32')
    balanceSheet = balanceSheet.T
    balanceSheet.columns = balanceSheet.iloc[0]
    balanceSheet = balanceSheet.iloc[1:,:]
    balanceSheet.reset_index(inplace=True)


    ####################################
    ### Original Copy of Balance Sheet##
    ####################################
    ori_balanceSheet = balanceSheet.copy()


    ####################
    # percentage change#
    ####################
    cols = ori_balanceSheet.columns.drop('index')
    balanceSheet[cols] = balanceSheet[cols].apply(pd.to_numeric, errors='coerce')
    balanceSheet[cols] = balanceSheet[cols].pct_change(-1, axis=1)
    balanceSheet[cols] = balanceSheet[cols].multiply(100)
    for col in cols:
        balanceSheet[col] = round(balanceSheet[col],2).astype(str) + '%'
    balanceSheet['index'] = balanceSheet['index'].apply(lambda x: "{}{}".format(x,'_chg_prev'))
    chg_balanceSheet = balanceSheet.copy()

    df = pd.concat([ori_balanceSheet, chg_balanceSheet])
    df.sort_index(inplace=True)
    df.reset_index(inplace=True, drop= True)
    return df


def warrenBigFour(quote):
    
    """
    Operating Income:Operating income, often referred to as EBIT or earnings before interest and taxes, is a profitability formula that calculates a company’s profits derived from operations. In other words, it measures the amount of money a company makes from its core business activities not including other income expenses not directly related to the core activities of the business.
    Operating Income formula: Gross income - Operating expenses - Depreciation & Amortization
    
    Book Value: Book value is the total value of a business' assets found on its balance sheet, and represents the value of all assets if liquidated.
    Book Value formula = total assets - total liabilities
    
    Net income: The net income formula is calculated by subtracting total expenses from total revenues
    Net income: Total revnenues - total expenses    
    """
    
    # Getting data from income statement
    df = incomeStatementHistorical(quote)
    keyMetric = ['Net Income','Net Income chg_prev','Revenue','Revenue chg_prev','Operating Income','Operating Income chg_prev']
    df_metric1 = df.loc[df['index'].isin(keyMetric)]
    
    # getting data from balance sheet
    df = balanceSheetHistorical(quote)
    keyMetric = ['Book Value','Book Value_chg_prev']
    df_metric2 = df.loc[df['index'].isin(keyMetric)]
    test = pd.concat([df_metric1, df_metric2])
    test = test.sort_values('index')
    test.reset_index(inplace=True, drop=True)
    return test



### FINANCIAL RATIOS ###
def financialratios(quote):
    r = requests.get(f"https://financialmodelingprep.com/api/v3/financial-ratios/{quote}")
    r = r.json()
    valuation = r['ratios'][0]['investmentValuationRatios']
    profitability = r['ratios'][0]['profitabilityIndicatorRatios']
    operating = r['ratios'][0]['operatingPerformanceRatios']
    liquidity = r['ratios'][0]['liquidityMeasurementRatios']
    debt = r['ratios'][0]['debtRatios']

    valuation = pd.DataFrame(list(valuation.items()),columns=['Ratio',quote])
    profitability = pd.DataFrame(list(profitability.items()),columns=['Ratio',quote])
    operating = pd.DataFrame(list(operating.items()),columns=['Ratio',quote])
    liquidity = pd.DataFrame(list(liquidity.items()),columns=['Ratio',quote])
    debt = pd.DataFrame(list(debt.items()),columns=['Ratio',quote])

    final_df = pd.concat([valuation, profitability, operating, liquidity, debt])
    return final_df


# listofstocks = ['AAPL','MSFT','TSLA']
# x = financialratios('FB')

# for i in listofstocks:
#     y = financialratios(i)
#     x = x.merge(y, on='Ratio')
    
# display_all(x.drop_duplicates())