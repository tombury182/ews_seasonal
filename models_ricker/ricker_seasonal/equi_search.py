#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 17 18:12:16 2019

@author: Thomas Bury

Function to compute stable equilbria of seasonal Ricker model
(by running trajectories until they settle down)
"""


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



# Density dep. parameters
alpha_b = 0.01 # density dependent effects in breeding period
alpha_nb = 0.000672 # density dependent effects in non-breeding period



# Difference equation (no noise)
def de_fun(state, rb, rnb):
    '''
    Inputs:
        state: array of state variables [x,y]
        rb: breeding growth rate
        rnb: non-breeding growth rate
    Output:
        array for subsequent state
    '''        
    
    [x, y] = state   # x (y) population after breeding (non-breeding) period
    
    # Compute pop size after breeding period season t+1
    xnew = y * np.exp(rb - alpha_b * y )
    # Compute pop size after non-breeding period season t+1
    ynew =  xnew * np.exp(rnb - alpha_nb * xnew )
    # Ouput updated state        
    return np.array([xnew, ynew])




def find_equi(rb, rnb):
    '''
    Function to find the equilibrium of the system given the breeding
    and non-breeding growth rates.
    
    Inputs:
        rb: growth rate in the breeding period
        rng: growth rate in the non-breeding period
    
    Ouptut: One of
        array of equilibrium value
        string 'oscillations' if oscillations observed
    '''
    
    # Parameters
    s0 = [rb/alpha_b,rb/alpha_b] # Initial condition
    tmax = 2000     # Time steps to simulate
    eps = 0.1    # Error margin required for equilibria convergence
    
    # Set up
    tVals = np.arange(0,tmax+1,1)
    s = np.zeros([tmax+1,2])
    s[0] = s0
    
    # Run the system 
    for i in range(len(tVals)-1):
        s[i+1] = de_fun(s[i],rb,rnb)
        
    
    if abs(np.linalg.norm(s[-1]) - np.linalg.norm(s[-2])) < eps:
        if np.linalg.norm(s[-1]) < 0.01:
            out = ['Extinct']*2
        else:
            out = s[-1]
        return out
    
    elif abs(np.linalg.norm(s[-1]) - np.linalg.norm(s[-3])) < eps:
        return ['Period-2 oscillations']*2
    
    elif abs(np.linalg.norm(s[-1]) - np.linalg.norm(s[-5])) < eps:
        return ['Period-4 oscillations']*2

    else:
        return ['No convergence or oscillations higher than period 4']*2
    
    
# Find equilibrium values over a sweep of growth parameters
     
# Growth parameters
rbVals = np.arange(0,4.05,0.1).round(2)
rnbVals = np.arange(-3,0.05,0.1).round(2)



# Create a list to store values
list_temp = []

for rb in rbVals:
    for rnb in rnbVals:
        # Make a list 
        equi = find_equi(rb,rnb)
        list_temp.append([rb,rnb,equi[0],equi[1]])
    print('Complete for rb = %.2f' %rb)

# x: non-breeding pop size, y: breeding pop size
    
# Put into a DataFrame
df_equi = pd.DataFrame(list_temp, columns = ['rb','rnb','x','y']).round({'rb': 2, 'rnb': 2})


# Replace string entries with NaN
df_equi['x_num'] = pd.to_numeric(df_equi['x'], errors='coerce')
df_equi['y_num'] = pd.to_numeric(df_equi['y'], errors='coerce')


df_plot_x = df_equi.pivot(index='rb', columns='rnb', values='x_num').iloc[::-1]
df_plot_y = df_equi.pivot(index='rb', columns='rnb', values='y_num').iloc[::-1]




# Plot for breeding population
plt.figure(figsize=(3,3))
ax = plt.axes()
sns.heatmap(df_plot_x, cmap='RdYlGn', vmin=0, vmax=500, ax=ax, 
            xticklabels=8,
            yticklabels=8)
ax.set_title('Non-breedinge population: size')
plt.show()

# Plot for non-breeding population
plt.figure(figsize=(3,3))
ax = plt.axes()
sns.heatmap(df_plot_y, cmap='RdYlGn', vmin=0, ax=ax,
            xticklabels=8,
            yticklabels=8)
ax.set_title('Breeding population: size')
plt.show()



# Export as csv
df_equi.to_csv('data_export/equi_data/equi_data.csv')







