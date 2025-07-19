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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .step-header {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .peptide-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .sidebar-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: white;
    }
    
    .success-box {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .sequence-display {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
    }
    
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🧬 AI-Enhanced Peptide Generator</h1>
        <p>Upload a protein structure (PDB) and generate AI-suggested peptide candidates with detailed reasoning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h3>⚙️ Configuration</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # LLM Provider Selection
        provider_name = st.selectbox(
            "🤖 LLM Provider",
            ["OpenAI", "Anthropic", "Groq", "Mistral"],
            help="Select the AI provider for peptide generation"
        )
        
        # API Key input
        api_key = st.text_input(
            "🔑 API Key",
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
            "🧠 Model",
            model_options.get(provider_name, []),
            help="Select the specific model to use"
        )
        
        st.markdown("---")
        
        # Analysis settings
        st.markdown("""
        <div class="sidebar-section">
            <h3>🔬 Analysis Settings</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Chain selection
        chain_id = st.text_input(
            "🔗 Chain ID",
            value="A",
            help="Enter the chain ID to analyze (default: A)"
        )
        
        # Number of peptides
        num_peptides = st.slider(
            "📊 Number of Peptides",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of peptide candidates to generate"
        )
        
        # Surface analysis toggle
        enable_surface_analysis = st.checkbox(
            "🌊 Enable Surface Analysis",
            value=True,
            help="Calculate solvent-accessible surface area for residues"
        )
        
        # Help section
        st.markdown("---")
        st.markdown("""
        <div class="sidebar-section">
            <h3>❓ Help</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("How to use"):
            st.markdown("""
            1. **Upload PDB File**: Choose a protein structure file
            2. **Configure AI**: Select provider and enter API key
            3. **Analyze**: Review protein structure and surface analysis
            4. **Generate**: Create AI-suggested peptide candidates
            """)
        
        with st.expander("API Keys"):
            st.markdown("""
            - **OpenAI**: Get from [platform.openai.com](https://platform.openai.com/api-keys)
            - **Anthropic**: Get from [console.anthropic.com](https://console.anthropic.com/)
            - **Groq**: Get from [console.groq.com](https://console.groq.com/)
            - **Mistral**: Get from [console.mistral.ai](https://console.mistral.ai/)
            """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="upload-area">
            <h3>📁 Upload Protein Structure</h3>
            <p>Choose a PDB file to begin analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a PDB file",
            type=['pdb'],
            help="Upload a PDB file to analyze"
        )
        
        if uploaded_file is not None:
            # Display file info
            st.markdown(f"""
            <div class="success-box">
                <h4>✅ File Uploaded Successfully</h4>
                <p><strong>Filename:</strong> {uploaded_file.name}</p>
                <p><strong>Size:</strong> {uploaded_file.size} bytes</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Read file content
            pdb_content = uploaded_file.read().decode('utf-8')
            
            # Progress indicator
            st.markdown("""
            <div class="progress-container">
                <h4>🔄 Analysis Progress</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Step 1: Parse PDB Structure
            st.markdown("""
            <div class="step-header">
                <h3>🔍 Step 1: Protein Structure Analysis</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("Analyzing protein structure..."):
                try:
                    parser = PDBParser()
                    parsed_result = parser.parse_structure(pdb_content, chain_id)
                    
                    if parsed_result['success']:
                        st.markdown("""
                        <div class="success-box">
                            <h4>✅ Protein Structure Parsed Successfully!</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display parsed information in a nice layout
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("""
                            <div class="metric-card">
                                <h4>Chain ID</h4>
                                <h2>{}</h2>
                            </div>
                            """.format(parsed_result['chain_id']), unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("""
                            <div class="metric-card">
                                <h4>Sequence Length</h4>
                                <h2>{}</h2>
                            </div>
                            """.format(len(parsed_result['sequence'])), unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown("""
                            <div class="metric-card">
                                <h4>Total Residues</h4>
                                <h2>{}</h2>
                            </div>
                            """.format(len(parsed_result['residues'])), unsafe_allow_html=True)
                        
                        # Display sequence in a nice format
                        st.subheader("🧬 Protein Sequence")
                        st.markdown(f"""
                        <div class="sequence-display">
                            {parsed_result['sequence']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display residue information
                        with st.expander("📋 Detailed Residue Information", expanded=False):
                            residue_df = pd.DataFrame(parsed_result['residues'])
                            st.dataframe(residue_df, use_container_width=True)
                        
                        # Store parsed data in session state
                        st.session_state['parsed_data'] = parsed_result
                        
                    else:
                        st.markdown(f"""
                        <div class="warning-box">
                            <h4>❌ Error Parsing Structure</h4>
                            <p>{parsed_result['error']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        return
                        
                except Exception as e:
                    st.markdown(f"""
                    <div class="warning-box">
                        <h4>❌ Error During Parsing</h4>
                        <p>{str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    return
            
            # Step 2: Surface Analysis (Optional)
            if enable_surface_analysis:
                st.markdown("""
                <div class="step-header">
                    <h3>🌊 Step 2: Surface Analysis</h3>
                </div>
                """, unsafe_allow_html=True)
                
                with st.spinner("Analyzing surface properties..."):
                    try:
                        analyzer = SurfaceAnalyzer()
                        surface_result = analyzer.analyze_surface(pdb_content, chain_id)
                        
                        if surface_result['success']:
                            st.markdown("""
                            <div class="success-box">
                                <h4>✅ Surface Analysis Completed!</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display surface analysis results in a nice layout
                            summary = surface_result['summary']
                            
                            # Create metrics in a grid
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>Total Residues</h4>
                                    <h2>{summary['total_residues']}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>Surface Residues</h4>
                                    <h2>{summary['surface_residues']}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col3:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>Hydrophobic</h4>
                                    <h2>{summary['hydrophobic_count']}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col4:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>Charged</h4>
                                    <h2>{summary['charged_count']}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Additional metrics
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>Polar/Other</h4>
                                    <h2>{summary['polar_count']}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>Avg SASA</h4>
                                    <h2>{summary['avg_sasa']:.2f} Å²</h2>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Surface analysis table
                            with st.expander("📊 Detailed Surface Analysis", expanded=False):
                                surface_df = pd.DataFrame(surface_result['residues'])
                                st.dataframe(surface_df, use_container_width=True)
                            
                            # Store surface data in session state
                            st.session_state['surface_data'] = surface_result
                            
                        else:
                            st.markdown(f"""
                            <div class="warning-box">
                                <h4>⚠️ Surface Analysis Failed</h4>
                                <p>{surface_result['error']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown("""
                            <div class="info-box">
                                <h4>ℹ️ Continuing without surface analysis data...</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.markdown(f"""
                        <div class="warning-box">
                            <h4>⚠️ Surface Analysis Error</h4>
                            <p>{str(e)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("""
                        <div class="info-box">
                            <h4>ℹ️ Continuing without surface analysis data...</h4>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Step 3: Peptide Generation
            if api_key:
                st.markdown("""
                <div class="step-header">
                    <h3>🤖 Step 3: AI Peptide Generation</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 Generate Peptide Candidates", type="primary", use_container_width=True):
                    with st.spinner("🤖 Generating peptide candidates..."):
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
                                st.markdown(f"""
                                <div class="success-box">
                                    <h4>✅ Generated {len(peptides_result['peptides'])} Peptide Candidates!</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Display peptides in a nice layout
                                st.subheader("🧬 Generated Peptide Candidates")
                                
                                for i, peptide in enumerate(peptides_result['peptides'], 1):
                                    st.markdown(f"""
                                    <div class="peptide-card">
                                        <h4>Peptide {i}: {peptide['sequence']}</h4>
                                        <div style="display: flex; justify-content: space-between;">
                                            <div style="flex: 1;">
                                                <h5>Properties:</h5>
                                                <ul>
                                                    <li><strong>Length:</strong> {peptide['properties']['length']}</li>
                                                    <li><strong>Net Charge:</strong> {peptide['properties']['net_charge']}</li>
                                                    <li><strong>Hydrophobicity:</strong> {peptide['properties']['hydrophobicity']}</li>
                                                    <li><strong>Motifs:</strong> {', '.join(peptide['properties']['motifs'])}</li>
                                                </ul>
                                            </div>
                                            <div style="flex: 2; margin-left: 1rem;">
                                                <h5>Reasoning:</h5>
                                                <p>{peptide['explanation']}</p>
                                            </div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Store peptides in session state
                                st.session_state['peptides'] = peptides_result['peptides']
                                
                            else:
                                st.markdown(f"""
                                <div class="warning-box">
                                    <h4>❌ Peptide Generation Failed</h4>
                                    <p>{peptides_result['error']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                        except Exception as e:
                            st.markdown(f"""
                            <div class="warning-box">
                                <h4>❌ Error During Peptide Generation</h4>
                                <p>{str(e)}</p>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-box">
                    <h4>🔑 Please enter your API key in the sidebar to generate peptides</h4>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="step-header">
            <h3>🎯 3D Visualization</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if uploaded_file is not None and 'parsed_data' in st.session_state:
            try:
                visualizer = ProteinVisualizer()
                visualizer.display_structure(pdb_content, chain_id)
            except Exception as e:
                st.markdown(f"""
                <div class="warning-box">
                    <h4>❌ Visualization Error</h4>
                    <p>{str(e)}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                <h4>📁 Upload a PDB file to see the 3D structure visualization</h4>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
