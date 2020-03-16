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
        self.targetTile = (0,1) 
        self.facing = Direction.RIGHT 
        self.findGoldState = True 
        self.goHomeState = False 
        self.onGoldState = False
        self.isTurning = False
        self.possibleMapSize = [8,8] 

    def getAction( self, stench, breeze, glitter, bump, scream ):
        if not self.isTurning:
            self.updateWorld(stench, breeze, glitter, bump, scream)
        if self.onGoldState:
            self.onGoldState = False
            self.findGoldState = False
            self.goHomeState = True
            return Agent.Action.GRAB
        if self.findGoldState and not self.isTurning:
            self.setTargetTile()
        if self.goHomeState and not self.isTurning:
            self.setGoHomeTile()    
        return self.moveToTargetTile()

    def setGoHomeTile(self):
        if len(self.moveStack) > 0:
            self.targetTile = self.moveStack.pop()

    def setTargetTile(self):
        unvisitedAdjTiles = [tile for tile in self.safeMap[self.currentTile] if tile not in self.visited]
        if len(unvisitedAdjTiles) > 1:
            self.targetTile = unvisitedAdjTiles[random.randint(0,len(unvisitedAdjTiles)-1)]
        elif len(unvisitedAdjTiles) == 1:
            self.targetTile = unvisitedAdjTiles[0]
        elif len(self.moveStack) > 0:
            print('BACKTRACK')
            self.targetTile = self.moveStack.pop()
            print(f'new target: {self.targetTile}')
        else:
            self.goHomeState = True
            self.findGoldState = False
        print(f'visited tiles{self.visited}')
        print(f'UNVISITED ADJ TILES {unvisitedAdjTiles}')

    def updateWorld(self, stench, breeze, glitter, bump, scream):
        if glitter:
            self.handleGlitter()
            return
        if not breeze and not stench and not bump:
            self.addSafe()
        if breeze and self.currentTile == (0,0):
            self.onGoldState = False
            self.findGoldState = False
            self.goHomeState = True
            return
        if stench:
            self.handleStench()
        if bump:
            self.handleBump()
        if scream:
            self.handleScream()
        self.markVisited()
        
    def handleGlitter(self):
        self.onGoldState = True

    def handleStench(self):
        return Agent.Action.SHOOT

    def handleScream(self):
        self.addSafe()

    def markVisited(self):
        self.visited.add(self.currentTile)
        if self.currentTile not in self.moveStack:
            self.moveStack.append(self.currentTile)

    def addSafe(self):
        for tile in self.adjTiles():
            self.safeMap[self.currentTile].add(tile)

    def handleBump(self):
        if self.facing == Direction.UP:
            self.possibleMapSize[1] = self.currentTile[1]
        elif self.facing == Direction.RIGHT:
            self.possibleMapSize[0] = self.currentTile[0]
        # self.visited.remove(self.currentTile)
        self.currentTile = self.moveStack.pop()

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

    def moveToTargetTile(self): 
        if self.currentTile == (0,0) and self.goHomeState:
            return Agent.Action.CLIMB
        if (self.targetTile[0] > self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
            if self.facing == Direction.RIGHT:
                self.isTurning = False
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD
            elif self.facing == Direction.DOWN:
                self.isTurning = True
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_LEFT
            elif self.facing == Direction.UP:
                self.isTurning = True
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_RIGHT
            elif self.facing == Direction.LEFT:
                self.isTurning = True 
                self.facing = Direction.UP
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] > self.currentTile[1]): 
            if self.facing == Direction.UP:
                self.isTurning = False
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD
            elif self.facing == Direction.RIGHT:
                self.isTurning = True
                self.facing = Direction.UP
                return Agent.Action.TURN_LEFT
            elif self.facing == Direction.LEFT:
                self.isTurning = True
                self.facing = Direction.UP
                return Agent.Action.TURN_RIGHT
            elif self.facing == Direction.DOWN:
                self.isTurning = True
                # need to face left first
                self.facing = Direction.LEFT
                return Agent.Action.TURN_RIGHT
            
        elif (self.targetTile[0] < self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
            if self.facing == Direction.LEFT:
                self.isTurning = False
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD
            elif self.facing == Direction.UP:
                self.isTurning = True
                self.facing = Direction.LEFT
                return Agent.Action.TURN_LEFT
            elif self.facing == Direction.DOWN:
                self.isTurning = True
                self.facing = Direction.LEFT
                return Agent.Action.TURN_RIGHT
            elif self.facing == Direction.RIGHT:
                self.isTurning = True
                self.facing = Direction.DOWN
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] < self.currentTile[1]):
            if self.facing == Direction.DOWN:
                self.isTurning = False
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD
            elif self.facing == Direction.LEFT:
                self.isTurning = True
                self.facing = Direction.DOWN
                return Agent.Action.TURN_LEFT
            elif self.facing == Direction.RIGHT:
                self.isTurning = True
                self.facing = Direction.DOWN
                return Agent.Action.TURN_RIGHT
            elif self.facing == Direction.UP:
                self.isTurning = True
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_RIGHT