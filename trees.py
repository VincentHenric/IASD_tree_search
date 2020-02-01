#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 12:44:44 2020

@author: henric
"""

class Tree:
    def __init__(self):
        self.tree = dict()
        
    def add_node(self, h):
        if h not in self.tree.keys():
            self.tree[h] = {'nb_win':0, 'nb_played':0, 'moves':[]}
        
    def best_child(self, value_func, h, keys):
        tree = {k:v for k,v in self.tree.items() if k in keys}
        return max(tree.items(), key=lambda v: value_func(self.tree[h]['nb_win'], self.tree[h]['nb_played'], v[1]))[0] 
    
    def __getitem__(self, i):
        return self.tree[i]
    
    def __setitem__(self, k, v):
        self.tree[k] = v
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return str(self.tree)
    
    
    
class Tree2(Tree):
    def __init__(self):
        super().__init__()
        
    def add_node(self, h):
        if h not in self.tree.keys():
            self.tree[h] = {'nb_win':0, 'nb_played':0, 'moves':dict()}
            
    def add_son(self, h, move):
        self.tree[h]['moves'][move] = {'nb_win':0, 'nb_played':0}
        
    def best_child(self, value_func, h):
        return max(self.tree[h]['moves'].items(), key=lambda v: value_func(self.tree[h]['nb_win'], self.tree[h]['nb_played'], v[1]))[0]