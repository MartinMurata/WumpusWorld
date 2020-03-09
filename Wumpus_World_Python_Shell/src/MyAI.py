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
    STENCH = 1
    BREEZE = 2
    GLITTER = 3
    BUMP = 4
    SCREAM = 5
    SAFE = 6 # no pits or wumpus
    VISITED = 7
    MAYBE_WUMPUS = 8
    MAYBE_PITS = 9
    NO_WUMPUS = 10
    NO_PITS = 11

#printWord.printWorld("/home/hsuth/CS171/WumpusWorld/Wumpus_World_World_Generator/Worlds/world_0.txt")

class MyAI ( Agent ):
    #=============================================================================
    #=============================================================================
    def __init__ ( self ):
        self.knownWorld = defaultdict(set) #(coordinate:sensors) map of visited tiles (tuple:list)
        self.previousTile = (0,0) 
        self.heuristic = {} # for A*, after finding the gold
        self.currentTile = (0,0) # set initial tile
        self.facing = 'right' #set initial direction
        self.targetTile = (0,0) #tile you want to either move to, or shoot at, should always be adjacent to current square, initially same as origin
        self.findGoldState = True #1 of two stages agent can be in
        self.goHomeState = False #1 of two stages agent can be in
        self.possibleMapSize = [100000,100000] # change it to a list b/c tuple is immutable [col,row]

    #=============================================================================
    '''main interface for this class'''
    #=============================================================================
    def getAction( self, stench, breeze, glitter, bump, scream ):
        #self.updateWorld( stench, breeze, bump, scream )
        if self.findGoldState:
            return self.findingGoldAction(glitter)
        if self.goHomeState:
            return self.goHomeAction(stench, breeze, glitter, bump, scream)

    #=============================================================================
    '''main logic pertaining to getting to the gold.''' 
    #=============================================================================
    def findingGoldAction( self, glitter):
        if self.currentTile != self.targetTile:
            return self.moveToTargetTile()
        if glitter:  
            # grab that big gold man 
            print ("Found the Gold!")
            if self.currentTile in self.knownWorld:
                self.knownWorld[self.currentTile].add(Sensor.GLITTER)
            else:
                self.knownWorld[self.currentTile].add(Sensor.GLITTER)
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
        print("GOING HOME MAN")
        if self.currentTile == (0,0):
            print("already at home")
            return Agent.Action.CLIMB
        else:
            self.setlowestScoreTarget()
            return self.moveToTargetTile()

    #=============================================================================
    '''scores all adjacent tiles on cost and heuristic. Sets target tile to the adj
        tile with lowest score. used in A* search

        G(n) cost = prob of wumpus + prob of pit
        H(n) heuristic = min(x-coord,y-coord)
        F(n) score = cost + heuristic
    '''
    #=============================================================================  
    def allAdjSafe(self):
        for tile in self.adjTiles():
            if Sensor.SAFE not in self.knownWorld[tile]:
                return False
        return True

    def ifWumpusScoreSame(self):
        return all(i == list(self.possibleWumpus.values())[0] for i in list(self.possibleWumpus.values()))
    
    def ifPitsScoreSame(self):
        return all(i == list(self.possibleWumpus.values())[0] for i in list(self.possibleWumpus.values()))

    #=============================================================================
    '''randomly picks unvisited tile. If there is any intelligence in this AI, it should
        be done here.....since picking the next tile requires a smart noodle...
        THIS IS NOT MECHANICS, USE SMART AI ALGORITHM
        use the weights for the pits and wumpus you made 
        probs want to make the possibleWumpus/Pit map into a priority queue, most probable tile at the top
    '''
    #=============================================================================
    def setTargetTile(self): # set the next Target Tile
        #if the current tile has breeze or pit and there's no way to backtrack
        
        self.targetTile = self.adjTiles()[random.randrange(len(self.adjTiles()))]


        '''
        if self.allAdjSafe(): # if all adj tiles are safe
            for tile in self.adjTiles():
                # the safest tile and yet visited
                if (Sensor.BREEZE and Sensor.STENCH and Sensor.VISITED) not in self.knownWorld[tile]:
                    self.targetTile = tile
                    break
                
                # second safest and visited
                elif (Sensor.BREEZE and Sensor.STENCH) not in self.knownWorld[tile] and Sensor.VISITED in self.knownWorld[tile]:
                    self.targetTile = tile
                    break
                # randomly picked one
                else:
                    self.targetTile = self.adjTiles()[random.randrange(len(self.adjTiles()))]

        # if not all tiles are safe       
        else:
            for tile in self.adjTiles():
                # pick the one that's safe
                if (Sensor.SAFE) in self.knownWorld[tile] and (Sensor.BREEZE or Sensor.STENCH) in self.knownWorld[tile]:
                        self.targetTile = tile
                        break
                else:
                    self.targetTile = self.adjTiles()[random.randrange(len(self.adjTiles()))]
        '''

    

    #=============================================================================
    '''returns the action to move to next tile. Only turns in the left direction (can be optimized later).
        THIS IS MECHANICS, NOT AI ALGORITHM
    '''
    #=============================================================================
    def moveToTargetTile(self):
        '''update the face and current tile before turning'''
        
        print()
        print("the current tile is", self.currentTile)
        print("the target tile is ", self.targetTile)
        print()

        if (self.targetTile[0] > self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):

            print("the target is on the right")
            # if the target tile is on the right of the current tile
            if self.facing == "right":
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD

            elif self.facing == "down":
                self.facing = "right" 
                return Agent.Action.TURN_LEFT

            elif self.facing == "up":
                self.facing = "right"
                return Agent.Action.TURN_RIGHT

            elif self.facing == "left": # facing the opposite way
                # need to face up
                self.facing = "up"
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] > self.currentTile[1]): 
            # if the target tile is on the top of the current tile

            print("the target is on the top")
            if self.facing == "up":
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD

            elif self.facing == "right":
                self.facing = "up"
                return Agent.Action.TURN_LEFT

            elif self.facing == "left":
                self.facing = "up"
                return Agent.Action.TURN_RIGHT

            elif self.facing == "down":
                # need to face left first
                self.facing = "left"
                return Agent.Action.TURN_RIGHT
            
        elif (self.targetTile[0] < self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
            # if the target tile is on the left of the current tile

            print("the target is on the left")
            if self.facing == "left":
                self.currentTile = self.targetTile

                return Agent.Action.FORWARD
            elif self.facing == "up":
                self.facing = "left"
                return Agent.Action.TURN_LEFT

            elif self.facing == "down":
                self.facing = "left"
                return Agent.Action.TURN_RIGHT

            elif self.facing == "right":
                # neet to face right first
                self.facing = "down"
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] < self.currentTile[1]):
            # if the target tile is on the bottom of the current tile

            print("the target is on the bottom")

            if self.facing == "down":
                self.currentTile = self.targetTile
                return Agent.Action.FORWARD

            elif self.facing == "left":
                self.facing = "down"
                return Agent.Action.TURN_LEFT

            elif self.facing == "right":
                self.facing = "down"
                return Agent.Action.TURN_RIGHT

            elif self.facing == "up":
                # which way doesn't matter, either left, right
                self.facing = "right"
                return Agent.Action.TURN_RIGHT


    def updateWalls(self):
        if self.facing == "up":
            self.possibleMapSize[1] = self.currentTile[1]
            print("now knows the bound of the row: ", self.possibleMapSize[1])
            #self.currentTile[1] = self.currentTile[1]-1 # backtrack here
        elif self.facing == "right":
            self.possibleMapSize[0] = self.currentTile[0]
            print("now knows the bound of the col: ", self.possibleMapSize[0])
            #elf.currentTile[0] = self.currentTile[0] - 1
    
    #======================cl=======================================================
    ''' keeps track of everything agent has seen so far. Saves in a dictionary
        as key = coordinate and value = sense
        THIS IS MECHANICS, NOT AI ALGORITHM
    '''
    #=============================================================================
    def updateWorld( self, stench, breeze, bump, scream):
        if (not stench and not breeze):
            self.knownWorld[self.currentTile].add(Sensor.SAFE)
            for tile in self.adjTiles():
                self.knownWorld[tile].add(Sensor.SAFE)

        if Sensor.VISITED not in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].add(Sensor.VISITED)

        if stench:
            self.knownWorld[self.currentTile].add(Sensor.STENCH)
            for tile in self.adjTiles():
                if Sensor.SAFE not in self.knownWorld[tile]: # if the tile is not marked safe yet
                    self.knownWorld[tile].add(Sensor.MAYBE_WUMPUS) # possible wumpus

        if breeze:
            self.knownWorld[self.currentTile].add(Sensor.BREEZE)
            for tile in self.adjTiles():
                if Sensor.SAFE not in self.knownWorld[tile]:
                    self.knownWorld[tile].add(Sensor.MAYBE_PITS) # possible pits

        '''which is tile marked as the wall'''
        if bump: # tile you're on is a wall (not tile you tried to move to), or does bump mean 
            self.updateWalls()
            '''randomly pick one tile to go'''
            self.targetTile = self.adjTiles()[random.randrange(len(self.adjTiles()))]

        if not stench and Sensor.MAYBE_WUMPUS in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].discard(Sensor.MAYBE_WUMPUS)
            self.knownWorld[self.currentTile].add(Sensor.NO_WUMPUS)
            if not breeze:
                self.knownWorld[self.currentTile].add(Sensor.SAFE)
        
        if not breeze and Sensor.MAYBE_PITS in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].discard(Sensor.MAYBE_PITS)
            self.knownWorld[self.currentTile].add(Sensor.NO_PITS)
            if not stench:
                self.knownWorld[self.currentTile].add(Sensor.SAFE)

        # if there is no wumpus or pits
        self.knownWorld[self.currentTile].add(Sensor.SAFE)
        

        # update the whole world again (make sure everything is right here)
        for tile in self.knownWorld:
            if Sensor.BREEZE in self.knownWorld[tile] and Sensor.SAFE in self.knownWorld[tile]:
                self.knownWorld[tile].discard(Sensor.BREEZE)
            if Sensor.STENCH in self.knownWorld[tile] and Sensor.SAFE in self.knownWorld[tile]:
                self.knownWorld[tile].discard(Sensor.STENCH)
            if (Sensor.NO_WUMPUS or Sensor.MAYBE_WUMPUS) in self.knownWorld[tile] and Sensor.SAFE in self.knownWorld[tile]:
                self.knownWorld[tile].discard(Sensor.MAYBE_WUMPUS)
                self.knownWorld[tile].discard(Sensor.NO_WUMPUS)
            if (Sensor.MAYBE_PITS or Sensor.NO_PITS) in self.knownWorld[tile] and Sensor.SAFE in self.knownWorld[tile]:
                # safe == no pits and no wumpus
                self.knownWorld[tile].discard(Sensor.MAYBE_PITS)
                self.knownWorld[tile].discard(Sensor.NO_PITS)

        print(self.knownWorld)
        
        #print()
        #print("the world looks like, ", self.knownWorld)
        #print("the possible wumpus", self.possibleWumpus)
        #print("the possible pits", self.possiblePits)

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
            if tile[0] >= 0 and tile[1] >= 0 and tile[0] < self.possibleMapSize[0] and tile[1] < self.possibleMapSize[1]:
                adjT.append(tile)
  
        return adjT
    #=============================================================================
    ''' updates the weights of a tile if we think theres a wumpus there
    '''
    #=============================================================================


    #=============================================================================
    ''' updates the weights of a tile if we think theres a pit there
    '''
    #=============================================================================
