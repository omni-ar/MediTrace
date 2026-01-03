"""
Feature Extractor for Random Forest Counterfeit Detection

Extracts 10 features from drug data:
- 2 visual features (from YOLOv8)
- 8 behavioral features (from supply chain + database)
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from anomaly_detection import haversine_distance


def extract_features(drug_id, supply_chain, yolo_features=None):
    """
    Extract all 10 features for a drug
    
    Args:
        drug_id: Drug ID from database (integer)
        supply_chain: List of supply chain event dicts
        yolo_features: Optional dict from YOLO detection
                      {'packaging_present': 0/1, 'packaging_confidence': 0.0-1.0}
    
    Returns:
        dict: Feature dictionary with 10 keys
    """
    
    features = {}
    
    # ========================================
    # VISUAL FEATURES (from YOLOv8)
    # ========================================
    
    if yolo_features:
        # Feature 1: Packaging detected (binary)
        features['packaging_present'] = int(yolo_features.get('packaging_present', 0))
        
        # Feature 2: Detection confidence (float 0-1)
        features['packaging_confidence'] = float(yolo_features.get('packaging_confidence', 0.0))
    else:
        # No image provided - assume packaging present (for text-only verification)
        features['packaging_present'] = 1
        features['packaging_confidence'] = 0.8  # Default neutral confidence
    
    # ========================================
    # BEHAVIORAL FEATURES (from supply chain)
    # ========================================
    
    # Feature 3: Maximum travel speed (km/h)
    max_speed = 0.0
    
    if len(supply_chain) >= 2:
        for i in range(1, len(supply_chain)):
            prev = supply_chain[i-1]
            curr = supply_chain[i]
            
            try:
                # Calculate distance between locations
                distance = haversine_distance(
                    prev['latitude'], prev['longitude'],
                    curr['latitude'], curr['longitude']
                )
                
                # Calculate time difference in hours
                time1 = datetime.fromisoformat(prev['timestamp'].replace(' ', 'T'))
                time2 = datetime.fromisoformat(curr['timestamp'].replace(' ', 'T'))
                time_diff = (time2 - time1).total_seconds() / 3600  # Convert to hours
                
                # Calculate speed (km/h)
                if time_diff > 0:
                    speed = distance / time_diff
                    max_speed = max(max_speed, speed)
                    
            except (ValueError, KeyError, ZeroDivisionError) as e:
                # Handle parsing errors gracefully
                continue
    
    features['max_speed_kmh'] = float(max_speed)
    
    # Feature 4: Total number of supply chain locations
    features['total_locations'] = len(supply_chain)
    
    # Feature 5: Location deviation from expected
    # Expected: Factory(1) → Quality Check(2) → Warehouse(3) → Retail(4) = 4 locations
    expected_locations = 4
    features['location_deviation'] = abs(len(supply_chain) - expected_locations)
    
    # Feature 6: Total time elapsed (hours)
    total_hours = 0.0
    if len(supply_chain) >= 2:
        try:
            first_time = datetime.fromisoformat(supply_chain[0]['timestamp'].replace(' ', 'T'))
            last_time = datetime.fromisoformat(supply_chain[-1]['timestamp'].replace(' ', 'T'))
            total_hours = (last_time - first_time).total_seconds() / 3600
        except (ValueError, KeyError):
            total_hours = 0.0
    
    features['total_time_hours'] = float(total_hours)
    
    # Feature 7: Weekend scan detection (suspicious)
    weekend_scan = 0
    if len(supply_chain) > 0:
        try:
            last_time = datetime.fromisoformat(supply_chain[-1]['timestamp'].replace(' ', 'T'))
            # weekday(): Monday=0, Sunday=6
            weekend_scan = 1 if last_time.weekday() >= 5 else 0
        except (ValueError, KeyError):
            weekend_scan = 0
    
    features['weekend_scan'] = weekend_scan
    
    # ========================================
    # DATABASE FEATURES
    # ========================================
    
    db_path = Path(__file__).parent.parent / 'meditrace.db'
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get drug details
        cursor.execute(
            'SELECT manufacturer, license_number, mrp FROM drugs WHERE id = ?',
            (drug_id,)
        )
        row = cursor.fetchone()
        
        if row:
            manufacturer, license, mrp = row
            
            # Feature 8: License valid (non-empty and not null)
            features['license_valid'] = 1 if (license and len(license.strip()) > 0) else 0
            
            # Feature 9: Price valid (MRP > 0)
            features['price_valid'] = 1 if (mrp and mrp > 0) else 0
        else:
            # Drug not found in database
            features['license_valid'] = 0
            features['price_valid'] = 0
        
        # Feature 10: Recent failed attempts for similar drug IDs
        # Get unique_id pattern (batch prefix)
        cursor.execute('SELECT unique_id FROM drugs WHERE id = ?', (drug_id,))
        unique_row = cursor.fetchone()
        
        if unique_row:
            unique_id = unique_row[0]
            # Extract batch prefix (e.g., "ABC12345" from "ABC12345-1")
            batch_prefix = unique_id.split('-')[0] if '-' in unique_id else unique_id
            
            # Count failed attempts for this batch in last 30 days
            cursor.execute('''
                SELECT COUNT(*) FROM failed_attempts 
                WHERE scanned_id LIKE ? 
                AND timestamp > datetime('now', '-30 days')
            ''', (f"%{batch_prefix}%",))
            
            count = cursor.fetchone()[0]
            features['recent_failures'] = int(count)
        else:
            features['recent_failures'] = 0
        
        conn.close()
        
    except Exception as e:
        # Database error - use safe defaults
        print(f"Warning: Database error in feature extraction: {e}")
        features['license_valid'] = 0
        features['price_valid'] = 0
        features['recent_failures'] = 0
    
    return features


def features_to_vector(features):
    """
    Convert feature dict to ordered list for sklearn
    
    Args:
        features: Dict with 10 feature keys
    
    Returns:
        list: Ordered feature values [f1, f2, ..., f10]
    """
    
    return [
        features['packaging_present'],
        features['packaging_confidence'],
        features['max_speed_kmh'],
        features['total_locations'],
        features['location_deviation'],
        features['total_time_hours'],
        features['weekend_scan'],
        features['license_valid'],
        features['price_valid'],
        features['recent_failures']
    ]


# Feature names for reference (must match order in features_to_vector)
FEATURE_NAMES = [
    'packaging_present',      # 0: Binary (0/1)
    'packaging_confidence',   # 1: Float (0.0-1.0)
    'max_speed_kmh',          # 2: Float (0-10000+)
    'total_locations',        # 3: Int (1-10)
    'location_deviation',     # 4: Int (0-5)
    'total_time_hours',       # 5: Float (0-1000+)
    'weekend_scan',           # 6: Binary (0/1)
    'license_valid',          # 7: Binary (0/1)
    'price_valid',            # 8: Binary (0/1)
    'recent_failures'         # 9: Int (0-100+)
]


# =============================================================================
# DEMO / TESTING
# =============================================================================

if __name__ == '__main__':
    print("="*60)
    print("🧪 FEATURE EXTRACTOR - DEMO")
    print("="*60)
    
    # Test case 1: Authentic drug
    print("\n📦 Test Case 1: AUTHENTIC DRUG")
    print("-" * 60)
    
    authentic_supply_chain = [
        {
            'location': 'Bangalore Factory',
            'latitude': 12.9716,
            'longitude': 77.5946,
            'timestamp': '2024-12-29 10:00:00'
        },
        {
            'location': 'Mumbai Warehouse',
            'latitude': 19.0760,
            'longitude': 72.8777,
            'timestamp': '2024-12-30 12:00:00'  # 26 hours later
        },
        {
            'location': 'Delhi Retail',
            'latitude': 28.7041,
            'longitude': 77.1025,
            'timestamp': '2024-12-31 15:00:00'  # 27 hours later
        }
    ]
    
    yolo_good = {
        'packaging_present': 1,
        'packaging_confidence': 0.95
    }
    
    features_authentic = extract_features(
        drug_id=1,
        supply_chain=authentic_supply_chain,
        yolo_features=yolo_good
    )
    
    print("\n✅ Extracted Features:")
    for name, value in features_authentic.items():
        print(f"   {name:25s}: {value}")
    
    print(f"\n📊 Feature Vector:")
    print(f"   {features_to_vector(features_authentic)}")
    
    # Test case 2: Counterfeit drug (cloned QR)
    print("\n\n🚨 Test Case 2: COUNTERFEIT DRUG (Cloned QR)")
    print("-" * 60)
    
    fake_supply_chain = [
        {
            'location': 'Mumbai',
            'latitude': 19.0760,
            'longitude': 72.8777,
            'timestamp': '2024-12-29 10:00:00'
        },
        {
            'location': 'Delhi',
            'latitude': 28.7041,
            'longitude': 77.1025,
            'timestamp': '2024-12-29 10:10:00'  # Only 10 minutes! Impossible!
        }
    ]
    
    yolo_suspicious = {
        'packaging_present': 0,  # No packaging detected
        'packaging_confidence': 0.35
    }
    
    features_fake = extract_features(
        drug_id=999,  # Assume doesn't exist
        supply_chain=fake_supply_chain,
        yolo_features=yolo_suspicious
    )
    
    print("\n❌ Extracted Features:")
    for name, value in features_fake.items():
        print(f"   {name:25s}: {value}")
    
    print(f"\n📊 Feature Vector:")
    print(f"   {features_to_vector(features_fake)}")
    
    # Calculate the impossible speed
    distance = haversine_distance(19.0760, 72.8777, 28.7041, 77.1025)
    time_hours = 10 / 60  # 10 minutes
    speed = distance / time_hours
    
    print(f"\n🔍 Speed Analysis:")
    print(f"   Distance: {distance:.2f} km")
    print(f"   Time: {time_hours:.4f} hours (10 minutes)")
    print(f"   Speed: {speed:.2f} km/h (IMPOSSIBLE! Max plane = 900 km/h)")
    
    print("\n" + "="*60)
    print("✅ Feature Extractor Demo Complete!")
    print("="*60)