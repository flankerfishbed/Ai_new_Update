"""
Enhanced Visualization Module

Provides advanced 3D visualization with interaction highlighting, 
binding site visualization, and comparative analysis views.
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
from .interaction_analyzer import InteractionAnalyzer

class EnhancedVisualizer:
    def __init__(self):
        self.interaction_analyzer = InteractionAnalyzer()
        self.color_schemes = {
            'chain': {'A': 'red', 'B': 'blue', 'C': 'green', 'D': 'yellow'},
            'residue_type': {
                'hydrophobic': '#FF6B6B',
                'polar': '#4ECDC4', 
                'charged': '#45B7D1',
                'aromatic': '#96CEB4'
            },
            'interaction': {
                'high': '#FF4757',
                'medium': '#FFA502', 
                'low': '#2ED573'
            }
        }
    
    def create_interactive_viewer(self, pdb_content: str, chain_id: str = 'A', 
                                show_interactions: bool = True, 
                                show_pockets: bool = True) -> Dict[str, Any]:
        """
        Create enhanced interactive 3D viewer with interaction analysis.
        
        Args:
            pdb_content: PDB file content
            chain_id: Chain identifier
            show_interactions: Whether to highlight interaction sites
            show_pockets: Whether to show binding pockets
            
        Returns:
            Dictionary with viewer configuration and analysis data
        """
        if not PY3DMOL_AVAILABLE:
            return {
                'success': False,
                'error': 'py3Dmol not available',
                'explanation': '3D visualization requires py3Dmol package'
            }
        
        try:
            # Analyze interactions if requested
            interaction_data = None
            if show_interactions or show_pockets:
                interaction_result = self.interaction_analyzer.analyze_interaction_sites(pdb_content, chain_id)
                if interaction_result['success']:
                    interaction_data = interaction_result
            
            # Create viewer
            viewer_config = self._create_viewer_config(pdb_content, chain_id, interaction_data, 
                                                     show_interactions, show_pockets)
            
            return {
                'success': True,
                'viewer_config': viewer_config,
                'interaction_data': interaction_data,
                'visualization_features': self._get_visualization_features(show_interactions, show_pockets)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Visualization creation failed: {str(e)}"
            }
    
    def _create_viewer_config(self, pdb_content: str, chain_id: str, 
                            interaction_data: Optional[Dict[str, Any]], 
                            show_interactions: bool, show_pockets: bool) -> Dict[str, Any]:
        """Create configuration for the 3D viewer."""
        
        # Base viewer setup
        viewer_config = {
            'viewer_type': 'py3Dmol',
            'width': 800,
            'height': 600,
            'style': {
                'cartoon': {'color': 'spectrum'},
                'stick': {'radius': 0.5}
            },
            'background': '#000000',
            'view': {'alpha': 0.8, 'beta': 0.8}
        }
        
        # Add interaction highlighting
        if show_interactions and interaction_data:
            viewer_config['interaction_highlights'] = self._create_interaction_highlights(
                interaction_data['interaction_sites']
            )
        
        # Add binding pocket visualization
        if show_pockets and interaction_data:
            viewer_config['pocket_visualization'] = self._create_pocket_visualization(
                interaction_data['binding_pockets']
            )
        
        return viewer_config
    
    def _create_interaction_highlights(self, interaction_sites: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create highlighting configuration for interaction sites."""
        highlights = []
        
        for site in interaction_sites:
            highlight = {
                'residue_id': site['residue_id'],
                'chain_id': site['chain_id'],
                'color': self.color_schemes['interaction'][site['affinity_level']],
                'style': 'sphere',
                'radius': 2.0,
                'opacity': 0.8,
                'label': f"{site['residue_type']} ({site['affinity_level']} affinity)"
            }
            highlights.append(highlight)
        
        return highlights
    
    def _create_pocket_visualization(self, binding_pockets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create visualization configuration for binding pockets."""
        pocket_viz = []
        
        for pocket in binding_pockets:
            viz = {
                'pocket_id': pocket['pocket_id'],
                'center': pocket['center'],
                'radius': pocket['radius'],
                'color': '#FF6B6B',
                'opacity': 0.3,
                'style': 'sphere',
                'label': f"Binding Pocket {pocket['pocket_id']}"
            }
            pocket_viz.append(viz)
        
        return pocket_viz
    
    def _get_visualization_features(self, show_interactions: bool, show_pockets: bool) -> List[str]:
        """Get list of active visualization features."""
        features = ['3D Structure View']
        
        if show_interactions:
            features.append('Interaction Site Highlighting')
        if show_pockets:
            features.append('Binding Pocket Visualization')
        
        return features
    
    def display_enhanced_structure(self, pdb_content: str, chain_id: str = 'A'):
        """Display enhanced 3D structure with interaction analysis."""
        if not PY3DMOL_AVAILABLE:
            st.warning("⚠️ 3D visualization is not available (py3Dmol not installed).")
            st.info("💡 The ExPASy stability analysis will still work perfectly!")
            return
        
        try:
            # Create viewer
            viewer_result = self.create_interactive_viewer(pdb_content, chain_id)
            
            if viewer_result['success']:
                # Display viewer
                viewer = py3Dmol.view(width=800, height=600)
                viewer.addModel(pdb_content, "pdb")
                
                # Apply styling
                viewer.setStyle({}, {"cartoon": {"color": "spectrum"}})
                
                # Apply interaction highlights if available
                if 'interaction_highlights' in viewer_result['viewer_config']:
                    self._apply_interaction_highlights(viewer, viewer_result['viewer_config']['interaction_highlights'])
                
                # Apply pocket visualization if available
                if 'pocket_visualization' in viewer_result['viewer_config']:
                    self._apply_pocket_visualization(viewer, viewer_result['viewer_config']['pocket_visualization'])
                
                # Set view
                viewer.zoomTo()
                viewer.show()
                
                # Display interaction summary if available
                if viewer_result['interaction_data']:
                    self._display_interaction_summary(viewer_result['interaction_data'])
                
                # Display features
                st.info(f"🎨 **Active Features:** {', '.join(viewer_result['visualization_features'])}")
                
            else:
                st.error(f"❌ Visualization failed: {viewer_result['error']}")
                st.info(f"💡 {viewer_result['explanation']}")
                
        except Exception as e:
            st.error(f"❌ Visualization error: {str(e)}")
            st.info("💡 The ExPASy stability analysis will still work perfectly!")
    
    def _apply_interaction_highlights(self, viewer, highlights: List[Dict[str, Any]]):
        """Apply interaction site highlights to the viewer."""
        for highlight in highlights:
            selection = f"{highlight['chain_id']} and {highlight['residue_id']}"
            viewer.addStyle({selection: {}}, {
                "sphere": {
                    "color": highlight['color'],
                    "radius": highlight['radius'],
                    "opacity": highlight['opacity']
                }
            })
    
    def _apply_pocket_visualization(self, viewer, pocket_viz: List[Dict[str, Any]]):
        """Apply binding pocket visualization to the viewer."""
        for viz in pocket_viz:
            viewer.addSphere({
                "center": viz['center'],
                "radius": viz['radius'],
                "color": viz['color'],
                "opacity": viz['opacity']
            })
    
    def _display_interaction_summary(self, interaction_data: Dict[str, Any]):
        """Display summary of interaction analysis."""
        summary = interaction_data['summary']
        
        st.subheader("🎯 Interaction Analysis Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Interaction Sites", summary['total_interaction_sites'])
        with col2:
            st.metric("High Affinity Sites", summary['high_affinity_sites'])
        with col3:
            st.metric("Binding Pockets", summary['binding_pockets_found'])
        
        if summary['recommendations']:
            st.info("💡 **Interaction Analysis Recommendations:**")
            for rec in summary['recommendations']:
                st.write(f"• {rec}")
    
    def create_comparative_view(self, peptides: List[Dict[str, Any]], 
                              target_protein: str) -> Dict[str, Any]:
        """
        Create comparative visualization of multiple peptides against target protein.
        
        Args:
            peptides: List of peptide dictionaries
            target_protein: Target protein sequence or structure
            
        Returns:
            Dictionary with comparative analysis results
        """
        if not PY3DMOL_AVAILABLE:
            return {
                'success': False,
                'error': 'py3Dmol not available',
                'explanation': 'Comparative visualization requires py3Dmol package'
            }
        
        try:
            comparative_data = {
                'peptides': [],
                'target_protein': target_protein,
                'binding_analysis': {},
                'visualization_config': {}
            }
            
            # Analyze each peptide
            for peptide in peptides:
                peptide_analysis = self._analyze_peptide_binding(peptide, target_protein)
                comparative_data['peptides'].append(peptide_analysis)
            
            # Calculate comparative metrics
            comparative_data['binding_analysis'] = self._compare_binding_characteristics(
                peptides[0], peptides
            )
            
            # Generate summary
            comparative_data['summary'] = self._generate_comparative_summary(comparative_data)
            
            return {
                'success': True,
                'data': comparative_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Comparative analysis failed: {str(e)}"
            }
    
    def _analyze_peptide_binding(self, peptide: Dict[str, Any], target_protein: str) -> Dict[str, Any]:
        """Analyze binding characteristics of a single peptide."""
        sequence = peptide['sequence']
        
        return {
            'sequence': sequence,
            'binding_score': self._calculate_binding_score(sequence),
            'complementarity': self._assess_complementarity(sequence, target_protein),
            'interaction_potential': self._assess_interaction_potential(sequence)
        }
    
    def _calculate_binding_score(self, sequence: str) -> float:
        """Calculate binding score based on sequence properties."""
        # Simplified scoring based on hydrophobicity and charge
        hydrophobic_aa = ['A', 'V', 'I', 'L', 'M', 'F', 'W', 'Y']
        charged_aa = ['R', 'K', 'H', 'D', 'E']
        
        hydrophobic_count = sum(1 for aa in sequence if aa in hydrophobic_aa)
        charged_count = sum(1 for aa in sequence if aa in charged_aa)
        
        # Normalize by sequence length
        length = len(sequence)
        hydrophobic_ratio = hydrophobic_count / length
        charged_ratio = charged_count / length
        
        # Calculate score (0-1 scale)
        score = (hydrophobic_ratio * 0.6) + (charged_ratio * 0.4)
        return min(score, 1.0)
    
    def _assess_complementarity(self, sequence: str, target_protein: str) -> Dict[str, Any]:
        """Assess complementarity between peptide and target protein."""
        return {
            'hydrophobic_complementarity': 0.7,  # Placeholder
            'charge_complementarity': 0.6,       # Placeholder
            'size_complementarity': 0.8,         # Placeholder
            'overall_complementarity': 0.7       # Placeholder
        }
    
    def _assess_interaction_potential(self, sequence: str) -> Dict[str, Any]:
        """Assess interaction potential of the peptide."""
        return {
            'hydrogen_bond_potential': 0.6,      # Placeholder
            'electrostatic_potential': 0.5,      # Placeholder
            'hydrophobic_potential': 0.7,        # Placeholder
            'overall_potential': 0.6             # Placeholder
        }
    
    def _compare_binding_characteristics(self, peptide: Dict[str, Any], 
                                       all_peptides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare binding characteristics across multiple peptides."""
        return {
            'best_binding_score': max(p['binding_score'] for p in all_peptides),
            'average_binding_score': sum(p['binding_score'] for p in all_peptides) / len(all_peptides),
            'score_variance': 0.1,  # Placeholder
            'ranking': sorted(all_peptides, key=lambda x: x['binding_score'], reverse=True)
        }
    
    def _generate_comparative_summary(self, comparative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of comparative analysis."""
        return {
            'total_peptides': len(comparative_data['peptides']),
            'best_performer': comparative_data['peptides'][0]['sequence'],
            'average_performance': 0.7,  # Placeholder
            'recommendations': [
                "Consider peptide with highest binding score for experimental validation",
                "Evaluate complementarity with target protein structure",
                "Assess interaction potential for drug development"
            ]
        } 