
import pandas as pd
import numpy as np

# summary file: amount of cars in speed classes (1-200 km/h) during one hour period
summaryFile='lam.csv'

# data fetched from this period
fromDay=1
fromYear=2017
toDay=1
toYear=2017

# max speed under 200
maxSpeed=200

# amount of sensors -in Uusimaa sensor ids between 1 and 1607
amountOfSensors=1606

# fetch data from liikennevirasto page
def writeFile(sensor, year, day):
    address = "https://aineistot.liikennevirasto.fi/lam/rawdata/%d/%s/" % (year, getAreaCode())
    fileName = "lamraw_%d_%d_%d.csv" % (sensor, year % 100, day)
    path = "".join((address, fileName))
    print("Loading %s ..." % fileName)
    try:
        #original lam file
        df = pd.read_csv(path, header = None, names = getLamHeader(), sep = ";")
        #cleaned data
        df2=cleanData(df)
        #print(df2['speed'].max())
        #summary data
        df3=createDataframeForDay(df2) 
        with open(summaryFile, 'a') as f:
            df3.to_csv(f)
    except: # all error cases 
        print("   Tiedostoa ei löydy: "+fileName) # only area 01's sensors
    
def getAreaCode():
    return "01" #Uusimaa

def getLamHeader():
    return ["id", "year", "day", "hour", "minute", "second","centisecond","length","lane","direction","class","speed","faulty","time", "interval", "start"]

def cleanData(df):
    df2=df.dropna()
    df3=df2.loc[df['faulty']==0] #valid observation
    return df3

# edit input & cleaned data to summary file format
def createDataframeForDay(df):
    counts = getAggregatesForDay(df)
    h = np.arange(24) # 0-23
    df2 = pd.DataFrame()
    df2['hour'] = h
    df2['day']=df['day'][0]
    df2['id']=df['id'][0]
    for i in range(0,maxSpeed): # indexes 0-199
        colName = 'velocity%d' % (i+1) # speed 1-200
        df2[colName] = counts[:, i] 
    #print(df2)
    return df2

# calculate amount of cars in speed classes
def getAggregatesForDay(df):
    counts = np.zeros((24, maxSpeed)) # 0-23, 0-199
    for h in range(0, 24): #0-23
        df2=df.loc[df['hour']==h]
        c = np.bincount(df2['speed'], minlength = maxSpeed) # 0-199
        c = c[: maxSpeed]
        counts[h, :] = c
    return counts
             
def main():
    dataTofile()
    df=readFile()
    print(df.head(20))
    print(df.tail(20))

# fetch data from certain period
def dataTofile():
    for v in range(fromYear, toYear+1):#year
        x=1
        y=365+1
        if v==fromYear: x=fromDay
        if v==toYear: y=toDay+1
        for s in range(1, amountOfSensors+1): #sensor
            for d in range(x, y): #day
                writeFile(s, v, d)
                
# read summary file
def readFile():
    df = pd.read_csv(summaryFile)
    return df
    
main()
