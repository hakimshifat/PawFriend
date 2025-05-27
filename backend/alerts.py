import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

ALERTS_FILE = 'data/alerts.json'
NOTIFICATIONS_FILE = 'data/notifications.json'


ALERT_CATEGORIES = {
    'LOST_PET': 'Lost Pet',
    'FOUND_PET': 'Found Pet',
    'EMERGENCY': 'Emergency',
    'SUSPICIOUS_ACTIVITY': 'Suspicious Activity',
    'COMMUNITY_ALERT': 'Community Alert'
}


PRIORITY_LEVELS = {
    1: 'Critical',
    2: 'High',
    3: 'Medium',
    4: 'Low'
}


ALERT_STATUSES = {
    'ACTIVE': 'Active',
    'RESOLVED': 'Resolved',
    'EXPIRED': 'Expired',
    'VERIFIED': 'Verified'
}

def load_alerts() -> List[Dict]:
    if not os.path.exists(ALERTS_FILE):
        return []
    with open(ALERTS_FILE, 'r') as f:
        return json.load(f)

def save_alerts(alerts: List[Dict]) -> None:
    os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)

def load_notifications() -> Dict[str, List[Dict]]:
    if not os.path.exists(NOTIFICATIONS_FILE):
        return {}
    with open(NOTIFICATIONS_FILE, 'r') as f:
        return json.load(f)

def save_notifications(notifications: Dict[str, List[Dict]]) -> None:
    os.makedirs(os.path.dirname(NOTIFICATIONS_FILE), exist_ok=True)
    with open(NOTIFICATIONS_FILE, 'w') as f:
        json.dump(notifications, f, indent=2)

def create_notification(username: str, alert_id: int, message: str, notification_type: str) -> Dict:
    notifications = load_notifications()
    if username not in notifications:
        notifications[username] = []
    
    notification = {
        "id": len(notifications[username]) + 1,
        "alert_id": alert_id,
        "message": message,
        "type": notification_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "read": False
    }
    
    notifications[username].append(notification)
    save_notifications(notifications)
    return notification

def get_user_notifications(username: str, unread_only: bool = False) -> List[Dict]:
    notifications = load_notifications()
    user_notifications = notifications.get(username, [])
    if unread_only:
        return [n for n in user_notifications if not n["read"]]
    return user_notifications

def mark_notification_read(username: str, notification_id: int) -> bool:
    notifications = load_notifications()
    if username in notifications:
        for notification in notifications[username]:
            if notification["id"] == notification_id:
                notification["read"] = True
                save_notifications(notifications)
                return True
    return False

def add_alert(
    username: str,
    pet_type: str,
    description: str,
    location: List[float],
    category: str,
    priority: int = 3,
    media_url: Optional[str] = None,
    expiration_days: int = 30
) -> Dict:
    alerts = load_alerts()
    
    
    if category not in ALERT_CATEGORIES:
        raise ValueError(f"Invalid category. Must be one of: {', '.join(ALERT_CATEGORIES.keys())}")
    
    
    if priority not in PRIORITY_LEVELS:
        raise ValueError(f"Invalid priority level. Must be between 1-4")

    
    expires_at = (datetime.now() + timedelta(days=expiration_days)).isoformat()

    alert = {
        "id": len(alerts) + 1,
        "username": username,
        "pet_type": pet_type,
        "description": description,
        "location": location,
        "category": category,
        "priority": priority,
        "status": "ACTIVE",
        "media_url": media_url,
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at,  
        "responses": [],
        "subscribers": [username],
        "verification_count": 0,
        "tags": extract_tags(description)
    }
    
    alerts.append(alert)
    save_alerts(alerts)
    
    
    if priority <= 2:
        notify_nearby_users(alert)
    
    return alert

def extract_tags(description: str) -> List[str]:
    words = description.lower().split()
    hashtags = [word[1:] for word in words if word.startswith('#')]
    
    
    keywords = ['lost', 'found', 'missing', 'injured', 'emergency', 'urgent', 'help']
    extracted_keywords = [word for word in words if word in keywords]
    
    return list(set(hashtags + extracted_keywords))

def notify_nearby_users(alert: Dict) -> None:
    alerts = load_alerts()
    alert_location = alert["location"]
    
    
    nearby_users = set()
    for existing_alert in alerts:
        if existing_alert["id"] != alert["id"]:
            distance = calculate_distance(alert_location, existing_alert["location"])
            if distance <= 5:  
                nearby_users.add(existing_alert["username"])
    
    
    message = f"New {PRIORITY_LEVELS[alert['priority']]} priority alert in your area: {alert['description'][:100]}..."
    for username in nearby_users:
        create_notification(username, alert["id"], message, "NEARBY_ALERT")

def calculate_distance(loc1: List[float], loc2: List[float]) -> float:
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  
    lat1, lon1 = radians(loc1[0]), radians(loc1[1])
    lat2, lon2 = radians(loc2[0]), radians(loc2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def update_alert_status(alert_id: int, new_status: str) -> bool:
    if new_status not in ALERT_STATUSES:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(ALERT_STATUSES.keys())}")
    
    alerts = load_alerts()
    for alert in alerts:
        if alert["id"] == alert_id:
            old_status = alert["status"]
            alert["status"] = new_status
            save_alerts(alerts)
            
            
            message = f"Alert status changed from {old_status} to {new_status}"
            for subscriber in alert["subscribers"]:
                create_notification(subscriber, alert_id, message, "STATUS_UPDATE")
            
            return True
    return False

