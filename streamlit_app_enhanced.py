import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any

# Import our enhanced modular pipeline components
from modules.pdb_parser import PDBParser
from modules.surface_analyzer import SurfaceAnalyzer
from modules.peptide_generator import PeptideGenerator
from modules.enhanced_visualizer import EnhancedVisualizer
from modules.llm_providers import LLMProviderFactory
from modules.solubility_predictor import SolubilityPredictor, SOLVENTS
from modules.peptide_analyzer import AdvancedPeptideAnalyzer
# from modules.interaction_analyzer import InteractionAnalyzer  # Disabled for simplified visualization
from modules.expasy_integration import ExPASyIntegration
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="AI-Enhanced Peptide Generator Pro",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS injection
def inject_enhanced_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        .main { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
        .main-container { max-width: 1800px; margin: 0 auto; padding: 0 2vw; }
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
        
        /* Enhanced generate button */
        .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 1rem 3rem;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: rgba(99, 102, 241, 0.3) 0 4px 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
            transform: translateY(-2px);
            box-shadow: rgba(99, 102, 241, 0.4) 0 8px 24px;
        }
        
        /* Analysis tabs */
        .analysis-tabs {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Progress indicators */
        .progress-container {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Comparative analysis */
        .comparative-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 1.5rem 0;
        }
        
        /* Enhanced peptide cards */
        .enhanced-peptide-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: rgba(0,0,0,0.1) 0 4px 12px;
        }
        
        .analysis-section {
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .metric-badge {
            display: inline-block;
            background: rgba(99, 102, 241, 0.2);
            color: #6366f1;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 0.25rem;
        }
        
        @media (max-width: 900px) { 
            .main-container { padding: 0 0.5rem; } 
            .kpi-grid { grid-template-columns: 1fr; } 
            .peptide-content { grid-template-columns: 1fr; } 
        }
    </style>
    """, unsafe_allow_html=True)

def kpi_tile(value, label):
    st.markdown(f"""
    <div class="kpi-tile">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def display_peptide_analysis(peptide: Dict[str, Any], analysis_result: Dict[str, Any], peptide_index: int = 1, expasy_data: Dict[str, Any] = None):
    """Display comprehensive peptide analysis."""
    import plotly.graph_objects as go
    
    st.markdown(f"""
    <div class="enhanced-peptide-card">
        <div class="peptide-header">
            <span class="peptide-sequence">Peptide: {peptide['sequence']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Basic properties
    basic_props = analysis_result['analysis']['basic_properties']
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Molecular Weight", f"{basic_props['molecular_weight']:.1f} Da")
    with col2:
        st.metric("Isoelectric Point", f"{basic_props['isoelectric_point']:.2f}")
    with col3:
        st.metric("GRAVY Score", f"{basic_props['gravy_score']:.3f}")
    with col4:
        st.metric("Net Charge", basic_props['net_charge'])
    
    # Binding affinity
    st.subheader("🔗 Binding Affinity Analysis")
    binding = analysis_result['analysis']['binding_affinity']
    st.metric("Binding Score", f"{binding['binding_score']:.3f}")
    
    # Factors contributing to binding
    factors = binding['factors']
    st.write("**Contributing Factors:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Hydrophobicity", f"{factors['hydrophobicity']:.3f}")
    with col2:
        st.metric("Charge Contribution", f"{factors['charge_contribution']:.3f}")
    with col3:
        st.metric("Polarity Contribution", f"{factors['polarity_contribution']:.3f}")
    
    # Stability analysis removed - using ExPASy for professional stability analysis
    
    # Immunogenicity
    st.subheader("🩸 Immunogenicity Assessment")
    immuno = analysis_result['analysis']['immunogenicity']
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Immunogenicity Score", f"{immuno['immunogenicity_score']:.3f}")
    with col2:
        st.metric("Risk Level", immuno['risk_level'])
    with col3:
        st.metric("Charged Residues", immuno['charged_residues'])
    
    # Enhanced Solubility Profile
    st.subheader("💧 Solubility Profile")
    solubility = analysis_result['analysis']['solubility_profile']
    
    # Basic solubility metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("GRAVY Score", f"{solubility['gravy_score']:.3f}")
    with col2:
        st.metric("Net Charge", solubility['net_charge'])
    with col3:
        st.metric("Overall Solubility", solubility['solubility_level'])
    
    # Multi-solvent solubility analysis
    st.write("""**Solvents analyzed:**  
- Water (universal biological solvent)  
- PBS (physiological buffer)  
- DMSO (for hydrophobic peptides)  
- Ethanol, Methanol, Acetonitrile (chromatography, precipitation)  
- Urea, Guanidine HCl (denaturants)  
- TFA (peptide synthesis/purification)  
""")
    
    # Import solubility predictor and generate data
    from modules.solubility_predictor import SolubilityPredictor, REFERENCE_PEPTIDES
    solubility_predictor = SolubilityPredictor()
    solubility_data = solubility_predictor.solubility_panel(peptide['sequence'])
    
    # Reference peptide selection
    st.write("**Compare with reference peptides:**")
    reference_options = ["None"] + list(REFERENCE_PEPTIDES.keys())
    selected_references = st.multiselect(
        "Select reference peptides for comparison:",
        options=reference_options[1:],  # Exclude "None"
        default=["GRGDS", "RGD"],
        help="Choose reference peptides to compare solubility profiles",
        key=f"reference_peptides_{peptide_index}"
    )
    
    # Create enhanced solubility chart with references
    fig = go.Figure()
    
    # Add user's peptide data
    solvents = [item["Solvent"] for item in solubility_data]
    values = [item["Solubility (AU)"] for item in solubility_data]
    
    fig.add_trace(go.Bar(
        x=solvents,
        y=values,
        name=f"Your Peptide: {peptide['sequence']}",
        marker_color='#6366f1',
        opacity=0.9
    ))
    
    # Add reference peptides
    colors = ['#2ED573', '#FFA502', '#FF4757', '#3742FA', '#FF6B6B', '#45B7D1', '#96CEB4']
    for i, ref_key in enumerate(selected_references):
        if ref_key in REFERENCE_PEPTIDES:
            ref_data = solubility_predictor.get_reference_solubility_data(ref_key)
            if ref_data:
                ref_values = [item["Solubility (AU)"] for item in ref_data["solubility_data"]]
                ref_info = ref_data["peptide_info"]
                
                fig.add_trace(go.Bar(
                    x=solvents,
                    y=ref_values,
                    name=f"{ref_key}: {ref_info['description']}",
                    marker_color=colors[i % len(colors)],
                    opacity=0.7
                ))
    
    fig.update_layout(
        title="Peptide Solubility Comparison Across Different Solvents",
        xaxis_title="Solvent",
        yaxis_title="Solubility (AU)",
        height=500,
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True, key=f"solubility_chart_{peptide_index}")
    
    # Display reference peptide information
    if selected_references:
        st.subheader("📋 Reference Peptide Information")
        ref_cols = st.columns(len(selected_references))
        for i, ref_key in enumerate(selected_references):
            if ref_key in REFERENCE_PEPTIDES:
                ref_info = REFERENCE_PEPTIDES[ref_key]
                with ref_cols[i]:
                    st.markdown(f"""
                    **{ref_key}**
                    - **Category:** {ref_info['category']}
                    - **Use:** {ref_info['typical_use']}
                    - **Description:** {ref_info['description']}
                    """)
    
    # Display solubility table
    st.subheader("📊 Detailed Solubility Data")
    solubility_df = pd.DataFrame(solubility_data)
    solubility_df["Peptide"] = peptide['sequence']
    
    # Add reference data to table if selected
    if selected_references:
        for ref_key in selected_references:
            if ref_key in REFERENCE_PEPTIDES:
                ref_data = solubility_predictor.get_reference_solubility_data(ref_key)
                if ref_data:
                    ref_df = pd.DataFrame(ref_data["solubility_data"])
                    ref_df["Peptide"] = ref_key
                    solubility_df = pd.concat([solubility_df, ref_df], ignore_index=True)
    
    st.dataframe(solubility_df, use_container_width=True, key=f"solubility_table_{peptide_index}")
    
    # Interaction potential
    st.subheader("⚡ Interaction Potential")
    interactions = analysis_result['analysis']['interaction_potential']
    
    # Create interaction type chart
    interaction_types = interactions['interaction_types']
    fig = go.Figure(data=[
        go.Bar(x=list(interaction_types.keys()), y=list(interaction_types.values()), 
               marker_color='#6366f1')
    ])
    fig.update_layout(
        title="Interaction Type Distribution",
        xaxis_title="Interaction Type",
        yaxis_title="Count",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True, key=f"interaction_chart_{peptide_index}")
    
    # Summary and recommendations with ExPASy integration
    st.subheader("📊 Analysis Summary")
    summary = analysis_result['summary']
    
    # Enhanced summary with ExPASy stability assessment
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Overall Score", f"{summary['overall_score']:.3f}")
        
        # Include ExPASy stability assessment if available
        if expasy_data:
            stability = expasy_data['stability_analysis']
            st.metric("ExPASy Stability Score", f"{stability['stability_score']:.3f}")
            st.metric("ExPASy Risk Level", stability['risk_level'])
        
        if summary['key_strengths']:
            st.write("**Key Strengths:**")
            for strength in summary['key_strengths']:
                st.write(f"✅ {strength}")
    
    with col2:
        if summary['key_concerns']:
            st.write("**Key Concerns:**")
            for concern in summary['key_concerns']:
                st.write(f"⚠️ {concern}")
        
        # Add ExPASy-specific concerns if available
        if expasy_data:
            stability = expasy_data['stability_analysis']
            if stability['risk_level'] in ['High', 'Medium']:
                st.write(f"⚠️ **ExPASy Stability Risk:** {stability['risk_level']} risk level")
                if stability['stability_factors']['hydrophobicity'] == 'High':
                    st.write("⚠️ **High Hydrophobicity:** May affect solubility")
                if stability['stability_factors']['charge_stability'] == 'Unstable':
                    st.write("⚠️ **Charge Instability:** May affect binding")
    
    # Enhanced recommendations incorporating ExPASy data
    st.subheader("💡 Recommendations")
    
    # Base recommendations
    if summary['recommendations']:
        for rec in summary['recommendations']:
            st.write(f"• {rec}")
    
    # ExPASy-specific recommendations
    if expasy_data:
        st.write("**🌐 ExPASy Stability Recommendations:**")
        if expasy_data['recommendations']:
            for rec in expasy_data['recommendations']:
                st.write(f"• {rec}")
        
        # Additional stability insights
        stability = expasy_data['stability_analysis']
        if stability['risk_level'] == 'Low':
            st.write("• ✅ **Excellent stability profile** - suitable for experimental validation")
        elif stability['risk_level'] == 'Medium':
            st.write("• ⚠️ **Moderate stability** - consider optimization before experimental testing")
        else:
            st.write("• ❌ **High stability risk** - significant optimization required")
        
        # Instability index insights
        instability_index = expasy_data['basic_properties']['instability_index']
        if instability_index > 40:
            st.write("• ⚠️ **High instability index** - consider sequence modifications")
        elif instability_index > 30:
            st.write("• ⚠️ **Moderate instability** - monitor during experiments")
        else:
            st.write("• ✅ **Low instability index** - good stability characteristics")


def main():
    inject_enhanced_css()
    
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.title("🧬 AI-Enhanced Peptide Generator Pro")
        st.markdown("Advanced computational biology platform for AI-driven peptide design and analysis.")
        
        # Sidebar with enhanced options
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # LLM Configuration
            st.subheader("🤖 AI Configuration")
            provider_name = st.selectbox("LLM Provider", ["OpenAI", "Anthropic", "Groq", "Mistral"], 
                                       help="Select the AI provider for peptide generation")
            api_key = st.text_input("API Key", type="password", help="Enter your API key for the selected provider")
            model_options = {
                "OpenAI": ["gpt-4", "gpt-3.5-turbo"], 
                "Anthropic": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"], 
                "Groq": ["llama3-8b-8192", "llama3-70b-8192"], 
                "Mistral": ["mistral-large-latest", "mistral-medium-latest"]
            }
            model_name = st.selectbox("Model", model_options.get(provider_name, []), 
                                    help="Select the specific model to use")
            
            # Analysis Settings
            st.subheader("🔬 Analysis Settings")
            chain_id = st.text_input("Chain ID", value="A", help="Enter the chain ID to analyze (default: A)")
            num_peptides = st.slider("Number of Peptides", min_value=1, max_value=10, value=3, 
                                   help="Number of peptide candidates to generate")
            
            # Enhanced analysis options
            st.subheader("📊 Advanced Analysis")
            enable_surface_analysis = st.checkbox("Surface Analysis", value=True, 
                                               help="Calculate solvent-accessible surface area for residues")
            # enable_interaction_analysis = st.checkbox("Interaction Analysis", value=True, 
            #                                        help="Analyze potential interaction sites and binding pockets")
            # Interaction analysis disabled for simplified visualization
            enable_advanced_analysis = st.checkbox("Advanced Peptide Analysis", value=True, 
                                                help="Perform comprehensive peptide property analysis")
            enable_comparative_analysis = st.checkbox("Comparative Analysis", value=True, 
                                                   help="Compare multiple peptides side-by-side")
            
            # Visualization options
            st.subheader("🎨 Visualization")
            # show_interaction_sites = st.checkbox("Show Interaction Sites", value=True, 
            #                                   help="Highlight interaction sites in 3D visualization")
            # show_binding_pockets = st.checkbox("Show Binding Pockets", value=True, 
            #                                 help="Show binding pockets in 3D visualization")
            # Interaction visualization disabled for simplified 3D viewer
            
            st.markdown("---")
            
            # Help and documentation
            with st.expander("📚 Help & Documentation"):
                st.markdown("""
                ### Getting Started
                1. **Upload PDB File**: Choose a protein structure file
                2. **Configure AI**: Select provider and enter API key
                3. **Analyze**: Review protein structure and surface analysis
                4. **Generate**: Create AI-suggested peptide candidates
                5. **Analyze**: Perform comprehensive peptide analysis
                
                ### Advanced Features
                - **Surface Analysis**: Identifies surface-exposed residues
                - **Interaction Analysis**: Finds potential binding sites
                - **Advanced Analysis**: Comprehensive peptide property analysis
                - **Comparative Analysis**: Side-by-side peptide comparison
                """)
            
            with st.expander("🔑 API Keys"):
                st.markdown("""
                - **OpenAI**: [platform.openai.com](https://platform.openai.com/api-keys)
                - **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
                - **Groq**: [console.groq.com](https://console.groq.com/)
                - **Mistral**: [console.mistral.ai](https://console.mistral.ai/)
                """)
        
        # Main content with tabs
        st.header("📁 Upload Protein Structure")
        st.markdown("""
        <div class="upload-area">
            <div class="upload-text">Choose a PDB file to begin advanced analysis</div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose a PDB file", type=['pdb'], 
                                       help="Upload a PDB file to analyze")
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
            pdb_content = uploaded_file.read().decode('utf-8')
            
            # Create tabs for different analysis sections
            tab1, tab2, tab3, tab4 = st.tabs([
                "🔬 Basic Analysis", 
                "🧬 Peptide Generation", 
                "📊 Advanced Analysis", 
                "🎨 3D Visualization"
            ])
            
            with tab1:
                st.header("🔬 Basic Protein Analysis")
                with st.spinner("Analyzing protein structure..."):
                    try:
                        parser = PDBParser()
                        parsed_result = parser.parse_structure(pdb_content, chain_id)
                        
                        if parsed_result['success']:
                            st.success("✅ Protein structure parsed successfully!")
                            
                            # Display basic metrics
                            st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
                            kpi_cols = st.columns(4)
                            with kpi_cols[0]: 
                                kpi_tile(parsed_result['chain_id'], "Chain ID")
                            with kpi_cols[1]: 
                                kpi_tile(len(parsed_result['sequence']), "Sequence Length")
                            with kpi_cols[2]: 
                                kpi_tile(len(parsed_result['residues']), "Total Residues")
                            with kpi_cols[3]: 
                                kpi_tile(f"{len(parsed_result['sequence'])/3:.1f}", "Avg Residue Size (aa)")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Protein sequence
                            st.subheader("🧬 Protein Sequence")
                            st.markdown(f"<div class='sequence-display'>{parsed_result['sequence']}</div>", 
                                      unsafe_allow_html=True)
                            
                            # Store parsed data
                            st.session_state['parsed_data'] = parsed_result
                            
                        else:
                            st.error(f"❌ Error parsing structure: {parsed_result['error']}")
                            return
                            
                    except Exception as e:
                        st.error(f"❌ Error during parsing: {str(e)}")
                        return
                
                # Surface analysis
                if enable_surface_analysis:
                    st.header("🌊 Surface Analysis")
                    with st.spinner("Analyzing surface properties..."):
                        try:
                            analyzer = SurfaceAnalyzer()
                            surface_result = analyzer.analyze_surface(pdb_content, chain_id)
                            
                            if surface_result['success']:
                                st.success("✅ Surface analysis completed!")
                                summary = surface_result['summary']
                                
                                # Display surface metrics
                                st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
                                kpi_cols = st.columns(4)
                                with kpi_cols[0]: 
                                    kpi_tile(summary['total_residues'], "Total Residues")
                                with kpi_cols[1]: 
                                    kpi_tile(summary['surface_residues'], "Surface Residues")
                                with kpi_cols[2]: 
                                    kpi_tile(summary['hydrophobic_count'], "Hydrophobic")
                                with kpi_cols[3]: 
                                    kpi_tile(summary['charged_count'], "Charged")
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Additional metrics
                                col1, col2 = st.columns(2)
                                with col1:
                                    kpi_tile(summary['polar_count'], "Polar/Other")
                                with col2:
                                    kpi_tile(f"{summary['avg_sasa']:.2f} Å²", "Avg SASA")
                                
                                # Store surface data
                                st.session_state['surface_data'] = surface_result
                                
                            else:
                                st.warning(f"⚠️ Surface analysis failed: {surface_result['error']}")
                                
                        except Exception as e:
                            st.warning(f"⚠️ Surface analysis error: {str(e)}")
            
            with tab2:
                st.header("🧬 AI Peptide Generation")
                if api_key:
                    st.markdown("**Click the button below to generate AI-suggested peptide candidates:**")
                    if st.button("🚀 GENERATE PEPTIDE CANDIDATES", use_container_width=True):
                        with st.spinner("Generating peptide candidates..."):
                            try:
                                llm_factory = LLMProviderFactory()
                                llm_provider = llm_factory.create_provider(provider_name, api_key, model_name)
                                generator = PeptideGenerator(llm_provider)
                                
                                context_data = {
                                    'sequence': st.session_state['parsed_data']['sequence'],
                                    'residues': st.session_state['parsed_data']['residues'],
                                    'chain_id': chain_id,
                                    'num_peptides': num_peptides
                                }
                                
                                # Add surface data if available
                                if 'surface_data' in st.session_state:
                                    context_data['surface_data'] = st.session_state['surface_data']
                                
                                # Interaction data removed for simplified visualization
                                
                                peptides_result = generator.generate_peptides(context_data)
                                
                                if peptides_result['success']:
                                    st.success(f"✅ Generated {len(peptides_result['peptides'])} peptide candidates!")
                                    st.session_state['peptides'] = peptides_result['peptides']
                                    
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
                                    
                                else:
                                    st.error(f"❌ Peptide generation failed: {peptides_result['error']}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error during peptide generation: {str(e)}")
                else:
                    st.info("ℹ️ Please enter your API key in the sidebar to generate peptides.")
            
            with tab3:
                st.header("📊 Advanced Peptide Analysis")
                if 'peptides' in st.session_state and enable_advanced_analysis:
                    st.subheader("🔬 Comprehensive Analysis Results")
                    
                    # Initialize ExPASy integration
                    expasy_integration = ExPASyIntegration()
                    
                    # Add ExPASy stability analysis option
                    st.subheader("🛡️ ExPASy Stability Analysis")
                    enable_expasy_analysis = st.checkbox(
                        "Enable ExPASy ProtParam Analysis", 
                        value=True,
                        help="Use ExPASy ProtParam for advanced stability prediction"
                    )
                    
                    if enable_expasy_analysis:
                        st.info("🌐 **ExPASy Integration**: Using ExPASy ProtParam for stability assessment (instability index, risk levels) and local calculations for basic properties (molecular weight, GRAVY score, pI).")
                    
                    # Analyze each peptide
                    peptide_analyzer = AdvancedPeptideAnalyzer()
                    
                    for i, peptide in enumerate(st.session_state['peptides'], 1):
                        with st.expander(f"Peptide {i}: {peptide['sequence']}", expanded=(i==1)):
                            with st.spinner(f"Analyzing peptide {i}..."):
                                # Basic analysis
                                analysis_result = peptide_analyzer.comprehensive_analysis(peptide['sequence'])
                                
                                if analysis_result['success']:
                                    # ExPASy stability analysis (if enabled)
                                    expasy_data = None
                                    if enable_expasy_analysis:
                                        with st.spinner("Analyzing with ExPASy ProtParam..."):
                                            expasy_result = expasy_integration.analyze_peptide_stability(peptide['sequence'])
                                            
                                            if expasy_result['success']:
                                                expasy_data = expasy_result['data']
                                                st.success("✅ ExPASy analysis completed!")
                                                
                                                # Display ExPASy results
                                                st.subheader("🌐 ExPASy ProtParam Stability Analysis")
                                                
                                                # Basic properties (local calculations)
                                                col1, col2, col3, col4 = st.columns(4)
                                                with col1:
                                                    st.metric("Molecular Weight (Local)", f"{expasy_data['basic_properties']['molecular_weight']:.1f} Da")
                                                with col2:
                                                    st.metric("Isoelectric Point (Local)", f"{expasy_data['basic_properties']['isoelectric_point']:.2f}")
                                                with col3:
                                                    st.metric("GRAVY Score (Local)", f"{expasy_data['basic_properties']['gravy_score']:.3f}")
                                                with col4:
                                                    st.metric("Instability Index (ExPASy)", f"{expasy_data['basic_properties']['instability_index']:.1f}")
                                                
                                                # Stability analysis (ExPASy-based)
                                                stability = expasy_data['stability_analysis']
                                                st.subheader("🛡️ ExPASy Stability Assessment")
                                                
                                                col1, col2, col3 = st.columns(3)
                                                with col1:
                                                    st.metric("Stability Score", f"{stability['stability_score']:.3f}")
                                                with col2:
                                                    st.metric("Risk Level", stability['risk_level'])
                                                with col3:
                                                    st.metric("Aliphatic Index (ExPASy)", f"{expasy_data['basic_properties']['aliphatic_index']:.1f}")
                                                
                                                # Stability factors
                                                st.subheader("📊 Stability Factors")
                                                factors = stability['stability_factors']
                                                col1, col2, col3, col4 = st.columns(4)
                                                with col1:
                                                    st.metric("Hydrophobicity", factors['hydrophobicity'])
                                                with col2:
                                                    st.metric("Charge Stability", factors['charge_stability'])
                                                with col3:
                                                    st.metric("Size Stability", factors['size_stability'])
                                                with col4:
                                                    st.metric("Composition", factors['composition_stability'])
                                                
                                                # Amino acid composition
                                                if expasy_data['amino_acid_composition']:
                                                    st.subheader("🧬 Amino Acid Composition (ExPASy)")
                                                    composition_df = pd.DataFrame([
                                                        {
                                                            'Amino Acid': aa,
                                                            'Count': data['count'],
                                                            'Percentage': f"{data['percentage']:.1f}%"
                                                        }
                                                        for aa, data in expasy_data['amino_acid_composition'].items()
                                                    ])
                                                    st.dataframe(composition_df, use_container_width=True)
                                                
                                            else:
                                                st.warning(f"⚠️ ExPASy analysis failed: {expasy_result['error']}")
                                                st.info("💡 This may be due to network issues or service availability. The analysis will continue with local calculations.")
                                    
                                    # Display comprehensive analysis with ExPASy integration
                                    display_peptide_analysis(peptide, analysis_result, i, expasy_data)
                                else:
                                    st.error(f"❌ Analysis failed: {analysis_result['error']}")
                    
                    # Comparative analysis with ExPASy
                    if enable_comparative_analysis and len(st.session_state['peptides']) > 1:
                        st.subheader("📈 Comparative Analysis")
                        
                        # Create comparison chart
                        comparison_data = []
                        expasy_comparison_data = []
                        
                        for i, peptide in enumerate(st.session_state['peptides'], 1):
                            analysis_result = peptide_analyzer.comprehensive_analysis(peptide['sequence'])
                            if analysis_result['success']:
                                comparison_data.append({
                                    'Peptide': f"Peptide {i}",
                                    'Sequence': peptide['sequence'],
                                    'Binding Score': analysis_result['analysis']['binding_affinity']['binding_score'],
                                    'Overall Score': analysis_result['summary']['overall_score'],
                                    'Immunogenicity Risk': analysis_result['analysis']['immunogenicity']['risk_level']
                                })
                                
                                # Add ExPASy data if available
                                if enable_expasy_analysis:
                                    expasy_result = expasy_integration.analyze_peptide_stability(peptide['sequence'])
                                    if expasy_result['success']:
                                        expasy_data = expasy_result['data']
                                        expasy_comparison_data.append({
                                            'Peptide': f"Peptide {i}",
                                            'Sequence': peptide['sequence'],
                                            'ExPASy Stability Score': expasy_data['stability_analysis']['stability_score'],
                                            'ExPASy Risk Level': expasy_data['stability_analysis']['risk_level'],
                                            'Instability Index (ExPASy)': expasy_data['basic_properties']['instability_index'],
                                            'GRAVY Score (Local)': expasy_data['basic_properties']['gravy_score']
                                        })
                        
                        if comparison_data:
                            df = pd.DataFrame(comparison_data)
                            
                            # Create comparison chart
                            fig = make_subplots(
                                rows=2, cols=2,
                                subplot_titles=('Binding Scores', 'Overall Scores', 'Immunogenicity Risk', 'Risk Levels'),
                                specs=[[{"type": "bar"}, {"type": "bar"}],
                                   [{"type": "bar"}, {"type": "scatter"}]]
                            )
                            
                            # Binding scores
                            fig.add_trace(
                                go.Bar(x=df['Peptide'], y=df['Binding Score'], name='Binding Score'),
                                row=1, col=1
                            )
                            
                            # Overall scores
                            fig.add_trace(
                                go.Bar(x=df['Peptide'], y=df['Overall Score'], name='Overall Score'),
                                row=1, col=2
                            )
                            
                            # Immunogenicity risk
                            fig.add_trace(
                                go.Bar(x=df['Peptide'], y=df['Immunogenicity Risk'].map({'Low': 1, 'Medium': 2, 'High': 3}), name='Immunogenicity Risk'),
                                row=2, col=1
                            )
                            
                            fig.update_layout(height=600, title_text="Peptide Comparison Analysis")
                            st.plotly_chart(fig, use_container_width=True, key="comparison_chart")
                            
                            # Display comparison table
                            st.subheader("📋 Comparison Summary")
                            st.dataframe(df, use_container_width=True)
                            
                            # ExPASy comparison if available
                            if expasy_comparison_data:
                                st.subheader("🌐 ExPASy Comparison Summary")
                                expasy_df = pd.DataFrame(expasy_comparison_data)
                                st.dataframe(expasy_df, use_container_width=True)
                                
                                # ExPASy comparison chart
                                fig_expasy = make_subplots(
                                    rows=2, cols=2,
                                    subplot_titles=('ExPASy Stability Scores', 'Instability Indices', 'GRAVY Scores', 'Risk Levels'),
                                    specs=[[{"type": "bar"}, {"type": "bar"}],
                                       [{"type": "bar"}, {"type": "scatter"}]]
                                )
                                
                                # ExPASy stability scores
                                fig_expasy.add_trace(
                                    go.Bar(x=expasy_df['Peptide'], y=expasy_df['ExPASy Stability Score'], name='ExPASy Stability'),
                                    row=1, col=1
                                )
                                
                                # Instability indices
                                fig_expasy.add_trace(
                                    go.Bar(x=expasy_df['Peptide'], y=expasy_df['Instability Index'], name='Instability Index'),
                                    row=1, col=2
                                )
                                
                                # GRAVY scores
                                fig_expasy.add_trace(
                                    go.Bar(x=expasy_df['Peptide'], y=expasy_df['GRAVY Score'], name='GRAVY Score'),
                                    row=2, col=1
                                )
                                
                                fig_expasy.update_layout(height=600, title_text="ExPASy Stability Comparison")
                                st.plotly_chart(fig_expasy, use_container_width=True, key="expasy_comparison_chart")
                                
                                # Enhanced comparison summary with ExPASy insights
                                st.subheader("🌐 ExPASy Stability Assessment Summary")
                                
                                if expasy_comparison_data:
                                    # Find best and worst performers based on ExPASy data
                                    expasy_df = pd.DataFrame(expasy_comparison_data)
                                    best_stability = expasy_df.loc[expasy_df['ExPASy Stability Score'].idxmax()]
                                    worst_stability = expasy_df.loc[expasy_df['ExPASy Stability Score'].idxmin()]
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.info(f"**🏆 Best Stability:** {best_stability['Peptide']} ({best_stability['Sequence']})")
                                        st.write(f"• Stability Score: {best_stability['ExPASy Stability Score']:.3f}")
                                        st.write(f"• Risk Level: {best_stability['ExPASy Risk Level']}")
                                        st.write(f"• Instability Index: {best_stability['Instability Index']:.1f}")
                                    
                                    with col2:
                                        st.warning(f"**⚠️ Lowest Stability:** {worst_stability['Peptide']} ({worst_stability['Sequence']})")
                                        st.write(f"• Stability Score: {worst_stability['ExPASy Stability Score']:.3f}")
                                        st.write(f"• Risk Level: {worst_stability['ExPASy Risk Level']}")
                                        st.write(f"• Instability Index: {worst_stability['Instability Index']:.1f}")
                                    
                                    # Overall recommendations
                                    st.subheader("💡 ExPASy-Based Recommendations")
                                    avg_stability = expasy_df['ExPASy Stability Score'].mean()
                                    high_risk_count = len(expasy_df[expasy_df['ExPASy Risk Level'] == 'High'])
                                    
                                    if avg_stability > 0.7:
                                        st.success("✅ **Overall excellent stability profile** - All peptides show good stability characteristics")
                                    elif avg_stability > 0.5:
                                        st.info("⚠️ **Moderate stability profile** - Consider optimization for lower-performing peptides")
                                    else:
                                        st.error("❌ **Poor stability profile** - Significant optimization required for all peptides")
                                    
                                    if high_risk_count > 0:
                                        st.warning(f"⚠️ **{high_risk_count} peptide(s) with high stability risk** - Consider sequence modifications")
                                    else:
                                        st.success("✅ **No high-risk peptides** - All peptides have acceptable stability profiles")
                else:
                    st.info("ℹ️ Generate peptides and enable advanced analysis to see comprehensive results.")
            
            with tab4:
                st.header("🎨 Enhanced 3D Visualization")
                st.markdown("""
                <div class="viewer-instructions">
                    <strong>💡 Interactive 3D Viewer:</strong> Simple protein structure visualization:
                    <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem;">
                        <li><strong>Rotate:</strong> Click and drag to rotate the molecule</li>
                        <li><strong>Zoom:</strong> Scroll to zoom in/out</li>
                        <li><strong>Pan:</strong> Right-click and drag to move the view</li>
                        <li><strong>Reset:</strong> Double-click to reset the view</li>
                        <li><strong>Colors:</strong> Protein chains are color-coded for easy identification</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                try:
                    visualizer = EnhancedVisualizer()
                    visualizer.display_enhanced_structure(pdb_content, chain_id)
                except Exception as e:
                    st.error(f"❌ Visualization error: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
