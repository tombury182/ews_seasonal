#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 16:41:47 2018

@author: Thomas Bury

Simulate transient simulations of the seasonal Ricker with 
stochasticity from first principles undergoing the
Flip bifurcation as rb is increased.



"""

# import python libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy.stats import poisson
from scipy.stats import nbinom

# import ewstools
from ewstools import ewstools

# import cross correlation function
from cross_corr import cross_corr


#---------------------
# Directory for data output
#–----------------------

# Name of directory within data_export
dir_name = 'ricker_trans_rb'

if not os.path.exists('data_export/'+dir_name):
    os.makedirs('data_export/'+dir_name)


#--------------------------------
# Global parameters
#–-----------------------------


# Simulation parameters
dt = 1 # time-step (must be 1 since discrete-time system)
t0 = 0
tmax = 400
tburn = 100 # burn-in period
numSims = 1
seed = 0 # random number generation seed


# EWS parameters
dt2 = 1 # spacing between time-series for EWS computation
rw = 0.4 # rolling window
span = 0.5 # Lowess span
lags = [1,2,3] # autocorrelation lag times
ews = ['var','ac','sd','cv','skew','kurt','smax','aic','cf'] # EWS to compute
ham_length = 80 # number of data points in Hamming window
ham_offset = 0.5 # proportion of Hamming window to offset by upon each iteration
pspec_roll_offset = 20 # offset for rolling window when doing spectrum metrics


#----------------------------------
# Simulate many (transient) realisations
#----------------------------------



# Model parameters
    
#rb = 1     # Growth rate for breeding period
kb = 200    # Carrying capacity for breeding period
knb = 70   # Carrying capacity for non-breeding period
rnb = 0.1     # Growth rate for non-breeding period
a = 0.001     # Effect of non-breeding density on breeding output (COE)
sig1 = 0     # Noise amplitude in breeding dyanmics
sig2 = 0    # Noise amplitude in non-breeding dynamics
ke = 50     # Env noise parameter


# Bifurcation parameter
rbl = 1
rbh = 3.5
rbcrit = 2.85

# Function dynamic - outputs the subsequent state
# The model goes through a Poisson distibution to determine the next state


def de_fun(state, control, params, noise):
    '''
    Inputs:
        state: array of state variables [x,y]
        control: control parameter that is to be varied
        params: list of parameter values [kb, knb, rnb, a, eps1, eps2]
    Output:
        array for subsequent state
    '''
        
    
    [x, y] = state   # x (y) population after breeding (non-breeding) period
    [kb, knb, rnb, a] = params
    [eps1, eps2] = noise
    rb = control
    
    # Compute pop size after breeding period season t+1
    
    # Parameters for negative binomial distribution
    mu = y * np.exp((rb - a*x) * (1-y/kb))
    p = ke / (ke + mu)
    
    # Compute pop size
    xnew = nbinom.rvs(ke, p)
    # Compute pop size after non-breeding period season t+1
    
    ## Parameters for negative binomial distribution
    mu = xnew * np.exp(rnb * (1-xnew/knb))
    p = ke / (ke + mu)
    ynew = nbinom.rvs(ke, p)
    
    # Ouput updated state        
    return np.array([xnew, ynew])
    
# Parameter list
params = [kb, knb, rnb, a]
 

# Initialise arrays to store time-series data
t = np.arange(t0,tmax,dt)
s = np.zeros([len(t),2])
   
# Set bifurcation parameter b, that increases linearly in time from bl to bh
b = pd.Series(np.linspace(rbl,rbh,len(t)),index=t)
# Time at which bifurcation occurs
tcrit = b[b > rbcrit].index[1]


# Initial conditions
x0 = kb
y0 = x0 * np.exp(rnb * (1-x0/knb))
s0 = [x0, y0]


## Implement Euler Maryuyama for stocahstic simulation

# Set seed
np.random.seed(seed)

# Initialise a list to collect trajectories
list_traj_append = []

# loop over simulations
print('\nBegin simulations \n')
for j in range(numSims):
    
    
    # Create brownian increments (s.d. sigma*sqrt(dt) )
    dW_burn = np.random.normal(loc=0, scale=np.sqrt(dt), size = (int(tburn/dt),2))*np.array([sig1,sig2])
    dW = np.random.normal(loc=0, scale=np.sqrt(dt), size = (len(t),2))*np.array([sig1,sig2])
    
    # Run burn-in period on s0
    for i in range(int(tburn/dt)):
        s0 = de_fun(s0, rbl, params, dW_burn[i])
        
    # Initial condition post burn-in period
    s[0] = s0
    
    # Run simulation
    for i in range(len(t)-1):
        s[i+1] = de_fun(s[i], b.iloc[i], params, dW[i])
        # make sure that state variable remains >= 0 
        s[i+1] = [np.max([k,0]) for k in s[i+1]]
            
    # Store series data in a temporary DataFrame
    data = {'Realisation number': (j+1)*np.ones(len(t)),
                'Time': t,
                'x': s[:,0],
                'y': s[:,1]}
    df_temp = pd.DataFrame(data)
    # Append to list
    list_traj_append.append(df_temp)
    
    print('Simulation '+str(j+1)+' complete')

#  Concatenate DataFrame from each realisation
df_traj = pd.concat(list_traj_append)
df_traj.set_index(['Realisation number','Time'], inplace=True)






# ----------------------
# Execute ews_compute for each realisation
# ---------------------

# Filter time-series to have time-spacing dt2
df_traj_filt = df_traj.loc[::int(dt2/dt)]

# set up a list to store output dataframes from ews_compute- we will concatenate them at the end
appended_ews = []
appended_pspec = []
appended_ktau = []

# loop through realisation number
print('\nBegin EWS computation\n')
for i in range(numSims):
    # loop through variable
    for var in ['x','y']:
        
        ews_dic = ewstools.ews_compute(df_traj_filt.loc[i+1][var], 
                          roll_window = rw,
                          smooth='Lowess',
                          span=span,
                          lag_times = lags, 
                          ews = ews,
                          ham_length = ham_length,
                          ham_offset = ham_offset,
                          pspec_roll_offset = pspec_roll_offset,
                          upto=tcrit,
                          sweep=False)
        
        # The DataFrame of EWS
        df_ews_temp = ews_dic['EWS metrics']
        # The DataFrame of power spectra
        df_pspec_temp = ews_dic['Power spectrum']
        # The DataFrame of kendall tau values
        df_ktau_temp = ews_dic['Kendall tau']
        
        # Compute cross-correlation
        df_cross_corr = cross_corr(df_traj_filt.loc[i+1][['x','y']],
                                   roll_window = rw,
                                   span = span,
                                   upto=tcrit)
        series_cross_corr = df_cross_corr['EWS metrics']['Cross correlation']
        
        
        # Include a column in the DataFrames for realisation number and variable
        df_ews_temp['Realisation number'] = i+1
        df_ews_temp['Variable'] = var
        df_ews_temp['Cross correlation'] = series_cross_corr

        
        df_pspec_temp['Realisation number'] = i+1
        df_pspec_temp['Variable'] = var


        df_ktau_temp['Realisation number'] = i+1
        df_ktau_temp['Variable'] = var
        df_ktau_temp['Cross correlation'] = df_cross_corr['Kendall tau'].iloc[0,0]
                
        
        # Add DataFrames to list
        appended_ews.append(df_ews_temp)
        appended_pspec.append(df_pspec_temp)
        appended_ktau.append(df_ktau_temp)


        
    # Print status every realisation
    if np.remainder(i+1,1)==0:
        print('EWS for realisation '+str(i+1)+' complete')


# Concatenate EWS DataFrames. Index [Realisation number, Variable, Time]
df_ews = pd.concat(appended_ews).reset_index().set_index(['Realisation number','Variable','Time'])
# Concatenate power spectrum DataFrames. Index [Realisation number, Variable, Time, Frequency]
df_pspec = pd.concat(appended_pspec).reset_index().set_index(['Realisation number','Variable','Time','Frequency'])
# Concatenate kendall tau DataFrames. Index [Realisation number, Variable]
df_ktau = pd.concat(appended_ktau).reset_index().set_index(['Realisation number','Variable'])


## Compute ensemble statistics of EWS over all realisations (mean, pm1 s.d.)
#ews_names = ['Variance', 'Lag-1 AC', 'Lag-2 AC', 'Lag-4 AC', 'AIC fold', 'AIC hopf', 'AIC null', 'Coherence factor']

#df_ews_means = df_ews[ews_names].mean(level='Time')
#df_ews_deviations = df_ews[ews_names].std(level='Time')



#-------------------------
# Plots to visualise EWS
#-------------------------

# Realisation number to plot
plot_num = 1
var = 'x'
## Plot of trajectory, smoothing and EWS of var (x or y)
fig1, axes = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(6,6))
df_ews.loc[plot_num,var][['State variable','Smoothing']].plot(ax=axes[0],
          title='Early warning signals for a single realisation')
df_ews.loc[plot_num,var]['Variance'].plot(ax=axes[1],legend=True)
df_ews.loc[plot_num,var][['Lag-1 AC','Lag-2 AC','Lag-3 AC']].plot(ax=axes[1], secondary_y=True,legend=True)
df_ews.loc[plot_num,var]['Smax'].dropna().plot(ax=axes[2],legend=True)
df_ews.loc[plot_num,var]['Coherence factor'].dropna().plot(ax=axes[2], secondary_y=True, legend=True)
df_ews.loc[plot_num,var][['AIC fold','AIC hopf','AIC null']].plot(ax=axes[3],legend=True, marker='o')


## Define function to make grid plot for evolution of the power spectrum in time
def plot_pspec_grid(tVals, plot_num, var):
    
    g = sns.FacetGrid(df_pspec.loc[plot_num,var].loc[t_display].reset_index(), 
                  col='Time',
                  col_wrap=3,
                  sharey=False,
                  aspect=1.5,
                  height=1.8
                  )

    g.map(plt.plot, 'Frequency', 'Empirical', color='k', linewidth=2)
    g.map(plt.plot, 'Frequency', 'Fit fold', color='b', linestyle='dashed', linewidth=1)
    g.map(plt.plot, 'Frequency', 'Fit hopf', color='r', linestyle='dashed', linewidth=1)
    g.map(plt.plot, 'Frequency', 'Fit null', color='g', linestyle='dashed', linewidth=1)
    # Axes properties
    axes = g.axes
    # Set y labels
    for ax in axes[::3]:
        ax.set_ylabel('Power')
        # Set y limit as max power over all time
        for ax in axes:
            ax.set_ylim(top=1.05*max(df_pspec.loc[plot_num,var]['Empirical']), bottom=0)
       
    return g

#  Choose time values at which to display power spectrum
t_display = df_pspec.index.levels[2][::3].values

plot_pspec = plot_pspec_grid(t_display, plot_num, 'x')



#
## Box plot to visualise kendall tau values
#df_ktau[['Variance','Lag-1 AC','Lag-2 AC','Smax','Cross correlation']].boxplot()
#






#------------------------------------
## Export data 
#-----------------------------------

## Export power spectrum evolution (grid plot)
#plot_pspec.savefig('figures/pspec_evol.png', dpi=200)



## Export the first 5 realisations to see individual behaviour
# EWS DataFrame (includes trajectories)
df_ews.loc[:5].to_csv('data_export/'+dir_name+'/ews_singles.csv')
# Power spectrum DataFrame (only empirical values)
df_pspec.loc[:5,'Empirical'].dropna().to_csv('data_export/'+dir_name+'/pspecs.csv',
            header=True)


# Export kendall tau values
df_ktau.to_csv('data_export/'+dir_name+'/ktau.csv')


    






