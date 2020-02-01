#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 12:48:07 2020

@author: henric
"""

import numpy as np
import copy
import itertools
from collections import defaultdict
import operator

import games
import policies

class FlatMonteCarloPolicy(policies.Policy):
    def __init__(self, nb_playout, default_policy=policies.randomPolicy(), c=0.4):
        self.nb_playout = nb_playout
        self.default_policy = default_policy
        self.c = c
    
    def play(self, board):
        remaining_moves = itertools.cycle(board.possible_moves())
        stats = defaultdict(lambda: (0,0)) # key = the move; value = the statistics (nb wins, nb simu)
        t = 0
        
        while t<self.nb_playout:
            # tree policy

            move = next(remaining_moves)
            
            # playout
            win = self.playout(move, board) 
            
            # back up
            w,n = stats[move]
            stats[move] = (w+win, n+1)
            
            t+=1
            
        move = self.choose_move(stats)
        return move
    
    def choose_move(self, stats):
        wins = {k: w/n for k,(w,n) in stats.items()}
        move = max(wins.items(), key=operator.itemgetter(1))[0]
        return move
        
    def playout(self, move, board):
       # print('Start playout')
        play = games.Play(board=copy.deepcopy(board)) # create a fictitious game from the board state
        play.board.play_move(move)
        
        win_player = play.play(self.default_policy, copy.deepcopy(self.default_policy), interactive=False)
        win = max(win_player * board.current_player, 0)
       # print('end playout')
        
        return win
    

class UCBMonteCarloPolicy(policies.Policy):
    def __init__(self, nb_playout, default_policy=policies.randomPolicy(), c=0.4):
        self.nb_playout = nb_playout
        self.default_policy = default_policy
        self.c = c
    
    def play(self, board):
        remaining_moves = board.possible_moves()
        stats = defaultdict(lambda: (0,0)) # key = the move; value = the statistics (nb wins, nb simu)
        t = 0
        
        while t<self.nb_playout:
            # tree policy
            if remaining_moves != []:
                # we take randomly one move
                move = remaining_moves.pop(np.random.randint(len(remaining_moves)))
            else:
                move = self.choose_UTC_move(stats, t)
            
            # playout
            win = self.playout(move, board) 
            
            # back up
            w,n = stats[move]
            stats[move] = (w+win, n+1)
            
            t+=1
            
        move = self.choose_final_move(stats)
        return move
        
    
    def compute_UCTs(self, stats, t):
        return {k: w/n + self.c * np.sqrt(np.log(t)/n) for k,(w,n) in stats.items()}
    
    def choose_UTC_move(self, stats, t):
        uct = self.compute_UCTs(stats, t)
        move = max(uct.items(), key=operator.itemgetter(1))[0]
        return move
    
    def choose_final_move(self, stats):
        move = max(stats.items(), key=lambda x: x[1][1])[0]
        return move
        
    def playout(self, move, board):
       # print('Start playout')
        play = games.Play(board=copy.deepcopy(board)) # create a fictitious game from the board state
        play.board.play_move(move)
        
        win_player = play.play(self.default_policy, copy.deepcopy(self.default_policy), interactive=False)
        win = max(win_player * board.current_player, 0)
       # print('end playout')
        
        return win