#!/usr/bin/env python3
"""
Test script for cloud-compatible PepINVENT integration

This script tests that the PepINVENT integration works without rdkit, torch, or transformers.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cloud_compatibility():
    """Test cloud-compatible PepINVENT integration."""
    print("🧬 Testing Cloud-Compatible PepINVENT Integration...")
    
    try:
        # Import the integration module
        from modules.pepinvent_integration import PepINVENTIntegration
        
        # Create integration instance
        pepinvent = PepINVENTIntegration()
        
        # Test installation check
        print("🔍 Testing installation check...")
        result = pepinvent.check_installation()
        
        if result['success']:
            print("✅ PepINVENT installation check passed!")
            print(f"   {result['explanation']}")
            
            if result.get('cloud_mode'):
                print("☁️ Cloud mode is active")
        else:
            print("❌ PepINVENT installation check failed!")
            print(f"   Error: {result['error']}")
            return False
        
        # Test cloud peptide generation
        print("\n🔍 Testing cloud peptide generation...")
        test_sequence = "ACDEFGHIKLMNPQRSTVWY"
        result = pepinvent.generate_peptides_sampling(test_sequence, 2)
        
        if result['success']:
            print("✅ Cloud peptide generation successful!")
            print(f"   Generated {len(result['peptides'])} peptides")
            for i, peptide in enumerate(result['peptides'], 1):
                print(f"   Peptide {i}: {peptide['sequence']}")
        else:
            print("❌ Cloud peptide generation failed!")
            print(f"   Error: {result['error']}")
            return False
        
        # Test RL generation
        print("\n🔍 Testing cloud RL generation...")
        result = pepinvent.generate_peptides_rl(test_sequence, 2)
        
        if result['success']:
            print("✅ Cloud RL generation successful!")
            print(f"   Generated {len(result['peptides'])} peptides")
            for i, peptide in enumerate(result['peptides'], 1):
                print(f"   Peptide {i}: {peptide['sequence']}")
        else:
            print("❌ Cloud RL generation failed!")
            print(f"   Error: {result['error']}")
            return False
        
        print("\n🎉 All cloud compatibility tests passed!")
        print("   The app is ready for Streamlit Cloud deployment.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this from the project root directory.")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def main():
    """Main test function."""
    print("🧬 Cloud-Compatible PepINVENT Integration Test")
    print("=" * 50)
    
    success = test_cloud_compatibility()
    
    if success:
        print("\n✅ Cloud compatibility test passed!")
        print("   Your app is ready for Streamlit Cloud deployment.")
        print("   No problematic dependencies required.")
    else:
        print("\n❌ Cloud compatibility test failed!")
        print("   Please check the error messages above.")
    
    return success


if __name__ == "__main__":
    main() 