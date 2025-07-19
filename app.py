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

def main():
    st.title("🧬 AI-Enhanced Peptide Generator")
    st.markdown("Upload a protein structure (PDB) and generate AI-suggested peptide candidates with detailed reasoning.")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
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
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 Upload Protein Structure")
        
        uploaded_file = st.file_uploader(
            "Choose a PDB file",
            type=['pdb'],
            help="Upload a PDB file to analyze"
        )
        
        if uploaded_file is not None:
            # Display file info
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Read file content
            pdb_content = uploaded_file.read().decode('utf-8')
            
            # Step 1: Parse PDB Structure
            st.header("🔍 Step 1: Protein Structure Analysis")
            
            try:
                parser = PDBParser()
                parsed_result = parser.parse_structure(pdb_content, chain_id)
                
                if parsed_result['success']:
                    st.success("✅ Protein structure parsed successfully!")
                    
                    # Display parsed information
                    with st.expander("📋 Parsed Protein Information", expanded=True):
                        st.write(f"**Chain ID:** {parsed_result['chain_id']}")
                        st.write(f"**Sequence Length:** {len(parsed_result['sequence'])} residues")
                        st.write(f"**Number of Residues:** {len(parsed_result['residues'])}")
                        
                        # Display sequence
                        st.subheader("Protein Sequence")
                        st.code(parsed_result['sequence'])
                        
                        # Display first few residues
                        st.subheader("Residue Information (First 10)")
                        residue_df = pd.DataFrame(parsed_result['residues'][:10])
                        st.dataframe(residue_df, use_container_width=True)
                        
                        # Store parsed data in session state
                        st.session_state['parsed_data'] = parsed_result
                        
                else:
                    st.error(f"❌ Error parsing structure: {parsed_result['error']}")
                    return
                    
            except Exception as e:
                st.error(f"❌ Error during parsing: {str(e)}")
                return
            
            # Step 2: Surface Analysis (Optional)
            if enable_surface_analysis:
                st.header("🌊 Step 2: Surface Analysis")
                
                try:
                    analyzer = SurfaceAnalyzer()
                    surface_result = analyzer.analyze_surface(pdb_content, chain_id)
                    
                    if surface_result['success']:
                        st.success("✅ Surface analysis completed!")
                        
                        # Display surface analysis results
                        with st.expander("📊 Surface Analysis Results", expanded=True):
                            # Summary metrics
                            st.subheader("Summary Metrics")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Residues", surface_result['summary']['total_residues'])
                                st.metric("Surface Residues", surface_result['summary']['surface_residues'])
                            
                            with col2:
                                st.metric("Hydrophobic", surface_result['summary']['hydrophobic_count'])
                                st.metric("Charged", surface_result['summary']['charged_count'])
                            
                            with col3:
                                st.metric("Polar/Other", surface_result['summary']['polar_count'])
                                st.metric("Avg SASA", f"{surface_result['summary']['avg_sasa']:.2f}")
                            
                            # Surface analysis table
                            st.subheader("Residue Surface Analysis")
                            surface_df = pd.DataFrame(surface_result['residues'])
                            st.dataframe(surface_df, use_container_width=True)
                            
                            # Store surface data in session state
                            st.session_state['surface_data'] = surface_result
                            
                    else:
                        st.warning(f"⚠️ Surface analysis failed: {surface_result['error']}")
                        st.info("Continuing without surface analysis data...")
                        
                except Exception as e:
                    st.warning(f"⚠️ Surface analysis error: {str(e)}")
                    st.info("Continuing without surface analysis data...")
            
            # Step 3: Peptide Generation
            if api_key:
                st.header("🤖 Step 3: AI Peptide Generation")
                
                if st.button("Generate Peptide Candidates", type="primary"):
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
                        with st.spinner("🤖 Generating peptide candidates..."):
                            peptides_result = generator.generate_peptides(context_data)
                        
                        if peptides_result['success']:
                            st.success(f"✅ Generated {len(peptides_result['peptides'])} peptide candidates!")
                            
                            # Display peptides
                            st.subheader("🧬 Generated Peptide Candidates")
                            
                            for i, peptide in enumerate(peptides_result['peptides'], 1):
                                with st.expander(f"Peptide {i}: {peptide['sequence']}", expanded=True):
                                    col1, col2 = st.columns([1, 2])
                                    
                                    with col1:
                                        st.write("**Properties:**")
                                        for prop, value in peptide['properties'].items():
                                            st.write(f"• {prop}: {value}")
                                    
                                    with col2:
                                        st.write("**Reasoning:**")
                                        st.write(peptide['explanation'])
                            
                            # Store peptides in session state
                            st.session_state['peptides'] = peptides_result['peptides']
                            
                        else:
                            st.error(f"❌ Peptide generation failed: {peptides_result['error']}")
                            
                    except Exception as e:
                        st.error(f"❌ Error during peptide generation: {str(e)}")
            else:
                st.info("🔑 Please enter your API key in the sidebar to generate peptides.")
    
    with col2:
        st.header("🎯 3D Visualization")
        
        if uploaded_file is not None and 'parsed_data' in st.session_state:
            try:
                visualizer = ProteinVisualizer()
                visualizer.display_structure(pdb_content, chain_id)
            except Exception as e:
                st.error(f"❌ Visualization error: {str(e)}")
        else:
            st.info("📁 Upload a PDB file to see the 3D structure visualization.")

if __name__ == "__main__":
    main() 