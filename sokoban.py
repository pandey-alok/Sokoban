'''
Group Name: Eagle Nebula
COURSE: Artificial Intelligence (CDS311)
Group Number: 24
Group Members: 
    1. Alok Pandey(2010110071)
    2. Harshit Agarwal(2010110824)

'''
import sys
import heapq
import numpy as np
import re
import sys
import time

#we use heap data structure in priority queue to store data from huristic function
class PriorityQueue:

    def __init__(self):
        self.Heap = []
        self.Count = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0


#Loading and defining the game state

def transferToGameState(formation):
   
    formation = [x.replace('\n','') for x in formation]
    
    formation = [','.join(x) for x in formation]
    
    formation = [x.split(',') for x in formation]
    
    #for max column length
    maxLenColumn = max([len(x) for x in formation]) 
   
    #Assigning formation number to every object in the game state.
    for i in range(len(formation)):
        for j in range(len(formation[i])):
            if formation[i][j] == ' ':   formation[i][j] = 0  #free space
            elif formation[i][j] == '#': formation[i][j] = 1  #wall
            elif formation[i][j] == '@': formation[i][j] = 2  #player
            elif formation[i][j] == '$': formation[i][j] = 3  #box
            elif formation[i][j] == '.': formation[i][j] = 4  #goal
            elif formation[i][j] == '*': formation[i][j] = 5  #box on goal
            elif formation[i][j] == '+': formation[i][j] = 6  #player on goal

        #adding walls in the formation to form equal column length
        columns = len(formation[i])
        if columns < maxLenColumn:
            formation[i].extend([1 for _ in range(maxLenColumn - columns)])

    return np.array(formation)

#Return the positions of boxes in the game state
def boxPos(gameState):
    return tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5)))

#Returns the position of player in the game state
def playerPos(gameState):
    return tuple(np.argwhere(gameState == 2)[0])  

#Return the positions of all the walls in the game state
def wallPos(gameState):
    return tuple(tuple(x) for x in np.argwhere(gameState == 1))

#Return the positions of goals in the game state
def goalPos(gameState):
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5)))

#Check for the goal state
def isGoalState(posBox):
    return sorted(posBox) == sorted(posGoals)

#Check if the given move is legal
def isValidMove(move, posPlayer, posBox):
    xPlayer, yPlayer = posPlayer
    if move[-1].isupper():  # the move was a push
        x1, y1 = xPlayer + 2 * move[0], yPlayer + 2 * move[1]
    else:
        x1, y1 = xPlayer + move[0], yPlayer + move[1]
    return (x1, y1) not in posBox + posWalls

#Return all legal moves for the agent in the current game state
def ValidMoves(posPlayer, posBox):
    allMoves = [[-1, 0, 'u', 'U'], [1, 0, 'd', 'D'], [0, -1, 'l', 'L'], [0, 1, 'r', 'R']]
    xPlayer, yPlayer = posPlayer
    ValidMoves = []
    for move in allMoves:
        x1, y1 = xPlayer + move[0], yPlayer + move[1]
        if (x1, y1) in posBox:  
            # the move was a push
            # for push, we need only upparcase letter
            move.pop(2)  
        else:
            # else we need only lowercase letter
            move.pop(3)  
        if isValidMove(move, posPlayer, posBox):
            ValidMoves.append(move)
        else:
            continue
    return tuple(tuple(x) for x in ValidMoves) 

#Return updated game state after an move is taken
def updatePosition(posPlayer, posBox, move):
    # the previous position of player
    xPlayer, yPlayer = posPlayer 
    # the current position of player
    newPosPlayer = [xPlayer + move[0], yPlayer + move[1]]  
    posBox = [list(x) for x in posBox]
    # if pushing, update the position of box
    if move[-1].isupper():  
        posBox.remove(newPosPlayer)
        posBox.append([xPlayer + 2 * move[0], yPlayer + 2 * move[1]])
    posBox = tuple(tuple(x) for x in posBox)
    newPosPlayer = tuple(newPosPlayer)
    return newPosPlayer, posBox

