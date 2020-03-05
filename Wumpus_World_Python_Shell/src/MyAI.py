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
        self.knownWorld = {} #(coordinate:sensors) map of visited tiles (tuple:list)
        self.possiblePits = {} #(coordinate:weight) tuple:integer
        self.possibleWumpus = {} #(coordinate:weight)
        self.walls = {}
        self.heuristic = {} # for A* ?????
        self.currentTile = (0,0) # set initial tile
        self.facing = 'right' #set initial direction
        self.targetTile = (0,0) #tile you want to either move to, or shoot at, should always be adjacent to current square, initially same as origin
        self.findGoldState = True #1 of two stages agent can be in
        self.goHomeState = False #1 of two stages agent can be in

    #=============================================================================
    '''main interface for this class'''
    #=============================================================================
    def getAction( self, stench, breeze, glitter, bump, scream ):
        self.updateWorld( stench, breeze, bump, scream )
        if self.findGoldState:
            return self.findingGoldAction(glitter)
        if self.goHomeState:
            return self.goHomeAction(stench, breeze, glitter, bump, scream)

    #=============================================================================
    '''main logic pertaining to getting to the gold.''' 
    #=============================================================================
    def findingGoldAction( self, glitter):
        if glitter:  
            # grab that big gold man 
            print ("Find the Gold!")
            if self.currentTile in self.knownWorld:
                self.knownWorld[self.currentTile].append('glitter')
            else:
                self.knownWorld[self.currentTile] = ['glitter']
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
    def setlowestScoreTarget(self):
            minScore = 100000
            adjTiles=[
                (self.currentTile[0],self.currentTile[1]+1), #right
                (self.currentTile[0],self.currentTile[1]-1), #left
                (self.currentTile[0]+1,self.currentTile[1]), #above
                (self.currentTile[0]-1,self.currentTile[1])  #below
            ]
            tempScore = 0
            tempTile = None
            for tile in adjTiles:
                if tile[0] < 0 or tile[1] < 0:
                    continue
                if tile in self.possibleWumpus:
                    tempScore += self.possibleWumpus[tile]
                if tile in self.possiblePits:
                    tempScore += self.possiblePits[tile]
                if tile in self.knownWorld:
                    if 'wall' in self.knownWorld[tile]:
                        tempScore += 5
                # A* heuristic
                tempScore += max(tile[0],tile[1])

                # reset values if new min
                if tempScore < minScore:
                    minScore = tempScore
                    tempTile = tile
                tempScore = 0  
            self.targetTile = tempTile

    #=============================================================================
    '''randomly picks unvisited tile. If there is any intelligence in this AI, it should
        be done here.....since picking the next tile requires a smart noodle...
        THIS IS NOT MECHANICS, USE SMART AI ALGORITHM
        use the weights for the pits and wumpus you made 
        probs want to make the possibleWumpus/Pit map into a priority queue, most probable tile at the top
    '''
    #=============================================================================
    def setTargetTile(self): # set the next Target Tile
        print("the known world is", self.knownWorld)
        if self.currentTile == self.targetTile: #only set new target if we already moved to previous target
            minScore = 100000
            adjTiles=[
                (self.currentTile[0],self.currentTile[1]+1), # top
                (self.currentTile[0],self.currentTile[1]-1), # down
                (self.currentTile[0]+1,self.currentTile[1]), # right
                (self.currentTile[0]-1,self.currentTile[1])  # left
            ] # has to also check if all tiles wall
            tempScore = 0
            tempTile = None
            for tile in adjTiles:
                if tile[0] < 0 or tile[1] < 0:
                    print("the tile", tile, "is skipped")
                    continue
                if tile in self.possibleWumpus:
                    tempScore += self.possibleWumpus[tile]
                if tile in self.possiblePits:
                    tempScore += self.possiblePits[tile]
                if tile in self.walls:
                    tempScore += 5

                # reset values if new min
                if tempScore < minScore and tile not in self.knownWorld:
                    minScore = tempScore
                    tempTile = tile
                tempScore = 0  
            print('target is now ', tempTile)      
            self.targetTile = tempTile



    #=============================================================================
    '''returns the action to move to next tile. Only turns in the left direction (can be optimized later).
        -updates the current tile 
        THIS IS MECHANICS, NOT AI ALGORITHM
    '''
    #=============================================================================
    def moveToTargetTile(self):
        '''update the face and current tile before turning'''
        if (self.targetTile[0] > self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
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
            elif self.facing == "left":
                # which way doesn't matter, either left, right
                self.facing = "right"
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] > self.currentTile[1]): 
            # if the target tile is on the top of the current tile
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
                # which way doesn't matter, either left, right
                self.facing = "left"
                return Agent.Action.TURN_RIGHT
            
        elif (self.targetTile[0] < self.currentTile[0]) and (self.targetTile[1] == self.currentTile[1]):
            # if the target tile is on the left of the current tile
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
                # which way doesn't matter, either left, right
                self.facing = "left"
                return Agent.Action.TURN_RIGHT

        elif (self.targetTile[0] == self.currentTile[0]) and (self.targetTile[1] < self.currentTile[1]):
            # if the target tile is on the bottom of the current tile
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
                self.facing = "left"
                return Agent.Action.TURN_RIGHT

    #=============================================================================
    ''' keeps track of everything agent has seen so far. Saves in a dictionary
        as key = coordinate and value = sense
        THIS IS MECHANICS, NOT AI ALGORITHM
    '''
    #=============================================================================
    def updateWorld( self, stench, breeze, bump, scream) :
        print("the current tile before updating the world", self.currentTile)
        if self.currentTile not in self.knownWorld:
            #initialize to empty list 
            self.knownWorld[self.currentTile] = []

        if stench and 'stench' not in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].append('stench')
            self.updateWumpusWeights()
        if breeze and 'breeze' not in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].append('breeze')
            self.updatePitWeights()
        '''which is tile marked as the wall'''
        if bump: # tile you're on is a wall (not tile you tried to move to), or does bump mean 
            #edge of map
            if self.facing == 'right':
                wallTile = (self.currentTile[0]+1,self.currentTile[1]) #just make a list of tuples???
            if self.facing == 'left':
                wallTile = (self.currentTile[0]-1,self.currentTile[1]) #just make a list of tuples???
            if self.facing == 'up':
                wallTile = (self.currentTile[0],self.currentTile[1]+1) #just make a list of tuples???
            if self.facing == 'down':
                wallTile = (self.currentTile[0],self.currentTile[1]-1) #just make a list of tuples???
            self.walls[wallTile] = ['wall']
        if scream:
            print("might kill the wumpus")
            # you killled the wumpus? 
            del self.possibleWumpus['tile you are facing'] #target tile you shot at no longer a wumpus
            # go through dict coordinates in a straight line and see if they are possible wumpus'
            self.knownWorld[self.targetTile] = ['clear'] #target tile is now known, and clear. 
        if not (stench or breeze or bump) and 'clear' not in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].append('clear')
            if self.currentTile in self.possiblePits:
                del self.possiblePits[self.currentTile]
            if self.currentTile in self.possibleWumpus.keys():
                del self.possibleWumpus[self.currentTile]

    #=============================================================================
    ''' updates the weights of a tile if we think theres a wumpus there
    '''
    #=============================================================================
    def updateWumpusWeights(self):
        adjTiles=[
            (self.currentTile[0],self.currentTile[1]+1), #top
            (self.currentTile[0],self.currentTile[1]-1), #down
            (self.currentTile[0]+1,self.currentTile[1]), #right
            (self.currentTile[0]-1,self.currentTile[1])  #left
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
            (self.currentTile[0],self.currentTile[1]+1), #top
            (self.currentTile[0],self.currentTile[1]-1), #down
            (self.currentTile[0]+1,self.currentTile[1]), #right
            (self.currentTile[0]-1,self.currentTile[1])  #left
        ]
        for tile in adjTiles:
            if tile not in self.knownWorld:
                if tile not in self.possiblePits:
                    self.possiblePits[tile] = 1
                else:
                    self.possiblePits[tile]+=1
