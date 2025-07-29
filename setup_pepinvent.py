#!/usr/bin/env python3
"""
PepINVENT Setup Script

This script helps set up PepINVENT integration for the AI-Enhanced Peptide Generator Pro.
It clones the PepINVENT repository and configures the environment.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def run_command(cmd, description, cwd=None):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found. Please ensure the required tools are installed.")
        return False


def check_prerequisites():
    """Check if required tools are available."""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    if not run_command([sys.executable, "--version"], "Python version check"):
        return False
    
    # Check Git
    if not run_command(["git", "--version"], "Git version check"):
        print("⚠️  Git not found. Please install Git to clone PepINVENT.")
        return False
    
    # Check Conda (optional)
    try:
        subprocess.run(["conda", "--version"], capture_output=True, check=True)
        print("✅ Conda found")
        use_conda = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Conda not found. Will use pip for installation.")
        use_conda = False
    
    return True, use_conda


def setup_pepinvent():
    """Set up PepINVENT integration."""
    print("🚀 Setting up PepINVENT integration...")
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Please install required tools.")
        return False
    
    _, use_conda = check_prerequisites()
    
    # Check if PepINVENT already exists
    if os.path.exists("PepINVENT"):
        print("⚠️  PepINVENT directory already exists.")
        response = input("Do you want to remove the existing installation and reinstall? (y/N): ")
        if response.lower() == 'y':
            shutil.rmtree("PepINVENT")
        else:
            print("✅ Using existing PepINVENT installation")
            return True
    
    # Clone PepINVENT repository
    if not run_command([
        "git", "clone", "https://github.com/MolecularAI/PepINVENT.git"
    ], "Cloning PepINVENT repository"):
        return False
    
    # Check if clone was successful
    if not os.path.exists("PepINVENT"):
        print("❌ Failed to clone PepINVENT repository")
        return False
    
    print("✅ PepINVENT repository cloned successfully")
    
    # Install dependencies
    if use_conda:
        # Try to create conda environment
        print("🔄 Creating conda environment...")
        env_file = os.path.join("PepINVENT", "pepinvent_env.yml")
        if os.path.exists(env_file):
            if not run_command([
                "conda", "env", "create", "-f", env_file
            ], "Creating conda environment"):
                print("⚠️  Conda environment creation failed. Trying pip installation...")
                use_conda = False
        else:
            print("⚠️  Conda environment file not found. Using pip installation...")
            use_conda = False
    
    if not use_conda:
        # Install with pip
        print("🔄 Installing PepINVENT dependencies with pip...")
        requirements_file = os.path.join("PepINVENT", "requirements.txt")
        if os.path.exists(requirements_file):
            if not run_command([
                sys.executable, "-m", "pip", "install", "-r", requirements_file
            ], "Installing PepINVENT requirements"):
                print("⚠️  Pip installation failed. Trying basic installation...")
                # Install basic dependencies
                basic_deps = [
                    "rdkit-pypi>=2023.9.1",
                    "torch>=2.0.0", 
                    "transformers>=4.30.0",
                    "numpy>=1.24.0",
                    "pandas>=2.0.0"
                ]
                for dep in basic_deps:
                    run_command([
                        sys.executable, "-m", "pip", "install", dep
                    ], f"Installing {dep}")
    
    # Test installation
    print("🔄 Testing PepINVENT installation...")
    test_result = test_pepinvent_installation()
    
    if test_result:
        print("✅ PepINVENT setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Restart your Streamlit app")
        print("2. Enable PepINVENT in the sidebar")
        print("3. Try generating peptides with PepINVENT")
        return True
    else:
        print("⚠️  PepINVENT setup completed with warnings.")
        print("   You may need to manually configure some dependencies.")
        return True


def test_pepinvent_installation():
    """Test if PepINVENT is properly installed."""
    try:
        # Import the integration module
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from modules.pepinvent_integration import PepINVENTIntegration
        
        # Test the integration
        pepinvent = PepINVENTIntegration()
        result = pepinvent.check_installation()
        
        if result['success']:
            print("✅ PepINVENT integration test passed")
            return True
        else:
            print(f"⚠️  PepINVENT integration test failed: {result['error']}")
            return False
            
    except ImportError as e:
        print(f"⚠️  Could not import PepINVENT integration: {e}")
        return False
    except Exception as e:
        print(f"⚠️  PepINVENT test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🧬 PepINVENT Setup for AI-Enhanced Peptide Generator Pro")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("streamlit_app_enhanced.py"):
        print("❌ Please run this script from the project root directory")
        print("   (where streamlit_app_enhanced.py is located)")
        return False
    
    # Run setup
    success = setup_pepinvent()
    
    if success:
        print("\n🎉 Setup completed! You can now use PepINVENT in your app.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
    
    return success


if __name__ == "__main__":
    main() 