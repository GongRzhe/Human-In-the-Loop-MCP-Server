#!/usr/bin/env python3
"""
Enhanced Human-in-the-Loop MCP Server

This server provides tools for getting human input and choices through beautiful GUI dialogs.
It enables LLMs to pause and ask for human feedback, input, decisions, and file selections.

Features:
- Cross-platform support (Windows, macOS, Linux)
- Beautiful, modern UI with dark/light theme support
- File selection and drag-and-drop support
- Multiple input types (text, numbers, files, folders)
- Customizable styling and themes
"""

import asyncio
import json
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
from tkinter import font as tkFont
import tkinter.dnd as dnd
from typing import List, Dict, Any, Optional, Literal, Union
import sys
import os
import platform
from pathlib import Path
from pydantic import Field
from typing import Annotated
import base64
import mimetypes

from fastmcp import FastMCP, Context

# Initialize the MCP server
mcp = FastMCP("Enhanced Human-in-the-Loop Server")

# Global variables
_gui_initialized = False
_gui_lock = threading.Lock()
_current_theme = "dark"  # or "light"

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# Theme configurations
THEMES = {
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#ffffff",
        "select_bg": "#404040",
        "select_fg": "#ffffff",
        "button_bg": "#404040",
        "button_fg": "#ffffff",
        "entry_bg": "#404040",
        "entry_fg": "#ffffff",
        "frame_bg": "#2b2b2b",
        "accent": "#0078d4",
        "success": "#107c10",
        "warning": "#ff8c00",
        "error": "#d13438"
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "select_bg": "#e1e1e1",
        "select_fg": "#000000",
        "button_bg": "#e1e1e1",
        "button_fg": "#000000",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "frame_bg": "#f0f0f0",
        "accent": "#0078d4",
        "success": "#107c10",
        "warning": "#ff8c00",
        "error": "#d13438"
    }
}

def get_theme():
    """Get current theme colors"""
    return THEMES[_current_theme]

def ensure_gui_initialized():
    """Ensure GUI subsystem is properly initialized"""
    global _gui_initialized
    with _gui_lock:
        if not _gui_initialized:
            try:
                test_root = tk.Tk()
                test_root.withdraw()
                
                # Configure for high DPI on Windows
                if IS_WINDOWS:
                    try:
                        test_root.tk.call('tk', 'scaling', 1.5)
                    except:
                        pass
                
                test_root.destroy()
                _gui_initialized = True
            except Exception as e:
                print(f"Warning: GUI initialization failed: {e}")
                _gui_initialized = False
        return _gui_initialized

def configure_style(root):
    """Configure the visual style for the application"""
    theme = get_theme()
    
    # Configure the root window
    root.configure(bg=theme["bg"])
    
    # Create and configure ttk style
    style = ttk.Style()
    
    # Configure ttk widgets
    style.configure("Themed.TLabel", 
                   background=theme["bg"], 
                   foreground=theme["fg"],
                   font=("Segoe UI", 10))
    
    style.configure("Title.TLabel", 
                   background=theme["bg"], 
                   foreground=theme["fg"],
                   font=("Segoe UI", 12, "bold"))
    
    style.configure("Themed.TButton", 
                   background=theme["button_bg"],
                   foreground=theme["button_fg"],
                   font=("Segoe UI", 9),
                   focuscolor=theme["accent"])
    
    style.configure("Accent.TButton", 
                   background=theme["accent"],
                   foreground="#ffffff",
                   font=("Segoe UI", 9, "bold"))
    
    style.configure("Themed.TFrame", 
                   background=theme["bg"])
    
    style.configure("Card.TFrame", 
                   background=theme["frame_bg"],
                   relief="solid",
                   borderwidth=1)
    
    style.configure("Themed.TEntry", 
                   fieldbackground=theme["entry_bg"],
                   foreground=theme["entry_fg"],
                   font=("Segoe UI", 10))
    
    # Configure hover effects
    style.map("Themed.TButton",
             background=[('active', theme["select_bg"]),
                        ('pressed', theme["accent"])])
    
    style.map("Accent.TButton",
             background=[('active', '#106ebe'),
                        ('pressed', '#005a9e')])

