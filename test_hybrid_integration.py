#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for hybrid peptide generation functionality.
Tests the complete workflow: PepINVENT → Property Analysis → LLM Refinement → Comparison
"""

import sys
import os
from typing import Dict, Any

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from hybrid_peptide_generator import HybridPeptideGenerator
from llm_providers import LLMProviderFactory


def test_hybrid_generation():
    """Test the hybrid peptide generation workflow."""
    
    print("🧬 Testing Hybrid Peptide Generation...")
    
    try:
        # Initialize LLM provider (mock for testing)
        llm_factory = LLMProviderFactory()
        
        # Create a mock LLM provider for testing
        class MockLLMProvider:
            def generate_response(self, prompt, **kwargs):
                return {
                    'success': True,
                    'response': '''
                    {
                        "refined_peptides": [
                            {
                                "id": "REF_001",
                                "sequence": "ACDEFGHIKLMN",
                                "original_id": "PEP_001",
                                "improvements": ["Improved solubility", "Better stability", "Enhanced binding"],
                                "reasoning": "Modified sequence to improve solubility while maintaining binding affinity",
                                "focus_areas": ["solubility", "stability", "binding"]
                            },
                            {
                                "id": "REF_002", 
                                "sequence": "QRSTUVWXYZAB",
                                "original_id": "PEP_002",
                                "improvements": ["Reduced aggregation", "Better charge distribution"],
                                "reasoning": "Optimized charge distribution to reduce aggregation tendency",
                                "focus_areas": ["stability", "solubility"]
                            }
                        ],
                        "summary": "Successfully refined peptides with focus on solubility and stability improvements"
                    }
                    ''',
                    'provider': 'Mock',
                    'model': 'test-model'
                }
        
        mock_llm = MockLLMProvider()
        
        # Initialize hybrid generator
        hybrid_generator = HybridPeptideGenerator(mock_llm, "./PepINVENT")
        
        # Test data
        context_data = {
            'sequence': 'MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWUAIGLNKALELVKGRKAAQVEYLVKKNSRFSKEGLEFLLAS',
            'chain_id': 'A',
            'num_peptides': 2,
            'surface_data': {'surface_residues': 45, 'hydrophobic_count': 12}
        }
        
        print("📊 Testing hybrid generation workflow...")
        
        # Test the complete workflow
        result = hybrid_generator.generate_and_refine_peptides(
            context_data, 
            num_peptides=2, 
            refinement_focus="balanced"
        )
        
        if result['success']:
            print("✅ Hybrid generation successful!")
            print(f"📈 Generated {len(result['original_peptides'])} original peptides")
            print(f"🔬 Generated {len(result['refined_peptides'])} refined peptides")
            print(f"📊 Strategy: {result.get('metadata', {}).get('strategy', 'Unknown')}")
            
            # Test comparison functionality
            print("\n📋 Testing comparison functionality...")
            comparison_df = hybrid_generator.get_comparison_dataframe()
            
            if not comparison_df.empty:
                print("✅ Comparison DataFrame created successfully!")
                print(f"📊 DataFrame shape: {comparison_df.shape}")
                print(f"📋 Columns: {list(comparison_df.columns)}")
                
                # Test top candidates
                top_candidates = hybrid_generator.get_top_candidates(2)
                if top_candidates:
                    print("✅ Top candidates retrieved successfully!")
                    for candidate in top_candidates:
                        print(f"🏆 Rank {candidate['rank']}: {candidate['refined_sequence']} (Score: {candidate['improvement_score']:.1f})")
                
                # Test CSV export
                csv_filename = hybrid_generator.export_comparison_csv("test_comparison.csv")
                if csv_filename and os.path.exists(csv_filename):
                    print("✅ CSV export successful!")
                    os.remove(csv_filename)  # Clean up
                else:
                    print("⚠️ CSV export failed or file not created")
            
            else:
                print("❌ Comparison DataFrame is empty")
                
        else:
            print(f"❌ Hybrid generation failed: {result['error']}")
            print(f"📝 Explanation: {result.get('explanation', 'No explanation provided')}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


def test_property_analysis():
    """Test the property analysis functionality."""
    
    print("\n🔬 Testing Property Analysis...")
    
    try:
        from peptide_analyzer import AdvancedPeptideAnalyzer
        
        analyzer = AdvancedPeptideAnalyzer()
        test_sequence = "ACDEFGHIKLMN"
        
        result = analyzer.analyze_peptide(test_sequence)
        
        if result['success']:
            print("✅ Property analysis successful!")
            print(f"📊 Molecular Weight: {result.get('molecular_weight', 'N/A')}")
            print(f"📊 Isoelectric Point: {result.get('isoelectric_point', 'N/A')}")
            print(f"📊 GRAVY Score: {result.get('gravy_score', 'N/A')}")
        else:
            print(f"❌ Property analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Property analysis test failed: {str(e)}")


def test_pepinvent_integration():
    """Test PepINVENT integration functionality."""
    
    print("\n🌐 Testing PepINVENT Integration...")
    
    try:
        from pepinvent_integration import PepINVENTIntegration
        
        pepinvent = PepINVENTIntegration("./PepINVENT")
        
        # Test installation check
        install_result = pepinvent.check_installation()
        
        if install_result['success']:
            print("✅ PepINVENT integration successful!")
            print(f"📊 Cloud mode: {install_result.get('cloud_mode', False)}")
        else:
            print(f"⚠️ PepINVENT installation check failed: {install_result.get('error', 'Unknown error')}")
            print("💡 This is expected if PepINVENT is not installed locally")
            
    except Exception as e:
        print(f"❌ PepINVENT integration test failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Hybrid Integration Tests...")
    print("=" * 50)
    
    # Run tests
    test_hybrid_generation()
    test_property_analysis()
    test_pepinvent_integration()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📝 Test Summary:")
    print("• Hybrid generation workflow")
    print("• Property analysis functionality") 
    print("• PepINVENT integration")
    print("• Comparison and export features") 