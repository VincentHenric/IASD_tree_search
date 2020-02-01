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
import time

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
    
    def play(self, board):
        moves = board.possible_moves()
        if len(moves) == 0:
            return None
        i = np.random.randint(len(moves))
        return moves[i]
    
class FlatMonteCarloPolicy(Policy):
    def __init__(self, nb_playout, default_policy=randomPolicy(), c=0.4):
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
        play = Play(board=copy.deepcopy(board)) # create a fictitious game from the board state
        play.board.play_move(move)
        
        win_player = play.play(self.default_policy, copy.deepcopy(self.default_policy), interactive=False)
        win = max(win_player * board.current_player, 0)
       # print('end playout')
        
        return win
    

class UCBMonteCarloPolicy(Policy):
    def __init__(self, nb_playout, default_policy=randomPolicy(), c=0.4):
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
        play = Play(board=copy.deepcopy(board)) # create a fictitious game from the board state
        play.board.play_move(move)
        
        win_player = play.play(self.default_policy, copy.deepcopy(self.default_policy), interactive=False)
        win = max(win_player * board.current_player, 0)
       # print('end playout')
        
        return win



""" ===================================================================== """ 
 
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
    

class MCTS(Policy):
    def __init__(self, budget, default_policy):
        self.budget = budget
        self.default_policy = default_policy
        self.tree = Tree()
        
    def play(self, board):        
        t = 0
        self.tree.add_node(board.h)
        while t < self.budget:
            new_board, hstates = self.tree_policy(board)
            win_value, moves_playout = self.play_default_policy(new_board, board.current_player)
            self.back_up(win_value, hstates, moves_playout)
            t += 1
        possible_hmoves = [board.get_move_hash(move) for move in board.possible_moves()]
        # best_hmove = self.best_child(self.tree, board.h, possible_hmoves)
        best_hmove = self.tree.best_child(self.best_child_func, board.h, possible_hmoves)
        return self.get_next_move(board, best_hmove)
            
    def play_default_policy(self, board, player):
        play = Play(board=copy.deepcopy(board)) # create a fictitious game from the board state
        
        win_player = play.play(self.default_policy, copy.deepcopy(self.default_policy))
        win = win_player * player
        return max(0,win), play.history
    
    def get_next_move(self, board, best_hmove):
        possible_moves = board.possible_moves()
        for move in possible_moves:
            h = board.get_move_hash(move)
            if h==best_hmove:
                return move
    
    def tree_policy(tree, player, board):
        pass
    
    def back_up(self, win_value, hmoves, moves_playout):
        for hmove in hmoves:
            self.tree[hmove]['nb_win'] += win_value
            self.tree[hmove]['nb_played'] += 1
    
    def best_child_func(nb_win, nb_play, child_v):
        pass
    
class FlatMonteCarlo(MCTS):
    def __init__(self, budget, default_policy):
        super().__init__(budget, default_policy)
        self.tree = Tree() #nb win, nb plays
        
    def tree_policy(self, board):
        # we try all nodes the same nb of times
        # returns the new board as we descend the tree, and updates the tree 
        hstates = [board.h]
        board = copy.deepcopy(board)
        
        possible_moves = board.possible_moves()
        k = np.random.randint(len(possible_moves))
        move = possible_moves[k]
        
        hstate = board.get_move_hash(move)
        self.tree.add_node(hstate)
        hstates.append(hstate)
        board.play_move(move)
        return board, hstates
         
    def best_child_func(self, nb_win, nb_play, child_v):
        win,n = child_v['nb_win'], child_v['nb_played']
        if n == 0:
            return 0
        return win/n  
    

class UCBMonteCarlo(MCTS):
    def __init__(self, budget, default_policy, c=0.4):
        super().__init__(budget, default_policy)
        self.tree = Tree() #nb win, nb plays
        self.c = c
        
    def play(self, board):
        self.remaining_moves = board.possible_moves()       
        return super().play(board)
        
    def tree_policy(self, board):
        hstates = [board.h]
        board = copy.deepcopy(board)
        
        if len(self.remaining_moves) != 0:
            move = self.remaining_moves.pop()
        else:
            possible_moves = board.possible_moves()
            possible_hmoves = [board.get_move_hash(move) for move in possible_moves]
            hmove = self.tree.best_child(self.best_child_func, board.h, possible_hmoves)
            move = self.get_next_move(board, hmove)
        
        hstate = board.get_move_hash(move)
        self.tree.add_node(hstate)
        hstates.append(hstate)
        board.play_move(move)
        return board, hstates
         
    def best_child_func(self, nb_win, nb_play, child_v):
        win,n = child_v['nb_win'], child_v['nb_played']
        if n==0:
            return 0
        return win/n + self.c * np.sqrt(np.log(nb_play)/n) 
    