def create_modern_window(title: str, width: int = 500, height: int = 400):
    """Create a modern-styled window"""
    root = tk.Tk()
    root.title(title)
    root.withdraw()  # Hide initially
    
    # Configure for high DPI
    if IS_WINDOWS:
        try:
            root.tk.call('tk', 'scaling', 1.2)
        except:
            pass
    
    # Set window properties
    root.geometry(f"{width}x{height}")
    root.resizable(True, True)
    root.attributes('-topmost', True)
    
    # Platform-specific window styling
    if IS_MACOS:
        root.attributes('-modified', False)
    elif IS_WINDOWS:
        try:
            # Windows-specific styling
            root.wm_attributes('-transparentcolor', '')
        except:
            pass
    
    # Configure styling
    configure_style(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.deiconify()  # Show window
    root.lift()
    root.focus_force()
    
    return root

def create_input_dialog(title: str, prompt: str, default_value: str = "", input_type: str = "text"):
    """Create a beautiful input dialog window"""
    try:
        root = create_modern_window(title, 450, 250)
        theme = get_theme()
        
        # Main container
        main_frame = ttk.Frame(root, style="Themed.TFrame", padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=title, style="Title.TLabel")
        title_label.pack(pady=(0, 10))
        
        # Prompt
        prompt_label = ttk.Label(main_frame, text=prompt, style="Themed.TLabel", wraplength=400)
        prompt_label.pack(pady=(0, 15))
        
        # Input field
        input_var = tk.StringVar(value=default_value)
        
        if input_type in ["integer", "float"]:
            # Create a validated entry for numbers
            vcmd = (root.register(lambda x: x.isdigit() or x == "" or (x.count('.') <= 1 and input_type == "float")), '%P')
            entry = ttk.Entry(main_frame, textvariable=input_var, style="Themed.TEntry", 
                            font=("Consolas", 11), validate='key', validatecommand=vcmd)
        else:
            entry = ttk.Entry(main_frame, textvariable=input_var, style="Themed.TEntry", 
                            font=("Segoe UI", 11))
        
        entry.pack(fill=tk.X, pady=(0, 20))
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        # Result variable
        result = {"value": None, "cancelled": False}
        
        # Button frame
        button_frame = ttk.Frame(main_frame, style="Themed.TFrame")
        button_frame.pack(fill=tk.X)
        
        def on_ok():
            value = input_var.get().strip()
            if input_type == "integer" and value:
                try:
                    result["value"] = int(value)
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter a valid integer.")
                    return
            elif input_type == "float" and value:
                try:
                    result["value"] = float(value)
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter a valid number.")
                    return
            else:
                result["value"] = value
            root.quit()
        
        def on_cancel():
            result["cancelled"] = True
            root.quit()
        
        # Buttons
        ttk.Button(button_frame, text="Cancel", command=on_cancel, 
                  style="Themed.TButton").pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="OK", command=on_ok, 
                  style="Accent.TButton").pack(side=tk.RIGHT)
        
        # Bind Enter key
        root.bind('<Return>', lambda e: on_ok())
        root.bind('<Escape>', lambda e: on_cancel())
        
        # Handle window close
        root.protocol("WM_DELETE_WINDOW", on_cancel)
        
        # Run the dialog
        root.mainloop()
        root.destroy()
        
        return None if result["cancelled"] else result["value"]
        
    except Exception as e:
        print(f"Error in input dialog: {e}")
        return None

class FileDropTarget:
    """Handle file drag and drop"""
    def __init__(self, widget, callback):
        self.widget = widget
        self.callback = callback
        
        # Platform-specific drag and drop setup
        if IS_WINDOWS:
            try:
                widget.drop_target_register('*')
                widget.dnd_bind('<<Drop>>', self.on_drop)
            except:
                pass  # Fallback if drag-drop not available
    
    def on_drop(self, event):
        files = event.data.split()
        self.callback([f.strip('{}') for f in files])

