"""
Flask web application for AI Book Writer
"""
import os
import json
from flask import Flask, render_template, request, jsonify, session
from config import get_config
from agents import BookAgents
from book_generator import BookGenerator
from outline_generator import OutlineGenerator
import prompts

app = Flask(__name__)
app.secret_key = 'ai-book-writer-secret-key'  # For session management

# Ensure book_output directory exists
os.makedirs('book_output/chapters', exist_ok=True)

# Initialize global variables
agent_config = get_config()

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/world', methods=['GET', 'POST'])
def world():
    """Generate or display world theme"""
    if request.method == 'POST':
        topic = request.form.get('topic')
        # Save topic to session
        session['topic'] = topic
        
        # Initialize agents for world building
        book_agents = BookAgents(agent_config)
        agents = book_agents.create_agents(topic, 0)  # 0 chapters as we're just building the world
        
        # Generate world theme using the prompt
        world_theme = book_agents.generate_content(
            "world_builder",
            prompts.WORLD_THEME_PROMPT.format(topic=topic)
        )
        
        # Clean and save world theme to session and file
        world_theme = world_theme.strip()
        session['world_theme'] = world_theme
        with open('book_output/world.txt', 'w') as f:
            f.write(world_theme)
        
        return jsonify({'world_theme': world_theme})
    
    # GET request - show world page with existing theme if available
    world_theme = ''
    if os.path.exists('book_output/world.txt'):
        with open('book_output/world.txt', 'r') as f:
            world_theme = f.read().strip()
        session['world_theme'] = world_theme
    
    return render_template('world.html', world_theme=world_theme, topic=session.get('topic', ''))

@app.route('/save_world', methods=['POST'])
def save_world():
    """Save edited world theme"""
    world_theme = request.form.get('world_theme')
    
    # Strip extra newlines at the beginning and normalize newlines
    world_theme = world_theme.strip()
    
    # Save to session
    session['world_theme'] = world_theme
    
    # Save to file
    with open('book_output/world.txt', 'w') as f:
        f.write(world_theme)
    
    return jsonify({'success': True})

@app.route('/characters', methods=['GET', 'POST'])
def characters():
    """Generate or display characters"""
    if request.method == 'POST':
        num_characters = int(request.form.get('num_characters', 3))
        world_theme = session.get('world_theme', '')
        
        if not world_theme:
            return jsonify({'error': 'World theme not found. Please generate a world theme first.'})
        
        # Initialize agents for character creation
        book_agents = BookAgents(agent_config)
        agents = book_agents.create_agents(world_theme, 0)
        
        # Generate characters using the character_generator agent
        characters_content = book_agents.generate_content(
            "character_generator",
            prompts.CHARACTER_CREATION_PROMPT.format(
                world_theme=world_theme,
                num_characters=num_characters
            )
        )
        
        # Clean and save characters to session and file
        characters_content = characters_content.strip()
        session['characters'] = characters_content
        with open('book_output/characters.txt', 'w') as f:
            f.write(characters_content)
        
        return jsonify({'characters': characters_content})
    
    # GET request - show characters page with existing characters if available
    characters_content = ''
    if os.path.exists('book_output/characters.txt'):
        with open('book_output/characters.txt', 'r') as f:
            characters_content = f.read().strip()
        session['characters'] = characters_content
    
    # Load world theme from file if it exists
    world_theme = ''
    if os.path.exists('book_output/world.txt'):
        with open('book_output/world.txt', 'r') as f:
            world_theme = f.read().strip()
    # If not available from file, try from session
    else:
        world_theme = session.get('world_theme', '')
    
    return render_template('characters.html', 
                           characters=characters_content, 
                           world_theme=world_theme)

@app.route('/save_characters', methods=['POST'])
def save_characters():
    """Save edited characters"""
    characters_content = request.form.get('characters')
    
    # Strip extra newlines at the beginning and normalize newlines
    characters_content = characters_content.strip()
    
    # Save to session
    session['characters'] = characters_content
    
    # Save to file
    with open('book_output/characters.txt', 'w') as f:
        f.write(characters_content)
    
    return jsonify({'success': True})