#reference: https://github.com/KnightofLuna/sokoban-solver/blob/master/sokoban.py

def isFailed(posBox):
    #This function used to observe if the state is potentially failed, then prune the search
    rotatePattern = [[0, 1, 2, 3, 4, 5, 6, 7, 8],
                     [2, 5, 8, 1, 4, 7, 0, 3, 6],
                     [0, 1, 2, 3, 4, 5, 6, 7, 8][::-1],
                     [2, 5, 8, 1, 4, 7, 0, 3, 6][::-1]]                 
    flipPattern = [[2, 1, 0, 5, 4, 3, 8, 7, 6],
                   [0, 3, 6, 1, 4, 7, 2, 5, 8],
                   [2, 1, 0, 5, 4, 3, 8, 7, 6][::-1],
                   [0, 3, 6, 1, 4, 7, 2, 5, 8][::-1]]

    allPattern = rotatePattern + flipPattern


    for box in posBox:
        if box not in posGoals:
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1),
                     (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1),
                     (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls:
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls:
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox:
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox:
                    return True
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[
                    3] in posWalls and newBoard[8] in posWalls:
                    return True
    return False


#A heuristic function to calculate the overall distance between the else boxes and the else goals
def heuristic(posPlayer, posBox): 
    distance = 0
    completes = set(posGoals) & set(posBox)
    sortposBox = list(set(posBox).difference(completes))
    sortposGoals = list(set(posGoals).difference(completes))
    for i in range(len(sortposBox)):
        distance += (abs(sortposBox[i][0] - sortposGoals[i][0])) + (abs(sortposBox[i][1] - sortposGoals[i][1]))
    return distance


#Imlimenting cost function
def cost(moves):
    return len([x for x in moves if x.islower()])


#Implement aStarSearch approach
def aStarSearch():
    beginBox = boxPos(gameState)
    beginPlayer = playerPos(gameState)

    start_state = (beginPlayer, beginBox)
    frontier = PriorityQueue()
    frontier.push([start_state], heuristic(beginPlayer, beginBox))
    exploredSet = set()
    moves = PriorityQueue()
    moves.push([0], heuristic(beginPlayer, start_state[1]))
    counter=0
    while frontier:
        counter+=1
        node = frontier.pop()
        node_action = moves.pop()
        #foe cheking goal state
        if isGoalState(node[-1][-1]):
            return (','.join(node_action[1:]).replace(',', ''),counter)

        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            Cost = cost(node_action[1:])
            for move in ValidMoves(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updatePosition(node[-1][0], node[-1][1], move)
                if isFailed(newPosBox):
                    continue
                Heuristic = heuristic(newPosPlayer, newPosBox)
                frontier.push(node + [(newPosPlayer, newPosBox)], Heuristic + Cost)
                moves.push(node_action + [move[-1]], Heuristic + Cost)


def getLayout(file_name):
    with open(file_name, "r") as f:
        return f.readlines()
    
#Start of exicution section
for i in range(1,int(sys.argv[1])+1):
    start_time=time.time()
    formation = list(getLayout('testCases/testExample'+str(i)+'.xsb'))
    gameState = transferToGameState(formation)
    posWalls = wallPos(gameState)
    posGoals = goalPos(gameState)
    print("Solving teastExample "+str(i)+"...")
    sol,nExpand=aStarSearch()
    end_time = time.time()
    print("Solved teastExample "+str(i)+" in %.2f sec\nNodes Expanded:"% float(end_time-start_time),nExpand)
    print("--------------------------------------")
    with open("testCases/Solution_"+str(i)+".xsb",'w') as op:
            op.write(sol)
            op.write("\nSolved in %.2f seconds."% float(end_time-start_time))
            op.write("\nNodes Expanded: %d"% nExpand)
#END of exicution section
