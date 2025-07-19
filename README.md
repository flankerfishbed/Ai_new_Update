# AI-Enhanced Peptide Generator

A web-based application that allows users to upload protein structure files (PDB), analyze surface-exposed residues, and generate AI-suggested peptide candidates with detailed, explainable reasoning.

## Features

### 🔍 **Protein Structure Analysis**
- Upload PDB files and parse protein sequences
- Extract residue information and 3D coordinates
- Support for chain selection and validation

### 🌊 **Surface Analysis**
- Calculate solvent-accessible surface area (SASA) using FreeSASA
- Classify residues as hydrophobic, charged, or polar
- Identify surface-exposed residues for peptide targeting

### 🤖 **AI-Powered Peptide Generation**
- Support for multiple LLM providers (OpenAI, Anthropic, Groq, Mistral)
- Generate peptide candidates (8-15 amino acids) optimized for surface interaction
- Detailed reasoning for each peptide suggestion
- Context-aware design based on surface analysis

### 🎯 **3D Visualization**
- Interactive 3D protein structure visualization
- Surface residue highlighting
- Multiple visualization styles and color schemes

### 📊 **Explainability & Context Engineering**
- Every pipeline step produces clean, explainable output
- Each output is suitable for direct use as LLM prompt context
- Transparent reasoning for peptide selection

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd ai-peptide-generator
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage

### 1. **Upload Protein Structure**
- Click "Browse files" to upload a PDB file
- Select the chain ID to analyze (default: "A")
- The system will parse the structure and display sequence information

### 2. **Configure AI Settings**
- Select an LLM provider (OpenAI, Anthropic, Groq, Mistral)
- Enter your API key
- Choose a model and number of peptides to generate

### 3. **Surface Analysis (Optional)**
- Enable surface analysis to calculate SASA values
- View residue classification and surface exposure metrics
- Identify potential binding sites

### 4. **Generate Peptides**
- Click "Generate Peptide Candidates"
- Review AI-suggested peptides with detailed reasoning
- Each peptide includes properties and explanation

### 5. **3D Visualization**
- Interact with the protein structure in 3D
- Rotate, zoom, and pan to explore the structure
- View surface residues highlighted by type

## API Key Setup

### OpenAI
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account and generate an API key
3. Use the key in the application

### Anthropic
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account and generate an API key
3. Use the key in the application

### Groq
1. Visit [Groq Console](https://console.groq.com/)
2. Create an account and generate an API key
3. Use the key in the application

### Mistral
1. Visit [Mistral AI](https://console.mistral.ai/)
2. Create an account and generate an API key
3. Use the key in the application

## Deployment on Streamlit Cloud

### 1. **Prepare for Deployment**
- Ensure all dependencies are in `requirements.txt`
- Test locally before deployment

### 2. **Deploy to Streamlit Cloud**
1. Push your code to GitHub
2. Visit [Streamlit Cloud](https://share.streamlit.io/)
3. Connect your GitHub repository
4. Deploy the application

### 3. **Environment Variables**
For production deployment, consider using environment variables for API keys:
```bash
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

## Architecture

### Modular Design
The application follows a modular, extensible architecture:

```
modules/
├── pdb_parser.py          # PDB file parsing
├── surface_analyzer.py    # Surface analysis with FreeSASA
├── peptide_generator.py   # AI peptide generation
├── visualizer.py          # 3D visualization
└── llm_providers.py      # LLM provider factory
```

### Pipeline Flow
1. **PDB Parsing** → Extract sequence and residue data
2. **Surface Analysis** → Calculate SASA and classify residues
3. **AI Generation** → Generate peptides with reasoning
4. **Visualization** → Display 3D structure

### Context Engineering
Each step produces structured output suitable for LLM prompts:
- Clean, explainable data structures
- Human-readable explanations
- Modular, reusable components

## Example Output

### Peptide Suggestion
```json
{
  "sequence": "ACDEFGHI",
  "properties": {
    "length": 8,
    "net_charge": 0,
    "hydrophobicity": "moderate",
    "motifs": ["hydrophobic core", "charged termini"]
  },
  "explanation": "This peptide targets the hydrophobic surface region around residues 42-45 (Leu, Ile, Val) with high SASA values. The central hydrophobic core (DEF) provides strong van der Waals interactions, while the charged termini (A, I) ensure solubility and provide additional electrostatic interactions with nearby charged surface residues."
}
```

## Contributing

### Adding New LLM Providers
1. Create a new provider class in `modules/llm_providers.py`
2. Implement the `LLMProvider` interface
3. Add to the `LLMProviderFactory`

### Adding New Analysis Modules
1. Create a new module in the `modules/` directory
2. Follow the clean, explainable output pattern
3. Integrate with the main application

### Code Style
- Follow PEP 8 guidelines
- Include comprehensive docstrings
- Ensure all functions return explainable output
- Add type hints for better code clarity

## Troubleshooting

### Common Issues

**FreeSASA Installation:**
```bash
# On Windows, you may need to install Visual Studio Build Tools
# On Linux/Mac, ensure you have a C compiler
pip install freesasa
```

**py3Dmol Issues:**
```bash
# If 3D visualization doesn't work, try:
pip install --upgrade py3dmol
```

**API Key Errors:**
- Ensure your API key is correct
- Check your account has sufficient credits
- Verify the model name is supported

### Debug Information
The application provides detailed error messages and debug information for troubleshooting. Check the console output for specific error details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Biopython** for PDB parsing
- **FreeSASA** for surface area calculations
- **py3Dmol** for 3D visualization
- **Streamlit** for the web interface
- Various LLM providers for AI capabilities

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review the code documentation
3. Open an issue on GitHub
4. Contact the development team

---

**Built with ❤️ for the computational biology community** 