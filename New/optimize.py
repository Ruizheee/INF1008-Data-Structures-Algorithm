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
			#print(node.value, end="")
			node = node.next
			if (node != None):
				print("->", end="")
		return



def traversal(graph, start_node):
	stack = [start_node]
	visited = set([start_node])
	shortest_path = []
	path = [start_node]

	while stack:
		current_node = stack.pop()

        # Check if a shorter path to the current node is found
		if not shortest_path or len(path) < len(shortest_path):
			shortest_path = list(path)

		for neighbor in graph[current_node]:
			if neighbor not in visited:
				stack.append(neighbor)
				visited.add(neighbor)

                # Add the neighbor to the path
				path.append(neighbor)

	return shortest_path

def find_shortest_path(graph, start_node):
    return traversal(graph, start_node)





