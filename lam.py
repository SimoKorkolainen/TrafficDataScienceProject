
import pandas as pd
import math
import numpy as np

lamfile='lam.csv'
lamHeader = ["id", "year", "day", "hour", "minute", "second","centisecond","length","lane","direction","class","speed","faulty","time", "interval", "start"]

#ajanjakso jolta tieto noudetaan
fromDay=1
fromYear=2017
toDay=2
toYear=2017
#alue
area="01" #uusimaa
maxSpeed=200

def writeFile(area, sensor, year, day):
    address = "https://aineistot.liikennevirasto.fi/lam/rawdata/%d/%s/" % (year, area)
    fileName = "lamraw_%d_%d_%d.csv" % (sensor, year % 100, day)
    
    path = "".join((address, fileName))
    print(path)
    print("loading %s ..." % fileName)


    try:
        df = pd.read_csv(path, header = None, names = lamHeader, sep = ";")
        df2=cleanData(df)
        df3=createDataframeForDay(df2)
        df3.to_csv(lamfile)
    except:
        print("    Tiedosto puuttuu: "+fileName)
 

def createDataframeForDay(df):

    counts = getAggregatesForDay(df)

    h = np.arange(24)

    df3 = pd.DataFrame()

    df3['hour'] = h

    df3['id']=df['id'][0]

    for i in xrange(200):
        colName = 'velocity%d' % (i + 1)
        df3[colName] = counts[:, i]

    print(df3)
    return df3
    

def getAggregatesForDay(df):

    counts = np.zeros((24, 200))

    for h in range(0, 24):
        df2=df.loc[df['hour']==h]
        c = np.bincount(df2['speed'], minlength = 200)
        c = c[: 200]

        counts[h, :] = c

    return counts
        
            
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
    dataTofile()
    df=readFile()
    #print(df.head(20))
    #print(df.tail(20))
    #print(np.unique(df['day']))
    #print(df2['speed'].max())
    #print(df2[df2['speed']==df2['speed'].max()])
    #print(df2['speed'].mean())
    #data=df2.groupby(['speed','hour'])['speed'].count()
    #print(data.to_string())
    

    
main()