class EnhancedChoiceDialog:
    def __init__(self, parent, title, prompt, choices, allow_multiple=False, allow_files=False):
        self.result = None
        self.allow_files = allow_files
        
        # Create modern window
        self.dialog = create_modern_window(title, 550, 450)
        theme = get_theme()
        
        # Main container
        main_frame = ttk.Frame(self.dialog, style="Themed.TFrame", padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=title, style="Title.TLabel")
        title_label.pack(pady=(0, 10))
        
        # Prompt
        prompt_label = ttk.Label(main_frame, text=prompt, style="Themed.TLabel", wraplength=500)
        prompt_label.pack(pady=(0, 15))
        
        # Choice frame with card styling
        choice_frame = ttk.Frame(main_frame, style="Card.TFrame", padding="10")
        choice_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Listbox with custom styling
        list_frame = ttk.Frame(choice_frame, style="Themed.TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure listbox
        if allow_multiple:
            self.listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=12,
                                    bg=theme["entry_bg"], fg=theme["entry_fg"],
                                    selectbackground=theme["accent"],
                                    selectforeground="#ffffff",
                                    font=("Segoe UI", 10),
                                    relief="flat", borderwidth=0)
        else:
            self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, height=12,
                                    bg=theme["entry_bg"], fg=theme["entry_fg"],
                                    selectbackground=theme["accent"],
                                    selectforeground="#ffffff",
                                    font=("Segoe UI", 10),
                                    relief="flat", borderwidth=0)
        
        # Add choices
        for choice in choices:
            self.listbox.insert(tk.END, choice)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        # File selection area (if enabled)
        if allow_files:
            file_frame = ttk.Frame(main_frame, style="Card.TFrame", padding="10")
            file_frame.pack(fill=tk.X, pady=(0, 15))
            
            file_label = ttk.Label(file_frame, text="Or select files:", style="Themed.TLabel")
            file_label.pack(anchor=tk.W)
            
            file_button_frame = ttk.Frame(file_frame, style="Themed.TFrame")
            file_button_frame.pack(fill=tk.X, pady=(5, 0))
            
            ttk.Button(file_button_frame, text="📁 Browse Files", 
                      command=self.browse_files, style="Themed.TButton").pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(file_button_frame, text="📂 Browse Folder", 
                      command=self.browse_folder, style="Themed.TButton").pack(side=tk.LEFT)
            
            # Drag and drop area
            drop_frame = ttk.Frame(file_frame, style="Card.TFrame", padding="20")
            drop_frame.pack(fill=tk.X, pady=(10, 0))
            
            drop_label = ttk.Label(drop_frame, text="💾 Drag and drop files here", 
                                 style="Themed.TLabel", anchor=tk.CENTER)
            drop_label.pack()
            
            # Set up drag and drop
            if IS_WINDOWS:
                try:
                    FileDropTarget(drop_frame, self.on_files_dropped)
                except:
                    pass
        
        # Button frame
        button_frame = ttk.Frame(main_frame, style="Themed.TFrame")
        button_frame.pack(fill=tk.X)
        
        # Buttons
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked, 
                  style="Themed.TButton").pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="OK", command=self.ok_clicked, 
                  style="Accent.TButton").pack(side=tk.RIGHT)
        
        # Focus and selection
        self.listbox.focus_set()
        if choices:
            self.listbox.selection_set(0)
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel_clicked)
        
        # Wait for dialog completion
        self.dialog.mainloop()
    
    def browse_files(self):
        """Open file browser"""
        files = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Documents", "*.pdf *.doc *.docx"),
                ("Spreadsheets", "*.xls *.xlsx *.csv")
            ]
        )
        if files:
            self.result = list(files)
            self.dialog.quit()
    
    def browse_folder(self):
        """Open folder browser"""
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.result = [folder]
            self.dialog.quit()
    
    def on_files_dropped(self, files):
        """Handle dropped files"""
        self.result = files
        self.dialog.quit()
    
    def ok_clicked(self):
        selection = self.listbox.curselection()
        if selection:
            selected_items = [self.listbox.get(i) for i in selection]
            self.result = selected_items if len(selected_items) > 1 else selected_items[0]
        self.dialog.quit()
    
    def cancel_clicked(self):
        self.result = None
        self.dialog.quit()

