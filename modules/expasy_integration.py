"""
ExPASy Integration Module

Provides cloud-optimized integration with ExPASy ProtParam for peptide stability prediction.
Designed specifically for Streamlit Cloud deployment with robust error handling and rate limiting.
"""

import requests
import time
import re
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from urllib.parse import urlencode
import json

class ExPASyIntegration:
    """
    Cloud-optimized ExPASy ProtParam integration for peptide stability prediction.
    
    Features:
    - Robust error handling for cloud deployment
    - Rate limiting to respect service limits
    - Caching to reduce API calls
    - Comprehensive stability analysis
    - Streamlit Cloud compatibility
    """
    
    def __init__(self):
        self.base_url = "https://web.expasy.org/cgi-bin/protparam/protparam"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PeptideAnalyzer/1.0 (Streamlit Cloud)'
        })
        self.rate_limit_delay = 2.0  # Seconds between requests
        self.last_request_time = 0
        self.cache = {}
        
    def _rate_limit(self):
        """Implement rate limiting to respect service limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _parse_protparam_response(self, html_content: str) -> Dict[str, Any]:
        """
        Parse ExPASy ProtParam HTML response to extract stability data.
        
        Args:
            html_content: HTML response from ExPASy ProtParam
            
        Returns:
            Dictionary containing parsed stability parameters
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            results = {}
            
            # Extract molecular weight
            mw_match = re.search(r'Molecular weight:\s*([\d.]+)', html_content)
            if mw_match:
                results['molecular_weight'] = float(mw_match.group(1))
            
            # Extract isoelectric point
            pi_match = re.search(r'Theoretical pI:\s*([\d.]+)', html_content)
            if pi_match:
                results['isoelectric_point'] = float(pi_match.group(1))
            
            # Extract amino acid composition
            aa_composition = {}
            aa_table = soup.find('table', {'class': 'protparam'})
            if aa_table:
                rows = aa_table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        aa = cells[0].get_text(strip=True)
                        count = cells[1].get_text(strip=True)
                        percentage = cells[2].get_text(strip=True)
                        if aa and count.isdigit():
                            aa_composition[aa] = {
                                'count': int(count),
                                'percentage': float(percentage.replace('%', ''))
                            }
            results['amino_acid_composition'] = aa_composition
            
            # Extract instability index
            instability_match = re.search(r'Instability index:\s*([\d.]+)', html_content)
            if instability_match:
                results['instability_index'] = float(instability_match.group(1))
            
            # Extract aliphatic index
            aliphatic_match = re.search(r'Aliphatic index:\s*([\d.]+)', html_content)
            if aliphatic_match:
                results['aliphatic_index'] = float(aliphatic_match.group(1))
            
            # Extract GRAVY (Grand Average of Hydropathy)
            gravy_match = re.search(r'Grand average of hydropathy \(GRAVY\):\s*([-\d.]+)', html_content)
            if gravy_match:
                results['gravy_score'] = float(gravy_match.group(1))
            
            # Extract extinction coefficients
            extinction_match = re.search(r'Extinction coefficients:\s*([\d,]+)', html_content)
            if extinction_match:
                results['extinction_coefficient'] = int(extinction_match.group(1).replace(',', ''))
            
            return results
            
        except Exception as e:
            st.warning(f"⚠️ Error parsing ExPASy response: {str(e)}")
            return {}
    
    def analyze_peptide_stability(self, peptide_sequence: str) -> Dict[str, Any]:
        """
        Analyze peptide stability using ExPASy ProtParam.
        
        Args:
            peptide_sequence: Amino acid sequence to analyze
            
        Returns:
            Dictionary containing stability analysis results
        """
        # Check cache first
        cache_key = f"expasy_{peptide_sequence}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            self._rate_limit()
            
            # Prepare request data
            data = {
                'sequence': peptide_sequence,
                'title': f'Peptide Analysis: {peptide_sequence[:20]}...',
                'organism': 'Unknown',
                'email': 'user@example.com'
            }
            
            # Make request to ExPASy
            response = self.session.post(
                self.base_url,
                data=data,
                timeout=30  # 30 second timeout for cloud
            )
            
            if response.status_code == 200:
                # Parse the response
                parsed_data = self._parse_protparam_response(response.text)
                
                if parsed_data:
                    # Calculate additional stability metrics
                    stability_analysis = self._calculate_stability_metrics(parsed_data, peptide_sequence)
                    
                    # Cache the result
                    self.cache[cache_key] = stability_analysis
                    
                    return stability_analysis
                else:
                    return {
                        'success': False,
                        'error': 'Failed to parse ExPASy response',
                        'data': {}
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.reason}',
                    'data': {}
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout - service may be busy',
                'data': {}
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'data': {}
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'data': {}
            }
    
    def _calculate_stability_metrics(self, expasy_data: Dict[str, Any], sequence: str) -> Dict[str, Any]:
        """
        Calculate comprehensive stability metrics from ExPASy data.
        
        Args:
            expasy_data: Parsed ExPASy data
            sequence: Original peptide sequence
            
        Returns:
            Enhanced stability analysis with calculated metrics
        """
        try:
            # Basic stability assessment
            instability_index = expasy_data.get('instability_index', 0)
            gravy_score = expasy_data.get('gravy_score', 0)
            isoelectric_point = expasy_data.get('isoelectric_point', 7.0)
            
            # Stability scoring
            stability_score = self._calculate_stability_score(instability_index, gravy_score, sequence)
            
            # Risk assessment
            risk_level = self._assess_stability_risk(instability_index, gravy_score)
            
            # Recommendations
            recommendations = self._generate_stability_recommendations(expasy_data, sequence)
            
            return {
                'success': True,
                'data': {
                    'basic_properties': {
                        'molecular_weight': expasy_data.get('molecular_weight', 0),
                        'isoelectric_point': isoelectric_point,
                        'gravy_score': gravy_score,
                        'instability_index': instability_index,
                        'aliphatic_index': expasy_data.get('aliphatic_index', 0),
                        'extinction_coefficient': expasy_data.get('extinction_coefficient', 0)
                    },
                    'stability_analysis': {
                        'stability_score': stability_score,
                        'risk_level': risk_level,
                        'stability_factors': {
                            'hydrophobicity': self._assess_hydrophobicity(gravy_score),
                            'charge_stability': self._assess_charge_stability(isoelectric_point),
                            'size_stability': self._assess_size_stability(len(sequence)),
                            'composition_stability': self._assess_composition_stability(expasy_data.get('amino_acid_composition', {}))
                        }
                    },
                    'recommendations': recommendations,
                    'amino_acid_composition': expasy_data.get('amino_acid_composition', {})
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error calculating stability metrics: {str(e)}',
                'data': {}
            }
    
    def _calculate_stability_score(self, instability_index: float, gravy_score: float, sequence: str) -> float:
        """Calculate overall stability score (0-1, higher is more stable)."""
        try:
            # Normalize instability index (lower is better, max ~100)
            instability_score = max(0, 1 - (instability_index / 100))
            
            # Normalize GRAVY score (moderate hydrophobicity is good)
            gravy_score_norm = max(0, 1 - abs(gravy_score + 0.5) / 2)
            
            # Size factor (optimal size range)
            size_factor = 1.0
            if len(sequence) < 5:
                size_factor = 0.7
            elif len(sequence) > 50:
                size_factor = 0.8
            
            # Calculate weighted average
            stability_score = (instability_score * 0.4 + gravy_score_norm * 0.4 + size_factor * 0.2)
            
            return min(1.0, max(0.0, stability_score))
            
        except Exception:
            return 0.5  # Default neutral score
    
    def _assess_stability_risk(self, instability_index: float, gravy_score: float) -> str:
        """Assess overall stability risk level."""
        try:
            risk_score = 0
            
            # Instability index risk
            if instability_index > 40:
                risk_score += 2
            elif instability_index > 30:
                risk_score += 1
            
            # GRAVY score risk
            if gravy_score > 1.0 or gravy_score < -2.0:
                risk_score += 1
            
            if risk_score >= 3:
                return "High"
            elif risk_score >= 1:
                return "Medium"
            else:
                return "Low"
                
        except Exception:
            return "Unknown"
    
    def _assess_hydrophobicity(self, gravy_score: float) -> str:
        """Assess hydrophobicity stability."""
        if gravy_score < -0.5:
            return "Very Hydrophilic"
        elif gravy_score < 0:
            return "Moderately Hydrophilic"
        elif gravy_score < 0.5:
            return "Moderately Hydrophobic"
        else:
            return "Very Hydrophobic"
    
    def _assess_charge_stability(self, isoelectric_point: float) -> str:
        """Assess charge stability."""
        if 5.0 <= isoelectric_point <= 9.0:
            return "Stable"
        elif 4.0 <= isoelectric_point <= 10.0:
            return "Moderate"
        else:
            return "Unstable"
    
    def _assess_size_stability(self, length: int) -> str:
        """Assess size-based stability."""
        if 5 <= length <= 30:
            return "Optimal"
        elif 3 <= length <= 50:
            return "Acceptable"
        else:
            return "Suboptimal"
    
    def _assess_composition_stability(self, composition: Dict[str, Any]) -> str:
        """Assess amino acid composition stability."""
        try:
            if not composition:
                return "Unknown"
            
            # Check for problematic amino acids
            problematic_aa = ['C', 'M', 'W']  # Cysteine, Methionine, Tryptophan
            problematic_count = sum(composition.get(aa, {}).get('count', 0) for aa in problematic_aa)
            
            if problematic_count == 0:
                return "Excellent"
            elif problematic_count <= 2:
                return "Good"
            else:
                return "Concerning"
                
        except Exception:
            return "Unknown"
    
    def _generate_stability_recommendations(self, expasy_data: Dict[str, Any], sequence: str) -> List[str]:
        """Generate stability improvement recommendations."""
        recommendations = []
        
        try:
            instability_index = expasy_data.get('instability_index', 0)
            gravy_score = expasy_data.get('gravy_score', 0)
            composition = expasy_data.get('amino_acid_composition', {})
            
            # Instability recommendations
            if instability_index > 40:
                recommendations.append("Consider reducing unstable amino acids (D, E, N, Q, S, T)")
            elif instability_index > 30:
                recommendations.append("Monitor instability - consider stabilizing modifications")
            
            # Hydrophobicity recommendations
            if gravy_score > 1.0:
                recommendations.append("Very hydrophobic - consider hydrophilic modifications for solubility")
            elif gravy_score < -2.0:
                recommendations.append("Very hydrophilic - may need hydrophobic modifications for membrane penetration")
            
            # Size recommendations
            if len(sequence) < 5:
                recommendations.append("Very short peptide - consider extending for better stability")
            elif len(sequence) > 50:
                recommendations.append("Long peptide - consider truncation for better bioavailability")
            
            # Composition recommendations
            cys_count = composition.get('C', {}).get('count', 0)
            if cys_count > 2:
                recommendations.append("Multiple cysteines detected - consider disulfide bond formation")
            
            if not recommendations:
                recommendations.append("Peptide shows good stability characteristics")
                
        except Exception:
            recommendations.append("Unable to generate specific recommendations")
        
        return recommendations
    
    def batch_analyze_peptides(self, peptides: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple peptides with rate limiting.
        
        Args:
            peptides: List of peptide sequences to analyze
            
        Returns:
            Dictionary containing analysis results for all peptides
        """
        results = {
            'success': True,
            'peptides': {},
            'summary': {
                'total_analyzed': 0,
                'successful_analyses': 0,
                'failed_analyses': 0,
                'average_stability_score': 0.0
            }
        }
        
        stability_scores = []
        
        for i, peptide in enumerate(peptides):
            st.write(f"Analyzing peptide {i+1}/{len(peptides)}: {peptide[:20]}...")
            
            analysis = self.analyze_peptide_stability(peptide)
            
            if analysis['success']:
                results['peptides'][peptide] = analysis['data']
                results['summary']['successful_analyses'] += 1
                stability_scores.append(analysis['data']['stability_analysis']['stability_score'])
            else:
                results['peptides'][peptide] = {
                    'error': analysis['error'],
                    'data': {}
                }
                results['summary']['failed_analyses'] += 1
            
            results['summary']['total_analyzed'] += 1
        
        # Calculate average stability score
        if stability_scores:
            results['summary']['average_stability_score'] = sum(stability_scores) / len(stability_scores)
        
        return results 