"""
Simple Protein Visualization Module

Provides basic 3D visualization of uploaded protein structures.
"""

try:
    import py3Dmol
    PY3DMOL_AVAILABLE = True
except ImportError:
    PY3DMOL_AVAILABLE = False
    print("Warning: py3Dmol not available. 3D visualization will be limited.")

import streamlit as st
from typing import Dict, List, Any, Optional

class EnhancedVisualizer:
    def __init__(self):
        pass
    
    def display_enhanced_structure(self, pdb_content: str, chain_id: str = 'A'):
        """Display simple 3D protein structure."""
        if not PY3DMOL_AVAILABLE:
            st.warning("⚠️ 3D visualization is not available (py3Dmol not installed).")
            st.info("💡 The ExPASy stability analysis will still work perfectly!")
            return
        
        try:
            # Create simple viewer
            viewer = py3Dmol.view(width=800, height=600)
            viewer.addModel(pdb_content, "pdb")
            
            # Apply basic styling
            viewer.setStyle({}, {"cartoon": {"color": "spectrum"}})
            
            # Set view
            viewer.zoomTo()
            
            # Display in Streamlit
            st.components.v1.html(viewer._make_html(), height=600)
            
            # Add simple instructions
            st.info("""
            **🎨 3D Protein Viewer Controls:**
            - **Rotate:** Click and drag to rotate the molecule
            - **Zoom:** Scroll to zoom in/out  
            - **Pan:** Right-click and drag to move the view
            - **Reset:** Double-click to reset the view
            """)
            
        except Exception as e:
            st.error(f"❌ Visualization error: {str(e)}")
            st.info("💡 The ExPASy stability analysis will still work perfectly!")
    
    def create_interactive_viewer(self, pdb_content: str, chain_id: str = 'A', 
                                show_interactions: bool = True, 
                                show_pockets: bool = True) -> Dict[str, Any]:
        """Create simple interactive 3D viewer."""
        if not PY3DMOL_AVAILABLE:
            return {
                'success': False,
                'error': 'py3Dmol not available',
                'explanation': '3D visualization requires py3Dmol package'
            }
        
        try:
            # Create basic viewer
            viewer = py3Dmol.view(width=800, height=600)
            viewer.addModel(pdb_content, "pdb")
            viewer.setStyle({}, {"cartoon": {"color": "spectrum"}})
            viewer.zoomTo()
            
            return {
                'success': True,
                'viewer': viewer,
                'visualization_features': ['3D Structure View']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Visualization creation failed: {str(e)}"
            }
    
    def create_comparative_view(self, peptides: List[Dict[str, Any]], 
                              target_protein: str) -> Dict[str, Any]:
        """Create simple comparative visualization."""
        if not PY3DMOL_AVAILABLE:
            return {
                'success': False,
                'error': 'py3Dmol not available',
                'explanation': 'Comparative visualization requires py3Dmol package'
            }
        
        try:
            return {
                'success': True,
                'data': {
                    'peptides': peptides,
                    'target_protein': target_protein
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Comparative analysis failed: {str(e)}"
            } 