@app.route('/outline', methods=['GET', 'POST'])
def outline():
    """Generate or display book outline"""
    # Ensure we have the latest world data and characters from files if they exist
    world_theme = ''
    characters = ''
    
    # Try to load data from files first
    if os.path.exists('book_output/world.txt'):
        with open('book_output/world.txt', 'r') as f:
            file_content = f.read().strip()
            if file_content:  # Make sure we don't assign empty content
                world_theme = file_content
                session['world_theme'] = world_theme
    
    # If not loaded from file, try from session
    if not world_theme:
        session_content = session.get('world_theme', '')
        if session_content:
            world_theme = session_content
    
    # Try to load characters from file
    if os.path.exists('book_output/characters.txt'):
        with open('book_output/characters.txt', 'r') as f:
            file_content = f.read().strip()
            if file_content:  # Make sure we don't assign empty content
                characters = file_content
                session['characters'] = characters
    
    # If not loaded from file, try from session
    if not characters:
        session_content = session.get('characters', '')
        if session_content:
            characters = session_content
    
    # Ensure data is properly cleaned
    world_theme = world_theme.strip() if world_theme else ''
    characters = characters.strip() if characters else ''
    
    # Print diagnostics to help debug
    print(f"World theme loaded: {bool(world_theme)}, Characters loaded: {bool(characters)}")
    print(f"World theme length: {len(world_theme)}, Characters length: {len(characters)}")
    
    # Force a valid value even if there are issues
    if not characters and os.path.exists('book_output/characters.txt'):
        try:
            with open('book_output/characters.txt', 'rb') as f:
                characters = f.read().decode('utf-8', errors='ignore').strip()
                if not characters and len(characters) < 10:
                    # Add a fallback value
                    characters = "CHARACTER_PROFILES:\n\nDefault character - please regenerate characters."
        except Exception as e:
            print(f"Error reading characters file: {e}")
    
    if not world_theme and os.path.exists('book_output/world.txt'):
        try:
            with open('book_output/world.txt', 'rb') as f:
                world_theme = f.read().decode('utf-8', errors='ignore').strip()
                if not world_theme and len(world_theme) < 10:
                    # Add a fallback value
                    world_theme = "WORLD_ELEMENTS:\n\nDefault world - please regenerate world setting."
        except Exception as e:
            print(f"Error reading world file: {e}")
    
    if request.method == 'POST':
        num_chapters = int(request.form.get('num_chapters', 10))
        
        # Verify we have the necessary data before proceeding
        if not world_theme or not characters:
            return jsonify({'error': 'World theme or characters not found. Please complete previous steps first.'})
        
        # Initialize agents for outline generation
        book_agents = BookAgents(agent_config)
        agents = book_agents.create_agents(world_theme, num_chapters)
        
        # Generate outline using the prompt
        outline_content = book_agents.generate_content(
            "outline_creator",
            prompts.OUTLINE_GENERATION_PROMPT.format(
                world_theme=world_theme,
                characters=characters,
                num_chapters=num_chapters
            )
        )
        
        # Parse the outline into a structured format
        chapters = []
        try:
            # Extract just the outline content (between OUTLINE: and END OF OUTLINE)
            start_idx = outline_content.find('OUTLINE:')
            end_idx = outline_content.find('END OF OUTLINE')
            if start_idx != -1 and end_idx != -1:
                outline_text = outline_content[start_idx + len('OUTLINE:'):end_idx].strip()
            else:
                outline_text = outline_content
            
            # Split by chapter
            chapter_blocks = []
            for i in range(1, num_chapters + 1):
                chapter_marker = f"Chapter {i}:"
                next_chapter_marker = f"Chapter {i+1}:" if i < num_chapters else "END OF OUTLINE"
                
                start = outline_text.find(chapter_marker)
                if start == -1:
                    continue  # This chapter marker wasn't found
                
                end = outline_text.find(next_chapter_marker, start)
                if end == -1:
                    end = len(outline_text)  # Last chapter
                
                chapter_blocks.append(outline_text[start:end].strip())
            
            # Process each chapter block to extract info
            for i, block in enumerate(chapter_blocks, 1):
                lines = block.split('\n')
                if not lines:
                    continue
                
                # Extract title from first line
                title_line = lines[0]
                title = title_line.replace(f"Chapter {i}:", "").strip()
                
                # The rest is the chapter content/prompt
                chapter_content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                
                chapters.append({
                    'chapter_number': i,
                    'title': title,
                    'prompt': chapter_content
                })
            
            # If parsing fails or produces no chapters, use a fallback
            if not chapters:
                for i in range(1, num_chapters + 1):
                    chapters.append({
                        'chapter_number': i,
                        'title': f"Chapter {i}",
                        'prompt': f"Content for chapter {i}"
                    })
                    
        except Exception as e:
            # Fallback if parsing fails
            print(f"Error parsing outline: {e}")
            for i in range(1, num_chapters + 1):
                chapters.append({
                    'chapter_number': i,
                    'title': f"Chapter {i}",
                    'prompt': f"Content for chapter {i}"
                })
        
        # Clean and save outline to session and file
        outline_content = outline_content.strip()
        session['outline'] = outline_content
        session['chapters'] = chapters
        with open('book_output/outline.txt', 'w') as f:
            f.write(outline_content)
        
        # Save structured outline for later use
        with open('book_output/outline.json', 'w') as f:
            json.dump(chapters, f, indent=2)
        
        return jsonify({'outline': outline_content, 'chapters': chapters})
    
    # GET request - show outline page with existing outline if available
    outline_content = ''
    chapters = []
    
    if os.path.exists('book_output/outline.txt'):
        with open('book_output/outline.txt', 'r') as f:
            outline_content = f.read().strip()
        session['outline'] = outline_content
    
    if os.path.exists('book_output/outline.json'):
        with open('book_output/outline.json', 'r') as f:
            chapters = json.load(f)
        session['chapters'] = chapters
    
    return render_template('outline.html', 
                           outline=outline_content, 
                           chapters=chapters,
                           world_theme=world_theme,
                           characters=characters)

