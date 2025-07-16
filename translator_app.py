import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import zipfile
import tempfile
from pathlib import Path
import shutil
from datetime import datetime
import webbrowser
import time

# Import your existing translator
from ultimateTranslator import DeepSeekOnlyTranslator

# Set appearance mode and theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TranslatorApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🌐 Ultimate Korean Translator")
        self.root.geometry("1200x800")
        self.root.minsize(750, 550)
        
        # Initialize translator
        self.translator = DeepSeekOnlyTranslator()
        self.uploaded_files = []
        self.glossary_files = []
        self.translation_results = None
        self.edit_entries = {}  # For term editing
        
        # Create the UI
        self.setup_ui()
        
        # Enable mouse wheel scrolling
        self.bind_mousewheel_to_scrollframes()
        
    def setup_ui(self):
        """Setup the main UI"""
        # Configure grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
        
    def create_sidebar(self):
        """Create the sidebar with settings"""
        # Main sidebar container with fixed width but scrollable content
        self.sidebar_container = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        self.sidebar_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_container.grid_propagate(False)  # Maintain fixed width
        
        # Scrollable frame inside the sidebar
        self.sidebar_frame = ctk.CTkScrollableFrame(self.sidebar_container, width=260)
        self.sidebar_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Logo and title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🌐 Ultimate Translator", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.logo_label.pack(pady=(10, 5))
        
        # Status indicator
        status_text = "🎉 Azure DeepSeek Ready!" if self.translator.use_azure_deepseek else "❌ Azure DeepSeek Not Available"
        status_color = "green" if self.translator.use_azure_deepseek else "red"
        
        self.status_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text=status_text,
            text_color=status_color,
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=(0, 15))
        
        # Language settings
        self.lang_frame = ctk.CTkFrame(self.sidebar_frame)
        self.lang_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(self.lang_frame, text="🔄 Translation Settings", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        ctk.CTkLabel(self.lang_frame, text="Source Language:", font=ctk.CTkFont(size=12)).pack(pady=(8,2))
        self.source_lang = ctk.CTkOptionMenu(self.lang_frame, values=["ko", "en"], width=120)
        self.source_lang.set("ko")
        self.source_lang.pack(pady=3)
        
        ctk.CTkLabel(self.lang_frame, text="Target Language:", font=ctk.CTkFont(size=12)).pack(pady=(8,2))
        self.target_lang = ctk.CTkOptionMenu(self.lang_frame, values=["en", "ko"], width=120)
        self.target_lang.set("en")
        self.target_lang.pack(pady=3)
        
        # Context input
        ctk.CTkLabel(self.lang_frame, text="Context (Optional):", font=ctk.CTkFont(size=12)).pack(pady=(8,2))
        self.context_entry = ctk.CTkTextbox(self.lang_frame, height=50)
        self.context_entry.pack(pady=3, padx=8, fill="x")
        self.context_entry.insert("0.0", "Fantasy light novel")
        
        # File info
        self.file_info_frame = ctk.CTkFrame(self.sidebar_frame)
        self.file_info_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(self.file_info_frame, text="📁 Files Ready", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.files_label = ctk.CTkLabel(self.file_info_frame, text="Documents: 0", font=ctk.CTkFont(size=12))
        self.files_label.pack(pady=2)
        
        self.glossary_label = ctk.CTkLabel(self.file_info_frame, text="Glossaries: 0", font=ctk.CTkFont(size=12))
        self.glossary_label.pack(pady=2)
        
        # Features info
        features_frame = ctk.CTkFrame(self.sidebar_frame)
        features_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(features_frame, text="✨ Features", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        features_text = """• Bulk file processing
• Manual glossary loading
• HTML support
• Multiple formats
• AI-powered translation
• Proper error handling"""
        
        ctk.CTkLabel(features_frame, text=features_text, justify="left", font=ctk.CTkFont(size=11)).pack(pady=3, padx=8)
        
        # Theme switcher
        theme_frame = ctk.CTkFrame(self.sidebar_frame)
        theme_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(theme_frame, text="🎨 Appearance", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            theme_frame, 
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
            width=120
        )
        self.appearance_mode_optionemenu.pack(pady=3)
        self.appearance_mode_optionemenu.set("Dark")
        
    def create_main_content(self):
        """Create the main content area with tabs"""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Korean ↔ English AI Translator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=20)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self.main_frame, width=250)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Add tabs
        self.tabview.add("📁 Files")
        self.tabview.add("🚀 Translate")
        self.tabview.add("📊 Results")
        self.tabview.add("📚 Glossaries")
        self.tabview.add("📋 About")  # Renamed from Settings
        
        # Setup each tab
        self.setup_files_tab()
        self.setup_translate_tab()
        self.setup_results_tab()
        self.setup_glossaries_tab()
        self.setup_about_tab()  # Renamed from settings
        
    def setup_files_tab(self):
        """Setup the files tab"""
        files_tab = self.tabview.tab("📁 Files")
        
        # Create scrollable frame for the entire tab
        scrollable_frame = ctk.CTkScrollableFrame(files_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        scrollable_frame.configure(label_text="📁 Files & Glossaries")
        
        # Documents section
        docs_frame = ctk.CTkFrame(scrollable_frame)
        docs_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(docs_frame, text="📄 Documents to Translate", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # File selection buttons
        button_frame = ctk.CTkFrame(docs_frame)
        button_frame.pack(pady=10)
        
        self.select_files_btn = ctk.CTkButton(
            button_frame, 
            text="📂 Select Files",
            command=self.select_files,
            width=150
        )
        self.select_files_btn.pack(side="left", padx=5)
        
        self.select_folder_btn = ctk.CTkButton(
            button_frame, 
            text="📁 Select Folder",
            command=self.select_folder,
            width=150
        )
        self.select_folder_btn.pack(side="left", padx=5)
        
        self.clear_files_btn = ctk.CTkButton(
            button_frame, 
            text="🗑️ Clear",
            command=self.clear_files,
            width=100,
            fg_color="red",
            hover_color="darkred"
        )
        self.clear_files_btn.pack(side="left", padx=5)
        
        # Files listbox
        self.files_listbox = ctk.CTkTextbox(docs_frame, height=180)
        self.files_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Processing Options
        options_frame = ctk.CTkFrame(scrollable_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(options_frame, text="📋 Processing Options", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # File type options
        filetype_frame = ctk.CTkFrame(options_frame)
        filetype_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(filetype_frame, text="File Types to Process:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=2)
        
        # Checkboxes for file types
        checkbox_container = ctk.CTkFrame(filetype_frame)
        checkbox_container.pack(fill="x", padx=5, pady=5)
        
        self.process_txt = ctk.CTkCheckBox(checkbox_container, text="📄 Text files (.txt)", onvalue=True, offvalue=False)
        self.process_txt.pack(anchor="w", padx=5, pady=2)
        self.process_txt.select()
        
        self.process_pdf = ctk.CTkCheckBox(checkbox_container, text="📕 PDF files (.pdf)", onvalue=True, offvalue=False)
        self.process_pdf.pack(anchor="w", padx=5, pady=2)
        self.process_pdf.select()
        
        self.process_docx = ctk.CTkCheckBox(checkbox_container, text="📘 Word docs (.docx/.doc)", onvalue=True, offvalue=False)
        self.process_docx.pack(anchor="w", padx=5, pady=2)
        self.process_docx.select()
        
        self.process_html = ctk.CTkCheckBox(checkbox_container, text="🌐 HTML files (.html/.htm) - Preserves structure & images", onvalue=True, offvalue=False)
        self.process_html.pack(anchor="w", padx=5, pady=2)
        self.process_txt.configure(command=self.update_file_counts)
        self.process_pdf.configure(command=self.update_file_counts)
        self.process_docx.configure(command=self.update_file_counts)
        self.process_html.configure(command=self.update_file_counts)
        
        # Additional processing options
        processing_frame = ctk.CTkFrame(options_frame)
        processing_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(processing_frame, text="Processing Behavior:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=2)
        
        self.skip_existing = ctk.CTkCheckBox(processing_frame, text="⏭️ Skip files that already exist in output", onvalue=True, offvalue=False)
        self.skip_existing.pack(anchor="w", padx=5, pady=2)
        self.skip_existing.select()
        
        self.clean_output = ctk.CTkCheckBox(processing_frame, text="📄 Clean output mode (no metadata headers)", onvalue=True, offvalue=False)
        self.clean_output.pack(anchor="w", padx=5, pady=2)
        self.clean_output.select()
        
        # Glossaries section
        glossary_frame = ctk.CTkFrame(scrollable_frame)
        glossary_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(glossary_frame, text="📚 Glossary Files (Optional)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.select_glossaries_btn = ctk.CTkButton(
            glossary_frame, 
            text="📋 Select CSV Glossaries",
            command=self.select_glossaries,
            width=200
        )
        self.select_glossaries_btn.pack(pady=10)
        
        self.glossaries_listbox = ctk.CTkTextbox(glossary_frame, height=100)
        self.glossaries_listbox.pack(fill="x", padx=10, pady=10)
        
    def setup_translate_tab(self):
        """Setup the translate tab"""
        translate_tab = self.tabview.tab("🚀 Translate")
        
        # Create scrollable frame for the entire tab
        scrollable_frame = ctk.CTkScrollableFrame(translate_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        scrollable_frame.configure(label_text="🚀 Translation Controls")
        
        # Main translate frame
        main_frame = ctk.CTkFrame(scrollable_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(main_frame, text="🚀 Start Translation", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Summary frame with detailed pre-flight info
        summary_frame = ctk.CTkFrame(main_frame)
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(summary_frame, text="📋 Pre-Flight Summary", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.summary_label = ctk.CTkLabel(summary_frame, text="No files selected", wraplength=600)
        self.summary_label.pack(pady=5)
        
        # Detailed processing plan
        self.processing_plan_label = ctk.CTkLabel(summary_frame, text="", font=ctk.CTkFont(size=11), wraplength=600)
        self.processing_plan_label.pack(pady=2)
        
        # Progress section
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=20, pady=20)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready to translate")
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        
        # Translate button
        self.translate_btn = ctk.CTkButton(
            main_frame,
            text="🚀 START TRANSLATION",
            command=self.start_translation,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=300
        )
        self.translate_btn.pack(pady=30)
        
        # Log area
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(log_frame, text="📋 Translation Log", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.log_textbox = ctk.CTkTextbox(log_frame, height=200)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
    def setup_results_tab(self):
        """Setup the results tab"""
        results_tab = self.tabview.tab("📊 Results")
        
        # Create scrollable frame for the entire tab
        scrollable_frame = ctk.CTkScrollableFrame(results_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        scrollable_frame.configure(label_text="📊 Translation Results")
        
        # Results frame
        results_frame = ctk.CTkFrame(scrollable_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(results_frame, text="📊 Translation Results", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Stats frame
        self.stats_frame = ctk.CTkFrame(results_frame)
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_label = ctk.CTkLabel(self.stats_frame, text="No translation results yet")
        self.stats_label.pack(pady=20)
        
        # Open folder section
        open_frame = ctk.CTkFrame(results_frame)
        open_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(open_frame, text="📁 Output Location", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.open_folder_btn = ctk.CTkButton(
            open_frame,
            text="📁 Open Results Folder",
            command=self.open_results_folder,
            state="disabled"
        )
        self.open_folder_btn.pack(pady=10)
        
        # Results details
        self.results_textbox = ctk.CTkTextbox(results_frame, height=300)
        self.results_textbox.pack(fill="both", expand=True, padx=20, pady=10)
        
    def setup_about_tab(self):
        """Setup the about tab (renamed from settings)"""
        about_tab = self.tabview.tab("📋 About")
        
        # Create scrollable frame for the entire tab
        scrollable_frame = ctk.CTkScrollableFrame(about_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        scrollable_frame.configure(label_text="📋 About Ultimate Korean Translator")
        
        # About section
        about_frame = ctk.CTkFrame(scrollable_frame)
        about_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(about_frame, text="📋 About Ultimate Korean Translator", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Version and status
        version_frame = ctk.CTkFrame(about_frame)
        version_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(version_frame, text="Version Information", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Status indicators
        azure_status = "🟢 ENABLED" if self.translator.use_azure_deepseek else "🔴 DISABLED"
        
        about_text = f"""🌐 Ultimate Korean Translator v2.0
🧠 Azure AI DeepSeek: {azure_status}
📄 Output: Application directory
🌐 HTML support: Structure + image preservation
📚 Glossary system: Manual loading with usage tracking
🔄 Translation: Proper failure handling
⚙️ Output format: Clean text (no metadata)"""
        
        self.about_label = ctk.CTkLabel(version_frame, text=about_text, justify="left")
        self.about_label.pack(pady=10, padx=20)
        
        # Features section
        features_frame = ctk.CTkFrame(about_frame)
        features_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(features_frame, text="✨ Features", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        # Feature buttons
        feature_button_frame = ctk.CTkFrame(features_frame)
        feature_button_frame.pack(fill="x", padx=20, pady=10)
        
        # Azure Configuration
        self.azure_config_btn = ctk.CTkButton(
            feature_button_frame,
            text="🔧 Configure Azure AI DeepSeek",
            command=self.configure_azure_credentials,
            width=300,
            fg_color="blue",
            hover_color="darkblue"
        )
        self.azure_config_btn.pack(pady=5)
        
        # Azure DeepSeek Status
        self.azure_status_btn = ctk.CTkButton(
            feature_button_frame,
            text="🔍 View Azure AI DeepSeek Status",
            command=self.view_azure_status,
            width=300
        )
        self.azure_status_btn.pack(pady=5)
        
        # View Supported File Types
        self.file_types_btn = ctk.CTkButton(
            feature_button_frame,
            text="📄 View Supported File Types",
            command=self.view_supported_file_types,
            width=300
        )
        self.file_types_btn.pack(pady=5)
        
        # Application info
        info_frame = ctk.CTkFrame(features_frame)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(info_frame, text="ℹ️ Application Information", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        info_text = """Key Features:
• Azure AI DeepSeek integration for direct translation
• HTML support with structure preservation  
• Manual glossary loading and usage tracking
• Clean output mode (no metadata headers)
• Multi-format support (.txt, .pdf, .docx, .html)
• Proper error handling and failure reporting
• Output saved to application directory

Translation Process:
• Files are processed with up to 6 retry attempts
• Failed translations are properly reported
• Glossary terms are tracked: "korean" → "english"
• Output is clean without metadata headers"""
        
        ctk.CTkLabel(info_frame, text=info_text, justify="left", font=ctk.CTkFont(size=11)).pack(pady=5, padx=10)
        
    def setup_glossaries_tab(self):
        """Setup the glossaries management tab"""
        glossaries_tab = self.tabview.tab("📚 Glossaries")
        
        # Create scrollable frame for the entire tab
        scrollable_frame = ctk.CTkScrollableFrame(glossaries_tab)
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        scrollable_frame.configure(label_text="📚 Glossary Management & Editing")
        
        # Info section
        info_frame = ctk.CTkFrame(scrollable_frame)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text="📚 Glossary Manager", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        info_text = """Glossaries help maintain consistent character names and terminology.

Required CSV format:
• type: character, location, skill, etc.
• raw_name: Korean term  
• translated_name: English translation
• gender: male/female (optional)"""
        
        ctk.CTkLabel(info_frame, text=info_text, justify="left", font=ctk.CTkFont(size=12)).pack(pady=5, padx=15)
        
        # Management buttons
        button_frame = ctk.CTkFrame(info_frame)
        button_frame.pack(fill="x", padx=15, pady=10)
        
        # Row 1 buttons
        button_row1 = ctk.CTkFrame(button_frame)
        button_row1.pack(fill="x", pady=2)
        
        # Load glossary button
        self.load_glossary_btn = ctk.CTkButton(
            button_row1,
            text="📂 Load Glossary CSV",
            command=self.load_glossary_file,
            width=200
        )
        self.load_glossary_btn.pack(side="left", padx=3)
        
        # Export current glossary
        self.export_glossary_btn = ctk.CTkButton(
            button_row1,
            text="💾 Export Active",
            command=self.export_active_glossary,
            width=180
        )
        self.export_glossary_btn.pack(side="right", padx=3)
        
        # Row 2 buttons
        button_row2 = ctk.CTkFrame(button_frame)
        button_row2.pack(fill="x", pady=2)
        
        # Edit terms button
        self.edit_terms_btn = ctk.CTkButton(
            button_row2,
            text="✏️ Edit Terms",
            command=self.open_term_editor,
            width=160,
            fg_color="orange",
            hover_color="darkorange"
        )
        self.edit_terms_btn.pack(side="left", padx=3)
        
        # Add new term button
        self.add_term_btn = ctk.CTkButton(
            button_row2,
            text="➕ Add Term",
            command=self.add_new_term,
            width=160,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.add_term_btn.pack(side="left", padx=3)
        
        # Clear glossaries button
        self.clear_glossaries_btn = ctk.CTkButton(
            button_row2,
            text="🗑️ Clear All",
            command=self.clear_glossaries,
            width=140,
            fg_color="red",
            hover_color="darkred"
        )
        self.clear_glossaries_btn.pack(side="right", padx=3)
        
        # Currently loaded glossaries
        loaded_frame = ctk.CTkFrame(scrollable_frame)
        loaded_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(loaded_frame, text="📋 Currently Loaded Glossaries", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Glossary selection dropdown
        selection_frame = ctk.CTkFrame(loaded_frame)
        selection_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(selection_frame, text="Active Glossary:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        
        self.glossary_selector = ctk.CTkOptionMenu(
            selection_frame,
            values=["None"],
            command=self.on_glossary_selected,
            width=200
        )
        self.glossary_selector.pack(side="left", padx=10)
        
        # Glossary content display
        self.glossaries_display = ctk.CTkTextbox(loaded_frame, height=250)
        self.glossaries_display.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Statistics frame
        stats_frame = ctk.CTkFrame(scrollable_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(stats_frame, text="📊 Glossary Statistics", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.stats_display = ctk.CTkTextbox(stats_frame, height=80)
        self.stats_display.pack(fill="x", padx=15, pady=(0, 10))
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_frame = ctk.CTkFrame(self.root, height=30)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        
        self.status_text = ctk.CTkLabel(self.status_frame, text="Ready")
        self.status_text.pack(side="left", padx=10, pady=5)
    
    def bind_mousewheel_to_scrollframes(self):
        """Enable mouse wheel scrolling for all scroll frames including sidebar"""
        def _on_mousewheel(event):
            # Get the widget under mouse cursor
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            
            # Find the scrollable frame parent
            while widget:
                if isinstance(widget, ctk.CTkScrollableFrame):
                    # Scroll the frame with faster speed (multiplied by 3)
                    widget._parent_canvas.yview_scroll(int(-3 * (event.delta / 120)), "units")
                    break
                widget = widget.master
        
        # Bind mousewheel to the main window and all scrollable areas
        self.root.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
        self.root.bind_all("<Button-4>", lambda e: _on_mousewheel(type('obj', (object,), {'delta': 360, 'widget': e.widget, 'x_root': e.x_root, 'y_root': e.y_root})()))  # Linux
        self.root.bind_all("<Button-5>", lambda e: _on_mousewheel(type('obj', (object,), {'delta': -360, 'widget': e.widget, 'x_root': e.x_root, 'y_root': e.y_root})()))  # Linux
        
    # Event handlers
    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Change appearance mode"""
        ctk.set_appearance_mode(new_appearance_mode)
        
    def select_files(self):
        """Select individual files"""
        filetypes = [
            ("All supported", "*.txt;*.pdf;*.docx;*.doc;*.html;*.htm"),
            ("Text files", "*.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx;*.doc"),
            ("HTML files", "*.html;*.htm"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select files to translate",
            filetypes=filetypes
        )
        
        if files:
            self.uploaded_files.extend(files)
            self.update_files_display()
            self.update_file_counts()
            
    def select_folder(self):
        """Select entire folder"""
        folder = filedialog.askdirectory(title="Select folder to translate")
        
        if folder:
            # Find all supported files in folder
            supported_extensions = {'.txt', '.pdf', '.docx', '.doc', '.html', '.htm'}
            folder_path = Path(folder)
            
            for file_path in folder_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    self.uploaded_files.append(str(file_path))
            
            self.update_files_display()
            self.update_file_counts()
            
    def select_glossaries(self):
        """Select glossary CSV files"""
        files = filedialog.askopenfilenames(
            title="Select glossary CSV files",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if files:
            self.glossary_files.extend(files)
            self.update_glossaries_display_files()
            self.update_file_counts()
            
    def clear_files(self):
        """Clear all selected files"""
        self.uploaded_files.clear()
        self.glossary_files.clear()
        self.update_files_display()
        self.update_glossaries_display_files()
        self.update_file_counts()
        # Update glossary displays
        try:
            self.update_glossary_selector()
            self.update_glossaries_display()
            self.update_glossary_stats()
        except AttributeError:
            pass
        
    def update_files_display(self):
        """Update files display with processing indicators"""
        self.files_listbox.delete("0.0", tk.END)
        
        if self.uploaded_files:
            text = f"📄 {len(self.uploaded_files)} files selected:\n\n"
            
            # Group files by type and show processing status
            processed_count = 0
            for i, file_path in enumerate(self.uploaded_files, 1):
                filename = Path(file_path).name
                ext = Path(file_path).suffix.lower()
                size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
                
                # Determine if this file will be processed
                will_process = False
                if hasattr(self, 'process_txt') and ext == '.txt' and self.process_txt.get():
                    will_process = True
                elif hasattr(self, 'process_pdf') and ext == '.pdf' and self.process_pdf.get():
                    will_process = True
                elif hasattr(self, 'process_docx') and ext in {'.docx', '.doc'} and self.process_docx.get():
                    will_process = True
                elif hasattr(self, 'process_html') and ext in {'.html', '.htm'} and self.process_html.get():
                    will_process = True
                
                # Add visual indicator
                if will_process:
                    status_icon = "✅"
                    processed_count += 1
                else:
                    status_icon = "⏸️"
                
                text += f"{status_icon} {i}. {filename} ({size:,} bytes)\n"
            
            if processed_count < len(self.uploaded_files):
                text += f"\n💡 {processed_count}/{len(self.uploaded_files)} files will be processed based on your file type selections."
        else:
            text = """No files selected.

📋 How to use:
1. Select files or folders using the buttons above
2. Choose which file types to process using the checkboxes below
3. Configure other processing options as needed

Supported formats:
• .txt (Text files)
• .pdf (PDF documents) 
• .docx/.doc (Word documents)
• .html/.htm (Web pages with structure preservation)"""
        
        self.files_listbox.insert("0.0", text)
        
    def update_glossaries_display_files(self):
        """Update glossaries file display"""
        self.glossaries_listbox.delete("0.0", tk.END)
        
        if self.glossary_files:
            text = f"📚 {len(self.glossary_files)} glossaries selected:\n\n"
            for i, file_path in enumerate(self.glossary_files, 1):
                filename = Path(file_path).name
                text += f"{i}. {filename}\n"
        else:
            text = "No glossary files selected.\n\nUpload CSV files with character names and terminology for consistent translations."
        
        self.glossaries_listbox.insert("0.0", text)
        
    def update_file_counts(self):
        """Update file count displays"""
        self.files_label.configure(text=f"Documents: {len(self.uploaded_files)}")
        self.glossary_label.configure(text=f"Glossaries: {len(self.glossary_files)}")
        
        # Update summary with processing options
        if self.uploaded_files:
            total_size = sum(Path(f).stat().st_size for f in self.uploaded_files if Path(f).exists())
            
            # Count files by type
            file_counts = {}
            for file_path in self.uploaded_files:
                ext = Path(file_path).suffix.lower()
                file_counts[ext] = file_counts.get(ext, 0) + 1
            
            # Build summary based on selected processing options
            will_process = []
            if hasattr(self, 'process_txt') and self.process_txt.get():
                txt_count = file_counts.get('.txt', 0)
                if txt_count > 0:
                    will_process.append(f"{txt_count} text")
            if hasattr(self, 'process_pdf') and self.process_pdf.get():
                pdf_count = file_counts.get('.pdf', 0)
                if pdf_count > 0:
                    will_process.append(f"{pdf_count} PDF")
            if hasattr(self, 'process_docx') and self.process_docx.get():
                docx_count = file_counts.get('.docx', 0) + file_counts.get('.doc', 0)
                if docx_count > 0:
                    will_process.append(f"{docx_count} Word")
            if hasattr(self, 'process_html') and self.process_html.get():
                html_count = file_counts.get('.html', 0) + file_counts.get('.htm', 0)
                if html_count > 0:
                    will_process.append(f"{html_count} HTML")
            
            if will_process:
                summary = f"Ready to translate: {', '.join(will_process)} files ({total_size:,} bytes)"
                if self.glossary_files:
                    summary += f"\nWith {len(self.glossary_files)} glossaries"
            else:
                summary = "No file types selected for processing"
                
            # Build processing plan details
            plan_details = []
            if hasattr(self, 'skip_existing') and self.skip_existing.get():
                plan_details.append("⏭️ Skip existing files")
            if hasattr(self, 'clean_output') and self.clean_output.get():
                plan_details.append("📄 Clean output mode")
            if hasattr(self, 'process_html') and self.process_html.get() and file_counts.get('.html', 0) + file_counts.get('.htm', 0) > 0:
                plan_details.append("🌐 Preserve HTML structure")
                
            plan_text = "Processing: " + " • ".join(plan_details) if plan_details else ""
        else:
            summary = "No files selected"
            plan_text = ""
            
        self.summary_label.configure(text=summary)
        if hasattr(self, 'processing_plan_label'):
            self.processing_plan_label.configure(text=plan_text)
    
    def update_glossaries_display(self):
        """Update loaded glossaries display in the Glossaries tab"""
        self.glossaries_display.delete("0.0", tk.END)
        
        if self.translator.glossaries:
            if self.translator.active_glossary and self.translator.active_glossary in self.translator.glossaries:
                # Show detailed view of active glossary
                glossary = self.translator.glossaries[self.translator.active_glossary]
                text = f"📖 {self.translator.active_glossary} ({len(glossary)} terms)\n\n"
                
                # Group terms by type
                terms_by_type = {}
                for korean, data in glossary.items():
                    term_type = data.get('type', 'unknown')
                    if term_type not in terms_by_type:
                        terms_by_type[term_type] = []
                    terms_by_type[term_type].append((korean, data))
                
                # Display terms organized by type
                for term_type, terms in sorted(terms_by_type.items()):
                    text += f"🏷️ {term_type.upper()} ({len(terms)} terms):\n"
                    for korean, data in terms:
                        gender = f" ({data.get('gender', '')})" if data.get('gender') else ""
                        usage = data.get('usage_count', 0)
                        usage_info = f" [Used: {usage}x]" if usage > 0 else ""
                        text += f"   • {korean} → {data['translation']}{gender}{usage_info}\n"
                    text += "\n"
            else:
                # Show overview of all glossaries
                text = f"📚 All Loaded Glossaries ({len(self.translator.glossaries)} total):\n\n"
                for name, glossary in self.translator.glossaries.items():
                    text += f"📖 {name} ({len(glossary)} terms)\n"
                    for i, (korean, data) in enumerate(list(glossary.items())[:8]):
                        text += f"   • {korean} → {data['translation']} ({data['type']})\n"
                    if len(glossary) > 8:
                        text += f"   ... and {len(glossary) - 8} more terms\n"
                    text += "\n"
                text += "💡 Select a glossary above to view ALL terms and edit them."
        else:
            text = """No glossaries loaded yet.

📋 How to add glossaries:
1. Click 'Load Glossary CSV' to upload existing files
2. Click 'Download Sample' to get a template
3. Create CSV files with the required format

✏️ How to edit glossaries:
1. Load or select an active glossary
2. Click 'Edit Terms' to modify existing entries
3. Click 'Add Term' to add new translations
4. Click 'Export Active' to save your changes"""
            
        self.glossaries_display.insert("0.0", text)
        
    def log_message(self, message):
        """Add message to log"""
        self.log_textbox.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_textbox.see(tk.END)
        self.root.update()
        
    def start_translation(self):
        """Start the translation process"""
        if not self.uploaded_files:
            messagebox.showwarning("No Files", "Please select files to translate first!")
            return
        
        # Check if any file types are selected
        if not any([self.process_txt.get(), self.process_pdf.get(), self.process_docx.get(), self.process_html.get()]):
            messagebox.showwarning("No File Types", "Please select at least one file type to process in the Files tab!")
            return
            
        if not self.translator.use_azure_deepseek:
            messagebox.showerror("Service Unavailable", "Azure AI DeepSeek is not available. Check your configuration.")
            return
            
        # Disable translate button
        self.translate_btn.configure(state="disabled", text="🔄 Translating...")
        self.progress_bar.set(0)
        
        # Start translation in separate thread
        translation_thread = threading.Thread(target=self.run_translation)
        translation_thread.daemon = True
        translation_thread.start()
        
    def run_translation(self):
        """Run translation in background thread with GUI settings"""
        try:
            self.log_message("🚀 Starting GUI-controlled translation process...")
            self.progress_label.configure(text="Analyzing files and settings...")
            self.progress_bar.set(0.1)
            
            # Filter files based on GUI checkboxes
            filtered_files = self.filter_files_by_gui_settings()
            
            if not filtered_files:
                self.log_message("❌ No files match the selected processing options")
                messagebox.showwarning("No Files", "No files match your selected file type options!")
                return
            
            self.log_message(f"📁 Processing {len(filtered_files)} files based on your settings...")
            
            # Create temporary folder
            temp_dir = tempfile.mkdtemp()
            
            # Copy filtered files to temp directory
            for file_path in filtered_files:
                if Path(file_path).exists():
                    shutil.copy2(file_path, temp_dir)
                    
            # Copy glossary files if uploaded
            if self.glossary_files:
                for glossary_path in self.glossary_files:
                    if Path(glossary_path).exists():
                        shutil.copy2(glossary_path, temp_dir)
                        
            self.progress_bar.set(0.2)
            
            # Load glossaries if any were uploaded
            if self.glossary_files:
                self.log_message("📚 Loading glossaries...")
                for glossary_path in self.glossary_files:
                    try:
                        result = self.translator.load_glossary_csv(str(glossary_path))
                        if "successfully" in result:
                            glossary_name = Path(glossary_path).stem
                            self.translator.set_active_glossary(glossary_name)
                            self.log_message(f"✅ Loaded glossary: {glossary_name}")
                        else:
                            self.log_message(f"❌ Failed to load glossary: {result}")
                    except Exception as e:
                        self.log_message(f"❌ Error loading glossary: {e}")
            
            # Get settings from GUI
            source_lang = self.source_lang.get()
            target_lang = self.target_lang.get()
            context = self.context_entry.get("0.0", tk.END).strip()
            
            self.log_message(f"🔄 Translating {source_lang} → {target_lang}")
            if context:
                self.log_message(f"📝 Context: {context}")
            
            # Log processing options
            options_used = []
            if self.skip_existing.get():
                options_used.append("Skip existing files")
            if self.clean_output.get():
                options_used.append("Clean output mode")
            if self.process_html.get():
                html_files = [f for f in filtered_files if Path(f).suffix.lower() in {'.html', '.htm'}]
                if html_files:
                    options_used.append(f"HTML structure preservation ({len(html_files)} files)")
                    
            if options_used:
                self.log_message(f"⚙️ Options: {', '.join(options_used)}")
                
            self.progress_label.configure(text="Running AI translation...")
            self.progress_bar.set(0.3)
            
            # Run translation using our custom method
            results = self.run_gui_translation(
                temp_dir, source_lang, target_lang, context, filtered_files
            )
            
            # Save glossary and logs (new functionality)
            if results and "error" not in results:
                try:
                    # Save updated glossary with usage stats
                    if self.translator.glossaries:
                        self.translator.save_updated_glossary(results['output_folder'])
                        self.log_message("💾 Glossary saved with usage statistics")
                    
                    # Save translation logs
                    self.translator.save_translation_logs(results['output_folder'], results)
                    self.log_message("📋 Translation logs saved")
                    
                except Exception as e:
                    self.log_message(f"⚠️ Error saving files: {e}")
            
            self.progress_bar.set(0.9)
            
            # Store results
            self.translation_results = results
            
            if "error" not in results:
                self.log_message("✅ Translation completed successfully!")
                self.progress_label.configure(text="Translation completed!")
                self.progress_bar.set(1.0)
                
                # Update results display
                self.update_results_display()
                
                # Update glossary displays if any were loaded during translation
                try:
                    self.update_glossary_selector()
                    self.update_glossaries_display()
                    self.update_glossary_stats()
                except AttributeError:
                    pass
                
                # Switch to results tab
                self.tabview.set("📊 Results")
                
                # Show success message with failed files if any
                success_msg = f"Translation completed!\n\nProcessed: {len(results['processed_files'])} files"
                if results['failed_files']:
                    failed_names = [f['file'] for f in results['failed_files']]
                    success_msg += f"\n\nFailed files: {', '.join(failed_names)}"
                success_msg += f"\nTime: {results['total_time']:.1f}s"
                
                messagebox.showinfo("Success", success_msg)
                
            else:
                self.log_message(f"❌ Translation failed: {results['error']}")
                messagebox.showerror("Translation Error", f"Translation failed:\n{results['error']}")
                
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            
        finally:
            # Re-enable button
            self.translate_btn.configure(state="normal", text="🚀 START TRANSLATION")
            self.progress_label.configure(text="Ready")
    
    def filter_files_by_gui_settings(self):
        """Filter uploaded files based on GUI checkbox settings"""
        filtered_files = []
        
        for file_path in self.uploaded_files:
            ext = Path(file_path).suffix.lower()
            
            # Check each file type against GUI settings
            if ext == '.txt' and self.process_txt.get():
                filtered_files.append(file_path)
            elif ext == '.pdf' and self.process_pdf.get():
                filtered_files.append(file_path)
            elif ext in {'.docx', '.doc'} and self.process_docx.get():
                filtered_files.append(file_path)
            elif ext in {'.html', '.htm'} and self.process_html.get():
                filtered_files.append(file_path)
        
        return filtered_files
    
    def run_gui_translation(self, temp_dir, source_lang, target_lang, context, original_files):
        """Run translation with GUI settings"""
        start_time = time.time()
        
        try:
            # Create output structure (now in application directory)
            output_folder = self.translator.create_output_structure(source_lang, target_lang)
            
            # Filter documents based on GUI settings
            all_files = []
            for file_path in original_files:
                if Path(file_path).exists():
                    ext = Path(file_path).suffix.lower()
                    all_files.append({
                        "path": Path(file_path),
                        "name": Path(file_path).name,
                        "type": ext,
                        "size": Path(file_path).stat().st_size
                    })
            
            # Sort documents by priority
            sorted_documents = self.translator.sort_documents_by_priority(all_files)
            
            if not sorted_documents:
                return {"error": "No documents to process"}
            
            self.log_message(f"📋 Processing {len(sorted_documents)} documents...")
            
            # Process each document
            results = {
                "processed_files": [],
                "skipped_files": [],
                "failed_files": [],
                "total_time": 0,
                "total_chars": 0,
                "output_folder": output_folder,
                "glossaries_used": list(self.translator.glossaries.keys()),
                "method": "Azure AI DeepSeek with GUI integration",
                "source_lang": source_lang,
                "target_lang": target_lang
            }
            
            for i, doc_info in enumerate(sorted_documents):
                doc_path = doc_info["path"]
                doc_name = doc_info["name"]
                
                self.log_message(f"📄 Processing {i+1}/{len(sorted_documents)}: {doc_name}")
                
                try:
                    # Process single document
                    file_result = self.translator.process_single_document(
                        doc_path, source_lang, target_lang, context, output_folder
                    )
                    
                    if file_result["success"]:
                        results["processed_files"].append(file_result)
                        results["total_chars"] += file_result["char_count"]
                        self.log_message(f"✅ Completed: {doc_name}")
                    else:
                        results["failed_files"].append({
                            "file": doc_name,
                            "error": file_result["error"]
                        })
                        self.log_message(f"❌ Failed: {doc_name} - {file_result['error']}")
                    
                except Exception as e:
                    error_msg = str(e)
                    results["failed_files"].append({
                        "file": doc_name,
                        "error": error_msg
                    })
                    self.log_message(f"❌ Error processing {doc_name}: {error_msg}")
                
                # Update progress
                progress = 0.3 + (0.6 * (i + 1) / len(sorted_documents))
                self.progress_bar.set(progress)
            
            # Final summary
            total_time = time.time() - start_time
            results["total_time"] = total_time
            
            self.log_message(f"🎉 Processing completed!")
            self.log_message(f"✅ Successfully processed: {len(results['processed_files'])} files")
            if results['failed_files']:
                self.log_message(f"❌ Failed: {len(results['failed_files'])} files")
                for failed in results['failed_files']:
                    self.log_message(f"   • {failed['file']}: {failed['error']}")
            self.log_message(f"📊 Total characters: {results['total_chars']:,}")
            self.log_message(f"⏱️ Total time: {total_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            return {"error": str(e)}
            
    def update_results_display(self):
        """Update the results tab with translation results"""
        if not self.translation_results or "error" in self.translation_results:
            return
            
        results = self.translation_results
        
        # Update stats
        stats_text = f"""📊 Translation Statistics

✅ Files Processed: {len(results['processed_files'])}
❌ Failed Files: {len(results['failed_files'])}
📝 Total Characters: {results['total_chars']:,}
⏱️ Processing Time: {results['total_time']:.2f} seconds
🧠 Method: {results['method']}
📁 Output: {results['output_folder']}"""

        self.stats_label.configure(text=stats_text)
        
        # Enable open folder button
        self.open_folder_btn.configure(state="normal")
        
        # Update results details
        self.results_textbox.delete("0.0", tk.END)
        
        details_text = "📋 Processed Files:\n\n"
        
        for file_info in results['processed_files']:
            details_text += f"✅ {file_info['file']}\n"
            details_text += f"   Output: {file_info['output_file']}\n"
            details_text += f"   Characters: {file_info['char_count']:,}\n"
            details_text += f"   Time: {file_info['translation_time']:.2f}s\n\n"
            
        if results['failed_files']:
            details_text += "\n❌ Failed Files:\n\n"
            for failed in results['failed_files']:
                details_text += f"❌ {failed['file']}: {failed['error']}\n"
                
        self.results_textbox.insert("0.0", details_text)
        
    def open_results_folder(self):
        """Open the results folder in file explorer"""
        if not self.translation_results or "error" in self.translation_results:
            return
            
        try:
            output_folder = self.translation_results['output_folder']
            
            # Open folder in OS file manager
            if os.name == 'nt':  # Windows
                os.startfile(output_folder)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{output_folder}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{output_folder}"')
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{str(e)}")
            
    def view_azure_status(self):
        """Display Azure AI DeepSeek status information"""
        if self.translator.use_azure_deepseek:
            status_message = """✅ Azure AI DeepSeek is ENABLED and working

Features active:
• Direct Korean→English translation
• HTML support with structure preservation  
• Glossary usage tracking enabled
• Clean output mode (no metadata headers)
• Proper failure handling (up to 6 retry attempts)
• Output saved to application directory

Model: DeepSeek-V3-0324
Endpoint: Connected and responsive"""
        else:
            status_message = """❌ Azure AI DeepSeek is DISABLED

Issues detected:
• Check your endpoint configuration
• Verify API key is correct
• Ensure internet connectivity

Please check your credentials in the ultimateTranslator.py file."""
        
        messagebox.showinfo("Azure AI DeepSeek Status", status_message)
    
    def view_supported_file_types(self):
        """Display supported file types"""
        doc_types = "\n".join([f"   • {ext}" for ext in sorted(self.translator.supported_extensions)])
        glossary_types = "\n".join([f"   • {ext}" for ext in sorted(self.translator.glossary_extensions)])
        
        file_types_info = f"""📄 Supported document types:
{doc_types}

📚 Supported glossary types:
{glossary_types}

🌐 HTML features:
   • Preserves images and structure
   • Translates titles, headings, paragraphs
   • Keeps original filenames

🔄 Translation features:
   • Up to 6 retry attempts per chunk
   • Proper error handling and failure reporting
   • Output saved to application directory
   • Clean output without metadata headers"""
        
        messagebox.showinfo("Supported File Types", file_types_info)
        
    def load_glossary_file(self):
        """Load a single glossary CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select glossary CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                result = self.translator.load_glossary_csv(file_path)
                
                if "successfully" in result:
                    self.update_glossary_selector()
                    self.update_glossaries_display()
                    self.update_glossary_stats()
                    messagebox.showinfo("Success", result)
                else:
                    messagebox.showerror("Error", result)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load glossary:\n{str(e)}")
    
    def clear_glossaries(self):
        """Clear all loaded glossaries"""
        if self.translator.glossaries:
            result = messagebox.askyesno("Confirm", "Are you sure you want to clear all loaded glossaries?")
            if result:
                self.translator.glossaries.clear()
                self.translator.active_glossary = None
                self.update_glossary_selector()
                self.update_glossaries_display()
                self.update_glossary_stats()
                messagebox.showinfo("Success", "All glossaries cleared")
        else:
            messagebox.showinfo("Info", "No glossaries to clear")
    
    def on_glossary_selected(self, selected_name):
        """Handle glossary selection from dropdown"""
        if selected_name and selected_name != "None":
            self.translator.set_active_glossary(selected_name)
            self.update_glossaries_display()
            self.update_glossary_stats()
    
    def update_glossary_selector(self):
        """Update the glossary selection dropdown"""
        glossary_names = list(self.translator.glossaries.keys())
        if glossary_names:
            self.glossary_selector.configure(values=glossary_names)
            if self.translator.active_glossary:
                self.glossary_selector.set(self.translator.active_glossary)
            else:
                self.glossary_selector.set(glossary_names[0])
                self.translator.set_active_glossary(glossary_names[0])
        else:
            self.glossary_selector.configure(values=["None"])
            self.glossary_selector.set("None")
    
    def update_glossary_stats(self):
        """Update glossary statistics display"""
        self.stats_display.delete("0.0", tk.END)
        
        if self.translator.glossaries:
            total_terms = sum(len(glossary) for glossary in self.translator.glossaries.values())
            stats_text = f"""Total Glossaries: {len(self.translator.glossaries)}
Total Terms: {total_terms}
Active Glossary: {self.translator.active_glossary or 'None'}

Terms by Type:"""
            
            # Count terms by type across all glossaries
            type_counts = {}
            for glossary in self.translator.glossaries.values():
                for term_data in glossary.values():
                    term_type = term_data.get('type', 'unknown')
                    type_counts[term_type] = type_counts.get(term_type, 0) + 1
            
            for term_type, count in sorted(type_counts.items()):
                stats_text += f"\n  • {term_type}: {count}"
        else:
            stats_text = "No glossaries loaded.\n\nUse 'Load Glossary CSV' to add terminology files."
            
        self.stats_display.insert("0.0", stats_text)
        

    def export_active_glossary(self):
        """Export the currently active glossary to CSV - KEEP ORIGINAL 4-column format"""
        if not self.translator.active_glossary:
            messagebox.showwarning("No Active Glossary", "Please select an active glossary first.")
            return

        try:
            save_path = filedialog.asksaveasfilename(
                title="Export active glossary",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=f"{self.translator.active_glossary}_exported.csv"
            )

            if save_path:
                glossary = self.translator.glossaries[self.translator.active_glossary]

                # Create CSV content with ORIGINAL 4-column format
                csv_content = "type,raw_name,translated_name,gender\n"
                for korean, data in glossary.items():
                    # Keep only the original 4 columns
                    csv_content += f"{data.get('type', '')},{korean},{data.get('translation', '')},{data.get('gender', '')}\n"

                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(csv_content)

                messagebox.showinfo("Success", f"Glossary exported to:\n{save_path}\n\nFormat: type,raw_name,translated_name,gender")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export glossary:\n{str(e)}")
            
    def open_term_editor(self):
        """Open a window to edit existing terms"""
        if not self.translator.active_glossary:
            messagebox.showwarning("No Active Glossary", "Please select an active glossary to edit.")
            return
            
        # Create a new window for editing
        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title(f"Edit Terms - {self.translator.active_glossary}")
        edit_window.geometry("800x600")
        
        # Make it modal
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(edit_window)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(scrollable_frame, text=f"Editing: {self.translator.active_glossary}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        glossary = self.translator.glossaries[self.translator.active_glossary]
        self.edit_entries = {}
        
        # Create edit fields for each term
        for korean, data in glossary.items():
            term_frame = ctk.CTkFrame(scrollable_frame)
            term_frame.pack(fill="x", padx=5, pady=3)
            
            # Korean term (read-only)
            ctk.CTkLabel(term_frame, text=f"Korean: {korean}", width=200).pack(side="left", padx=5)
            
            # English translation (editable)
            translation_var = ctk.StringVar(value=data.get('translation', ''))
            translation_entry = ctk.CTkEntry(term_frame, textvariable=translation_var, width=200)
            translation_entry.pack(side="left", padx=5)
            
            # Type (editable)
            type_var = ctk.StringVar(value=data.get('type', ''))
            type_entry = ctk.CTkEntry(term_frame, textvariable=type_var, width=100)
            type_entry.pack(side="left", padx=5)
            
            # Gender (editable)
            gender_var = ctk.StringVar(value=data.get('gender', ''))
            gender_entry = ctk.CTkEntry(term_frame, textvariable=gender_var, width=80)
            gender_entry.pack(side="left", padx=5)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                term_frame, 
                text="🗑️", 
                width=30, 
                command=lambda k=korean: self.delete_term_from_edit(k, edit_window),
                fg_color="red",
                hover_color="darkred"
            )
            delete_btn.pack(side="right", padx=5)
            
            # Store references
            self.edit_entries[korean] = {
                'translation': translation_var,
                'type': type_var,
                'gender': gender_var
            }
        
        # Buttons
        button_frame = ctk.CTkFrame(edit_window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Changes",
            command=lambda: self.save_term_edits(edit_window),
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=edit_window.destroy
        )
        cancel_btn.pack(side="right", padx=10)
    
    def add_new_term(self):
        """Open dialog to add a new term"""
        if not self.translator.active_glossary:
            messagebox.showwarning("No Active Glossary", "Please select an active glossary to add terms to.")
            return
            
        # Create a simple dialog
        add_window = ctk.CTkToplevel(self.root)
        add_window.title("Add New Term")
        add_window.geometry("400x300")
        add_window.transient(self.root)
        add_window.grab_set()
        
        # Input fields
        ctk.CTkLabel(add_window, text="Add New Term", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Korean term
        ctk.CTkLabel(add_window, text="Korean Term:").pack(pady=(10,0))
        korean_entry = ctk.CTkEntry(add_window, width=300)
        korean_entry.pack(pady=5)
        
        # English translation
        ctk.CTkLabel(add_window, text="English Translation:").pack(pady=(10,0))
        english_entry = ctk.CTkEntry(add_window, width=300)
        english_entry.pack(pady=5)
        
        # Type
        ctk.CTkLabel(add_window, text="Type:").pack(pady=(10,0))
        type_entry = ctk.CTkEntry(add_window, width=300, placeholder_text="character, location, skill, etc.")
        type_entry.pack(pady=5)
        
        # Gender (optional)
        ctk.CTkLabel(add_window, text="Gender (optional):").pack(pady=(10,0))
        gender_entry = ctk.CTkEntry(add_window, width=300, placeholder_text="male, female, or leave blank")
        gender_entry.pack(pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(add_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_new_term():
            korean = korean_entry.get().strip()
            english = english_entry.get().strip()
            term_type = type_entry.get().strip()
            gender = gender_entry.get().strip()
            
            if not korean or not english or not term_type:
                messagebox.showwarning("Missing Information", "Korean term, English translation, and type are required.")
                return
            
            # Add to glossary
            glossary = self.translator.glossaries[self.translator.active_glossary]
            glossary[korean] = {
                'translation': english,
                'type': term_type,
                'gender': gender,
                'usage_count': 0,
                'last_used': None
            }
            
            # Update displays
            self.update_glossaries_display()
            self.update_glossary_stats()
            
            messagebox.showinfo("Success", f"Added new term: {korean} → {english}")
            add_window.destroy()
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Add Term",
            command=save_new_term,
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=add_window.destroy
        )
        cancel_btn.pack(side="right", padx=10)
    
    def delete_term_from_edit(self, korean_term, edit_window):
        """Delete a term from the glossary"""
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the term '{korean_term}'?")
        if result:
            del self.translator.glossaries[self.translator.active_glossary][korean_term]
            if korean_term in self.edit_entries:
                del self.edit_entries[korean_term]
            messagebox.showinfo("Deleted", f"Term '{korean_term}' deleted.")
            edit_window.destroy()
            self.open_term_editor()  # Reopen to refresh
    
    def save_term_edits(self, edit_window):
        """Save all term edits"""
        try:
            glossary = self.translator.glossaries[self.translator.active_glossary]
            
            # Update all terms
            for korean, entries in self.edit_entries.items():
                if korean in glossary:
                    glossary[korean]['translation'] = entries['translation'].get()
                    glossary[korean]['type'] = entries['type'].get()
                    glossary[korean]['gender'] = entries['gender'].get()
            
            # Update displays
            self.update_glossaries_display()
            self.update_glossary_stats()
            
            messagebox.showinfo("Success", "All changes saved successfully!")
            edit_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes:\n{str(e)}")
        
    def configure_azure_credentials(self):
        """Open dialog to configure Azure credentials"""
        # Create configuration window
        config_window = ctk.CTkToplevel(self.root)
        config_window.title("Configure Azure AI DeepSeek")
        config_window.geometry("650x600")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Make window resizable
        config_window.resizable(True, True)
        config_window.minsize(500, 400)
        
        # Create main scrollable frame (vertical scrolling only - this is what works)
        main_scroll_frame = ctk.CTkScrollableFrame(config_window)
        main_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_scroll_frame, 
            text="🔧 Azure AI DeepSeek Configuration", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 15))
        
        # Instructions frame
        instructions_frame = ctk.CTkFrame(main_scroll_frame)
        instructions_frame.pack(fill="x", padx=10, pady=10)
        
        instructions = """Enter your Azure AI DeepSeek credentials below.
These will be saved to 'azure_config.txt' for future use.

📍 How to get credentials:
1. Go to Azure AI Studio (https://ai.azure.com)
2. Navigate to your DeepSeek deployment
3. Copy the endpoint URL and API key
4. Paste them below and click 'Test & Save'"""
        
        instructions_label = ctk.CTkLabel(
            instructions_frame, 
            text=instructions, 
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        instructions_label.pack(pady=15, padx=15)
        
        # Current status frame
        status_frame = ctk.CTkFrame(main_scroll_frame)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        status_text = "🟢 Currently configured and working" if self.translator.use_azure_deepseek else "🔴 Not configured or not working"
        status_label = ctk.CTkLabel(
            status_frame, 
            text=f"Current Status: {status_text}",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        status_label.pack(pady=10)
        
        # Input fields frame
        input_frame = ctk.CTkFrame(main_scroll_frame)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Endpoint section
        ctk.CTkLabel(
            input_frame, 
            text="🌐 Endpoint URL:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(15,5), anchor="w", padx=15)
        
        endpoint_entry = ctk.CTkEntry(
            input_frame, 
            height=35,
            placeholder_text="https://your-deployment.services.ai.azure.com/models",
            font=ctk.CTkFont(size=11)
        )
        endpoint_entry.pack(pady=5, padx=15, fill="x")
        
        # Pre-fill with current values
        if self.translator.azure_endpoint:
            endpoint_entry.insert(0, self.translator.azure_endpoint)
        
        # Endpoint example
        endpoint_example = ctk.CTkLabel(
            input_frame,
            text="💡 Example: https://ultimatetranslatorusingdeepseek.services.ai.azure.com/models",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        )
        endpoint_example.pack(pady=(2,15), padx=15, anchor="w")
        
        # API Key section
        ctk.CTkLabel(
            input_frame, 
            text="🔑 API Key:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(15,5), anchor="w", padx=15)
        
        api_key_entry = ctk.CTkEntry(
            input_frame, 
            height=35,
            placeholder_text="Your Azure API Key (starts with letters/numbers)",
            show="*",
            font=ctk.CTkFont(size=11)
        )
        api_key_entry.pack(pady=5, padx=15, fill="x")
        
        if self.translator.azure_api_key:
            api_key_entry.insert(0, self.translator.azure_api_key)
        
        # Show/Hide API key
        show_key = ctk.BooleanVar()
        show_checkbox = ctk.CTkCheckBox(
            input_frame, 
            text="👁️ Show API Key", 
            variable=show_key,
            font=ctk.CTkFont(size=11),
            command=lambda: api_key_entry.configure(show="" if show_key.get() else "*")
        )
        show_checkbox.pack(pady=8, padx=15, anchor="w")
        
        # API Key note
        apikey_note = ctk.CTkLabel(
            input_frame,
            text="💡 Found in Azure AI Studio → Your Deployment → Keys and Endpoint",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        )
        apikey_note.pack(pady=(2,15), padx=15, anchor="w")
        
        # Test results section
        results_frame = ctk.CTkFrame(main_scroll_frame)
        results_frame.pack(fill="x", padx=10, pady=10)
        
        # Status display area
        test_status_label = ctk.CTkLabel(
            results_frame, 
            text="Click 'Test & Save' to verify your credentials",
            font=ctk.CTkFont(size=11)
        )
        test_status_label.pack(pady=15)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(main_scroll_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def test_and_save():
            endpoint = endpoint_entry.get().strip()
            api_key = api_key_entry.get().strip()
            
            if not endpoint or not api_key:
                test_status_label.configure(
                    text="❌ Please enter both endpoint and API key", 
                    text_color="red"
                )
                return
            
            # Validate endpoint format
            if not endpoint.startswith("https://") or not ".services.ai.azure.com" in endpoint:
                test_status_label.configure(
                    text="❌ Endpoint should be: https://your-deployment.services.ai.azure.com/models", 
                    text_color="red"
                )
                return
            
            # Validate API key length
            if len(api_key) < 20:
                test_status_label.configure(
                    text="❌ API key seems too short. Please check your Azure AI Studio.", 
                    text_color="red"
                )
                return
            
            test_status_label.configure(text="🔄 Testing credentials... Please wait...", text_color="blue")
            config_window.update()
            
            # Test credentials
            success, message = self.translator.configure_azure_credentials(endpoint, api_key)
            
            if success:
                test_status_label.configure(text="✅ " + message, text_color="green")
                # Update sidebar status
                self.status_label.configure(text="🎉 Azure DeepSeek Ready!", text_color="green")
                
                # Show success dialog
                messagebox.showinfo(
                    "Success", 
                    "✅ Azure AI DeepSeek configured successfully!\n\n"
                    "📁 Credentials saved to azure_config.txt\n"
                    "🚀 You can now start translating files!"
                )
                config_window.destroy()
            else:
                test_status_label.configure(text="❌ " + message, text_color="red")
                
                # Show detailed error help in the same frame
                if hasattr(test_and_save, 'help_shown'):
                    return
                
                error_help = """
🔍 Troubleshooting tips:
• Check your internet connection
• Verify the endpoint URL is correct
• Ensure the API key is valid and not expired  
• Try regenerating the API key in Azure AI Studio
• Make sure your deployment is running"""
                
                help_label = ctk.CTkLabel(
                    results_frame,
                    text=error_help,
                    font=ctk.CTkFont(size=10),
                    text_color="gray60",
                    justify="left"
                )
                help_label.pack(pady=8)
                test_and_save.help_shown = True
        
        # Button container
        button_container = ctk.CTkFrame(button_frame)
        button_container.pack(pady=15)
        
        test_btn = ctk.CTkButton(
            button_container,
            text="🧪 Test & Save Credentials",
            command=test_and_save,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green",
            hover_color="darkgreen",
            width=200,
            height=40
        )
        test_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_container,
            text="❌ Cancel",
            command=config_window.destroy,
            font=ctk.CTkFont(size=12),
            width=120,
            height=40
        )
        cancel_btn.pack(side="left", padx=10)
        
        # Additional help section
        help_frame = ctk.CTkFrame(main_scroll_frame)
        help_frame.pack(fill="x", padx=10, pady=10)
        
        help_title = ctk.CTkLabel(
            help_frame,
            text="❓ Need Help?",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        help_title.pack(pady=(15,5))
        
        help_text = """If you don't have Azure AI DeepSeek credentials:

1. 🌐 Go to Azure AI Studio: https://ai.azure.com
2. 🔐 Sign in with your Microsoft account  
3. ➕ Create a new DeepSeek deployment (if needed)
4. 📋 Copy the endpoint URL and API key
5. 📥 Paste them above and test

📚 For detailed setup instructions, check the README.md file."""
        
        help_label = ctk.CTkLabel(
            help_frame,
            text=help_text,
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        help_label.pack(pady=15, padx=15)
                
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function"""
    app = TranslatorApp()
    app.run()

if __name__ == "__main__":
    main()