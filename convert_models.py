"""Convert old pickle models to be compatible with NumPy 1.24"""
import pickle
import sys
import os

def convert_pickle(input_file, output_file):
    """Load and re-save pickle file to make it compatible."""
    print(f"Converting {input_file}...")
    try:
        # Try loading with pickle protocol 4 (most compatible)
        with open(input_file, 'rb') as f:
            data = pickle.load(f, encoding='latin1')
        
        # Save with protocol 4 for compatibility
        with open(output_file, 'wb') as f:
            pickle.dump(data, f, protocol=4)
        
        print(f"✓ Successfully converted to {output_file}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    # Convert both model files
    success = True
    
    # Convert TF-IDF vectorizer
    if os.path.exists('tfidf.pkl'):
        success &= convert_pickle('tfidf.pkl', 'tfidf_v2.pkl')
    
    # Convert ML model
    if os.path.exists('model.pkl'):
        success &= convert_pickle('model.pkl', 'model_v2.pkl')
    
    if success:
        print("\n✓ All models converted successfully!")
        print("You can now use tfidf_v2.pkl and model_v2.pkl")
    else:
        print("\n✗ Some conversions failed")
        sys.exit(1)
