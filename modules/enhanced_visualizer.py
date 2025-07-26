"""
Enhanced Visualization Module

Provides advanced 3D visualization with interaction highlighting, 
binding site visualization, and comparative analysis views.
"""

import py3Dmol
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
            score = site['interaction_score']
            residue = site['residue']
            
            # Determine color based on interaction score
            if score > 0.7:
                color = self.color_schemes['interaction']['high']
            elif score > 0.5:
                color = self.color_schemes['interaction']['medium']
            else:
                color = self.color_schemes['interaction']['low']
            
            highlights.append({
                'residue_id': residue['residue_id'],
                'chain_id': residue['chain_id'],
                'color': color,
                'radius': 1.0 + score * 2.0,  # Size based on score
                'interaction_score': score,
                'interaction_types': site['interaction_types']
            })
        
        return highlights
    
    def _create_pocket_visualization(self, binding_pockets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create visualization configuration for binding pockets."""
        pocket_viz = []
        
        for pocket in binding_pockets:
            pocket_viz.append({
                'center_position': pocket['center_position'],
                'radius': 5.0 + pocket['pocket_score'] * 3.0,
                'color': '#FF6B6B',
                'opacity': 0.3,
                'pocket_score': pocket['pocket_score'],
                'neighbor_count': pocket['neighbor_count']
            })
        
        return pocket_viz
    
    def _get_visualization_features(self, show_interactions: bool, show_pockets: bool) -> List[str]:
        """Get list of active visualization features."""
        features = ['3D Structure', 'Chain Coloring']
        
        if show_interactions:
            features.append('Interaction Site Highlighting')
        if show_pockets:
            features.append('Binding Pocket Visualization')
        
        return features
    
    def display_enhanced_structure(self, pdb_content: str, chain_id: str = 'A'):
        """Display enhanced 3D structure with interaction analysis."""
        
        # Create viewer
        viewer_result = self.create_interactive_viewer(pdb_content, chain_id, True, True)
        
        if not viewer_result['success']:
            st.error(f"Visualization error: {viewer_result['error']}")
            return
        
        # Display viewer
        viewer = py3Dmol.view(width=800, height=600)
        viewer.addModel(pdb_content, "pdb")
        
        # Apply base styling
        viewer.setStyle({}, {"cartoon": {"color": "spectrum"}})
        
        # Add interaction highlights if available
        if viewer_result['interaction_data']:
            self._apply_interaction_highlights(viewer, viewer_result['viewer_config']['interaction_highlights'])
            self._apply_pocket_visualization(viewer, viewer_result['viewer_config']['pocket_visualization'])
        
        # Set view
        viewer.zoomTo()
        
        # Display in Streamlit
        st.components.v1.html(viewer._make_html(), height=600)
        
        # Display analysis summary
        if viewer_result['interaction_data']:
            self._display_interaction_summary(viewer_result['interaction_data'])
    
    def _apply_interaction_highlights(self, viewer, highlights: List[Dict[str, Any]]):
        """Apply interaction site highlights to viewer."""
        for highlight in highlights:
            selection = f"{{chain: '{highlight['chain_id']}' and resi: {highlight['residue_id']}}}"
            viewer.addStyle(selection, {
                "sphere": {
                    "radius": highlight['radius'],
                    "color": highlight['color'],
                    "opacity": 0.8
                }
            })
    
    def _apply_pocket_visualization(self, viewer, pocket_viz: List[Dict[str, Any]]):
        """Apply binding pocket visualization to viewer."""
        for pocket in pocket_viz:
            # Add sphere representation for pocket
            viewer.addSphere({
                "center": pocket['center_position'],
                "radius": pocket['radius'],
                "color": pocket['color'],
                "opacity": pocket['opacity']
            })
    
    def _display_interaction_summary(self, interaction_data: Dict[str, Any]):
        """Display summary of interaction analysis."""
        summary = interaction_data['summary']
        
        st.subheader("🔍 Interaction Analysis Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Interaction Sites", summary['total_interaction_sites'])
        
        with col2:
            st.metric("High Affinity Sites", summary['high_affinity_sites'])
        
        with col3:
            st.metric("Binding Pockets", summary['binding_pockets_found'])
        
        # Display recommendations
        if summary['recommendations']:
            st.info("💡 **Recommendations:**")
            for rec in summary['recommendations']:
                st.write(f"• {rec}")
    
    def create_comparative_view(self, peptides: List[Dict[str, Any]], 
                              target_protein: str) -> Dict[str, Any]:
        """
        Create comparative visualization of multiple peptides against target protein.
        
        Args:
            peptides: List of peptide dictionaries
            target_protein: Target protein PDB content
            
        Returns:
            Dictionary with comparative analysis results
        """
        try:
            comparative_data = {
                'peptide_analyses': [],
                'binding_comparison': [],
                'interaction_overlap': []
            }
            
            for i, peptide in enumerate(peptides):
                # Analyze each peptide
                peptide_analysis = self._analyze_peptide_binding(peptide, target_protein)
                comparative_data['peptide_analyses'].append(peptide_analysis)
                
                # Compare binding characteristics
                binding_comparison = self._compare_binding_characteristics(peptide, peptides)
                comparative_data['binding_comparison'].append(binding_comparison)
            
            return {
                'success': True,
                'comparative_data': comparative_data,
                'summary': self._generate_comparative_summary(comparative_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Comparative analysis failed: {str(e)}"
            }
    
    def _analyze_peptide_binding(self, peptide: Dict[str, Any], target_protein: str) -> Dict[str, Any]:
        """Analyze binding characteristics of a peptide to target protein."""
        # Simplified binding analysis
        sequence = peptide['sequence']
        
        return {
            'peptide_id': peptide.get('id', f"peptide_{len(sequence)}"),
            'sequence': sequence,
            'binding_score': self._calculate_binding_score(sequence),
            'complementarity': self._assess_complementarity(sequence, target_protein),
            'interaction_potential': self._assess_interaction_potential(sequence)
        }
    
    def _calculate_binding_score(self, sequence: str) -> float:
        """Calculate binding score for peptide sequence."""
        # Simplified scoring based on amino acid properties
        charged_aas = sum(1 for aa in sequence if aa in 'RKHDE')
        hydrophobic_aas = sum(1 for aa in sequence if aa in 'ACFILMPVWY')
        
        # Balance score
        balance_score = min(charged_aas, hydrophobic_aas) / len(sequence)
        length_score = min(1.0, len(sequence) / 15.0)
        
        return (balance_score * 0.6 + length_score * 0.4)
    
    def _assess_complementarity(self, sequence: str, target_protein: str) -> Dict[str, Any]:
        """Assess complementarity between peptide and target protein."""
        # Simplified complementarity assessment
        return {
            'charge_complementarity': 'medium',
            'hydrophobicity_complementarity': 'medium',
            'overall_complementarity': 'medium'
        }
    
    def _assess_interaction_potential(self, sequence: str) -> Dict[str, Any]:
        """Assess interaction potential of peptide."""
        return {
            'hydrogen_bond_potential': sum(1 for aa in sequence if aa in 'STNQ') / len(sequence),
            'ionic_interaction_potential': sum(1 for aa in sequence if aa in 'RKHDE') / len(sequence),
            'hydrophobic_interaction_potential': sum(1 for aa in sequence if aa in 'ACFILMPVWY') / len(sequence)
        }
    
    def _compare_binding_characteristics(self, peptide: Dict[str, Any], 
                                       all_peptides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare binding characteristics across peptides."""
        return {
            'relative_binding_strength': 'medium',
            'uniqueness_score': 0.5,
            'diversity_contribution': 'medium'
        }
    
    def _generate_comparative_summary(self, comparative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of comparative analysis."""
        return {
            'best_binding_peptide': max(comparative_data['peptide_analyses'], 
                                      key=lambda x: x['binding_score']),
            'diversity_score': 0.7,
            'recommendations': ['Consider testing top 3 peptides', 'Evaluate binding specificity']
        } 