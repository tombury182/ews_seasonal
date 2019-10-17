#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 18:04:51 2019


Plot stationary EWS in (rb, rnb) of seasonal Ricker model

@author: ThomasMBury
"""



#------------------------
# Import modules
#–----------------------

# Default python modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
    

# Job number
jobnum = 523647
filepath = '../hagrid/ricker_seasonal_coe/stationary/output/job-'+str(jobnum)+'/'

# Import data
df_ews = pd.read_csv(filepath+'ews.csv', index_col='Variable')
# Import params
df_pars = pd.read_csv(filepath+'pars.txt', sep = ' ')
sigma = df_pars['sigma'].values[0]
a = df_pars['a'].values[0]



# Figure params
left = 0.125  # the left side of the subplots of the figure
right = 0.9   # the right side of the subplots of the figure
bottom = 0.1  # the bottom of the subplots of the figure
top = 0.9     # the top of the subplots of the figure
wspace = 0.1  # the amount of width reserved for space between subplots,
              # expressed as a fraction of the average axis width
hspace = 0.3  # the amount of height reserved for space between subplots,
              # expressed as a fraction of the average axis height
    
cmap = "coolwarm" # Colour map for heat plot
dpi = 400 
        
   

# Take range of df_ews for plotting
#df_ews = df_ews[(df_ews['rb']<2.31)]
 
        
#---------------------
# Breeding population plot
#------------------



# Create grid for plot
fig, axes = plt.subplots(nrows=4, ncols=2, sharex=True,figsize=(8,8))
fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top, wspace=wspace, hspace=hspace)
fig.suptitle('Breeding population')


    
## Equilibrium values from equi_search
#df_plot = df_equi.pivot(index='rb', columns='rnb', values='y_num').iloc[::-1]
#sns.heatmap(df_plot, cmap=sns.diverging_palette(145, 280, s=85, l=25, as_cmap=True), vmin=0, vmax=200, ax=axes[0,0])
#axes[0,0].set_title('Equilibrium')
#axes[0,0].set_xlabel('')
#axes[0,0].set_ylabel('$r_b$')


# Equilibrium values from smoothing of stochastic time-series
df_plot = df_ews.loc['Breeding'].reset_index().pivot(index='rb', columns='rnb', values='Smoothing').iloc[::-1]
sns.heatmap(df_plot, cmap=sns.diverging_palette(145, 280, s=85, l=25, as_cmap=True), vmin=0, vmax=200, ax=axes[0,0])
axes[0,0].set_title('Equilibrium')
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel('$r_b$')


# Variance
df_plot = df_ews.loc['Breeding'].reset_index().pivot(index='rb', columns='rnb', values='Variance').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, vmin=0, vmax=12, ax=axes[0,1])
axes[0,1].set_title('Variance')
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')
axes[0,1].get_yaxis().set_ticklabels([])

# Coefficient of variation
df_plot = df_ews.loc['Breeding'].reset_index().pivot(index='rb', columns='rnb', values='Coefficient of variation').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[1,0], vmax=0.1)
axes[1,0].set_title('C.V.')
axes[1,0].set_xlabel('')
axes[1,0].set_ylabel('$r_b$')


# Smax/Var
df_plot = df_ews.loc['Breeding'].reset_index().pivot(index='rb', columns='rnb', values='Smax/Var').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[1,1], vmax=0.2)
axes[1,1].set_title('Smax/Var')
axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')
axes[1,1].get_yaxis().set_ticklabels([])

# Lag-1 AC
df_plot = df_ews.loc['Breeding'].reset_index().pivot(index='rb', columns='rnb', values='Lag-1 AC').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[2,0])
axes[2,0].set_title('Lag-1 AC')
axes[2,0].set_xlabel('')
axes[2,0].set_ylabel('$r_b$')

# Lag-2 AC
df_plot = df_ews.loc['Breeding'].reset_index().pivot(index='rb', columns='rnb', values='Lag-2 AC').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[2,1])
axes[2,1].set_title('Lag-2 AC')
axes[2,1].set_xlabel('')
axes[2,1].set_ylabel('')
axes[2,1].get_yaxis().set_ticklabels([])


# Skewness
df_plot = df_ews.loc['Breeding'].reset_index().pivot(index='rb', columns='rnb', values='Skewness').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[3,0],vmin=-0.15, vmax=0.15)
axes[3,0].set_title('Skewness')
axes[3,0].set_xlabel('')
axes[3,0].set_ylabel('')

# Kurtosis
df_plot = df_ews.loc['Breeding'].reset_index().pivot(index='rb', columns='rnb', values='Kurtosis').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[3,1],vmin=-0.2,vmax=0.2)
axes[3,1].set_title('Kurtosis')
axes[3,1].set_xlabel('$r_{nb}$')
axes[3,1].set_ylabel('')
axes[3,1].get_yaxis().set_ticklabels([])


# Make frames for plot
for ax in axes.flatten(): 
    for _, spine in ax.spines.items():
        spine.set_visible(True)
    

# Export plot
#plt.savefig('../figures/stat_ews/breeding_a'+str(a)+'_sigma'+str(sigma)+'.png', dpi=dpi)

   
#------------------------------
# Non-breeding population plot
#--------------------------------



# Create grid for plot
fig, axes = plt.subplots(nrows=4, ncols=2, sharex=True, figsize=(8,8))
fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top, wspace=wspace, hspace=hspace)
fig.suptitle('Non-breeding population')


# Equilibrium values from smoothing of stochastic time-series
df_plot = df_ews.loc['Non-breeding'].reset_index().pivot(index='rb', columns='rnb', values='Smoothing').iloc[::-1]
sns.heatmap(df_plot, cmap=sns.diverging_palette(145, 280, s=85, l=25, as_cmap=True), vmin=0, vmax=500, ax=axes[0,0])
axes[0,0].set_title('Equilibrium')
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel('$r_b$')


# Variance
df_plot = df_ews.loc['Non-breeding'].reset_index().pivot(index='rb', columns='rnb', values='Variance').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, vmin=0, vmax=200, ax=axes[0,1])
axes[0,1].set_title('Variance')
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')
axes[0,1].get_yaxis().set_ticklabels([])


# Coefficient of variation
df_plot = df_ews.loc['Non-breeding'].reset_index().pivot(index='rb', columns='rnb', values='Coefficient of variation').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[1,0], vmax=0.4)
axes[1,0].set_title('C.V.')
axes[1,0].set_xlabel('')
axes[1,0].set_ylabel('$r_b$')


# Smax/Var
df_plot = df_ews.loc['Non-breeding'].reset_index().pivot(index='rb', columns='rnb', values='Smax/Var').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[1,1], vmax=0.4)
axes[1,1].set_title('Smax/Var')
axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')
axes[1,1].get_yaxis().set_ticklabels([])


# Lag-1 AC
df_plot = df_ews.loc['Non-breeding'].reset_index().pivot(index='rb', columns='rnb', values='Lag-1 AC').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[2,0])
axes[2,0].set_title('Lag-1 AC')
axes[2,0].set_xlabel('')
axes[2,0].set_ylabel('$r_b$')

# Lag-2 AC
df_plot = df_ews.loc['Non-breeding'].reset_index().pivot(index='rb', columns='rnb', values='Lag-2 AC').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[2,1])
axes[2,1].set_title('Lag-2 AC')
axes[2,1].set_xlabel('')
axes[2,1].set_ylabel('')
axes[2,1].get_yaxis().set_ticklabels([])


# Skewness
df_plot = df_ews.loc['Non-breeding'].reset_index().pivot(index='rb', columns='rnb', values='Skewness').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[3,0],vmin=-0.5, vmax=0.5)
axes[3,0].set_title('Skewness')
axes[3,0].set_xlabel('')
axes[3,0].set_ylabel('')

# Kurtosis
df_plot = df_ews.loc['Non-breeding'].reset_index().pivot(index='rb', columns='rnb', values='Kurtosis').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[3,1],vmin=-0.5,vmax=0.5)
axes[3,1].set_title('Kurtosis')
axes[3,1].set_xlabel('$r_{nb}$')
axes[3,1].set_ylabel('')
axes[3,1].get_yaxis().set_ticklabels([])


# Make frames for plot
for ax in axes.flatten(): 
    for _, spine in ax.spines.items():
        spine.set_visible(True)
    
# Export plot
#plt.savefig('../figures/stat_ews/nonbreeding_a'+str(a)+'_sigma'+str(sigma)+'.png', dpi=dpi)
       
     











