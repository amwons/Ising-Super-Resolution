# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 21:09:15 2018

@author: Stavros
"""

from numpy import save as npsave
from os import path, mkdir
from architectures import get_model, get_name
from calculators import round_loss, cont_loss
from metrics import get_metrics
from keras.callbacks import History, EarlyStopping

def create_directory(d):
    ## Create directory if it doesn't exist ##
    if not path.exists(d):
        mkdir(d)

class TrainerCritical():
    def __init__(self, args):
        self.args = args
        
        self.create_loss()
        self.create_callbacks()
        
        self.name = get_name([1, self.args.L, self.args.L, 1], 
                             hid_act=self.args.ACT,
                             hid_filters=self.args.HF, 
                             kernels=self.args.K,
                             pbc=self.args.PBC)
        
        self.create_saving_dirs()

    def create_loss(self):
        self.metrics_list = [round_loss, cont_loss, 'accuracy']
        if self.args.magR == 0 and self.args.enR == 0:
            self.reg_flag = False
            from calculators import create_loss
            def loss(self, y_true, y_pred):
                return create_loss(y_true, y_pred, ce=self.args.CE)
        else:
            self.reg_flag = True
            from calculators import create_loss_reg, regularization
            self.metrics_list.append(regularization)
            def loss(self, y_true, y_pred):
                return create_loss_reg(y_true, y_pred, ce=self.args.CE, 
                                       mag_reg=self.args.magR, en_reg=self.args.enR)
                
    def create_callbacks(self):
        self.callbacks = [History()]
        if self.args.ES:
            self.callbacks.append(EarlyStopping(monitor='loss', 
                                                min_delta=self.args.ESdelta, 
                                                patience=self.args.ESpat))
            self.args.EP = 1000
            
    def crete_saving_dirs(self):
        create_directory(self.args.metrics_dir)
        create_directory(self.args.model_dir)

    def train(self, data, run_time=0):
        self.crete_saving_dirs()
        
        self.model = get_model(data.train_in.shape, 
                               hid_act=self.args.ACT,
                               hid_filters=self.args.HF, 
                               kernels=self.args.K,
                               pbc=self.args.PBC)
        
        self.model.compile(optimizer=self.args.OPT, loss=self.loss, 
                           metrics=self.metrics_list)

        hist = self.model.fit(x=data.train_in[:self.args.TRS], 
                              y=data.train_out[:self.args.TRS],
                              batch_size=self.args.BS, epochs=self.args.EP, 
                              verbose=0, callbacks=self.callbacks, 
                              validation_data=(data.test_in[:self.args.VALS], 
                                               data.test_out[:self.args.VALS]))
        
        self.metrics = get_metrics(hist, reg=self.reg_flag)
        
        ### Save files ###
        npsave('%s/%s_B%d_Ver%dRun%d.npy'%(self.args.metrics_dir, self.name, 
                                           self.args.BS, self.args.VER, run_time))
        self.model.save('%s/%s_B%d_Ver%dRun%d.h5'%(self.args.model_dir, self.name,
                                                   self.args.BS, self.args.VER, run_time))

class TrainerTemp(TrainerCritical):
    def crete_saving_dirs(self):
        create_directory('%s/%s'%(self.args.metrics_dir, self.name))
        create_directory('%s/%s'%(self.args.model_dir, self.name))
    
    def train(self, data):
        for (iT,T) in enumerate(self.args.T_list):
            self.model = get_model(data.train_in.shape, 
                                   hid_act=self.args.ACT,
                                   hid_filters=self.args.HF, 
                                   kernels=self.args.K,
                                   pbc=self.args.PBC)
        
            self.model.compile(optimizer=self.args.OPT, loss=self.loss, 
                               metrics=self.metrics_list)
            
            hist = self.model.fit(
                    x=data.train_in[iT*self.args.nTR:(iT+1)*self.args.nTR][:self.args.TRS], 
                    y=data.train_out[iT*self.args.nTR:(iT+1)*self.args.nTR][:self.args.TRS],
                    batch_size=self.args.BS, epochs=self.args.EP, 
                    verbose=0, callbacks=self.callbacks, 
                    validation_data=(data.test_in[iT*self.args.nTE:(iT+1)*self.args.nTE][:self.args.VALS], 
                                     data.test_out[iT*self.args.nTE:(iT+1)*self.args.nTE][:self.args.VALS]))
        
            self.metrics = get_metrics(hist, reg=self.reg_flag)
            
            ### Save files ###
            npsave('%s/%s/Met%.4f.npy'%(self.args.metrics_dir, self.name, T))
            self.model.save('%s/%s/%Net%.4f.h5'%(self.args.model_dir, self.name, T))