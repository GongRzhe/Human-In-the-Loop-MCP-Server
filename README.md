# 🚀 Human-in-the-Loop MCP Server

A beautiful, cross-platform Model Context Protocol (MCP) server that enables LLMs to interact with humans through modern, intuitive GUI dialogs. Perfect for getting user input, file selections, confirmations, and more during AI conversations.

## ✨ Features

### 🎨 Beautiful Modern UI
- **Dark & Light Themes** - Switch between modern dark and light themes
- **Cross-Platform Design** - Native look and feel on Windows, macOS, and Linux
- **Responsive Layout** - Dialogs adapt to content and screen size
- **High DPI Support** - Crisp rendering on high-resolution displays

### 📁 File Management
- **File Selection** - Browse and select files with native file dialogs
- **Folder Selection** - Choose directories for batch operations
- **Drag & Drop Support** - Drop files directly into dialogs (Windows)
- **File Type Filtering** - Restrict selection to specific file types
- **File Information** - Get detailed metadata about selected files

### 💬 Rich Input Options
- **Text Input** - Single-line text with validation
- **Number Input** - Validated integer and float inputs
- **Multi-line Text** - Rich text editor with character counting
- **Multiple Choice** - Single or multi-select from options
- **Confirmation Dialogs** - Yes/No questions with custom messaging
- **Information Messages** - Status updates with different icon types

### 🔧 Developer Friendly
- **FastMCP Integration** - Built on the FastMCP framework
- **Async/Await Support** - Non-blocking operations
- **Error Handling** - Comprehensive error reporting
- **Logging Integration** - Detailed operation logging
- **Health Checks** - Monitor server status

## 📋 Requirements

- **Python 3.8+**
- **tkinter** (usually included with Python)
- **fastmcp** - MCP server framework
- **pydantic** - Data validation

### Platform-Specific Requirements

#### Windows
- Windows 10 or later recommended
- Built-in tkinter support

#### macOS
- macOS 10.12 or later
- tkinter (install via Homebrew if needed): `brew install python-tk`

#### Linux
- Any modern Linux distribution
- tkinter package: `sudo apt-get install python3-tk` (Ubuntu/Debian)

## 🚀 Installation

1. **Clone or download** the server script
2. **Install dependencies**:
   ```bash
   pip install fastmcp pydantic
   ```
3. **Run the server**:
   ```bash
   python hitl_server.py
   ```

## 🛠️ Available Tools

### `get_user_input`
Get text or numeric input from the user.

**Parameters:**
- `title` (str): Dialog window title
- `prompt` (str): Question/instruction for the user
- `default_value` (str): Pre-filled default value
- `input_type` (str): "text", "integer", or "float"

**Example:**
```python
result = await get_user_input(
    title="User Information",
    prompt="Please enter your name:",
    default_value="",
    input_type="text"
)
```

### `get_user_choice`
Present multiple options for user selection.

**Parameters:**
- `title` (str): Dialog window title
- `prompt` (str): Question/instruction for the user
- `choices` (List[str]): List of available options
- `allow_multiple` (bool): Allow selecting multiple options
- `allow_files` (bool): Include file selection option

**Example:**
```python
result = await get_user_choice(
    title="Choose Options",
    prompt="Select your preferences:",
    choices=["Option A", "Option B", "Option C"],
    allow_multiple=True
)
```

### `get_multiline_input`
Get longer text input with rich editing capabilities.

**Parameters:**
- `title` (str): Dialog window title
- `prompt` (str): Question/instruction for the user
- `default_value` (str): Pre-filled text
- `allow_files` (bool): Allow file attachments

**Example:**
```python
result = await get_multiline_input(
    title="Feedback",
    prompt="Please provide detailed feedback:",
    default_value="",
    allow_files=True
)
```

### `get_file_selection`
Open native file/folder selection dialogs.

**Parameters:**
- `title` (str): Dialog window title
- `prompt` (str): Instructions for the user
- `file_types` (List[str]): Allowed file extensions
- `allow_multiple` (bool): Allow multiple selections
- `select_folders` (bool): Select folders instead of files

**Example:**
```python
result = await get_file_selection(
    title="Select Images",
    prompt="Choose image files to process:",
    file_types=[".jpg", ".png", ".gif"],
    allow_multiple=True
)
```

### `show_confirmation_dialog`
Ask for Yes/No confirmation.

**Parameters:**
- `title` (str): Dialog window title
- `message` (str): Confirmation message

**Example:**
```python
result = await show_confirmation_dialog(
    title="Confirm Action",
    message="Are you sure you want to delete these files?"
)
```

### `show_info_message`
Display information to the user.

**Parameters:**
- `title` (str): Dialog window title
- `message` (str): Information message
- `icon_type` (str): "info", "warning", "error", or "success"

**Example:**
```python
result = await show_info_message(
    title="Operation Complete",
    message="Files have been processed successfully!",
    icon_type="success"
)
```

### `set_theme`
Change the visual theme.

**Parameters:**
- `theme` (str): "dark" or "light"

**Example:**
```python
result = await set_theme(theme="light")
```

### `health_check`
Check server status and capabilities.

**Example:**
```python
result = await health_check()
```

## 🎨 Themes

The server supports two beautiful themes:

### Dark Theme (Default)
- Modern dark background with light text
- Blue accent colors for highlights
- Comfortable for low-light environments

### Light Theme
- Clean white background with dark text
- Consistent with system light themes
- Great for bright environments

Switch themes using the `set_theme` tool or by modifying the `_current_theme` variable.

## 📁 File Support

### Supported File Operations
- **File Selection**: Choose individual files with type filtering
- **Folder Selection**: Select entire directories
- **Multiple Selection**: Choose multiple files/folders at once
- **Drag & Drop**: Drop files directly into dialogs (Windows)
- **File Information**: Get detailed metadata including:
  - File size (human-readable format)
  - MIME type detection
  - File extension analysis
  - Modification timestamps
  - File type categorization

### File Type Detection
The server automatically detects and categorizes files:
- **Images**: .png, .jpg, .jpeg, .gif, .bmp
- **Documents**: .pdf, .doc, .docx, .txt, .rtf
- **Spreadsheets**: .xls, .xlsx, .csv
- **Archives**: .zip, .rar, .7z
- **And many more...**

## 🖥️ Cross-Platform Support

### Windows
- Native Windows styling and behavior
- High DPI scaling support
- Drag & drop functionality
- Windows-specific file dialogs

### macOS
- Native macOS appearance
- Retina display support
- macOS file selection dialogs
- Respect system theme preferences

### Linux
- GTK-based native styling
- Consistent with desktop environment
- Support for various Linux distributions
- Adaptive to system themes

## 🔧 Configuration

### Environment Variables
You can customize the server behavior with environment variables:

```bash
# Set default theme
export HITL_THEME=dark

# Set default window size
export HITL_WINDOW_WIDTH=600
export HITL_WINDOW_HEIGHT=400

# Enable debug logging
export HITL_DEBUG=true
```

### Programmatic Configuration
```python
# Change theme globally
_current_theme = "light"

# Modify theme colors
THEMES["custom"] = {
    "bg": "#1e1e1e",
    "fg": "#ffffff",
    # ... other colors
}
```

## 🚨 Error Handling

The server includes comprehensive error handling:

- **GUI Unavailable**: Graceful fallback when GUI system isn't available
- **Timeout Protection**: All dialogs have timeout limits (5 minutes default)
- **Validation Errors**: Input validation with user-friendly error messages
- **File System Errors**: Proper error reporting for file operations
- **Threading Safety**: Thread-safe GUI operations

## 📊 Response Formats

All tools return consistent response formats:

### Success Response
```json
{
  "success": true,
  "user_input": "user response",
  "cancelled": false,
  "additional_data": "..."
}
```

### Error Response
```json
{
  "success": false,
  "error": "error message",
  "cancelled": false
}
```

### Cancelled Response
```json
{
  "success": false,
  "cancelled": true,
  "user_input": null
}
```

## 🔍 Debugging

### Enable Debug Mode
```python
# Add to the top of your script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

#### GUI Not Available
- **Symptom**: "GUI system not available" error
- **Solution**: Ensure tkinter is installed and DISPLAY is set (Linux)

#### High DPI Issues
- **Symptom**: Blurry or small dialogs on high-DPI displays
- **Solution**: The server automatically handles DPI scaling

#### Theme Not Applying
- **Symptom**: Dialogs don't reflect theme changes
- **Solution**: Theme changes apply to new dialogs only

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- **Additional Input Types**: Date pickers, color selectors, etc.
- **More Themes**: Additional color schemes and styles
- **Enhanced File Support**: Preview capabilities, file validation
- **Accessibility**: Screen reader support, keyboard navigation
- **Mobile Support**: Touch-friendly interfaces

## 📄 License

This project is open source. Please check the license file for specific terms.

## 🆘 Support

For issues and questions:

1. **Check the health_check tool** - Verify server status
2. **Review error messages** - Most issues include helpful error details
3. **Check platform compatibility** - Ensure your system is supported
4. **Enable debug logging** - Get detailed operation information

## 📝 Examples

### Basic User Input
```python
# Get user's name
name = await get_user_input(
    title="Welcome",
    prompt="What's your name?",
    input_type="text"
)

# Get user's age
age = await get_user_input(
    title="Profile",
    prompt="How old are you?",
    input_type="integer"
)
```

### File Processing Workflow
```python
# Select files to process
files = await get_file_selection(
    title="Select Files",
    prompt="Choose files to process:",
    file_types=[".txt", ".doc", ".pdf"],
    allow_multiple=True
)

# Confirm processing
if files["success"]:
    confirmed = await show_confirmation_dialog(
        title="Confirm Processing",
        message=f"Process {files['count']} files?"
    )
    
    if confirmed["confirmed"]:
        # Process files...
        await show_info_message(
            title="Complete",
            message="Files processed successfully!",
            icon_type="success"
        )
```

### Interactive Configuration
```python
# Get user preferences
theme_choice = await get_user_choice(
    title="Preferences",
    prompt="Choose your preferred theme:",
    choices=["Dark Theme", "Light Theme"]
)

# Apply theme
if theme_choice["success"]:
    theme = "dark" if "Dark" in theme_choice["selected_choice"] else "light"
    await set_theme(theme=theme)
```

---

**Made with ❤️ for the MCP community**