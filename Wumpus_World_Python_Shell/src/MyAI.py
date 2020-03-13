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
'''
OVERALL STRATEGY
- perform depth first search (basically unintelligently lol) until you grab the gold, use algorithm to get back and climb out of cave. 
ASSUMPTIONS:
- there is only one gold and one wumpus 
- notation for coordinates is (row,column)
QUESTIONS:    
- how does agent know its at the edge of the board? 
- does agent know size of the board?
BUGS:
- when setting the target tile, it only considers tiles you haven't visited yet, but what if you are surrounded by all visted tiles?
'''


import printWord
from Agent import Agent
import random
from collections import defaultdict
from enum import Enum

class Sensor(Enum):
    STENCH = "ST"
    BREEZE = "BR"
    GLITTER = "GL"
    BUMP = "BU"
    SCREAM = "SC"
    SAFE = "SA" # no pits or wumpus
    VISITED = "VI"
    MAYBE_WUMPUS = "MW"
    MAYBE_PITS = "MP"

class Direction(Enum):
    RIGHT = "R"
    LEFT = "L"
    UP = "U"
    DOWN = "D"

#printWord.printWorld("/home/hsuth/CS171/WumpusWorld/Wumpus_World_World_Generator/Worlds/world_0.txt")

class MyAI ( Agent ):
    #=============================================================================
    #=============================================================================
    def __init__ ( self ):
        self.visited = set() #(coordinate:sensors) map of visited tiles (tuple:list)
        self.previousTile = (0,0) 
        self.heuristic = {} # for A*, after finding the gold
        self.currentTile = (0,0) # set initial tile
        self.prevFacing = Direction.RIGHT
        self.facing = Direction.RIGHT #set initial direction
        self.targetTile = (0,0) #tile you want to either move to, or shoot at, should always be adjacent to current square, initially same as origin
        self.findGoldState = True #1 of two stages agent can be in
        self.goHomeState = False #1 of two stages agent can be in
        self.possibleMapSize = [100000,100000] # change it to a list b/c tuple is immutable [col,row]

    #=============================================================================
    '''main interface for this class'''
    #=============================================================================
    def getAction( self, stench, breeze, glitter, bump, scream ):
        self.updateWorld( stench, breeze, bump, scream )
        if self.findGoldState:
            print("still finding gold")
            return self.findingGoldAction(glitter)
        if self.goHomeState:
            print("already found the gold")
            return self.goHomeAction(stench, breeze, glitter, bump, scream)

    #=============================================================================
    '''main logic pertaining to getting to the gold.''' 
    #=============================================================================
    def findingGoldAction( self, glitter):
        if self.currentTile != self.targetTile:
            print("have to turn again")
            return self.moveToTargetTile()
        if glitter:  
            # grab that big gold man 
            print("!!!!!!!!!!!! FOUND THE GOLD !!!!!!!!!!!!")
            self.visited.add(self.currentTile)
            self.findGoldState = False
            self.goHomeState = True
            return Agent.Action.GRAB

        self.setTargetTile()
        return self.moveToTargetTile()

    #=============================================================================
    ''' main logic pertaining to climbing out of the cave after getting gold. 
        Uses algorithm to find best path out of cave based on known world 
        (dijkstras? A*? idk yet) 
        THIS IS NOT MECHANICS, USE SMART AI ALGORITHM
    '''
    #=============================================================================
    def goHomeAction(self, stench, breeze, glitter, bump, scream ):
        if self.currentTile == (0,0):
            print("already get back home!")
            return Agent.Action.CLIMB
        
        print()
        print("################ ON THE WAY HOME ###################")
        print("refer to the top map")
        print("the current tile is", self.currentTile)
        print("the target tile is", self.targetTile)
        print("the agent is facing", self.facing)
        print()
        print(self.visited)
        print("################ ON THE WAY HOME ###################")
        print()

        if self.currentTile != self.targetTile:
            return self.moveToTargetTile()

        self.goHomeTile()
        return self.moveToTargetTile()

    def goHomeTile(self):
        # going home 
        # on way home, follow visited tiles in direction that the max(x,y) is decreasing 
        # after you leave a tile, mark unvisited 
        scores = {}
        for tile in self.adjTiles():
            scores[tile] = 0
            if tile not in self.visited:
                scores[tile] += 10
            else:
                scores[tile] = max(tile[0],tile[1])
        sorted_scores = sorted(scores.items(), key=lambda item: item[1])
        # print(f'ADJ SCORES {sorted_scores}')
        # input()
        self.visited.remove(sorted_scores[0][0])
        self.targetTile = sorted_scores[0][0]


    #=============================================================================
    '''chooses the adj tile with lowest score
    '''
    #=============================================================================
    def setTargetTile(self): # set the next Target Tile
        scores = {}
        for tile in self.adjTiles():
            scores[tile] = self.heuristic[tile]
        sorted_scores = sorted(scores.items(), key=lambda item: item[1])
        # print(f'ADJ SCORES {sorted_scores}')
        # input()
        self.targetTile = sorted_scores[0][0]