class EnhancedMultilineDialog:
    def __init__(self, parent, title, prompt, default_value="", allow_files=False):
        self.result = None
        self.allow_files = allow_files
        
        # Create modern window
        self.dialog = create_modern_window(title, 650, 500)
        theme = get_theme()
        
        # Main container
        main_frame = ttk.Frame(self.dialog, style="Themed.TFrame", padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=title, style="Title.TLabel")
        title_label.pack(pady=(0, 10))
        
        # Prompt
        prompt_label = ttk.Label(main_frame, text=prompt, style="Themed.TLabel", wraplength=600)
        prompt_label.pack(pady=(0, 15))
        
        # Text area with card styling
        text_frame = ttk.Frame(main_frame, style="Card.TFrame", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Text widget
        self.text_widget = tk.Text(text_frame, wrap=tk.WORD, height=15, 
                                  font=("Consolas", 10),
                                  bg=theme["entry_bg"], fg=theme["entry_fg"],
                                  insertbackground=theme["fg"],
                                  selectbackground=theme["accent"],
                                  selectforeground="#ffffff",
                                  relief="flat", borderwidth=0)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Set default value
        if default_value:
            self.text_widget.insert("1.0", default_value)
        
        # File attachment area (if enabled)
        if allow_files:
            file_frame = ttk.Frame(main_frame, style="Card.TFrame", padding="10")
            file_frame.pack(fill=tk.X, pady=(0, 15))
            
            file_label = ttk.Label(file_frame, text="📎 Attach files:", style="Themed.TLabel")
            file_label.pack(anchor=tk.W)
            
            ttk.Button(file_frame, text="Browse Files", command=self.attach_files, 
                      style="Themed.TButton").pack(anchor=tk.W, pady=(5, 0))
        
        # Button frame
        button_frame = ttk.Frame(main_frame, style="Themed.TFrame")
        button_frame.pack(fill=tk.X)
        
        # Character count
        self.char_count_var = tk.StringVar()
        self.update_char_count()
        char_label = ttk.Label(button_frame, textvariable=self.char_count_var, 
                              style="Themed.TLabel")
        char_label.pack(side=tk.LEFT)
        
        # Buttons
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked, 
                  style="Themed.TButton").pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="OK", command=self.ok_clicked, 
                  style="Accent.TButton").pack(side=tk.RIGHT)
        
        # Bind events
        self.text_widget.bind('<KeyRelease>', lambda e: self.update_char_count())
        self.text_widget.focus_set()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel_clicked)
        
        # Wait for dialog completion
        self.dialog.mainloop()
    
    def update_char_count(self):
        """Update character count display"""
        content = self.text_widget.get("1.0", tk.END).strip()
        char_count = len(content)
        line_count = len(content.split('\n')) if content else 0
        self.char_count_var.set(f"{char_count} characters, {line_count} lines")
    
    def attach_files(self):
        """Attach files to the text"""
        files = filedialog.askopenfilenames(title="Select Files to Attach")
        if files:
            self.text_widget.insert(tk.END, f"\n\n[Attached Files: {', '.join(files)}]")
            self.update_char_count()
    
    def ok_clicked(self):
        self.result = self.text_widget.get("1.0", tk.END).strip()
        self.dialog.quit()
    
    def cancel_clicked(self):
        self.result = None
        self.dialog.quit()

def create_choice_dialog(title: str, prompt: str, choices: List[str], allow_multiple: bool = False, allow_files: bool = False):
    """Create an enhanced choice dialog"""
    try:
        dialog = EnhancedChoiceDialog(None, title, prompt, choices, allow_multiple, allow_files)
        return dialog.result
    except Exception as e:
        print(f"Error in choice dialog: {e}")
        return None

