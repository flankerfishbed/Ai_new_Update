# 🧬 AI-Enhanced Peptide Generator Pro

A comprehensive computational biology platform for AI-driven peptide design and analysis with advanced protein structure analysis capabilities.

## ✨ Features

### 🔬 Advanced Analysis
- **Secondary Structure Prediction**: Alpha-helix, beta-sheet, and turn content analysis
- **Binding Affinity Estimation**: Quantitative binding scores based on physicochemical properties
- **Stability Analysis**: Identifies stability motifs and predicts peptide stability
- **Immunogenicity Prediction**: Assesses potential immune response risks
- **Comprehensive Property Analysis**: Molecular weight, isoelectric point, GRAVY scores

### 🎯 Protein-Protein Interaction Analysis
- **Surface Residue Identification**: Automatic detection of surface-exposed residues
- **Interaction Site Detection**: Finds high-affinity binding sites on target proteins
- **Binding Pocket Discovery**: Identifies potential binding pockets for peptide targeting
- **Interaction Type Prediction**: Hydrogen bonding, ionic, hydrophobic, and aromatic interactions

### 🎨 Enhanced Visualization
- **Interactive 3D Visualization**: Advanced protein structure viewing with interaction highlighting
- **Binding Site Visualization**: Color-coded interaction sites and binding pockets
- **Comparative Analysis**: Side-by-side comparison of multiple peptides
- **Dynamic Coloring Schemes**: Different color schemes for chains, residue types, and interaction levels

### 🤖 AI-Powered Generation
- **Multi-Provider Support**: OpenAI, Anthropic, Groq, Mistral
- **Context-Aware Generation**: Uses protein structure and surface analysis data
- **Detailed Reasoning**: AI explains why each peptide was suggested
- **Modular Architecture**: Clean, extensible pipeline components

## 🚀 Quick Start

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd new-peptides
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the enhanced app**:
   ```bash
   streamlit run streamlit_app_enhanced.py
   ```

### Streamlit Cloud Deployment

1. **Push to GitHub**: Ensure your code is in a GitHub repository

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set the main file path to: `streamlit_app_enhanced.py`
   - Deploy!

3. **Environment Variables** (Optional):
   - Add your API keys as secrets in Streamlit Cloud
   - Or use the sidebar to input API keys manually

## 📊 Usage Guide

### 1. Upload Protein Structure
- Upload a PDB file containing your target protein
- The app will automatically parse and analyze the structure

### 2. Configure Analysis Settings
- **Chain ID**: Specify which protein chain to analyze (default: A)
- **Number of Peptides**: Choose how many candidates to generate (1-10)
- **Advanced Analysis**: Enable surface analysis, interaction analysis, etc.

### 3. Generate Peptides
- Enter your API key for the chosen LLM provider
- Click "Generate Peptide Candidates"
- Review AI-generated peptides with detailed reasoning

### 4. Advanced Analysis
- **Basic Analysis**: Protein structure and surface properties
- **Interaction Analysis**: Binding sites and pockets on target protein
- **Advanced Analysis**: Comprehensive peptide property analysis
- **3D Visualization**: Interactive structure viewer with highlights

### 5. Comparative Analysis
- Compare multiple peptides side-by-side
- View binding scores, stability, and risk assessments
- Export analysis results

## 🔧 Configuration

### API Keys
The app supports multiple LLM providers:
- **OpenAI**: [platform.openai.com](https://platform.openai.com/api-keys)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
- **Groq**: [console.groq.com](https://console.groq.com/)
- **Mistral**: [console.mistral.ai](https://console.mistral.ai/)

### Analysis Options
- **Surface Analysis**: Calculate solvent-accessible surface area
- **Interaction Analysis**: Find potential binding sites and pockets
- **Advanced Analysis**: Comprehensive peptide property analysis
- **Comparative Analysis**: Side-by-side peptide comparison

## 📁 Project Structure

```
new-peptides/
├── streamlit_app_enhanced.py    # Enhanced main app
├── streamlit_app.py             # Original app
├── requirements.txt             # Python dependencies
├── packages.txt                 # System dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── modules/
│   ├── pdb_parser.py          # Protein structure parsing
│   ├── surface_analyzer.py    # Surface analysis
│   ├── peptide_generator.py   # AI peptide generation
│   ├── enhanced_visualizer.py # Advanced 3D visualization
│   ├── peptide_analyzer.py    # Advanced peptide analysis
│   ├── interaction_analyzer.py # Protein-protein interaction analysis
│   ├── llm_providers.py       # LLM provider interface
│   ├── solubility_predictor.py # Solubility prediction
│   └── visualizer.py          # Basic visualization
└── sample_protein.pdb         # Sample protein structure
```

## 🔬 Scientific Background

### Peptide Analysis Methods
- **Secondary Structure**: Garnier-Gibrat-Robson algorithm
- **Binding Affinity**: Hydrophobicity, charge, and polarity scoring
- **Stability**: Disulfide potential, proline/glycine content, hydrophobic clusters
- **Immunogenicity**: Charged amino acid composition analysis
- **Solubility**: GRAVY score and net charge assessment

### Interaction Analysis
- **Surface Detection**: Solvent accessibility calculation
- **Binding Sites**: Interaction potential scoring
- **Pocket Detection**: Surface curvature analysis
- **Interaction Types**: Hydrogen bonding, ionic, hydrophobic, aromatic

## 🛠️ Development

### Adding New Analysis Types
1. Create a new module in `modules/`
2. Implement the analysis class with `success`/`error` return format
3. Import and integrate in `streamlit_app_enhanced.py`

### Adding New LLM Providers
1. Add provider to `modules/llm_providers.py`
2. Update the provider factory
3. Add to the sidebar options in the app

### Customizing Visualizations
1. Modify `modules/enhanced_visualizer.py`
2. Add new color schemes or visualization types
3. Update the viewer configuration

## 📈 Performance Optimization

### For Large Proteins
- Enable only necessary analysis types
- Use chain-specific analysis
- Consider protein size limits for cloud deployment

### For Multiple Peptides
- Batch analysis capabilities
- Comparative visualization
- Export functionality for further analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Biopython**: Protein structure analysis
- **py3Dmol**: 3D molecular visualization
- **Streamlit**: Web app framework
- **OpenAI/Anthropic/Groq/Mistral**: LLM providers

## 📞 Support

For issues and questions:
- Check the documentation above
- Review the code comments
- Open an issue on GitHub

---

**Made with ❤️ for computational biology and peptide therapeutics research** 