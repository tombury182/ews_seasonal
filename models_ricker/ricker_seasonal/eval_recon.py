#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 11:47:31 2019

@author: tbury

Investigate eigenavlue reconstruction with stationary time series
See Williamson (2015) for technique to reconstruct Jacobian from time-series data

"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# Imoprt trajectoreis dataframe
df_traj = pd.read_csv('data_export/ews_stat_evaltest/traj.csv', index_col=['rb','rnb','Time'])
df_traj.rename(columns={'Non-breeding':'x', 'Breeding':'y'}, inplace=True)

rb_vals = df_traj.index.levels[0]
rnb_vals = df_traj.index.levels[1]

# Select time series to analyse
df_temp = df_traj.loc[(0,-1)]

# Visualise with plot
df_temp[['x','y']].plot()



# Define function to compute lag-1 autocovariance matrix
def autocov(df_in):
    '''
    Computes the autocovariance of two time-series
    Input:
        df_in: DataFrame with two columns indexed by time
    Ouptut:
        np.array of autocovariance matrix
    '''
    
    # Obtain column names of df_in
    col_names = df_in.columns
    
    # Create columns shifted forward by 1 to compute autocovariance
    df_in['xshift'] =  df_temp[col_names[0]].shift(1)
    df_in['yshift'] =  df_temp[col_names[1]].shift(1)

    # Compute components of autocovariance matrix
    x0x1 = df_in[[col_names[0],'xshift']].cov().iloc[0,1]
    x1y0 = df_in[[col_names[1],'xshift']].cov().iloc[0,1]
    x0y1 = df_in[[col_names[0],'yshift']].cov().iloc[0,1]
    y0y1 = df_in[[col_names[1],'yshift']].cov().iloc[0,1]

    # Assign to matrix
    acov = np.array([[x0x1,x1y0],[x0y1,y0y1]])
    
    return acov



# Function to output jacobian reconstruction from two time-series
    
def eval_recon(df_in):
    '''
    Constructs estimate of Jacobian matrix from stationary time-series data
    and outputs the eigenvalues
    Input:
        df_in: DataFrame with two columns indexed by time
    Output:
        np.array of of eigenvalues, np.array of evecs
    '''
    
    # Compute covariance matrix
    cov = np.array(df_in.cov())
    
    # Compute autocovariance matrix
    acov = autocov(df_in)
    
    # Estimate of Jacobian (formula in Williamson (2015))
    jac = np.matmul( acov, np.linalg.inv(cov))
    
    # Eigenvalues
    evals, evecs = np.linalg.eig(jac)
    
    return evals, evecs





# Initiate list for eval data
list_evals = []
# Compute eigenvalues for each set of r values
for rb in rb_vals:
    for rnb in rnb_vals:
        df_temp = df_traj.loc[(rb,rnb)]
        
        # If trajecotry is zero set evals to NA
        if df_temp.iloc[-1,0]==0:
            evals = np.array([np.nan,np.nan])
            vec1 = np.array([np.nan,np.nan])
            vec2 = np.array([np.nan,np.nan])
        else:
        # Compute evals and evecs
            evals, evecs = eval_recon(df_temp)
            vec1 = evecs[:,0]
            vec2 = evecs[:,1]
            
        # Choose evecs to lie in the half-plane x>0 (wlog)
        if vec1[0]<0:
            vec1 = -vec1
        if vec2[0]<0:
            vec2 = -vec2
            
        
        # Add data to a dictionary    
        dic_temp = {'rb':rb, 'rnb':rnb, 'eval1':evals[0], 'eval2':evals[1], 
                    'evec1_x':np.real(vec1[0]), 'evec1_y':np.real(vec1[1]),
                    'evec2_x':np.real(vec2[0]), 'evec2_y':np.real(vec2[1])}    
        # Append to list
        list_evals.append(dic_temp)


# Add to dataframe
df_evals = pd.DataFrame(list_evals).set_index(['rb','rnb'])

     


# Columns for real and imaginary parts   
df_evals['eval1_re'] = df_evals['eval1'].apply(lambda x: np.real(x))
df_evals['eval1_im'] = df_evals['eval1'].apply(lambda x: np.imag(x))
df_evals['eval2_re'] = df_evals['eval2'].apply(lambda x: np.real(x))
df_evals['eval2_im'] = df_evals['eval2'].apply(lambda x: np.imag(x))

# Compute absolute values of eigenvector components
df_evals['evec1_x_abs'] = df_evals['evec1_x'].apply(np.abs)
df_evals['evec1_y_abs'] = df_evals['evec1_y'].apply(np.abs)


# Heatmap of real part of eigenvalue


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


# Create grid for plot
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10,10));

# Eval1
df_plot = df_evals.reset_index().pivot(index='rb', columns='rnb', values='eval1_re').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[0,0], vmax=1,vmin=-1)
axes[0,0].set_title('Re$(\lambda_1)$')
axes[0,0].set_xlabel('$r_{nb}$')
axes[0,0].set_ylabel('$r_{b}$')

# Eval2
df_plot = df_evals.reset_index().pivot(index='rb', columns='rnb', values='eval2_re').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[0,1], vmax=1,vmin=-1)
axes[0,1].set_title('Re$(\lambda_2)$')
axes[0,1].set_xlabel('$r_{nb}$')
axes[0,1].set_ylabel('$r_{b}$')


# Evec1 in x direction
df_plot = df_evals.reset_index().pivot(index='rb', columns='rnb', values='evec1_x_abs').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[1,0],vmax=1,vmin=0)
axes[1,0].set_title('$v1x$')
axes[1,0].set_xlabel('$r_{nb}$')
axes[1,0].set_ylabel('$r_{b}$')


# Evec1 in y direction
df_plot = df_evals.reset_index().pivot(index='rb', columns='rnb', values='evec1_y_abs').iloc[::-1]
sns.heatmap(df_plot, cmap=cmap, ax=axes[1,1],vmax=1,vmin=0)
axes[1,1].set_title('$v1y$')
axes[1,1].set_xlabel('$r_{nb}$')
axes[1,1].set_ylabel('$r_{b}$')




