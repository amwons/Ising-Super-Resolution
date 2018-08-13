# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 22:23:40 2018

@author: Stavros
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'font.size': 32})

from plot_directories import T_list1D as T_list
from plot_directories import quantities_dir1D
# Use this T_list when plot_directories module is not available
#T_list = np.linspace(0.01, 4.538, 32)


### !!! .NPY DESCRIPTION !!! ###
# obs = (32, 5, 12)
# ind1: temperatures
# ind2: [MC, RG, SR continuous, SR rounded, SR sampled]
# ind3: [Mag, En, Susc, specHeat, Mag2, Mag4, En2, tpf(L/2), 
#        tpf(L/4), S0, S1, S2]

# Load data (fix .npy directory here)
NAME = 'Simple1D32relu_L1_32_K53_PBC_MReg0.00EReg0.10B1000'
obs = np.load('%s/%s.npy'%(quantities_dir1D, NAME))

# Use rounding instead of sampling for the five lowest temperatures 
# to correct noise in susc and Cv
obs[:3, -1] = obs[:3, -2]

def plot_one(q=0, figsize=(8, 5), L=32):
    # q: which quantity to plot
    plt.figure(figsize=figsize)
    plt.plot(T_list, obs[:, 0, q], color='blue', label='%d MC'%L)
    plt.plot(T_list, obs[:, 1, q], '--', color='green', label='%d RG'%(L//2))
    plt.plot(T_list, obs[:, -1, q], 'x', color='red', label='%d SR'%L)
    
    plt.legend()
    
    plt.show()
    
def plot_four(figsize=(14, 8), L=32, linewidth=1.5, save=False):
    # plots the four plots (M, E, chi, Cv)
    plt.figure(figsize=figsize)
    ylab = ['$M$', '$E$', '$\chi $', '$C_V$']
    for q in range(4):
        plt.subplot(221 + q)
        plt.plot(T_list, obs[:, 0, q], color='blue', label='%d MC'%L,
                 linewidth=linewidth)
        plt.plot(T_list, obs[:, 1, q], '--', color='green', 
                 label='%d RG'%(L//2), linewidth=linewidth)
        
        plt.plot(T_list, obs[:, -1, q], '*', color='red', label='%d SR'%L)
        if q == 0:
            plt.legend()
        plt.xlabel('$T$')
        plt.ylabel(ylab[q])
    
    if save:
        plt.savefig('%s.pdf'%NAME)
    else:
        plt.show()