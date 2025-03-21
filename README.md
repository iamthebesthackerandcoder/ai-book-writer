# AI Book Writer

A web-based application that guides you through the process of writing a book with AI assistance. The system uses local AI models to help generate world settings, characters, outlines, and complete chapters.

## Features

- Web-based user interface with no authentication required
- Step-by-step guided book writing process
- Real-time AI generation of:
  - World settings and environments
  - Character profiles and development
  - Book outlines with chapter structure
  - Scene generation for individual chapters
  - Full chapter content
- Local AI model support (compatible with your existing config)
- Progress tracking
- Ability to edit and save generated content
- All content stored in local files for easy access

## Architecture

The application consists of:

- **Flask Web Server**: Provides the user interface and manages the book generation process
- **AI Agents**: Specialized agents for different aspects of book creation:
  - Story planning
  - World building
  - Character development
  - Scene creation
  - Writing and editing
- **Prompt Management**: Centralized prompt templates in `prompts.py`
- **File Storage**: Local storage of all generated content in the `book_output` directory

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-book-writer.git
cd ai-book-writer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the local AI model server according to your `config.py` settings.

2. Run the web application:
```bash
python web_app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

4. Follow the step-by-step process in the web interface:
   - Create a world setting
   - Generate characters
   - Create a book outline
   - Work chapter by chapter to generate your book

## Book Writing Workflow

The application guides you through a logical book creation process:

1. **World Building**: Define the setting, time period, and environment for your story
2. **Character Creation**: Generate the main characters for your book
3. **Outline Generation**: Create a chapter-by-chapter outline of your story
4. **Chapter Writing**:
   - Generate individual scenes for a chapter
   - Generate a complete chapter
   - Edit and save your chapters
   - Proceed to the next chapter

## Output Structure

All generated content is saved in the `book_output` directory:
```
book_output/
├── world.txt                # World setting
├── characters.txt           # Character profiles
├── outline.txt              # Full book outline
├── outline.json             # Structured outline data
├── chapters/
│   ├── chapter_1.txt
│   ├── chapter_2.txt
│   └── ...
│   └── chapter_1_scenes/    # Generated scenes for chapters
│       ├── scene_1.txt
│       └── ...
```

## Requirements

- Python 3.8+
- Flask 2.2.0+
- AutoGen 0.2.0+
- Local AI model (as configured in your existing `config.py`)
- Other dependencies listed in requirements.txt

## Configuration

The system can be configured through `config.py` for the AI model settings and `prompts.py` for generation prompts.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.