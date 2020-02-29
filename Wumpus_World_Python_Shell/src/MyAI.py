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

class MyAI ( Agent ):
    #=============================================================================
    #=============================================================================
    def __init__ ( self ):
        self.knownWorld = {} #(coordinate:sensors) map of visited tiles
        self.possiblePits = {} #(coordinate:weight)
        self.possibleWumpus = {} #(coordinate:weight)
        self.currentTile = (1,1) #set initial tile
        self.facing = 'right' #set initial direction
        self.targetTile = None #ile you want to either move to, or shoot at, should always be adjacent to current square
        self.findGoldState = True #1 of two stages agent can be in
        self.goHomeState = False #1 of two stages agent can be in
    #=============================================================================
    #=============================================================================
    def getAction( self, stench, breeze, glitter, bump, scream ):
        if findGoldState:
            return findingGold(stench, breeze, glitter, bump, scream)
        if goHomeState:
            return goHome(stench, breeze, glitter, bump, scream)

    #=============================================================================
    '''main logic pertaining to getting to the gold.''' 
    #=============================================================================
    def findingGold( self, stench, breeze, glitter, bump, scream ):
        self.updateWorld( stench, breeze, glitter, bump, scream )
        self.setTargetTile()d
        return self.moveToTargetTile()

    #=============================================================================
    ''' main logic pertaining to climbing out of the cave after getting gold. 
        Uses algorithm to find best path out of cave based on known world 
        (dijkstras? A*? idk yet) 
        THIS IS NOT MECHANICS, USE SMART AI ALGORITHM
    '''
    #=============================================================================
    def goHome(self, stench, breeze, glitter, bump, scream ):
        print("GOING HOME MAN")
        if currentTile == (1,1):
            return Agent.Action.CLIMB
        else:
            #implement 

    #=============================================================================
    '''randomly picks unvisited tile. If there is any intelligence in this AI, it should
        be done here.....since picking the next tile requires a smart noodle...
        THIS IS NOT MECHANICS, USE SMART AI ALGORITHM
        use the weights for the pits and wumpus you made 
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
                break
        # next tile is below
        if self.targetTile[0] < self.currentTile[0]:
            #face the correct way first 
            if self.facing != 'down':
                return Agent.Action.TURN_LEFT
            else:
                self.facing = 'down'
                break
        # next tile is right 
        if self.targetTile[1] > self.currentTile[1]:
            #face the correct way first 
            if self.facing != 'right':
                return Agent.Action.TURN_LEFT
            else:
                self.facing = 'right'
                break
        # next tile is left
        if self.targetTile[1] < self.currentTile[1]:
            #face the correct way first 
            if self.facing != 'left':
                return Agent.Action.TURN_LEFT
            else:
                self.facing = 'left'
                break
        self.currentTile = self.targetTile
        return Agent.Action.FORWARD

    #=============================================================================
    ''' keeps track of everything agent has seen so far. Saves in a dictionary
        as key = coordinate and value = sense
        THIS IS MECHANICS, NOT AI ALGORITHM
    '''
    #=============================================================================
    def updateWorld( self, stench, breeze, glitter, bump, scream) :
        if coord not in self.knownWorld:
            #initialize to empty list 
            self.knownWorld[self.currentTile] = []

        if stench:
            self.knownWorld[self.currentTile].append('stench')
            self.updateWumpusWeights()
        if breeze:
            self.knownWorld[self.currentTile].append('breeze')
            self.updatePitWeights()
        if glitter:  
            # grab gold
            self.knownWorld[self.currentTile].append('glitter')
            findGoldState = False
            goHome = True
            return Agent.Action.GRAB
        if bump:
            #edge of map
            if self.targetTile:
                perimeterTile = self.targetTile #the previus targetTile is now known as perimeter
                self.knownWorld[perimeterTile].append('perimeter')
        if scream:
            # you killled the wumpus? 
            del self.possibleWumpus[self.targetTile] #target tile you shot at no longer a wumpus
            self.knownWorld[self.targetTile] = ['clear'] #target tile is now known, and clear. 
            pass
        if not (stench or breeze or glitter or bump):
            # nothing
            self.knownWorld[self.currentTile].append('clear')
            pass
    #=============================================================================
    ''' updates the weights of a tile if we think theres a wumpus there
    '''
    #=============================================================================
    def updateWumpusWeights():
        adjTiles=[
            (self.currentTile[0],self.currentTile[1]+1), #right
            (self.currentTile[0],self.currentTile[1]-1), #left
            (self.currentTile[0]+1,self.currentTile[1]), #above
            (self.currentTile[0]-1,self.currentTile[1])  #below
        ]
        for tile in adjTiles:
            if tile not in self.knownWorld:
                if tile not in self.possibleWumpus:
                    self.possibleWumpus[tile] = 1
                else:
                    self.possibleWumpus[tile]+=1

            
    #=============================================================================
    ''' updates the weights of a tile if we think theres a pit there
    '''
    #=============================================================================
    def updatePitWeights():
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
