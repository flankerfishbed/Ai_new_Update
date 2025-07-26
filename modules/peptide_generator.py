"""
Peptide Generator Module

This module provides functionality to generate AI-suggested peptide candidates using LLM providers.
Each function returns clean, explainable output suitable for LLM prompt context.
"""

import re
import json
from typing import Dict, List, Any
from .llm_providers import LLMProvider


class PeptideGenerator:
    """
    A modular generator for AI-suggested peptide candidates.
    
    Uses LLM providers to generate peptides with detailed reasoning based on protein structure analysis.
    Returns clean, explainable output with both data and human-readable explanations.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def generate_peptides(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate peptide candidates using AI with detailed reasoning.
        
        Args:
            context_data: Dictionary containing protein sequence, residues, and surface data
            
        Returns:
            Dictionary with success status, peptides, and explanation
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_peptide_prompt(context_data)
            
            # Generate response from LLM
            llm_response = self.llm_provider.generate_response(
                prompt,
                max_tokens=4000,
                temperature=0.7
            )
            
            if not llm_response['success']:
                return {
                    'success': False,
                    'error': llm_response['error'],
                    'explanation': f"Failed to generate peptides: {llm_response['error']}"
                }
            
            # Parse LLM response
            peptides = self._parse_peptide_response(llm_response['response'])
            
            if not peptides:
                return {
                    'success': False,
                    'error': "Failed to parse peptide response from LLM",
                    'explanation': "The AI response could not be parsed into valid peptide candidates."
                }
            
            return {
                'success': True,
                'peptides': peptides,
                'explanation': f"Successfully generated {len(peptides)} peptide candidates using {llm_response['provider']} {llm_response['model']}.",
                'llm_metadata': {
                    'provider': llm_response['provider'],
                    'model': llm_response['model'],
                    'usage': llm_response.get('usage')
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Error during peptide generation: {str(e)}"
            }
    
    def _build_peptide_prompt(self, context_data: Dict[str, Any]) -> str:
        """
        Build a comprehensive prompt for peptide generation.
        
        Args:
            context_data: Dictionary containing protein analysis data
            
        Returns:
            Formatted prompt string
        """
        sequence = context_data['sequence']
        residues = context_data['residues']
        chain_id = context_data['chain_id']
        num_peptides = context_data.get('num_peptides', 3)
        surface_data = context_data.get('surface_data')
        
        prompt = f"""
You are an expert computational biologist specializing in peptide therapeutics. Your task is to generate {num_peptides} peptide candidates (8-15 amino acids) that could potentially bind to the surface of a target protein.

**TARGET PROTEIN INFORMATION:**
- Chain ID: {chain_id}
- Sequence: {sequence}
- Total residues: {len(residues)}

**RESIDUE ANALYSIS:**
"""
        
        # Add surface analysis if available
        if surface_data and surface_data['success']:
            surface_summary = surface_data['summary']
            prompt += f"""
**SURFACE ANALYSIS:**
- Surface-exposed residues (SASA > 10 Å²): {surface_summary['surface_residues']}
- Hydrophobic surface residues: {surface_summary['hydrophobic_count']}
- Charged surface residues: {surface_summary['charged_count']}
- Polar surface residues: {surface_summary['polar_count']}
- Average SASA: {surface_summary['avg_sasa']} Å²
- Maximum SASA: {surface_summary['max_sasa']} Å²

**SURFACE RESIDUE DETAILS:**
"""
            # Add top surface residues
            surface_residues = [r for r in surface_data['residues'] if r['is_surface']]
            surface_residues.sort(key=lambda x: x['sasa'], reverse=True)
            
            for i, residue in enumerate(surface_residues[:10]):
                prompt += f"- Residue {residue['residue_id']} ({residue['residue_name']}): {residue['sasa']} Å² ({residue['residue_type']})\n"
        
        prompt += f"""

**TASK:**
Generate {num_peptides} peptide candidates optimized for binding to this protein surface. Each peptide should be 8-15 amino acids long.

**REQUIREMENTS:**
1. Consider the surface composition (hydrophobic, charged, polar regions)
2. Design peptides that can form complementary interactions
3. Include both hydrophobic and hydrophilic residues for balanced binding
4. Consider charge complementarity for charged surface regions
5. Avoid proline-rich sequences unless specifically beneficial
6. Ensure peptides are soluble and stable

**OUTPUT FORMAT:**
For each peptide, provide:
1. Peptide sequence (8-15 amino acids)
2. Properties: length, net charge, hydrophobicity, key motifs
3. Detailed reasoning explaining why this peptide was chosen, referencing specific surface features

**EXAMPLE FORMAT:**
```json
{{
  "peptides": [
    {{
      "sequence": "ACDEFGHI",
      "properties": {{
        "length": 8,
        "net_charge": 0,
        "hydrophobicity": "moderate",
        "motifs": ["hydrophobic core", "charged termini"]
      }},
      "explanation": "This peptide targets the hydrophobic surface region around residues 42-45 (Leu, Ile, Val) with high SASA values. The central hydrophobic core (DEF) provides strong van der Waals interactions, while the charged termini (A, I) ensure solubility and provide additional electrostatic interactions with nearby charged surface residues."
    }}
  ]
}}
```

Please generate {num_peptides} diverse peptide candidates with detailed reasoning for each.
"""
        
        return prompt
    
    def _parse_peptide_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse the LLM response to extract peptide candidates.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            List of peptide dictionaries
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                return data.get('peptides', [])
            
            # Fallback: try to find JSON anywhere in response
            json_match = re.search(r'\{.*"peptides".*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return data.get('peptides', [])
            
            # If no JSON found, try to extract peptides manually
            peptides = self._extract_peptides_manual(response)
            return peptides
            
        except Exception as e:
            # Fallback to manual extraction
            peptides = self._extract_peptides_manual(response)
            return peptides
    
    def _extract_peptides_manual(self, response: str) -> List[Dict[str, Any]]:
        """
        Manually extract peptides from LLM response when JSON parsing fails.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            List of peptide dictionaries
        """
        peptides = []
        
        # Look for peptide sequences (8-15 amino acids)
        sequence_pattern = r'[ACDEFGHIKLMNPQRSTVWY]{8,15}'
        sequences = re.findall(sequence_pattern, response.upper())
        
        # Split response into sections
        sections = response.split('\n\n')
        
        for i, sequence in enumerate(sequences):
            if i >= 10:  # Limit to 10 peptides
                break
                
            # Try to find explanation for this peptide
            explanation = ""
            for section in sections:
                if sequence in section:
                    # Extract explanation (everything after the sequence)
                    lines = section.split('\n')
                    for j, line in enumerate(lines):
                        if sequence in line:
                            explanation = '\n'.join(lines[j+1:]).strip()
                            break
                    break
            
            # Calculate basic properties
            properties = self._calculate_peptide_properties(sequence)
            
            peptide = {
                'sequence': sequence,
                'properties': properties,
                'explanation': explanation or f"AI-generated peptide targeting protein surface interactions."
            }
            peptides.append(peptide)
        
        return peptides
    
    def _calculate_peptide_properties(self, sequence: str) -> Dict[str, Any]:
        """
        Calculate properties for a peptide sequence.
        
        Args:
            sequence: Peptide sequence
            
        Returns:
            Dictionary with peptide properties
        """
        # Amino acid properties
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
        
        return {
            'length': length,
            'net_charge': net_charge,
            'hydrophobicity': hydrophobicity,
            'hydrophobic_ratio': round(hydrophobicity_ratio, 2),
            'charged_residues': charged_count,
            'motifs': motifs
        } 