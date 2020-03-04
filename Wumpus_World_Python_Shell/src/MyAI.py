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

'''this is a method that helps visualize the map'''

import printWord
from Agent import Agent
import random
from collections import defaultdict

#printWord.printWorld("/home/hsuth/CS171/WumpusWorld/Wumpus_World_World_Generator/Worlds/world_0.txt")

class MyAI ( Agent ):
    #=============================================================================
    #=============================================================================
    def __init__ ( self ):
        self.knownWorld = defaultdict(list) #(coordinate:sensors) map of visited tiles (tuple:list)
        self.possiblePits = defaultdict(int) #(coordinate:weight) tuple:integer
        self.possibleWumpus = defaultdict(int) #(coordinate:weight)
        self.heuristic = {} # for A* ?????
        self.currentTile = (0,0) # set initial tile
        self.facing = 'right' #set initial direction
        self.targetTile = (0,0) #tile you want to either move to, or shoot at, should always be adjacent to current square, initially same as origin
        self.findGoldState = True #1 of two stages agent can be in
        self.goHomeState = False #1 of two stages agent can be in
        self.walls = set()
        self.possibleMapSize = 100
        self.goHomePath = []

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
        self.target = self.goHomePath[0]
        self.goHomePath.pop()
    '''
            minScore = 100000
            tempScore = 0
            tempTile = None
            for tile in self.adjTiles():
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
    '''

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
        if self.currentTile == self.targetTile:
            # if every adjacent tile does not have the same value
            if not self.ifWumpusScoreSame() and not self.ifPitsScoreSame():
                minScore = 100000
                tempTile = None
                #print("the adjacent tiles are ", self.adjTiles())
                for tile in self.adjTiles():
                    tempScore = 0
                    if tile in self.possibleWumpus:
                        tempScore += self.possibleWumpus[tile]
                    else: tempScore += 0
                    if tile in self.possiblePits:
                        tempScore += self.possiblePits[tile]
                    else: tempScore += 0

                    # reset values if new min
                    if tempScore < minScore:
                        minScore = tempScore
                        tempTile = tile
                self.targetTile = tempTile

            else:
                print("the scores are now the same, randomly pick one")
                print("the adj tiles has", self.adjTiles())
                self.targetTile = self.adjTiles()[random.randrange(len(self.adjTiles()))]
            #print(f'current is now {self.currentTile}')
            #print(f'target is now {self.targetTile}')
            #input( )


    #=============================================================================
    '''returns the action to move to next tile. Only turns in the left direction (can be optimized later).
        THIS IS MECHANICS, NOT AI ALGORITHM
    '''
    #=============================================================================
    def moveToTargetTile(self):
        print(f'current is now {self.currentTile}')
        print(f'target is now {self.targetTile}')
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
    def updateWorld( self, stench, breeze, bump, scream):
        if "visited" not in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].append("visited")
        
        self.goHomePath.append(self.currentTile)

        if stench and 'stench' not in self.knownWorld[self.currentTile] and self.currentTile not in self.walls:
            self.knownWorld[self.currentTile].append('stench')
            self.updateWumpusWeights()
        if breeze and 'breeze' not in self.knownWorld[self.currentTile]:
            self.knownWorld[self.currentTile].append('breeze')
            self.updatePitWeights()
        '''which is tile marked as the wall'''
        if bump: # tile you're on is a wall (not tile you tried to move to), or does bump mean 
            #edge of map
            self.walls.add(self.currentTile)
            if self.currentTile[0] != 0 and self.currentTile[1] != 0:
                self.possibleMapSize = max(self.currentTile)
                print("The possible map size is now ", self.possibleMapSize)
            self.targetTile = self.adjTiles()[random.randrange(len(self.adjTiles()))]
            
        
        print()
        print("the world looks like, ", self.knownWorld)
        print("the possible wumpus", self.possibleWumpus)
        print("the possible pits", self.possiblePits)
        print("the walls are ", self.walls)

        
        '''
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
        '''

    def adjTiles(self):
        '''return a list of adjTiles'''
        adjT = []
        adjTiles=[
                (self.currentTile[0]+1,self.currentTile[1]),
                (self.currentTile[0],self.currentTile[1]+1),
                (self.currentTile[0],self.currentTile[1]-1), 
                (self.currentTile[0]-1,self.currentTile[1])
            ]
        for tile in adjTiles: # if it's not in the map
            if tile[0] >= 0 and tile[1] >= 0 and tile not in self.walls and tile[0] < self.possibleMapSize and tile[1] < self.possibleMapSize:
                adjT.append(tile)
  
        return adjT
    #=============================================================================
    ''' updates the weights of a tile if we think theres a wumpus there
    '''
    #=============================================================================
    def updateWumpusWeights(self):
        for tile in self.adjTiles():
            if tile not in self.knownWorld:
                if tile not in self.possibleWumpus.keys():
                    self.possibleWumpus[tile] = 1
                else:
                    self.possibleWumpus[tile] += 1

    #=============================================================================
    ''' updates the weights of a tile if we think theres a pit there
    '''
    #=============================================================================
    def updatePitWeights(self):
        for tile in self.adjTiles():
            if tile not in self.knownWorld:
                if tile not in self.possiblePits:
                    self.possiblePits[tile] = 1
                else:
                    self.possiblePits[tile]+=1
