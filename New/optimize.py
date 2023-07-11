from foliumMap import *
import copy
import random
import sys

class QueueNode:
	def __init__(self, value = None):
		self.value = value
		self.next =  None

class Queue:
	def __init__(self):
		self.front = self.rear = None

	def checkEmpty(self):
		return self.front == None

	def enqueue(self, data):
		temp = QueueNode(data)

		if self.rear == None:
			self.front = self.rear = temp
			return
		self.rear.next = temp
		self.rear = temp

	def dequeue(self):

		if self.checkEmpty():
			return
		temp = self.front
		self.front = temp.next

		if self.front == None:
			self.rear = None

		return temp.value

def backtrace(parent, start_node, end_node):
	path = [end_node]
	while path[-1] != start_node:
		path.append(parent[path[-1]])
	path.reverse()
	return path

def bfs(graph, start_node, end_node):
	parent = {}
	queue_list = [start_node]
	queue = Queue()
	queue.enqueue(start_node)
	while queue:
		node = queue.dequeue()
		#print("node: " + str(node) + "\n")
		if node == end_node:
			return backtrace(parent, start_node, end_node)
		for neighbours in graph.neighbors(node):
			if neighbours not in queue_list:
				parent[neighbours] = node
				queue_list.append(neighbours)
				queue.enqueue(neighbours)

class Distance:
	def __init__(self, df, hotels_array):
		self.df = df
		self.hotels_array = hotels_array

	def calculateDistance(self):
		matrix = []
		for mainHotel in self.hotels_array:
			temp_list = []
			for hotels in self.hotels_array:
				#hotel_a = new[new["Name"] == hotels_array[i]][["y","x"]].values[0]
				hotel_a = self.df[self.df["Name"] == mainHotel][["y","x"]].values[0]
				hotel_b = self.df[self.df["Name"] == hotels][["y","x"]].values[0]
				distance_from_i_to_j = ox.distance.euclidean_dist_vec(hotel_a[0], hotel_a[1], hotel_b[0], hotel_b[1])
				temp_list.append(distance_from_i_to_j)
			matrix.append(temp_list)

		
		return matrix


class State:
	def __init__(self, route: [], distance: int = 0):
		self.route = route
		self.distance = distance

	#used to compare a state route with another state route
	def __eq__(self, other):
		for i in range(len(self.route)):
			if self.route[i] != other.route[i]:
				return False
		return True

	def __lt__(self, other):
		return self.distance < other.distance

	def deepcopy(self):
		return State(copy.deepcopy(self.route), copy.deepcopy(self.distance))

	def update_distance(self, matrix, start):
		self.distance = 0

		#starting node
		from_index = start

		#loop through the different nodes and update the total distance
		for i in range(len(self.route)):
			self.distance += matrix[start][self.route[i]]
			start = self.route[i]

		self.distance += matrix[from_index][start]


def probability(p):
	return p > random.uniform(0.0, 1.0)


#the schedule function for SA
def schedule(temp, iteration):
	temperature = temp / (iteration + 1)
	return temperature

def random_soln(matrix: [], start, hotels_array_index, size):
	nodes = hotels_array_index.copy()
	nodes.pop(start)
	soln_list = []

	for i in range(size):

		random.shuffle(nodes)

		states = State(nodes)
		states.update_distance(matrix, start)

		soln_list.append(states)

	soln_list.sort()
	return soln_list[0]


def change(matrix, start, state, change_rate: float = 0.01):

	changed_state = state.deepcopy()

	for i in range(len(changed_state.route)):
		if (random.random() < change_rate):

			random_value = int(random.random() * len(state.route))
			first_node = changed_state.route[i]
			second_node = changed_state.route[random_value]
			changed_state.route[i] =  second_node
			changed_state.route[random_value] = first_node

	changed_state.update_distance(matrix, start)
	return changed_state


def simulated_annealing_optimize(matrix, start, initial_state, change_rate: float = 0.01):

	optimal_state = initial_state
	max = sys.maxsize
	temp = 0

	for i in range(max):
		temp = schedule(temp, i)

		if temp == 0:
			return optimal_state

		candidate = change(matrix, start, optimal_state, change_rate)

		difference = optimal_state.distance - candidate.distance

		if difference > 0 or probability(difference / temp):
			optimal_state = candidate

