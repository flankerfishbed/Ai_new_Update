import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

# Import our modular pipeline components
from modules.pdb_parser import PDBParser
from modules.surface_analyzer import SurfaceAnalyzer
from modules.peptide_generator import PeptideGenerator
from modules.visualizer import ProteinVisualizer
from modules.llm_providers import LLMProviderFactory

# Page configuration
st.set_page_config(
    page_title="AI-Enhanced Peptide Generator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global CSS injection
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        .main { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
        .main-container { max-width: 1600px; margin: 0 auto; padding: 0 2vw; }
        .upload-area { border: 2px dashed rgba(255,255,255,0.3); border-radius: 12px; padding: 3rem 2rem; text-align: center; background: rgba(255,255,255,0.02); margin: 1rem 0; width: 100%; }
        .upload-text { color: rgba(255,255,255,0.7); font-size: 1.1rem; margin-bottom: 1rem; }
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin: 1.5rem 0; width: 100%; }
        .kpi-tile { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: rgba(0,0,0,0.1) 0 2px 8px; }
        .kpi-value { font-size: 2rem; font-weight: 700; color: #6366f1; margin-bottom: 0.5rem; }
        .kpi-label { font-size: 0.875rem; color: rgba(255,255,255,0.7); font-weight: 500; }
        .sequence-display { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; font-family: 'Courier New', monospace; font-size: 0.9rem; overflow-x: auto; color: #6366f1; }
        .peptide-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 1.5rem; margin: 1rem 0; box-shadow: rgba(0,0,0,0.1) 0 2px 8px; width: 100%; }
        .peptide-header { display: flex; align-items: center; margin-bottom: 1rem; }
        .peptide-sequence { font-family: 'Courier New', monospace; font-size: 1.1rem; font-weight: 600; color: #6366f1; margin-right: 1rem; }
        .peptide-content { display: grid; grid-template-columns: 1fr 2fr; gap: 1.5rem; width: 100%; }
        .dataframe { background: rgba(255,255,255,0.05); border-radius: 12px; overflow: hidden; width: 100%; }
        @media (max-width: 900px) { .main-container { padding: 0 0.5rem; } .kpi-grid { grid-template-columns: 1fr; } .peptide-content { grid-template-columns: 1fr; } }
    </style>
    """, unsafe_allow_html=True)

def kpi_tile(value, label):
    st.markdown(f"""
    <div class="kpi-tile">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def main():
    inject_css()
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.title("AI-Enhanced Peptide Generator")
        st.markdown("Upload a protein structure (PDB) and generate AI-suggested peptide candidates with detailed reasoning.")
        # Sidebar
        with st.sidebar:
            st.header("Configuration")
            provider_name = st.selectbox("LLM Provider", ["OpenAI", "Anthropic", "Groq", "Mistral"], help="Select the AI provider for peptide generation")
            api_key = st.text_input("API Key", type="password", help="Enter your API key for the selected provider")
            model_options = {"OpenAI": ["gpt-4", "gpt-3.5-turbo"], "Anthropic": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"], "Groq": ["llama3-8b-8192", "llama3-70b-8192"], "Mistral": ["mistral-large-latest", "mistral-medium-latest"]}
            model_name = st.selectbox("Model", model_options.get(provider_name, []), help="Select the specific model to use")
            st.header("Analysis Settings")
            chain_id = st.text_input("Chain ID", value="A", help="Enter the chain ID to analyze (default: A)")
            num_peptides = st.slider("Number of Peptides", min_value=1, max_value=10, value=3, help="Number of peptide candidates to generate")
            enable_surface_analysis = st.checkbox("Enable Surface Analysis", value=True, help="Calculate solvent-accessible surface area for residues")
            st.markdown("---")
            with st.expander("Help"):
                st.markdown("""
                1. **Upload PDB File**: Choose a protein structure file
                2. **Configure AI**: Select provider and enter API key
                3. **Analyze**: Review protein structure and surface analysis
                4. **Generate**: Create AI-suggested peptide candidates
                """)
            with st.expander("API Keys"):
                st.markdown("""
                - **OpenAI**: [platform.openai.com](https://platform.openai.com/api-keys)
                - **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
                - **Groq**: [console.groq.com](https://console.groq.com/)
                - **Mistral**: [console.mistral.ai](https://console.mistral.ai/)
                """)
        # Main content (full width)
        st.header("Upload Protein Structure")
        st.markdown("""
        <div class="upload-area">
            <div class="upload-text">Choose a PDB file to begin analysis</div>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a PDB file", type=['pdb'], help="Upload a PDB file to analyze")
        if uploaded_file is not None:
            st.success(f"File uploaded successfully: {uploaded_file.name}")
            pdb_content = uploaded_file.read().decode('utf-8')
            st.header("Protein Structure Analysis")
            with st.spinner("Analyzing protein structure..."):
                try:
                    parser = PDBParser()
                    parsed_result = parser.parse_structure(pdb_content, chain_id)
                    if parsed_result['success']:
                        st.success("Protein structure parsed successfully!")
                        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
                        kpi_cols = st.columns(3)
                        with kpi_cols[0]: kpi_tile(parsed_result['chain_id'], "Chain ID")
                        with kpi_cols[1]: kpi_tile(len(parsed_result['sequence']), "Sequence Length")
                        with kpi_cols[2]: kpi_tile(len(parsed_result['residues']), "Total Residues")
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.subheader("Protein Sequence")
                        st.markdown(f"<div class='sequence-display'>{parsed_result['sequence']}</div>", unsafe_allow_html=True)
                        with st.expander("Detailed Residue Information", expanded=False):
                            residue_df = pd.DataFrame(parsed_result['residues'][:10])
                            st.dataframe(residue_df, use_container_width=True)
                        st.session_state['parsed_data'] = parsed_result
                    else:
                        st.error(f"Error parsing structure: {parsed_result['error']}")
                        return
                except Exception as e:
                    st.error(f"Error during parsing: {str(e)}")
                    return
            if enable_surface_analysis:
                st.header("Surface Analysis")
                with st.spinner("Analyzing surface properties..."):
                    try:
                        analyzer = SurfaceAnalyzer()
                        surface_result = analyzer.analyze_surface(pdb_content, chain_id)
                        if surface_result['success']:
                            st.success("Surface analysis completed!")
                            summary = surface_result['summary']
                            st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
                            kpi_cols = st.columns(4)
                            with kpi_cols[0]: kpi_tile(summary['total_residues'], "Total Residues")
                            with kpi_cols[1]: kpi_tile(summary['surface_residues'], "Surface Residues")
                            with kpi_cols[2]: kpi_tile(summary['hydrophobic_count'], "Hydrophobic")
                            with kpi_cols[3]: kpi_tile(summary['charged_count'], "Charged")
                            st.markdown('</div>', unsafe_allow_html=True)
                            kpi_cols2 = st.columns(2)
                            with kpi_cols2[0]: kpi_tile(summary['polar_count'], "Polar/Other")
                            with kpi_cols2[1]: kpi_tile(f"{summary['avg_sasa']:.2f} Å²", "Avg SASA")
                            with st.expander("Detailed Surface Analysis", expanded=False):
                                surface_df = pd.DataFrame(surface_result['residues'])
                                st.dataframe(surface_df, use_container_width=True)
                            st.session_state['surface_data'] = surface_result
                        else:
                            st.warning(f"Surface analysis failed: {surface_result['error']}")
                            st.info("Continuing without surface analysis data...")
                    except Exception as e:
                        st.warning(f"Surface analysis error: {str(e)}")
                        st.info("Continuing without surface analysis data...")
            if api_key:
                st.header("AI Peptide Generation")
                if st.button("Generate Peptide Candidates", use_container_width=True):
                    with st.spinner("Generating peptide candidates..."):
                        try:
                            llm_factory = LLMProviderFactory()
                            llm_provider = llm_factory.create_provider(provider_name, api_key, model_name)
                            generator = PeptideGenerator(llm_provider)
                            context_data = {
                                'sequence': parsed_result['sequence'],
                                'residues': parsed_result['residues'],
                                'chain_id': chain_id,
                                'num_peptides': num_peptides
                            }
                            if enable_surface_analysis and 'surface_data' in st.session_state:
                                context_data['surface_data'] = st.session_state['surface_data']
                            peptides_result = generator.generate_peptides(context_data)
                            if peptides_result['success']:
                                st.success(f"Generated {len(peptides_result['peptides'])} peptide candidates!")
                                st.subheader("Generated Peptide Candidates")
                                for i, peptide in enumerate(peptides_result['peptides'], 1):
                                    st.markdown(f"""
                                    <div class="peptide-card">
                                        <div class="peptide-header">
                                            <span class="peptide-sequence">Peptide {i}: {peptide['sequence']}</span>
                                        </div>
                                        <div class="peptide-content">
                                            <div>
                                                <h5 style="color: #ffffff; margin-bottom: 0.5rem;">Properties:</h5>
                                                <ul style="color: rgba(255, 255, 255, 0.8);">
                                                    <li><strong>Length:</strong> {peptide['properties']['length']}</li>
                                                    <li><strong>Net Charge:</strong> {peptide['properties']['net_charge']}</li>
                                                    <li><strong>Hydrophobicity:</strong> {peptide['properties']['hydrophobicity']}</li>
                                                    <li><strong>Motifs:</strong> {', '.join(peptide['properties']['motifs'])}</li>
                                                </ul>
                                            </div>
                                            <div>
                                                <h5 style="color: #ffffff; margin-bottom: 0.5rem;">Reasoning:</h5>
                                                <p style="color: rgba(255, 255, 255, 0.8); line-height: 1.6;">{peptide['explanation']}</p>
                                            </div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                st.session_state['peptides'] = peptides_result['peptides']
                            else:
                                st.error(f"Peptide generation failed: {peptides_result['error']}")
                        except Exception as e:
                            st.error(f"Error during peptide generation: {str(e)}")
            else:
                st.info("Please enter your API key in the sidebar to generate peptides")
            st.header("3D Visualization")
            if uploaded_file is not None and 'parsed_data' in st.session_state:
                try:
                    visualizer = ProteinVisualizer()
                    visualizer.display_structure(pdb_content, chain_id)
                except Exception as e:
                    st.error(f"Visualization error: {str(e)}")
            else:
                st.info("Upload a PDB file to see the 3D structure visualization")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
