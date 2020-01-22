#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 14:19:57 2020

@author: henric
"""

import numpy as np
import itertools
import time
import operator
import copy
from collections import defaultdict
import random

PLAYERS = [1, -1]

class Board:
    def __init__(self, n, colors = [1, -1]):
        self.size = n
        self.players = PLAYERS
        self.empty = ''
        if isinstance(colors, dict):
            self.colors = colors
        else:
            colors = [str(c) for c in colors]
            self.colors = dict(zip(self.players, colors))
        self.col_to_player = {col:player for player,col in self.colors.items()}
        self.color_len = max([len(c) for c in self.colors.values()])
        
        self.board = np.zeros((n,n), dtype='<U{}'.format(self.color_len))
        self.initialize()
        
        #self.check_player_position(1)
        #self.check_player_position(-1)
    
    def initialize(self):
        self.board[:2,:]=self.colors[1]
        self.board[-2:,:]=self.colors[-1]
        
        self.zobrist = Zobrist_hash(self.size)
        self.h = self.zobrist.board_hash(self)
        
    def hash(self):
        return self.zobrist.board_hash(self)
    
    def get_move_hash(self, move, player):
        return self.zobrist.move_hash(self.h, move, player)
        
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
    
    def check_player_position(self, player):
        positions = []
        for i in range(len(self.board)):
            for j in range(len(self.board)):
                if self.board[i,j] == self.colors[player]:
                    positions.append((i,j))
        return positions
        
    def possible_moves(self, player):
        possibles_moves = []
        positions = self.check_player_position(player)
        
        for position in positions:
            possibles_moves += self.possible_move(position, player)
            
        return possibles_moves
    
    def check_move(self, i, j):
        return i>=0 and i<len(self.board) and j>=0 and j<len(self.board)
    
    def possible_move(self, position, player):
        i,j = position
        moves = []
        if self.check_move(i + player, j) and self.board[i + player, j] == self.empty:
            moves.append(((i,j),(i+player,j)))
            
        if self.check_move(i + player, j-1) and  self.board[i + player, j-1] != self.colors[player]:
            moves.append(((i,j),(i+player,j-1)))

        if self.check_move(i + player, j+1) and  self.board[i + player, j+1] != self.colors[player]:
            moves.append(((i,j),(i+player,j+1)))

        return moves
              
    def play_move(self, player, move, with_comment=False):
        if move is None:
            if with_comment:
                print('Player cannot play')
        else:
            init, target = move
            self.board[target] = self.board[init]
            self.board[init] = self.empty
            self.h = self.zobrist.move_hash(self.h, move, player)
            
            if with_comment:
                print('Player {} moves from {} to {}'.format(self.colors[player], init, target))
                print(self)
        return self
    
    def play_moves(self, player, moves, with_comment=False):
        board = copy.deepcopy(self)
        for move in moves:
            board.play_move(player, move, with_comment)
            player = - player
        return board
        
    def check_win(self):
        for player in self.players:
            if self.colors[player] in self.board[min(-player,0)]:
                return True
        return False
    
""" ===================================================================== """    
    
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
            self.board = Board(n, colors)
        self.current_player = -1 # player 1 starts; see function play
        self.save = save
        self.history = Game_history()
    
    def player_play(self, player, policy, interactive=False):
        move = policy.play(player, self.board)
        if self.save:
            self.history.update_move(move)
        self.board.play_move(player, move, interactive)
        
    def play(self, policy1, policy2, interactive=False, sleep=1):
        while not self.board.check_win():
            self.current_player = - self.current_player
            if self.current_player == 1:
                policy = policy1
            else:
                policy = policy2
            self.player_play(self.current_player, policy, interactive)
            
            if interactive:
                time.sleep(sleep)
        if interactive:
            print('Player {} wins !'.format(self.board.colors[self.current_player]))
        self.history.update_win(self.current_player)
        return self.current_player
    
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
    
""" ===================================================================== """ 
    
class Policy:
    def __init__(self):
        pass
    
    def play(board):
        """
        chooses the move and returns it
        """
        pass
    
class randomPolicy(Policy):
    def __init__(self):
        pass
    
    def play(self, player, board):
        moves = board.possible_moves(player)
        if len(moves) == 0:
            return None
        i = np.random.randint(len(moves))
        return moves[i]
    
class FlatMonteCarloPolicy(Policy):
    def __init__(self, nb_playout, default_policy=randomPolicy(), c=0.4):
        self.nb_playout = nb_playout
        self.default_policy = default_policy
        self.c = c
    
    def play(self, player, board):
        remaining_moves = itertools.cycle(board.possible_moves(player))
        stats = defaultdict(lambda: (0,0)) # key = the move; value = the statistics (nb wins, nb simu)
        t = 0
        
        while t<self.nb_playout:
            # tree policy

            move = next(remaining_moves)
            
            # playout
            win = self.playout(player, move, board) 
            
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
        
    def playout(self, player, move, board):
       # print('Start playout')
        play = Play(board=copy.deepcopy(board)) # create a fictitious game from the board state
        play.current_player= player
        play.board.play_move(player, move)
        
        win_player = play.play(self.default_policy, copy.deepcopy(self.default_policy), interactive=False)
        win = max(win_player * player, 0)
       # print('end playout')
        
        return win
    

class UCBMonteCarloPolicy(Policy):
    def __init__(self, nb_playout, default_policy=randomPolicy(), c=0.4):
        self.nb_playout = nb_playout
        self.default_policy = default_policy
        self.c = c
    
    def play(self, player, board):
        remaining_moves = board.possible_moves(player)
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
            win = self.playout(player, move, board) 
            
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
        
    def playout(self, player, move, board):
       # print('Start playout')
        play = Play(board=copy.deepcopy(board)) # create a fictitious game from the board state
        play.current_player= player
        play.board.play_move(player, move)
        
        win_player = play.play(self.default_policy, copy.deepcopy(self.default_policy), interactive=False)
        win = max(win_player * player, 0)
       # print('end playout')
        
        return win



""" ===================================================================== """ 
 
class Tree:
    def __init__(self, default_value):
        self.tree = dict()
        self.default_value = default_value
        
    def add_node(self, h):
        if h not in self.tree.keys():
            self.tree[h] = self.default_value
        
    def best_child(self, value_func):
        return max(self.tree.items(), key=lambda v: value_func(v[1]))[0] 
    
    def __getitem__(self, i):
        return self.tree[i]
    
    def __setitem__(self, k, v):
        self.tree[k] = v
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return str(self.tree)

class MCTS(Policy):
    def __init__(self, budget, default_policy):
        self.budget = budget
        self.default_policy = default_policy
        self.tree = Tree((0,0))
        
    def play(self, player, board):        
        t = 0
        while t < self.budget:
            new_board, hmoves = self.tree_policy(player, board)
            win_value, moves_playout = self.play_default_policy(new_board, player)
            self.back_up(win_value, hmoves)
            t += 1
        best_hmove = self.tree.best_child(self.best_child_func)
        return self.get_next_move(board, player, best_hmove)
            
    def play_default_policy(self, board, player):
        play = Play(board=copy.deepcopy(board)) # create a fictitious game from the board state
        
        win_player = play.play(self.default_policy, copy.deepcopy(self.default_policy))
        win = win_player * player
        return max(0,win), play.history
    
    def get_next_move(self, board, player, best_hmove):
        possible_moves = board.possible_moves(player)
        for move in possible_moves:
            h = board.get_move_hash(move, player)
            if h==best_hmove:
                return move
    
    def tree_policy(tree, player, board):
        pass
    
    def back_up(tree, win_value, moves):
        pass
    
    def best_child_func(value_func):
        pass
    
class FlatMonteCarlo(MCTS):
    def __init__(self, budget, default_policy):
        super().__init__(budget, default_policy)
        self.tree = Tree((0,0)) #nb win, nb plays
        
    def tree_policy(self, player, board):
        # we try all nodes the same nb of times
        # returns the new board as we descend the tree, and updates the tree 
        hmoves = []
        board = copy.deepcopy(board)
        
        possible_moves = board.possible_moves(player)
        k = np.random.randint(len(possible_moves))
        move = possible_moves[k]
        
        hmove = board.get_move_hash(move, player)
        self.tree.add_node(hmove)
        hmoves.append(hmove)
        board.play_move(player, move)
        return board, hmoves
    
    def back_up(self, win_value, hmoves):
        for hmove in hmoves:
            win, n = self.tree[hmove]
            win_value = win + win_value
            n = n + 1
            self.tree[hmove] = (win_value, n)
         
    def best_child_func(self, v):
        win,n = v
        return win/n  
    
    
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
                    


""" ===================================================================== """ 
  
if __name__ == '__main__':
    flag_simple_game = True
    flag_series_games = False
    
    #board =  Board(5, ['x', 'o'])
    #print(board)
    
    if flag_simple_game:
        play = Play(5, ['x', 'o'], True)
        
        #policy1 = randomPolicy()
        #policy1 = UCBMonteCarloPolicy(100, randomPolicy())
        policy1 = FlatMonteCarlo(100, randomPolicy())
        policy2 = randomPolicy()
        
        a = play.play(policy1, policy2, interactive=True, sleep=0.1)
        a
    
    if flag_series_games:
        #policy1 = randomPolicy()
        #policy1 = UCBMonteCarloPolicy(100, randomPolicy())
        policy2 = randomPolicy()
        #policy2 = FlatMonteCarloPolicy(100, randomPolicy())
    
        plays = Plays(policy1, policy2, n=5, colors=['x', 'o'])
        plays.play(30, True)
        print(plays.get_results())

    
    