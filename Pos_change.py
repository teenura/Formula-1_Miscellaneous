# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 20:54:01 2022

@author: aruneet
"""


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt 
import numpy as np

result = pd.read_csv('results.csv')
stats = pd.read_csv('status.csv')
driver = pd.read_csv('drivers.csv')
races = pd.read_csv('races.csv')
const = pd.read_csv('constructors.csv')
driver_s = pd.read_csv('driver_standings.csv')
laps=pd.read_csv('lap_times.csv')

laps.dtypes
races.dtypes

df=laps.groupby(['raceId','driverId']).mean()
lap_list=df.index.tolist()

overtake=pd.DataFrame()



for (x,y) in lap_list:
    temp=laps[(laps['raceId']==x) & (laps['driverId']==y)].sort_values(by='lap').reset_index().drop(['index'],axis=1)
    prev_lap=temp['position'].iloc[:-1]
    a=pd.Series(temp['position'][0])
    prev_lap=a.append(prev_lap, ignore_index=True)
    temp['prev_pos']=prev_lap
    temp['diff_pos']=temp['position']-temp['prev_pos']
    overtake=overtake.append(temp)
    
overtake.dtypes
overtake['diff_pos']=overtake['diff_pos']*-1    
overtake=overtake.rename(columns={'diff_pos':'pos_change'})
overtake.to_csv('laps_overtake.csv')


    

