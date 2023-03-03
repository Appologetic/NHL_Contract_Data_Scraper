import requests
import datetime
import os
import pandas as pd
from bs4 import BeautifulSoup

#change directory to where you'd like to download the file
os.chdir("C:/Users/Spencer/Desktop/NHL_Contract_Data_Scraper/Data")

#set file name to date downloaded
date = str(datetime.date.today())
filepath = date + ".csv"
#download the file
download = requests.get("https://moneypuck.com/moneypuck/playerData/seasonSummary/2022/regular/skaters.csv")
#add downloaded file to folder
with open (filepath, "wb") as statData:
    statData.write(download.content)

#clean data (somewhat) to only contain 5 on 5 data for dmen
stats = pd.read_csv(filepath)
#iterate through rows of downloaded csv
for index, row in stats.iterrows():
    if stats.loc[index, 'position'] != "D" or stats.loc[index, 'situation'] != "5on5":
        stats = stats.drop(index)


#request to contract data page
webPage = requests.get("https://www.hockey-reference.com/friv/current_nhl_salaries.cgi").text
soupified = BeautifulSoup(webPage, 'html.parser')
#find table on webpage
capTable = soupified.find('tbody')
#create dictionary of all contracts from table
playerNames = []
capHits = []
for tr in capTable.find_all('tr'):
    playerNames.append(tr.contents[0].text)
    capHits.append(tr.contents[3].text)

for player in playerNames:
    if ", " in player:
        splitUp = player.split(", ")
        rearranged = splitUp[1] + " " + splitUp[0]
        playerNames[playerNames.index(player)] = rearranged
contractDict = dict(zip(playerNames, capHits))

#add column to cleaned data
stats["cap hit"]='not available'
#iterate through rows of dataframe to find name in dictionary
noDataFound = []

for index, row in stats.iterrows():
    currentPlayer = stats.loc[index, 'name']
    if currentPlayer in contractDict:
        stats.at[index, "cap hit"] = contractDict[currentPlayer]
        print("cap hit added for " + currentPlayer)
    else:
        noDataFound.append(currentPlayer)
        stats = stats.drop(index)
print("could not find cap data for players: " + str(noDataFound))

#save complete data to excel
cleanedFilepath = "complete_"+ date + ".xlsx"
stats.to_excel(cleanedFilepath)