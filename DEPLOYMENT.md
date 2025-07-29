# 🚀 Streamlit Cloud Deployment Guide

This guide covers deploying the AI-Enhanced Peptide Generator Pro with PepINVENT integration on Streamlit Cloud.

## 📋 Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Python Dependencies**: All dependencies are in `requirements.txt`

## 🔧 Streamlit Cloud Configuration

### 1. Repository Setup

Ensure your repository structure looks like this:
```
your-repo/
├── streamlit_app_enhanced.py    # Main app file
├── requirements.txt              # Dependencies
├── modules/                     # Modular components
│   ├── __init__.py
│   ├── pdb_parser.py
│   ├── surface_analyzer.py
│   ├── peptide_generator.py
│   ├── llm_providers.py
│   ├── solubility_predictor.py
│   ├── peptide_analyzer.py
│   ├── expasy_integration.py
│   └── pepinvent_integration.py # NEW: PepINVENT integration
├── setup_pepinvent.py           # NEW: Setup script (local only)
├── test_pepinvent_integration.py # NEW: Test script
├── README.md
└── .gitignore
```

**Note**: `setup_pepinvent.py` is for local installation only. Streamlit Cloud uses cloud-compatible methods.

### 2. Streamlit Cloud Deployment

1. **Go to Streamlit Cloud**: [share.streamlit.io](https://share.streamlit.io)
2. **Connect GitHub**: Link your GitHub account
3. **Select Repository**: Choose your repository
4. **Configure App**:
   - **Main file path**: `streamlit_app_enhanced.py`
   - **Python version**: 3.9 or higher
   - **Advanced settings**: Use default (or customize if needed)

### 3. Environment Variables (Optional)

You can add these as secrets in Streamlit Cloud:

```toml
# In Streamlit Cloud → Settings → Secrets
[secrets]
OPENAI_API_KEY = "your-openai-key"
ANTHROPIC_API_KEY = "your-anthropic-key"
GROQ_API_KEY = "your-groq-key"
MISTRAL_API_KEY = "your-mistral-key"
```

## 🌐 PepINVENT Integration for Cloud

### Cloud Limitations

Streamlit Cloud has some limitations for PepINVENT:

1. **No Subprocess Execution**: Cannot run external commands
2. **No File System Access**: Cannot clone repositories or install packages
3. **Memory Limits**: Limited memory for large models
4. **No GPU Access**: CPU-only environment

### Cloud-Compatible PepINVENT

For Streamlit Cloud, we've implemented a **cloud-compatible version** that:

1. **Graceful Degradation**: Falls back to LLM-based generation if PepINVENT unavailable
2. **No External Dependencies**: Doesn't require subprocess execution
3. **Mock Implementation**: Provides realistic peptide generation for demonstration
4. **Clear User Feedback**: Informs users about cloud limitations

### Cloud Configuration

The app automatically detects cloud environment and adjusts:

```python
# Automatic cloud detection
if os.environ.get('STREAMLIT_SERVER_RUNNING'):
    # Cloud environment detected
    enable_pepinvent_cloud_mode = True
else:
    # Local environment
    enable_pepinvent_cloud_mode = False
```

## 🚀 Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Add PepINVENT integration with cloud compatibility"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**: [share.streamlit.io](https://share.streamlit.io)
2. **Connect GitHub**: Link your GitHub account
3. **Select Repository**: Choose your repository
4. **Configure App**:
   - **Main file path**: `streamlit_app_enhanced.py`
   - **Python version**: 3.9 or higher
   - **Advanced settings**: Use default

### 3. Test the Deployment

1. **Wait for deployment** (usually 2-5 minutes)
2. **Test PepINVENT**: Enable PepINVENT in the sidebar
3. **Upload a PDB file** and test peptide generation
4. **Verify cloud mode**: Should show "Cloud Mode Active" message

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all modules are in the `modules/` directory
2. **Dependency Issues**: Check `requirements.txt` includes all dependencies
3. **PepINVENT Not Working**: Cloud mode should work automatically
4. **API Key Issues**: Add keys as secrets in Streamlit Cloud settings

### Cloud-Specific Notes

- **No Subprocess**: PepINVENT uses cloud-compatible methods
- **Memory Limits**: Large proteins may be slower
- **No GPU**: All processing is CPU-based
- **Temporary Files**: All file operations are in-memory

## 📊 Performance Optimization

### For Cloud Deployment

1. **Limit Protein Size**: Large proteins (>1000 residues) may be slow
2. **Use Cloud Mode**: PepINVENT cloud mode is optimized for cloud
3. **Cache Results**: Use Streamlit caching for repeated operations
4. **Monitor Memory**: Large peptide sets may use significant memory

## 🔧 Configuration Files

### `.streamlit/config.toml`
```toml
[global]
developmentMode = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#6366f1"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
```

### `packages.txt`
```
python3-dev
build-essential
libffi-dev
libssl-dev
libxml2-dev
libxslt1-dev
libjpeg-dev
libpng-dev
libfreetype6-dev
libblas-dev
liblapack-dev
gfortran
```

### `requirements.txt`
```
streamlit>=1.28.0
biopython>=1.81,<2.0
freesasa>=2.2.0
pandas>=2.0.0
numpy>=1.24.0
py3Dmol>=2.0.0
openai>=1.0.0
anthropic>=0.7.0
requests>=2.31.0
plotly>=5.15.0
matplotlib>=3.0.0
scikit-learn>=1.3.0
scipy>=1.11.0
seaborn>=0.12.0
plotly-express>=0.4.1
```

## 🌐 ExPASy Integration Features

### Cloud-Optimized Stability Analysis
The app now includes **ExPASy ProtParam integration** for professional-grade peptide stability prediction:

#### Features
- **Real-time stability analysis** using ExPASy ProtParam service
- **Rate limiting** to respect service limits (2-second delays between requests)
- **Robust error handling** for cloud deployment reliability
- **Caching** to reduce redundant API calls
- **Comprehensive metrics** including:
  - Molecular weight calculation
  - Isoelectric point prediction
  - GRAVY (Grand Average of Hydropathy) scores
  - Instability index assessment
  - Aliphatic index calculation
  - Extinction coefficients

#### Stability Assessment
- **Stability scoring** (0-1 scale, higher is more stable)
- **Risk level assessment** (Low/Medium/High)
- **Multi-factor analysis**:
  - Hydrophobicity assessment
  - Charge stability evaluation
  - Size-based stability
  - Amino acid composition analysis

#### Recommendations Engine
The system provides **AI-powered recommendations** for stability improvement:
- Instability reduction strategies
- Hydrophobicity optimization
- Size-based modifications
- Disulfide bond considerations
- Composition-based suggestions

### Network Considerations
- **30-second timeout** for cloud reliability
- **Automatic fallback** to local calculations if ExPASy is unavailable
- **User-friendly error messages** for network issues
- **Progress indicators** for long-running analyses

### Usage in Streamlit Cloud
1. **Enable ExPASy Analysis** in the Advanced Analysis tab
2. **Upload protein structure** and generate peptides
3. **View comprehensive stability reports** with ExPASy data
4. **Compare multiple peptides** with professional metrics
5. **Export results** for further analysis

### Testing
Run the test script to verify ExPASy integration:
```bash
python test_expasy_cloud.py
```

This will test the integration with various peptide types and verify cloud compatibility.

## 🚨 Common Issues & Solutions

### 1. Build Failures

**Issue**: App fails to build on Streamlit Cloud
**Solutions**:
- Check that all dependencies are in `requirements.txt`
- Ensure `packages.txt` includes necessary system libraries
- Verify Python version compatibility

### 2. Import Errors

**Issue**: Module import errors
**Solutions**:
- Ensure all modules are in the `modules/` directory
- Check that `__init__.py` exists in the modules directory
- Verify import paths in the main app file

### 3. Memory Issues

**Issue**: App runs out of memory with large proteins
**Solutions**:
- Limit protein size in the app
- Disable heavy analysis features for large proteins
- Use chain-specific analysis instead of full protein

### 4. API Key Issues

**Issue**: API keys not working
**Solutions**:
- Verify API keys are correct
- Check account has sufficient credits
- Ensure model names are supported
- Try using secrets instead of sidebar input

### 5. 3D Visualization Issues

**Issue**: 3D viewer not displaying
**Solutions**:
- Check py3Dmol installation
- Verify JavaScript is enabled
- Try different visualization settings

## 🔍 Debugging

### Check Logs
1. Go to your app on Streamlit Cloud
2. Click the hamburger menu → "Settings"
3. Click "Logs" to see error messages

### Local Testing
Before deploying, test locally:
```bash
streamlit run streamlit_app_enhanced.py
```

### Common Error Messages

**"Module not found"**:
- Check all files are committed to GitHub
- Verify import statements

**"API key invalid"**:
- Check API key format
- Verify provider account status

**"Memory limit exceeded"**:
- Reduce protein size
- Disable heavy analysis features

## 📊 Performance Optimization

### For Large Proteins
- Use chain-specific analysis
- Disable unnecessary analysis types
- Limit peptide generation number

### For Multiple Users
- Implement caching for analysis results
- Use session state for temporary data
- Optimize visualization rendering

## 🔐 Security Considerations

### API Key Management
- Use Streamlit secrets for production
- Never commit API keys to GitHub
- Rotate keys regularly

### File Upload Limits
- Set reasonable file size limits
- Validate PDB file format
- Sanitize user inputs

## 📈 Monitoring

### App Health
- Monitor app response times
- Check error rates
- Track API usage

### Usage Analytics
- Monitor user engagement
- Track feature usage
- Analyze performance metrics

## 🆘 Getting Help

### Streamlit Cloud Support
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Community Forum](https://discuss.streamlit.io/)

### App-Specific Issues
- Check the logs in Streamlit Cloud
- Review the README.md for usage instructions
- Open an issue on GitHub

## 🎉 Success Checklist

- [ ] Repository is public or you have Streamlit Cloud Pro
- [ ] All dependencies are in `requirements.txt`
- [ ] System dependencies are in `packages.txt`
- [ ] Main file path is correct (`streamlit_app_enhanced.py`)
- [ ] API keys are configured (optional)
- [ ] App builds successfully
- [ ] All features work as expected
- [ ] 3D visualization displays correctly
- [ ] File upload works
- [ ] Analysis features function properly

## 🚀 Advanced Deployment

### Custom Domain
1. Go to app settings
2. Click "Custom domain"
3. Configure your domain

### Environment Variables
Set additional environment variables in Streamlit Cloud settings if needed.

### Scaling
For high-traffic apps, consider:
- Streamlit Cloud Pro for more resources
- Implementing caching strategies
- Optimizing analysis algorithms

---

**Your enhanced peptide generator is now ready for the world! 🌍** 