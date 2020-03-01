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
from Agent import Agent
import random
class MyAI ( Agent ):
    #=============================================================================
    #=============================================================================
    def __init__ ( self ):
        self.knownWorld = {} #(coordinate:sensors) map of visited tiles
        self.possiblePits = {} #(coordinate:weight)
        self.possibleWumpus = {} #(coordinate:weight)
        self.heuristic = {} # for A* ?????
        self.currentTile = (1,1) #set initial tile
        self.facing = 'right' #set initial direction
        self.targetTile = None #ile you want to either move to, or shoot at, should always be adjacent to current square
        self.findGoldState = True #1 of two stages agent can be in
        self.goHomeState = False #1 of two stages agent can be in

    #=============================================================================
    '''main interfacefor this class'''
    #=============================================================================
    def getAction( self, stench, breeze, glitter, bump, scream ):
        if self.findGoldState:
            return self.findingGoldAction(stench, breeze, glitter, bump, scream)
        if self.goHomeState:
            return self.goHomeAction(stench, breeze, glitter, bump, scream)

    #=============================================================================
    '''main logic pertaining to getting to the gold.''' 
    #=============================================================================
    def findingGoldAction( self, stench, breeze, glitter, bump, scream ):
        if glitter:  
            # grab that big gold man 
            if self.currentTile in self.knownWorld:
                self.knownWorld[self.currentTile].append('glitter')
            else:
                self.knownWorld[self.currentTile] = ['glitter']
            self.findGoldState = False
            self.goHomeState = True
            self.updateWorld( stench, breeze, bump, scream )
            return Agent.Action.GRAB
        self.updateWorld( stench, breeze, bump, scream )
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
        if self.currentTile == (1,1):
            return Agent.Action.CLIMB
        else:
            pass
            #implement A*
            #calc cost+hearustic of adj tiles. the heuristic cost is just the max(x,y).
            #Cost is determined by distance, but more importantly, what kind of square it is.

    #=============================================================================
    '''randomly picks unvisited tile. If there is any intelligence in this AI, it should
        be done here.....since picking the next tile requires a smart noodle...
        THIS IS NOT MECHANICS, USE SMART AI ALGORITHM
        use the weights for the pits and wumpus you made 
        probs want to make the possibleWumpus/Pit map into a priority queue, most probable tile at the top
    '''
    #=============================================================================
    def setTargetTile(self):
        adjTiles=[
            (self.currentTile[0],self.currentTile[1]+1), #right
            (self.currentTile[0],self.currentTile[1]-1), #left
            (self.currentTile[0]+1,self.currentTile[1]), #above
            (self.currentTile[0]-1,self.currentTile[1])  #below
        ]
        while True:
            self.targetTile = adjTiles[ random.randrange ( len (adjTiles) ) ]
            if self.targetTile not in self.knownWorld: #might get stuck, what if all surroundings are visited 
                break

    #=============================================================================
    '''returns the action to move to next tile. Only turns in the left direction (can be optimized later).
        THIS IS MECHANICS, NOT AI ALGORITHM
    '''
    #=============================================================================
    def moveToTargetTile(self):
        # next tile is above
        if self.targetTile[0] > self.currentTile[0]:
            #face the correct way first 
            if self.facing != 'up':
                return Agent.Action.TURN_LEFT
            else:
                self.facing = 'up'
        # next tile is below
        if self.targetTile[0] < self.currentTile[0]:
            #face the correct way first 
            if self.facing != 'down':
                return Agent.Action.TURN_LEFT
            else:
                self.facing = 'down'
        # next tile is right 
        if self.targetTile[1] > self.currentTile[1]:
            #face the correct way first 
            if self.facing != 'right':
                return Agent.Action.TURN_LEFT
            else:
                self.facing = 'right'
        # next tile is left
        if self.targetTile[1] < self.currentTile[1]:
            #face the correct way first 
            if self.facing != 'left':
                return Agent.Action.TURN_LEFT
            else:
                self.facing = 'left'
        self.currentTile = self.targetTile
        return Agent.Action.FORWARD

    #=============================================================================
    ''' keeps track of everything agent has seen so far. Saves in a dictionary
        as key = coordinate and value = sense
        THIS IS MECHANICS, NOT AI ALGORITHM
    '''
    #=============================================================================
    def updateWorld( self, stench, breeze, bump, scream) :
        if self.currentTile not in self.knownWorld:
            #initialize to empty list 
            self.knownWorld[self.currentTile] = []

        if stench and 'stench' not in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].append('stench')
            self.updateWumpusWeights()
        if breeze and 'breeze' not in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].append('breeze')
            self.updatePitWeights()
        if bump:
            #edge of map
            if self.targetTile:
                perimeterTile = self.targetTile #the previus targetTile is now known as perimeter
                self.knownWorld[perimeterTile].append('perimeter')
        if scream:
            # you killled the wumpus? 
            del self.possibleWumpus[self.targetTile] #target tile you shot at no longer a wumpus
            self.knownWorld[self.targetTile] = ['clear'] #target tile is now known, and clear. 
        if not (stench or breeze or bump) and 'clear' not in self.knownWorld[self.currentTile]:
            # nothing
            self.knownWorld[self.currentTile].append('clear')
            if self.currentTile in self.possiblePits:
                del self.possiblePits[self.currentTile]
            if self.currentTile in self.possibleWumpus.keys():
                del self.possibleWumpus

    #=============================================================================
    ''' updates the weights of a tile if we think theres a wumpus there
    '''
    #=============================================================================
    def updateWumpusWeights(self):
        adjTiles=[
            (self.currentTile[0],self.currentTile[1]+1), #right
            (self.currentTile[0],self.currentTile[1]-1), #left
            (self.currentTile[0]+1,self.currentTile[1]), #above
            (self.currentTile[0]-1,self.currentTile[1])  #below
        ]
        for tile in adjTiles:
            if tile not in self.knownWorld:
                if tile not in self.possibleWumpus.keys():
                    self.possibleWumpus[tile] = 1
                else:
                    self.possibleWumpus[tile]+=1

            
    #=============================================================================
    ''' updates the weights of a tile if we think theres a pit there
    '''
    #=============================================================================
    def updatePitWeights(self):
        adjTiles=[
            (self.currentTile[0],self.currentTile[1]+1), #right
            (self.currentTile[0],self.currentTile[1]-1), #left
            (self.currentTile[0]+1,self.currentTile[1]), #above
            (self.currentTile[0]-1,self.currentTile[1])  #below
        ]
        for tile in adjTiles:
            if tile not in self.knownWorld:
                if tile not in self.possiblePits:
                    self.possiblePits[tile] = 1
                else:
                    self.possiblePits[tile]+=1
