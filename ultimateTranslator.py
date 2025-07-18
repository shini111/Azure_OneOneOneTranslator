# DeepSeek-Only Automated Folder Translation System
# With HTML support and interactive glossary updates

import pandas as pd
import os
import re
from pathlib import Path
import time
import PyPDF2
import docx
from datetime import datetime
import json
from typing import List, Dict, Tuple
import shutil
from bs4 import BeautifulSoup, NavigableString
import sys

# Azure AI DeepSeek imports
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Azure AI DeepSeek Configuration
AZURE_AI_MODEL = "DeepSeek-V3-0324"

def load_azure_config():
    """Load Azure configuration from config file or return defaults"""
    config_file = Path(__file__).parent / "azure_config.txt"
    
    try:
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                lines = f.read().strip().split('\n')
                if len(lines) >= 2:
                    endpoint = lines[0].split('=', 1)[1].strip() if '=' in lines[0] else lines[0].strip()
                    api_key = lines[1].split('=', 1)[1].strip() if '=' in lines[1] else lines[1].strip()
                    return endpoint, api_key
    except Exception as e:
        print(f"⚠️ Error reading config file: {e}")
    
    # Return empty values if config file doesn't exist or is invalid
    return "", ""

def save_azure_config(endpoint, api_key):
    """Save Azure configuration to config file"""
    config_file = Path(__file__).parent / "azure_config.txt"
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(f"ENDPOINT={endpoint}\n")
            f.write(f"API_KEY={api_key}\n")
        return True
    except Exception as e:
        print(f"❌ Error saving config file: {e}")
        return False

class TranslationFailedException(Exception):
    """Exception raised when translation completely fails after all attempts"""
    pass

