"""
Protein-Protein Interaction Analysis Module

Analyzes potential interaction sites and binding interfaces between peptides and target proteins.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from Bio.PDB import *
from Bio.PDB.DSSP import DSSP
import warnings
import io
warnings.filterwarnings('ignore')

class InteractionAnalyzer:
    def __init__(self):
        self.interaction_types = {
            'hydrogen_bond': ['N', 'O', 'S'],
            'ionic': ['R', 'K', 'H', 'D', 'E'],
            'hydrophobic': ['A', 'C', 'F', 'I', 'L', 'M', 'P', 'V', 'W', 'Y'],
            'aromatic': ['F', 'W', 'Y']
        }
    
    def analyze_interaction_sites(self, pdb_content: str, chain_id: str = 'A') -> Dict[str, Any]:
        """
        Analyze potential interaction sites on the protein surface.
        
        Args:
            pdb_content: PDB file content
            chain_id: Chain identifier
            
        Returns:
            Dictionary with interaction analysis results
        """
        try:
            # Parse structure
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure('protein', io.StringIO(pdb_content))
            
            # Get the specified chain
            chain = structure[0][chain_id]
            
            # Analyze surface residues
            surface_residues = self._identify_surface_residues(chain)
            interaction_sites = self._find_interaction_sites(surface_residues)
            binding_pockets = self._identify_binding_pockets(chain)
            
            return {
                'success': True,
                'surface_residues': surface_residues,
                'interaction_sites': interaction_sites,
                'binding_pockets': binding_pockets,
                'summary': self._generate_interaction_summary(interaction_sites, binding_pockets)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Interaction analysis failed: {str(e)}"
            }
    
    def _identify_surface_residues(self, chain) -> List[Dict[str, Any]]:
        """Identify surface-exposed residues."""
        surface_residues = []
        
        for residue in chain:
            if residue.get_id()[0] == ' ':  # Only amino acids
                # Calculate solvent accessibility (simplified)
                ca_atom = residue['CA']
                neighbors = self._count_neighbors(ca_atom, chain, radius=8.0)
                
                if neighbors < 15:  # Surface residue threshold
                    surface_residues.append({
                        'residue_id': residue.get_id()[1],
                        'residue_name': residue.get_resname(),
                        'chain_id': chain.get_id(),
                        'accessibility': 1.0 - (neighbors / 20.0),  # Normalized accessibility
                        'position': ca_atom.get_coord().tolist(),
                        'properties': self._get_residue_properties(residue)
                    })
        
        return surface_residues
    
    def _find_interaction_sites(self, surface_residues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find potential interaction sites."""
        interaction_sites = []
        
        for residue in surface_residues:
            site_score = self._calculate_interaction_score(residue)
            
            if site_score > 0.5:  # Threshold for interaction potential
                interaction_sites.append({
                    'residue': residue,
                    'interaction_score': site_score,
                    'interaction_types': self._predict_interaction_types(residue),
                    'binding_potential': self._assess_binding_potential(residue)
                })
        
        # Sort by interaction score
        interaction_sites.sort(key=lambda x: x['interaction_score'], reverse=True)
        return interaction_sites
    
    def _identify_binding_pockets(self, chain) -> List[Dict[str, Any]]:
        """Identify potential binding pockets."""
        pockets = []
        
        # Simplified pocket detection based on surface curvature
        surface_residues = [r for r in chain if r.get_id()[0] == ' ']
        
        for i, residue in enumerate(surface_residues):
            if residue.get_id()[0] == ' ':  # Only amino acids
                ca_atom = residue['CA']
                neighbors = self._get_nearby_residues(ca_atom, surface_residues, radius=6.0)
                
                if len(neighbors) >= 3:  # Potential pocket
                    pocket_score = self._calculate_pocket_score(residue, neighbors)
                    
                    if pocket_score > 0.6:
                        pockets.append({
                            'center_residue': residue.get_resname(),
                            'center_position': ca_atom.get_coord().tolist(),
                            'pocket_score': pocket_score,
                            'neighbor_count': len(neighbors),
                            'pocket_properties': self._analyze_pocket_properties(neighbors)
                        })
        
        return pockets
    
    def _calculate_interaction_score(self, residue: Dict[str, Any]) -> float:
        """Calculate interaction potential score."""
        residue_name = residue['residue_name']
        accessibility = residue['accessibility']
        
        # Base score from accessibility
        score = accessibility * 0.4
        
        # Add contribution from residue type
        if residue_name in self.interaction_types['ionic']:
            score += 0.3  # Charged residues
        elif residue_name in self.interaction_types['hydrophobic']:
            score += 0.2  # Hydrophobic residues
        elif residue_name in self.interaction_types['aromatic']:
            score += 0.25  # Aromatic residues
        
        return min(1.0, score)
    
    def _predict_interaction_types(self, residue: Dict[str, Any]) -> List[str]:
        """Predict possible interaction types."""
        residue_name = residue['residue_name']
        interaction_types = []
        
        if residue_name in self.interaction_types['ionic']:
            interaction_types.append('ionic')
        if residue_name in self.interaction_types['hydrophobic']:
            interaction_types.append('hydrophobic')
        if residue_name in self.interaction_types['aromatic']:
            interaction_types.append('aromatic')
        if residue_name in ['N', 'Q', 'S', 'T']:
            interaction_types.append('hydrogen_bond')
        
        return interaction_types
    
    def _assess_binding_potential(self, residue: Dict[str, Any]) -> Dict[str, Any]:
        """Assess binding potential for this residue."""
        residue_name = residue['residue_name']
        
        binding_assessment = {
            'peptide_compatibility': 'medium',
            'binding_strength': 'medium',
            'specificity': 'medium'
        }
        
        # Adjust based on residue properties
        if residue_name in ['R', 'K', 'D', 'E']:
            binding_assessment['peptide_compatibility'] = 'high'
            binding_assessment['binding_strength'] = 'high'
        elif residue_name in ['F', 'W', 'Y']:
            binding_assessment['specificity'] = 'high'
        
        return binding_assessment
    
    def _calculate_pocket_score(self, center_residue, neighbors) -> float:
        """Calculate binding pocket score."""
        # Simplified pocket scoring
        neighbor_diversity = len(set(n.get_resname() for n in neighbors))
        pocket_depth = self._estimate_pocket_depth(center_residue, neighbors)
        
        score = (neighbor_diversity * 0.3 + pocket_depth * 0.7)
        return min(1.0, score)
    
    def _analyze_pocket_properties(self, neighbors) -> Dict[str, Any]:
        """Analyze properties of binding pocket."""
        residue_types = [n.get_resname() for n in neighbors]
        
        return {
            'hydrophobic_ratio': sum(1 for r in residue_types if r in self.interaction_types['hydrophobic']) / len(residue_types),
            'charged_ratio': sum(1 for r in residue_types if r in self.interaction_types['ionic']) / len(residue_types),
            'aromatic_ratio': sum(1 for r in residue_types if r in self.interaction_types['aromatic']) / len(residue_types),
            'residue_diversity': len(set(residue_types))
        }
    
    def _count_neighbors(self, atom, chain, radius: float) -> int:
        """Count neighboring atoms within radius."""
        count = 0
        for residue in chain:
            for other_atom in residue:
                if other_atom != atom:
                    distance = atom - other_atom
                    if distance < radius:
                        count += 1
        return count
    
    def _get_nearby_residues(self, atom, residues, radius: float):
        """Get residues within radius of atom."""
        nearby = []
        for residue in residues:
            if residue.get_id()[0] == ' ':
                ca_atom = residue['CA']
                distance = atom - ca_atom
                if distance < radius:
                    nearby.append(residue)
        return nearby
    
    def _estimate_pocket_depth(self, center_residue, neighbors) -> float:
        """Estimate pocket depth."""
        # Simplified depth estimation
        return min(1.0, len(neighbors) / 10.0)
    
    def _get_residue_properties(self, residue) -> Dict[str, Any]:
        """Get physicochemical properties of residue."""
        residue_name = residue.get_resname()
        
        return {
            'is_charged': residue_name in self.interaction_types['ionic'],
            'is_hydrophobic': residue_name in self.interaction_types['hydrophobic'],
            'is_aromatic': residue_name in self.interaction_types['aromatic'],
            'can_hbond': residue_name in ['N', 'Q', 'S', 'T']
        }
    
    def _generate_interaction_summary(self, interaction_sites: List[Dict[str, Any]], 
                                   binding_pockets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of interaction analysis."""
        return {
            'total_interaction_sites': len(interaction_sites),
            'high_affinity_sites': len([s for s in interaction_sites if s['interaction_score'] > 0.7]),
            'binding_pockets_found': len(binding_pockets),
            'best_interaction_sites': interaction_sites[:5] if interaction_sites else [],
            'best_binding_pockets': binding_pockets[:3] if binding_pockets else [],
            'recommendations': self._generate_interaction_recommendations(interaction_sites, binding_pockets)
        }
    
    def _generate_interaction_recommendations(self, interaction_sites: List[Dict[str, Any]], 
                                           binding_pockets: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on interaction analysis."""
        recommendations = []
        
        if len(interaction_sites) > 10:
            recommendations.append("Multiple interaction sites available - consider targeting specific regions")
        
        if binding_pockets:
            recommendations.append("Binding pockets identified - focus peptide design on pocket-complementary sequences")
        
        high_affinity_sites = [s for s in interaction_sites if s['interaction_score'] > 0.7]
        if high_affinity_sites:
            recommendations.append("High-affinity interaction sites detected - prioritize these regions")
        
        return recommendations 