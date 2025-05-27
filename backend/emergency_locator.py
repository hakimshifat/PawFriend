import math
import heapq
import os
import json
from backend.data_structures.graph import Graph

def haversine_distance(point1, point2):
    
    R = 6371.0
    
    
    lat1 = math.radians(point1[0])
    lon1 = math.radians(point1[1])
    lat2 = math.radians(point2[0])
    lon2 = math.radians(point2[1])
    
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

def create_clinic_graph():
    clinics_file = 'data/clinics.json'
    
    
    os.makedirs('data', exist_ok=True)
    
    
    sample_clinics = {
        "1": {
            "name": "Downtown Pet Hospital",
            "location": (40.7128, -74.0060),  
            "address": "123 Main St, New York, NY",
            "phone": "212-555-1000",
            "emergency": True,
            "hours": "24/7"
        },
        "2": {
            "name": "Uptown Animal Clinic",
            "location": (40.7831, -73.9712),  
            "address": "456 Park Ave, New York, NY",
            "phone": "212-555-2000",
            "emergency": False,
            "hours": "8AM-6PM"
        },
        "3": {
            "name": "Brooklyn Veterinary Center",
            "location": (40.6782, -73.9442),  
            "address": "789 Atlantic Ave, Brooklyn, NY",
            "phone": "718-555-3000",
            "emergency": True,
            "hours": "24/7"
        },
        "4": {
            "name": "Queens Pet Care",
            "location": (40.7282, -73.7949),  
            "address": "101 Queens Blvd, Queens, NY",
            "phone": "718-555-4000",
            "emergency": False,
            "hours": "9AM-7PM"
        },
        "5": {
            "name": "Bronx Animal Hospital",
            "location": (40.8448, -73.8648),  
            "address": "202 Grand Concourse, Bronx, NY",
            "phone": "718-555-5000",
            "emergency": True,
            "hours": "24/7"
        }
    }
    
    
    if not os.path.exists(clinics_file):
        with open(clinics_file, 'w') as f:
            json.dump(sample_clinics, f, indent=2)
    
    
    try:
        with open(clinics_file, 'r') as f:
            clinics = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        clinics = sample_clinics
    
    
    clinic_graph = Graph()
    
    
    clinic_graph.build_clinic_graph(clinics)
    
    return clinic_graph, clinics

def dijkstra_shortest_path(graph, start_clinic_id, end_clinic_id):
    
    return graph.dijkstra_shortest_path(start_clinic_id, end_clinic_id)

def find_nearest_clinic(graph, user_location, emergency_only=True):
    
    if isinstance(graph, tuple) and hasattr(graph[0], 'find_nearest_vertex'):
        actual_graph = graph[0]
        clinics = graph[1]
    else:
        actual_graph = graph
        clinics = None

    
    if emergency_only:
        condition = lambda clinic: clinic.get('emergency', False)
    else:
        condition = lambda clinic: True

    nearest = actual_graph.find_nearest_vertex(user_location, condition)

    
    if isinstance(nearest, tuple) and len(nearest) == 2:
        clinic_data = nearest[1]
    
    elif clinics and isinstance(nearest, (str, int)) and nearest in clinics:
        clinic_data = clinics[nearest]
    
    elif isinstance(nearest, dict):
        clinic_data = nearest
    else:
        clinic_data = None

    
    if clinic_data and "location" in clinic_data:
        
        clinic_data["location"] = tuple(clinic_data["location"])
        return clinic_data
    else:
        return {}

def get_path_to_clinic(graph, user_location, clinic_id):
    
    clinic_data = graph.get_vertex_data(clinic_id)
    
    if not clinic_data:
        return []
    
    
    basic_directions = graph.get_directions(user_location, clinic_id)
    
    
    enhanced_directions = [
        f"Head to {clinic_data['name']}",
        f"Address: {clinic_data.get('address', 'N/A')}",
        f"Phone: {clinic_data.get('phone', 'N/A')}",
        f"Hours: {clinic_data.get('hours', 'N/A')}"
    ]
    
    
    enhanced_directions.extend(basic_directions[1:])
    
    return enhanced_directions
