"""
Train Random Forest Classifier V2 - FOR GOOGLE COLAB
=====================================================

CHANGES FROM V1:
1. Uses 10 NEW behavioral features (not old visual features)
2. Regularization parameters (prevents overfitting!)
3. Multi-tier confidence output (REVIEW category for 53% case)
4. Works on Colab (no local path dependencies)

AUTHOR: Built with understanding!
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


def train_random_forest_v2(csv_path='../dataset/rf_training_data_v2_noisy.csv'):
    """
    Train Random Forest with regularization to prevent overfitting.
    
    KEY IMPROVEMENTS:
    1. max_depth=7 (limits tree depth - prevents memorization)
    2. min_samples_split=20 (requires 20 samples to split)
    3. min_samples_leaf=10 (requires 10 samples per leaf)
    4. 5-fold cross-validation (more reliable accuracy estimate)
    
    Args:
        csv_path: Path to training data CSV
    
    Returns:
        Trained model, accuracy, feature importances
    """
    
    print("="*70)
    print("🌳 RANDOM FOREST TRAINING V2 - WITH REGULARIZATION")
    print("="*70)
    
    # ========================================================================
    # LOAD DATA
    # ========================================================================
    
    print(f"\n📂 Loading data from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Dataset loaded: {len(df)} samples")
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {csv_path}")
        print(f"   Make sure you uploaded the CSV file to Colab!")
        return None
    
    # Check columns
    expected_features = 10
    actual_features = len(df.columns) - 1  # Minus label column
    
    print(f"   Features: {actual_features}")
    print(f"   Expected: {expected_features}")
    
    if actual_features != expected_features:
        print(f"❌ ERROR: Expected {expected_features} features, got {actual_features}!")
        return None
    
    # Class distribution
    authentic = (df['is_counterfeit'] == 0).sum()
    counterfeit = (df['is_counterfeit'] == 1).sum()
    
    print(f"\n📊 Class Distribution:")
    print(f"   ✅ Authentic:   {authentic} ({authentic/len(df)*100:.1f}%)")
    print(f"   ❌ Counterfeit: {counterfeit} ({counterfeit/len(df)*100:.1f}%)")
    
    # ========================================================================
    # PREPARE DATA
    # ========================================================================
    
    print(f"\n🔧 Preparing data...")
    
    # Separate features and target
    X = df.drop('is_counterfeit', axis=1)
    y = df['is_counterfeit']
    
    feature_names = X.columns.tolist()
    
    # Split data (70% train, 30% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.3, 
        random_state=42, 
        stratify=y  # Maintain class distribution
    )
    
    print(f"\n📈 Data Split:")
    print(f"   Training:   {len(X_train)} samples ({len(X_train)/len(df)*100:.1f}%)")
    print(f"   Testing:    {len(X_test)} samples ({len(X_test)/len(df)*100:.1f}%)")
    
    # ========================================================================
    # TRAIN MODEL WITH REGULARIZATION
    # ========================================================================
    
    print(f"\n🌲 Training Random Forest with REGULARIZATION...")
    print(f"   (This prevents overfitting - your 100% → 93% improvement!)")
    print(f"\n   Hyperparameters:")
    print(f"   - n_estimators: 100 (number of trees)")
    print(f"   - max_depth: 7 ← REGULARIZATION (limits tree depth)")
    print(f"   - min_samples_split: 20 ← REGULARIZATION (min samples to split)")
    print(f"   - min_samples_leaf: 10 ← REGULARIZATION (min samples per leaf)")
    print(f"   - max_features: 'sqrt' ← Use √10 = 3 features per tree")
    
    rf = RandomForestClassifier(
        n_estimators=100,        # 100 trees
        max_depth=7,             # ← Prevent deep trees (overfitting)
        min_samples_split=20,    # ← Need 20 samples to split
        min_samples_leaf=10,     # ← Need 10 samples per leaf
        max_features='sqrt',     # ← Use sqrt(10) = 3 features randomly
        random_state=42,
        n_jobs=-1,               # Use all CPU cores
        verbose=1                # Show progress
    )
    
    print(f"\n⏳ Training... (this may take 10-30 seconds)")
    rf.fit(X_train, y_train)
    print(f"✅ Training complete!")
    
    # ========================================================================
    # EVALUATE MODEL
    # ========================================================================
    
    print(f"\n" + "="*70)
    print("📊 MODEL EVALUATION")
    print("="*70)
    
    # Predictions
    y_train_pred = rf.predict(X_train)
    y_test_pred = rf.predict(X_test)
    
    # Accuracy
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    print(f"\n🎯 Accuracy:")
    print(f"   Training:   {train_acc:.2%}")
    print(f"   Testing:    {test_acc:.2%}")
    
    # Check for overfitting
    overfit_gap = train_acc - test_acc
    print(f"\n🔍 Overfitting Check:")
    print(f"   Gap: {overfit_gap:.2%}")
    
    if overfit_gap < 0.05:
        print(f"   ✅ EXCELLENT! Model generalizes well!")
    elif overfit_gap < 0.10:
        print(f"   ✅ GOOD! Acceptable overfitting.")
    else:
        print(f"   ⚠️  WARNING! High overfitting detected!")
    
    # Cross-validation (5-fold)
    print(f"\n🔄 Cross-Validation (5-fold):")
    print(f"   (More reliable than single train/test split)")
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(rf, X_train, y_train, cv=cv, scoring='accuracy')
    
    print(f"   Fold scores: {[f'{s:.2%}' for s in cv_scores]}")
    print(f"   Mean:        {cv_scores.mean():.2%} (±{cv_scores.std():.2%})")
    
    # Detailed metrics
    precision = precision_score(y_test, y_test_pred)
    recall = recall_score(y_test, y_test_pred)
    f1 = f1_score(y_test, y_test_pred)
    
    # Probability predictions for AUC
    y_test_proba = rf.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_test_proba)
    
    print(f"\n📏 Test Set Metrics:")
    print(f"   Precision: {precision:.2%}  (of predicted fakes, how many are actually fake)")
    print(f"   Recall:    {recall:.2%}  (of actual fakes, how many we catch)")
    print(f"   F1-Score:  {f1:.2%}  (harmonic mean of precision & recall)")
    print(f"   AUC-ROC:   {auc:.2%}  (area under ROC curve)")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_test_pred)
    
    print(f"\n📊 Confusion Matrix:")
    print(f"                 Predicted")
    print(f"               Authentic  Fake")
    print(f"   Authentic      {cm[0,0]:3d}     {cm[0,1]:3d}")
    print(f"   Fake           {cm[1,0]:3d}     {cm[1,1]:3d}")
    
    # False positives and negatives
    false_positives = cm[0, 1]  # Authentic predicted as Fake
    false_negatives = cm[1, 0]  # Fake predicted as Authentic
    
    print(f"\n⚠️  Error Analysis:")
    print(f"   False Positives: {false_positives} (authentic flagged as fake)")
    print(f"   False Negatives: {false_negatives} (fake passed as authentic)")
    
    # Classification Report
    print(f"\n📋 Detailed Classification Report:")
    print(classification_report(
        y_test, y_test_pred, 
        target_names=['Authentic', 'Counterfeit'],
        digits=3
    ))
    
    # ========================================================================
    # FEATURE IMPORTANCE
    # ========================================================================
    
    print(f"\n" + "="*70)
    print("🔍 FEATURE IMPORTANCE")
    print("="*70)
    print("(Which features matter most for detection?)")
    
    importances = pd.DataFrame({
        'feature': feature_names,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop Features for Counterfeit Detection:")
    for idx, row in importances.iterrows():
        bar = '█' * int(row['importance'] * 50)
        print(f"   {row['feature']:30s} {row['importance']:.3f} {bar}")
    
    # ========================================================================
    # MULTI-TIER CONFIDENCE ANALYSIS
    # ========================================================================
    
    print(f"\n" + "="*70)
    print("🎯 MULTI-TIER CONFIDENCE ANALYSIS")
    print("="*70)
    print("(This FIXES your 53% case!)")
    
    # Get probabilities for test set
    proba = rf.predict_proba(X_test)[:, 1]  # Probability of being counterfeit
    
    # Define tiers
    tiers = {
        'AUTHENTIC': (proba < 0.50),
        'REVIEW': (proba >= 0.50) & (proba < 0.75),
        'SUSPICIOUS': (proba >= 0.75) & (proba < 0.85),
        'COUNTERFEIT': (proba >= 0.85)
    }
    
    print(f"\n📊 Confidence Distribution:")
    for tier_name, mask in tiers.items():
        count = mask.sum()
        pct = count / len(proba) * 100
        print(f"   {tier_name:15s}: {count:3d} samples ({pct:5.1f}%)")
    
    # Check how many authentic drugs fall in each tier
    print(f"\n🔍 Authentic Drugs by Tier:")
    for tier_name, mask in tiers.items():
        authentic_in_tier = ((y_test == 0) & mask).sum()
        total_in_tier = mask.sum()
        
        if total_in_tier > 0:
            pct = authentic_in_tier / total_in_tier * 100
            print(f"   {tier_name:15s}: {authentic_in_tier}/{total_in_tier} ({pct:.1f}% authentic)")
    
    print(f"\n💡 KEY INSIGHT:")
    review_authentic = ((y_test == 0) & tiers['REVIEW']).sum()
    review_total = tiers['REVIEW'].sum()
    
    if review_total > 0:
        print(f"   REVIEW category has {review_authentic}/{review_total} authentic drugs")
        print(f"   → These are noisy but legitimate (like your 53% case!)")
        print(f"   → System will show WARNING, not BLOCKED!")
    
    # ========================================================================
    # VISUALIZATIONS
    # ========================================================================
    
    print(f"\n📊 Generating visualizations...")
    
    # Plot 1: Feature Importance
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Feature Importance Bar Chart
    axes[0, 0].barh(importances['feature'], importances['importance'], color='steelblue')
    axes[0, 0].set_xlabel('Importance', fontsize=12)
    axes[0, 0].set_title('Feature Importance', fontsize=14, fontweight='bold')
    axes[0, 0].invert_yaxis()
    
    # Confusion Matrix Heatmap
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Authentic', 'Counterfeit'],
                yticklabels=['Authentic', 'Counterfeit'],
                ax=axes[0, 1], cbar_kws={'label': 'Count'})
    axes[0, 1].set_title('Confusion Matrix', fontsize=14, fontweight='bold')
    axes[0, 1].set_ylabel('True Label')
    axes[0, 1].set_xlabel('Predicted Label')
    
    # Confidence Distribution
    axes[1, 0].hist([proba[y_test == 0], proba[y_test == 1]], 
                    bins=20, label=['Authentic', 'Counterfeit'],
                    alpha=0.7, color=['green', 'red'])
    axes[1, 0].axvline(0.50, color='orange', linestyle='--', label='REVIEW threshold')
    axes[1, 0].axvline(0.75, color='red', linestyle='--', label='SUSPICIOUS threshold')
    axes[1, 0].axvline(0.85, color='darkred', linestyle='--', label='COUNTERFEIT threshold')
    axes[1, 0].set_xlabel('Counterfeit Probability', fontsize=12)
    axes[1, 0].set_ylabel('Count', fontsize=12)
    axes[1, 0].set_title('Confidence Distribution by Class', fontsize=14, fontweight='bold')
    axes[1, 0].legend()
    
    # Cross-validation Scores
    axes[1, 1].plot(range(1, 6), cv_scores, marker='o', linewidth=2, markersize=10, color='steelblue')
    axes[1, 1].axhline(cv_scores.mean(), color='red', linestyle='--', label=f'Mean: {cv_scores.mean():.2%}')
    axes[1, 1].set_xlabel('Fold', fontsize=12)
    axes[1, 1].set_ylabel('Accuracy', fontsize=12)
    axes[1, 1].set_title('5-Fold Cross-Validation Scores', fontsize=14, fontweight='bold')
    axes[1, 1].set_ylim([0.85, 1.0])
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('rf_v2_results.png', dpi=150, bbox_inches='tight')
    print(f"   ✅ Saved: rf_v2_results.png")
    plt.show()
    
    # ========================================================================
    # SAVE MODEL
    # ========================================================================
    
    print(f"\n💾 Saving model...")
    
    joblib.dump(rf, 'rf_classifier_v2.pkl')
    print(f"   ✅ Saved: rf_classifier_v2.pkl")
    
    # Save feature names for later use
    joblib.dump(feature_names, 'feature_names_v2.pkl')
    print(f"   ✅ Saved: feature_names_v2.pkl")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print(f"\n" + "="*70)
    print("🎉 TRAINING COMPLETE!")
    print("="*70)
    
    print(f"\n✅ Model Performance Summary:")
    print(f"   Test Accuracy:       {test_acc:.2%}")
    print(f"   Cross-Val Accuracy:  {cv_scores.mean():.2%} (±{cv_scores.std():.2%})")
    print(f"   Precision:           {precision:.2%}")
    print(f"   Recall:              {recall:.2%}")
    print(f"   F1-Score:            {f1:.2%}")
    print(f"   AUC-ROC:             {auc:.2%}")
    
    print(f"\n🔍 Top 3 Most Important Features:")
    for i, row in importances.head(3).iterrows():
        print(f"   {i+1}. {row['feature']:30s} ({row['importance']:.3f})")
    
    print(f"\n📋 What Changed From V1:")
    print(f"   ❌ V1: 100% train accuracy (overfitted!)")
    print(f"   ✅ V2: {train_acc:.1%} train accuracy (regularized!)")
    print(f"   ❌ V1: Binary classification (authentic/fake only)")
    print(f"   ✅ V2: Multi-tier (REVIEW category for 53% case!)")
    
    print(f"\n📁 Files Created:")
    print(f"   - rf_classifier_v2.pkl (trained model)")
    print(f"   - feature_names_v2.pkl (feature list)")
    print(f"   - rf_v2_results.png (visualizations)")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Download rf_classifier_v2.pkl to your laptop")
    print(f"   2. Test with your 53% case drug")
    print(f"   3. Verify it shows REVIEW (not COUNTERFEIT)")
    
    print("="*70)
    
    return rf, test_acc, importances


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "🏥"*35)
    print("MEDITRACE V3.0 - RANDOM FOREST TRAINING V2")
    print("🏥"*35 + "\n")
    
    # Train model
    result = train_random_forest_v2('../dataset/rf_training_data_v2_noisy.csv')
    
    if result:
        rf, accuracy, importances = result
        
        print(f"\n" + "="*70)
        print(f"✅ SUCCESS! Model trained with {accuracy:.2%} accuracy")
        print(f"   (Regularized to prevent overfitting)")
        print("="*70)
    else:
        print(f"\n❌ Training failed. Check error messages above.")