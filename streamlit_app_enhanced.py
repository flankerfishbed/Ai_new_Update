import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import our enhanced modular pipeline components
from modules.pdb_parser import PDBParser
from modules.surface_analyzer import SurfaceAnalyzer
from modules.peptide_generator import PeptideGenerator
from modules.enhanced_visualizer import EnhancedVisualizer
from modules.llm_providers import LLMProviderFactory
from modules.solubility_predictor import SolubilityPredictor, SOLVENTS
from modules.peptide_analyzer import AdvancedPeptideAnalyzer
from modules.interaction_analyzer import InteractionAnalyzer
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

def display_peptide_analysis(peptide: Dict[str, Any], analysis_result: Dict[str, Any]):
    """Display comprehensive peptide analysis."""
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
    
    # Secondary structure
    st.subheader("🧬 Secondary Structure Prediction")
    sec_struct = analysis_result['analysis']['secondary_structure']
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Alpha Helix", f"{sec_struct['helix_fraction']:.1%}")
    with col2:
        st.metric("Beta Sheet", f"{sec_struct['sheet_fraction']:.1%}")
    with col3:
        st.metric("Turns", f"{sec_struct['turn_fraction']:.1%}")
    
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
    
    # Stability analysis
    st.subheader("🛡️ Stability Analysis")
    stability = analysis_result['analysis']['stability']
    st.metric("Stability Score", f"{stability['stability_score']:.3f}")
    
    # Stability motifs
    motifs = stability['stability_motifs']
    st.write("**Stability Motifs:**")
    motif_cols = st.columns(4)
    with motif_cols[0]:
        st.metric("Disulfide Potential", "✓" if motifs['disulfide_potential'] else "✗")
    with motif_cols[1]:
        st.metric("Proline-Rich", "✓" if motifs['proline_rich'] else "✗")
    with motif_cols[2]:
        st.metric("Glycine-Rich", "✓" if motifs['glycine_rich'] else "✗")
    with motif_cols[3]:
        st.metric("Hydrophobic Clusters", "✓" if motifs['hydrophobic_clusters'] else "✗")
    
    # Immunogenicity
    st.subheader("🩸 Immunogenicity Assessment")
    immuno = analysis_result['analysis']['immunogenicity']
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Immunogenicity Score", f"{immuno['immunogenicity_score']:.3f}")
    with col2:
        risk_color = {"low": "green", "medium": "orange", "high": "red"}
        st.metric("Risk Level", immuno['risk_level'], delta_color=risk_color[immuno['risk_level']])
    with col3:
        st.metric("Charged Residues", immuno['charged_residues'])
    
    # Solubility profile
    st.subheader("💧 Solubility Profile")
    solubility = analysis_result['analysis']['solubility_profile']
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sol_color = {"high": "green", "medium": "orange", "low": "red"}
        st.metric("Solubility Level", solubility['solubility_level'], delta_color=sol_color[solubility['solubility_level']])
    with col2:
        st.metric("GRAVY Score", f"{solubility['gravy_score']:.3f}")
    with col3:
        st.metric("Net Charge", solubility['net_charge'])
    
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
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary and recommendations
    st.subheader("📊 Analysis Summary")
    summary = analysis_result['summary']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Overall Score", f"{summary['overall_score']:.3f}")
        
        if summary['key_strengths']:
            st.write("**Key Strengths:**")
            for strength in summary['key_strengths']:
                st.write(f"✅ {strength}")
    
    with col2:
        if summary['key_concerns']:
            st.write("**Key Concerns:**")
            for concern in summary['key_concerns']:
                st.write(f"⚠️ {concern}")
    
    if summary['recommendations']:
        st.subheader("💡 Recommendations")
        for rec in summary['recommendations']:
            st.write(f"• {rec}")

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
            enable_interaction_analysis = st.checkbox("Interaction Analysis", value=True, 
                                                   help="Analyze potential interaction sites and binding pockets")
            enable_advanced_analysis = st.checkbox("Advanced Peptide Analysis", value=True, 
                                                help="Perform comprehensive peptide property analysis")
            enable_comparative_analysis = st.checkbox("Comparative Analysis", value=True, 
                                                   help="Compare multiple peptides side-by-side")
            
            # Visualization options
            st.subheader("🎨 Visualization")
            show_interaction_sites = st.checkbox("Show Interaction Sites", value=True, 
                                              help="Highlight interaction sites in 3D visualization")
            show_binding_pockets = st.checkbox("Show Binding Pockets", value=True, 
                                            help="Show binding pockets in 3D visualization")
            
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
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🔬 Basic Analysis", 
                "🎯 Interaction Analysis", 
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
                                kpi_tile(f"{len(parsed_result['sequence'])/3:.1f}", "Avg Residue Size")
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
                st.header("🎯 Interaction Analysis")
                if enable_interaction_analysis:
                    with st.spinner("Analyzing interaction sites..."):
                        try:
                            interaction_analyzer = InteractionAnalyzer()
                            interaction_result = interaction_analyzer.analyze_interaction_sites(pdb_content, chain_id)
                            
                            if interaction_result['success']:
                                st.success("✅ Interaction analysis completed!")
                                summary = interaction_result['summary']
                                
                                # Display interaction metrics
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Interaction Sites", summary['total_interaction_sites'])
                                with col2:
                                    st.metric("High Affinity Sites", summary['high_affinity_sites'])
                                with col3:
                                    st.metric("Binding Pockets", summary['binding_pockets_found'])
                                
                                # Display recommendations
                                if summary['recommendations']:
                                    st.info("💡 **Interaction Analysis Recommendations:**")
                                    for rec in summary['recommendations']:
                                        st.write(f"• {rec}")
                                
                                # Store interaction data
                                st.session_state['interaction_data'] = interaction_result
                                
                            else:
                                st.warning(f"⚠️ Interaction analysis failed: {interaction_result['error']}")
                                
                        except Exception as e:
                            st.warning(f"⚠️ Interaction analysis error: {str(e)}")
                else:
                    st.info("ℹ️ Enable interaction analysis in the sidebar to analyze binding sites.")
            
            with tab3:
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
                                
                                # Add interaction data if available
                                if 'interaction_data' in st.session_state:
                                    context_data['interaction_data'] = st.session_state['interaction_data']
                                
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
            
            with tab4:
                st.header("📊 Advanced Peptide Analysis")
                if 'peptides' in st.session_state and enable_advanced_analysis:
                    st.subheader("🔬 Comprehensive Analysis Results")
                    
                    # Analyze each peptide
                    peptide_analyzer = AdvancedPeptideAnalyzer()
                    
                    for i, peptide in enumerate(st.session_state['peptides'], 1):
                        with st.expander(f"Peptide {i}: {peptide['sequence']}", expanded=(i==1)):
                            with st.spinner(f"Analyzing peptide {i}..."):
                                analysis_result = peptide_analyzer.comprehensive_analysis(peptide['sequence'])
                                
                                if analysis_result['success']:
                                    display_peptide_analysis(peptide, analysis_result)
                                else:
                                    st.error(f"❌ Analysis failed: {analysis_result['error']}")
                    
                    # Comparative analysis
                    if enable_comparative_analysis and len(st.session_state['peptides']) > 1:
                        st.subheader("📈 Comparative Analysis")
                        
                        # Create comparison chart
                        comparison_data = []
                        for i, peptide in enumerate(st.session_state['peptides'], 1):
                            analysis_result = peptide_analyzer.comprehensive_analysis(peptide['sequence'])
                            if analysis_result['success']:
                                comparison_data.append({
                                    'Peptide': f"Peptide {i}",
                                    'Sequence': peptide['sequence'],
                                    'Binding Score': analysis_result['analysis']['binding_affinity']['binding_score'],
                                    'Stability Score': analysis_result['analysis']['stability']['stability_score'],
                                    'Overall Score': analysis_result['summary']['overall_score'],
                                    'Immunogenicity Risk': analysis_result['analysis']['immunogenicity']['risk_level']
                                })
                        
                        if comparison_data:
                            df = pd.DataFrame(comparison_data)
                            
                            # Create comparison chart
                            fig = make_subplots(
                                rows=2, cols=2,
                                subplot_titles=('Binding Scores', 'Stability Scores', 'Overall Scores', 'Risk Levels'),
                                specs=[[{"type": "bar"}, {"type": "bar"}],
                                   [{"type": "bar"}, {"type": "scatter"}]]
                            )
                            
                            # Binding scores
                            fig.add_trace(
                                go.Bar(x=df['Peptide'], y=df['Binding Score'], name='Binding Score'),
                                row=1, col=1
                            )
                            
                            # Stability scores
                            fig.add_trace(
                                go.Bar(x=df['Peptide'], y=df['Stability Score'], name='Stability Score'),
                                row=1, col=2
                            )
                            
                            # Overall scores
                            fig.add_trace(
                                go.Bar(x=df['Peptide'], y=df['Overall Score'], name='Overall Score'),
                                row=2, col=1
                            )
                            
                            fig.update_layout(height=600, title_text="Peptide Comparison Analysis")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Display comparison table
                            st.subheader("📋 Comparison Summary")
                            st.dataframe(df, use_container_width=True)
                else:
                    st.info("ℹ️ Generate peptides and enable advanced analysis to see comprehensive results.")
            
            with tab5:
                st.header("🎨 Enhanced 3D Visualization")
                st.markdown("""
                <div class="viewer-instructions">
                    <strong>💡 Interactive 3D Viewer:</strong> Advanced visualization with interaction analysis:
                    <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem;">
                        <li><strong>Rotate:</strong> Click and drag to rotate the molecule</li>
                        <li><strong>Zoom:</strong> Scroll to zoom in/out</li>
                        <li><strong>Pan:</strong> Right-click and drag to move the view</li>
                        <li><strong>Reset:</strong> Double-click to reset the view</li>
                        <li><strong>Highlights:</strong> Interaction sites and binding pockets are highlighted</li>
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