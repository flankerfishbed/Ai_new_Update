"""
Hybrid Peptide Generator Module

This module combines PepINVENT generation with LLM refinement and comprehensive comparison.
Implements the workflow: PepINVENT → Property Analysis → LLM Refinement → Side-by-Side Comparison.
Each function returns clean, explainable output suitable for LLM prompt context.
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from .peptide_generator import PeptideGenerator
from .pepinvent_integration import PepINVENTIntegration
from .peptide_analyzer import AdvancedPeptideAnalyzer
from .llm_providers import LLMProvider


class HybridPeptideGenerator:
    """
    A hybrid generator that combines PepINVENT generation with LLM refinement.
    
    Workflow:
    1. PepINVENT generates initial peptide sequences
    2. Compute comprehensive biochemical properties for each peptide
    3. LLM analyzes properties and generates refined sequences
    4. Provide side-by-side comparison of original vs refined peptides
    
    Returns clean, explainable output with detailed comparison data.
    """
    
    def __init__(self, llm_provider: LLMProvider, pepinvent_path: str = None):
        """
        Initialize hybrid peptide generator.
        
        Args:
            llm_provider: LLM provider for analysis and refinement
            pepinvent_path: Path to PepINVENT installation
        """
        self.llm_generator = PeptideGenerator(llm_provider)
        self.pepinvent = PepINVENTIntegration(pepinvent_path)
        self.llm_provider = llm_provider
        self.analyzer = AdvancedPeptideAnalyzer()
        
        # Storage for tracking peptides and their properties
        self.original_peptides = []
        self.refined_peptides = []
        self.comparison_data = {}
    
    def generate_and_refine_peptides(self, context_data: Dict[str, Any], 
                                   num_peptides: int = 3,
                                   refinement_focus: str = "balanced") -> Dict[str, Any]:
        """
        Complete workflow: Generate → Analyze → Refine → Compare.
        
        Args:
            context_data: Dictionary containing protein analysis data
            num_peptides: Number of peptides to generate
            refinement_focus: Focus area for refinement ("solubility", "stability", "binding", "balanced")
            
        Returns:
            Dictionary with original peptides, refined peptides, and comparison data
        """
        try:
            # Step 1: Generate peptides with PepINVENT
            st.info("🧬 **Step 1**: Generating peptides with PepINVENT...")
            pepinvent_result = self.pepinvent.generate_peptides_sampling(
                context_data['sequence'],
                num_peptides
            )
            
            if not pepinvent_result['success']:
                return {
                    'success': False,
                    'error': "PepINVENT generation failed",
                    'explanation': pepinvent_result.get('explanation', 'Unknown error')
                }
            
            # Step 2: Analyze properties of original peptides
            st.info("🔬 **Step 2**: Analyzing biochemical properties...")
            original_peptides_with_properties = self._analyze_peptide_properties(
                pepinvent_result['peptides']
            )
            
            # Step 3: Use LLM to generate refined peptides
            st.info("🤖 **Step 3**: Generating refined peptides with LLM...")
            refinement_result = self._generate_refined_peptides(
                original_peptides_with_properties, 
                context_data, 
                refinement_focus
            )
            
            if not refinement_result['success']:
                return {
                    'success': False,
                    'error': "LLM refinement failed",
                    'explanation': refinement_result.get('error', 'Unknown error')
                }
            
            # Step 4: Analyze properties of refined peptides
            st.info("🔬 **Step 4**: Analyzing refined peptide properties...")
            refined_peptides_with_properties = self._analyze_peptide_properties(
                refinement_result['peptides']
            )
            
            # Step 5: Create comprehensive comparison
            st.info("📊 **Step 5**: Creating side-by-side comparison...")
            comparison_data = self._create_comparison_data(
                original_peptides_with_properties,
                refined_peptides_with_properties
            )
            
            # Store results for tracking
            self.original_peptides = original_peptides_with_properties
            self.refined_peptides = refined_peptides_with_properties
            self.comparison_data = comparison_data
            
            return {
                'success': True,
                'original_peptides': original_peptides_with_properties,
                'refined_peptides': refined_peptides_with_properties,
                'comparison_data': comparison_data,
                'explanation': f"Generated {len(original_peptides_with_properties)} original peptides with PepINVENT, refined with {refinement_result['llm_provider']} {refinement_result['llm_model']}, and created comprehensive comparison.",
                'metadata': {
                    'original_count': len(original_peptides_with_properties),
                    'refined_count': len(refined_peptides_with_properties),
                    'llm_provider': refinement_result['llm_provider'],
                    'llm_model': refinement_result['llm_model'],
                    'refinement_focus': refinement_focus
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': f"Error in hybrid peptide generation: {str(e)}"
            }
    
    def _analyze_peptide_properties(self, peptides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze comprehensive biochemical properties for each peptide.
        
        Args:
            peptides: List of peptide dictionaries with sequences
            
        Returns:
            List of peptides with comprehensive property analysis
        """
        analyzed_peptides = []
        
        for i, peptide in enumerate(peptides):
            sequence = peptide.get('sequence', '')
            if not sequence:
                continue
                
            # Generate unique ID for tracking
            peptide_id = f"PEP_{i+1:03d}"
            
            # Perform comprehensive analysis
            analysis_result = self.analyzer.analyze_peptide(sequence)
            
            # Combine original peptide data with analysis
            enhanced_peptide = peptide.copy()
            enhanced_peptide.update({
                'id': peptide_id,
                'sequence': sequence,
                'analysis': analysis_result,
                'properties': {
                    'molecular_weight': analysis_result.get('molecular_weight', 0),
                    'isoelectric_point': analysis_result.get('isoelectric_point', 0),
                    'gravy_score': analysis_result.get('gravy_score', 0),
                    'net_charge': analysis_result.get('net_charge', 0),
                    'instability_index': analysis_result.get('instability_index', 0),
                    'aliphatic_index': analysis_result.get('aliphatic_index', 0),
                    'hydrophobicity': analysis_result.get('hydrophobicity', 0),
                    'solubility_score': analysis_result.get('solubility_score', 0),
                    'aggregation_tendency': analysis_result.get('aggregation_tendency', 0),
                    'binding_potential': analysis_result.get('binding_potential', 0)
                }
            })
            
            analyzed_peptides.append(enhanced_peptide)
        
        return analyzed_peptides
    
    def _generate_refined_peptides(self, original_peptides: List[Dict[str, Any]], 
                                 context_data: Dict[str, Any],
                                 refinement_focus: str) -> Dict[str, Any]:
        """
        Use LLM to generate refined peptides based on property analysis.
        
        Args:
            original_peptides: List of original peptides with properties
            context_data: Protein context data
            refinement_focus: Focus area for refinement
            
        Returns:
            Dictionary with refined peptides and metadata
        """
        # Build comprehensive prompt for LLM refinement
        refinement_prompt = self._build_refinement_prompt(
            original_peptides, context_data, refinement_focus
        )
        
        # Generate refined peptides with LLM
        llm_response = self.llm_provider.generate_response(
            refinement_prompt,
            max_tokens=4000,
            temperature=0.7
        )
        
        if not llm_response['success']:
            return {
                'success': False,
                'error': "LLM refinement failed",
                'explanation': llm_response.get('error', 'Unknown error')
            }
        
        # Parse refined peptides from LLM response
        refined_peptides = self._parse_refined_peptides(llm_response['response'])
        
        return {
            'success': True,
            'peptides': refined_peptides,
            'llm_provider': llm_response['provider'],
            'llm_model': llm_response['model'],
            'refinement_focus': refinement_focus
        }
    
    def _build_refinement_prompt(self, original_peptides: List[Dict[str, Any]], 
                               context_data: Dict[str, Any],
                               refinement_focus: str) -> str:
        """
        Build comprehensive prompt for LLM refinement.
        
        Args:
            original_peptides: Original peptides with properties
            context_data: Protein context data
            refinement_focus: Focus area for refinement
            
        Returns:
            Formatted prompt string
        """
        # Create detailed peptide analysis table
        peptide_analysis = []
        for peptide in original_peptides:
            properties = peptide.get('properties', {})
            analysis = {
                'id': peptide.get('id', ''),
                'sequence': peptide.get('sequence', ''),
                'molecular_weight': properties.get('molecular_weight', 0),
                'isoelectric_point': properties.get('isoelectric_point', 0),
                'gravy_score': properties.get('gravy_score', 0),
                'net_charge': properties.get('net_charge', 0),
                'instability_index': properties.get('instability_index', 0),
                'solubility_score': properties.get('solubility_score', 0),
                'aggregation_tendency': properties.get('aggregation_tendency', 0),
                'binding_potential': properties.get('binding_potential', 0)
            }
            peptide_analysis.append(analysis)
        
        focus_instructions = {
            "solubility": "Focus on improving solubility by reducing hydrophobicity, increasing net charge, and optimizing amino acid composition for better aqueous solubility.",
            "stability": "Focus on improving stability by reducing instability index, optimizing aliphatic index, and enhancing structural stability.",
            "binding": "Focus on improving binding potential by optimizing charge distribution, hydrophobicity patterns, and amino acid composition for target interaction.",
            "balanced": "Focus on balanced improvements across solubility, stability, and binding potential while maintaining peptide length and avoiding aggregation."
        }
        
        focus_instruction = focus_instructions.get(refinement_focus, focus_instructions["balanced"])
        
        return f"""
You are a peptide design expert specializing in computational peptide optimization. You are given a set of peptides and their corresponding biochemical properties. Design a new set of peptides (same number) with improved characteristics.

**TARGET PROTEIN CONTEXT:**
Sequence: {context_data['sequence'][:100]}...
Chain ID: {context_data['chain_id']}

**ORIGINAL PEPTIDES AND THEIR PROPERTIES:**
{json.dumps(peptide_analysis, indent=2)}

**REFINEMENT FOCUS:**
{focus_instruction}

**TASK:**
1. Analyze the weaknesses in each original peptide based on their properties
2. Design new peptide sequences that address these weaknesses
3. Avoid repeating any of the original sequences
4. Maintain similar peptide lengths (8-15 amino acids)
5. Provide detailed reasoning for each improvement

**IMPORTANT CONSTRAINTS:**
- Do NOT repeat any original sequences
- Focus on {refinement_focus} improvements
- Maintain peptide length within 8-15 amino acids
- Consider both natural and non-natural amino acids if beneficial
- Provide clear reasoning for each modification

**OUTPUT FORMAT:**
Return your response as JSON with this exact structure:
{{
    "refined_peptides": [
        {{
            "id": "REF_001",
            "sequence": "NEWSEQUENCE",
            "original_id": "PEP_001",
            "improvements": ["reason1", "reason2", "reason3"],
            "reasoning": "Detailed explanation of improvements",
            "focus_areas": ["solubility", "stability", "binding"]
        }}
    ],
    "summary": "Overall improvement strategy and key changes made"
}}

**PROPERTY INTERPRETATION GUIDE:**
- Molecular Weight: Lower is generally better for synthesis and delivery
- Isoelectric Point: Consider target pH environment
- GRAVY Score: Negative values indicate hydrophilic (better solubility)
- Net Charge: Positive/negative charge affects binding and solubility
- Instability Index: Lower values indicate more stable peptides
- Solubility Score: Higher values indicate better solubility
- Aggregation Tendency: Lower values indicate less aggregation
- Binding Potential: Higher values indicate better target interaction
"""
    
    def _parse_refined_peptides(self, llm_response: str) -> List[Dict[str, Any]]:
        """
        Parse refined peptides from LLM response.
        
        Args:
            llm_response: LLM response string
            
        Returns:
            List of refined peptide dictionaries
        """
        try:
            # Try to parse JSON response
            if '{' in llm_response and '}' in llm_response:
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                json_str = llm_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                refined_peptides = []
                for refined in parsed.get('refined_peptides', []):
                    peptide = {
                        'id': refined.get('id', ''),
                        'sequence': refined.get('sequence', ''),
                        'original_id': refined.get('original_id', ''),
                        'improvements': refined.get('improvements', []),
                        'reasoning': refined.get('reasoning', ''),
                        'focus_areas': refined.get('focus_areas', []),
                        'source': 'llm_refined'
                    }
                    refined_peptides.append(peptide)
                
                return refined_peptides
        except Exception as e:
            print(f"Error parsing refined peptides: {e}")
        
        # Fallback: return empty list if parsing fails
        return []
    
    def _create_comparison_data(self, original_peptides: List[Dict[str, Any]], 
                              refined_peptides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create comprehensive comparison data for side-by-side analysis.
        
        Args:
            original_peptides: Original peptides with properties
            refined_peptides: Refined peptides with properties
            
        Returns:
            Dictionary with comparison data and analysis
        """
        comparison_data = {
            'summary': {
                'total_peptides': len(original_peptides),
                'improvement_areas': [],
                'overall_score': 0
            },
            'detailed_comparison': [],
            'improvement_metrics': {},
            'property_changes': {}
        }
        
        # Create detailed comparison for each peptide pair
        for i, (original, refined) in enumerate(zip(original_peptides, refined_peptides)):
            if i >= len(refined_peptides):
                break
                
            original_props = original.get('properties', {})
            refined_props = refined.get('properties', {})
            
            # Calculate property changes
            property_changes = {}
            for prop in ['molecular_weight', 'isoelectric_point', 'gravy_score', 
                        'net_charge', 'instability_index', 'solubility_score', 
                        'aggregation_tendency', 'binding_potential']:
                orig_val = original_props.get(prop, 0)
                ref_val = refined_props.get(prop, 0)
                change = ref_val - orig_val
                change_percent = (change / orig_val * 100) if orig_val != 0 else 0
                
                property_changes[prop] = {
                    'original': orig_val,
                    'refined': ref_val,
                    'change': change,
                    'change_percent': change_percent,
                    'improved': self._is_improvement(prop, change)
                }
            
            # Create comparison entry
            comparison_entry = {
                'pair_id': f"PAIR_{i+1:03d}",
                'original': {
                    'id': original.get('id', ''),
                    'sequence': original.get('sequence', ''),
                    'properties': original_props
                },
                'refined': {
                    'id': refined.get('id', ''),
                    'sequence': refined.get('sequence', ''),
                    'properties': refined_props,
                    'improvements': refined.get('improvements', []),
                    'reasoning': refined.get('reasoning', ''),
                    'focus_areas': refined.get('focus_areas', [])
                },
                'property_changes': property_changes,
                'overall_improvement_score': self._calculate_improvement_score(property_changes)
            }
            
            comparison_data['detailed_comparison'].append(comparison_entry)
        
        # Calculate overall improvement metrics
        comparison_data['improvement_metrics'] = self._calculate_overall_improvements(
            comparison_data['detailed_comparison']
        )
        
        return comparison_data
    
    def _is_improvement(self, property_name: str, change: float) -> bool:
        """
        Determine if a property change represents an improvement.
        
        Args:
            property_name: Name of the property
            change: Change in value (positive or negative)
            
        Returns:
            True if the change is an improvement
        """
        improvement_directions = {
            'molecular_weight': False,  # Lower is better
            'isoelectric_point': True,  # Depends on context
            'gravy_score': False,       # Lower (more hydrophilic) is better
            'net_charge': True,         # Depends on target
            'instability_index': False, # Lower is better
            'solubility_score': True,   # Higher is better
            'aggregation_tendency': False, # Lower is better
            'binding_potential': True   # Higher is better
        }
        
        direction = improvement_directions.get(property_name, True)
        return (change > 0) == direction
    
    def _calculate_improvement_score(self, property_changes: Dict[str, Any]) -> float:
        """
        Calculate overall improvement score for a peptide pair.
        
        Args:
            property_changes: Dictionary of property changes
            
        Returns:
            Improvement score (0-10)
        """
        improvements = 0
        total_properties = 0
        
        for prop, change_data in property_changes.items():
            if change_data['improved']:
                improvements += 1
            total_properties += 1
        
        if total_properties == 0:
            return 0
        
        return (improvements / total_properties) * 10
    
    def _calculate_overall_improvements(self, detailed_comparison: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall improvement metrics across all peptides.
        
        Args:
            detailed_comparison: List of detailed comparison entries
            
        Returns:
            Dictionary with overall improvement metrics
        """
        if not detailed_comparison:
            return {}
        
        total_improvements = 0
        property_improvements = {}
        
        for comparison in detailed_comparison:
            property_changes = comparison['property_changes']
            total_improvements += comparison['overall_improvement_score']
            
            for prop, change_data in property_changes.items():
                if prop not in property_improvements:
                    property_improvements[prop] = {'improved': 0, 'total': 0}
                
                property_improvements[prop]['total'] += 1
                if change_data['improved']:
                    property_improvements[prop]['improved'] += 1
        
        avg_improvement = total_improvements / len(detailed_comparison)
        
        return {
            'average_improvement_score': avg_improvement,
            'property_improvement_rates': property_improvements,
            'total_peptides_analyzed': len(detailed_comparison)
        }
    
    def get_comparison_dataframe(self) -> pd.DataFrame:
        """
        Create a pandas DataFrame for easy comparison display and export.
        
        Returns:
            DataFrame with comparison data
        """
        if not self.comparison_data:
            return pd.DataFrame()
        
        rows = []
        for comparison in self.comparison_data.get('detailed_comparison', []):
            original = comparison['original']
            refined = comparison['refined']
            changes = comparison['property_changes']
            
            row = {
                'Pair_ID': comparison['pair_id'],
                'Original_ID': original['id'],
                'Original_Sequence': original['sequence'],
                'Refined_ID': refined['id'],
                'Refined_Sequence': refined['sequence'],
                'Improvement_Score': comparison['overall_improvement_score'],
                'Improvements': ', '.join(refined.get('improvements', [])),
                'Focus_Areas': ', '.join(refined.get('focus_areas', []))
            }
            
            # Add property comparisons
            for prop, change_data in changes.items():
                row[f'{prop}_Original'] = change_data['original']
                row[f'{prop}_Refined'] = change_data['refined']
                row[f'{prop}_Change'] = change_data['change']
                row[f'{prop}_Change_Percent'] = change_data['change_percent']
                row[f'{prop}_Improved'] = change_data['improved']
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def export_comparison_csv(self, filename: str = "peptide_comparison.csv") -> str:
        """
        Export comparison data to CSV file.
        
        Args:
            filename: Output filename
            
        Returns:
            File path of exported CSV
        """
        df = self.get_comparison_dataframe()
        if not df.empty:
            df.to_csv(filename, index=False)
            return filename
        return ""
    
    def get_top_candidates(self, num_candidates: int = 3) -> List[Dict[str, Any]]:
        """
        Get top candidates based on improvement scores.
        
        Args:
            num_candidates: Number of top candidates to return
            
        Returns:
            List of top candidate dictionaries
        """
        if not self.comparison_data:
            return []
        
        # Sort by improvement score
        sorted_comparisons = sorted(
            self.comparison_data.get('detailed_comparison', []),
            key=lambda x: x['overall_improvement_score'],
            reverse=True
        )
        
        top_candidates = []
        for i, comparison in enumerate(sorted_comparisons[:num_candidates]):
            candidate = {
                'rank': i + 1,
                'pair_id': comparison['pair_id'],
                'improvement_score': comparison['overall_improvement_score'],
                'original_sequence': comparison['original']['sequence'],
                'refined_sequence': comparison['refined']['sequence'],
                'improvements': comparison['refined']['improvements'],
                'reasoning': comparison['refined']['reasoning']
            }
            top_candidates.append(candidate)
        
        return top_candidates 