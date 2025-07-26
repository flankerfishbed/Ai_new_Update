"""
Surface Analyzer Module

This module provides functionality to analyze protein surface properties using FreeSASA.
Each function returns clean, explainable output suitable for LLM prompt context.
"""

import freesasa
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import tempfile
import os


class SurfaceAnalyzer:
    """
    A modular analyzer for protein surface properties using FreeSASA.
    
    Returns clean, explainable output with both data and human-readable explanations.
    """
    
    def __init__(self):
        pass  # FreeSASA doesn't need a parser instance
    
    def analyze_surface(self, pdb_content: str, chain_id: str = "A") -> Dict[str, Any]:
        """
        Analyze protein surface properties using FreeSASA and Biopython.
        Args:
            pdb_content: Raw PDB file content as string
            chain_id: Chain identifier to analyze (default: "A")
        Returns:
            Dictionary with success status, surface data, and explanation
        """
        from Bio.PDB import PDBParser
        try:
            # Create temporary file for FreeSASA
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdb', delete=False) as tmp_file:
                tmp_file.write(pdb_content)
                tmp_file_path = tmp_file.name
            try:
                # Parse structure with Biopython
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure('protein', tmp_file_path)
                # Calculate SASA with FreeSASA
                fs_structure = freesasa.Structure(tmp_file_path)
                result = freesasa.calc(fs_structure)
                # Amino acid classification
                hydrophobic_aa = {'ALA', 'VAL', 'ILE', 'LEU', 'MET', 'PHE', 'TRP', 'PRO', 'GLY'}
                charged_aa = {'ARG', 'LYS', 'ASP', 'GLU', 'HIS'}
                hydrophobic_count = 0
                charged_count = 0
                polar_count = 0
                residues = []
                total_sasa = 0
                surface_residues = 0
                # Only use the first model
                model = next(structure.get_models())
                if chain_id not in [c.id for c in model]:
                    raise ValueError(f"Chain '{chain_id}' not found in structure. Available: {[c.id for c in model]}")
                chain = model[chain_id]
                for residue in chain:
                    if not hasattr(residue, 'id') or residue.id[0] != ' ':  # skip hetero/water
                        continue
                    res_id = residue.id[1]
                    res_name = residue.get_resname()
                    residue_sasa = 0
                    for atom in residue:
                        # FreeSASA atom naming: chain:resseq:atomname
                        atom_id = f"{chain.id}:{res_id}:{atom.get_name()}"
                        try:
                            atom_sasa = result.atomArea(atom_id)
                        except Exception:
                            atom_sasa = 0.0
                        residue_sasa += atom_sasa
                    # Classify residue
                    if res_name in hydrophobic_aa:
                        res_type = 'hydrophobic'
                        hydrophobic_count += 1
                    elif res_name in charged_aa:
                        res_type = 'charged'
                        charged_count += 1
                    else:
                        res_type = 'polar'
                        polar_count += 1
                    # Determine if surface-exposed (SASA > 10 Å²)
                    is_surface = residue_sasa > 10
                    if is_surface:
                        surface_residues += 1
                    residue_info = {
                        'residue_id': res_id,
                        'residue_name': res_name,
                        'residue_type': res_type,
                        'sasa': round(residue_sasa, 2),
                        'is_surface': is_surface,
                        'chain_id': chain_id
                    }
                    residues.append(residue_info)
                    total_sasa += residue_sasa
                # Calculate summary statistics
                avg_sasa = total_sasa / len(residues) if residues else 0
                max_sasa = max([r['sasa'] for r in residues]) if residues else 0
                explanation = self._generate_surface_explanation(
                    residues, surface_residues, hydrophobic_count, 
                    charged_count, polar_count, avg_sasa, max_sasa
                )
                return {
                    'success': True,
                    'residues': residues,
                    'summary': {
                        'total_residues': len(residues),
                        'surface_residues': surface_residues,
                        'hydrophobic_count': hydrophobic_count,
                        'charged_count': charged_count,
                        'polar_count': polar_count,
                        'avg_sasa': round(avg_sasa, 2),
                        'max_sasa': round(max_sasa, 2),
                        'total_sasa': round(total_sasa, 2)
                    },
                    'explanation': explanation
                }
            finally:
                os.unlink(tmp_file_path)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Failed to analyze surface properties due to: {str(e)}"
            }
    
    def _generate_surface_explanation(self, residues: List[Dict], surface_residues: int,
                                    hydrophobic_count: int, charged_count: int, 
                                    polar_count: int, avg_sasa: float, max_sasa: float) -> str:
        """
        Generate a human-readable explanation of the surface analysis results.
        
        Args:
            residues: List of residue dictionaries with SASA data
            surface_residues: Number of surface-exposed residues
            hydrophobic_count: Number of hydrophobic residues
            charged_count: Number of charged residues
            polar_count: Number of polar residues
            avg_sasa: Average SASA value
            max_sasa: Maximum SASA value
            
        Returns:
            Human-readable explanation
        """
        explanation = f"""
        **Surface Analysis Results:**
        
        **Residue Classification:**
        - Total residues analyzed: {len(residues)}
        - Surface-exposed residues (SASA > 10 Å²): {surface_residues}
        - Hydrophobic residues: {hydrophobic_count}
        - Charged residues: {charged_count}
        - Polar/other residues: {polar_count}
        
        **SASA Statistics:**
        - Average SASA: {avg_sasa:.2f} Å²
        - Maximum SASA: {max_sasa:.2f} Å²
        
        **Surface Exposure Analysis:**
        Residues with SASA > 10 Å² are considered surface-exposed and potentially accessible for peptide binding.
        This analysis helps identify regions that may be suitable targets for peptide therapeutics.
        
        **Residue Type Distribution:**
        The distribution of hydrophobic, charged, and polar residues on the surface provides insight into
        the types of interactions that would be most favorable for peptide binding.
        """
        
        return explanation.strip()
    
    def get_surface_hotspots(self, residues: List[Dict], top_n: int = 10) -> List[Dict]:
        """
        Identify surface hotspots (residues with highest SASA).
        
        Args:
            residues: List of residue dictionaries with SASA data
            top_n: Number of top surface residues to return
            
        Returns:
            List of top surface residues
        """
        # Sort by SASA (descending) and filter surface residues
        surface_residues = [r for r in residues if r['is_surface']]
        surface_residues.sort(key=lambda x: x['sasa'], reverse=True)
        
        return surface_residues[:top_n]
    
    def get_residue_clusters(self, residues: List[Dict], distance_threshold: float = 5.0) -> List[List[Dict]]:
        """
        Group surface residues into clusters based on spatial proximity.
        
        Args:
            residues: List of residue dictionaries
            distance_threshold: Maximum distance for clustering (Å)
            
        Returns:
            List of residue clusters
        """
        # This is a simplified clustering - in practice, you'd use 3D coordinates
        # For now, we'll group by residue type and SASA ranges
        clusters = []
        
        # Group by residue type
        hydrophobic_cluster = [r for r in residues if r['residue_type'] == 'hydrophobic' and r['is_surface']]
        charged_cluster = [r for r in residues if r['residue_type'] == 'charged' and r['is_surface']]
        polar_cluster = [r for r in residues if r['residue_type'] == 'polar' and r['is_surface']]
        
        if hydrophobic_cluster:
            clusters.append(hydrophobic_cluster)
        if charged_cluster:
            clusters.append(charged_cluster)
        if polar_cluster:
            clusters.append(polar_cluster)
        
        return clusters 