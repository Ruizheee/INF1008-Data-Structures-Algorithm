from foliumMap import *

class StackNode:
	def __init__(self, value=None):
		self.value = value
		self.next = None

class Stack:
	def __init__(self):
		self.head = None
		self.size = 0

	def push(self, value):
		#if the stack is empty
		if self.head == None:
			self.head = StackNode(value)
		else:
			new_node = StackNode(value)
			new_node.next = self.head
			self.head = new_node
		self.size += 1

	def pop(self):
		if self.head == None:
			return None
		else:
			popped = self.head
			self.head = self.head.next
			popped.next = None
			return popped.value
		self.size -= 1

	def display(self):
		node = self.head

		while (node != None):
			print(node.value, end="")
			node = node.next
			if (node != None):
				print("->", end="")
		return

def nodes_connected(graph, u, v):
	return u in graph.neighbors(v)


def traversal(graph, start_node, end_node):
	stack = Stack()
	stack.push(start_node)
	visited = set([start_node])
	route_list = []
	#print(graph[start_node])
	#print(f"Start Node: {start_node}\n")
	j = 0
	weightage = []
	myDict = {}
	
	while stack.size > 0:
		start_node = stack.pop()
		weightage.append(0)
		#print("This is popped: " + str(start_node) + "\n")
		#print(graph[start_node])
		try:
			neighbours = list(graph[start_node].keys())
			neighbours = list(neighbors(graph, start_node))
			print("neighbours: " + neighbours + "\n")
		except:
			break
		#print(neighbours)
		for neighbour in neighbours:
			if neighbour not in visited:
				#print(graph[neighbour])
				stack.push(neighbour)
				visited.add(neighbour)
				myDict[neighbour] = start_node

		iter_neighbour = iter(neighbours)
		for i in iter_neighbour:
			try:
				next_node = next(iter_neighbour)
				#weightage[j] += graph[start_node][next_node][0]['travel_time']
				#route_list.append(start_node)
			except StopIteration:
				break

			if nodes_connected(graph, start_node, next_node) == True:
				route_list.append(next_node)

			#route_list.append(start_node)
			weightage[j] += graph[start_node][next_node][0]['travel_time']	
			'''
			if graph[start_node][i][0]['length'] <= graph[start_node][next_node][0]['length']:
				#this block if 1st edge is shorter than 2nd edge to 2nd node
				#print(str(graph[start_node][i][0]['length']) + " - " + str(graph[start_node][next_node][0]['length']))
				route_list.append(graph[start_node][i])
				#print("this is route list" + str(route_list[0]))
			'''
		if start_node == end_node:
			print("THIS IS THE END: " + str(start_node))
			print("\nTOTAL TRAVEL TIME: " + str(weightage[j]))
			j += 1
			print(myDict[start_node])
			return route_list
				#weightage.append()
				#break
