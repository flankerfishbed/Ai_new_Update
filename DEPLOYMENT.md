# Deployment Guide for Streamlit Cloud

This guide provides step-by-step instructions for deploying the AI-Enhanced Peptide Generator to Streamlit Cloud.

## Prerequisites

1. **GitHub Account**: You need a GitHub account to host your code
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io/)
3. **API Keys**: Get API keys from your chosen LLM providers

## Step 1: Prepare Your Repository

### 1.1 Create a GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it something like `ai-peptide-generator`
3. Make it public (required for free Streamlit Cloud deployment)

### 1.2 Upload Your Code

```bash
# Clone your repository locally
git clone https://github.com/yourusername/ai-peptide-generator.git
cd ai-peptide-generator

# Copy all the files from this project to your repository
# Make sure you have:
# - app.py
# - requirements.txt
# - modules/ (directory with all module files)
# - README.md
# - .streamlit/config.toml
# - sample_protein.pdb
# - test_installation.py

# Add all files to git
git add .

# Commit your changes
git commit -m "Initial commit: AI-Enhanced Peptide Generator"

# Push to GitHub
git push origin main
```

### 1.3 Verify Repository Structure

Your repository should have this structure:
```
ai-peptide-generator/
├── app.py
├── requirements.txt
├── README.md
├── DEPLOYMENT.md
├── test_installation.py
├── sample_protein.pdb
├── .streamlit/
│   └── config.toml
└── modules/
    ├── __init__.py
    ├── pdb_parser.py
    ├── surface_analyzer.py
    ├── peptide_generator.py
    ├── visualizer.py
    └── llm_providers.py
```

## Step 2: Deploy to Streamlit Cloud

### 2.1 Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"

### 2.2 Configure Your App

Fill in the deployment form:

- **Repository**: Select your GitHub repository
- **Branch**: `main` (or your default branch)
- **Main file path**: `app.py`
- **App URL**: Leave blank (Streamlit will generate one)

### 2.3 Advanced Settings (Optional)

Click "Advanced settings" to configure:

- **Python version**: 3.9 or higher
- **Environment variables**: Add your API keys (see Security section below)

### 2.4 Deploy

Click "Deploy" and wait for the build to complete (usually 2-5 minutes).

## Step 3: Security Configuration

### 3.1 Environment Variables (Recommended)

For production deployment, use environment variables for API keys:

1. In Streamlit Cloud, go to your app settings
2. Add these environment variables:
   ```
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GROQ_API_KEY=your_groq_key_here
   MISTRAL_API_KEY=your_mistral_key_here
   ```

### 3.2 Update App for Environment Variables

Modify `app.py` to use environment variables:

```python
import os

# In the sidebar section, update the API key input:
api_key = st.text_input(
    "API Key",
    type="password",
    value=os.getenv(f"{provider_name.upper()}_API_KEY", ""),
    help="Enter your API key for the selected provider"
)
```

## Step 4: Testing Your Deployment

### 4.1 Basic Functionality Test

1. Visit your deployed app URL
2. Upload the `sample_protein.pdb` file
3. Test the surface analysis feature
4. Verify 3D visualization works

### 4.2 API Integration Test

1. Enter a valid API key
2. Test peptide generation
3. Verify the AI responses are working

## Step 5: Troubleshooting

### Common Issues

#### Build Failures

**Error**: `ModuleNotFoundError: No module named 'freesasa'`
**Solution**: Ensure `freesasa` is in `requirements.txt`

**Error**: `ModuleNotFoundError: No module named 'modules'`
**Solution**: Check that all module files are in the `modules/` directory

#### Runtime Errors

**Error**: API key authentication failed
**Solution**: 
- Verify your API key is correct
- Check your account has sufficient credits
- Ensure the model name is supported

**Error**: PDB parsing failed
**Solution**:
- Check the PDB file format
- Verify the chain ID exists in the structure

### Debug Information

1. **Check Build Logs**: In Streamlit Cloud, go to your app settings and view build logs
2. **Test Locally**: Run `python test_installation.py` to verify dependencies
3. **Check Console**: Use browser developer tools to see JavaScript errors

## Step 6: Customization

### 6.1 Custom Styling

Modify `.streamlit/config.toml` to change the app appearance:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### 6.2 Add Custom Features

1. Create new modules in the `modules/` directory
2. Follow the clean, explainable output pattern
3. Integrate with the main application

### 6.3 Performance Optimization

For large proteins:
- Consider adding progress bars for long operations
- Implement caching for repeated calculations
- Add timeout handling for API calls

## Step 7: Monitoring and Maintenance

### 7.1 Usage Monitoring

- Monitor API usage through your provider dashboards
- Set up usage alerts to avoid unexpected charges
- Track app performance in Streamlit Cloud

### 7.2 Regular Updates

- Keep dependencies updated
- Monitor for security patches
- Update API endpoints as needed

### 7.3 Backup Strategy

- Keep a local copy of your code
- Use version control for all changes
- Document any custom configurations

## Advanced Configuration

### Custom Domain (Optional)

1. Purchase a domain name
2. Configure DNS settings
3. Add custom domain in Streamlit Cloud settings

### Multiple Environments

Create separate deployments for:
- Development (testing new features)
- Staging (pre-production testing)
- Production (live application)

## Support and Resources

### Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud Guide](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub Pages](https://pages.github.com/)

### Community
- [Streamlit Community](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

### API Provider Documentation
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)
- [Groq API](https://console.groq.com/docs)
- [Mistral AI API](https://docs.mistral.ai/)

---

**🎉 Congratulations! Your AI-Enhanced Peptide Generator is now deployed and ready to use!**

For additional support or questions, please refer to the main README.md file or open an issue in your GitHub repository. 