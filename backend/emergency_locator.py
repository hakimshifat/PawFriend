import math
import heapq
import os
import json
from backend.data_structures.graph import Graph

def create_clinic_graph():
    # Define all locations (no coordinates needed for pathfinding)
    sample_locations = {
        "A": {"name": "Dhaka University", "type": "place"},
        "B": {"name": "Bashundhara City Shopping Mall", "type": "place"},
        "C": {"name": "Shahbagh Intersection", "type": "place"},
        "D": {"name": "Farmgate", "type": "place"},
        "E": {"name": "Uttara Sector 7 Park", "type": "place"},
        "F": {"name": "Hatirjheel Lake", "type": "place"},
        "G": {"name": "Lalbagh Fort", "type": "place"},
        "H": {"name": "Ramna Park", "type": "place"},
        "I": {"name": "Gulistan", "type": "place"},
        "J": {"name": "Mohakhali Bus Terminal", "type": "place"},
        "K": {"name": "Baily Road", "type": "place"},
        "L": {"name": "New Market", "type": "place"},
        "M": {"name": "Khilgaon Flyover", "type": "place"},
        "N": {"name": "Shyamoli Square", "type": "place"},
        "O": {"name": "Mirpur 1 Circle", "type": "place"},
        "P": {"name": "Dhanmondi Lake", "type": "place"},
        "Q": {"name": "Banani Lake", "type": "place"},
        "R": {"name": "Agargaon", "type": "place"},
        "S": {"name": "Baridhara Park", "type": "place"},
        "T": {"name": "Jatrabari Crossing", "type": "place"},
        "1": {"name": "Dhanmondi Pet Hospital", "address": "House 12, Road 7, Dhanmondi, Dhaka", "phone": "02-1234567", "emergency": True, "hours": "24/7", "type": "clinic"},
        "2": {"name": "Banani Animal Clinic", "address": "Road 11, Banani, Dhaka", "phone": "02-2345678", "emergency": False, "hours": "8AM-6PM", "type": "clinic"},
        "3": {"name": "Gulshan Veterinary Center", "address": "Gulshan Ave, Dhaka", "phone": "02-3456789", "emergency": True, "hours": "24/7", "type": "clinic"},
        "4": {"name": "Mirpur Pet Care", "address": "Section 10, Mirpur, Dhaka", "phone": "02-4567890", "emergency": False, "hours": "9AM-7PM", "type": "clinic"},
        "5": {"name": "Motijheel Animal Hospital", "address": "Motijheel, Dhaka", "phone": "02-5678901", "emergency": True, "hours": "24/7", "type": "clinic"},
        "6": {"name": "Apollo Veterinary Hospital", "address": "Baridhara, Dhaka", "phone": "02-6789012", "emergency": True, "hours": "24/7", "type": "clinic"},
        "7": {"name": "Central Veterinary Hospital", "address": "Kazi Nazrul Islam Ave, Dhaka", "phone": "02-7890123", "emergency": True, "hours": "24/7", "type": "clinic"},
        "8": {"name": "Uttara Pet Clinic", "address": "Uttara, Dhaka", "phone": "02-8901234", "emergency": False, "hours": "9AM-8PM", "type": "clinic"},
        "9": {"name": "Green Road Animal Hospital", "address": "Green Road, Dhaka", "phone": "02-9012345", "emergency": True, "hours": "24/7", "type": "clinic"},
        "10": {"name": "Shantinagar Vet Clinic", "address": "Shantinagar, Dhaka", "phone": "02-9123456", "emergency": False, "hours": "8AM-6PM", "type": "clinic"},
        "11": {"name": "Mohammadpur Animal Care", "address": "Mohammadpur, Dhaka", "phone": "02-9234567", "emergency": True, "hours": "24/7", "type": "clinic"},
        "12": {"name": "Khilgaon Pet Hospital", "address": "Khilgaon, Dhaka", "phone": "02-9345678", "emergency": False, "hours": "9AM-7PM", "type": "clinic"},
        "13": {"name": "Tejgaon Veterinary Clinic", "address": "Tejgaon, Dhaka", "phone": "02-9456789", "emergency": True, "hours": "24/7", "type": "clinic"},
        "14": {"name": "Badda Animal Hospital", "address": "Badda, Dhaka", "phone": "02-9567890", "emergency": False, "hours": "8AM-6PM", "type": "clinic"},
        "15": {"name": "Rampura Vet Clinic", "address": "Rampura, Dhaka", "phone": "02-9678901", "emergency": True, "hours": "24/7", "type": "clinic"},
        "16": {"name": "Dakkhinkhan Pet Hospital", "address": "Dakkhinkhan, Dhaka", "phone": "02-9789012", "emergency": False, "hours": "9AM-8PM", "type": "clinic"},
        "17": {"name": "Wari Animal Clinic", "address": "Wari, Dhaka", "phone": "02-9890123", "emergency": True, "hours": "24/7", "type": "clinic"},
        "18": {"name": "Azimpur Veterinary Center", "address": "Azimpur, Dhaka", "phone": "02-9901234", "emergency": False, "hours": "8AM-6PM", "type": "clinic"},
        "19": {"name": "Kurmitola Veterinary Hospital", "address": "Kurmitola, Dhaka", "phone": "02-9912345", "emergency": True, "hours": "24/7", "type": "clinic"},
        "20": {"name": "Purbachal Pet Clinic", "address": "Purbachal, Dhaka", "phone": "02-9923456", "emergency": False, "hours": "9AM-7PM", "type": "clinic"},
        "21": {"name": "Kamalapur Animal Hospital", "address": "Kamalapur, Dhaka", "phone": "02-9934567", "emergency": True, "hours": "24/7", "type": "clinic"},
        "22": {"name": "Agargaon Pet Hospital", "address": "Agargaon, Dhaka", "phone": "02-9945678", "emergency": False, "hours": "8AM-6PM", "type": "clinic"},
        "23": {"name": "Jatrabari Vet Clinic", "address": "Jatrabari, Dhaka", "phone": "02-9956789", "emergency": True, "hours": "24/7", "type": "clinic"},
        "24": {"name": "Demra Animal Care", "address": "Demra, Dhaka", "phone": "02-9967890", "emergency": False, "hours": "9AM-8PM", "type": "clinic"},
        "25": {"name": "Savar Veterinary Hospital", "address": "Savar, Dhaka", "phone": "02-9978901", "emergency": True, "hours": "24/7", "type": "clinic"},
        "26": {"name": "Keraniganj Pet Clinic", "address": "Keraniganj, Dhaka", "phone": "02-9989012", "emergency": False, "hours": "8AM-6PM", "type": "clinic"},
        "27": {"name": "Banasree Animal Hospital", "address": "Banasree, Dhaka", "phone": "02-9990123", "emergency": True, "hours": "24/7", "type": "clinic"},
        "28": {"name": "Dania Veterinary Center", "address": "Dania, Dhaka", "phone": "02-9991234", "emergency": False, "hours": "9AM-7PM", "type": "clinic"},
    }
    # Define edges and weights (example, you must expand this for your real map)
    edges = [
        ("A", "B", 2), ("A", "C", 3), ("A", "G", 2), ("A", "L", 2),
        ("B", "C", 1), ("B", "F", 4), ("B", "Q", 2),
        ("C", "D", 2), ("C", "H", 1), ("C", "L", 2), ("C", "1", 4),
        ("D", "1", 3), ("D", "N", 2), ("D", "G", 2),
        ("E", "8", 2), ("E", "F", 3), ("E", "O", 2),
        ("F", "2", 5), ("F", "M", 2), ("F", "Q", 2),
        ("G", "L", 1), ("G", "N", 3),
        ("H", "K", 2), ("H", "C", 1),
        ("I", "T", 2), ("I", "5", 3),
        ("J", "R", 2), ("J", "B", 3),
        ("K", "M", 2), ("K", "H", 2),
        ("L", "G", 1), ("L", "C", 2),
        ("M", "F", 2), ("M", "K", 2),
        ("N", "D", 2), ("N", "O", 2),
        ("O", "E", 2), ("O", "N", 2), ("O", "4", 3),
        ("P", "1", 2), ("P", "L", 2),
        ("Q", "2", 2), ("Q", "F", 2),
        ("R", "J", 2), ("R", "22", 3),
        ("S", "6", 2), ("S", "3", 2),
        ("T", "23", 2), ("T", "I", 2),
        ("1", "P", 2), ("1", "C", 4), ("1", "D", 3),
        ("2", "Q", 2), ("2", "F", 5),
        ("3", "S", 2), ("3", "6", 2),
        ("4", "O", 3),
        ("5", "I", 3),
        ("6", "S", 2), ("6", "3", 2),
        ("7", "H", 2), ("7", "K", 2),
        ("8", "E", 2),
        ("9", "L", 2),
        ("10", "M", 2),
        ("11", "N", 2),
        ("12", "M", 2),
        ("13", "K", 2),
        ("14", "Q", 2),
        ("15", "M", 2),
        ("16", "O", 2),
        ("17", "I", 2),
        ("18", "G", 2),
        ("19", "R", 2),
        ("20", "S", 2),
        ("21", "T", 2),
        ("22", "R", 3),
        ("23", "T", 2),
        ("24", "T", 3),
        ("25", "O", 4),
        ("26", "G", 4),
        ("27", "M", 3),
        ("28", "T", 3)
    ]
    graph = Graph()
    for node_id, node_data in sample_locations.items():
        graph.add_vertex(node_id, node_data)
    for from_id, to_id, weight in edges:
        graph.add_edge(from_id, to_id, weight)
        graph.add_edge(to_id, from_id, weight)  # if undirected
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
