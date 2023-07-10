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
