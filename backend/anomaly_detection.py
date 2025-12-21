# backend/anomaly_detection.py
"""
Geospatial Anomaly Detection for MediTrace
Detects impossible travel speeds (potential cloning attacks)
"""

from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two points on Earth
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in kilometers
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    return distance


def calculate_travel_speed(loc1, loc2, time1, time2):
    """
    Calculate speed between two locations
    
    Returns:
        Speed in km/h
    """
    # Calculate distance
    distance_km = haversine_distance(
        loc1['lat'], loc1['lon'],
        loc2['lat'], loc2['lon']
    )
    
    # Calculate time difference
    if isinstance(time1, str):
        time1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
    if isinstance(time2, str):
        time2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
    
    time_diff_seconds = (time2 - time1).total_seconds()
    time_diff_hours = time_diff_seconds / 3600
    
    # Avoid division by zero
    if time_diff_hours == 0:
        return float('inf')
    
    speed_kmh = distance_km / time_diff_hours
    return speed_kmh


def detect_cloning_attempt(supply_chain_events):
    """
    Analyze supply chain events for impossible travel speeds
    
    Args:
        supply_chain_events: List of events with location and timestamp
    
    Returns:
        List of detected anomalies
    """
    anomalies = []
    
    # Need at least 2 events to compare
    if len(supply_chain_events) < 2:
        return anomalies
    
    for i in range(1, len(supply_chain_events)):
        prev_event = supply_chain_events[i-1]
        curr_event = supply_chain_events[i]
        
        # Extract coordinates
        loc1 = {'lat': prev_event['latitude'], 'lon': prev_event['longitude']}
        loc2 = {'lat': curr_event['latitude'], 'lon': curr_event['longitude']}
        
        # Calculate distance and speed
        distance = haversine_distance(loc1['lat'], loc1['lon'], loc2['lat'], loc2['lon'])
        speed = calculate_travel_speed(loc1, loc2, prev_event['timestamp'], curr_event['timestamp'])
        
        # Define thresholds
        MAX_COMMERCIAL_FLIGHT_SPEED = 900  # km/h
        MAX_GROUND_SPEED = 120  # km/h for trucks
        
        # Flag suspicious speeds
        if speed > MAX_COMMERCIAL_FLIGHT_SPEED:
            anomalies.append({
                'type': 'CLONING_SUSPECTED',
                'severity': 'CRITICAL',
                'reason': f'Impossible travel speed detected',
                'details': {
                    'from_location': prev_event['location'],
                    'to_location': curr_event['location'],
                    'distance_km': round(distance, 2),
                    'time_diff_hours': round((datetime.strptime(curr_event['timestamp'], '%Y-%m-%d %H:%M:%S') - 
                                            datetime.strptime(prev_event['timestamp'], '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600, 2),
                    'calculated_speed_kmh': round(speed, 2),
                    'max_allowed_speed': MAX_COMMERCIAL_FLIGHT_SPEED
                },
                'recommendation': 'Flag for manual investigation - Potential product cloning'
            })
        
        elif speed > MAX_GROUND_SPEED and distance > 50:
            # Suspicious but not impossible (could be air freight)
            anomalies.append({
                'type': 'UNUSUAL_SPEED',
                'severity': 'MEDIUM',
                'reason': f'Unusually fast ground transport',
                'details': {
                    'from_location': prev_event['location'],
                    'to_location': curr_event['location'],
                    'distance_km': round(distance, 2),
                    'calculated_speed_kmh': round(speed, 2),
                    'note': 'Could be air freight - verify transport mode'
                },
                'recommendation': 'Verify transport documentation'
            })
    
    return anomalies


def check_scan_frequency(drug_id, time_window_hours=1):
    """
    Detect suspicious scan patterns (too many scans in short time)
    
    Args:
        drug_id: ID of drug to check
        time_window_hours: Time window to analyze
    
    Returns:
        Alert dict if suspicious, None otherwise
    """
    import sqlite3
    
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    # Count recent scans
    cursor.execute('''
        SELECT COUNT(*) 
        FROM supply_chain 
        WHERE drug_id = ? 
        AND timestamp > datetime('now', '-' || ? || ' hours')
    ''', (drug_id, time_window_hours))
    
    scan_count = cursor.fetchone()[0]
    conn.close()
    
    # Flag if more than 10 scans in 1 hour
    SUSPICIOUS_THRESHOLD = 10
    
    if scan_count > SUSPICIOUS_THRESHOLD:
        return {
            'alert': 'SUSPICIOUS_SCAN_FREQUENCY',
            'severity': 'HIGH',
            'scan_count': scan_count,
            'time_window_hours': time_window_hours,
            'message': f'Drug scanned {scan_count} times in {time_window_hours} hour(s)',
            'recommendation': 'Potential photocopy attack - Investigate immediately'
        }
    
    return None


def analyze_drug_safety(unique_id):
    """
    Comprehensive safety analysis for a drug
    
    Returns:
        Safety report with all detected issues
    """
    import sqlite3
    
    conn = sqlite3.connect('meditrace.db')
    cursor = conn.cursor()
    
    # Get drug ID
    cursor.execute('SELECT id FROM drugs WHERE unique_id = ?', (unique_id,))
    result = cursor.fetchone()
    
    if not result:
        return {'error': 'Drug not found'}
    
    drug_id = result[0]
    
    # Get supply chain events
    cursor.execute('''
        SELECT location, latitude, longitude, event_type, timestamp
        FROM supply_chain
        WHERE drug_id = ?
        ORDER BY timestamp ASC
    ''', (drug_id,))
    
    events = []
    for row in cursor.fetchall():
        events.append({
            'location': row[0],
            'latitude': row[1],
            'longitude': row[2],
            'event_type': row[3],
            'timestamp': row[4]
        })
    
    conn.close()
    
    # Run all checks
    cloning_anomalies = detect_cloning_attempt(events)
    scan_frequency_alert = check_scan_frequency(drug_id)
    
    # Compile report
    report = {
        'unique_id': unique_id,
        'analysis_timestamp': datetime.now().isoformat(),
        'total_events': len(events),
        'cloning_alerts': cloning_anomalies,
        'scan_frequency_alert': scan_frequency_alert,
        'overall_status': 'SAFE' if not cloning_anomalies and not scan_frequency_alert else 'SUSPICIOUS',
        'risk_level': 'LOW' if not cloning_anomalies and not scan_frequency_alert else 
                     'CRITICAL' if cloning_anomalies else 'MEDIUM'
    }
    
    return report


# ═══════════════════════════════════════════════════════
# DEMO FUNCTIONS FOR VIVA
# ═══════════════════════════════════════════════════════

def demo_haversine():
    """Demonstrate Haversine calculation"""
    # Mumbai to Delhi
    mumbai = (19.0760, 72.8777)
    delhi = (28.7041, 77.1025)
    
    distance = haversine_distance(*mumbai, *delhi)
    print(f"📍 Mumbai to Delhi distance: {distance:.2f} km")
    
    # If traveled in 10 minutes
    speed = (distance / 10) * 60
    print(f"⚡ Speed if traveled in 10 mins: {speed:.2f} km/h")
    print(f"🚨 Max airplane speed: 900 km/h")
    
    if speed > 900:
        print("❌ CLONING DETECTED - Impossible speed!")
    else:
        print("✅ Travel speed is plausible")


if __name__ == '__main__':
    print("🔍 Testing Anomaly Detection System...\n")
    demo_haversine()