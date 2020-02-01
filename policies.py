#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 12:47:43 2020

@author: henric
"""

import numpy as np
import time
import copy
import time

import trees
import games

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
    
class MCTS(Policy):
    def __init__(self, budget, default_policy):
        self.budget = budget
        self.default_policy = default_policy
        self.tree = trees.Tree()
        
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
        play = games.Play(board=copy.deepcopy(board)) # create a fictitious game from the board state
        
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
        self.tree = trees.Tree() #nb win, nb plays
        
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
        self.tree = trees.Tree() #nb win, nb plays
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
        self.tree = trees.Tree() #nb win, nb plays
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
        self.tree = trees.Tree() #nb win, nb plays
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
        self.tree = trees.Tree2() #nb win, nb plays, moves map
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
        self.tree = trees.Tree() #nb win, nb plays
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
    
    
    
if __name__ == '__main__':
    flag_simple_game = True
    flag_series_games = False
    
    #board =  Board(5, ['x', 'o'])
    #print(board)
    
    if flag_simple_game:
        play = games.Play(5, ['x', 'o'], True)
        
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
    
        plays = games.Plays(policy1, policy2, n=5, colors=['x', 'o'])
        plays.play(10, True)
        print(plays.get_results())
