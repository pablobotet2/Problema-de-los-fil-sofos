#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 10:14:47 2022

@author: alumno
"""

from multiprocessing import Process, \
  BoundedSemaphore, Semaphore, Lock, Condition,\
  current_process, \
  Value, Array, Manager
from time import sleep
from random import random

class Table:
    def __init__(self,size:int,manager):
        self.mutex=Lock()
        self.nphil=size
        self.phil = manager.list([False for _ in range(size)])
        self.freefork = Condition(self.mutex)
        self.neating=Value('i',0)
        self.nthinking=Value('i',size)
    
    def set_current_phil(self,num):
        self.current_phil=num
        
    def freeforknum(self):
        return not(max(self.phil[(self.current_phil-1)%self.nphil],self.phil[(self.current_phil+1)%self.nphil]))

    def wants_eat(self,num):
        self.mutex.acquire()
        self.freefork.wait_for(self.freeforknum)
        self.phil[num]=True
        self.neating.value+=1
        self.nthinking.value-=1
        self.mutex.release()
    
    def wants_think(self,num):
        self.mutex.acquire()
        self.phil[num]=False
        self.neating.value-=1
        self.nthinking.value+=1
        self.freefork.notify_all()
        self.mutex.release()    

class AnticheatTable:
    def __init__(self,size:int,manager):
        self.mutex=Lock()
        self.nphil=size
        self.phil = manager.list([False for _ in range(size)])
        self.hungry = manager.list([False for _ in range(size)])
        self.caneat = Condition(self.mutex)
        self.not_hungry_cond = Condition(self.mutex)
        self.neating=Value('i',0)
        self.nthinking=Value('i',size)
    
    def set_currentphil(self,num):
        self.current_phil=num
        
    def freeforknum(self):
        return not(max(self.phil[(self.current_phil-1)%self.nphil],self.phil[(self.current_phil+1)%self.nphil]))
    
    def not_hungry(self):
        return not(self.hungry[(self.current_phil-1)%self.nphil])
    
    def start_eating(self):
        return (self.freeforknum() and self.not_hungry())
    
    def wants_eat(self,num):
        self.mutex.acquire()
        
        self.not_hungry_cond.wait_for(self.not_hungry)
        self.hungry[num]=True
        self.caneat.wait_for(self.freeforknum)
        self.phil[num]=True
        self.hungry[num]=False
        self.neating.value+=1
        self.nthinking.value-=1
        self.not_hungry_cond.notify_all()
        self.mutex.release()
    
    def wants_think(self,num):
        self.mutex.acquire()
        self.phil[num]=False
        self.neating.value-=1
        self.nthinking.value+=1
        self.caneat.notify_all()
        self.mutex.release() 

class CheatMonitor:
    def __init__(self):
        self.mutex=Lock()
        self.cheat0=Value('b',False)
        self.cheat2=Value('b',False)
        self.trampas=Condition(self.mutex)
    
    def cheating(self):
        return (self.cheat0.value and self.cheat2.value)
    
    def is_eating(self,num):
        self.mutex.acquire()
        if num==0:
            self.cheat0.value=True
        if num==2:
            self.cheat2.value=True
        self.trampas.notify_all()
        self.mutex.release()
    
    def wants_think(self,num):
        self.mutex.acquire()
        self.trampas.wait_for(self.cheating,0.5)
        if num ==0:
            self.cheat0.value=False
        if num==2:
            self.cheat2.value=False
        self.mutex.release()