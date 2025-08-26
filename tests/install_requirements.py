#!/usr/bin/env python3
"""
Script to install requirements in the conda environment.
Run this from the study directory with the conda environment activated.
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Check if we're in a conda environment
    conda_env = subprocess.run(['conda', 'info', '--envs'], 
                              capture_output=True, text=True, check=True)
    
    if 'bean-study-env' not in conda_env.stdout:
        print("❌ bean-study-env not found in conda environments!")
        print("💡 Please create the environment first:")
        print("   conda create -n bean-study-env python=3.9 -y")
        sys.exit(1)
    
    print("✅ Found bean-study-env conda environment")
    
    # Get the requirements.txt path
    script_dir = Path(__file__).parent
    requirements_path = script_dir / "requirements.txt"
    
    if not requirements_path.exists():
        print(f"❌ requirements.txt not found: {requirements_path}")
        sys.exit(1)
    
    print(f"📦 Installing requirements from: {requirements_path}")
    
    try:
        # Install requirements
        result = subprocess.run(['pip', 'install', '-r', str(requirements_path)], 
                              check=True, capture_output=True, text=True)
        print("✅ Requirements installed successfully!")
        
        # Install the framework in editable mode
        print("📦 Installing study-framework-core in editable mode...")
        result = subprocess.run(['pip', 'install', '-e', '.'], 
                              check=True, capture_output=True, text=True)
        print("✅ Framework installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