@app.route('/save_outline', methods=['POST'])
def save_outline():
    """Save edited outline"""
    outline_content = request.form.get('outline')
    
    # Strip extra newlines at the beginning and normalize newlines
    outline_content = outline_content.strip()
    
    # Save to session
    session['outline'] = outline_content
    
    # Save to file
    with open('book_output/outline.txt', 'w') as f:
        f.write(outline_content)
    
    # You would also need to update the structured chapters data here
    # This is simplified - you'd need to parse the outline to update chapters
    
    return jsonify({'success': True})

@app.route('/chapter/<int:chapter_number>', methods=['GET', 'POST'])
def chapter(chapter_number):
    """Generate or display a specific chapter"""
    chapters = session.get('chapters', [])
    
    # If no chapters in session, try to load from file
    if not chapters and os.path.exists('book_output/outline.json'):
        with open('book_output/outline.json', 'r') as f:
            chapters = json.load(f)
            session['chapters'] = chapters
    
    # Check if chapter exists
    chapter_data = None
    for ch in chapters:
        if ch['chapter_number'] == chapter_number:
            chapter_data = ch
            break
    
    if not chapter_data:
        return render_template('error.html', message=f"Chapter {chapter_number} not found")
    
    if request.method == 'POST':
        # Generate chapter content
        world_theme = session.get('world_theme', '')
        characters = session.get('characters', '')
        outline = session.get('outline', '')
        
        # Get previous chapters context
        previous_context = ""
        if chapter_number > 1:
            prev_chapter_path = f'book_output/chapters/chapter_{chapter_number-1}.txt'
            if os.path.exists(prev_chapter_path):
                with open(prev_chapter_path, 'r') as f:
                    # Get a summary or the last few paragraphs
                    content = f.read()
                    previous_context = content[-1000:] if len(content) > 1000 else content
        
        # Initialize agents for chapter generation
        book_agents = BookAgents(agent_config, chapters)
        agents = book_agents.create_agents(world_theme, len(chapters))
        
        # Generate the chapter
        chapter_content = book_agents.generate_content(
            "writer",
            prompts.CHAPTER_GENERATION_PROMPT.format(
                chapter_number=chapter_number,
                chapter_title=chapter_data['title'],
                chapter_outline=chapter_data['prompt'],
                world_theme=world_theme,
                relevant_characters=characters,  # You might want to filter for relevant characters only
                scene_details="",  # This would be filled if scenes were generated first
                previous_context=previous_context
            )
        )
        
        # Clean and save chapter content
        chapter_content = chapter_content.strip()
        chapter_path = f'book_output/chapters/chapter_{chapter_number}.txt'
        with open(chapter_path, 'w') as f:
            f.write(chapter_content)
        
        return jsonify({'chapter_content': chapter_content})
    
    # GET request - show chapter page with existing content if available
    chapter_content = ''
    chapter_path = f'book_output/chapters/chapter_{chapter_number}.txt'
    if os.path.exists(chapter_path):
        with open(chapter_path, 'r') as f:
            chapter_content = f.read().strip()
    
    return render_template('chapter.html', 
                           chapter=chapter_data,
                           chapter_content=chapter_content,
                           chapters=chapters)

