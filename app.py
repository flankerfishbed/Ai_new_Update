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
        /* Import Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global styles */
        .main {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Container with full width */
        .main-container {
            width: 100%;
            padding: 0 2rem;
        }
        
        /* Card component */
        .card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: rgba(0, 0, 0, 0.15) 0 4px 16px;
            backdrop-filter: blur(10px);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .card-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #ffffff;
            margin: 0;
        }
        
        .card-subtitle {
            font-size: 0.95rem;
            color: rgba(255, 255, 255, 0.7);
            margin: 0.5rem 0 0 0;
        }
        
        /* KPI tiles */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .kpi-tile {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: rgba(0, 0, 0, 0.1) 0 2px 8px;
        }
        
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            color: #6366f1;
            margin-bottom: 0.5rem;
        }
        
        .kpi-label {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
            font-weight: 500;
        }
        
        /* Buttons */
        .stButton > button {
            background: #6366f1;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            box-shadow: rgba(0, 0, 0, 0.1) 0 2px 8px;
        }
        
        .stButton > button:hover {
            background: #4f46e5;
            transform: translateY(-1px);
            box-shadow: rgba(0, 0, 0, 0.15) 0 4px 12px;
        }
        
        .stButton > button:focus {
            outline: 2px solid #6366f1;
            outline-offset: 2px;
        }
        
        /* Status messages */
        .status-success {
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            color: #22c55e;
        }
        
        .status-warning {
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            color: #f59e0b;
        }
        
        .status-error {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            color: #ef4444;
        }
        
        .status-info {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            color: #3b82f6;
        }
        
        /* Tables */
        .dataframe {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .dataframe th {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            font-weight: 600;
            padding: 1rem;
        }
        
        .dataframe td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .dataframe tr:nth-child(even) {
            background: rgba(255, 255, 255, 0.02);
        }
        
        /* Sequence display */
        .sequence-display {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            overflow-x: auto;
            color: #6366f1;
        }
        
        /* Peptide cards */
        .peptide-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: rgba(0, 0, 0, 0.1) 0 2px 8px;
        }
        
        .peptide-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .peptide-sequence {
            font-family: 'Courier New', monospace;
            font-size: 1.1rem;
            font-weight: 600;
            color: #6366f1;
            margin-right: 1rem;
        }
        
        .peptide-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 1.5rem;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-container {
                padding: 0 1rem;
            }
            
            .peptide-content {
                grid-template-columns: 1fr;
            }
            
            .kpi-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: #1a1a1a;
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def card(title, body, subtitle=None):
    """Reusable card component"""
    subtitle_html = f'<p class="card-subtitle">{subtitle}</p>' if subtitle else ''
    
    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            <div>
                <h2 class="card-title">{title}</h2>
                {subtitle_html}
            </div>
        </div>
        <div class="card-body">
            {body}
        </div>
    </div>
    """, unsafe_allow_html=True)

def kpi_tile(value, label):
    """KPI tile component"""
    st.markdown(f"""
    <div class="kpi-tile">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def status_message(message, status_type="info"):
    """Status message component"""
    status_class = f"status-{status_type}"
    st.markdown(f'<div class="{status_class}">{message}</div>', unsafe_allow_html=True)

