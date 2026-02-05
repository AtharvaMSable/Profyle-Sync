"""Diagnostic script to check model files and environment."""
import os
import sys
import pickle

print("="*60)
print("DIAGNOSTIC REPORT")
print("="*60)

print("\n1. Python Version:")
print(f"   {sys.version}")

print("\n2. Working Directory:")
print(f"   {os.getcwd()}")

print("\n3. Model Files Check:")
files_to_check = ['tfidf.pkl', 'model.pkl']
for filename in files_to_check:
    exists = os.path.exists(filename)
    if exists:
        size = os.path.getsize(filename)
        print(f"   ✓ {filename}: {size:,} bytes")
        
        # Try to load
        try:
            with open(filename, 'rb') as f:
                obj = pickle.load(f)
            print(f"     - Pickle load: SUCCESS")
            print(f"     - Type: {type(obj)}")
        except Exception as e:
            print(f"     - Pickle load: FAILED - {e}")
    else:
        print(f"   ✗ {filename}: NOT FOUND")
        # List files in current directory
        print(f"     Files in {os.getcwd()}:")
        for f in os.listdir('.')[:20]:
            print(f"       - {f}")

print("\n4. NumPy Version:")
try:
    import numpy as np
    print(f"   {np.__version__}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n5. Scikit-learn Version:")
try:
    import sklearn
    print(f"   {sklearn.__version__}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "="*60)
