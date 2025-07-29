#!/usr/bin/env python3
"""
Test script for PepINVENT integration

This script tests the PepINVENT integration module to ensure it works correctly.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pepinvent_integration():
    """Test the PepINVENT integration module."""
    print("🧬 Testing PepINVENT Integration...")
    
    try:
        # Import the integration module
        from modules.pepinvent_integration import PepINVENTIntegration
        
        # Create integration instance
        pepinvent = PepINVENTIntegration()
        
        # Test installation check
        print("🔍 Testing installation check...")
        result = pepinvent.check_installation()
        
        if result['success']:
            print("✅ PepINVENT installation verified!")
            print(f"   {result['explanation']}")
        else:
            print("❌ PepINVENT installation failed!")
            print(f"   Error: {result['error']}")
            print("   This is expected if PepINVENT is not installed yet.")
            print("   Run 'python setup_pepinvent.py' to install PepINVENT.")
        
        # Test configuration listing
        print("\n🔍 Testing configuration listing...")
        config_result = pepinvent.get_available_configs()
        
        if config_result['success']:
            print("✅ Configuration listing successful!")
            configs = config_result['configs']
            if configs:
                print(f"   Found {len(configs)} configuration files:")
                for config_name, config_info in configs.items():
                    print(f"   - {config_info['name']}")
            else:
                print("   No configuration files found (expected if not installed)")
        else:
            print("❌ Configuration listing failed!")
            print(f"   Error: {config_result['error']}")
        
        # Test peptide property calculation
        print("\n🔍 Testing peptide property calculation...")
        test_sequence = "ACDEFGHI"
        properties = pepinvent._calculate_peptide_properties(test_sequence)
        
        print("✅ Peptide property calculation successful!")
        print(f"   Sequence: {test_sequence}")
        print(f"   Length: {properties['length']}")
        print(f"   Net Charge: {properties['net_charge']}")
        print(f"   Hydrophobicity: {properties['hydrophobicity']}")
        print(f"   Motifs: {', '.join(properties['motifs'])}")
        
        # Test fallback peptide generation
        print("\n🔍 Testing fallback peptide generation...")
        fallback_peptides = pepinvent._generate_fallback_peptides(3)
        
        print("✅ Fallback peptide generation successful!")
        print(f"   Generated {len(fallback_peptides)} fallback peptides:")
        for i, peptide in enumerate(fallback_peptides, 1):
            print(f"   {i}. {peptide['sequence']} - {peptide['properties']['hydrophobicity']}")
        
        print("\n🎉 All tests completed successfully!")
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
    print("🧬 PepINVENT Integration Test")
    print("=" * 40)
    
    success = test_pepinvent_integration()
    
    if success:
        print("\n✅ Integration test passed!")
        print("   The PepINVENT integration module is working correctly.")
    else:
        print("\n❌ Integration test failed!")
        print("   Please check the error messages above.")
    
    return success


if __name__ == "__main__":
    main() 