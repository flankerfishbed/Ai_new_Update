import streamlit as st

# Demo of improved UI components
st.set_page_config(
    page_title="UI Demo - AI Peptide Generator",
    page_icon="🧬",
    layout="wide"
)

# Custom CSS for demo
st.markdown("""
<style>
    .demo-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .demo-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    .metric-demo {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("""
    <div class="demo-header">
        <h1>🧬 AI-Enhanced Peptide Generator - UI Demo</h1>
        <p>Improved user interface with modern styling and better user experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 UI Improvements")
        
        st.markdown("""
        <div class="demo-card">
            <h4>✨ Enhanced Features</h4>
            <ul>
                <li>Gradient backgrounds and modern styling</li>
                <li>Better organized sidebar with sections</li>
                <li>Improved progress indicators</li>
                <li>Card-based layout for results</li>
                <li>Color-coded status messages</li>
                <li>Responsive design for different screen sizes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo metrics
        st.subheader("📊 Metric Cards")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-demo">
                <h4>Chain ID</h4>
                <h2>A</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-demo">
                <h4>Sequence Length</h4>
                <h2>150</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-demo">
                <h4>Total Residues</h4>
                <h2>150</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🚀 New Features")
        
        st.markdown("""
        <div class="demo-card">
            <h4>🎯 User Experience</h4>
            <ul>
                <li>Step-by-step progress tracking</li>
                <li>Clear error messages with suggestions</li>
                <li>Expandable sections for detailed data</li>
                <li>Interactive 3D visualization</li>
                <li>Real-time status updates</li>
                <li>Helpful tooltips and guidance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo peptide card
        st.subheader("🧬 Peptide Display")
        st.markdown("""
        <div class="demo-card">
            <h4>Peptide 1: ACDEFGHI</h4>
            <div style="display: flex; justify-content: space-between;">
                <div style="flex: 1;">
                    <h5>Properties:</h5>
                    <ul>
                        <li><strong>Length:</strong> 8</li>
                        <li><strong>Net Charge:</strong> 0</li>
                        <li><strong>Hydrophobicity:</strong> moderate</li>
                        <li><strong>Motifs:</strong> hydrophobic core</li>
                    </ul>
                </div>
                <div style="flex: 2; margin-left: 1rem;">
                    <h5>Reasoning:</h5>
                    <p>This peptide targets the hydrophobic surface region with high SASA values...</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Instructions
    st.markdown("---")
    st.subheader("📋 How to Use the Improved App")
    
    st.markdown("""
    1. **Replace `app.py`** with the improved version (`app_improved.py`)
    2. **Update the config** - The `.streamlit/config.toml` is already updated
    3. **Deploy to Streamlit Cloud** - The improved UI will be automatically applied
    4. **Test the features** - Upload a PDB file and see the enhanced interface
    """)
    
    st.success("✅ The improved UI provides a much better user experience with modern styling, better organization, and clearer visual feedback!")

if __name__ == "__main__":
    main() 