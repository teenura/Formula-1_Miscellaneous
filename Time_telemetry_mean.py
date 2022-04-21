# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 02:51:30 2022

@author: arune
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 14:16:29 2022

@author: arune
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt 
import numpy as np

circuits = pd.read_csv('circuits.csv')
constructorResults = pd.read_csv('constructor_results.csv')
constructors = pd.read_csv('constructors.csv')
constructorStandings = pd.read_csv('constructor_standings.csv')
drivers = pd.read_csv('drivers.csv')
driverStandings = pd.read_csv('driver_standings.csv')
lapTimes = pd.read_csv('lap_times.csv')
pitStops = pd.read_csv('pit_stops.csv')
qualifying = pd.read_csv('qualifying.csv')
races = pd.read_csv('races.csv', index_col='raceId')
results = pd.read_csv('results.csv')
seasons = pd.read_csv('seasons.csv')
status = pd.read_csv('status.csv')
yellow=pd.read_csv('safety_cars.csv')
red=pd.read_csv('red_flags.csv')
red=red[['Race','Lap','Round']]

yellow['year']=yellow['Race'].apply(lambda x: int(x.split(' ')[0]))
red['year']=red['Race'].apply(lambda x: int(x.split(' ')[0]))
races['raceKey'] = races['year']*100+races['round']
races=races.reset_index()

#Filter all race data yearly
YEAR=2021
races = races.query('year==@YEAR').sort_values('round').copy()
results = results[results.raceId.isin(races.raceId)].copy()
lapTimes = lapTimes[lapTimes.raceId.isin(races.raceId)].copy()
yellow1=yellow[yellow['year']==YEAR]
red1=red[red['year']==YEAR]
yellow1['raceKey']=yellow1['year']*100+yellow1['Round']
yellow1=yellow1.reset_index()
yellow1=yellow1.drop(['index'],axis=1)
yellow1=yellow1.astype({'Retreated':int})
red1['raceKey']=red1['year']*100+red1['Round']
red1=red1.reset_index().drop(['index'],axis=1)

lapTimes = lapTimes.merge(results[['raceId', 'driverId', 'positionOrder']], on=['raceId', 'driverId'])
lapTimes['seconds'] = lapTimes.pop('milliseconds') / 1000
lapTimes=lapTimes.merge(races[['raceId','raceKey']], how='left', on='raceId')

#Create a baseline using mean and median of cumulative lap times
#Compare with minimum cumulative times to see which is a better metric for baseline
#We find out that in 30% of laps median is lower than minimum cumulative lap times which should not be
#On the other hand we get almost 0% of laps where mean is lower than minimum

base=lapTimes[['raceKey','lap','seconds']].groupby(['raceKey','lap']).agg(Mean=('seconds', 'mean'), Median=('seconds', 'median')).reset_index()
base['cum_mean']=base[['raceKey', 'lap', 'Mean']].sort_values(by=['lap']).groupby(['raceKey'])['Mean'].cumsum()
base['cum_median']=base[['raceKey', 'lap', 'Median']].sort_values(by=['lap']).groupby(['raceKey'])['Median'].cumsum()
lapTimes['cum']=lapTimes[['raceKey','driverId','lap','seconds']].sort_values(by=['lap']).groupby(['raceKey','driverId'])['seconds'].cumsum()
pole=lapTimes[['raceKey','lap','cum']].groupby(['raceKey','lap']).min('cum').reset_index()
pole=pole.rename(columns={'cum':'min_cum'})
base=base.merge(pole, how='left', on=['raceKey','lap'])
base['diff_mean']=base['cum_mean']-base['min_cum']
base['diff_median']=base['cum_median']-base['min_cum']

lapTimes1=lapTimes.merge(base[['raceKey','lap','cum_mean']], how='left', on=['raceKey','lap'])
lapTimes1['delta_mean']=lapTimes1['cum_mean']-lapTimes1['cum']

lapTimes1=lapTimes1.merge(base[['raceKey','lap','cum_median']], how='left', on=['raceKey','lap'])
lapTimes1['delta_median']=lapTimes1['cum_median']-lapTimes1['cum']
hist1=lapTimes1['delta_mean'].hist(bins=10000)
hist2=lapTimes1['delta_median'].hist(bins=10000)

#Remove outliers from cumulative data
lapTimes1['delta_mean']=lapTimes1['delta_mean'].apply(lambda x: np.nan if (x>500 or x<-500) else x)
lapTimes1['delta_median']=lapTimes1['delta_median'].apply(lambda x: np.nan if (x>500 or x<-500) else x)
lapTimes1.to_csv('delta_nan_2021.csv')
lapTimes2=lapTimes1[['raceId', 'driverId', 'lap', 'position', 'positionOrder', 'raceKey',  'delta_mean', 'delta_median']]

#to highlight safety car and red flag, the laps where sfety car was introduced is assigned maximum value
#of the delta while others are given min value so that they can be highlighted in Tableau
max_delta=lapTimes2.groupby(['raceKey']).agg(Max=('delta_mean','max'),Min=('delta_mean','min')).reset_index()
lapTimes2=lapTimes2.merge(max_delta, how='left', on=['raceKey'])

lapRace=lapTimes2.groupby(['raceKey','lap']).count().reset_index()
lapRace['Safety']=np.nan
lapRace['Red_flag']=np.nan
lapRace=lapRace[['raceKey','lap','Safety','Red_flag']].copy()

for i in range(0,len(yellow1)):
    key=yellow1['raceKey'].iat[i]
    low=yellow1['Deployed'].iat[i]
    high=yellow1['Retreated'].iat[i]
    for j in range(low,high+1):
        k=lapRace[(lapRace['raceKey']==key) & (lapRace['lap']==j)].index.item()
        lapRace.at[k,'Safety']=1
    
for i in range(0,len(red1)):
    key=red1['raceKey'].iat[i]
    red2=red1['Lap'].iat[i]
    k=lapRace[(lapRace['raceKey']==key) & (lapRace['lap']==red2)].index.item()
    lapRace.at[k,'Red_flag']=1

lapTimes2=lapTimes2.merge(lapRace, how='left', on=['raceKey','lap'])
lapTimes2['Safety_max']=lapTimes2['Safety']*lapTimes2['Max']
lapTimes2['Safety_min']=lapTimes2['Safety']*lapTimes2['Min']

lapTimes2=lapTimes2.merge(lapRace[['raceKey', 'lap', 'Red_flag']], how='left', on=['raceKey','lap'])
lapTimes2['Red_flag_max']=lapTimes2['Red_flag']*lapTimes2['Max']
lapTimes2['Red_flag_min']=lapTimes2['Red_flag']*lapTimes2['Min']
lapTimes2.to_csv('delta_safetyred.csv')