def create_multiline_input_dialog(title: str, prompt: str, default_value: str = "", allow_files: bool = False):
    """Create an enhanced multiline input dialog"""
    try:
        dialog = EnhancedMultilineDialog(None, title, prompt, default_value, allow_files)
        return dialog.result
    except Exception as e:
        print(f"Error in multiline dialog: {e}")
        return None

def show_confirmation(title: str, message: str):
    """Show enhanced confirmation dialog"""
    try:
        root = create_modern_window(title, 400, 200)
        theme = get_theme()
        
        # Main container
        main_frame = ttk.Frame(root, style="Themed.TFrame", padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon and message frame
        content_frame = ttk.Frame(main_frame, style="Themed.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Icon (using emoji for cross-platform compatibility)
        icon_label = ttk.Label(content_frame, text="❓", font=("Segoe UI", 24), 
                              style="Themed.TLabel")
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Message
        message_label = ttk.Label(content_frame, text=message, style="Themed.TLabel", 
                                 wraplength=300)
        message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Result
        result = {"value": False}
        
        # Button frame
        button_frame = ttk.Frame(main_frame, style="Themed.TFrame")
        button_frame.pack(fill=tk.X)
        
        def on_yes():
            result["value"] = True
            root.quit()
        
        def on_no():
            result["value"] = False
            root.quit()
        
        # Buttons
        ttk.Button(button_frame, text="No", command=on_no, 
                  style="Themed.TButton").pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Yes", command=on_yes, 
                  style="Accent.TButton").pack(side=tk.RIGHT)
        
        # Bind keys
        root.bind('<Return>', lambda e: on_yes())
        root.bind('<Escape>', lambda e: on_no())
        
        # Handle window close
        root.protocol("WM_DELETE_WINDOW", on_no)
        
        # Run dialog
        root.mainloop()
        root.destroy()
        
        return result["value"]
        
    except Exception as e:
        print(f"Error in confirmation dialog: {e}")
        return False

def show_info(title: str, message: str, icon_type: str = "info"):
    """Show enhanced info dialog"""
    try:
        root = create_modern_window(title, 400, 200)
        theme = get_theme()
        
        # Main container
        main_frame = ttk.Frame(root, style="Themed.TFrame", padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon and message frame
        content_frame = ttk.Frame(main_frame, style="Themed.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Icon based on type
        icons = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "success": "✅"}
        icon = icons.get(icon_type, "ℹ️")
        
        icon_label = ttk.Label(content_frame, text=icon, font=("Segoe UI", 24), 
                              style="Themed.TLabel")
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Message
        message_label = ttk.Label(content_frame, text=message, style="Themed.TLabel", 
                                 wraplength=300)
        message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = ttk.Frame(main_frame, style="Themed.TFrame")
        button_frame.pack(fill=tk.X)
        
        def on_ok():
            root.quit()
        
        # OK button
        ttk.Button(button_frame, text="OK", command=on_ok, 
                  style="Accent.TButton").pack(side=tk.RIGHT)
        
        # Bind keys
        root.bind('<Return>', lambda e: on_ok())
        root.bind('<Escape>', lambda e: on_ok())
        
        # Handle window close
        root.protocol("WM_DELETE_WINDOW", on_ok)
        
        # Run dialog
        root.mainloop()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"Error in info dialog: {e}")
        return False

def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get information about a file"""
    try:
        path = Path(file_path)
        stat = path.stat()
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size": stat.st_size,
            "size_human": format_file_size(stat.st_size),
            "modified": stat.st_mtime,
            "mime_type": mime_type,
            "extension": path.suffix.lower(),
            "is_image": mime_type and mime_type.startswith("image/"),
            "is_document": path.suffix.lower() in [".pdf", ".doc", ".docx", ".txt", ".rtf"],
            "is_spreadsheet": path.suffix.lower() in [".xls", ".xlsx", ".csv"],
            "exists": path.exists(),
            "is_file": path.is_file(),
            "is_directory": path.is_dir()
        }
    except Exception as e:
        return {"error": str(e), "path": file_path}

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

# Enhanced MCP Tools

@mcp.tool()
async def get_user_input(
    title: Annotated[str, Field(description="Title of the input dialog window")],
    prompt: Annotated[str, Field(description="The prompt/question to show to the user")],
    default_value: Annotated[str, Field(description="Default value to pre-fill in the input field")] = "",
    input_type: Annotated[Literal["text", "integer", "float"], Field(description="Type of input expected")] = "text",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Create an input dialog window for the user to enter text, numbers, or other data.
    
    This tool opens a beautiful GUI dialog box where the user can input information that the LLM needs.
    Perfect for getting specific details, clarifications, or data from the user.
    """
    try:
        if ctx:
            await ctx.info(f"Requesting user input: {prompt}")
        
        if not ensure_gui_initialized():
            return {"success": False, "error": "GUI system not available", "cancelled": False}
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(create_input_dialog, title, prompt, default_value, input_type)
            result = future.result(timeout=300)
        
        if result is not None:
            if ctx:
                await ctx.info(f"User provided input: {result}")
            return {
                "success": True,
                "user_input": result,
                "input_type": input_type,
                "cancelled": False
            }
        else:
            if ctx:
                await ctx.warning("User cancelled the input dialog")
            return {
                "success": False,
                "user_input": None,
                "input_type": input_type,
                "cancelled": True
            }
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Error creating input dialog: {str(e)}")
        return {"success": False, "error": str(e), "cancelled": False}

@mcp.tool()
async def get_user_choice(
    title: Annotated[str, Field(description="Title of the choice dialog window")],
    prompt: Annotated[str, Field(description="The prompt/question to show to the user")],
    choices: Annotated[List[str], Field(description="List of choices to present to the user")],
    allow_multiple: Annotated[bool, Field(description="Whether user can select multiple choices")] = False,
    allow_files: Annotated[bool, Field(description="Whether to allow file selection in addition to choices")] = False,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Create a choice dialog window for the user to select from multiple options.
    
    This tool opens a beautiful GUI dialog box with a list of choices where the user can select
    one or multiple options. Can also allow file selection. Perfect for getting decisions, 
    preferences, or selections from the user.
    """
    try:
        if ctx:
            await ctx.info(f"Requesting user choice: {prompt}")
            await ctx.debug(f"Available choices: {choices}")
        
        if not ensure_gui_initialized():
            return {"success": False, "error": "GUI system not available", "cancelled": False}
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(create_choice_dialog, title, prompt, choices, allow_multiple, allow_files)
            result = future.result(timeout=300)
        
        if result is not None:
            if ctx:
                await ctx.info(f"User selected: {result}")
            
            # Handle file selection results
            file_info = []
            if allow_files and result:
                if isinstance(result, list):
                    for item in result:
                        if os.path.exists(str(item)):
                            file_info.append(get_file_info(str(item)))
                elif os.path.exists(str(result)):
                    file_info.append(get_file_info(str(result)))
            
            return {
                "success": True,
                "selected_choice": result,
                "selected_choices": result if isinstance(result, list) else [result],
                "allow_multiple": allow_multiple,
                "file_info": file_info,
                "cancelled": False
            }
        else:
            if ctx:
                await ctx.warning("User cancelled the choice dialog")
            return {
                "success": False,
                "selected_choice": None,
                "selected_choices": [],
                "allow_multiple": allow_multiple,
                "cancelled": True
            }
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Error creating choice dialog: {str(e)}")
        return {"success": False, "error": str(e), "cancelled": False}

@mcp.tool()
async def get_multiline_input(
    title: Annotated[str, Field(description="Title of the input dialog window")],
    prompt: Annotated[str, Field(description="The prompt/question to show to the user")],
    default_value: Annotated[str, Field(description="Default text to pre-fill in the text area")] = "",
    allow_files: Annotated[bool, Field(description="Whether to allow file attachment")] = False,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Create a multi-line text input dialog for the user to enter longer text content.
    
    This tool opens a beautiful GUI dialog box with a large text area where the user can input
    multiple lines of text. Can also allow file attachments. Perfect for getting detailed 
    descriptions, code, or long-form content.
    """
    try:
        if ctx:
            await ctx.info(f"Requesting multiline user input: {prompt}")
        
        if not ensure_gui_initialized():
            return {"success": False, "error": "GUI system not available", "cancelled": False}
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(create_multiline_input_dialog, title, prompt, default_value, allow_files)
            result = future.result(timeout=300)
        
        if result is not None:
            if ctx:
                await ctx.info(f"User provided multiline input ({len(result)} characters)")
            return {
                "success": True,
                "user_input": result,
                "character_count": len(result),
                "line_count": len(result.split('\n')),
                "word_count": len(result.split()),
                "cancelled": False
            }
        else:
            if ctx:
                await ctx.warning("User cancelled the multiline input dialog")
            return {
                "success": False,
                "user_input": None,
                "cancelled": True
            }
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Error creating multiline input dialog: {str(e)}")
        return {"success": False, "error": str(e), "cancelled": False}

@mcp.tool()
async def get_file_selection(
    title: Annotated[str, Field(description="Title of the file selection dialog")] = "Select Files",
    prompt: Annotated[str, Field(description="Instructions for the user")] = "Please select the files you need:",
    file_types: Annotated[List[str], Field(description="Allowed file extensions (e.g., ['.txt', '.pdf'])")] = [],
    allow_multiple: Annotated[bool, Field(description="Whether to allow multiple file selection")] = True,
    select_folders: Annotated[bool, Field(description="Whether to select folders instead of files")] = False,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Open a file selection dialog for the user to choose files or folders.
    
    This tool opens a native file browser dialog where users can select files or folders.
    Perfect for when you need the user to provide specific files for processing.
    """
    try:
        if ctx:
            await ctx.info(f"Requesting file selection: {prompt}")
        
        if not ensure_gui_initialized():
            return {"success": False, "error": "GUI system not available", "cancelled": False}
        
        def select_files():
            root = tk.Tk()
            root.withdraw()
            
            if select_folders:
                if allow_multiple:
                    # Multiple folder selection (not natively supported, use custom dialog)
                    result = filedialog.askdirectory(title=title)
                    return [result] if result else None
                else:
                    result = filedialog.askdirectory(title=title)
                    return [result] if result else None
            else:
                # File selection
                filetypes = [("All Files", "*.*")]
                if file_types:
                    for ext in file_types:
                        filetypes.insert(0, (f"{ext.upper()} Files", f"*{ext}"))
                
                if allow_multiple:
                    result = filedialog.askopenfilenames(title=title, filetypes=filetypes)
                    return list(result) if result else None
                else:
                    result = filedialog.askopenfilename(title=title, filetypes=filetypes)
                    return [result] if result else None
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(select_files)
            result = future.result(timeout=300)
        
        if result:
            # Get file information
            file_info = [get_file_info(path) for path in result]
            
            if ctx:
                await ctx.info(f"User selected {len(result)} {'folder(s)' if select_folders else 'file(s)'}")
            
            return {
                "success": True,
                "selected_paths": result,
                "file_info": file_info,
                "count": len(result),
                "cancelled": False
            }
        else:
            if ctx:
                await ctx.warning("User cancelled file selection")
            return {
                "success": False,
                "selected_paths": [],
                "file_info": [],
                "count": 0,
                "cancelled": True
            }
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Error in file selection: {str(e)}")
        return {"success": False, "error": str(e), "cancelled": False}

@mcp.tool()
async def show_confirmation_dialog(
    title: Annotated[str, Field(description="Title of the confirmation dialog")],
    message: Annotated[str, Field(description="The message to show to the user")],
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Show a confirmation dialog with Yes/No buttons.
    
    This tool displays a message to the user and asks for confirmation.
    Perfect for getting approval before proceeding with an action.
    """
    try:
        if ctx:
            await ctx.info(f"Requesting user confirmation: {message}")
        
        if not ensure_gui_initialized():
            return {"success": False, "error": "GUI system not available", "confirmed": False}
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(show_confirmation, title, message)
            result = future.result(timeout=300)
        
        if ctx:
            await ctx.info(f"User confirmation result: {'Yes' if result else 'No'}")
        
        return {
            "success": True,
            "confirmed": result,
            "response": "yes" if result else "no"
        }
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Error showing confirmation dialog: {str(e)}")
        return {"success": False, "error": str(e), "confirmed": False}

@mcp.tool()
async def show_info_message(
    title: Annotated[str, Field(description="Title of the information dialog")],
    message: Annotated[str, Field(description="The information message to show to the user")],
    icon_type: Annotated[Literal["info", "warning", "error", "success"], Field(description="Type of icon to show")] = "info",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Show an information message to the user.
    
    This tool displays an informational message dialog to notify the user about something.
    The user just needs to click OK to acknowledge the message.
    """
    try:
        if ctx:
            await ctx.info(f"Showing {icon_type} message to user: {message}")
        
        if not ensure_gui_initialized():
            return {"success": False, "error": "GUI system not available"}
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(show_info, title, message, icon_type)
            result = future.result(timeout=300)
        
        if ctx:
            await ctx.info("Info message acknowledged by user")
        
        return {
            "success": True,
            "acknowledged": result,
            "icon_type": icon_type
        }
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Error showing info message: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def set_theme(
    theme: Annotated[Literal["dark", "light"], Field(description="Theme to apply")] = "dark",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Set the visual theme for the dialogs.
    
    This tool allows changing between dark and light themes for all dialogs.
    """
    global _current_theme
    try:
        if ctx:
            await ctx.info(f"Setting theme to: {theme}")
        
        _current_theme = theme
        
        return {
            "success": True,
            "theme": theme,
            "available_themes": list(THEMES.keys())
        }
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Error setting theme: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Check if the Enhanced Human-in-the-Loop server is running and GUI is available."""
    try:
        gui_available = ensure_gui_initialized()
        
        return {
            "status": "healthy" if gui_available else "degraded",
            "gui_available": gui_available,
            "server_name": "Enhanced Human-in-the-Loop Server",
            "platform": f"{platform.system()} {platform.release()}",
            "python_version": sys.version.split()[0],
            "theme": _current_theme,
            "features": [
                "Beautiful modern UI",
                "Cross-platform support",
                "File selection and drag-drop",
                "Dark/Light themes",
                "Enhanced input validation"
            ],
            "tools_available": [
                "get_user_input",
                "get_user_choice", 
                "get_multiline_input",
                "get_file_selection",
                "show_confirmation_dialog",
                "show_info_message",
                "set_theme"
            ]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "gui_available": False,
            "error": str(e),
            "platform": platform.system()
        }

# Main execution
if __name__ == "__main__":
    print("🚀 Starting Enhanced Human-in-the-Loop MCP Server...")
    print("=" * 60)
    print("This server provides beautiful, cross-platform GUI tools for LLMs")
    print("to interact with humans through modern dialog interfaces.")
    print("")
    print("✨ Features:")
    print("• Beautiful dark/light theme support")
    print("• Cross-platform compatibility (Windows, macOS, Linux)")
    print("• File selection with drag-and-drop support")
    print("• Enhanced input validation and formatting")
    print("• Modern, accessible UI design")
    print("")
    print("🛠️  Available tools:")
    print("• get_user_input - Get text/number input from user")
    print("• get_user_choice - Let user choose from options")
    print("• get_multiline_input - Get multi-line text from user")
    print("• get_file_selection - File/folder selection dialog")
    print("• show_confirmation_dialog - Ask user for yes/no confirmation")
    print("• show_info_message - Display information to user")
    print("• set_theme - Change visual theme")
    print("• health_check - Check server status")
    print("")
    
    # Platform-specific info
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Test GUI availability
    if ensure_gui_initialized():
        print("✅ GUI system initialized successfully")
    else:
        print("⚠️  Warning: GUI system may not be available")
    
    print("=" * 60)
    print("🎯 Starting MCP server...")
    
    # Run the server
    mcp.run()