class AzureDeepSeekTranslator:
    """Azure AI DeepSeek for direct Korean-to-English translation with glossary support"""
    
    def __init__(self, endpoint: str, api_key: str):
        """Initialize Azure AI DeepSeek client"""
        self.endpoint = endpoint
        self.api_key = api_key
        self.model_name = AZURE_AI_MODEL
        self.working = False
        
        try:
            print("🔧 Setting up Azure AI DeepSeek client...")
            
            self.client = ChatCompletionsClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.api_key),
                api_version="2024-05-01-preview"
            )
            
            # Only validate credentials format, don't test connection
            if endpoint and api_key and len(api_key) > 20:
                self.working = True
                print("✅ Azure AI DeepSeek client ready (credentials validated)")
            else:
                print("❌ Invalid Azure AI DeepSeek credentials")
                
        except Exception as e:
            print(f"❌ Azure AI DeepSeek setup failed: {e}")
    
    def test_connection(self):
        """Test if Azure AI DeepSeek is working - ONLY call this when explicitly needed"""
        try:
            print("🧪 Testing Azure AI DeepSeek connection...")
            
            response = self.client.complete(
                messages=[
                    SystemMessage(content="You are a Korean-to-English translator."),
                    UserMessage(content="Translate this Korean to English: '안녕하세요. 저는 학생입니다.' Be natural and fluent.")
                ],
                max_tokens=100,
                temperature=0.1,
                top_p=0.95,
                presence_penalty=0.0,
                frequency_penalty=0.0,
                model=self.model_name
            )
            
            if response.choices and len(response.choices) > 0:
                self.working = True
                result = response.choices[0].message.content
                print(f"✅ Azure AI DeepSeek test successful: {result}")
                return True, result
            else:
                print("❌ Azure AI DeepSeek test failed - no response")
                self.working = False
                return False, "No response received"
                
        except Exception as e:
            print(f"❌ Azure AI DeepSeek test error: {e}")
            self.working = False
            return False, str(e)
    
    def translate_with_glossary(self, korean_text: str, glossary_terms: str = "", context: str = "", element_type: str = "text", max_retries: int = 5) -> str:
        """Translate Korean text directly to English using DeepSeek with glossary support and better error handling"""
        
        if not self.working:
            print(f"      ❌ Azure AI DeepSeek not available")
            raise TranslationFailedException("Azure AI DeepSeek not available")
        
        # Skip very short or empty chunks
        if not korean_text.strip() or len(korean_text.strip()) < 3:
            return korean_text
        
        for attempt in range(max_retries + 1):
            try:
                # Build comprehensive prompt for direct translation
                system_prompt = """You are an expert Korean-to-English translator specializing in novels and literature. 
                You are translating Korean fiction/literature to English.
                This is creative content from published novels and stories.
                The content includes fictional scenarios, fantasy elements, and dramatic situations.
                Translate accurately while maintaining appropriate literary tone.
                Focus on narrative flow and character development.
                
                Your job is to translate Korean text directly to natural, fluent English while preserving:
                - Exact meaning and nuance
                - Character personalities and voice
                - Cultural context and honorifics
                - Dialogue formatting and flow
                - Narrative tone and style
                
                Rules:
                - Output ONLY the English translation
                - Do not include any meta-commentary, explanations, or notes
                - Do not mention the translation process
                - Just provide the clean English text"""

                # Build user prompt with element context
                element_context = {
                    "title": "page title",
                    "heading": "section heading", 
                    "paragraph": "story content",
                    "text": "general text"
                }
                
                user_prompt = f"""Translate this Korean {element_context.get(element_type, 'text')} to natural, fluent English.

Context: {context if context else "Korean novel/literature"}"""

                if glossary_terms:
                    user_prompt += f"""

IMPORTANT - Use these specific translations for character names and terms:
{glossary_terms}

Make sure to use these exact English names/terms when they appear in the text."""

                user_prompt += f"""

Korean {element_type} to translate:
{korean_text}

English translation:"""

                response = self.client.complete(
                    messages=[
                        SystemMessage(content=system_prompt),
                        UserMessage(content=user_prompt)
                    ],
                    max_tokens=len(korean_text) + 500,  # Allow for expansion
                    temperature=0.1,  # Low temperature for consistent translation
                    top_p=0.95,
                    presence_penalty=0.0,
                    frequency_penalty=0.0,
                    model=self.model_name
                )
                
                if response.choices and len(response.choices) > 0:
                    english_text = response.choices[0].message.content
                    
                    # Check if response is None or empty
                    if english_text is None:
                        print(f"      ⚠️ Received None response from Azure AI DeepSeek (attempt {attempt + 1})")
                        if attempt < max_retries:
                            time.sleep(2)
                            continue
                        else:
                            break
                    
                    english_text = english_text.strip()
                    
                    # Clean up any meta-commentary
                    english_text = self.clean_output(english_text)
                    
                    # Validate that we got a reasonable translation
                    if english_text and len(english_text) > 5 and not english_text.startswith("Translation"):
                        print(f"      ✅ Azure AI DeepSeek translated {element_type} successfully")
                        return english_text
                    else:
                        print(f"      ⚠️ Received poor translation quality, retrying... (attempt {attempt + 1})")
                        if attempt < max_retries:
                            time.sleep(1)
                            continue
                else:
                    print(f"      ⚠️ Azure AI DeepSeek returned no response (attempt {attempt + 1})")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    
            except Exception as e:
                print(f"      ⚠️ Azure AI DeepSeek error (attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    time.sleep(2)
                    continue
        
        # If all attempts failed, raise exception instead of returning original text
        print(f"      ❌ Translation failed after {max_retries + 1} attempts")
        raise TranslationFailedException(f"Translation failed after {max_retries + 1} attempts")
    
    def clean_output(self, text: str) -> str:
        """Clean up DeepSeek output to remove meta-commentary"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip meta-commentary patterns
            skip_patterns = [
                'english translation:', 'translation:', 'here is the', 'the translation is',
                'korean text:', 'context:', 'original:', 'note:', 'important:',
                'here\'s the translation:', 'the english version:', 'translated text:',
                'improved translation:', 'here is your translation:'
            ]
            
            if any(pattern in line.lower() for pattern in skip_patterns):
                continue
            
            cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        # Additional cleaning for common artifacts
        result = re.sub(r'^[Tt]ranslation:\s*', '', result)
        result = re.sub(r'^[Ee]nglish:\s*', '', result)
        result = re.sub(r'^[Tt]ranslated:\s*', '', result)
        
        return result.strip()

class DeepSeekOnlyTranslator:
    def __init__(self):
        # Initialize settings without heavy ML dependencies
        self.glossaries = {}
        self.active_glossary = None
        self.glossary_usage = {}  # Track which terms are used
        self.new_terms_found = {}  # Track potential new terms
        
        # Folder processing settings
        self.interactive_mode = True
        self.min_term_frequency = 2
        self.supported_extensions = {'.txt', '.pdf', '.docx', '.doc', '.html', '.htm'}
        self.glossary_extensions = {'.csv'}
        
        # Glossary update settings - removed auto_update_glossary
        self.process_html_files = True
        
        # Log tracking for saving
        self.translation_logs = []
        
        print(f"🚀 DeepSeek-Only Translation System - HTML + Glossary support!")
        
        # Azure AI DeepSeek integration
        self.azure_translator = None
        self.use_azure_deepseek = False
        self.azure_endpoint = ""
        self.azure_api_key = ""
        self.setup_azure_deepseek()
    
    def setup_azure_deepseek(self):
        """Setup Azure AI DeepSeek translator"""
        try:
            # Try to load from config file first
            endpoint, api_key = load_azure_config()
            
            # If config file is empty, try environment variables
            if not endpoint or not api_key:
                endpoint = os.getenv("AZURE_AI_ENDPOINT", "")
                api_key = os.getenv("AZURE_AI_API_KEY", "")
            
            # Store credentials for potential GUI input
            self.azure_endpoint = endpoint
            self.azure_api_key = api_key
            
            # Check if we have valid credentials
            if endpoint and api_key and len(api_key) > 20:
                self.azure_translator = AzureDeepSeekTranslator(endpoint, api_key)
                self.use_azure_deepseek = self.azure_translator.working
                
                if self.use_azure_deepseek:
                    print("🚀 Azure AI DeepSeek ready for translation!")
                    print("   💡 Credentials loaded and validated")
                else:
                    print("⚠️ Azure AI DeepSeek credentials invalid")
            else:
                print("❌ Azure AI DeepSeek credentials not found")
                print("   Create 'azure_config.txt' with your endpoint and API key")
                print("   Or use the GUI to enter credentials")
                
        except Exception as e:
            print(f"⚠️ Azure AI DeepSeek setup error: {e}")
            self.use_azure_deepseek = False
    
    def configure_azure_credentials(self, endpoint, api_key):
        """Configure Azure credentials manually (for GUI use)"""
        try:
            self.azure_endpoint = endpoint
            self.azure_api_key = api_key
            
            # Create test translator and actually test the connection
            test_translator = AzureDeepSeekTranslator(endpoint, api_key)
            success, result = test_translator.test_connection()
            
            if success:
                # Save to config file for future use
                save_azure_config(endpoint, api_key)
                
                # Update current translator
                self.azure_translator = test_translator
                self.use_azure_deepseek = True
                
                return True, "Azure AI DeepSeek configured and tested successfully!"
            else:
                return False, f"Azure AI DeepSeek test failed: {result}"
                
        except Exception as e:
            return False, f"Error configuring Azure: {e}"
    
    def get_application_directory(self):
        """Get the directory where the application is running from"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return Path(sys.executable).parent
        else:
            # Running as script
            return Path(__file__).parent
    
    # ========== FOLDER ANALYSIS ==========
    
    def analyze_folder(self, folder_path: str) -> Dict:
        """Analyze folder contents and create processing plan"""
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            return {"error": f"Folder does not exist: {folder_path}"}
        
        analysis = {
            "folder_path": folder_path,
            "glossaries": [],
            "documents": [],
            "html_files": [],
            "other_files": [],
            "subfolders": [],
            "total_size": 0
        }
        
        print(f"🔍 Analyzing folder: {folder_path}")
        print("=" * 50)
        
        # Scan all files
        for item in folder_path.iterdir():
            if item.is_file():
                file_size = item.stat().st_size
                analysis["total_size"] += file_size
                
                if item.suffix.lower() in self.glossary_extensions:
                    analysis["glossaries"].append({
                        "path": item,
                        "name": item.stem,
                        "size": file_size
                    })
                elif item.suffix.lower() in {'.html', '.htm'}:
                    analysis["html_files"].append({
                        "path": item,
                        "name": item.name,
                        "type": item.suffix.lower(),
                        "size": file_size
                    })
                elif item.suffix.lower() in {'.txt', '.pdf', '.docx', '.doc'}:
                    analysis["documents"].append({
                        "path": item,
                        "name": item.name,
                        "type": item.suffix.lower(),
                        "size": file_size
                    })
                else:
                    analysis["other_files"].append({
                        "path": item,
                        "name": item.name,
                        "type": item.suffix.lower(),
                        "size": file_size
                    })
            elif item.is_dir():
                analysis["subfolders"].append(item)
        
        # Display analysis
        print(f"📁 Folder Contents:")
        print(f"   📚 Glossaries found: {len(analysis['glossaries'])}")
        for glossary in analysis["glossaries"]:
            print(f"      • {glossary['name']}.csv ({glossary['size']:,} bytes)")
        
        print(f"   📄 Text documents found: {len(analysis['documents'])}")
        print(f"   🌐 HTML files found: {len(analysis['html_files'])}")
        
        doc_types = {}
        for doc in analysis["documents"]:
            doc_type = doc["type"]
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        for doc_type, count in doc_types.items():
            print(f"      • {doc_type}: {count} files")
        
        if analysis["html_files"]:
            print(f"      • .html/.htm: {len(analysis['html_files'])} files")
        
        if analysis["other_files"]:
            print(f"   📋 Other files: {len(analysis['other_files'])} (will be ignored)")
        
        print(f"   💾 Total size: {analysis['total_size']:,} bytes ({analysis['total_size']/1024/1024:.1f} MB)")
        
        return analysis
    
    # ========== GLOSSARY SYSTEM ==========
    
    def load_glossary_csv(self, csv_path: str, glossary_name: str = None) -> str:
        """Load glossary from CSV file"""
        try:
            # Read CSV with proper handling of missing values
            df = pd.read_csv(csv_path, encoding='utf-8', keep_default_na=False, na_values=[''])
            
            # Validate CSV format
            required_columns = ['type', 'raw_name', 'translated_name']
            if not all(col in df.columns for col in required_columns):
                return f"❌ CSV must have columns: {required_columns}. Found: {list(df.columns)}"
            
            # Convert to glossary dictionary
            glossary = {}
            skipped_rows = 0
            
            for index, row in df.iterrows():
                try:
                    # Handle potential NaN/float values safely
                    raw_name = row['raw_name']
                    translated_name = row['translated_name']
                    term_type = row['type']
                    
                    # Skip rows with missing essential data
                    if pd.isna(raw_name) or pd.isna(translated_name) or pd.isna(term_type):
                        skipped_rows += 1
                        continue
                    
                    # Convert to string and strip whitespace
                    korean_term = str(raw_name).strip()
                    english_term = str(translated_name).strip()
                    term_type_clean = str(term_type).strip()
                    
                    # Handle gender field (optional)
                    gender = row.get('gender', '')
                    if pd.isna(gender):
                        gender = ''
                    else:
                        gender = str(gender).strip()
                    
                    # Skip empty terms
                    if not korean_term or not english_term or not term_type_clean:
                        skipped_rows += 1
                        continue
                    
                    glossary[korean_term] = {
                        'translation': english_term,
                        'type': term_type_clean,
                        'gender': gender,
                        'usage_count': 0,
                        'last_used': None
                    }
                    
                except Exception as e:
                    print(f"   ⚠️ Skipping row {index + 1}: {e}")
                    skipped_rows += 1
                    continue
            
            # Store glossary
            if not glossary_name:
                glossary_name = Path(csv_path).stem
                
            self.glossaries[glossary_name] = glossary
            
            success_msg = f"✅ Loaded glossary '{glossary_name}' with {len(glossary)} terms"
            if skipped_rows > 0:
                success_msg += f" (skipped {skipped_rows} invalid rows)"
            
            print(success_msg)
            
            # Show sample terms
            print(f"   📋 Sample terms:")
            for i, (korean, data) in enumerate(list(glossary.items())[:3]):
                print(f"      • {korean} → {data['translation']} ({data['type']})")
                if i >= 2:  # Show max 3 samples
                    break
            
            return f"Glossary '{glossary_name}' loaded successfully"
            
        except Exception as e:
            return f"❌ Error loading glossary: {e}"
    
    def set_active_glossary(self, glossary_name: str) -> bool:
        """Set which glossary to use for translation"""
        if glossary_name in self.glossaries:
            self.active_glossary = glossary_name
            print(f"✅ Active glossary set to: {glossary_name}")
            # Initialize usage tracking for this glossary
            self.glossary_usage = {}
            return True
        else:
            print(f"❌ Glossary '{glossary_name}' not found")
            return False
    
    def prepare_glossary_for_translation(self) -> str:
        """Prepare glossary terms as a string for DeepSeek"""
        if not self.active_glossary:
            return ""
        
        glossary = self.glossaries[self.active_glossary]
        
        glossary_text = []
        for korean_term, data in glossary.items():
            english_term = data['translation']
            term_type = data['type']
            glossary_text.append(f"- {korean_term} → {english_term} ({term_type})")
        
        return '\n'.join(glossary_text)
    
    def track_glossary_usage(self, korean_text: str, english_text: str):
        """Track which glossary terms were used in translation"""
        if not self.active_glossary:
            return
        
        glossary = self.glossaries[self.active_glossary]
        
        for korean_term, data in glossary.items():
            if korean_term in korean_text:
                # Term was in the source text
                english_term = data['translation']
                if english_term in english_text:
                    # Term was translated correctly
                    if korean_term not in self.glossary_usage:
                        self.glossary_usage[korean_term] = 0
                    self.glossary_usage[korean_term] += 1
    
    def update_glossary_after_file(self, file_name: str):
        """Update glossary usage counts after processing a file"""
        if not self.active_glossary or not self.glossary_usage:
            return
        
        print(f"\n📚 Updating glossary usage for {file_name}...")
        
        # Update usage counts
        glossary = self.glossaries[self.active_glossary]
        updated_terms = []
        
        for korean_term, usage_count in self.glossary_usage.items():
            if korean_term in glossary:
                glossary[korean_term]['usage_count'] += usage_count
                glossary[korean_term]['last_used'] = datetime.now().strftime('%Y-%m-%d')
                english_term = glossary[korean_term]['translation']
                updated_terms.append(f"{korean_term} → {english_term} (used {usage_count} times)")
        
        if updated_terms:
            print(f"   ✅ Updated usage for {len(updated_terms)} terms")
            for term in updated_terms[:5]:  # Show first 5
                print(f"      • {term}")
            if len(updated_terms) > 5:
                print(f"      • ... and {len(updated_terms) - 5} more")
        
        # Reset usage tracking for next file
        self.glossary_usage = {}
    
    def save_updated_glossary(self, output_folder: Path):
        """Save the updated glossary to the glossary folder - KEEP ORIGINAL 4-column format"""
        if not self.active_glossary:
            return

        try:
            glossary_name = self.active_glossary
            glossary = self.glossaries[glossary_name]

            # Create glossary output file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            glossary_file = output_folder / "glossaries" / f"{glossary_name}_updated_{timestamp}.csv"

            # Create CSV content with ORIGINAL 4-column format
            csv_content = "type,raw_name,translated_name,gender\n"
            for korean_term, info in glossary.items():
                # Keep only the original 4 columns
                csv_content += f"{info.get('type', '')},{korean_term},{info.get('translation', '')},{info.get('gender', '')}\n"

            # Save to file
            with open(glossary_file, 'w', encoding='utf-8') as f:
                f.write(csv_content)

            print(f"💾 Glossary saved to: {glossary_file}")
            print(f"   📋 Format: type,raw_name,translated_name,gender (4 columns)")

        except Exception as e:
            print(f"❌ Error saving glossary: {e}")

    def save_translation_logs(self, output_folder: Path, results: Dict):
        """Save translation logs to the logs folder"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = output_folder / "logs" / f"translation_log_{timestamp}.txt"
            
            # Create log content
            log_content = f"🌐 Ultimate Korean Translator - Translation Log\n"
            log_content += f"=" * 60 + "\n"
            log_content += f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            log_content += f"🔄 Languages: {results.get('source_lang', 'ko')} → {results.get('target_lang', 'en')}\n"
            log_content += f"🧠 Method: {results.get('method', 'Azure AI DeepSeek')}\n"
            log_content += f"📊 Total time: {results.get('total_time', 0):.2f} seconds\n"
            log_content += f"📝 Total characters: {results.get('total_chars', 0):,}\n"
            log_content += f"=" * 60 + "\n\n"
            
            # Processed files
            if results.get('processed_files'):
                log_content += f"✅ SUCCESSFULLY PROCESSED FILES ({len(results['processed_files'])}):\n"
                log_content += f"-" * 50 + "\n"
                for file_info in results['processed_files']:
                    log_content += f"📄 {file_info['file']}\n"
                    log_content += f"   → {file_info['output_file']}\n"
                    log_content += f"   📊 {file_info['char_count']:,} characters\n"
                    log_content += f"   ⏱️ {file_info['translation_time']:.2f} seconds\n"
                    log_content += f"   🔧 {file_info['method']}\n\n"
            
            # Failed files
            if results.get('failed_files'):
                log_content += f"❌ FAILED FILES ({len(results['failed_files'])}):\n"
                log_content += f"-" * 50 + "\n"
                for failed_info in results['failed_files']:
                    log_content += f"📄 {failed_info['file']}\n"
                    log_content += f"   ❌ Error: {failed_info['error']}\n\n"
            
            # Glossary usage
            if self.active_glossary and self.glossaries:
                log_content += f"📚 GLOSSARY USAGE:\n"
                log_content += f"-" * 50 + "\n"
                log_content += f"Active glossary: {self.active_glossary}\n"
                
                glossary = self.glossaries[self.active_glossary]
                used_terms = [(k, v) for k, v in glossary.items() if v.get('usage_count', 0) > 0]
                
                if used_terms:
                    log_content += f"Used terms ({len(used_terms)}):\n"
                    for korean, data in sorted(used_terms, key=lambda x: x[1]['usage_count'], reverse=True):
                        log_content += f"   • {korean} → {data['translation']} (used {data['usage_count']} times)\n"
                else:
                    log_content += f"No glossary terms were used in this translation.\n"
                log_content += "\n"
            
            # Additional logs from translation process
            if hasattr(self, 'translation_logs') and self.translation_logs:
                log_content += f"📋 DETAILED TRANSLATION LOG:\n"
                log_content += f"-" * 50 + "\n"
                for log_entry in self.translation_logs:
                    log_content += f"{log_entry}\n"
            
            # Save log file
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            print(f"📋 Translation log saved to: {log_file}")
            
        except Exception as e:
            print(f"❌ Error saving translation log: {e}")
    
    def log_translation_message(self, message: str):
        """Add a message to the translation log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        if not hasattr(self, 'translation_logs'):
            self.translation_logs = []
        self.translation_logs.append(log_entry)
        print(log_entry)
    
    # ========== DOCUMENT READING ==========
    
    def read_txt_file(self, file_path):
        """Read text from a .txt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            return "Error: Could not read file with any encoding"
        except Exception as e:
            return f"Error reading file: {e}"
    
    def read_pdf_file(self, file_path):
        """Read text from a PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            return f"Error reading PDF: {e}"
    
    def read_docx_file(self, file_path):
        """Read text from a Word document"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            return f"Error reading Word document: {e}"
    
    def read_html_file(self, file_path):
        """Read and parse HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            return "Error: Could not read HTML file with any encoding"
        except Exception as e:
            return f"Error reading HTML file: {e}"
    
    def read_document(self, file_path):
        """Read text from various document formats"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return "Error: File not found"
        
        extension = file_path.suffix.lower()
        print(f"📖 Reading {extension} file: {file_path.name}")
        
        if extension == '.txt':
            return self.read_txt_file(file_path)
        elif extension == '.pdf':
            return self.read_pdf_file(file_path)
        elif extension in ['.docx', '.doc']:
            return self.read_docx_file(file_path)
        elif extension in ['.html', '.htm']:
            return self.read_html_file(file_path)
        else:
            return f"Error: Unsupported file format '{extension}'. Supported: .txt, .pdf, .docx, .html"
    
    # ========== HTML PROCESSING ==========
    
    def has_meaningful_content_after_title(self, soup):
        """Check if there's meaningful text content after an empty title"""
        
        # Find all text-containing elements
        text_elements = soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span'])
        
        meaningful_text_found = False
        for element in text_elements:
            text = element.get_text(strip=True)
            # Skip elements that are just formatting or images
            if text and len(text) > 5 and not text.startswith('#'):
                # Check if it's not just image references or formatting
                if not re.match(r'^[#\-=\s]*$', text):
                    meaningful_text_found = True
                    break
        
        return meaningful_text_found
    
    def extract_translatable_elements(self, soup):
        """Extract translatable elements from HTML"""
        translatable_elements = []
        
        # Handle title
        title = soup.find('title')
        if title:
            title_text = title.get_text(strip=True)
            if title_text:  # Only add non-empty titles
                translatable_elements.append({
                    'element': title,
                    'original_text': title_text,
                    'type': 'title'
                })
            elif not self.has_meaningful_content_after_title(soup):
                # Remove empty title if no meaningful content after
                title.decompose()
        
        # Handle headings
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for element in soup.find_all(tag):
                text = element.get_text(strip=True)
                if text:
                    translatable_elements.append({
                        'element': element,
                        'original_text': text,
                        'type': 'heading'
                    })
        
        # Handle paragraphs
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 3:  # Skip very short paragraphs
                # Skip paragraphs that are just formatting
                if not re.match(r'^[#\-=\s]*$', text):
                    translatable_elements.append({
                        'element': p,
                        'original_text': text,
                        'type': 'paragraph'
                    })
        
        # Handle divs with text content
        for div in soup.find_all('div'):
            # Only process divs that have direct text content (not just nested elements)
            direct_text = ''.join(str(content) for content in div.contents if isinstance(content, NavigableString)).strip()
            if direct_text and len(direct_text) > 3:
                translatable_elements.append({
                    'element': div,
                    'original_text': direct_text,
                    'type': 'text'
                })
        
        return translatable_elements
    
    def translate_html_document(self, html_content: str, context: str = "") -> str:
        """Translate HTML document preserving structure"""
        
        if not self.use_azure_deepseek:
            raise TranslationFailedException("Azure AI DeepSeek not available")
        
        print(f"🌐 Translating HTML document with structure preservation...")
        
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract translatable elements
            translatable_elements = self.extract_translatable_elements(soup)
            
            if not translatable_elements:
                print("   ⚠️ No translatable content found in HTML")
                return html_content
            
            print(f"   📦 Found {len(translatable_elements)} translatable elements")
            
            # Prepare glossary terms
            glossary_terms = self.prepare_glossary_for_translation()
            
            # Group elements for batch translation (similar to paragraph chunking)
            element_chunks = self.group_elements_for_translation(translatable_elements)
            
            # Translate each chunk
            for chunk_num, chunk in enumerate(element_chunks):
                print(f"   🔄 Translating chunk {chunk_num + 1}/{len(element_chunks)}...")
                
                # Combine texts for this chunk
                combined_text = '\n'.join([elem['original_text'] for elem in chunk])
                
                # Translate the combined text - this can now raise TranslationFailedException
                translated_text = self.azure_translator.translate_with_glossary(
                    combined_text, glossary_terms, context, "paragraph"
                )
                
                # Track glossary usage
                self.track_glossary_usage(combined_text, translated_text)
                
                # Split translated text back to individual elements
                translated_parts = translated_text.split('\n')
                
                # Map translations back to elements
                for i, elem_info in enumerate(chunk):
                    if i < len(translated_parts):
                        new_text = translated_parts[i].strip()
                        if new_text:
                            # Update the element's text content
                            elem_info['element'].string = new_text
            
            # Return the modified HTML
            return str(soup)
            
        except Exception as e:
            print(f"   ❌ HTML translation error: {e}")
            raise TranslationFailedException(f"HTML translation failed: {e}")
    
    def group_elements_for_translation(self, elements, max_chunk_size=1500):
        """Group HTML elements into chunks for efficient translation"""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for element in elements:
            text_size = len(element['original_text'])
            
            if current_size + text_size > max_chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = [element]
                current_size = text_size
            else:
                current_chunk.append(element)
                current_size += text_size
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    # ========== DIRECT TRANSLATION WITH DEEPSEEK ==========
    
    def split_text_for_translation(self, text, max_chunk_size=1800):
        """Split text into optimal chunks for DeepSeek translation"""
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            para_size = len(paragraph)
            
            # If adding this paragraph would exceed limit, start new chunk
            if current_size + para_size > max_chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_size = para_size
            else:
                current_chunk.append(paragraph)
                current_size += para_size + 2
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        print(f"   📦 Split text into {len(chunks)} chunks for translation")
        return chunks
    
    def translate_document_with_deepseek(self, content: str, context: str = "", is_html: bool = False) -> str:
        """Translate entire document using Azure AI DeepSeek with glossary"""
        
        if not self.use_azure_deepseek:
            raise TranslationFailedException("Azure AI DeepSeek not available")
        
        if is_html:
            return self.translate_html_document(content, context)
        else:
            print(f"🌐 Using Azure AI DeepSeek for direct Korean→English translation...")
            
            # Prepare glossary terms
            glossary_terms = self.prepare_glossary_for_translation()
            
            # Split text into manageable chunks
            chunks = self.split_text_for_translation(content, 1800)
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                print(f"   🔄 Translating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
                
                # This can now raise TranslationFailedException
                translated_chunk = self.azure_translator.translate_with_glossary(
                    chunk, glossary_terms, context, "paragraph"
                )
                
                # Track glossary usage
                self.track_glossary_usage(chunk, translated_chunk)
                
                translated_chunks.append(translated_chunk)
            
            final_translation = '\n\n'.join(translated_chunks)
            print(f"✅ DeepSeek translation completed! Processed {len(chunks)} chunks")
            
            return final_translation
    
    # ========== FOLDER PROCESSING ==========
    
    def create_output_structure(self, source_lang: str, target_lang: str) -> Path:
        """Create organized output folder structure in application directory"""
        # Get application directory instead of input folder
        app_dir = self.get_application_directory()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder_name = f"translated_{source_lang}_to_{target_lang}_{timestamp}"
        output_folder = app_dir / output_folder_name
        
        (output_folder / "translations").mkdir(parents=True, exist_ok=True)
        (output_folder / "glossaries").mkdir(parents=True, exist_ok=True)
        (output_folder / "logs").mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Created output structure: {output_folder}")
        return output_folder
    
    def sort_documents_by_priority(self, documents: List[Dict]) -> List[Dict]:
        """Sort documents by translation priority"""
        def priority_score(doc):
            type_scores = {'.txt': 3, '.docx': 2, '.doc': 2, '.pdf': 1, '.html': 4, '.htm': 4}
            
            name_lower = doc["name"].lower()
            if any(pattern in name_lower for pattern in ['chapter', '화', 'episode', 'ch']):
                return 100 + type_scores.get(doc["type"], 0)
            
            return type_scores.get(doc["type"], 0)
        
        sorted_docs = sorted(documents, key=priority_score, reverse=True)
        
        print(f"📋 Document processing order:")
        for i, doc in enumerate(sorted_docs):
            print(f"   {i+1}. {doc['name']} ({doc['type']})")
        
        return sorted_docs
    
    def process_single_document(self, doc_path: Path, source_lang: str, target_lang: str, 
                               context: str, output_folder: Path) -> Dict:
        """Process single document with DeepSeek direct translation - supports HTML"""
        
        try:
            # Read document
            content = self.read_document(str(doc_path))
            if content.startswith("Error:"):
                return {"success": False, "error": content}
            
            char_count = len(content)
            print(f"📊 Document length: {char_count:,} characters")
            
            # Determine if this is an HTML file
            is_html = doc_path.suffix.lower() in {'.html', '.htm'}
            
            # Direct translation with Azure AI DeepSeek
            start_time = time.time()
            
            try:
                final_translation = self.translate_document_with_deepseek(content, context, is_html)
                translation_time = time.time() - start_time
                
                # Save translated document
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                if is_html:
                    # For HTML files, keep the original filename
                    output_file = output_folder / "translations" / doc_path.name
                else:
                    # For other files, add language info
                    output_file = output_folder / "translations" / f"{doc_path.stem}_{source_lang}_to_{target_lang}_{timestamp}.txt"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    # Write ONLY the translation - no metadata headers!
                    f.write(final_translation)
                
                # Update glossary usage after each file
                self.update_glossary_after_file(doc_path.name)
                
                return {
                    "success": True,
                    "file": doc_path.name,
                    "output_file": output_file.name,
                    "char_count": char_count,
                    "translation_time": translation_time,
                    "method": f"Azure AI DeepSeek {'HTML' if is_html else 'text'} translation"
                }
                
            except TranslationFailedException as e:
                return {"success": False, "error": str(e)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def ask_about_html_processing(self, html_count: int) -> bool:
        """Ask user if they want to process HTML files"""
        if html_count == 0:
            return False
        
        print(f"\n🌐 Found {html_count} HTML files.")
        print("HTML files will be translated while preserving images and structure.")
        
        choice = input("Process HTML files? (y/n) [y]: ").strip().lower()
        return choice != 'n'
    
    def process_folder(self, folder_path: str, source_lang: str, target_lang: str, 
                      context: str = "", skip_existing: bool = True) -> Dict:
        """Main method to process entire folder with DeepSeek - includes HTML support"""
        
        # Initialize translation logs
        self.translation_logs = []
        
        self.log_translation_message(f"🚀 DEEPSEEK FOLDER TRANSLATION WITH HTML SUPPORT")
        self.log_translation_message("=" * 60)
        self.log_translation_message(f"📂 Folder: {folder_path}")
        self.log_translation_message(f"🔄 Languages: {source_lang.upper()} → {target_lang.upper()}")
        self.log_translation_message(f"🧠 Method: Azure AI DeepSeek direct translation")
        self.log_translation_message(f"🌐 HTML support: Structure + image preservation")
        self.log_translation_message("=" * 60)
        
        start_time = time.time()
        
        # Step 1: Analyze folder
        analysis = self.analyze_folder(folder_path)
        if "error" in analysis:
            return analysis
        
        # Step 2: Ask about HTML processing
        process_html = self.ask_about_html_processing(len(analysis["html_files"]))
        
        # Step 3: Create output structure (now in application directory)
        output_folder = self.create_output_structure(source_lang, target_lang)
        
        # Step 4: Combine documents based on user choice
        all_documents = analysis["documents"].copy()
        if process_html:
            all_documents.extend(analysis["html_files"])
        
        # Step 5: Sort documents by priority
        sorted_documents = self.sort_documents_by_priority(all_documents)
        
        if not sorted_documents:
            return {"error": "No translatable documents found in folder"}
        
        # Step 6: Process each document
        results = {
            "processed_files": [],
            "skipped_files": [],
            "failed_files": [],
            "total_time": 0,
            "total_chars": 0,
            "output_folder": output_folder,
            "glossaries_used": list(self.glossaries.keys()),
            "method": "Azure AI DeepSeek with HTML support",
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
        self.log_translation_message(f"🔄 Processing {len(sorted_documents)} documents...")
        
        for i, doc_info in enumerate(sorted_documents):
            doc_path = doc_info["path"]
            doc_name = doc_info["name"]
            
            self.log_translation_message(f"📄 Processing file {i+1}/{len(sorted_documents)}: {doc_name}")
            self.log_translation_message("─" * 50)
            
            try:
                # Process single document
                file_result = self.process_single_document(
                    doc_path, source_lang, target_lang, context, output_folder
                )
                
                if file_result["success"]:
                    results["processed_files"].append(file_result)
                    results["total_chars"] += file_result["char_count"]
                    self.log_translation_message(f"✅ Completed: {doc_name}")
                else:
                    results["failed_files"].append({
                        "file": doc_name,
                        "error": file_result["error"]
                    })
                    self.log_translation_message(f"❌ Failed: {doc_name} - {file_result['error']}")
                
            except Exception as e:
                error_msg = str(e)
                results["failed_files"].append({
                    "file": doc_name,
                    "error": error_msg
                })
                self.log_translation_message(f"❌ Error processing {doc_name}: {error_msg}")
            
            # Progress update
            progress = (i + 1) / len(sorted_documents) * 100
            self.log_translation_message(f"📊 Overall progress: {progress:.1f}%")
        
        # Step 7: Save glossary and logs
        if self.glossaries:
            self.save_updated_glossary(output_folder)
        
        # Final time calculation
        total_time = time.time() - start_time
        results["total_time"] = total_time
        
        # Save translation logs
        self.save_translation_logs(output_folder, results)
        
        # Step 8: Final summary
        self.log_translation_message(f"🎉 FOLDER PROCESSING COMPLETED!")
        self.log_translation_message(f"✅ Successfully processed: {len(results['processed_files'])} files")
        self.log_translation_message(f"❌ Failed: {len(results['failed_files'])} files")
        if results["failed_files"]:
            self.log_translation_message(f"   Failed files: {', '.join([f['file'] for f in results['failed_files']])}")
        self.log_translation_message(f"📊 Total characters: {results['total_chars']:,}")
        self.log_translation_message(f"⏱️ Total time: {total_time:.2f} seconds")
        self.log_translation_message(f"🧠 Method: Azure AI DeepSeek with HTML support")
        self.log_translation_message(f"📄 Output: Clean files with preserved structure")
        self.log_translation_message(f"📁 Output folder: {output_folder}")
        
        return results


def main():
    """DeepSeek-Only translation interface with HTML support"""
    translator = DeepSeekOnlyTranslator()
    
    print("🚀 DeepSeek Folder Translation System - HTML + Glossary Support")
    print("=" * 60)
    print("✨ Features:")
    print("   📁 Automatic folder processing")
    print("   📚 Glossary loading with usage tracking") 
    print("   🔄 Direct Korean→English translation")
    print("   🌐 HTML support (preserves images & structure)")
    print("   🧠 Azure AI DeepSeek powered")
    print("   📄 Clean output (no metadata headers)")
    print("=" * 60)
    
    # Show current setup
    if translator.use_azure_deepseek:
        print("🎉 Azure AI DeepSeek credentials loaded and ready!")
        print("   💡 Connection will be tested when you start translating")
    else:
        print("❌ Azure AI DeepSeek not configured")
        print("   💡 Set up your credentials to enable translation")
        return
    
    while True:
        print("\n" + "─" * 60)
        print("🎯 MAIN OPTIONS:")
        print("1. 📁 Process Single Folder")
        print("2. 🔍 Analyze Folder (Preview)")
        print("3. ⚙️ View Settings")
        print("4. 🚪 Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            # Single folder processing
            print("\n📁 DEEPSEEK FOLDER PROCESSING")
            print("─" * 40)
            
            folder_path = input("Enter folder path: ").strip().strip('"')
            if not folder_path:
                continue
            
            source_lang = input("Source language (ko): ").strip().lower() or "ko"
            target_lang = input("Target language (en): ").strip().lower() or "en"
            
            context = input("Novel context (e.g., 'Fantasy light novel'): ").strip()
            
            if source_lang and target_lang:
                print(f"\n🚀 Starting DeepSeek translation...")
                results = translator.process_folder(
                    folder_path, source_lang, target_lang, context
                )
                
                if "error" not in results:
                    print(f"\n✅ Processing completed successfully!")
                    print(f"📊 Check output folder: {results['output_folder']}")
                else:
                    print(f"❌ Error: {results['error']}")
        
        elif choice == "2":
            # Analyze folder
            print("\n🔍 FOLDER ANALYSIS")
            print("─" * 25)
            
            folder_path = input("Enter folder path to analyze: ").strip().strip('"')
            if folder_path:
                analysis = translator.analyze_folder(folder_path)
                
                if "error" not in analysis:
                    print(f"\n📊 Analysis completed!")
                    print(f"💡 Text documents: {len(analysis['documents'])}")
                    print(f"🌐 HTML files: {len(analysis['html_files'])}")
                    print(f"📚 Glossary files: {len(analysis['glossaries'])}")
                else:
                    print(f"❌ {analysis['error']}")
        
        elif choice == "3":
            # View settings
            print("\n⚙️ CURRENT SETTINGS")
            print("─" * 25)
            
            print(f"Current settings:")
            print(f"   🧠 Azure AI DeepSeek: {'ENABLED' if translator.use_azure_deepseek else 'DISABLED'}")
            print(f"   📄 Output format: Clean text (no metadata)")
            print(f"   📁 Output location: Application directory")
            print(f"   🌐 HTML support: ENABLED")
            print(f"   📚 Glossary system: Manual loading")
            print(f"   🔄 Translation failure: Proper error handling")
            
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    # Check if BeautifulSoup is available
    try:
        from bs4 import BeautifulSoup
        main()
    except ImportError:
        print("❌ BeautifulSoup4 is required for HTML support!")
        print("Install it with: pip install beautifulsoup4")
        print("Then run the translator again.")