"""
Generate Synthetic Training Data for Random Forest

Creates realistic examples of:
- Authentic drugs (normal supply chain patterns)
- Counterfeit drugs (suspicious patterns)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from feature_extractor import features_to_vector, FEATURE_NAMES

# Set random seed for reproducibility
np.random.seed(42)


def generate_training_data():
    """
    Generate synthetic training dataset
    
    Returns:
        pandas.DataFrame with features + label
    """
    
    print("="*60)
    print("📊 GENERATING TRAINING DATA")
    print("="*60)
    
    data = []
    
    # ========================================
    # AUTHENTIC EXAMPLES (Class 0)
    # ========================================
    
    print("\n✅ Generating AUTHENTIC examples...")
    
    # Type 1: Normal supply chain (20 samples)
    for i in range(20):
        features = {
            'packaging_present': 1,  # Packaging detected
            'packaging_confidence': np.random.uniform(0.85, 0.98),  # High confidence
            'max_speed_kmh': np.random.uniform(60, 120),  # Normal truck/train speed
            'total_locations': np.random.choice([3, 4]),  # Expected route
            'location_deviation': np.random.choice([0, 1]),  # Minor deviation acceptable
            'total_time_hours': np.random.uniform(24, 96),  # 1-4 days total
            'weekend_scan': np.random.choice([0, 1], p=[0.7, 0.3]),  # Mostly weekdays
            'license_valid': 1,  # Valid license
            'price_valid': 1,  # Valid MRP
            'recent_failures': 0  # No fraud history
        }
        
        # Convert to vector and add label
        data.append(features_to_vector(features) + [0])  # 0 = authentic
    
    # Type 1b: Near-simultaneous scans (like seed data) - 10 samples
    print("   Type 1b: Near-simultaneous scans (batch production)...")
    for i in range(10):
        features = {
            'packaging_present': 1,
            'packaging_confidence': np.random.uniform(0.85, 0.98),
            'max_speed_kmh': np.random.uniform(0, 50),  # Very low or zero (simultaneous)
            'total_locations': 3,  # Standard 3 checkpoints
            'location_deviation': 1,  # One deviation acceptable
            'total_time_hours': np.random.uniform(0.001, 2),  # Very short (batch creation)
            'weekend_scan': np.random.choice([0, 1], p=[0.7, 0.3]),
            'license_valid': 1,
            'price_valid': 1,
            'recent_failures': 0
        }
        
        data.append(features_to_vector(features) + [0])

    # Type 1c: Production batch (identical timestamps) - 10 samples
    print("   Type 1c: Production batch scenario...")
    for i in range(10):
        features = {
            'packaging_present': 1,
            'packaging_confidence': np.random.uniform(0.88, 0.97),
            'max_speed_kmh': 0.0,  # Zero speed (simultaneous creation)
            'total_locations': 3,  # Standard checkpoints
            'location_deviation': 1,
            'total_time_hours': 0.0,  # Zero time (batch)
            'weekend_scan': 0,
            'license_valid': 1,
            'price_valid': 1,
            'recent_failures': 0
        }
        
        data.append(features_to_vector(features) + [0])  # Authentic!
    
    # Type 2: Fast but legitimate air shipment (10 samples)
    for i in range(10):
        features = {
            'packaging_present': 1,
            'packaging_confidence': np.random.uniform(0.88, 0.96),
            'max_speed_kmh': np.random.uniform(400, 800),  # Airplane speed (legitimate)
            'total_locations': 4,  # All checkpoints
            'location_deviation': 0,  # Perfect route
            'total_time_hours': np.random.uniform(12, 48),  # Faster shipment
            'weekend_scan': 0,  # Business days
            'license_valid': 1,
            'price_valid': 1,
            'recent_failures': 0
        }
        
        data.append(features_to_vector(features) + [0])
    
    print(f"   Created 40 authentic samples")
    
    # ========================================
    # COUNTERFEIT EXAMPLES (Class 1)
    # ========================================
    
    print("\n❌ Generating COUNTERFEIT examples...")
    
    # Type 1: Cloned QR (impossible speed) - 15 samples
    print("   Type 1: Cloned QR attacks...")
    for i in range(15):
        features = {
            'packaging_present': np.random.choice([0, 1], p=[0.3, 0.7]),  # Might have packaging
            'packaging_confidence': np.random.uniform(0.40, 0.85),  # Lower confidence
            'max_speed_kmh': np.random.uniform(1000, 8000),  # IMPOSSIBLE speed!
            'total_locations': 2,  # Only 2 scans (skipped checkpoints)
            'location_deviation': 2,  # Missing locations
            'total_time_hours': np.random.uniform(0.1, 2),  # Very short time
            'weekend_scan': np.random.choice([0, 1]),
            'license_valid': np.random.choice([0, 1]),  # Might be copied
            'price_valid': np.random.choice([0, 1]),
            'recent_failures': np.random.randint(0, 5)  # Some fraud history
        }
        
        data.append(features_to_vector(features) + [1])  # 1 = counterfeit
    
    # Type 2: Missing packaging (visual fake) - 10 samples
    print("   Type 2: Missing/fake packaging...")
    for i in range(10):
        features = {
            'packaging_present': 0,  # NO packaging detected!
            'packaging_confidence': np.random.uniform(0.0, 0.45),  # Very low
            'max_speed_kmh': np.random.uniform(50, 200),  # Speed might be normal
            'total_locations': np.random.choice([2, 3, 4]),
            'location_deviation': np.random.randint(0, 2),
            'total_time_hours': np.random.uniform(12, 48),
            'weekend_scan': np.random.choice([0, 1]),
            'license_valid': 0,  # Invalid license
            'price_valid': 0,  # Invalid price
            'recent_failures': np.random.randint(2, 10)  # High fraud history
        }
        
        data.append(features_to_vector(features) + [1])
    
    # Type 3: Suspicious supply chain pattern - 10 samples
    print("   Type 3: Suspicious patterns...")
    for i in range(10):
        features = {
            'packaging_present': 1,
            'packaging_confidence': np.random.uniform(0.50, 0.75),  # Medium confidence
            'max_speed_kmh': np.random.uniform(200, 600),  # Fast but not impossible
            'total_locations': 2,  # Skipped warehouse (red flag!)
            'location_deviation': 2,  # Missing checkpoints
            'total_time_hours': np.random.uniform(1, 10),  # Too fast
            'weekend_scan': 1,  # Weekend (suspicious for pharma)
            'license_valid': 0,  # No license
            'price_valid': 1,  # Price might be copied
            'recent_failures': np.random.randint(1, 8)
        }
        
        data.append(features_to_vector(features) + [1])
    
    print(f"   Created 35 counterfeit samples")
    
    # ========================================
    # CREATE DATAFRAME
    # ========================================
    
    # Column names: 10 features + label
    columns = FEATURE_NAMES + ['is_counterfeit']
    
    df = pd.DataFrame(data, columns=columns)
    
    # Shuffle the data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # ========================================
    # STATISTICS
    # ========================================
    
    print("\n" + "="*60)
    print("📊 DATASET STATISTICS")
    print("="*60)
    
    total = len(df)
    authentic = (df['is_counterfeit'] == 0).sum()
    counterfeit = (df['is_counterfeit'] == 1).sum()
    
    print(f"\nTotal Samples: {total}")
    print(f"  Authentic:   {authentic} ({authentic/total*100:.1f}%)")
    print(f"  Counterfeit: {counterfeit} ({counterfeit/total*100:.1f}%)")
    
    print(f"\nFeature Statistics:")
    print(df.describe().round(2))
    
    print(f"\nClass Distribution:")
    print(df['is_counterfeit'].value_counts())
    
    # ========================================
    # SAVE TO CSV
    # ========================================
    
    output_path = Path(__file__).parent.parent / 'dataset' / 'rf_training_data.csv'
    output_path.parent.mkdir(exist_ok=True)
    
    df.to_csv(output_path, index=False)
    
    print(f"\n💾 Saved to: {output_path}")
    print("="*60)
    
    return df


# =============================================================================
# DEMO / TESTING
# =============================================================================

if __name__ == '__main__':
    # Generate dataset
    df = generate_training_data()
    
    print("\n✅ Sample Data (First 5 rows):")
    print(df.head())
    
    print("\n✅ Sample Data (Last 5 rows):")
    print(df.tail())
    
    # Show some counterfeit examples with high speed
    print("\n🚨 High-Speed Counterfeit Examples:")
    high_speed = df[df['max_speed_kmh'] > 1000].head(3)
    print(high_speed[['max_speed_kmh', 'total_locations', 'packaging_present', 'is_counterfeit']])
    
    # Show authentic examples
    print("\n✅ Authentic Examples:")
    authentic = df[df['is_counterfeit'] == 0].head(3)
    print(authentic[['max_speed_kmh', 'total_locations', 'packaging_confidence', 'is_counterfeit']])
    
    print("\n" + "="*60)
    print("🎉 Training Data Generation Complete!")
    print("="*60)
    print("\nNext step: Run train_random_forest.py")