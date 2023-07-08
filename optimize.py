import heapq
from main import *

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    queue = [(0, start)]

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))

    return distances


def traversal(graph, start_node):
    stack = Stack()
    stack.push(start_node)
    visited = set([start_node])
    route_list = []

    while stack.size > 0:
        start_node = stack.pop()

        try:
            neighbors = list(graph[start_node].keys())
        except:
            break

        for neighbor in neighbors:
            if neighbor not in visited:
                stack.push(neighbor)
                visited.add(neighbor)

        iter_neighbour = iter(neighbors)
        for i in iter_neighbour:
            try:
                next_node = next(iter_neighbour)
            except StopIteration:
                break

            if graph[start_node][i][0]['length'] <= graph[start_node][next_node][0]['length']:
                route_list.append(graph[start_node][i])

    return route_list


def optimized_traversal(graph, start_node):
    distances = dijkstra(graph, start_node)
    sorted_neighbors = sorted(graph[start_node].items(), key=lambda x: distances[x[0]])

    route_list = []
    for neighbor, _ in sorted_neighbors:
        if graph[start_node][neighbor][0]['length'] <= distances[neighbor]:
            route_list.append(graph[start_node][neighbor])

    return route_list
