# Imports
import pandas
import numpy
import scipy.stats.distributions as dist

#open the dataset we're using
dataframe = pandas.read_excel("C:/Users/Spencer/Desktop/NHL_Contract_Data_Scraper/Data/complete_2023-03-03.xlsx")

#Check if NDS in spreadsheet
if 'NDS' in dataframe.columns:
    print("NDS already in dataframe, moving to next operation")
#if it's not, add it and calculate
else:
    #create empty list
    ndsList = []
    for index, row in dataframe.iterrows():
        #calcultae NDS with data from dataframe
        highDangerShots = dataframe.loc[index, "OnIce_A_highDangerShots"]
        dZoneGiveaways = dataframe.loc[index, "I_F_dZoneGiveaways"]
        negativeDS = highDangerShots + dZoneGiveaways
        #append to list
        ndsList.append(negativeDS)
    #add list to spreadsheet as new column
    dataframe["NDS"] = ndsList
    #save spreadsheet
    dataframe.to_excel("C:/Users/Spencer/Desktop/NHL_Contract_Data_Scraper/Data/complete_2023-03-03.xlsx")
    print("file updated with NDS")
        

#Function will sort data for Good/Bad defensive players from cutoff x
def dataSort(cutoff = -1):
    #stop if an invalid cutoff is provided
    if cutoff == -1:
        print("invalid cutoff")
    #go!
    else:
        #define counts for each cell of table
        goodPositive = 0
        badPositive = 0
        goodNegative = 0
        badNegative = 0
        #iterate over each row to assign players values
        for index, row in dataframe.iterrows():
            #define +/- (will be used to sort into negative / positive)
            onIceFor = dataframe.loc[index, 'OnIce_F_goals']
            onIceAgainst = dataframe.loc[index, 'OnIce_A_goals']
            plusMinus = onIceFor - onIceAgainst
            #define NDS
            negativeDS = dataframe.loc[index, 'NDS']
            #sort based on these values
            if negativeDS >= cutoff and plusMinus >= 0:
                badPositive += 1
            elif negativeDS < cutoff and plusMinus >= 0:
                goodPositive += 1
            elif negativeDS >= cutoff and plusMinus < 0:
                badNegative += 1
            elif negativeDS < cutoff and plusMinus < 0:
                goodNegative += 1
            else:
                print("A row does not have a valid value needed to calculate.")
                break
        #return list of cells to use in calculation (think of this as the table spread out)
        cells = [goodPositive, badPositive, goodNegative, badNegative]
        return cells

#function to save data to spreadsheet based on significant cutoff
def saveFromCutoff(cutoff):
    #instantiate empty list
    classifications = []
    for index, row in dataframe.iterrows():
        #define +/- (will be used to sort into negative / positive)
        onIceFor = dataframe.loc[index, 'OnIce_F_goals']
        onIceAgainst = dataframe.loc[index, 'OnIce_A_goals']
        plusMinus = onIceFor - onIceAgainst
        #define NDS (used to sort good/bad)
        negativeDS = dataframe.loc[index, 'NDS']
        #sort based on these values
        if negativeDS >= cutoff and plusMinus >= 0:
            classifications.append('badPositive')
        elif negativeDS < cutoff and plusMinus >= 0:
            classifications.append('goodPositive')
        elif negativeDS >= cutoff and plusMinus < 0:
            classifications.append('badNegative')
        elif negativeDS < cutoff and plusMinus < 0:
            classifications.append('goodNegative')
        else:
            print("A row does not have a valid value needed to define")
            break
    #add classification as new column in dataframe
    dataframe['classification (NDS cutoff ' + str(cutoff) + ')'] = classifications
    #save excel spreadsheet
    dataframe.to_excel("C:/Users/Spencer/Desktop/NHL_Contract_Data_Scraper/Data/complete_2023-03-03.xlsx")
    print("file updated with classifications")

#calculate p value from the 4 cellas
def calculateTestStat(cell1, cell2, cell3, cell4):
    #define terms needed for test
    proportionGoodPositive = cell1/(cell1+cell2)
    proportionGoodNegative = cell3/(cell3+cell4)
    totalObs = cell1 + cell2 + cell3 + cell4
    #calculate pHat
    pHat = (cell1 + cell3)/totalObs
    #calculate SE(P) using pHat
    standardError = numpy.sqrt(pHat*(1-pHat)*((1/(cell1+cell2)) + (1/(cell3+cell4))))
    #calculate test statistic (Z)
    testStat = (proportionGoodPositive - proportionGoodNegative)/standardError
    #calculate pValue from test statistic for two tailed test in difference
    pValue = dist.norm.cdf(testStat)
    prob = 1-pValue
    return prob
    
#find highest NDS
def findNDSRange():
    currentHigh = 0
    for index, row in dataframe.iterrows():
        if dataframe.loc[index, 'NDS'] > currentHigh:
            currentHigh = dataframe.loc[index, 'NDS']
    return currentHigh


#test all cutoffs within range
#find the range
cutoffRange = findNDSRange()
currentCutoff = 0.5
#instantiate significant cutoff list to add to
significantCutoffs = []
#iterate through all possible cutoffs
while currentCutoff < cutoffRange:
    #sort data with cutoff
    testData = dataSort(currentCutoff)
    #calculate p with cutoff
    probability = calculateTestStat(testData[0], testData[1], testData[2], testData[3])
    #if significant, append to list
    if probability < 0.05:
        significantCutoffs.append(currentCutoff)
        currentCutoff += 1
    #if not significant, move on
    else:
        currentCutoff += 1
print("the cutoffs with significant values are: " + str(significantCutoffs))

#show p for all cutoffs with significant differences
for cutoff in significantCutoffs:
    testData = dataSort(cutoff)
    print(testData)
    probability = calculateTestStat(testData[0], testData[1], testData[2], testData[3])
    print("the p value for the cutoff " + str(cutoff) + " was " + str(probability))

#use First Value with Significant Cutoff to save values
saveFromCutoff(significantCutoffs[0])