@app.route('/save_chapter/<int:chapter_number>', methods=['POST'])
def save_chapter(chapter_number):
    """Save edited chapter content"""
    chapter_content = request.form.get('chapter_content')
    
    # Strip extra newlines at the beginning and normalize newlines
    chapter_content = chapter_content.strip()
    
    chapter_path = f'book_output/chapters/chapter_{chapter_number}.txt'
    with open(chapter_path, 'w') as f:
        f.write(chapter_content)
    
    return jsonify({'success': True})

@app.route('/scene/<int:chapter_number>', methods=['GET', 'POST'])
def scene(chapter_number):
    """Generate a scene for a specific chapter"""
    chapters = session.get('chapters', [])
    
    # Find chapter data
    chapter_data = None
    for ch in chapters:
        if ch['chapter_number'] == chapter_number:
            chapter_data = ch
            break
    
    if not chapter_data:
        return render_template('error.html', message=f"Chapter {chapter_number} not found")
    
    if request.method == 'POST':
        scene_description = request.form.get('scene_description', '')
        
        # Generate the scene
        world_theme = session.get('world_theme', '')
        characters = session.get('characters', '')
        
        # Get previous context
        previous_context = ""
        if chapter_number > 1:
            prev_chapter_path = f'book_output/chapters/chapter_{chapter_number-1}.txt'
            if os.path.exists(prev_chapter_path):
                with open(prev_chapter_path, 'r') as f:
                    content = f.read()
                    previous_context = content[-1000:] if len(content) > 1000 else content
        
        # Initialize agents
        book_agents = BookAgents(agent_config, chapters)
        agents = book_agents.create_agents(world_theme, len(chapters))
        
        # Generate the scene
        scene_content = book_agents.generate_content(
            "writer",
            prompts.SCENE_GENERATION_PROMPT.format(
                chapter_number=chapter_number,
                chapter_title=chapter_data['title'],
                chapter_outline=chapter_data['prompt'],
                world_theme=world_theme,
                relevant_characters=characters,
                previous_context=previous_context
            )
        )
        
        # Save scene to a file
        scene_dir = f'book_output/chapters/chapter_{chapter_number}_scenes'
        os.makedirs(scene_dir, exist_ok=True)
        
        # Count existing scenes and create a new one
        scene_count = len([f for f in os.listdir(scene_dir) if f.endswith('.txt')])
        scene_path = f'{scene_dir}/scene_{scene_count + 1}.txt'
        
        with open(scene_path, 'w') as f:
            f.write(scene_content)
        
        return jsonify({'scene_content': scene_content})
    
    # GET request - load existing scenes for this chapter
    scenes = []
    scene_dir = f'book_output/chapters/chapter_{chapter_number}_scenes'
    
    if os.path.exists(scene_dir):
        scene_files = [f for f in os.listdir(scene_dir) if f.endswith('.txt')]
        scene_files.sort(key=lambda f: int(f.split('_')[1].split('.')[0]))  # Sort by scene number
        
        for scene_file in scene_files:
            scene_path = os.path.join(scene_dir, scene_file)
            scene_number = int(scene_file.split('_')[1].split('.')[0])
            
            with open(scene_path, 'r') as f:
                content = f.read()
                
                # Extract a title from the first line or first few words
                lines = content.split('\n')
                if lines:
                    title = lines[0][:30] + '...' if len(lines[0]) > 30 else lines[0]
                else:
                    title = f"Scene {scene_number}"
                
                scenes.append({
                    'number': scene_number,
                    'title': title,
                    'content': content
                })
    
    # Return the template with loaded scenes
    return render_template('scene.html', 
                           chapter=chapter_data,
                           scenes=scenes)

if __name__ == '__main__':
    app.run(debug=True) 