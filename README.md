# 🌐 Ultimate Korean Translator

AI-Powered Korean ↔ English Translation with Azure DeepSeek integration

## ✨ Features

- **🧠 Azure AI DeepSeek Integration**: Direct Korean-English translation with high quality
- **📁 Bulk Processing**: Translate multiple files at once
- **🌐 HTML Support**: Preserves structure, images, and formatting
- **📚 Smart Glossaries**: Character names and terminology consistency
- **🔄 Robust Error Handling**: Up to 6 retry attempts per translation chunk
- **📋 Detailed Logging**: Complete translation logs saved automatically
- **💾 Glossary Tracking**: Automatic usage statistics and updates
- **📄 Multiple Formats**: .txt, .pdf, .docx, .html support
- **🎯 Clean Output**: Professional results in organized folders

## 🚀 Quick Start

### 1. Setup Azure AI DeepSeek

**Option A: Config File (Recommended)**
1. Copy `azure_config_sample.txt` to `azure_config.txt`
2. Edit the file with your credentials:
   ```
   ENDPOINT=https://your-deployment.services.ai.azure.com/models
   API_KEY=your-api-key-here
   ```

**Option B: GUI Configuration**
1. Run the application
2. Go to "About" tab → "Configure Azure AI DeepSeek"
3. Enter your credentials and test

### 2. Install Dependencies

```bash
# Run the setup script
setup.bat

# Or install manually
pip install customtkinter pandas PyPDF2 python-docx beautifulsoup4 azure-ai-inference streamlit
```

### 3. Run the Application

```bash
# Desktop GUI (Recommended)
run_desktop_app.bat

# Web Interface  
run_streamlit_app.bat

# Command Line
run_console_app.bat
```

## 📋 How to Use

### Basic Translation

1. **Upload Files**: Select `.txt`, `.pdf`, `.docx`, or `.html` files
2. **Add Glossaries** (Optional): Upload CSV files with character names
3. **Configure Settings**: Choose source/target languages and context
4. **Start Translation**: Click "Start Translation" and wait for completion
5. **Check Results**: View detailed results and open output folder

### Glossary Format

Create CSV files with this structure:

| type | raw_name | translated_name | gender |
|------|----------|----------------|--------|
| character | 이시헌 | Lee Si-heon | male |
| character | 산수유 | Sansuyu | female |
| location | 세계수 | World Tree | |
| skill | 개화 | Bloom | |

### Output Structure

After translation, you'll find organized folders:

```
translated_ko_to_en_20241216_143022/
├── translations/          # Translated files
│   ├── chapter001.html
│   ├── chapter002_ko_to_en_20241216_143022.txt
│   └── ...
├── glossaries/           # Updated glossaries with usage stats
│   └── characters_updated_20241216_143022.csv
└── logs/                # Detailed translation logs
    └── translation_log_20241216_143022.txt
```

## 🔧 Advanced Features

### HTML Translation
- Preserves all images, links, and formatting
- Translates text content while maintaining structure
- Keeps original filenames for easy reference

### Error Handling
- **6 Retry Attempts**: Each failed translation chunk gets multiple attempts
- **Failed File Reporting**: Clear identification of problematic files
- **Partial Success**: Successfully process what can be translated
- **Detailed Logs**: Complete error information for troubleshooting

### Glossary System
- **Manual Loading**: Reliable CSV file upload
- **Usage Tracking**: See which terms are used and how often
- **Auto-Update**: Glossaries saved with new usage statistics
- **Multiple Glossaries**: Load and manage multiple terminology sets

## 📊 Translation Quality

### Best Practices
1. **Provide Context**: Add genre/type information (e.g., "Fantasy light novel")
2. **Use Glossaries**: Character names and terminology for consistency
3. **Chunk Large Files**: Break very large documents into smaller parts
4. **Review Failed Files**: Check logs for translation issues

### Supported Formats
- **Text Files** (`.txt`): Direct content translation
- **PDF Files** (`.pdf`): Extracted text translation
- **Word Documents** (`.docx`, `.doc`): Formatted content
- **HTML Files** (`.html`, `.htm`): Structure-preserving translation

## 🛠️ Troubleshooting

### Common Issues

**❌ Azure AI DeepSeek Not Available**
- Check your `azure_config.txt` file
- Verify endpoint URL and API key
- Test credentials using the GUI configuration

**❌ Translation Failures**
- Check internet connection
- Verify Azure service status
- Review translation logs for specific errors
- Try smaller file chunks

**❌ File Reading Errors**
- Ensure files are not corrupted
- Check file permissions
- Try different file formats
- Verify encoding (UTF-8 recommended)

### Log Files
Check the `logs/` folder for detailed information:
- Processing times and character counts
- Failed file details with error messages
- Glossary usage statistics
- Complete translation workflow

## 📁 File Structure

```
Ultimate Korean Translator/
├── ultimateTranslator.py       # Core translation engine
├── translator_app.py           # Desktop GUI application
├── streamlit_app.py            # Web interface
├── azure_config.txt           # Your Azure credentials
├── setup.bat                  # Installation script
├── run_desktop_app.bat        # Launch desktop GUI
├── run_streamlit_app.bat      # Launch web interface
└── translated_*/              # Output folders
    ├── translations/
    ├── glossaries/
    └── logs/
```

## 🔒 Security Notes

- **Never share** your `azure_config.txt` file
- **Keep API keys private** and secure
- **Rotate credentials** regularly for security
- **Use environment variables** in production

## 📞 Support

For issues or questions:

1. **Check Logs**: Review the detailed logs in the `logs/` folder
2. **Verify Configuration**: Ensure Azure credentials are correct
3. **Test with Small Files**: Try simple text files first
4. **Check Network**: Verify internet connectivity

## 🎯 Tips for Best Results

### Translation Quality
- Add specific context for better accuracy
- Use consistent glossaries across projects
- Review and update terminology regularly
- Process similar content types together

### Performance
- Process files in batches for efficiency
- Use appropriate file types for your content
- Monitor translation logs for optimization
- Keep Azure connection stable

### Organization
- Use descriptive folder names
- Maintain glossary files consistently
- Archive completed projects
- Review translation logs periodically

---

**Version**: 2.0  
**Engine**: Azure AI DeepSeek V3-0324  
**Features**: Bulk processing, HTML support, glossary management, robust error handling