import math
import heapq
import os
import json
import random
from backend.data_structures.graph import Graph

def create_clinic_graph():
    
    sample_locations = {
        "A": {"name": "Dhaka University", "type": "place"},
        "B": {"name": "Bashundhara City Shopping Mall", "type": "place"},
        "C": {"name": "Shahbagh Intersection", "type": "place"},
        "D": {"name": "Farmgate", "type": "place"},
        "E": {"name": "Uttara Sector 7 Park", "type": "place"},
        "F": {"name": "Hatirjheel Lake", "type": "place"},
        "G": {"name": "Lalbagh Fort", "type": "place"},
        "H": {"name": "Ramna Park", "type": "place"},
        "I": {"name": "Gulshan Circle 2", "type": "place"},
        "J": {"name": "Motijheel Square", "type": "place"},
        "K": {"name": "Mirpur Zoo", "type": "place"},
        "L": {"name": "Dhanmondi Lake Park", "type": "place"},
        "M": {"name": "Baridhara DOHS Park", "type": "place"},
        "1": {"name": "Dhanmondi Pet Hospital", "address": "House 12, Road 7, Dhanmondi, Dhaka", "phone": "02-1234567", "emergency": True, "hours": "24/7", "type": "clinic"},
        "2": {"name": "Banani Animal Clinic", "address": "Road 11, Banani, Dhaka", "phone": "02-2345678", "emergency": False, "hours": "8AM-6PM", "type": "clinic"},
        "3": {"name": "Gulshan Veterinary Center", "address": "Gulshan Ave, Dhaka", "phone": "02-3456789", "emergency": True, "hours": "24/7", "type": "clinic"},
        "4": {"name": "Mirpur Pet Care", "address": "Section 10, Mirpur, Dhaka", "phone": "02-4567890", "emergency": False, "hours": "9AM-7PM", "type": "clinic"},
        "5": {"name": "Motijheel Animal Hospital", "address": "Motijheel, Dhaka", "phone": "02-5678901", "emergency": True, "hours": "24/7", "type": "clinic"},
        "6": {"name": "Apollo Veterinary Hospital", "address": "Baridhara, Dhaka", "phone": "02-6789012", "emergency": True, "hours": "24/7", "type": "clinic"},
        "7": {"name": "Central Veterinary Hospital", "address": "Kazi Nazrul Islam Ave, Dhaka", "phone": "02-7890123", "emergency": True, "hours": "24/7", "type": "clinic"},
        "8": {"name": "Uttara Pet Clinic", "address": "Uttara, Dhaka", "phone": "02-8901234", "emergency": False, "hours": "9AM-8PM", "type": "clinic"},
    }
    base_edges = [
        ("A", "B", 11.1), ("A", "C", 12.2), ("A", "G", 13.3), ("A", "1", 14.4),
        ("B", "C", 15.5), ("B", "F", 16.6), ("B", "2", 17.7),
        ("C", "D", 18.8), ("C", "H", 19.9), ("C", "1", 20.1), ("C", "3", 21.2),
        ("D", "1", 22.3), ("D", "G", 24.5),
        ("E", "8", 25.6), ("E", "F", 26.7),
        ("F", "2", 28.9), ("F", "G", 30.0), ("F", "3", 31.1),
        ("G", "1", 32.2), ("G", "B", 33.3),
        ("H", "C", 35.5), ("H", "3", 36.6),
        ("I", "C", 37.7), ("I", "3", 38.8), ("I", "K", 39.9),
        ("J", "B", 41.0), ("J", "5", 42.1), ("J", "L", 43.2),
        ("K", "F", 44.3), ("K", "I", 45.4), ("K", "M", 46.5),
        ("L", "A", 47.6), ("L", "J", 48.7), ("L", "M", 49.8),
        ("M", "K", 50.9), ("M", "L", 52.0), ("M", "6", 53.1)
    ]
    
    graph = Graph()
    for node_id, node_data in sample_locations.items():
        graph.add_vertex(node_id, node_data)
    for from_id, to_id, weight in base_edges:
        graph.add_edge(from_id, to_id, weight)
        graph.add_edge(to_id, from_id, weight)
    return graph, sample_locations

def dijkstra_shortest_path(graph, start_clinic_id, end_clinic_id):
    
    return graph.dijkstra_shortest_path(start_clinic_id, end_clinic_id)

def find_nearest_clinic(graph, from_id, emergency_only=True):
    clinics = {k: v for k, v in graph.vertices.items() if v['data'].get('type') == 'clinic'}
    min_dist = float('inf')
    nearest_id = None
    for cid in clinics:
        if emergency_only and not clinics[cid]['data'].get('emergency', False):
            continue
        dist, _ = graph.dijkstra_shortest_path(from_id, cid)
        if dist < min_dist:
            min_dist = dist
            nearest_id = cid
    if nearest_id:
        clinic_data = clinics[nearest_id]['data'].copy()
        clinic_data['distance'] = min_dist
        return clinic_data, nearest_id
    return None, None

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
