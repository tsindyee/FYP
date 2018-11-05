from itertools import chain
import math
import random
import numpy as np
import sys
import csv

#initialize 3 global variable for counting
totalNumberOfDeadStateOfHorizontalBlock = 0
totalNumberOfDeadStateOfVerticalBlock = 0
totalNumberOfDeadStateOfBothBlock = 0

dimension = 3
numberOfPieces = 3


def checkThreeConsecutiveOne(array):
	for i in range(dimension):
		if array[i][0] == 1 and array[i][1] == 1 and array[i][2] == 1:
			return True
		elif array[0][i] == 1 and array[1][i] == 1 and array[2][i]:
			return True
	return False

def createStates():
	allPossibleStates = []

	for i in range(512):
		x = format(i, '09b')
		modified_list = [int(i) for  element in x for i in element]
		array = np.array(modified_list)
		array = np.reshape(array, (3, 3))
		if not checkThreeConsecutiveOne(array):
			allPossibleStates.append(array)
	return allPossibleStates


def checkGameOver(array, piece):
	if piece == 0:
		horizontalPossibleMove = 0
		for i in range(dimension):
			for j in range(dimension -1):
				if array[i][j] == 0 and array[i][j+1] == 0:
					horizontalPossibleMove += 1
		if horizontalPossibleMove == 0:
			return True
		return False

	if piece == 1:
		verticalPossibleMove = 0
		for i in range(dimension - 1):
			for j in range(dimension):
				if array[i][j] == 0 and array[i+1][j] == 0:
					verticalPossibleMove += 1
		
		if verticalPossibleMove == 0:
			return True
		return False
	return False

def calculateReward(array, piece):
	if checkGameOver(array, piece):
		return -100
	else:
		return 10

def findInitialRandomPolicy(array, piece):
	if piece == 0:
		for i in range(dimension):
			for j in range(dimension -1):
				if array[i][j] == 0 and array[i][j+1] == 0:
					return (i, j)
	if piece == 1:
		for i in range(dimension - 1):
			for j in range(dimension):
				if array[i][j] == 0 and array[i+1][j] == 0:
					return (i, j)
	if piece == 2:
		for i in range(dimension):
			for j in range(dimension):
				if array[i][j] == 0:
					return (i, j)


def killThreeConsecutiveOne(array):
	numberofLineKilled = 0
	for i in range(dimension):
		if array[i][0] != 0 and array[i][1] != 0 and array[i][2] != 0:
			array[i][0] = 2
			array[i][1] = 2
			array[i][2] = 2
			numberofLineKilled +=1

		if array[0][i] != 0 and array[1][i] != 0 and array[2][i] !=0:
			array[0][i] = 2
			array[1][i] = 2
			array[2][i] = 2
			numberofLineKilled +=1
	for i in range(dimension):
		for j in range(dimension):
			if array[i][j] == 2:
				array[i][j] = 0
	return {'array':array, 'numberofLineKilled':numberofLineKilled }

def createAllState():
	allState = []
	boards = createStates()
	
	for board in boards:
		# 0: horizontal  1: vertical  2: 1x1
		for i in range(numberOfPieces):
			reward = calculateReward(board, i)
			policy = findInitialRandomPolicy(board, i)
			prob = 1.0 /numberOfPieces
			# prob = -1
			# if i <= 1:
			# 	prob = 0.4
			# else:
			# 	prob = 0.2


			state = {
				"board": board,
				"piece": i,
				"prob": prob,

				"policy": policy,
				"value": reward
			}
			# print type(state)
			allState.append(state);
	# print allState
	return allState

def predictNumberOfPossibleMove(board):
	h = 0
	for i in range(dimension):
		for j in range(dimension -1):
			if board[i][j] == 0 and board[i][j+1] == 0:
				h +=1
	v = 0
	for i in range(dimension - 1):
				for j in range(dimension):
					if board[i][j] == 0 and board[i+1][j] == 0:
						v +=1
	hole = 0
	for i in range(dimension):
		if board[i][j] == 0:
			hole +=1
	return (h + v + hole) / 3.0 * 10

def calculateValue(newArray):
	gamma = 0.5
	# print "gamma = ", gamma
	result = killThreeConsecutiveOne(newArray)
	newArray = result['array']

	numberofLineKilled = result['numberofLineKilled']
	reward = math.pow(numberofLineKilled, 2) * 10 #+ predictNumberOfPossibleMove(newArray)

	arrays = [ myState for myState in allState if np.array_equal(myState["board"], newArray)]
	# print "reward = ", reward
	secondPart = 0
	for array in arrays:
		secondPart += gamma * array["prob"] * array["value"]
		# print "secondPart = ", secondPart
	
	newValue = reward + secondPart
	# print "newValue = ", newValue

	return newValue


def updateValueAndPolicy(allState):
	

	for state in allState:
		board = state["board"]
		piece = state["piece"]

		if piece == 0:
			maxValue = -1000
			action = None
			for i in range(dimension):
				for j in range(dimension -1):
					if board[i][j] == 0 and board[i][j+1] == 0:

						tmpAction = (i, j)
						newArray = np.copy(board)
						newArray[i][j] = 1
						newArray[i][j+1] = 1

						newValue = calculateValue(newArray)

						if newValue > maxValue:
							action = (i, j)
							maxValue = newValue
							
			state["value"] = maxValue
			state["policy"] = action

		if piece == 1:
			maxValue = -1000
			action = None
			
			for i in range(dimension - 1):
				for j in range(dimension):
					if board[i][j] == 0 and board[i+1][j] == 0:
						
						newArray = np.copy(board)
						newArray[i][j] = 1
						newArray[i+1][j] = 1

						newValue = calculateValue(newArray)
						

						if newValue > maxValue:
							action = (i, j)
							maxValue = newValue
							
			state["value"] = maxValue
			state["policy"] = action

		if piece == 2:
			maxValue = -1000
			action = None
			
			for i in range(dimension):
				for j in range(dimension):
					if board[i][j] == 0:
						reward = 0
						newValue = 0
			
						newArray = np.copy(board)
						newArray[i][j] = 1

						newValue = calculateValue(newArray)


						if newValue > maxValue:
							action = (i, j)
							maxValue = newValue

			state["value"] = maxValue
			state["policy"] = action

						

	

allState = createAllState()

for i in range(20):

	updateValueAndPolicy(allState)
	name = "MDP" + str(i) + ".csv"
	with open(name, 'w') as csvfile:
		fieldnames = ['board','piece','prob','policy','value']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for state in allState:
			writer.writerow(state)


# for i in range(5):
# 	updateValueAndPolicy(allState)
# 	print "===============The ", i, "Time==============="
# 	for state in allState:
# 		print state
# 	print "============================================="

# print allState

# with open('MDP1.cse', 'w') as csvfile:
# 	fieldnames = ['board','piece','prob','policy','value']
# 	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
# 	writer.writeheader()
# 	for state in allState:
# 		writer.writerow(state)






# struct state {
# 	board (array)
# 	piece (intger 1-3 | array)
# 	prob to random block = 1/3;


# 	rewards (number)
# 	policy (coordinate)
# 	value (number)
# }

# for state in allStates:
# 	max = 0;
# 	policy = 0;
# 	for each policy:
# 		reward = map policy_to_state "reward function"
# 		sum (1/3 V(s' with 2x1) + 1/3 V(s' with 1x1) + 1/3 V(s' with 1x1))

# 		find max, polciy






