#======================cl=======================================================
    ''' updates scores of current tile and adj tiles
    '''
    #=============================================================================
    def updateWorld(self, stench, breeze, bump, scream):
        '''which is tile marked as the wall'''
        # if there is no wumpus or pits (the agent didn't die)
        if bump: # tile you're on is a wall (not tile you tried to move to), or does bump mean 
            self.updateWalls()
            self.currentTile = self.previousTile
            self.face = self.prevFacing
            self.setTargetTile()
            return 

        #initialize current tile score to 0
        if self.currentTile not in self.heuristic:
            self.heuristic[self.currentTile] = 0

        # initialize adj tiles scores to 0
        for tile in self.adjTiles():
            if tile not in self.heuristic:
                self.heuristic[tile] = 0

        # whenever breeze or stench, add 3 to all UNVISITED adj tiles 
        if breeze:
            for tile in self.adjTiles():
                if tile not in self.visited:
                    self.heuristic[tile] += 4
        
        if stench:
            for tile in self.adjTiles():
                if tile not in self.visited:
                    self.heuristic[tile] += 5

        # whenever tile you havent visited before has no senses, subtract 3 from all UNVISITED adj tiles 
        if self.currentTile not in self.visited and not stench and not breeze:
            for tile in self.adjTiles():
                if tile not in self.visited:
                    self.heuristic[tile] -= 3

        # whenever tile you visited before has no senses, subtract 1 from all UNVISITED adj tiles 
        if self.currentTile in self.visited and not stench and not breeze:
            for tile in self.adjTiles():
                if tile not in self.visited:
                    self.heuristic[tile] -= 1

        # whenever tile you visited before has senses, add 1 to all UNVISITED adj tiles 
        if self.currentTile in self.visited and (stench or breeze):
            for tile in self.adjTiles():
                if tile not in self.visited:
                    self.heuristic[tile] += 1
                    
        # # if any adj tiles around you are visited, add 1
        # for tile in self.adjTiles():
        #     if tile in self.visited:
        #         self.heuristic[tile] += 2

        # if stuck in loop
        for tile in self.adjTiles():
            if self.heuristic[tile] > 20 and tile in self.visited:
                self.heuristic[tile] += 30

        # mark current tile as visited 
        self.visited.add(self.currentTile)
        # whenever you visit, add 2
        self.heuristic[self.currentTile] += 2


    def moveToTargetTile(self):
        '''update the face and current tile before turning'''

        if self.findGoldState:
            print()
            print("################ PREV MAP INFO ###################")
            print("refer to the top map")
            print("the current tile is", self.currentTile)
            print("the target tile is", self.targetTile)
            print("the agent is facing", self.facing)
            print()
            print(self.visited)
            print("################ PREV MAP INFO ###################")
            print()

        if (self.targetTile[0] > self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
            print("the target is on the right")
            # if the target tile is on the right of the current tile
            if self.facing == Direction.RIGHT:
                self.prevFacing = self.facing
                self.previousTile = self.currentTile
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD

            elif self.facing == Direction.DOWN:
                self.prevFacing = self.facing
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_LEFT

            elif self.facing == Direction.UP:
                self.prevFacing = self.facing
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_RIGHT

            elif self.facing == Direction.LEFT: # facing the opposite way
                # need to face up
                self.prevFacing = self.facing
                self.facing = Direction.UP
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] > self.currentTile[1]): 
            # if the target tile is on the top of the current tile
            print("the target is on the top")
            if self.facing == Direction.UP:
                self.prevFacing = self.facing
                self.previousTile = self.currentTile
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD

            elif self.facing == Direction.RIGHT:
                self.prevFacing = self.facing
                self.facing = Direction.UP
                return Agent.Action.TURN_LEFT

            elif self.facing == Direction.LEFT:
                self.prevFacing = self.facing
                self.facing = Direction.UP
                return Agent.Action.TURN_RIGHT

            elif self.facing == Direction.DOWN:
                self.prevFacing = self.facing
                # need to face left first
                self.facing = Direction.LEFT
                return Agent.Action.TURN_RIGHT
            
        elif (self.targetTile[0] < self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
            # if the target tile is on the left of the current tile
            print("the target is on the left")
            if self.facing == Direction.LEFT:
                self.prevFacing = self.facing
                self.previousTile = self.currentTile
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD

            elif self.facing == Direction.UP:
                self.prevFacing = self.facing
                self.facing = Direction.LEFT
                return Agent.Action.TURN_LEFT

            elif self.facing == Direction.DOWN:
                self.prevFacing = self.facing
                self.facing = Direction.LEFT
                return Agent.Action.TURN_RIGHT

            elif self.facing == Direction.RIGHT:
                self.prevFacing = self.facing
                # neet to face right first
                self.facing = Direction.DOWN
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] < self.currentTile[1]):
            # if the target tile is on the bottom of the current tile
            print("the target is on the bottom")
            if self.facing == Direction.DOWN:
                self.prevFacing = self.facing
                self.previousTile = self.currentTile
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD

            elif self.facing == Direction.LEFT:
                self.prevFacing = self.facing
                self.facing = Direction.DOWN
                return Agent.Action.TURN_LEFT

            elif self.facing == Direction.RIGHT:
                self.prevFacing = self.facing
                self.facing = Direction.DOWN
                return Agent.Action.TURN_RIGHT

            elif self.facing == Direction.UP:
                self.prevFacing = self.facing
                # which way doesn't matter, either left, right
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_RIGHT


    def updateWalls(self):
        if self.facing == Direction.UP:
            self.possibleMapSize[1] = self.currentTile[1]
            print()
            print("################BOUND###################")
            print("now knows the bound of the row: ", self.possibleMapSize[1])
            print("################BOUND###################")
            print()
            #self.currentTile[1] = self.currentTile[1]-1 # backtrack here
        elif self.facing == Direction.RIGHT:
            self.possibleMapSize[0] = self.currentTile[0]
            print()
            print("################ BOUND ###################")
            print("now knows the bound of the col: ", self.possibleMapSize[0])
            print("################ BOUND ###################")
            print()
            #elf.currentTile[0] = self.currentTile[0] - 1

    def adjTiles(self):
        '''return a list of adjTiles'''
        adjT = []
        adjTiles=[
                (self.currentTile[0]+1,self.currentTile[1]), # right
                (self.currentTile[0],self.currentTile[1]+1), # up
                (self.currentTile[0],self.currentTile[1]-1), # down
                (self.currentTile[0]-1,self.currentTile[1])  # left
            ]

        for tile in adjTiles: # if it's not in the map
            # possibleMapSize 
            if (0 <= tile[0] < self.possibleMapSize[0] and 0 <= tile[1] < self.possibleMapSize[1]):
                adjT.append(tile)

        return adjT
