# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================
from Agent import Agent
import random
from collections import defaultdict
from enum import Enum

class Direction(Enum):
    RIGHT = "R"
    LEFT = "L"
    UP = "U"
    DOWN = "D"

class MyAI ( Agent ):
    #=============================================================================
    #=============================================================================
    def __init__ ( self ):
        self.safeMap = defaultdict(set)
        self.visited = set() 
        self.moveStack = []
        self.previousTile = (0,0)
        self.currentTile = (0,0) 
        self.targetTile = (0,0) 
        self.facing = Direction.RIGHT 
        self.findGoldState = True 
        self.goHomeState = False 
        self.possibleMapSize = [8,8] 

    def getAction( self, stench, breeze, glitter, bump, scream ):

    def findingGoldAction( self, glitter):

    def goHomeAction(self, stench, breeze, glitter, bump, scream ):

    def setGoHomeTile(self):

    def setTargetTile(self): # set the next Target Tile

    def updateWorld(self, stench, breeze, bump, scream):

    def moveToTargetTile(self):
        '''update the face and current tile before moving forward'''
        if (self.targetTile[0] > self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
            if self.facing == Direction.RIGHT:
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD
            elif self.facing == Direction.DOWN:
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_LEFT
            elif self.facing == Direction.UP:
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_RIGHT
            elif self.facing == Direction.LEFT: 
                self.facing = Direction.UP
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] > self.currentTile[1]): 
            if self.facing == Direction.UP:
                self.previousTile = self.currentTile
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD
            elif self.facing == Direction.RIGHT:
                self.facing = Direction.UP
                return Agent.Action.TURN_LEFT
            elif self.facing == Direction.LEFT:
                self.facing = Direction.UP
                return Agent.Action.TURN_RIGHT
            elif self.facing == Direction.DOWN:
                # need to face left first
                self.facing = Direction.LEFT
                return Agent.Action.TURN_RIGHT
            
        elif (self.targetTile[0] < self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
            if self.facing == Direction.LEFT:
                self.previousTile = self.currentTile
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD
            elif self.facing == Direction.UP:
                self.facing = Direction.LEFT
                return Agent.Action.TURN_LEFT
            elif self.facing == Direction.DOWN:
                self.facing = Direction.LEFT
                return Agent.Action.TURN_RIGHT
            elif self.facing == Direction.RIGHT:
                self.facing = Direction.DOWN
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] < self.currentTile[1]):
            if self.facing == Direction.DOWN:
                self.previousTile = self.currentTile
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD
            elif self.facing == Direction.LEFT:
                self.facing = Direction.DOWN
                return Agent.Action.TURN_LEFT
            elif self.facing == Direction.RIGHT:
                self.facing = Direction.DOWN
                return Agent.Action.TURN_RIGHT
            elif self.facing == Direction.UP:
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_RIGHT


    def updateWalls(self):
        if self.facing == Direction.UP:
            self.possibleMapSize[1] = self.currentTile[1]
        elif self.facing == Direction.RIGHT:
            self.possibleMapSize[0] = self.currentTile[0]

    def adjTiles(self):
        adjT = []
        adjTiles=[
                (self.currentTile[0]+1,self.currentTile[1]), # right
                (self.currentTile[0],self.currentTile[1]+1), # up
                (self.currentTile[0],self.currentTile[1]-1), # down
                (self.currentTile[0]-1,self.currentTile[1])  # left
            ]
        for tile in adjTiles:
            if (0 <= tile[0] < self.possibleMapSize[0] and 0 <= tile[1] < self.possibleMapSize[1]):
                adjT.append(tile)
        return adjT
