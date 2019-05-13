#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 17:46:28 2018

Generate a bifurcation diagram of a discrete system.
Model: Seasonal Ricker model with carry-over effects (COE)
Bifurcation parameter: kb

@author: Thomas Bury
"""


from pynamical import bifurcation_plot, simulate
import numpy as np
from numba import jit



# Model parameters
rb = 1     # Growth rate for breeding period
#kb = 200    # Carrying capacity for breeding period
knb = 70   # Carrying capacity for non-breeding period
rnb = 0.1     # Growth rate for non-breeding period
a = 0.001     # Effect of non-breeding density on breeding output (COE)

# Ricker model for population size after breeding season
@jit(nopython=True)
def ricker_b(x, kb):
    '''
    Annual iteration for population size after breeding season.
    Inputs:
        x - current population size after breeding season
        kb - carrying capacity for the breeding period
    Ouptut:
        population size after the following breeding season.
    '''
    
    # Compute population size after non-breeding season based on x
    y = x * np.exp(rnb * (1-x/knb) )
    
    # Compute population after breeding season
    xnew = y * np.exp((rb - a*x) * (1-y/kb) )
    
    # Output new population size
    return xnew


# Simulate to get bifurcation points
bif_data_x = simulate(model=ricker_b, num_gens=100, rate_min=0.1, rate_max=224, num_rates=1000, num_discard=100)



# Obtain population size after non-breeding season by direct map from X_{t+1} to Y_{t+1}
def x_to_y(x):
    return x * np.exp(rnb * (1-x/knb) )

# Compute bifurcation points for y by mapping from x
bif_data_y = x_to_y(bif_data_x)    


# Make plot of bifurcation
bifurcation_plot(bif_data_x, title='Ricker Bifurcation Diagram', xmin=0, xmax=224, ymin=0, ymax=200, save=False)
bifurcation_plot(bif_data_y, title='Ricker Bifurcation Diagram', xmin=0, xmax=224, ymin=0, ymax=200, save=False)


# Export bifurcation points
bif_data_x.to_csv('../data_export/bif_data/bif_kb_x.csv')
bif_data_y.to_csv('../data_export/bif_data/bif_kb_y.csv')





