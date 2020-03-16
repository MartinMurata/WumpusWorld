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
        self.visited = set() #(coordinate:sensors) map of visited tiles (tuple:list)
        self.previousTile = (0,0) 
        self.currentTile = (0,0) # set initial tile
        self.prevFacing = Direction.RIGHT
        self.facing = Direction.RIGHT #set initial direction
        self.targetTile = (0,0) #tile you want to either move to, or shoot at, should always be adjacent to current square, initially same as origin
        self.findGoldState = True #1 of two stages agent can be in
        self.goHomeState = False #1 of two stages agent can be in
        self.shootWumpusState = False
        self.hasArrow = True
        self.wumpusDead = False
        self.possibleMapSize = [8,8] # change it to a list b/c tuple is immutable [col,row]
        self.startCount = 0
        self.backtrack = False

    def getAction( self, stench, breeze, glitter, bump, scream ):
        if self.currentTile == (0,0) and breeze:
            return Agent.Action.CLIMB
        self.updateWorld( stench, breeze, bump, scream )
        if self.findGoldState:
            # print("still finding gold")
            return self.findingGoldAction(glitter)
        if self.goHomeState:
            # print("already found the gold")
            return self.goHomeAction(stench, breeze, glitter, bump, scream)

    def findingGoldAction( self, glitter):
        if glitter:  
            # grab that big gold man 
            # print("!!!!!!!!!!!! FOUND THE GOLD !!!!!!!!!!!!")
            self.visited.add(self.currentTile)
            self.findGoldState = False
            self.goHomeState = True
            return Agent.Action.GRAB
            
        if self.currentTile != self.targetTile:
            # print("have to turn again")
            return self.moveToTargetTile()

        if self.shootWumpusState and self.hasArrow and not self.goHomeState:
            self.hasArrow = False
            self.shootWumpusState = False
            return Agent.Action.SHOOT
        
        self.setTargetTile()
        return self.moveToTargetTile()

    def goHomeAction(self, stench, breeze, glitter, bump, scream ):
        if self.currentTile == (0,0):
            # print("already get back home!")
            return Agent.Action.CLIMB
        if self.currentTile != self.targetTile:
            return self.moveToTargetTile()

        self.goHomeTile()
        return self.moveToTargetTile()

    def goHomeTile(self):
        scores = {}
        for tile in self.adjTiles():
            scores[tile] = 0
            if tile not in self.visited:
                scores[tile] += 50
            else:
                scores[tile] = max(tile[0],tile[1])
        sorted_scores = sorted(scores.items(), key=lambda item: item[1])
        # print(f'ADJ SCORES {sorted_scores}')
        # input()
        self.visited.remove(self.currentTile)
        if sorted_scores[0][1] == sorted_scores[1][1]:
            self.targetTile = sorted_scores[random.randint(0,1)][0]
        elif sorted_scores[0][1] == sorted_scores[1][1] and sorted_scores[0][1] == sorted_scores[2][1]:
            self.targetTile = sorted_scores[random.randint(0,2)][0]
        else:
            self.targetTile = sorted_scores[0][0]

    def setTargetTile(self): # set the next Target Tile
        # pick a random one that's not visited 
        if not self.backtrack:
            notVisitedAdj = [tile for tile in self.safeMap[self.currentTile] if tile not in self.visited]
            if len(notVisitedAdj) >= 1:
                #print(f"not visited list {notVisitedAdj}")
                self.targetTile =  notVisitedAdj[random.randrange(len(notVisitedAdj))]
            else: # if it's 0
                self.findGoldState = False
                self.goHomeState = True
        else:
            #print("BACKTRACK")
            # backtrack here
            self.targetTile = self.previousTile
            self.backtrack = False

    '''
    UpdateWorld Algorithm:
    Assumes the setTarget always chooses the adj tile with the SMALLEST score

    1. initialize current tile score to 0 if UNVISITED
    2. initialize UNVISITED adj tiles scores to 0 
    3. if current tile has breeze or stench, add 3 to all UNVISITED adj tiles 
        - penalizes adj tiles
    4. if current tile is UNVISTED and has no senses, subtract 10 from all UNVISITED adj tiles
        - reward adj tiles, SAFE tiles means surrounding tiles are not wumpus or pit 
    5. if current tile you VISITED before has no senses, subtract 1 from all UNVISITED adj tiles
        - after backtracking to a safe tile, reward adj tiles a little more, promotes exloring new paths
    6. if any adj tiles around you are VISITED, add 1  
        - penalize visited tiles a little, promotes exploration
    7. for any adj tile greater than a threshold, give up, go home instead. Helps avoid inifinite LOOPING 
        - if agent cannot find new path (stuck in a cycle), adj scores will keep increasing, if gets to certain level, just go home. 
    8. mark current tile as visited 
    9. whenever you're done visiting current tile, add 2
        - penalize visited tiles a little, promotes exploration
    '''
    def updateWorld(self, stench, breeze, bump, scream):


        if bump: #current tile is wall
            self.updateWalls()
            self.currentTile = self.previousTile
            self.face = self.prevFacing
            self.setTargetTile()
            return 

        if not stench and not breeze: # want to add to okMap
            for tile in self.adjTiles():
                self.safeMap[self.currentTile].add(tile)

        if breeze:
            self.backtrack = True


        if stench:
            self.shootWumpusState = True # shoot the wumpus
        
        if scream and stench and not breeze:
            self.wumpusDead = True
            # the one that we facing is now safe, add to okay graph
        

        self.visited.add(self.currentTile)
    

        # print()
        # print(f"safeMap {self.safeMap}")
        # print(f"visited set {self.visited}")
        # print()
        # input()


    def moveToTargetTile(self):
        '''update the face and current tile before moving forward'''
        if (self.targetTile[0] > self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
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

            elif self.facing == Direction.LEFT: 
                self.prevFacing = self.facing
                self.facing = Direction.UP
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] > self.currentTile[1]): 
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
                self.facing = Direction.RIGHT
                return Agent.Action.TURN_RIGHT


    def updateWalls(self):
        if self.facing == Direction.UP:
            self.possibleMapSize[1] = self.currentTile[1]
        elif self.facing == Direction.RIGHT:
            self.possibleMapSize[0] = self.currentTile[0]

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
