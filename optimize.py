from main import *

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



def traversal(graph, start_node):
	stack = Stack()
	stack.push(start_node)
	visited = set([start_node])
	#print(graph[start_node])
	#print(f"Start Node: {start_node}\n")
	
	while stack.size > 0:
		start_node = stack.pop()
		print("This is popped: " + str(start_node) + "\n")
		#print(graph[start_node])
		try:
			neighbours = list(graph[start_node].keys())
		except:
			break
		print(neighbours)
		for neighbour in neighbours:
			if neighbour not in visited:
				#print(graph[neighbour])
				stack.push(neighbour)
				visited.add(neighbour)

		iter_neighbour = iter(neighbours)
		for i in iter_neighbour:
			try:
				next_node = next(iter_neighbour)
			except StopIteration:
				break
			if graph[start_node][i][0]['length'] <= graph[start_node][next_node][0]['length']:
				print(str(graph[start_node][i][0]['length']) + " - " + str(graph[start_node][next_node][0]['length']))



