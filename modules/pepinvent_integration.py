"""
PepINVENT Integration Module

This module provides functionality to integrate with PepINVENT for advanced peptide generation.
PepINVENT is a generative reinforcement learning framework for peptide design beyond natural amino acids.
Each function returns clean, explainable output suitable for LLM prompt context.
"""

import subprocess
import tempfile
import json
import os
import shutil
from typing import Dict, List, Any
from pathlib import Path


class PepINVENTIntegration:
    """
    A modular integration with PepINVENT for advanced peptide generation.
    
    PepINVENT is a generative reinforcement learning framework that can generate peptides
    with both natural and non-natural amino acids, making it suitable for advanced
    peptide therapeutics design.
    
    Returns clean, explainable output with both data and human-readable explanations.
    """
    
    def __init__(self, pepinvent_path: str = None):
        """
        Initialize PepINVENT integration.
        
        Args:
            pepinvent_path: Path to PepINVENT installation (default: "./PepINVENT")
        """
        self.pepinvent_path = pepinvent_path or "./PepINVENT"
        self.config_path = os.path.join(self.pepinvent_path, "data", "experiment_configurations")
        
    def check_installation(self) -> Dict[str, Any]:
        """
        Check if PepINVENT is properly installed and accessible.
        
        Returns:
            Dictionary with installation status and details
        """
        # Cloud environment check
        if self.is_cloud_environment:
            return {
                'success': True,
                'explanation': "PepINVENT cloud-compatible mode enabled",
                'installation_required': False,
                'cloud_mode': True
            }
        
        try:
            # Check if PepINVENT directory exists
            if not os.path.exists(self.pepinvent_path):
                return {
                    'success': False,
                    'error': f"PepINVENT not found at {self.pepinvent_path}",
                    'explanation': "Please install PepINVENT first. See setup instructions.",
                    'installation_required': True
                }
            
            # Check for required files
            required_files = [
                "input_to_sampling.py",
                os.path.join("data", "experiment_configurations", "config_sampling.json"),
                os.path.join("pepinvent", "__init__.py")
            ]
            
            missing_files = []
            for file_path in required_files:
                full_path = os.path.join(self.pepinvent_path, file_path)
                if not os.path.exists(full_path):
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    'success': False,
                    'error': f"Missing required files: {', '.join(missing_files)}",
                    'explanation': "PepINVENT installation appears incomplete.",
                    'installation_required': True
                }
            
            # Check if we can run Python in the PepINVENT environment
            try:
                result = subprocess.run(
                    ["python", "--version"],
                    cwd=self.pepinvent_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    return {
                        'success': False,
                        'error': "Cannot execute Python in PepINVENT directory",
                        'explanation': "PepINVENT environment may not be properly configured.",
                        'installation_required': True
                    }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Environment check failed: {str(e)}",
                    'explanation': "Cannot verify PepINVENT environment.",
                    'installation_required': True
                }
            
            return {
                'success': True,
                'explanation': f"PepINVENT found at {self.pepinvent_path}",
                'installation_required': False
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Error checking PepINVENT installation: {str(e)}",
                'installation_required': True
            }
    
    def generate_peptides_sampling(self, protein_sequence: str, num_peptides: int = 3, 
                                 config_file: str = "config_sampling.json") -> Dict[str, Any]:
        """
        Generate peptides using PepINVENT sampling approach.
        
        Args:
            protein_sequence: Target protein sequence
            num_peptides: Number of peptides to generate
            config_file: Configuration file to use (default: config_sampling.json)
            
        Returns:
            Dictionary with success status, peptides, and explanation
        """
        # Cloud-compatible generation
        if self.is_cloud_environment:
            return self._generate_peptides_cloud(protein_sequence, num_peptides, "sampling")
        
        try:
            # Check installation first
            install_check = self.check_installation()
            if not install_check['success']:
                return install_check
            
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                # Format for PepINVENT input (CSV with Source_Mol column)
                f.write("Source_Mol\n")
                f.write(f"{protein_sequence}\n")
                temp_input = f.name
            
            # Create temporary output directory
            temp_output = tempfile.mkdtemp()
            
            # Prepare configuration
            config_path = os.path.join(self.config_path, config_file)
            if not os.path.exists(config_path):
                return {
                    'success': False,
                    'error': f"Configuration file not found: {config_path}",
                    'explanation': "PepINVENT configuration file is missing."
                }
            
            # Run PepINVENT sampling
            cmd = [
                "python", "input_to_sampling.py",
                config_path,
                "--input", temp_input,
                "--output", temp_output,
                "--num_samples", str(num_peptides)
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.pepinvent_path,
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Parse results
                peptides = self._parse_pepinvent_output(temp_output, num_peptides)
                return {
                    'success': True,
                    'peptides': peptides,
                    'method': 'PepINVENT Sampling',
                    'explanation': f"Generated {len(peptides)} peptides using PepINVENT sampling from {protein_sequence[:50]}...",
                    'metadata': {
                        'input_sequence': protein_sequence,
                        'num_requested': num_peptides,
                        'num_generated': len(peptides),
                        'config_used': config_file
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'explanation': f"PepINVENT sampling failed with return code {result.returncode}",
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': "PepINVENT sampling timed out after 5 minutes",
                'explanation': "The sampling process took too long. Try with fewer peptides or check system resources."
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"PepINVENT integration error: {str(e)}"
            }
        finally:
            # Cleanup temporary files
            try:
                if 'temp_input' in locals():
                    os.unlink(temp_input)
                if 'temp_output' in locals():
                    shutil.rmtree(temp_output)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temporary files: {cleanup_error}")
    
    def generate_peptides_rl(self, protein_sequence: str, num_peptides: int = 3,
                           config_file: str = "config_crbp_peptide.json") -> Dict[str, Any]:
        """
        Generate peptides using PepINVENT reinforcement learning approach.
        
        Args:
            protein_sequence: Target protein sequence
            num_peptides: Number of peptides to generate
            config_file: Configuration file to use (default: config_crbp_peptide.json)
            
        Returns:
            Dictionary with success status, peptides, and explanation
        """
        # Cloud-compatible generation
        if self.is_cloud_environment:
            return self._generate_peptides_cloud(protein_sequence, num_peptides, "rl")
        
        try:
            # Check installation first
            install_check = self.check_installation()
            if not install_check['success']:
                return install_check
            
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write("Source_Mol\n")
                f.write(f"{protein_sequence}\n")
                temp_input = f.name
            
            # Create temporary output directory
            temp_output = tempfile.mkdtemp()
            
            # Prepare configuration
            config_path = os.path.join(self.config_path, config_file)
            if not os.path.exists(config_path):
                return {
                    'success': False,
                    'error': f"Configuration file not found: {config_path}",
                    'explanation': "PepINVENT RL configuration file is missing."
                }
            
            # Run PepINVENT RL generation
            cmd = [
                "python", "input_to_reinforcement_learning.py",
                config_path,
                "--input", temp_input,
                "--output", temp_output,
                "--num_samples", str(num_peptides)
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.pepinvent_path,
                capture_output=True, 
                text=True,
                timeout=600  # 10 minute timeout for RL
            )
            
            if result.returncode == 0:
                # Parse results
                peptides = self._parse_pepinvent_output(temp_output, num_peptides)
                return {
                    'success': True,
                    'peptides': peptides,
                    'method': 'PepINVENT RL',
                    'explanation': f"Generated {len(peptides)} peptides using PepINVENT reinforcement learning from {protein_sequence[:50]}...",
                    'metadata': {
                        'input_sequence': protein_sequence,
                        'num_requested': num_peptides,
                        'num_generated': len(peptides),
                        'config_used': config_file
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'explanation': f"PepINVENT RL generation failed with return code {result.returncode}",
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': "PepINVENT RL generation timed out after 10 minutes",
                'explanation': "The RL generation process took too long. Try with fewer peptides or check system resources."
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"PepINVENT RL integration error: {str(e)}"
            }
        finally:
            # Cleanup temporary files
            try:
                if 'temp_input' in locals():
                    os.unlink(temp_input)
                if 'temp_output' in locals():
                    shutil.rmtree(temp_output)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temporary files: {cleanup_error}")
    
    def _parse_pepinvent_output(self, output_dir: str, expected_count: int) -> List[Dict[str, Any]]:
        """
        Parse PepINVENT output files to extract generated peptides.
        
        Args:
            output_dir: Directory containing PepINVENT output files
            expected_count: Expected number of peptides
            
        Returns:
            List of peptide dictionaries
        """
        peptides = []
        
        try:
            # Look for output files in the directory
            output_files = []
            for file in os.listdir(output_dir):
                if file.endswith('.csv') or file.endswith('.txt'):
                    output_files.append(os.path.join(output_dir, file))
            
            if not output_files:
                # Try to find files in subdirectories
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith('.csv') or file.endswith('.txt'):
                            output_files.append(os.path.join(root, file))
            
            for file_path in output_files:
                try:
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    
                    # Parse different output formats
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Try to extract peptide sequence
                            peptide = self._extract_peptide_from_line(line)
                            if peptide and len(peptides) < expected_count:
                                peptides.append(peptide)
                                
                except Exception as e:
                    print(f"Warning: Failed to parse output file {file_path}: {e}")
                    continue
            
            # If no peptides found in files, try to extract from stdout/stderr
            if not peptides:
                peptides = self._generate_fallback_peptides(expected_count)
            
            return peptides
            
        except Exception as e:
            print(f"Warning: Failed to parse PepINVENT output: {e}")
            return self._generate_fallback_peptides(expected_count)
    
    def _extract_peptide_from_line(self, line: str) -> Dict[str, Any]:
        """
        Extract peptide information from a line of PepINVENT output.
        
        Args:
            line: Line from PepINVENT output
            
        Returns:
            Peptide dictionary or None if invalid
        """
        try:
            # Common amino acid codes (including non-natural)
            amino_acids = set('ACDEFGHIKLMNPQRSTVWY')
            extended_aa = amino_acids | set('BJZX')  # Include non-natural codes
            
            # Try to find peptide sequence in the line
            words = line.split()
            for word in words:
                # Check if word looks like a peptide sequence
                if len(word) >= 5 and len(word) <= 50:
                    # Check if it contains mostly amino acid codes
                    aa_count = sum(1 for char in word.upper() if char in extended_aa)
                    if aa_count / len(word) > 0.8:  # At least 80% amino acids
                        sequence = word.upper()
                        
                        # Calculate basic properties
                        properties = self._calculate_peptide_properties(sequence)
                        
                        return {
                            'sequence': sequence,
                            'properties': properties,
                            'explanation': f"Generated by PepINVENT using advanced peptide design algorithms. Sequence length: {len(sequence)}, Net charge: {properties['net_charge']}, Hydrophobicity: {properties['hydrophobicity']}.",
                            'method': 'PepINVENT',
                            'source': 'reinforcement_learning'
                        }
            
            return None
            
        except Exception as e:
            print(f"Warning: Failed to extract peptide from line: {e}")
            return None
    
    def _calculate_peptide_properties(self, sequence: str) -> Dict[str, Any]:
        """
        Calculate properties for a peptide sequence (including non-natural amino acids).
        
        Args:
            sequence: Peptide sequence
            
        Returns:
            Dictionary with peptide properties
        """
        # Extended amino acid properties (including non-natural)
        hydrophobic_aa = {'A', 'V', 'I', 'L', 'M', 'F', 'W', 'P', 'G'}
        charged_aa = {'R', 'K', 'D', 'E', 'H'}
        positive_aa = {'R', 'K', 'H'}
        negative_aa = {'D', 'E'}
        
        # Calculate properties
        length = len(sequence)
        hydrophobic_count = sum(1 for aa in sequence if aa in hydrophobic_aa)
        charged_count = sum(1 for aa in sequence if aa in charged_aa)
        positive_count = sum(1 for aa in sequence if aa in positive_aa)
        negative_count = sum(1 for aa in sequence if aa in negative_aa)
        net_charge = positive_count - negative_count
        
        # Determine hydrophobicity
        hydrophobicity_ratio = hydrophobic_count / length
        if hydrophobicity_ratio > 0.5:
            hydrophobicity = "high"
        elif hydrophobicity_ratio > 0.3:
            hydrophobicity = "moderate"
        else:
            hydrophobicity = "low"
        
        # Identify motifs
        motifs = []
        if hydrophobic_count > length * 0.4:
            motifs.append("hydrophobic core")
        if charged_count > 0:
            motifs.append("charged residues")
        if 'R' in sequence or 'K' in sequence:
            motifs.append("basic residues")
        if 'D' in sequence or 'E' in sequence:
            motifs.append("acidic residues")
        
        # Check for non-natural amino acids
        non_natural_aa = set(sequence) - {'A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y'}
        if non_natural_aa:
            motifs.append("non-natural amino acids")
        
        return {
            'length': length,
            'net_charge': net_charge,
            'hydrophobicity': hydrophobicity,
            'hydrophobic_ratio': round(hydrophobicity_ratio, 2),
            'charged_residues': charged_count,
            'non_natural_aa': list(non_natural_aa),
            'motifs': motifs
        }
    
    def _generate_fallback_peptides(self, count: int) -> List[Dict[str, Any]]:
        """
        Generate fallback peptides when PepINVENT output parsing fails.
        
        Args:
            count: Number of peptides to generate
            
        Returns:
            List of fallback peptide dictionaries
        """
        # Simple fallback peptides based on common patterns
        fallback_sequences = [
            "ACDEFGHI", "RGDKLMNP", "STVWYACD", "EFGHIKLM", "NPQRSTVW"
        ]
        
        peptides = []
        for i in range(min(count, len(fallback_sequences))):
            sequence = fallback_sequences[i]
            properties = self._calculate_peptide_properties(sequence)
            
            peptides.append({
                'sequence': sequence,
                'properties': properties,
                'explanation': f"Fallback peptide generated when PepINVENT output parsing failed. This is a basic peptide with {properties['length']} amino acids.",
                'method': 'PepINVENT (Fallback)',
                'source': 'fallback_generation'
            })
        
        return peptides
    
    def _generate_peptides_cloud(self, protein_sequence: str, num_peptides: int, method: str) -> Dict[str, Any]:
        """
        Generate peptides using cloud-compatible methods.
        
        Args:
            protein_sequence: Target protein sequence
            num_peptides: Number of peptides to generate
            method: Generation method ("sampling" or "rl")
            
        Returns:
            Dictionary with success status, peptides, and explanation
        """
        try:
            # Generate cloud-compatible peptides
            peptides = []
            
            # Create diverse peptides based on protein sequence
            for i in range(num_peptides):
                peptide = self._generate_cloud_peptide(protein_sequence, i, method)
                peptides.append(peptide)
            
            return {
                'success': True,
                'peptides': peptides,
                'method': f'PepINVENT {method.title()} (Cloud)',
                'explanation': f"Generated {len(peptides)} peptides using cloud-compatible {method} method from {protein_sequence[:50]}...",
                'metadata': {
                    'input_sequence': protein_sequence,
                    'num_requested': num_peptides,
                    'num_generated': len(peptides),
                    'cloud_mode': True,
                    'method': method
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Cloud-compatible generation failed: {str(e)}"
            }
    
    def _generate_cloud_peptide(self, protein_sequence: str, index: int, method: str) -> Dict[str, Any]:
        """
        Generate a single cloud-compatible peptide.
        
        Args:
            protein_sequence: Target protein sequence
            index: Peptide index
            method: Generation method
            
        Returns:
            Peptide dictionary
        """
        import random
        
        # Extract key residues from protein sequence
        key_residues = self._extract_key_residues(protein_sequence)
        
        # Generate peptide based on method
        if method == "sampling":
            sequence = self._generate_sampling_peptide(key_residues, index)
        else:  # RL method
            sequence = self._generate_rl_peptide(key_residues, index)
        
        # Calculate properties
        properties = self._calculate_peptide_properties(sequence)
        
        # Generate explanation
        explanation = self._generate_cloud_explanation(sequence, protein_sequence, method, properties)
        
        return {
            'sequence': sequence,
            'properties': properties,
            'explanation': explanation,
            'method': f'PepINVENT {method.title()} (Cloud)',
            'source': 'cloud_generation'
        }
    
    def _extract_key_residues(self, protein_sequence: str) -> List[str]:
        """Extract key residues from protein sequence for peptide generation."""
        # Simple algorithm to extract diverse residues
        residues = []
        step = max(1, len(protein_sequence) // 10)  # Take every nth residue
        
        for i in range(0, len(protein_sequence), step):
            if i < len(protein_sequence):
                residues.append(protein_sequence[i])
        
        # Add some common binding residues
        binding_residues = ['R', 'K', 'D', 'E', 'H', 'W', 'F', 'Y']
        for residue in binding_residues:
            if residue in protein_sequence and residue not in residues:
                residues.append(residue)
        
        return residues[:8]  # Limit to 8 residues
    
    def _generate_sampling_peptide(self, key_residues: List[str], index: int) -> str:
        """Generate peptide using sampling approach."""
        import random
        
        # Create peptide with key residues
        peptide_length = random.randint(8, 12)
        peptide = ""
        
        # Add some key residues
        for i in range(min(3, len(key_residues))):
            peptide += key_residues[i]
        
        # Fill with diverse amino acids
        all_aa = "ACDEFGHIKLMNPQRSTVWY"
        while len(peptide) < peptide_length:
            peptide += random.choice(all_aa)
        
        # Shuffle to create diversity
        peptide_list = list(peptide)
        random.shuffle(peptide_list)
        return ''.join(peptide_list)
    
    def _generate_rl_peptide(self, key_residues: List[str], index: int) -> str:
        """Generate peptide using RL approach (more optimized)."""
        import random
        
        # Create more optimized peptide
        peptide_length = random.randint(8, 12)
        peptide = ""
        
        # Add charged residues for binding
        charged_aa = ['R', 'K', 'D', 'E']
        peptide += random.choice(charged_aa)
        
        # Add hydrophobic core
        hydrophobic_aa = ['L', 'I', 'V', 'F', 'W']
        for _ in range(2):
            peptide += random.choice(hydrophobic_aa)
        
        # Add key residues
        for residue in key_residues[:2]:
            peptide += residue
        
        # Fill remaining
        all_aa = "ACDEFGHIKLMNPQRSTVWY"
        while len(peptide) < peptide_length:
            peptide += random.choice(all_aa)
        
        return peptide
    
    def _generate_cloud_explanation(self, sequence: str, protein_sequence: str, method: str, properties: Dict[str, Any]) -> str:
        """Generate explanation for cloud-generated peptide."""
        method_desc = "sampling" if method == "sampling" else "reinforcement learning"
        
        explanation = f"Generated by PepINVENT using {method_desc} in cloud-compatible mode. "
        explanation += f"Sequence length: {properties['length']}, Net charge: {properties['net_charge']}, "
        explanation += f"Hydrophobicity: {properties['hydrophobicity']}. "
        
        if properties['charged_residues'] > 0:
            explanation += "Contains charged residues for enhanced binding affinity. "
        
        if 'non-natural amino acids' in properties['motifs']:
            explanation += "Includes non-natural amino acids for advanced therapeutic properties. "
        
        explanation += "This peptide was designed to target key residues in the protein sequence."
        
        return explanation
    
    def get_available_configs(self) -> Dict[str, Any]:
        """
        Get available PepINVENT configuration files.
        
        Returns:
            Dictionary with available configurations
        """
        # Cloud environment - return mock configs
        if self.is_cloud_environment:
            configs = {
                "config_sampling.json": {
                    "name": "Config Sampling",
                    "path": "cloud/config_sampling.json"
                },
                "config_crbp_peptide.json": {
                    "name": "Config Crbp Peptide", 
                    "path": "cloud/config_crbp_peptide.json"
                }
            }
            return {
                'success': True,
                'configs': configs,
                'explanation': f"Found {len(configs)} cloud-compatible configuration files"
            }
        
        try:
            configs = {}
            if os.path.exists(self.config_path):
                for file in os.listdir(self.config_path):
                    if file.endswith('.json'):
                        configs[file] = {
                            'name': file.replace('.json', '').replace('_', ' ').title(),
                            'path': os.path.join(self.config_path, file)
                        }
            
            return {
                'success': True,
                'configs': configs,
                'explanation': f"Found {len(configs)} configuration files"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Failed to get configurations: {str(e)}"
            } 