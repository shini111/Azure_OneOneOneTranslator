import streamlit as st
import os
import tempfile
from pathlib import Path
import pandas as pd
from datetime import datetime
import shutil
import sys

# Import your existing translator
from ultimateTranslator import DeepSeekOnlyTranslator

# Page configuration
st.set_page_config(
    page_title="Ultimate Korean Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_application_directory():
    """Get the directory where the application is running from"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent

def initialize_session_state():
    """Initialize session state variables"""
    if 'translator' not in st.session_state:
        st.session_state.translator = DeepSeekOnlyTranslator()
    if 'translation_results' not in st.session_state:
        st.session_state.translation_results = None
    if 'temp_folder' not in st.session_state:
        st.session_state.temp_folder = None

def create_temp_folder_from_files(uploaded_files, glossary_files=None):
    """Create a temporary folder with uploaded files"""
    temp_dir = tempfile.mkdtemp()
    
    # Save uploaded files
    for uploaded_file in uploaded_files:
        file_path = Path(temp_dir) / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
    # Save glossary files if provided
    if glossary_files:
        for glossary_file in glossary_files:
            file_path = Path(temp_dir) / glossary_file.name
            with open(file_path, "wb") as f:
                f.write(glossary_file.getbuffer())
    
    return temp_dir

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌐 Ultimate Korean Translator</h1>
        <p>AI-Powered Korean ↔ English Translation with Azure DeepSeek</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check translator status
        if st.session_state.translator.use_azure_deepseek:
            st.success("🎉 Azure AI DeepSeek Ready!")
        else:
            st.error("❌ Azure AI DeepSeek Not Available")
            st.info("Check your endpoint and API key configuration")
        
        st.divider()
        
        # Translation settings
        st.subheader("🔄 Translation Settings")
        source_lang = st.selectbox("Source Language", ["ko", "en"], index=0)
        target_lang = st.selectbox("Target Language", ["en", "ko"], index=0)
        
        context = st.text_area(
            "Context (Optional)", 
            placeholder="e.g., Fantasy light novel, Romance story, Technical document",
            help="Provide context to improve translation quality"
        )
        
        st.divider()
        
        # Features info
        st.subheader("✨ Features")
        st.markdown("""
        - 📁 **Bulk Processing**: Multiple files at once
        - 📚 **Manual Glossaries**: Character & term consistency  
        - 🌐 **HTML Support**: Preserves structure & images
        - 🎯 **Multiple Formats**: .txt, .pdf, .docx, .html
        - 🧠 **AI-Powered**: Azure DeepSeek integration
        - 🔄 **Proper Error Handling**: Up to 6 retry attempts
        - 📁 **App Directory Output**: Clean organized results
        """)
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📁 File Translation", "📊 Results", "📚 Glossary Manager", "📋 About"])
    
    with tab1:
        st.header("📁 File Translation")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📄 Upload Files to Translate")
            uploaded_files = st.file_uploader(
                "Choose files",
                type=["txt", "pdf", "docx", "doc", "html", "htm"],
                accept_multiple_files=True,
                help="Supported formats: .txt, .pdf, .docx, .html"
            )
            
            if uploaded_files:
                st.info(f"📤 {len(uploaded_files)} files uploaded")
                for file in uploaded_files:
                    st.write(f"• {file.name} ({file.size:,} bytes)")
        
        with col2:
            st.subheader("📚 Upload Glossaries (Optional)")
            glossary_files = st.file_uploader(
                "Choose glossary CSV files",
                type=["csv"],
                accept_multiple_files=True,
                help="CSV files with columns: type, raw_name, translated_name"
            )
            
            if glossary_files:
                st.success(f"📚 {len(glossary_files)} glossaries uploaded")
                for file in glossary_files:
                    st.write(f"• {file.name}")
        
        # Translation button
        if uploaded_files and st.session_state.translator.use_azure_deepseek:
            if st.button("🚀 Start Translation", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing files..."):
                    try:
                        # Create temporary folder with files
                        temp_folder = create_temp_folder_from_files(uploaded_files, glossary_files)
                        st.session_state.temp_folder = temp_folder
                        
                        # Load glossaries if any were uploaded
                        if glossary_files:
                            st.write("📚 Loading glossaries...")
                            for glossary_file in glossary_files:
                                try:
                                    # Save glossary file to temp folder
                                    glossary_path = Path(temp_folder) / glossary_file.name
                                    with open(glossary_path, "wb") as f:
                                        f.write(glossary_file.getbuffer())
                                    
                                    # Load glossary
                                    result = st.session_state.translator.load_glossary_csv(str(glossary_path))
                                    if "successfully" in result:
                                        glossary_name = Path(glossary_path).stem
                                        st.session_state.translator.set_active_glossary(glossary_name)
                                        st.success(f"✅ Loaded glossary: {glossary_name}")
                                    else:
                                        st.error(f"❌ Failed to load glossary: {result}")
                                except Exception as e:
                                    st.error(f"❌ Error loading glossary: {e}")
                        
                        # Progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Process files
                        status_text.text("🔍 Processing files...")
                        progress_bar.progress(10)
                        
                        # Create file info for processing
                        file_info_list = []
                        for uploaded_file in uploaded_files:
                            file_path = Path(temp_folder) / uploaded_file.name
                            file_info_list.append({
                                "path": file_path,
                                "name": uploaded_file.name,
                                "type": file_path.suffix.lower(),
                                "size": uploaded_file.size
                            })
                        
                        # Sort files by priority
                        sorted_files = st.session_state.translator.sort_documents_by_priority(file_info_list)
                        
                        # Create output folder in application directory
                        output_folder = st.session_state.translator.create_output_structure(source_lang, target_lang)
                        
                        # Process each file
                        results = {
                            "processed_files": [],
                            "skipped_files": [],
                            "failed_files": [],
                            "total_time": 0,
                            "total_chars": 0,
                            "output_folder": output_folder,
                            "glossaries_used": list(st.session_state.translator.glossaries.keys()),
                            "method": "Azure AI DeepSeek with Streamlit integration",
                            "source_lang": source_lang,
                            "target_lang": target_lang
                        }
                        
                        import time
                        start_time = time.time()
                        
                        for i, file_info in enumerate(sorted_files):
                            file_path = file_info["path"]
                            file_name = file_info["name"]
                            
                            status_text.text(f"📄 Processing {i+1}/{len(sorted_files)}: {file_name}")
                            progress = 10 + (80 * i / len(sorted_files))
                            progress_bar.progress(int(progress))
                            
                            try:
                                # Process single document
                                file_result = st.session_state.translator.process_single_document(
                                    file_path, source_lang, target_lang, context, output_folder
                                )
                                
                                if file_result["success"]:
                                    results["processed_files"].append(file_result)
                                    results["total_chars"] += file_result["char_count"]
                                    st.write(f"✅ Completed: {file_name}")
                                else:
                                    results["failed_files"].append({
                                        "file": file_name,
                                        "error": file_result["error"]
                                    })
                                    st.error(f"❌ Failed: {file_name} - {file_result['error']}")
                                
                            except Exception as e:
                                error_msg = str(e)
                                results["failed_files"].append({
                                    "file": file_name,
                                    "error": error_msg
                                })
                                st.error(f"❌ Error processing {file_name}: {error_msg}")
                        
                        # Final results
                        total_time = time.time() - start_time
                        results["total_time"] = total_time
                        
                        # Save glossary and logs (new functionality)
                        try:
                            # Save updated glossary with usage stats
                            if st.session_state.translator.glossaries:
                                st.session_state.translator.save_updated_glossary(output_folder)
                                st.write("💾 Glossary saved with usage statistics")
                            
                            # Save translation logs
                            st.session_state.translator.save_translation_logs(output_folder, results)
                            st.write("📋 Translation logs saved")
                            
                        except Exception as e:
                            st.error(f"⚠️ Error saving files: {e}")
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Translation completed!")
                        
                        # Store results
                        st.session_state.translation_results = results
                        
                        # Show summary
                        if results["processed_files"] or results["failed_files"]:
                            st.markdown("""
                            <div class="success-box">
                                <h4>🎉 Translation Process Completed!</h4>
                                <p><strong>Successfully processed:</strong> {} files</p>
                                <p><strong>Failed:</strong> {} files</p>
                                <p><strong>Characters:</strong> {:,}</p>
                                <p><strong>Time:</strong> {:.2f} seconds</p>
                                <p><strong>Output:</strong> {}</p>
                            </div>
                            """.format(
                                len(results['processed_files']),
                                len(results['failed_files']),
                                results['total_chars'],
                                results['total_time'],
                                str(results['output_folder'])
                            ), unsafe_allow_html=True)
                            
                            # Show failed files if any
                            if results['failed_files']:
                                st.subheader("❌ Failed Files")
                                for failed in results['failed_files']:
                                    st.error(f"**{failed['file']}**: {failed['error']}")
                            
                            # Switch to results tab
                            st.success("👉 Check the 'Results' tab for detailed information!")
                        else:
                            st.error("❌ No files were processed successfully")
                            
                    except Exception as e:
                        st.error(f"❌ Error during translation: {str(e)}")
        
        elif not uploaded_files:
            st.info("👆 Upload files above to start translation")
        elif not st.session_state.translator.use_azure_deepseek:
            st.error("❌ Azure AI DeepSeek is not configured. Check your settings.")
    
    with tab2:
        st.header("📊 Translation Results")
        
        if st.session_state.translation_results:
            results = st.session_state.translation_results
            
            if results["processed_files"] or results["failed_files"]:
                # Summary statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📄 Files Processed", len(results['processed_files']))
                
                with col2:
                    st.metric("❌ Failed Files", len(results['failed_files']))
                
                with col3:
                    st.metric("📊 Total Characters", f"{results['total_chars']:,}")
                
                with col4:
                    st.metric("⏱️ Processing Time", f"{results['total_time']:.1f}s")
                
                st.divider()
                
                # Output folder information
                st.subheader("📁 Output Location")
                st.info(f"**Output folder:** {results['output_folder']}")
                st.write("💡 Files are saved in the application directory for easy access")
                
                st.divider()
                
                # File details
                st.subheader("📋 Processing Details")
                
                if results['processed_files']:
                    st.write("**✅ Successfully Processed Files:**")
                    # Create DataFrame for display
                    file_data = []
                    for file_info in results['processed_files']:
                        file_data.append({
                            'Original File': file_info['file'],
                            'Output File': file_info['output_file'],
                            'Characters': f"{file_info['char_count']:,}",
                            'Time (s)': f"{file_info['translation_time']:.2f}",
                            'Method': file_info['method']
                        })
                    
                    df = pd.DataFrame(file_data)
                    st.dataframe(df, use_container_width=True)
                
                # Failed files
                if results['failed_files']:
                    st.write("**❌ Failed Files:**")
                    for failed in results['failed_files']:
                        st.error(f"**{failed['file']}**: {failed['error']}")
                
            else:
                st.error("❌ No translation results available")
        else:
            st.info("🔄 No translation results yet. Upload and translate files first!")
    
    with tab3:
        st.header("📚 Glossary Manager")
        
        st.markdown("""
        <div class="feature-box">
            <h4>📝 Glossary Format</h4>
            <p>Upload CSV files with these columns:</p>
            <ul>
                <li><strong>type</strong>: character, location, skill, etc.</li>
                <li><strong>raw_name</strong>: Korean term</li>
                <li><strong>translated_name</strong>: English translation</li>
                <li><strong>gender</strong>: male/female (optional)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample glossary
        st.subheader("📋 Sample Glossary Format")
        sample_data = {
            'type': ['character', 'character', 'location', 'skill'],
            'raw_name': ['이시헌', '산수유', '세계수', '개화'],
            'translated_name': ['Lee Si-heon', 'Sansuyu', 'World Tree', 'Bloom'],
            'gender': ['male', 'female', '', '']
        }
        
        sample_df = pd.DataFrame(sample_data)
        st.dataframe(sample_df, use_container_width=True)
        
        st.info("💡 Create a CSV file with the format above and upload it in the File Translation tab.")
        
        st.divider()
        
        # Current glossaries
        if st.session_state.translator.glossaries:
            st.subheader("📚 Currently Loaded Glossaries")
            
            # Glossary selector
            glossary_names = list(st.session_state.translator.glossaries.keys())
            selected_glossary = st.selectbox(
                "Select glossary to view:", 
                ["None"] + glossary_names,
                index=1 if st.session_state.translator.active_glossary else 0
            )
            
            if selected_glossary and selected_glossary != "None":
                glossary = st.session_state.translator.glossaries[selected_glossary]
                st.write(f"**📖 {selected_glossary}** ({len(glossary)} terms)")
                
                # Group terms by type
                terms_by_type = {}
                for korean, data in glossary.items():
                    term_type = data.get('type', 'unknown')
                    if term_type not in terms_by_type:
                        terms_by_type[term_type] = []
                    terms_by_type[term_type].append((korean, data))
                
                # Display terms by type
                for term_type, terms in sorted(terms_by_type.items()):
                    with st.expander(f"🏷️ {term_type.upper()} ({len(terms)} terms)"):
                        for korean, data in terms:
                            gender = f" ({data.get('gender', '')})" if data.get('gender') else ""
                            usage = data.get('usage_count', 0)
                            usage_info = f" [Used: {usage}x]" if usage > 0 else ""
                            st.write(f"• **{korean}** → {data['translation']}{gender}{usage_info}")
            
            # Statistics
            st.subheader("📊 Glossary Statistics")
            total_terms = sum(len(glossary) for glossary in st.session_state.translator.glossaries.values())
            st.metric("Total Terms", total_terms)
            
            # Terms by type
            type_counts = {}
            for glossary in st.session_state.translator.glossaries.values():
                for term_data in glossary.values():
                    term_type = term_data.get('type', 'unknown')
                    type_counts[term_type] = type_counts.get(term_type, 0) + 1
            
            if type_counts:
                st.write("**Terms by Type:**")
                for term_type, count in sorted(type_counts.items()):
                    st.write(f"• {term_type}: {count}")
        else:
            st.info("No glossaries loaded yet. Upload CSV files in the File Translation tab to load glossaries.")
    
    with tab4:
        st.header("📋 About Ultimate Korean Translator")
        
        # Version info
        st.subheader("🌐 Version Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Version:** 2.0
            **Engine:** Azure AI DeepSeek
            **Status:** {'🟢 Active' if st.session_state.translator.use_azure_deepseek else '🔴 Inactive'}
            **Model:** DeepSeek-V3-0324
            """)
        
        with col2:
            st.info(f"""
            **Output:** Application directory
            **HTML Support:** ✅ Enabled
            **Glossary System:** Manual loading
            **Error Handling:** 6 retry attempts
            """)
        
        st.divider()
        
        # Azure Configuration
        st.subheader("🔧 Azure AI DeepSeek Configuration")
        
        with st.expander("Configure Azure Credentials"):
            st.info("Enter your Azure AI DeepSeek credentials. These will be saved to 'azure_config.txt' for future use.")
            
            # Current status
            if st.session_state.translator.use_azure_deepseek:
                st.success("✅ Azure AI DeepSeek is currently configured and working")
            else:
                st.warning("⚠️ Azure AI DeepSeek is not configured")
            
            # Input fields
            endpoint = st.text_input(
                "Endpoint URL:",
                value=st.session_state.translator.azure_endpoint,
                placeholder="https://your-deployment.services.ai.azure.com/models"
            )
            
            api_key = st.text_input(
                "API Key:",
                value=st.session_state.translator.azure_api_key,
                type="password",
                placeholder="Your Azure API Key"
            )
            
            if st.button("🧪 Test & Save Credentials"):
                if endpoint and api_key:
                    with st.spinner("Testing credentials..."):
                        success, message = st.session_state.translator.configure_azure_credentials(endpoint, api_key)
                        if success:
                            st.success(message)
                            st.rerun()  # Refresh the page to update status
                        else:
                            st.error(message)
                else:
                    st.error("Please enter both endpoint and API key")
        
        st.divider()
        
        # Features
        st.subheader("✨ Key Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Translation:**
            - Direct Korean ↔ English translation
            - Context-aware processing
            - Multiple file format support
            - HTML structure preservation
            - Glossary integration
            - Proper error handling (6 retries)
            """)
        
        with col2:
            st.markdown("""
            **Output & Logging:**
            - Bulk file processing
            - Application directory output
            - Auto-save glossaries with usage stats
            - Detailed translation logs
            - Failed file reporting
            - Clean output format
            """)
        
        st.divider()
        
        # Supported formats
        st.subheader("📄 Supported File Types")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Document Types:**
            - `.txt` - Text files
            - `.pdf` - PDF documents
            - `.docx/.doc` - Word documents
            - `.html/.htm` - Web pages
            """)
        
        with col2:
            st.markdown("""
            **Glossary Types:**
            - `.csv` - Comma-separated values
            
            **HTML Features:**
            - Preserves images and structure
            - Translates text content
            - Maintains formatting
            """)
        
        st.divider()
        
        # Technical details
        st.subheader("🔧 Technical Details")
        
        with st.expander("Azure AI DeepSeek Configuration"):
            if st.session_state.translator.use_azure_deepseek:
                st.success("✅ Azure AI DeepSeek is properly configured and working")
                st.info("Direct Korean-to-English translation with glossary support")
            else:
                st.error("❌ Azure AI DeepSeek is not configured")
                st.info("Please check your endpoint and API key in ultimateTranslator.py")
        
        with st.expander("Processing Details"):
            st.info("""
            **Translation Process:**
            1. Files are processed with up to 6 retry attempts per chunk
            2. Failed translations are properly reported with file names
            3. Glossary terms are tracked and usage is logged
            4. Output is saved to application directory for easy access
            5. Clean output format without metadata headers
            
            **Error Handling:**
            - Translation failures are caught and reported
            - Failed files are listed with specific error messages
            - Partial success is supported (some files succeed, others fail)
            """)

if __name__ == "__main__":
    main()
