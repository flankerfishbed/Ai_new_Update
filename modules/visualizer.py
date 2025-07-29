"""
Protein Visualizer Module

This module provides functionality to visualize protein structures in 3D using py3Dmol.
Each function returns clean, explainable output suitable for LLM prompt context.
"""

import py3Dmol
import streamlit as st
from typing import Dict, Any, Optional
import tempfile
import os


class ProteinVisualizer:
    """
    A modular visualizer for protein structures using py3Dmol.
    
    Returns clean, explainable output with both visualization and human-readable explanations.
    """
    
    def __init__(self):
        self.view_width = 600
        self.view_height = 400
    
    def display_structure(self, pdb_content: str, chain_id: str = "A", 
                         style: str = "cartoon", color_scheme: str = "chain") -> Dict[str, Any]:
        """
        Display protein structure in 3D using py3Dmol.
        
        Args:
            pdb_content: Raw PDB file content as string
            chain_id: Chain identifier to highlight (default: "A")
            style: Visualization style (cartoon, line, stick, sphere)
            color_scheme: Color scheme (chain, b-factor, secondary structure)
            
        Returns:
            Dictionary with success status and visualization info
        """
        try:
            # Create temporary file for py3Dmol
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdb', delete=False) as tmp_file:
                tmp_file.write(pdb_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Create 3D viewer
                view = py3Dmol.view(width=self.view_width, height=self.view_height)
                
                # Add structure to viewer
                view.addModel(pdb_content, "pdb")
                
                # Set visualization style
                if style == "cartoon":
                    view.setStyle({}, {"cartoon": {}})
                elif style == "line":
                    view.setStyle({}, {"line": {}})
                elif style == "stick":
                    view.setStyle({}, {"stick": {}})
                elif style == "sphere":
                    view.setStyle({}, {"sphere": {}})
                
                # Set color scheme
                if color_scheme == "chain":
                    view.setStyle({"chain": chain_id}, {"cartoon": {"color": "red"}})
                    view.setStyle({"chain": {"$ne": chain_id}}, {"cartoon": {"color": "gray"}})
                elif color_scheme == "b-factor":
                    view.setStyle({}, {"cartoon": {"colorscheme": "b-factor"}})
                elif color_scheme == "secondary":
                    view.setStyle({}, {"cartoon": {"colorscheme": "secondary structure"}})
                
                # Center and zoom the view
                view.zoomTo()
                
                # Display in Streamlit
                st.components.v1.html(view._make_html(), height=self.view_height + 50)
                
                # Generate explanation
                explanation = self._generate_visualization_explanation(chain_id, style, color_scheme)
                
                return {
                    'success': True,
                    'chain_id': chain_id,
                    'style': style,
                    'color_scheme': color_scheme,
                    'explanation': explanation
                }
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Failed to visualize protein structure: {str(e)}"
            }
    
    def display_surface_highlighted(self, pdb_content: str, surface_residues: list, 
                                  chain_id: str = "A") -> Dict[str, Any]:
        """
        Display protein structure with surface residues highlighted.
        
        Args:
            pdb_content: Raw PDB file content as string
            surface_residues: List of surface residue dictionaries
            chain_id: Chain identifier
            
        Returns:
            Dictionary with success status and visualization info
        """
        try:
            # Create 3D viewer
            view = py3Dmol.view(width=self.view_width, height=self.view_height)
            
            # Add structure to viewer
            view.addModel(pdb_content, "pdb")
            
            # Set default style
            view.setStyle({}, {"cartoon": {"color": "lightgray"}})
            
            # Highlight surface residues
            for residue in surface_residues[:20]:  # Limit to top 20 for performance
                res_id = residue['residue_id']
                res_type = residue['residue_type']
                
                # Color by residue type
                if res_type == 'hydrophobic':
                    color = "orange"
                elif res_type == 'charged':
                    color = "red"
                else:  # polar
                    color = "blue"
                
                # Highlight residue
                view.setStyle({"chain": chain_id, "resi": res_id}, 
                            {"stick": {"color": color, "radius": 0.3}})
            
            # Center and zoom the view
            view.zoomTo()
            
            # Display in Streamlit
            st.components.v1.html(view._make_html(), height=self.view_height + 50)
            
            # Generate explanation
            explanation = self._generate_surface_highlight_explanation(surface_residues, chain_id)
            
            return {
                'success': True,
                'highlighted_residues': len(surface_residues),
                'chain_id': chain_id,
                'explanation': explanation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Failed to highlight surface residues: {str(e)}"
            }
    
    def _generate_visualization_explanation(self, chain_id: str, style: str, 
                                          color_scheme: str) -> str:
        """
        Generate a human-readable explanation of the visualization.
        
        Args:
            chain_id: Chain identifier
            style: Visualization style
            color_scheme: Color scheme used
            
        Returns:
            Human-readable explanation
        """
        explanation = f"""
        **3D Protein Structure Visualization:**
        
        **Display Settings:**
        - Chain ID: {chain_id}
        - Visualization Style: {style}
        - Color Scheme: {color_scheme}
        
        **Interactive Features:**
        - Rotate: Click and drag to rotate the structure
        - Zoom: Scroll to zoom in/out
        - Pan: Right-click and drag to pan
        - Reset: Double-click to reset view
        
        **Visualization Information:**
        The protein structure is displayed in 3D space using the uploaded PDB coordinates.
        The {style} representation shows the protein backbone and side chains.
        The {color_scheme} color scheme helps identify different structural features.
        """
        
        return explanation.strip()
    
    def _generate_surface_highlight_explanation(self, surface_residues: list, 
                                              chain_id: str) -> str:
        """
        Generate a human-readable explanation of surface residue highlighting.
        
        Args:
            surface_residues: List of surface residue dictionaries
            chain_id: Chain identifier
            
        Returns:
            Human-readable explanation
        """
        # Count residue types
        hydrophobic_count = sum(1 for r in surface_residues if r['residue_type'] == 'hydrophobic')
        charged_count = sum(1 for r in surface_residues if r['residue_type'] == 'charged')
        polar_count = sum(1 for r in surface_residues if r['residue_type'] == 'polar')
        
        explanation = f"""
        **Surface Residue Highlighting:**
        
        **Highlighted Residues:**
        - Total surface residues: {len(surface_residues)}
        - Hydrophobic residues (orange): {hydrophobic_count}
        - Charged residues (red): {charged_count}
        - Polar residues (blue): {polar_count}
        
        **Color Legend:**
        - Orange: Hydrophobic surface residues (high SASA)
        - Red: Charged surface residues (high SASA)
        - Blue: Polar surface residues (high SASA)
        - Gray: Non-surface residues
        
        **Surface Analysis:**
        Surface-exposed residues are highlighted based on their solvent-accessible surface area (SASA).
        These residues are potential targets for peptide binding due to their accessibility.
        """
        
        return explanation.strip()
    
    def create_animation(self, pdb_content: str, chain_id: str = "A", 
                        frames: int = 36) -> Dict[str, Any]:
        """
        Create a simple rotation animation of the protein structure.
        
        Args:
            pdb_content: Raw PDB file content as string
            chain_id: Chain identifier
            frames: Number of animation frames
            
        Returns:
            Dictionary with success status and animation info
        """
        try:
            # Create 3D viewer
            view = py3Dmol.view(width=self.view_width, height=self.view_height)
            
            # Add structure to viewer
            view.addModel(pdb_content, "pdb")
            
            # Set style
            view.setStyle({}, {"cartoon": {}})
            view.setStyle({"chain": chain_id}, {"cartoon": {"color": "red"}})
            
            # Create rotation animation
            view.spin([0, 1, 0], 2)  # Rotate around Y-axis at 2 degrees per frame
            
            # Display in Streamlit
            st.components.v1.html(view._make_html(), height=self.view_height + 50)
            
            return {
                'success': True,
                'chain_id': chain_id,
                'frames': frames,
                'explanation': f"Created rotation animation with {frames} frames around the Y-axis."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Failed to create animation: {str(e)}"
            } 