from foliumMap import *
import copy
import random
import sys
import numpy as np
import math
import decimal

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
	total_distance = 0
	while path[-1] != start_node:
		distance = parent[path[-1]][1]
		total_distance += distance
		path.append(parent[path[-1]][0])

	path.reverse()
	return path, total_distance

def bfs(graph, start_node, end_node):
	#a dictionary that holds parent child pairing to backtrace to get the route
	parent = {}
	visited_list = [start_node]
	queue = Queue()
	queue.enqueue(start_node)
	while queue:
		node = queue.dequeue()
		if node == end_node:
			return backtrace(parent, start_node, end_node)
		for neighbours in graph.neighbors(node):
			if neighbours not in visited_list:
				parent[neighbours] = [node, graph[node][neighbours][0]['length']]
				visited_list.append(neighbours)
				queue.enqueue(neighbours)

class Distance:
	def __init__(self, df, hotels_array):
		self.df = df
		self.hotels_array = hotels_array

	#returns a matrix of distances, eg. [[0.0, 0.16733845161529082, 0.15804035047101792], [0.16733845161529082, 0.0, 0.029338032176682512], [0.15804035047101792, 0.029338032176682512, 0.0]], the first list is the
	#distance from node A to node A, node B and C, the second list is the distance from node B to node A, node B and C, so on
	def calculateDistance(self):
		matrix = []
		for mainHotel in self.hotels_array:
			temp_list = []
			for hotels in self.hotels_array:
				hotel_a = self.df[self.df["Name"] == mainHotel][["y","x"]].values[0]
				hotel_b = self.df[self.df["Name"] == hotels][["y","x"]].values[0]
				distance_from_i_to_j = ox.distance.euclidean_dist_vec(hotel_a[0], hotel_a[1], hotel_b[0], hotel_b[1])
				temp_list.append(distance_from_i_to_j)
			matrix.append(temp_list)

		
		return matrix


class State:
	def __init__(self, route, distance: int = 0):
		#route is a list
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

	#this is to update the distance
	def update_distance(self, matrix, start):
		self.distance = 0

		#starting node
		from_index = start

		#loop through the different nodes and update the total distance
		for i in range(len(self.route)):
			self.distance += matrix[start][self.route[i]]
			#next node
			start = self.route[i]

		
		self.distance += matrix[from_index][start]


def probability(p):
	return random.random() < p


#the schedule function for SA
def schedule(temp, iteration):
	temperature = temp / (iteration + 1)
	return temperature

def random_soln(matrix: [], start, hotels_array_index, size):
	nodes = hotels_array_index.copy()
	nodes.pop(start)
	soln_list = []

	for i in range(100):

		random.shuffle(nodes)

		states = State(nodes)
		states.update_distance(matrix, start)

		soln_list.append(states)

	soln_list.sort()
	return soln_list[0]

#changing/swapping the routes, aka solution
def change(matrix, start, state, change_rate: float = 0.5):

	changed_state = state.deepcopy()

	for i in range(len(changed_state.route)):
		if (random.random() < change_rate):

			random_value = int(random.random() * len(state.route)) #random value is 0
			first_node = changed_state.route[i]
			second_node = changed_state.route[random_value]
			changed_state.route[i] =  second_node
			changed_state.route[random_value] = first_node

	changed_state.update_distance(matrix, start)

	return changed_state

def simulated_annealing_optimize(matrix, start, initial_state, n_iteration, change_rate: float = 0.5):

	optimal_state = initial_state
	temp = 10
	temp = np.float_(temp)
	states_list = []
	for i in range(n_iteration):
		candidate = change(matrix, start, optimal_state, change_rate)
		difference = optimal_state.distance - candidate.distance
		temp = schedule(temp, i)

		if difference >= 0 or probability(np.exp(-difference / np.exp(temp))):
			optimal_state = candidate
			states_list.append(optimal_state)
			print("changed_state: ", str(optimal_state.route))
			print("distance: ", str(optimal_state.distance))
			print("temperature: ", str(temp))

	states_list.sort(key = lambda x: x.distance)
	return states_list[0]
	#return optimal_state

def dijkstra(graph, start_node, end_node, weight):
	weight_types = {'option 1': 'length', 'option 2': 'speed_kph', 'option 3': 'travel_time'}
	weight_selected = weight_types[weight]
	queue = Queue()
	queue.enqueue(start_node)
	distance = {}
	distance[start_node] = 0
	parent = {}

	while queue:
		current_node = queue.dequeue()

		if current_node == end_node:
			return backtrace(parent, start_node, end_node)

		for neighbours in graph.neighbors(current_node):
			try:
				if distance[neighbours] > distance[current_node] + graph[current_node][neighbours][0][weight_selected]:
					distance[neighbours] = distance[current_node] + graph[current_node][neighbours][0][weight_selected]
					parent[neighbours] = [current_node, graph[current_node][neighbours][0]['length']]
					queue.enqueue(neighbours)
			except KeyError:
				distance[neighbours] = distance[current_node] + graph[current_node][neighbours][0][weight_selected]
				parent[neighbours] = [current_node, graph[current_node][neighbours][0]['length']]
				queue.enqueue(neighbours)


