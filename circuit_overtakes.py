# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 01:10:04 2022

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
laps=pd.read_csv('laps_overtake.csv')
circuit=pd.read_csv('circuits.csv')

# master=pd.merge(laps, races[['raceId','year']], how='left', on='raceId')
# master=pd.merge(master, races[['raceId','circuitId']], how='left', on='raceId')
# master=master.drop(['Unnamed: 0'], axis=1)
# master['pos_change']=master['pos_change'].apply(lambda x:0 if x<0 else x)
# tot_overtakes=master.groupby(['raceId', 'driverId'], as_index=True)['pos_change'].sum()

# master.to_csv('laps_overtake.csv')
master=laps
m_overtake=master.groupby(['circuitId','raceId'])['pos_change'].sum().reset_index()
m_overtake1=m_overtake.groupby(['circuitId'])['raceId'].count().reset_index()
m_overtake2=m_overtake.groupby(['circuitId'])['pos_change'].sum().reset_index()
m_overtake2['tot_races']=m_overtake1['raceId']
m_overtake2['over_per_race']=m_overtake2['pos_change']/m_overtake1['raceId']
m_overtake2=m_overtake2.merge(circuit, how='left', on='circuitId')

m_overtake2.to_csv('Circuit_Overtakes.csv')
