"""
Advanced Peptide Analysis Module

Provides comprehensive analysis of peptide properties including:
- Secondary structure prediction
- Binding affinity estimation
- Stability analysis
- Immunogenicity prediction
"""

import numpy as np
from typing import Dict, List, Any
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import re

class AdvancedPeptideAnalyzer:
    def __init__(self):
        self.aa_properties = {
            'hydrophobicity': {'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5, 'E': -3.5, 'Q': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5, 'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6, 'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2},
            'charge': {'R': 1, 'K': 1, 'H': 0.5, 'D': -1, 'E': -1, 'C': -0.5},
            'polarity': {'R': 10.76, 'K': 9.74, 'D': 13.82, 'E': 13.57, 'N': 8.33, 'Q': 8.62, 'H': 8.18, 'S': 9.21, 'T': 8.16, 'Y': 6.11, 'C': 5.07, 'W': 5.89, 'A': 8.10, 'G': 7.03, 'I': 5.94, 'L': 4.76, 'M': 5.74, 'F': 5.48, 'P': 6.30, 'V': 5.96}
        }
    
    def comprehensive_analysis(self, peptide_sequence: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of peptide properties.
        
        Args:
            peptide_sequence: Amino acid sequence
            
        Returns:
            Dictionary with all analysis results
        """
        try:
            analysis = ProteinAnalysis(peptide_sequence)
            
            results = {
                'basic_properties': self._calculate_basic_properties(peptide_sequence),
                'secondary_structure': self._predict_secondary_structure(analysis),
                'binding_affinity': self._estimate_binding_affinity(peptide_sequence),
                'stability': self._analyze_stability(peptide_sequence),
                'immunogenicity': self._predict_immunogenicity(peptide_sequence),
                'solubility_profile': self._calculate_solubility_profile(peptide_sequence),
                'interaction_potential': self._analyze_interaction_potential(peptide_sequence)
            }
            
            return {
                'success': True,
                'analysis': results,
                'summary': self._generate_summary(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Analysis failed: {str(e)}"
            }
    
    def _calculate_basic_properties(self, sequence: str) -> Dict[str, Any]:
        """Calculate basic peptide properties."""
        analysis = ProteinAnalysis(sequence)
        
        return {
            'molecular_weight': analysis.molecular_weight(),
            'isoelectric_point': analysis.isoelectric_point(),
            'gravy_score': analysis.gravy(),
            'net_charge': self._calculate_net_charge(sequence),
            'amino_acid_composition': analysis.get_amino_acids_percent(),
            'length': len(sequence)
        }
    
    def _predict_secondary_structure(self, analysis) -> Dict[str, float]:
        """Predict secondary structure content."""
        try:
            helix, turn, sheet = analysis.secondary_structure_fraction()
            return {
                'helix_fraction': helix,
                'turn_fraction': turn,
                'sheet_fraction': sheet
            }
        except:
            return {'helix_fraction': 0.0, 'turn_fraction': 0.0, 'sheet_fraction': 0.0}
    
    def _estimate_binding_affinity(self, sequence: str) -> Dict[str, Any]:
        """Estimate binding affinity based on physicochemical properties."""
        # Simplified binding affinity estimation
        hydrophobicity = np.mean([self.aa_properties['hydrophobicity'].get(aa, 0) for aa in sequence])
        charge = self._calculate_net_charge(sequence)
        polarity = np.mean([self.aa_properties['polarity'].get(aa, 0) for aa in sequence])
        
        # Binding score (higher = better binding potential)
        binding_score = (abs(hydrophobicity) * 0.3 + abs(charge) * 0.4 + polarity * 0.3) / 10
        
        return {
            'binding_score': round(binding_score, 3),
            'confidence': 'medium',
            'factors': {
                'hydrophobicity': round(hydrophobicity, 3),
                'charge_contribution': round(abs(charge) * 0.4, 3),
                'polarity_contribution': round(polarity * 0.3, 3)
            }
        }
    
    def _analyze_stability(self, sequence: str) -> Dict[str, Any]:
        """Analyze peptide stability."""
        # Check for stability motifs
        stability_motifs = {
            'disulfide_potential': sequence.count('C') >= 2,
            'proline_rich': sequence.count('P') / len(sequence) > 0.15,
            'glycine_rich': sequence.count('G') / len(sequence) > 0.2,
            'hydrophobic_clusters': self._find_hydrophobic_clusters(sequence)
        }
        
        stability_score = 0
        if stability_motifs['disulfide_potential']: stability_score += 0.3
        if stability_motifs['proline_rich']: stability_score += 0.2
        if stability_motifs['glycine_rich']: stability_score += 0.2
        if stability_motifs['hydrophobic_clusters']: stability_score += 0.3
        
        return {
            'stability_score': round(stability_score, 3),
            'stability_motifs': stability_motifs,
            'recommendations': self._generate_stability_recommendations(stability_motifs)
        }
    
    def _predict_immunogenicity(self, sequence: str) -> Dict[str, Any]:
        """Predict immunogenicity potential."""
        # Simple immunogenicity prediction based on amino acid composition
        immunogenic_aas = ['R', 'K', 'D', 'E', 'H']  # Charged amino acids
        immunogenic_count = sum(sequence.count(aa) for aa in immunogenic_aas)
        immunogenicity_score = immunogenic_count / len(sequence)
        
        return {
            'immunogenicity_score': round(immunogenicity_score, 3),
            'risk_level': 'low' if immunogenicity_score < 0.3 else 'medium' if immunogenicity_score < 0.5 else 'high',
            'charged_residues': immunogenic_count
        }
    
    def _calculate_solubility_profile(self, sequence: str) -> Dict[str, Any]:
        """Calculate detailed solubility profile."""
        gravy = ProteinAnalysis(sequence).gravy()
        charge = self._calculate_net_charge(sequence)
        
        # Solubility prediction based on GRAVY and charge
        if gravy < -0.5 and abs(charge) > 2:
            solubility = 'high'
        elif gravy < 0 and abs(charge) > 1:
            solubility = 'medium'
        else:
            solubility = 'low'
        
        return {
            'solubility_level': solubility,
            'gravy_score': round(gravy, 3),
            'net_charge': charge,
            'recommendations': self._generate_solubility_recommendations(gravy, charge)
        }
    
    def _analyze_interaction_potential(self, sequence: str) -> Dict[str, Any]:
        """Analyze potential interaction types."""
        interaction_types = {
            'hydrogen_bonding': sum(sequence.count(aa) for aa in 'STNQ'),
            'ionic_interactions': sum(sequence.count(aa) for aa in 'RKHDE'),
            'hydrophobic_interactions': sum(sequence.count(aa) for aa in 'ACFILMPVWY'),
            'aromatic_interactions': sum(sequence.count(aa) for aa in 'FYW')
        }
        
        total_interactions = sum(interaction_types.values())
        
        return {
            'interaction_types': interaction_types,
            'total_interaction_potential': total_interactions,
            'primary_interaction': max(interaction_types, key=interaction_types.get),
            'interaction_diversity': len([v for v in interaction_types.values() if v > 0])
        }
    
    def _calculate_net_charge(self, sequence: str) -> int:
        """Calculate net charge at pH 7.4."""
        pos_charge = sum(sequence.count(aa) for aa in 'RKH')
        neg_charge = sum(sequence.count(aa) for aa in 'DE')
        return pos_charge - neg_charge
    
    def _find_hydrophobic_clusters(self, sequence: str) -> bool:
        """Find hydrophobic clusters in sequence."""
        hydrophobic_aas = 'ACFILMPVWY'
        hydrophobic_count = sum(1 for aa in sequence if aa in hydrophobic_aas)
        return hydrophobic_count / len(sequence) > 0.4
    
    def _generate_stability_recommendations(self, motifs: Dict[str, bool]) -> List[str]:
        """Generate stability recommendations."""
        recommendations = []
        if motifs['disulfide_potential']:
            recommendations.append("Consider disulfide bond formation for stability")
        if motifs['proline_rich']:
            recommendations.append("Proline-rich regions may confer rigidity")
        if motifs['hydrophobic_clusters']:
            recommendations.append("Hydrophobic clusters may affect solubility")
        return recommendations
    
    def _generate_solubility_recommendations(self, gravy: float, charge: int) -> List[str]:
        """Generate solubility recommendations."""
        recommendations = []
        if gravy > 0:
            recommendations.append("Consider adding charged residues for solubility")
        if abs(charge) < 2:
            recommendations.append("Low net charge may affect solubility")
        return recommendations
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary."""
        return {
            'overall_score': round((analysis['binding_affinity']['binding_score'] + 
                                  analysis['stability']['stability_score']) / 2, 3),
            'key_strengths': self._identify_strengths(analysis),
            'key_concerns': self._identify_concerns(analysis),
            'recommendations': self._generate_overall_recommendations(analysis)
        }
    
    def _identify_strengths(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify peptide strengths."""
        strengths = []
        if analysis['binding_affinity']['binding_score'] > 0.6:
            strengths.append("High binding potential")
        if analysis['stability']['stability_score'] > 0.5:
            strengths.append("Good stability profile")
        if analysis['solubility_profile']['solubility_level'] == 'high':
            strengths.append("High solubility")
        return strengths
    
    def _identify_concerns(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify potential concerns."""
        concerns = []
        if analysis['immunogenicity']['risk_level'] == 'high':
            concerns.append("High immunogenicity risk")
        if analysis['solubility_profile']['solubility_level'] == 'low':
            concerns.append("Low solubility")
        if analysis['stability']['stability_score'] < 0.3:
            concerns.append("Potential stability issues")
        return concerns
    
    def _generate_overall_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations."""
        recommendations = []
        if analysis['solubility_profile']['solubility_level'] == 'low':
            recommendations.append("Consider sequence modifications for improved solubility")
        if analysis['immunogenicity']['risk_level'] == 'high':
            recommendations.append("Evaluate immunogenicity in experimental studies")
        if analysis['binding_affinity']['binding_score'] < 0.4:
            recommendations.append("Consider alternative sequences for better binding")
        return recommendations 