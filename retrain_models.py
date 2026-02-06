"""
Retrain ML models with current scikit-learn version for compatibility
"""
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.text_processing import clean_resume_for_categorization

print("="*60)
print("RETRAINING ML MODELS")
print("="*60)

# Load data
print("\n1. Loading Resume.csv...")
try:
    df = pd.read_csv('Resume.csv')
    print(f"   ✓ Loaded {len(df)} resumes")
    print(f"   Columns: {list(df.columns)}")
except FileNotFoundError:
    print("   ✗ Resume.csv not found!")
    print("   Please ensure Resume.csv is in the project root directory.")
    sys.exit(1)

# Check required columns
resume_col = 'Resume' if 'Resume' in df.columns else 'Resume_str' if 'Resume_str' in df.columns else None
category_col = 'Category' if 'Category' in df.columns else None

if not resume_col or not category_col:
    print(f"   ✗ Required columns not found!")
    print(f"   Looking for: 'Resume'/'Resume_str' and 'Category'")
    print(f"   Found: {list(df.columns)}")
    sys.exit(1)

# Prepare data
print("\n2. Preparing data...")
X = df[resume_col].apply(clean_resume_for_categorization)
y = df[category_col]

# Create category mapping
categories = sorted(y.unique())
category_to_id = {cat: idx for idx, cat in enumerate(categories)}
id_to_category = {idx: cat for cat, idx in category_to_id.items()}

# Convert categories to IDs
y_encoded = y.map(category_to_id)

print(f"   ✓ Cleaned {len(X)} resumes")
print(f"   ✓ Found {len(categories)} categories")

# Split data
print("\n3. Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
print(f"   ✓ Train: {len(X_train)}, Test: {len(X_test)}")

# Train TF-IDF Vectorizer
print("\n4. Training TF-IDF Vectorizer...")
vectorizer = TfidfVectorizer(
    max_features=1500,
    min_df=5,
    max_df=0.7,
    stop_words='english',
    ngram_range=(1, 2)
)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)
print(f"   ✓ Vocabulary size: {len(vectorizer.vocabulary_)}")
print(f"   ✓ Feature shape: {X_train_tfidf.shape}")

# Verify vectorizer is fitted
from sklearn.utils.validation import check_is_fitted
try:
    check_is_fitted(vectorizer)
    print(f"   ✓ Vectorizer is properly fitted")
except:
    print(f"   ✗ Vectorizer fit verification failed!")
    sys.exit(1)

# Train Logistic Regression model
print("\n5. Training Logistic Regression model...")
model = LogisticRegression(
    max_iter=1000,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
model.fit(X_train_tfidf, y_train)
print(f"   ✓ Model trained")

# Evaluate
train_score = model.score(X_train_tfidf, y_train)
test_score = model.score(X_test_tfidf, y_test)
print(f"   ✓ Train accuracy: {train_score:.4f}")
print(f"   ✓ Test accuracy: {test_score:.4f}")

# Save models
print("\n6. Saving models...")
with open('tfidf.pkl', 'wb') as f:
    pickle.dump(vectorizer, f, protocol=4)
print(f"   ✓ Saved tfidf.pkl")

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f, protocol=4)
print(f"   ✓ Saved model.pkl")

# Save category mapping
with open('category_mapping.pkl', 'wb') as f:
    pickle.dump(id_to_category, f, protocol=4)
print(f"   ✓ Saved category_mapping.pkl")

# Test loading
print("\n7. Testing model loading...")
with open('tfidf.pkl', 'rb') as f:
    test_vec = pickle.load(f)
with open('model.pkl', 'rb') as f:
    test_model = pickle.load(f)

# Test prediction
test_text = X_test.iloc[0]
test_features = test_vec.transform([test_text])
test_pred = test_model.predict(test_features)[0]
test_cat = id_to_category[test_pred]
print(f"   ✓ Test prediction: {test_cat}")

print("\n" + "="*60)
print("✓ MODELS RETRAINED SUCCESSFULLY!")
print("="*60)
print("\nYou can now run: streamlit run app.py")