def verify_alert(alert_id: int, username: str) -> bool:
    alerts = load_alerts()
    for alert in alerts:
        if alert["id"] == alert_id:
            if username not in alert.get("verifiers", []):
                alert["verifiers"] = alert.get("verifiers", []) + [username]
                alert["verification_count"] = len(alert["verifiers"])
                
                
                if alert["verification_count"] >= 3 and alert["status"] == "ACTIVE":
                    alert["status"] = "VERIFIED"
                    
                    create_notification(
                        alert["username"],
                        alert_id,
                        f"Your alert has been verified by {alert['verification_count']} users",
                        "VERIFICATION"
                    )
                
                save_alerts(alerts)
                return True
    return False

def add_response(alert_id: int, username: str, response_text: str, contact_info: Optional[str] = None) -> bool:
    alerts = load_alerts()
    for alert in alerts:
        if alert["id"] == alert_id:
            response = {
                "username": username,
                "text": response_text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "contact_info": contact_info
            }
            alert["responses"] = alert.get("responses", []) + [response]
            save_alerts(alerts)
            
            
            message = f"New response from {username}: {response_text[:100]}..."
            create_notification(alert["username"], alert_id, message, "NEW_RESPONSE")
            for subscriber in alert["subscribers"]:
                if subscriber != username and subscriber != alert["username"]:
                    create_notification(subscriber, alert_id, message, "NEW_RESPONSE")
            
            return True
    return False

def subscribe_to_alert(alert_id: int, username: str) -> bool:
    alerts = load_alerts()
    for alert in alerts:
        if alert["id"] == alert_id:
            if username not in alert["subscribers"]:
                alert["subscribers"].append(username)
                save_alerts(alerts)
                return True
    return False

def get_active_alerts(
    max_distance_km: Optional[float] = None,
    location: Optional[List[float]] = None,
    tags: Optional[List[str]] = None,
    min_priority: Optional[int] = None
) -> List[Dict]:
    all_alerts = load_alerts()
    current_time = datetime.now()
    
    filtered_alerts = []
    for alert in all_alerts:
        
        if "expires_at" in alert:
            try:
                expiration = datetime.fromisoformat(alert["expires_at"])
                if expiration <= current_time:
                    continue
            except (ValueError, TypeError):
                
                pass
        
        
        if alert.get("status", "ACTIVE") != "ACTIVE":
            continue
            
        
        if min_priority and alert.get("priority", 3) < min_priority:
            continue
            
        
        if tags and not any(tag in alert.get("tags", []) for tag in tags):
            continue
            
        
        if max_distance_km and location:
            alert_location = alert.get("location")
            if alert_location:
                distance = calculate_distance(location, alert_location)
                if distance > max_distance_km:
                    continue
                alert["distance"] = round(distance, 1)
        
        filtered_alerts.append(alert)
    
    return filtered_alerts

def get_alerts_by_category(category: str) -> List[Dict]:
    if category not in ALERT_CATEGORIES:
        raise ValueError(f"Invalid category. Must be one of: {', '.join(ALERT_CATEGORIES.keys())}")
    
    alerts = load_alerts()
    return [alert for alert in alerts if alert["category"] == category]

def get_user_alerts(username: str) -> List[Dict]:
    alerts = load_alerts()
    return [alert for alert in alerts if alert["username"] == username]

def get_subscribed_alerts(username: str) -> List[Dict]:
    alerts = load_alerts()
    return [alert for alert in alerts if username in alert["subscribers"]]

def search_alerts(query: str) -> List[Dict]:
    alerts = load_alerts()
    query = query.lower()
    
    return [
        alert for alert in alerts
        if (
            query in alert["description"].lower()
            or query in alert["pet_type"].lower()
            or any(query in tag for tag in alert.get("tags", []))
        )
    ]

def get_alert_statistics():
    alerts = load_alerts()
    stats = {
        'total': len(alerts),
        'active': 0,
        'resolved': 0,
        'expired': 0,
        'verified': 0,
        'by_category': {},
        'by_priority': {1: 0, 2: 0, 3: 0, 4: 0},
        'total_responses': 0,
        'alerts_with_responses': 0,
        'response_rate': 0.0  
    }
    
    for alert in alerts:
        
        status = alert.get('status', 'ACTIVE')
        
        
        if status == 'ACTIVE':
            stats['active'] += 1
        elif status == 'RESOLVED':
            stats['resolved'] += 1
        elif status == 'EXPIRED':
            stats['expired'] += 1
        elif status == 'VERIFIED':
            stats['verified'] += 1
            
        
        category = alert.get('category', 'COMMUNITY_ALERT')
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        
        priority = alert.get('priority', 3)
        stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        
        responses = alert.get('responses', [])
        stats['total_responses'] += len(responses)
        if len(responses) > 0:
            stats['alerts_with_responses'] += 1
    
    
    if stats['total'] > 0:
        stats['response_rate'] = (stats['alerts_with_responses'] / stats['total']) * 100
        stats['verification_rate'] = (stats['verified'] / stats['total']) * 100  
    else:
        stats['verification_rate'] = 0.0  

    return stats
