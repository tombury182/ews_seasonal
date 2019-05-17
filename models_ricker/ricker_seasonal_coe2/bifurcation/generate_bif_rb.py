#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 17:46:28 2018

Generate a bifurcation diagram of a discrete system.
Model: Seasonal Ricker model with carry-over effects (COE) - no birth in non-breeding period

@author: Thomas Bury
"""


from pynamical import bifurcation_plot, simulate
import numpy as np
from numba import jit



# Model parameters (from Betini et al. (2013))
kb = 200    # Carrying capacity for breeding period
d2 = 0.001		# Death coefficient in non-breeding period
a = 0.001     # Effect of non-breeding density on breeding output (COE)

# Ricker model for population size after breeding season
@jit(nopython=True)
def ricker_b(x, rb):
    '''
    Annual iteration for population size after breeding season.
    Inputs:
        x - current population size after breeding season
        rb - growth rate during breeding season
    Ouptut:
        population size after the following breeding season.
    '''
    
    # Compute population size after non-breeding season based on x
    y = x * np.exp(-d2 * x )
    
    # Compute population after breeding season
    xnew = y * np.exp((rb - a*x) * (1-y/kb) )
    
    # Output new population size
    return xnew


# Simulate to get bifurcation points
bif_data_x = simulate(model=ricker_b, num_gens=100, rate_min=0.5, rate_max=5, num_rates=1000, num_discard=100)



# Obtain population size after non-breeding season by direct map from X_{t+1} to Y_{t+1}
def x_to_y(x):
    return x * np.exp(-d2 * x )

# Compute bifurcation points for y by mapping from x
bif_data_y = x_to_y(bif_data_x)    


# Make plot of bifurcation
bifurcation_plot(bif_data_x, title='Ricker Bifurcation Diagram', xmin=0, xmax=5, ymin=0, ymax=500, save=False)
bifurcation_plot(bif_data_y, title='Ricker Bifurcation Diagram', xmin=0, xmax=5, ymin=0, ymax=500, save=False)




## Export bifurcation points
#bif_data_x.to_csv('../data_export/bif_data/bif_rb_x.csv')
#bif_data_y.to_csv('../data_export/bif_data/bif_rb_y.csv')




