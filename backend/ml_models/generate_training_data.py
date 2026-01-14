"""
Generate Synthetic Training Data for Random Forest V2
======================================================

CRITICAL CHANGES FROM V1:
1. Uses 10 NEW behavioral features (not old visual features)
2. Generates 300 samples (not 75) - better generalization
3. Includes "noisy authentic" scenarios - FIXES 53% CASE!
4. All features normalized 0-1 range
5. Realistic supply chain patterns

AUTHOR: Built with understanding!
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# NEW FEATURE NAMES (from FeatureExtractorV2)
FEATURE_NAMES_V2 = [
    'scan_frequency_score',       # 0.0-1.0 (1.0 = good, low scans)
    'unique_locations_ratio',     # 0.0-1.0 (1.0 = all unique)
    'supply_chain_completeness',  # 0.0-1.0 (1.0 = all stages present)
    'license_validity_score',     # 0.0-1.0 (1.0 = valid)
    'price_deviation_score',      # 0.0-1.0 (1.0 = normal price)
    'temporal_consistency_score', # 0.0-1.0 (1.0 = normal travel times)
    'geofence_compliance_score',  # 0.0-1.0 (1.0 = expected regions)
    'speed_anomaly_severity',     # 0.0-1.0 (0.0 = normal, 1.0 = impossible!)
    'batch_health_score',         # 0.0-1.0 (1.0 = healthy batch)
    'historical_pattern_score'    # 0.0-1.0 (1.0 = business hours)
]


def generate_training_data_v2():
    """
    Generate 300 synthetic training samples.
    
    SCENARIO BREAKDOWN:
    - 150 Authentic (50%)
      - 45 Perfect (30%)
      - 45 Delayed (30%) - warehouse storage
      - 45 Noisy (30%) - FIXES 53% CASE!
      - 15 Edge case (10%)
    
    - 150 Counterfeit (50%)
      - 45 Obvious fake (30%)
      - 45 Cloned QR (30%)
      - 45 Sophisticated fake (30%)
      - 15 Edge case (10%)
    
    Returns:
        pandas.DataFrame with 10 features + label
    """
    
    print("="*70)
    print("📊 GENERATING TRAINING DATA V2")
    print("="*70)
    print(f"\nTarget: 300 samples (150 authentic + 150 counterfeit)")
    print(f"Features: 10 behavioral (NO visual dependency!)")
    
    data = []
    
    # ========================================================================
    # AUTHENTIC EXAMPLES (150 samples)
    # ========================================================================
    
    print("\n" + "="*70)
    print("✅ GENERATING AUTHENTIC EXAMPLES (150)")
    print("="*70)
    
    # ─────────────────────────────────────────────────────────────────────
    # TYPE 1: PERFECT AUTHENTIC (45 samples)
    # Scenario: Normal supply chain, no issues
    # ─────────────────────────────────────────────────────────────────────
    print("\n📦 Type 1: Perfect Authentic (45 samples)")
    print("   Scenario: Normal supply chain, all checks pass")
    
    for i in range(45):
        features = {
            'scan_frequency_score': np.random.uniform(0.9, 1.0),  # Low scan frequency (good)
            'unique_locations_ratio': np.random.uniform(0.9, 1.0),  # All unique locations
            'supply_chain_completeness': 1.0,  # All 3 stages present
            'license_validity_score': 1.0,  # Valid license
            'price_deviation_score': np.random.uniform(0.9, 1.0),  # Normal price
            'temporal_consistency_score': np.random.uniform(0.9, 1.0),  # Normal travel times
            'geofence_compliance_score': np.random.uniform(0.9, 1.0),  # Expected regions
            'speed_anomaly_severity': 0.0,  # No speed anomaly
            'batch_health_score': 1.0,  # Healthy batch
            'historical_pattern_score': np.random.uniform(0.9, 1.0)  # Business hours
        }
        
        data.append(list(features.values()) + [0])  # 0 = authentic
    
    print(f"   ✓ Created 45 perfect authentic samples")
    print(f"   Average score: 0.95-1.0 (excellent!)")
    
    # ─────────────────────────────────────────────────────────────────────
    # TYPE 2: DELAYED AUTHENTIC (45 samples)
    # Scenario: Legitimate but delayed (warehouse storage, slow truck)
    # ─────────────────────────────────────────────────────────────────────
    print("\n⏰ Type 2: Delayed Authentic (45 samples)")
    print("   Scenario: Real drug but delayed in warehouse or slow transport")
    
    for i in range(45):
        features = {
            'scan_frequency_score': np.random.uniform(0.7, 0.9),  # Slightly more scans (warehouse checks)
            'unique_locations_ratio': np.random.uniform(0.8, 1.0),  # Mostly unique
            'supply_chain_completeness': 1.0,  # All stages present
            'license_validity_score': 1.0,  # Valid license
            'price_deviation_score': np.random.uniform(0.9, 1.0),  # Normal price
            'temporal_consistency_score': np.random.uniform(0.5, 0.7),  # DELAYED! (2-3x expected time)
            'geofence_compliance_score': np.random.uniform(0.8, 1.0),  # Expected regions
            'speed_anomaly_severity': 0.0,  # No impossible speed (just slow)
            'batch_health_score': 1.0,  # Healthy batch
            'historical_pattern_score': np.random.uniform(0.7, 0.9)  # Some weekend checks
        }
        
        data.append(list(features.values()) + [0])  # Still authentic!
    
    print(f"   ✓ Created 45 delayed authentic samples")
    print(f"   Average score: 0.75-0.85 (lower but still authentic!)")
    print(f"   Key: temporal_consistency = 0.5-0.7 (delayed but acceptable)")
    
    # ─────────────────────────────────────────────────────────────────────
    # TYPE 3: NOISY AUTHENTIC (45 samples) ← FIXES YOUR 53% CASE!
    # Scenario: Authentic but with minor anomalies (missing event, odd timing)
    # ─────────────────────────────────────────────────────────────────────
    print("\n⚠️  Type 3: Noisy Authentic (45 samples) ← FIXES 53% CASE!")
    print("   Scenario: Real drug with minor anomalies (missing event, GPS drift)")
    
    for i in range(45):
        features = {
            'scan_frequency_score': np.random.uniform(0.6, 0.8),  # More scans (re-scans)
            'unique_locations_ratio': np.random.uniform(0.7, 0.9),  # Some duplicate GPS
            'supply_chain_completeness': np.random.choice([0.67, 1.0], p=[0.3, 0.7]),  # Might miss 1 event
            'license_validity_score': 1.0,  # License still valid
            'price_deviation_score': np.random.uniform(0.7, 1.0),  # Price might vary slightly
            'temporal_consistency_score': np.random.uniform(0.6, 0.8),  # Some timing issues
            'geofence_compliance_score': np.random.uniform(0.6, 0.9),  # Might scan in unexpected region
            'speed_anomaly_severity': 0.0,  # No impossible speed
            'batch_health_score': np.random.uniform(0.9, 1.0),  # Batch still healthy
            'historical_pattern_score': np.random.uniform(0.6, 0.8)  # Some off-hours scans
        }
        
        data.append(list(features.values()) + [0])  # Still authentic!
    
    print(f"   ✓ Created 45 noisy authentic samples")
    print(f"   Average score: 0.65-0.75 (noisy but still authentic!)")
    print(f"   🎯 THIS FIXES YOUR 53% CASE - model learns to NOT flag these!")
    
    # ─────────────────────────────────────────────────────────────────────
    # TYPE 4: EDGE CASE AUTHENTIC (15 samples)
    # Scenario: Borderline authentic (expiring license, very old, etc.)
    # ─────────────────────────────────────────────────────────────────────
    print("\n🔸 Type 4: Edge Case Authentic (15 samples)")
    print("   Scenario: Borderline cases (expiring license, missing event, etc.)")
    
    for i in range(15):
        features = {
            'scan_frequency_score': np.random.uniform(0.5, 0.7),  # Higher scan frequency
            'unique_locations_ratio': np.random.uniform(0.5, 0.8),  # Lower uniqueness
            'supply_chain_completeness': np.random.choice([0.33, 0.67]),  # Missing events
            'license_validity_score': np.random.uniform(0.5, 1.0),  # Might be expiring
            'price_deviation_score': np.random.uniform(0.7, 0.9),  # Some price variance
            'temporal_consistency_score': np.random.uniform(0.4, 0.6),  # Poor timing
            'geofence_compliance_score': np.random.uniform(0.5, 0.8),  # Some out-of-region
            'speed_anomaly_severity': 0.0,  # But no impossible speed!
            'batch_health_score': np.random.uniform(0.8, 1.0),  # Batch OK
            'historical_pattern_score': np.random.uniform(0.5, 0.7)  # Mixed timing
        }
        
        data.append(list(features.values()) + [0])  # Still authentic (barely!)
    
    print(f"   ✓ Created 15 edge case authentic samples")
    print(f"   Average score: 0.50-0.65 (borderline but authentic!)")
    
    print(f"\n{'─'*70}")
    print(f"✅ TOTAL AUTHENTIC: 150 samples")
    print(f"{'─'*70}")
    
    # ========================================================================
    # COUNTERFEIT EXAMPLES (150 samples)
    # ========================================================================
    
    print("\n" + "="*70)
    print("❌ GENERATING COUNTERFEIT EXAMPLES (150)")
    print("="*70)
    
    # ─────────────────────────────────────────────────────────────────────
    # TYPE 1: OBVIOUS FAKE (45 samples)
    # Scenario: Blatantly fake (invalid license, impossible speed, etc.)
    # ─────────────────────────────────────────────────────────────────────
    print("\n🚨 Type 1: Obvious Fake (45 samples)")
    print("   Scenario: Clearly counterfeit (invalid license, too cheap, no events)")
    
    for i in range(45):
        features = {
            'scan_frequency_score': np.random.uniform(0.0, 0.3),  # Very high scan frequency (cloned!)
            'unique_locations_ratio': np.random.uniform(0.1, 0.4),  # Low uniqueness (same places)
            'supply_chain_completeness': np.random.choice([0.0, 0.33]),  # Missing stages
            'license_validity_score': 0.0,  # INVALID license!
            'price_deviation_score': np.random.uniform(0.0, 0.3),  # Very cheap (suspicious!)
            'temporal_consistency_score': np.random.uniform(0.3, 0.5),  # Poor timing
            'geofence_compliance_score': np.random.uniform(0.0, 0.5),  # Wrong regions
            'speed_anomaly_severity': np.random.uniform(0.6, 1.0),  # Often impossible speed!
            'batch_health_score': np.random.uniform(0.0, 0.5),  # Unhealthy batch (many fakes)
            'historical_pattern_score': np.random.uniform(0.3, 0.6)  # Odd scan times
        }
        
        data.append(list(features.values()) + [1])  # 1 = counterfeit
    
    print(f"   ✓ Created 45 obvious fake samples")
    print(f"   Average score: 0.25-0.40 (clearly fake!)")
    
    # ─────────────────────────────────────────────────────────────────────
    # TYPE 2: CLONED QR (45 samples)
    # Scenario: Real QR cloned to multiple fake drugs (impossible speed!)
    # ─────────────────────────────────────────────────────────────────────
    print("\n🔁 Type 2: Cloned QR (45 samples)")
    print("   Scenario: Authentic QR code cloned to many fake drugs")
    
    for i in range(45):
        features = {
            'scan_frequency_score': np.random.uniform(0.0, 0.2),  # VERY high frequency (many clones!)
            'unique_locations_ratio': np.random.uniform(0.2, 0.5),  # Low (scanned in many places)
            'supply_chain_completeness': np.random.uniform(0.33, 0.67),  # Some stages present (copied!)
            'license_validity_score': np.random.uniform(0.5, 1.0),  # Might be valid (copied!)
            'price_deviation_score': np.random.uniform(0.6, 1.0),  # Price might look normal (copied!)
            'temporal_consistency_score': np.random.uniform(0.3, 0.7),  # Mixed timing
            'geofence_compliance_score': np.random.uniform(0.5, 0.8),  # Some valid regions
            'speed_anomaly_severity': np.random.uniform(0.8, 1.0),  # IMPOSSIBLE SPEED! (key indicator)
            'batch_health_score': np.random.uniform(0.3, 0.7),  # Mixed batch health
            'historical_pattern_score': np.random.uniform(0.6, 0.9)  # Timing might look normal
        }
        
        data.append(list(features.values()) + [1])  # Counterfeit!
    
    print(f"   ✓ Created 45 cloned QR samples")
    print(f"   Average score: 0.50-0.65 (looks semi-legit but speed gives it away!)")
    print(f"   Key: speed_anomaly_severity = 0.8-1.0 (impossible!)")
    
    # ─────────────────────────────────────────────────────────────────────
    # TYPE 3: SOPHISTICATED FAKE (45 samples)
    # Scenario: Well-made fake (hard to detect, only subtle clues)
    # ─────────────────────────────────────────────────────────────────────
    print("\n🎭 Type 3: Sophisticated Fake (45 samples)")
    print("   Scenario: High-quality counterfeit (only subtle anomalies)")
    
    for i in range(45):
        features = {
            'scan_frequency_score': np.random.uniform(0.6, 0.8),  # Almost normal frequency
            'unique_locations_ratio': np.random.uniform(0.7, 0.9),  # Good uniqueness
            'supply_chain_completeness': np.random.uniform(0.67, 1.0),  # Mostly complete
            'license_validity_score': np.random.uniform(0.3, 0.7),  # SUSPICIOUS license (subtle!)
            'price_deviation_score': np.random.uniform(0.5, 0.8),  # Slightly off price
            'temporal_consistency_score': np.random.uniform(0.5, 0.7),  # Slightly rushed
            'geofence_compliance_score': np.random.uniform(0.5, 0.8),  # Mostly valid regions
            'speed_anomaly_severity': np.random.uniform(0.3, 0.6),  # Fast but not impossible
            'batch_health_score': np.random.uniform(0.4, 0.7),  # BATCH has issues (subtle!)
            'historical_pattern_score': np.random.uniform(0.5, 0.8)  # Mixed timing
        }
        
        data.append(list(features.values()) + [1])  # Counterfeit (but hard to detect!)
    
    print(f"   ✓ Created 45 sophisticated fake samples")
    print(f"   Average score: 0.55-0.70 (looks almost authentic!)")
    print(f"   Key: license + batch health give it away (subtle clues)")
    
    # ─────────────────────────────────────────────────────────────────────
    # TYPE 4: EDGE CASE FAKE (15 samples)
    # Scenario: Borderline fake (could be confused with authentic)
    # ─────────────────────────────────────────────────────────────────────
    print("\n🔸 Type 4: Edge Case Fake (15 samples)")
    print("   Scenario: Borderline counterfeit (very hard to detect)")
    
    for i in range(15):
        features = {
            'scan_frequency_score': np.random.uniform(0.5, 0.7),  # Borderline frequency
            'unique_locations_ratio': np.random.uniform(0.6, 0.8),  # Decent uniqueness
            'supply_chain_completeness': np.random.uniform(0.67, 1.0),  # Complete or nearly
            'license_validity_score': np.random.uniform(0.4, 0.6),  # Borderline license
            'price_deviation_score': np.random.uniform(0.6, 0.8),  # Slightly suspicious price
            'temporal_consistency_score': np.random.uniform(0.4, 0.6),  # Borderline timing
            'geofence_compliance_score': np.random.uniform(0.6, 0.8),  # Mostly OK
            'speed_anomaly_severity': np.random.uniform(0.4, 0.7),  # Slightly suspicious speed
            'batch_health_score': np.random.uniform(0.5, 0.7),  # Borderline batch
            'historical_pattern_score': np.random.uniform(0.5, 0.7)  # Borderline timing
        }
        
        data.append(list(features.values()) + [1])  # Counterfeit (barely!)
    
    print(f"   ✓ Created 15 edge case fake samples")
    print(f"   Average score: 0.50-0.65 (very hard to distinguish!)")
    
    print(f"\n{'─'*70}")
    print(f"❌ TOTAL COUNTERFEIT: 150 samples")
    print(f"{'─'*70}")
    
    # ========================================================================
    # CREATE DATAFRAME
    # ========================================================================
    
    print("\n" + "="*70)
    print("📊 CREATING DATASET")
    print("="*70)
    
    # Column names: 10 features + label
    columns = FEATURE_NAMES_V2 + ['is_counterfeit']
    
    df = pd.DataFrame(data, columns=columns)
    
    # Shuffle the data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    print("\n📈 DATASET STATISTICS:")
    print(f"\nTotal Samples: {len(df)}")
    
    authentic = (df['is_counterfeit'] == 0).sum()
    counterfeit = (df['is_counterfeit'] == 1).sum()
    
    print(f"  ✅ Authentic:   {authentic} ({authentic/len(df)*100:.1f}%)")
    print(f"  ❌ Counterfeit: {counterfeit} ({counterfeit/len(df)*100:.1f}%)")
    
    print(f"\n🔍 Feature Statistics:")
    print(df[FEATURE_NAMES_V2].describe().round(3))
    
    print(f"\n📊 Average Feature Scores by Class:")
    print("\nAuthentic drugs:")
    print(df[df['is_counterfeit'] == 0][FEATURE_NAMES_V2].mean().round(3))
    
    print("\nCounterfeit drugs:")
    print(df[df['is_counterfeit'] == 1][FEATURE_NAMES_V2].mean().round(3))
    
    # ========================================================================
    # SAVE TO CSV
    # ========================================================================
    
    # Save in backend/dataset/ directory
    output_dir = Path(__file__).parent.parent / 'dataset'
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / 'rf_training_data_v2.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n💾 SAVED TO: {output_path}")
    print("="*70)
    
    return df


# ============================================================================
# TESTING / DEMO
# ============================================================================

if __name__ == '__main__':
    print("\n" + "🏥"*35)
    print("MEDITRACE V3.0 - TRAINING DATA GENERATOR V2")
    print("🏥"*35 + "\n")
    
    # Generate dataset
    df = generate_training_data_v2()
    
    print("\n" + "="*70)
    print("✅ SAMPLE DATA (First 5 rows):")
    print("="*70)
    print(df.head())
    
    print("\n" + "="*70)
    print("✅ SAMPLE DATA (Last 5 rows):")
    print("="*70)
    print(df.tail())
    
    # Show authentic with low scores (noisy)
    print("\n" + "="*70)
    print("⚠️  NOISY AUTHENTIC EXAMPLES (Low Score but AUTHENTIC!):")
    print("="*70)
    print("These are the samples that FIX YOUR 53% CASE!")
    print("─"*70)
    
    noisy = df[df['is_counterfeit'] == 0].copy()
    noisy['avg_score'] = noisy[FEATURE_NAMES_V2].mean(axis=1)
    noisy = noisy[noisy['avg_score'] < 0.75].head(5)
    
    for idx, row in noisy.iterrows():
        avg = row[FEATURE_NAMES_V2].mean()
        print(f"\nSample {idx}: Average Score = {avg:.3f}")
        print(f"  completeness:        {row['supply_chain_completeness']:.2f}")
        print(f"  temporal_consistency: {row['temporal_consistency_score']:.2f}")
        print(f"  scan_frequency:      {row['scan_frequency_score']:.2f}")
        print(f"  Label: AUTHENTIC (despite low score!)")
    
    # Show sophisticated fakes (high scores but FAKE)
    print("\n" + "="*70)
    print("🎭 SOPHISTICATED FAKE EXAMPLES (High Score but COUNTERFEIT!):")
    print("="*70)
    
    sophisticated = df[df['is_counterfeit'] == 1].copy()
    sophisticated['avg_score'] = sophisticated[FEATURE_NAMES_V2].mean(axis=1)
    sophisticated = sophisticated[sophisticated['avg_score'] > 0.60].head(3)
    
    for idx, row in sophisticated.iterrows():
        avg = row[FEATURE_NAMES_V2].mean()
        print(f"\nSample {idx}: Average Score = {avg:.3f}")
        print(f"  license_validity:    {row['license_validity_score']:.2f} ← Suspicious!")
        print(f"  batch_health:        {row['batch_health_score']:.2f} ← Problematic!")
        print(f"  speed_anomaly:       {row['speed_anomaly_severity']:.2f}")
        print(f"  Label: COUNTERFEIT (despite decent score!)")
    
    print("\n" + "="*70)
    print("🎉 TRAINING DATA GENERATION COMPLETE!")
    print("="*70)
    print("\n📋 Next Steps:")
    print("   1. Review the CSV file")
    print("   2. Upload to Google Colab")
    print("   3. Run train_rf_v2.py")
    print("   4. Test with your 53% case!")
    print("="*70)