def main():
    # Inject CSS
    inject_css()
    
    # Main container
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # Header
        card(
            "AI-Enhanced Peptide Generator",
            """
            <p style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.8); margin: 0;">
                Upload a protein structure (PDB) and generate AI-suggested peptide candidates with detailed reasoning.
            </p>
            """
        )
        
        # Sidebar configuration
        with st.sidebar:
            st.markdown("""
            <div style="padding: 1rem 0;">
                <h3 style="color: #ffffff; margin-bottom: 1rem;">Configuration</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # LLM Provider Selection
            provider_name = st.selectbox(
                "LLM Provider",
                ["OpenAI", "Anthropic", "Groq", "Mistral"],
                help="Select the AI provider for peptide generation"
            )
            
            # API Key input
            api_key = st.text_input(
                "API Key",
                type="password",
                help="Enter your API key for the selected provider"
            )
            
            # Model selection
            model_options = {
                "OpenAI": ["gpt-4", "gpt-3.5-turbo"],
                "Anthropic": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                "Groq": ["llama3-8b-8192", "llama3-70b-8192"],
                "Mistral": ["mistral-large-latest", "mistral-medium-latest"]
            }
            
            model_name = st.selectbox(
                "Model",
                model_options.get(provider_name, []),
                help="Select the specific model to use"
            )
            
            st.markdown("---")
            
            # Analysis settings
            st.markdown("""
            <div style="padding: 1rem 0;">
                <h3 style="color: #ffffff; margin-bottom: 1rem;">Analysis Settings</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Chain selection
            chain_id = st.text_input(
                "Chain ID",
                value="A",
                help="Enter the chain ID to analyze (default: A)"
            )
            
            # Number of peptides
            num_peptides = st.slider(
                "Number of Peptides",
                min_value=1,
                max_value=10,
                value=3,
                help="Number of peptide candidates to generate"
            )
            
            # Surface analysis toggle
            enable_surface_analysis = st.checkbox(
                "Enable Surface Analysis",
                value=True,
                help="Calculate solvent-accessible surface area for residues"
            )
            
            # Help section
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
        
        # Main content area - full width layout
        # File upload section
        card(
            "Upload Protein Structure",
            """
            <div style="text-align: center; padding: 2rem; border: 2px dashed rgba(255, 255, 255, 0.2); border-radius: 12px; background: rgba(255, 255, 255, 0.02);">
                <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">Choose a PDB file to begin analysis</p>
            </div>
            """
        )
        
        uploaded_file = st.file_uploader(
            "Choose a PDB file",
            type=['pdb'],
            help="Upload a PDB file to analyze"
        )
        
        if uploaded_file is not None:
            # Display file info
            status_message(f"File uploaded successfully: {uploaded_file.name}", "success")
            
            # Read file content
            pdb_content = uploaded_file.read().decode('utf-8')
            
            # Protein Structure Analysis
            card(
                "Protein Structure Analysis",
                "",
                subtitle="Analyzing protein structure and extracting sequence information"
            )
            
            with st.spinner("Analyzing protein structure..."):
                try:
                    parser = PDBParser()
                    parsed_result = parser.parse_structure(pdb_content, chain_id)
                    
                    if parsed_result['success']:
                        status_message("Protein structure parsed successfully!", "success")
                        
                        # Display KPI metrics
                        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            kpi_tile(parsed_result['chain_id'], "Chain ID")
                        
                        with col2:
                            kpi_tile(len(parsed_result['sequence']), "Sequence Length")
                        
                        with col3:
                            kpi_tile(len(parsed_result['residues']), "Total Residues")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Display sequence
                        st.subheader("Protein Sequence")
                        st.markdown(f"""
                        <div class="sequence-display">
                            {parsed_result['sequence']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display residue information
                        with st.expander("Detailed Residue Information", expanded=False):
                            residue_df = pd.DataFrame(parsed_result['residues'][:10])
                            st.dataframe(residue_df, use_container_width=True)
                        
                        # Store parsed data in session state
                        st.session_state['parsed_data'] = parsed_result
                        
                    else:
                        status_message(f"Error parsing structure: {parsed_result['error']}", "error")
                        return
                        
                except Exception as e:
                    status_message(f"Error during parsing: {str(e)}", "error")
                    return
            
            # Surface Analysis (Optional)
            if enable_surface_analysis:
                card(
                    "Surface Analysis",
                    "",
                    subtitle="Calculating solvent-accessible surface area and residue properties"
                )
                
                with st.spinner("Analyzing surface properties..."):
                    try:
                        analyzer = SurfaceAnalyzer()
                        surface_result = analyzer.analyze_surface(pdb_content, chain_id)
                        
                        if surface_result['success']:
                            status_message("Surface analysis completed!", "success")
                            
                            # Display surface analysis results
                            summary = surface_result['summary']
                            
                            # Create KPI grid for surface metrics
                            st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                kpi_tile(summary['total_residues'], "Total Residues")
                            
                            with col2:
                                kpi_tile(summary['surface_residues'], "Surface Residues")
                            
                            with col3:
                                kpi_tile(summary['hydrophobic_count'], "Hydrophobic")
                            
                            with col4:
                                kpi_tile(summary['charged_count'], "Charged")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Additional metrics
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                kpi_tile(summary['polar_count'], "Polar/Other")
                            
                            with col2:
                                kpi_tile(f"{summary['avg_sasa']:.2f} Å²", "Avg SASA")
                            
                            # Surface analysis table
                            with st.expander("Detailed Surface Analysis", expanded=False):
                                surface_df = pd.DataFrame(surface_result['residues'])
                                st.dataframe(surface_df, use_container_width=True)
                            
                            # Store surface data in session state
                            st.session_state['surface_data'] = surface_result
                            
                        else:
                            status_message(f"Surface analysis failed: {surface_result['error']}", "warning")
                            status_message("Continuing without surface analysis data...", "info")
                            
                    except Exception as e:
                        status_message(f"Surface analysis error: {str(e)}", "warning")
                        status_message("Continuing without surface analysis data...", "info")
            
            # Peptide Generation
            if api_key:
                card(
                    "AI Peptide Generation",
                    "",
                    subtitle="Generating AI-suggested peptide candidates with detailed reasoning"
                )
                
                if st.button("Generate Peptide Candidates", use_container_width=True):
                    with st.spinner("Generating peptide candidates..."):
                        try:
                            # Initialize LLM provider
                            llm_factory = LLMProviderFactory()
                            llm_provider = llm_factory.create_provider(provider_name, api_key, model_name)
                            
                            # Initialize peptide generator
                            generator = PeptideGenerator(llm_provider)
                            
                            # Prepare context data
                            context_data = {
                                'sequence': parsed_result['sequence'],
                                'residues': parsed_result['residues'],
                                'chain_id': chain_id,
                                'num_peptides': num_peptides
                            }
                            
                            # Add surface data if available
                            if enable_surface_analysis and 'surface_data' in st.session_state:
                                context_data['surface_data'] = st.session_state['surface_data']
                            
                            # Generate peptides
                            peptides_result = generator.generate_peptides(context_data)
                            
                            if peptides_result['success']:
                                status_message(f"Generated {len(peptides_result['peptides'])} peptide candidates!", "success")
                                
                                # Display peptides
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
                                
                                # Store peptides in session state
                                st.session_state['peptides'] = peptides_result['peptides']
                                
                            else:
                                status_message(f"Peptide generation failed: {peptides_result['error']}", "error")
                                
                        except Exception as e:
                            status_message(f"Error during peptide generation: {str(e)}", "error")
            else:
                status_message("Please enter your API key in the sidebar to generate peptides", "info")
            
            # 3D Visualization - full width
            card(
                "3D Visualization",
                "",
                subtitle="Interactive protein structure visualization"
            )
            
            if uploaded_file is not None and 'parsed_data' in st.session_state:
                try:
                    visualizer = ProteinVisualizer()
                    visualizer.display_structure(pdb_content, chain_id)
                except Exception as e:
                    status_message(f"Visualization error: {str(e)}", "error")
            else:
                status_message("Upload a PDB file to see the 3D structure visualization", "info")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
