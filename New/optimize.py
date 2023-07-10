from foliumMap import *

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

		return temp

def nodes_connected(graph, u, v):
	return u in graph.neighbors(v)

def bfs_traverse(graph, start_node, end_node):
	queue = Queue()
	queue.enqueue(start_node)
	while queue:
		path = queue.dequeue()
		node = list(graph.neighbors(path))[-1]
		if node == end_node:
			return path
		for neighbours in graph.neighbors(node):
			new_path = list(path)
			new_path.append(neighbours)
			queue.append(new_path)


'''
def traversal(graph, start_node, end_node):
	queue = Queue()
	queue.enqueue(start_node)
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
		
			#if graph[start_node][i][0]['length'] <= graph[start_node][next_node][0]['length']:
			#	#this block if 1st edge is shorter than 2nd edge to 2nd node
			#	#print(str(graph[start_node][i][0]['length']) + " - " + str(graph[start_node][next_node][0]['length']))
			#	route_list.append(graph[start_node][i])
				#print("this is route list" + str(route_list[0]))
			
		if start_node == end_node:
			print("THIS IS THE END: " + str(start_node))
			print("\nTOTAL TRAVEL TIME: " + str(weightage[j]))
			j += 1
			print(myDict[start_node])
			return route_list
				#weightage.append()
				#break
'''