class UCTMonteCarlo(MCTS):
    def __init__(self, budget, default_policy, c=0.4):
        super().__init__(budget, default_policy)
        self.tree = Tree() #nb win, nb plays
        self.c = c
        
    def tree_policy(self, board):
        hmoves = [board.h]
        board = copy.deepcopy(board)
        
        self.remaining_moves = board.possible_moves()
        
        possible_moves = board.possible_moves()
        possible_hmoves = [board.get_move_hash(move) for move in possible_moves]
        unexplored_hmoves = list(set(possible_hmoves)-self.tree.tree.keys())
        
        while len(unexplored_hmoves) == 0 and not board.check_win():
            hmove = self.tree.best_child(self.best_child_func, board.h, possible_hmoves)
            move = self.get_next_move(board, hmove)
            
            hmoves.append(hmove)
            
            board.play_move(move)
            
            possible_moves = board.possible_moves()
            possible_hmoves = [board.get_move_hash(move) for move in possible_moves]
            unexplored_hmoves = list(set(possible_hmoves)-self.tree.tree.keys())
            
        if board.check_win():
            return board, hmoves
            
        if len(unexplored_hmoves) != 0:  
            k = np.random.randint(len(unexplored_hmoves))
            hmove = unexplored_hmoves[k]
            move = self.get_next_move(board, hmove)
                        
            self.tree.add_node(hmove)
            hmoves.append(hmove)
            board.play_move(move)
            
        return board, hmoves
         
    def best_child_func(self, nb_win, nb_play, child_v):
        win,n = child_v['nb_win'], child_v['nb_played']
        if n==0:
            return 0
        return win/n + self.c * np.sqrt(np.log(nb_play)/n) 
    
class UCTMonteCarlo2(MCTS):
    def __init__(self, budget, default_policy, c=0.4):
        super().__init__(budget, default_policy)
        self.tree = Tree() #nb win, nb plays
        self.c = c
        
    def play(self, board):        
        t = 0
        self.tree.add_node(board.h)
        while t < self.budget:
            new_board, tree_hstates, tree_moves = self.tree_policy(copy.deepcopy(board), [board.h],[])
            win_value, moves_playout = self.play_default_policy(new_board, board.current_player)
            self.back_up(win_value, tree_hstates, moves_playout)
            #self.back_up(win_value, board, tree_moves, tree_hstates, moves_playout)
            t += 1
        possible_hmoves = [board.get_move_hash(move) for move in board.possible_moves()]
        # best_hmove = self.best_child(self.tree, board.h, possible_hmoves)
        best_hmove = self.tree.best_child(self.best_child_func, board.h, possible_hmoves)
        return self.get_next_move(board, best_hmove)
        
    def tree_policy(self, board, hstates, moves):
        possible_moves = board.possible_moves()
        
        if board.check_win():
            return board, hstates, moves
        elif len(self.tree[board.h]['moves'])!=len(possible_moves):
            unexplored_moves = [move for move in possible_moves if move not in self.tree[board.h]['moves']]
            k = np.random.randint(len(unexplored_moves))
            move = unexplored_moves.pop(k)
            hmove = board.get_move_hash(move)
                        
            self.tree.add_node(hmove)
            self.tree[board.h]['moves'].append(move)
            
            hstates.append(hmove)
            moves.append(move)
            
            board.play_move(move)
            
            return board, hstates, moves
        else:
            possible_hmoves = [board.get_move_hash(move) for move in possible_moves]
            hmove = self.tree.best_child(self.best_child_func, board.h, possible_hmoves)
            move = self.get_next_move(board, hmove)
            
            hstates.append(hmove)
            moves.append(move)
            
            board.play_move(move)
            
            return self.tree_policy(board, hstates, moves)
         
    def best_child_func(self, nb_win, nb_play, child_v):
        win,n = child_v['nb_win'], child_v['nb_played']
        if n==0:
            return 0
        return win/n + self.c * np.sqrt(np.log(nb_play)/n) 


class UCTMonteCarlo3(MCTS):
    def __init__(self, budget, default_policy, c=0.4):
        super().__init__(budget, default_policy)
        self.tree = Tree2() #nb win, nb plays, moves map
        self.c = c
        
    def play(self, board):        
        t = 0
        self.tree.add_node(board.h)
        while t < self.budget:
            new_board, tree_hstates, tree_moves = self.tree_policy(copy.deepcopy(board), [board.h],[])
            win_value, moves_playout = self.play_default_policy(new_board, board.current_player)
            self.back_up(win_value, tree_hstates, tree_moves, moves_playout)
            t += 1
        best_move = self.tree.best_child(self.best_child_func, board.h)
        return best_move
        
    def tree_policy(self, board, hstates, moves):
        possible_moves = board.possible_moves()
        
        if board.check_win():
            return board, hstates, moves
        elif len(self.tree[board.h]['moves'].keys())!=len(possible_moves):
            unexplored_moves = [move for move in possible_moves if move not in self.tree[board.h]['moves'].keys()]
            k = np.random.randint(len(unexplored_moves))
            move = unexplored_moves.pop(k)
            hmove = board.get_move_hash(move)
                        
            self.tree.add_node(hmove)
            self.tree.add_son(board.h, move)
            
            hstates.append(hmove)
            moves.append(move)
            
            board.play_move(move)
            
            return board, hstates, moves
        else:
            move = self.tree.best_child(self.best_child_func, board.h)
            hmove = board.get_move_hash(move)
            
            hstates.append(hmove)
            moves.append(move)
            
            board.play_move(move)
            
            return self.tree_policy(board, hstates, moves)
        
    def back_up(self, win_value, hmoves, tree_moves, moves_playout):
        for i in range(len(hmoves)-1):
            hmove = hmoves[i]
            move = tree_moves[i]
            self.tree[hmove]['nb_win'] += win_value
            self.tree[hmove]['nb_played'] += 1
            self.tree[hmove]['moves'][move]['nb_win'] += win_value
            self.tree[hmove]['moves'][move]['nb_played'] += 1
            
        self.tree[hmoves[-1]]['nb_win'] += win_value
        self.tree[hmoves[-1]]['nb_played'] += 1
         
    def best_child_func(self, nb_win, nb_play, child_v):
        win,n = child_v['nb_win'], child_v['nb_played']
        if n==0:
            return 0
        return win/n + self.c * np.sqrt(np.log(nb_play)/n) 
    
    
