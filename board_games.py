#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 12:44:24 2020

@author: henric
"""

import numpy as np
import itertools
import copy
import random

PLAYERS = [1, -1]

class Board:
    def __init__(self, n, colors = [1, -1]):
        self.size = n
        
        # player and color configuration
        self.players_list = PLAYERS
        self.empty = ''
        if isinstance(colors, dict):
            self.colors = colors
        else:
            colors = [str(c) for c in colors]
            self.colors = dict(zip(self.players_list, colors))
        self.col_to_player = {col:player for player,col in self.colors.items()}
        self.color_len = max([len(c) for c in self.colors.values()])
        self.players = itertools.cycle(self.players_list)
        self.next_player()
        
        # initialize board
        self.board = np.zeros((n,n), dtype='<U{}'.format(self.color_len))
        self.board[:2,:]=self.colors[1]
        self.board[-2:,:]=self.colors[-1]
        
        # initialize hash
        self.zobrist = Zobrist_hash(self.size)
        self.h = self.hash()
        
    def hash(self):
        return self.zobrist.board_hash(self)
    
    def next_player(self):
        self.current_player = next(self.players)
        return self.current_player
    
    def get_move_hash(self, move):
        return self.zobrist.move_hash(self.h, move, self.current_player)
        
    def __getitem__(self, key):
        return self.board[key]
    
    def __setitem__(self, key, val):
        self.board[key] = val
    
    def __len__(self):
        return self.size
    
    def get(self, i, j):
        return self.board[i,j]
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        s = ''
        
        row = ' '*(self.color_len + 4)
        for j in range(self.size):
            col_nb = str(j)
            col_nb.ljust(self.color_len//2, ' ').rjust(self.color_len, ' ')
            row += col_nb + ' | '
        s += row + '\n'
            
        for i in range(0, self.size):
            row = ''
            row_nb = str(i)
            row_nb.ljust(self.color_len//2, ' ').rjust(self.color_len, ' ')
            row_nb += '  | '
            row += row_nb
             #row='| '
            for j in range(self.size):
                x = str(self[i,j])
                x = x.ljust(self.color_len//2, ' ').rjust(self.color_len, ' ')
                row += x + ' | '
            s += row + '\n'
        return s
    
    def _check_player_position(self, player):
        positions = []
        for i in range(len(self.board)):
            for j in range(len(self.board)):
                if self.board[i,j] == self.colors[player]:
                    positions.append((i,j))
        return positions
        
    def possible_moves(self):
        player = self.current_player
        possibles_moves = []
        positions = self._check_player_position(player)
        
        for position in positions:
            possibles_moves += self._possible_move(position, player)
            
        return possibles_moves
    
    def move_in_board(self, i, j):
        return i>=0 and i<len(self.board) and j>=0 and j<len(self.board)
    
    def _possible_move(self, position, player):
        i,j = position
        moves = []
        if self.move_in_board(i + player, j) and self.board[i + player, j] == self.empty:
            moves.append(((i,j),(i+player,j)))
            
        if self.move_in_board(i + player, j-1) and  self.board[i + player, j-1] != self.colors[player]:
            moves.append(((i,j),(i+player,j-1)))

        if self.move_in_board(i + player, j+1) and  self.board[i + player, j+1] != self.colors[player]:
            moves.append(((i,j),(i+player,j+1)))

        return moves
              
    def play_move(self, move, with_comment=False):
        player = self.current_player
        
        if move is None:
            if with_comment:
                print('Player {} cannot play'.format(self.colors[player]))
        else:
            init, target = move
            self.board[target] = self.board[init]
            self.board[init] = self.empty
            self.h = self.zobrist.move_hash(self.h, move, player)
            
            if with_comment:
                print('Player {} moves from {} to {}'.format(self.colors[player], init, target))
                print(self)
                
            # change current player
            self.next_player()
        return self
    
    def play_moves(self, moves, with_comment=False):
        board = copy.deepcopy(self)
        for move in moves:
            board.play_move(move, with_comment)
        return board
        
    def check_win(self):
        for player in self.players_list:
            if self.colors[player] in self.board[min(-player,0)]:
                return True
        return False
    
    
""" ===================================================================== """ 

class Zobrist_hash:
    def __init__(self, n=5):
        self.n = n
        self.pieces = {-1:0, 1:1}
        self.table = [[[random.getrandbits(64) for k in range(len(self.pieces))] for i in range(self.n)] for j in range(self.n)]
#        self.table = np.empty((n,n,2))
#        for i in range(self.n):
#            for j in range(self.n):
#                for k in self.pieces:
#                    self.table[i,j,k] = random.getrandbits(64)
        
    def board_hash(self, board):
        h = 0
        for i in range(len(board)):
            for j in range(len(board[0])):
                piece = board.col_to_player.get(board[i,j])
                if piece in self.pieces.keys():
                    h = h ^ self.table[i][j][self.pieces[piece]]
        return h
                
    def move_hash(self, h, move, player):
        (i1,j1), (i2,j2) = move
        return h ^ self.table[i1][j1][self.pieces[player]] ^ self.table[i2][j2][self.pieces[player]]
    
    
    
    
