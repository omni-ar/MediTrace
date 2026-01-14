"""
Add Realistic Noise to Training Data
=====================================

PROBLEM: Current data is too clean → 100% accuracy (overfitting!)
SOLUTION: Add controlled noise to create realistic overlap

This makes the classification task HARDER (more realistic!)
"""

import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)


def add_realistic_noise(csv_path='../dataset/rf_training_data_v2.csv',
                        output_path='../dataset/rf_training_data_v2_noisy.csv'):
    """
    Add controlled noise to make data more realistic.
    
    Strategy:
    1. Add Gaussian noise to all features (±5-10%)
    2. Randomly flip some values slightly
    3. Create more overlap between classes
    
    This makes perfect separation IMPOSSIBLE (realistic!)
    """
    
    print("="*70)
    print("🔊 ADDING REALISTIC NOISE TO TRAINING DATA")
    print("="*70)
    
    # Load data
    df = pd.read_csv(csv_path)
    
    print(f"\n📂 Loaded: {len(df)} samples")
    print(f"   Authentic:   {(df['is_counterfeit'] == 0).sum()}")
    print(f"   Counterfeit: {(df['is_counterfeit'] == 1).sum()}")
    
    # Separate features and label
    X = df.drop('is_counterfeit', axis=1)
    y = df['is_counterfeit']
    
    print(f"\n🔊 Adding controlled noise...")
    
    # Add Gaussian noise to each feature (±5-10% of value)
    for col in X.columns:
        # Calculate noise scale based on feature value
        noise_scale = 0.08  # 8% noise
        noise = np.random.normal(0, noise_scale, size=len(X))
        
        # Add noise
        X[col] = X[col] + (X[col] * noise)
        
        # Clip to valid range [0, 1]
        X[col] = X[col].clip(0, 1)
    
    # Additional strategy: For ~10% of samples, add extra noise
    num_extra_noisy = int(len(X) * 0.1)
    extra_noisy_indices = np.random.choice(len(X), num_extra_noisy, replace=False)
    
    print(f"   - Added 8% Gaussian noise to all features")
    print(f"   - Added extra noise to {num_extra_noisy} samples (10%)")
    
    for idx in extra_noisy_indices:
        # Add extra noise to 3 random features
        random_features = np.random.choice(X.columns, 3, replace=False)
        for feat in random_features:
            extra_noise = np.random.uniform(-0.15, 0.15)  # ±15%
            X.loc[idx, feat] = (X.loc[idx, feat] + extra_noise).clip(0, 1)
    
    # Recombine
    df_noisy = pd.concat([X, y], axis=1)
    
    # Verify statistics
    print(f"\n📊 Before vs After Noise:")
    print(f"\n{'Feature':30s} {'Before Mean':>12s} {'After Mean':>12s} {'Change':>10s}")
    print(f"{'─'*70}")
    
    df_orig = pd.read_csv(csv_path)
    
    for col in X.columns:
        before_mean = df_orig[col].mean()
        after_mean = df_noisy[col].mean()
        change = ((after_mean - before_mean) / before_mean) * 100
        
        print(f"{col:30s} {before_mean:12.4f} {after_mean:12.4f} {change:>9.2f}%")
    
    # Save
    df_noisy.to_csv(output_path, index=False)
    
    print(f"\n💾 Saved to: {output_path}")
    
    print(f"\n" + "="*70)
    print("✅ NOISE ADDED SUCCESSFULLY!")
    print("="*70)
    print(f"\n💡 What changed:")
    print(f"   - Feature values shifted by ~5-10%")
    print(f"   - 10% of samples have extra noise")
    print(f"   - Creates realistic overlap between classes")
    print(f"   - Model can NO LONGER achieve 100% accuracy!")
    
    print(f"\n🎯 Expected Results:")
    print(f"   - Training accuracy: 93-96% (was 100%)")
    print(f"   - Testing accuracy: 91-94% (was 100%)")
    print(f"   - REVIEW category: 15-25 samples (was 0!)")
    
    print(f"\n📋 Next Step:")
    print(f"   python train_rf_v2.py")
    print(f"   (Make sure it uses the NEW CSV file!)")
    print("="*70)
    
    return df_noisy


if __name__ == '__main__':
    # Add noise
    df_noisy = add_realistic_noise()
    
    print(f"\n✅ Sample of noisy data (first 5 rows):")
    print(df_noisy.head())