class GraveMonteCarlo(MCTS):
    def __init__(self, budget, default_policy, c=0.4):
        super().__init__(budget, default_policy)
        self.tree = Tree() #nb win, nb plays
        self.c = c
        
    def play(self, board):        
        t = 0
        self.tree.add_node(board.h)
        while t < self.budget:
            new_board, tree_hstates, tree_moves = self.tree_policy(copy.deepcopy(board), [board.h],[])
            win_value, moves_playout = self.play_default_policy(new_board, board.current_player)
            self.back_up(win_value, tree_hstates, moves_playout)
            #self.back_up(win_value, board, tree_moves, tree_hstates, moves_playout)
            t += 1
        possible_hmoves = [board.get_move_hash(move) for move in board.possible_moves()]
        # best_hmove = self.best_child(self.tree, board.h, possible_hmoves)
        best_hmove = self.tree.best_child(self.best_child_func, board.h, possible_hmoves)
        return self.get_next_move(board, best_hmove)
        
    def tree_policy(self, board, hstates, moves):
        possible_moves = board.possible_moves()
        
        if board.check_win():
            return board, hstates, moves
        elif len(self.tree[board.h]['moves'])!=len(possible_moves):
            unexplored_moves = [move for move in possible_moves if move not in self.tree[board.h]['moves']]
            k = np.random.randint(len(unexplored_moves))
            move = unexplored_moves.pop(k)
            hmove = board.get_move_hash(move)
                        
            self.tree.add_node(hmove)
            self.tree[board.h]['moves'].append(move)
            
            hstates.append(hmove)
            moves.append(move)
            
            board.play_move(move)
            
            return board, hstates, moves
        else:
            possible_hmoves = [board.get_move_hash(move) for move in possible_moves]
            hmove = self.tree.best_child(self.best_child_func, board.h, possible_hmoves)
            move = self.get_next_move(board, hmove)
            
            hstates.append(hmove)
            moves.append(move)
            
            board.play_move(move)
            
            return self.tree_policy(board, hstates, moves)
            
    
    def back_up(self, win_value, board, tree_moves, tree_hmoves, moves_playout):
        playout_moves = moves_playout['moves']
        all_moves = tree_moves + playout_moves

        for t in range(tree_moves):
            hmove = tree_hmoves[t]
            
            #board.zobrist.move_hash()
            
            win, nb, direct_actions = self.tree[hmove]
            win = win + win_value
            nb = nb + 1
            
            for u in range(t+1,len(all_moves)):
                desc_move = all_moves[u]
                #desc_hmove = all_hmoves[u]
                a_win, a_nb = self.tree[hmove]['moves'][desc_move]
                a_win += win
                a_nb += 1
                self.tree[hmove]['moves'][desc_move] = a_win, a_nb
                
            self.tree[hmove] = (win, nb, )
         
    def best_child_func(self, nb_win, nb_play, child_v):
        win,n = child_v['nb_win'], child_v['nb_played']
        if n==0:
            return 0
        return win/n + self.c * np.sqrt(np.log(nb_play)/n) 
    
    
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
        #policy1 = FlatMonteCarloPolicy(100, randomPolicy())
        #policy1 = FlatMonteCarlo(100, randomPolicy())
        #policy1 = UCBMonteCarlo(100, randomPolicy())
        policy1 = UCTMonteCarlo3(100, randomPolicy())
        #policy1 = GraveMonteCarlo(100, randomPolicy())
        policy2 = randomPolicy()
        
        a = play.play(policy1, policy2, interactive=True, sleep=0.1)
        a
    
    if flag_series_games:
        #policy1 = randomPolicy()
        #policy1 = UCBMonteCarloPolicy(100, randomPolicy())
        #policy1 = FlatMonteCarlo(100, randomPolicy())
        policy1 = UCTMonteCarlo(100, randomPolicy())
        policy2 = randomPolicy()
        #policy2 = FlatMonteCarloPolicy(100, randomPolicy())
    
        plays = Plays(policy1, policy2, n=5, colors=['x', 'o'])
        plays.play(10, True)
        print(plays.get_results())

    
    