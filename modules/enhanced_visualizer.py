"""
Enhanced Visualization Module

Provides advanced 3D visualization with residue type highlighting.
"""

try:
    import py3Dmol
    PY3DMOL_AVAILABLE = True
except ImportError:
    PY3DMOL_AVAILABLE = False
    print("Warning: py3Dmol not available. 3D visualization will be limited.")

import streamlit as st
from typing import Dict, List, Any, Optional
import numpy as np
from Bio.PDB import *
import io

class EnhancedVisualizer:
    def __init__(self):
        # Define residue types and colors
        self.residue_types = {
            'hydrophobic': {
                'residues': ['A', 'V', 'I', 'L', 'M', 'F', 'W', 'Y'],
                'color': '#FF6B6B',  # Red
                'description': 'Hydrophobic (non-polar)'
            },
            'charged': {
                'residues': ['R', 'K', 'H', 'D', 'E'],
                'color': '#45B7D1',  # Blue
                'description': 'Charged (positive/negative)'
            },
            'polar': {
                'residues': ['N', 'Q', 'S', 'T', 'C', 'G', 'P'],
                'color': '#4ECDC4',  # Green
                'description': 'Polar (uncharged)'
            }
        }
    
    def display_enhanced_structure(self, pdb_content: str, chain_id: str = 'A'):
        """Display 3D protein structure with residue type highlighting."""
        if not PY3DMOL_AVAILABLE:
            st.warning("⚠️ 3D visualization is not available (py3Dmol not installed).")
            st.info("💡 The ExPASy stability analysis will still work perfectly!")
            return
        
        try:
            # Parse PDB to get residue information
            residue_data = self._parse_residues(pdb_content, chain_id)
            
            # Create viewer
            viewer = py3Dmol.view(width=800, height=600)
            viewer.addModel(pdb_content, "pdb")
            
            # Apply residue type highlighting
            self._apply_residue_highlighting(viewer, residue_data)
            
            # Set view
            viewer.zoomTo()
            
            # Display in Streamlit
            st.components.v1.html(viewer._make_html(), height=600)
            
            # Display legend
            self._display_legend()
            
            # Add instructions
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
    
    def _parse_residues(self, pdb_content: str, chain_id: str = 'A') -> Dict[str, List[str]]:
        """Parse PDB to identify residue types."""
        try:
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure('protein', io.StringIO(pdb_content))
            chain = structure[0][chain_id]
            
            residue_data = {
                'hydrophobic': [],
                'charged': [],
                'polar': []
            }
            
            for residue in chain:
                if residue.get_id()[0] == ' ':  # Only amino acids
                    res_name = residue.get_resname()
                    res_id = residue.get_id()[1]
                    
                    # Categorize residue
                    if res_name in self.residue_types['hydrophobic']['residues']:
                        residue_data['hydrophobic'].append(f"{chain_id} and {res_id}")
                    elif res_name in self.residue_types['charged']['residues']:
                        residue_data['charged'].append(f"{chain_id} and {res_id}")
                    elif res_name in self.residue_types['polar']['residues']:
                        residue_data['polar'].append(f"{chain_id} and {res_id}")
            
            return residue_data
            
        except Exception as e:
            st.warning(f"⚠️ Could not parse residue types: {str(e)}")
            return {'hydrophobic': [], 'charged': [], 'polar': []}
    
    def _apply_residue_highlighting(self, viewer, residue_data: Dict[str, List[str]]):
        """Apply color highlighting based on residue types."""
        
        # Apply hydrophobic highlighting (red)
        if residue_data['hydrophobic']:
            for selection in residue_data['hydrophobic']:
                viewer.addStyle({selection: {}}, {
                    "cartoon": {"color": self.residue_types['hydrophobic']['color']},
                    "stick": {"color": self.residue_types['hydrophobic']['color']}
                })
        
        # Apply charged highlighting (blue)
        if residue_data['charged']:
            for selection in residue_data['charged']:
                viewer.addStyle({selection: {}}, {
                    "cartoon": {"color": self.residue_types['charged']['color']},
                    "stick": {"color": self.residue_types['charged']['color']}
                })
        
        # Apply polar highlighting (green)
        if residue_data['polar']:
            for selection in residue_data['polar']:
                viewer.addStyle({selection: {}}, {
                    "cartoon": {"color": self.residue_types['polar']['color']},
                    "stick": {"color": self.residue_types['polar']['color']}
                })
    
    def _display_legend(self):
        """Display color legend for residue types."""
        st.subheader("🎨 Residue Type Legend")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <div style="width: 20px; height: 20px; background-color: {self.residue_types['hydrophobic']['color']}; 
                     border-radius: 3px; margin-right: 10px;"></div>
                <span>{self.residue_types['hydrophobic']['description']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <div style="width: 20px; height: 20px; background-color: {self.residue_types['charged']['color']}; 
                     border-radius: 3px; margin-right: 10px;"></div>
                <span>{self.residue_types['charged']['description']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <div style="width: 20px; height: 20px; background-color: {self.residue_types['polar']['color']}; 
                     border-radius: 3px; margin-right: 10px;"></div>
                <span>{self.residue_types['polar']['description']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Show residue counts
        st.markdown("**📊 Residue Distribution:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Hydrophobic", len(self._get_residue_list('hydrophobic')))
        with col2:
            st.metric("Charged", len(self._get_residue_list('charged')))
        with col3:
            st.metric("Polar", len(self._get_residue_list('polar')))
    
    def _get_residue_list(self, residue_type: str) -> List[str]:
        """Get list of residues for a given type."""
        return self.residue_types[residue_type]['residues']
    
    def create_interactive_viewer(self, pdb_content: str, chain_id: str = 'A', 
                                show_interactions: bool = True, 
                                show_pockets: bool = True) -> Dict[str, Any]:
        """Create enhanced interactive 3D viewer."""
        if not PY3DMOL_AVAILABLE:
            return {
                'success': False,
                'error': 'py3Dmol not available',
                'explanation': '3D visualization requires py3Dmol package'
            }
        
        try:
            # Create basic viewer with highlighting
            viewer = py3Dmol.view(width=800, height=600)
            viewer.addModel(pdb_content, "pdb")
            
            # Apply residue highlighting
            residue_data = self._parse_residues(pdb_content, chain_id)
            self._apply_residue_highlighting(viewer, residue_data)
            
            viewer.zoomTo()
            
            return {
                'success': True,
                'viewer': viewer,
                'visualization_features': ['3D Structure View', 'Residue Type Highlighting']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Visualization creation failed: {str(e)}"
            }
    
    def create_comparative_view(self, peptides: List[Dict[str, Any]], 
                              target_protein: str) -> Dict[str, Any]:
        """Create comparative visualization."""
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