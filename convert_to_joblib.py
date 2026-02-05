"""Convert pickle models to joblib format for better compatibility."""
import pickle
import joblib
import sys
import numpy as np

def convert_to_joblib(pkl_file, joblib_file):
    """Convert pickle file to joblib format."""
    try:
        print(f"Loading {pkl_file}...")
        
        # Map numpy modules for compatibility
        sys.modules['numpy._core'] = np.core
        sys.modules['numpy._core.multiarray'] = np.core.multiarray
        sys.modules['numpy._core._multiarray_umath'] = np.core._multiarray_umath
        
        with open(pkl_file, 'rb') as f:
            model = pickle.load(f, encoding='latin1')
        
        print(f"Saving as {joblib_file}...")
        joblib.dump(model, joblib_file, compress=3)
        
        print(f"✓ Successfully converted {pkl_file} to {joblib_file}")
        
        # Verify
        print(f"Verifying {joblib_file}...")
        test_load = joblib.load(joblib_file)
        print(f"✓ Verification successful")
        
        return True
    except Exception as e:
        print(f"✗ Error converting {pkl_file}: {e}")
        return False

if __name__ == "__main__":
    success = True
    
    # Convert both models
    success &= convert_to_joblib('tfidf.pkl', 'tfidf.joblib')
    success &= convert_to_joblib('model.pkl', 'model.joblib')
    
    if success:
        print("\n✓ All models converted to joblib format!")
    else:
        print("\n✗ Some conversions failed")
        sys.exit(1)
