"""
PDB Parser Module

This module provides functionality to parse PDB files and extract protein structure information.
Each function returns clean, explainable output suitable for LLM prompt context.
"""

import re
from typing import Dict, List, Any
from Bio import PDB
from Bio.PDB.Polypeptide import three_to_one, is_aa
import pandas as pd


class PDBParser:
    """
    A modular parser for PDB files that extracts protein sequence and residue information.
    
    Returns clean, explainable output with both data and human-readable explanations.
    """
    
    def __init__(self):
        self.parser = PDB.PDBParser(QUIET=True)
    
    def parse_structure(self, pdb_content: str, chain_id: str = "A") -> Dict[str, Any]:
        """
        Parse PDB content and extract protein information.
        
        Args:
            pdb_content: Raw PDB file content as string
            chain_id: Chain identifier to analyze (default: "A")
            
        Returns:
            Dictionary with success status, parsed data, and explanation
        """
        try:
            # Create temporary file for BioPython parser
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdb', delete=False) as tmp_file:
                tmp_file.write(pdb_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Parse structure
                structure = self.parser.get_structure('protein', tmp_file_path)
                
                # Extract chain
                if chain_id not in structure:
                    return {
                        'success': False,
                        'error': f"Chain '{chain_id}' not found in structure. Available chains: {list(structure.keys())}",
                        'explanation': f"Failed to find chain '{chain_id}' in the uploaded PDB structure."
                    }
                
                chain = structure[chain_id]
                
                # Extract sequence and residue information
                sequence = ""
                residues = []
                
                for residue in chain:
                    if is_aa(residue):
                        # Get residue information
                        res_id = residue.get_id()
                        res_name = residue.get_resname()
                        
                        # Convert to one-letter code
                        try:
                            one_letter = three_to_one(res_name)
                            sequence += one_letter
                        except KeyError:
                            # Handle non-standard amino acids
                            one_letter = "X"
                            sequence += one_letter
                        
                        # Get coordinates
                        ca_atom = None
                        for atom in residue:
                            if atom.get_id() == "CA":
                                ca_atom = atom
                                break
                        
                        residue_info = {
                            'residue_id': res_id[1],
                            'residue_name': res_name,
                            'one_letter': one_letter,
                            'chain_id': chain_id,
                            'x': ca_atom.get_coord()[0] if ca_atom else None,
                            'y': ca_atom.get_coord()[1] if ca_atom else None,
                            'z': ca_atom.get_coord()[2] if ca_atom else None,
                            'insertion_code': res_id[2] if len(res_id) > 2 else None
                        }
                        residues.append(residue_info)
                
                # Generate explanation
                explanation = self._generate_parsing_explanation(sequence, residues, chain_id)
                
                return {
                    'success': True,
                    'sequence': sequence,
                    'residues': residues,
                    'chain_id': chain_id,
                    'explanation': explanation,
                    'summary': {
                        'total_residues': len(residues),
                        'sequence_length': len(sequence),
                        'chain_id': chain_id
                    }
                }
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Failed to parse PDB structure due to: {str(e)}"
            }
    
    def _generate_parsing_explanation(self, sequence: str, residues: List[Dict], chain_id: str) -> str:
        """
        Generate a human-readable explanation of the parsing results.
        
        Args:
            sequence: Protein sequence
            residues: List of residue dictionaries
            chain_id: Chain identifier
            
        Returns:
            Human-readable explanation
        """
        explanation = f"""
        Successfully parsed protein structure from chain {chain_id}.
        
        **Structure Summary:**
        - Total residues: {len(residues)}
        - Sequence length: {len(sequence)} amino acids
        - Chain ID: {chain_id}
        
        **Sequence Information:**
        The protein sequence was extracted by converting three-letter amino acid codes to one-letter codes.
        Non-standard amino acids are represented as 'X'.
        
        **Residue Data:**
        Each residue entry contains:
        - Residue ID (position in chain)
        - Three-letter amino acid name
        - One-letter amino acid code
        - 3D coordinates (if available)
        - Chain identifier
        - Insertion code (if present)
        
        This parsed data provides the foundation for surface analysis and peptide generation.
        """
        
        return explanation.strip()
    
    def get_residue_properties(self, residue_name: str) -> Dict[str, Any]:
        """
        Get properties for a specific amino acid residue.
        
        Args:
            residue_name: Three-letter amino acid code
            
        Returns:
            Dictionary with residue properties
        """
        # Amino acid properties
        properties = {
            'ALA': {'type': 'hydrophobic', 'charge': 0, 'polarity': 'non-polar'},
            'ARG': {'type': 'charged', 'charge': 1, 'polarity': 'polar'},
            'ASN': {'type': 'polar', 'charge': 0, 'polarity': 'polar'},
            'ASP': {'type': 'charged', 'charge': -1, 'polarity': 'polar'},
            'CYS': {'type': 'polar', 'charge': 0, 'polarity': 'polar'},
            'GLN': {'type': 'polar', 'charge': 0, 'polarity': 'polar'},
            'GLU': {'type': 'charged', 'charge': -1, 'polarity': 'polar'},
            'GLY': {'type': 'hydrophobic', 'charge': 0, 'polarity': 'non-polar'},
            'HIS': {'type': 'charged', 'charge': 0.5, 'polarity': 'polar'},
            'ILE': {'type': 'hydrophobic', 'charge': 0, 'polarity': 'non-polar'},
            'LEU': {'type': 'hydrophobic', 'charge': 0, 'polarity': 'non-polar'},
            'LYS': {'type': 'charged', 'charge': 1, 'polarity': 'polar'},
            'MET': {'type': 'hydrophobic', 'charge': 0, 'polarity': 'non-polar'},
            'PHE': {'type': 'hydrophobic', 'charge': 0, 'polarity': 'non-polar'},
            'PRO': {'type': 'hydrophobic', 'charge': 0, 'polarity': 'non-polar'},
            'SER': {'type': 'polar', 'charge': 0, 'polarity': 'polar'},
            'THR': {'type': 'polar', 'charge': 0, 'polarity': 'polar'},
            'TRP': {'type': 'hydrophobic', 'charge': 0, 'polarity': 'non-polar'},
            'TYR': {'type': 'polar', 'charge': 0, 'polarity': 'polar'},
            'VAL': {'type': 'hydrophobic', 'charge': 0, 'polarity': 'non-polar'}
        }
        
        return properties.get(residue_name, {
            'type': 'unknown',
            'charge': 0,
            'polarity': 'unknown'
        }) 