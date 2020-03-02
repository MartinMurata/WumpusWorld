#path = "/home/hsuth/CS171/WumpusWorld/Wumpus_World_World_Generator/Worlds/world_0.txt"

def printWorld(path):
    f = open(path,'r')
    lines = f.read().split("\n")

    size_col = int(lines[0].split("\t")[0])
    size_row = int(lines[0].split("\t")[1])

    wumpus_posCol = int(lines[1].split("\t")[0])
    wumpus_posRow = int(lines[1].split("\t")[1])

    gold_posCol = int(lines[2].split("\t")[0])
    gold_posRow = int(lines[2].split("\t")[0])
    
    m = []
    
    '''initialize everythin with 0 first'''
    for i in range(size_col):
        row = []
        m.append(row)
        for j in range(size_row):
            row.append(".")

    m[wumpus_posRow][wumpus_posCol] += "W"

    updateAdjacentCoord((wumpus_posRow,wumpus_posCol),size_row,size_col,m, 'S')

    m[gold_posRow][gold_posCol] += "G"

    '''update the pit'''
    num_of_pits = int(lines[3][0])
    
    for i in range(num_of_pits): # breeze
        pit_posCol = int(lines[4+i].split("\t")[0])
        pit_posRow = int(lines[4+i].split("\t")[1])

        m[pit_posRow][pit_posCol] += "P"

        updateAdjacentCoord((pit_posRow,pit_posCol),size_row,size_col,m,'B')
                  

    for i in range(len(m)):
        for j in range(len(m[i])):
            print("{:6s}".format(m[::-1][i][j]), end = " ")
        print()

def checkIfInRange(currentCord1:int, currentCord2:int, sizeRow:int, sizeCol:int):
    return 0 <= currentCord1 < sizeRow and 0 <= currentCord2 < sizeCol

def updateAdjacentCoord(currentCord:tuple,sizeRow:int, sizeCol:int, m:[[]], s:str):
    if checkIfInRange(currentCord[0],currentCord[1]+1,sizeRow, sizeCol):
        m[currentCord[0]][currentCord[1]+1] += s
    if checkIfInRange(currentCord[0],currentCord[1]-1,sizeRow, sizeCol):
        m[currentCord[0]][currentCord[1]-1] += s
    if checkIfInRange(currentCord[0]+1,currentCord[1],sizeRow, sizeCol):
        m[currentCord[0]+1][currentCord[1]] += s
    if checkIfInRange(currentCord[0]-1,currentCord[1],sizeRow, sizeCol):
        m[currentCord[0]-1][currentCord[1]] += s
        