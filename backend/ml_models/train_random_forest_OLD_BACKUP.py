"""
Train Random Forest Classifier for Counterfeit Detection

Trains on synthetic data with 10 features
Outputs model performance metrics and saves trained model
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def train_random_forest():
    """
    Train Random Forest classifier on synthetic data
    """
    
    print("="*70)
    print("🌳 RANDOM FOREST TRAINING")
    print("="*70)
    
    # ========================================
    # LOAD DATA
    # ========================================
    
    data_path = Path(__file__).parent.parent / 'dataset' / 'rf_training_data.csv'
    
    if not data_path.exists():
        print(f"\n❌ ERROR: Training data not found!")
        print(f"   Expected: {data_path}")
        print(f"\n   Run: python generate_training_data.py")
        return None
    
    df = pd.read_csv(data_path)
    
    print(f"\n📊 Dataset Loaded: {len(df)} samples")
    print(f"   Features: {len(df.columns) - 1}")
    print(f"   Authentic: {(df['is_counterfeit'] == 0).sum()}")
    print(f"   Counterfeit: {(df['is_counterfeit'] == 1).sum()}")
    
    # ========================================
    # PREPARE DATA
    # ========================================
    
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
    
    # ========================================
    # FEATURE SCALING
    # ========================================
    
    print(f"\n⚖️  Scaling features...")
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # ========================================
    # TRAIN MODEL
    # ========================================
    
    print(f"\n🌲 Training Random Forest...")
    print(f"   Estimators: 100 trees")
    print(f"   Max Depth: 10")
    print(f"   Min Samples Split: 5")
    
    rf = RandomForestClassifier(
        n_estimators=100,      # Number of trees
        max_depth=10,          # Max tree depth
        min_samples_split=5,   # Min samples to split node
        min_samples_leaf=2,    # Min samples in leaf
        random_state=42,
        n_jobs=-1              # Use all CPU cores
    )
    
    rf.fit(X_train_scaled, y_train)
    
    print(f"✅ Training complete!")
    
    # ========================================
    # EVALUATE MODEL
    # ========================================
    
    print(f"\n📊 MODEL EVALUATION")
    print("="*70)
    
    # Predictions
    y_train_pred = rf.predict(X_train_scaled)
    y_test_pred = rf.predict(X_test_scaled)
    
    # Accuracy
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    print(f"\n🎯 Accuracy:")
    print(f"   Training:   {train_acc:.2%}")
    print(f"   Testing:    {test_acc:.2%}")
    
    # Cross-validation (5-fold)
    print(f"\n🔄 Cross-Validation (5-fold):")
    cv_scores = cross_val_score(rf, X_train_scaled, y_train, cv=5, scoring='accuracy')
    print(f"   Scores: {[f'{s:.2%}' for s in cv_scores]}")
    print(f"   Mean:   {cv_scores.mean():.2%} (±{cv_scores.std():.2%})")
    
    # Detailed metrics
    precision = precision_score(y_test, y_test_pred)
    recall = recall_score(y_test, y_test_pred)
    f1 = f1_score(y_test, y_test_pred)
    
    # Probability predictions for AUC
    y_test_proba = rf.predict_proba(X_test_scaled)[:, 1]
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
    
    # Classification Report
    print(f"\n📋 Detailed Classification Report:")
    print(classification_report(
        y_test, y_test_pred, 
        target_names=['Authentic', 'Counterfeit'],
        digits=3
    ))
    
    # ========================================
    # FEATURE IMPORTANCE
    # ========================================
    
    print(f"\n🔍 FEATURE IMPORTANCE")
    print("="*70)
    
    importances = pd.DataFrame({
        'feature': feature_names,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop Features for Counterfeit Detection:")
    for idx, row in importances.iterrows():
        bar = '█' * int(row['importance'] * 50)
        print(f"   {row['feature']:25s} {row['importance']:.3f} {bar}")
    
    # ========================================
    # SAVE MODELS
    # ========================================
    
    model_dir = Path(__file__).parent.parent / 'trained_models'
    model_dir.mkdir(exist_ok=True)
    
    rf_path = model_dir / 'rf_classifier.pkl'
    scaler_path = model_dir / 'scaler.pkl'
    
    joblib.dump(rf, rf_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"\n💾 MODELS SAVED")
    print("="*70)
    print(f"   Random Forest: {rf_path}")
    print(f"   Scaler:        {scaler_path}")
    
    # ========================================
    # VISUALIZATIONS (optional)
    # ========================================
    
    try:
        # Plot feature importance
        plt.figure(figsize=(10, 6))
        plt.barh(importances['feature'], importances['importance'])
        plt.xlabel('Importance')
        plt.title('Random Forest Feature Importance')
        plt.tight_layout()
        
        plot_path = model_dir / 'rf_feature_importance.png'
        plt.savefig(plot_path, dpi=100, bbox_inches='tight')
        print(f"   Plot:          {plot_path}")
        plt.close()
        
    except Exception as e:
        print(f"   (Skipped plot generation: {e})")
    
    # ========================================
    # SUMMARY
    # ========================================
    
    print(f"\n" + "="*70)
    print("🎉 TRAINING COMPLETE!")
    print("="*70)
    
    print(f"\n✅ Model Performance Summary:")
    print(f"   Test Accuracy:  {test_acc:.2%}")
    print(f"   Precision:      {precision:.2%}")
    print(f"   Recall:         {recall:.2%}")
    print(f"   F1-Score:       {f1:.2%}")
    print(f"   AUC-ROC:        {auc:.2%}")
    
    print(f"\n🎯 Top 3 Most Important Features:")
    for idx, row in importances.head(3).iterrows():
        print(f"   {idx+1}. {row['feature']:25s} ({row['importance']:.3f})")
    
    print(f"\n📁 Next Steps:")
    print(f"   1. Check saved models in: {model_dir}")
    print(f"   2. Create counterfeit_classifier.py wrapper")
    print(f"   3. Integrate with main.py API")
    
    return rf, scaler, test_acc


# =============================================================================
# DEMO / TESTING
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏥 MEDITRACE - RANDOM FOREST TRAINING")
    print("="*70)
    
    # Train model
    result = train_random_forest()
    
    if result:
        rf, scaler, accuracy = result
        
        print(f"\n" + "="*70)
        print(f"✅ Model trained successfully!")
        print(f"   Accuracy: {accuracy:.2%}")
        print("="*70)
    else:
        print(f"\n❌ Training failed. Check error messages above.")