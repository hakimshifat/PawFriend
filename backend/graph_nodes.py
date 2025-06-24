# Utility to get all graph nodes for dropdowns
from backend.emergency_locator import create_clinic_graph

def get_graph_nodes():
    _, clinics = create_clinic_graph()
    return [
        {'id': str(cid), 'name': cdata['name']}
        for cid, cdata in clinics.items()
    ]
