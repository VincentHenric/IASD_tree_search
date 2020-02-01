#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 12:46:11 2020

@author: henric
"""

import numpy as np
import time

import board_games

PLAYERS = [1, -1]

class Game_history:
    def __init__(self):
        self.history = {'moves':[], 'win':0}
        
    def update_move(self, move):
        self.history['moves'].append(move)
        
    def update_win(self, win):
        self.history['win'] = win
        
    def get_win(self):
        return self.history['win']

class Play:
    def __init__(self, n=5, colors=[1,-1], save=False, board=None):
        if board:
            self.board=board
        else:
            self.board = board_games.Board(n, colors)
        self.save = save
        self.history = Game_history()
    
    def player_play(self, policy, interactive=False):
        move = policy.play(self.board)
        if self.save:
            self.history.update_move(move)
        self.board.play_move(move, interactive)
        
    def play(self, policy1, policy2, interactive=False, sleep=1):
        while not self.board.check_win():
            current_player = self.board.current_player
            if current_player == 1:
                policy = policy1
            else:
                policy = policy2
            self.player_play(policy, interactive)
            
            if interactive:
                time.sleep(sleep)
        winning_player = self.board.next_player()
        if interactive:
            print('Player {} wins !'.format(self.board.colors[winning_player]))
        self.history.update_win(winning_player)
        return winning_player
    
class Plays:
    def __init__(self, policy1, policy2, n=5, colors=[1, -1]):
        self.n = n
        self.players = PLAYERS
        if isinstance(colors, dict):
            self.colors = colors
        else:
            colors = [str(c) for c in colors]
            self.colors = dict(zip(self.players, colors))
        self.policy1 = policy1
        self.policy2 = policy2
        self.histories = []
        
    def play(self, nb_games = 10, interactive = False):
        for k in range(nb_games):
            if interactive:
                print('Play Game {}'.format(k))
            play = Play(n=self.n, colors=self.colors, save=False)
            player = play.play(self.policy1, self.policy2, interactive=False)
            self.histories.append(play.history)
            if interactive:
                print('Player {} wins game {}'.format(self.colors[player], k))
            
    def get_results(self):
        unique, counts = np.unique([history.get_win() for history in self.histories], return_counts=True)
        win_stats = dict(zip(unique, counts))
        win_stats = {k:v/sum(win_stats.values()) for k,v in win_stats.items()}
        return win_stats