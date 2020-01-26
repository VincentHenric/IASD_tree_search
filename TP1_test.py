#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 14:20:08 2020

@author: henric
"""

import numpy as np
import copy
import TP1
import unittest

class TestMovesMethods(unittest.TestCase):
    def setUp(self):
        self.board = TP1.Board(n=5)
    
    
    def test_initial_nb_moves(self):
        self.assertEqual(len(self.board.possible_moves()), 13)
    
    
    def test_left_side_moves_1(self):
        self.assertEqual(len(self.board._possible_move((1,0), 1)), 2)
    
    def test_right_side_moves_1(self):
        self.assertEqual(len(self.board._possible_move((1,4), 1)), 2)
    
    def test_center_moves_1(self):
        self.assertEqual(len(self.board._possible_move((1,2), 1)), 3)
        
    def test_back_moves_1(self):
        self.assertEqual(len(self.board._possible_move((0,2), 1)), 0)
        

    def test_left_side_moves_2(self):
        self.assertEqual(len(self.board._possible_move((3,0), -1)), 2)
    
    def test_right_side_moves_2(self):
        self.assertEqual(len(self.board._possible_move((3,4), -1)), 2)
    
    def test_center_moves_2(self):
        self.assertEqual(len(self.board._possible_move((3,2), -1)), 3)
        
    def test_back_moves_2(self):
        self.assertEqual(len(self.board._possible_move((4,0), -1)), 0)
        

class TestMovesMethods2(unittest.TestCase):
    def setUp(self):
        self.board = TP1.Board(n=5)
        self.board.play_move(((1,1),(2,2)))
        
    def test_block_move1(self):
        self.assertEqual(len(self.board._possible_move((1,2), 1)), 2)
        
    def test_block_move2(self):
        self.assertEqual(len(self.board._possible_move((2,2), 1)), 2)
        
    def test_block_move3(self):
        self.assertEqual(len(self.board._possible_move((3,2), -1)), 2)


class TestZobristHash(unittest.TestCase):
    def setUp(self):
        self.board = TP1.Board(n=5)
        self.h = self.board.hash()
        
    def test_hash_move1(self):
        newboard = copy.deepcopy(self.board)
        move = ((1,1),(2,2))
        newboard.play_move(move)
        self.assertEqual(newboard.h, self.board.get_move_hash(move))
        
    def test_hash_move2(self):
        newboard = copy.deepcopy(self.board)
        move = ((1,1),(2,1))
        newboard.play_move(move)
        self.assertEqual(newboard.h, self.board.get_move_hash(move))
        

if __name__ == '__main__':
    unittest.main()