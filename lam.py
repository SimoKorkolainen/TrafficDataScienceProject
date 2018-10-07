# -*- coding: utf-8 -*-
"""

"""

import pandas as pd
import seaborn as sns
import math
lamfile='C:/Users/lulun/lam.csv'
lamHeader = ["id", "year", "day", "hour", "minute", "second","centisecond","length","lane","direction","class","speed","faulty","time", "interval", "start"]
#ajanjakso jolta tieto noudetaan
fromDay=1
fromYear=2017
toDay=2
toYear=2017
#alue
area="01" #uusimaa

def writeFile(area, sensor, year, day):
    address = "https://aineistot.liikennevirasto.fi/lam/rawdata/%d/%s/" % (year, area)
    fileName = "lamraw_%d_%d_%d.csv" % (sensor, year % 100, day)
    path = "".join((address, fileName))
    print("loading %s ..." % fileName)
    try:
        df = pd.read_csv(path, header = None, names = lamHeader, sep = ";")
        with open(lamfile, 'a') as f: #poista ei-validit jo täällä
            df.to_csv(f, header=False)
    except:
        print("    Tiedosto puuttuu: "+fileName)
    
def readFile():
    df = pd.read_csv(lamfile, names=lamHeader)
    return df

def dataTofile():
    for v in range(fromYear, toYear+1):#year
        x=1
        y=365
        if v==fromYear: x=fromDay
        if v==toYear: y=toDay
        for s in range(1, 1607): #sensor
            for d in range(x, y): #day
                writeFile(area, s, v, d)
                
def cleanData(df):
    df2=df.dropna()
    df3=df2.loc[df['faulty']==0] #validi havainto
    return df3

def main():
    #dataTofile()
    df=readFile()
    df2=cleanData(df)
    print(df2['speed'].max())
    print(df2[df2['speed']==df2['speed'].max()])
    print(df2['speed'].mean())
    data=df2.groupby(['speed','hour'])['speed'].count()
    print(data.to_string())
    
main()