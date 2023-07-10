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