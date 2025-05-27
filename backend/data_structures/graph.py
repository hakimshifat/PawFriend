import heapq
import math

class Graph:
    
    def __init__(self):
        self.vertices = {}
    
    def add_vertex(self, vertex_id, data=None):
        if vertex_id not in self.vertices:
            self.vertices[vertex_id] = {
                'data': data,
                'edges': {}
            }
            return True
        return False
    
    def add_edge(self, from_vertex, to_vertex, weight):
        if from_vertex in self.vertices and to_vertex in self.vertices:
            self.vertices[from_vertex]['edges'][to_vertex] = weight
            return True
        return False
    
    def get_vertex_data(self, vertex_id):
        if vertex_id in self.vertices:
            return self.vertices[vertex_id]['data']
        return None
    
    def get_vertices(self):
        return list(self.vertices.keys())
    
    def get_edges(self, vertex_id):
        if vertex_id in self.vertices:
            return self.vertices[vertex_id]['edges']
        return {}
    
    def calculate_distance(self, point1, point2):
        
        R = 6371.0
        
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        return distance
    
    def build_clinic_graph(self, clinics):
        
        for clinic_id, clinic_data in clinics.items():
            self.add_vertex(clinic_id, clinic_data)
        
        
        for id1 in clinics:
            for id2 in clinics:
                if id1 != id2:
                    loc1 = clinics[id1]['location']
                    loc2 = clinics[id2]['location']
                    distance = self.calculate_distance(loc1, loc2)
                    self.add_edge(id1, id2, distance)
        
        return self
    
    def dijkstra_shortest_path(self, start_vertex, end_vertex):
        if start_vertex not in self.vertices or end_vertex not in self.vertices:
            return float('infinity'), []
        
        
        distances = {vertex: float('infinity') for vertex in self.vertices}
        distances[start_vertex] = 0
        
        
        previous = {vertex: None for vertex in self.vertices}
        
        
        pq = [(0, start_vertex)]
        
        while pq:
            current_distance, current_vertex = heapq.heappop(pq)
            
            
            if current_vertex == end_vertex:
                break
                
            
            if current_distance > distances[current_vertex]:
                continue
                
            
            for neighbor, weight in self.vertices[current_vertex]['edges'].items():
                distance = current_distance + weight
                
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (distance, neighbor))
        
        
        path = []
        current = end_vertex
        
        while current:
            path.append(current)
            current = previous[current]
            
        
        path.reverse()
        
        return distances[end_vertex], path
    
    def find_nearest_vertex(self, location, condition=None):
        nearest_vertex = None
        min_distance = float('infinity')
        
        for vertex_id, vertex in self.vertices.items():
            
            if condition and not condition(vertex['data']):
                continue
                
            vertex_location = vertex['data'].get('location')
            if vertex_location:
                distance = self.calculate_distance(location, vertex_location)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_vertex = (vertex_id, distance, vertex['data'])
        
        return nearest_vertex
    
    def get_directions(self, location, vertex_id):
        if vertex_id not in self.vertices:
            return []
            
        vertex_data = self.vertices[vertex_id]['data']
        vertex_location = vertex_data.get('location')
        
        if not vertex_location:
            return []
            
        
        distance = self.calculate_distance(location, vertex_location)
        
        
        travel_time_minutes = int(distance * 2)
        
        
        directions = [
            f"Head to {vertex_data.get('name', 'destination')}",
            f"Total distance: {round(distance, 2)} km",
            f"Estimated travel time: {travel_time_minutes} minutes"
        ]
        
        return directions
