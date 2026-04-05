#!/usr/bin/env python3
"""
Utility script to switch between trained models.
Usage: python3 switch_models.py <model_name>
Example: python3 switch_models.py mnist_model.h5
"""

import sys
import shutil
import os

def switch_model(model_name):
    """Switch the active model by copying the specified model to model.h5"""
    if not os.path.exists(model_name):
        print(f"Error: Model file '{model_name}' not found!")
        return False
    
    # Backup current model if it exists
    if os.path.exists('model.h5'):
        shutil.copy2('model.h5', 'model_backup.h5')
        print("Current model backed up as 'model_backup.h5'")
    
    # Copy new model
    shutil.copy2(model_name, 'model.h5')
    print(f"Successfully switched to model: {model_name}")
    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 switch_models.py <model_name>")
        print("Example: python3 switch_models.py mnist_model.h5")
        sys.exit(1)
    
    model_name = sys.argv[1]
    switch_model(model_name)