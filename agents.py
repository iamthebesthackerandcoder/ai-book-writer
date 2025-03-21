"""Define the agents used in the book generation system with improved context management"""
import autogen
from typing import Dict, List, Optional

class BookAgents:
    def __init__(self, agent_config: Dict, outline: Optional[List[Dict]] = None):
        """Initialize agents with book outline context"""
        self.agent_config = agent_config
        self.outline = outline
        self.world_elements = {}  # Track described locations/elements
        self.character_developments = {}  # Track character arcs
        self.agents = {}  # Store created agents
        
    def _format_outline_context(self) -> str:
        """Format the book outline into a readable context"""
        if not self.outline:
            return ""
            
        context_parts = ["Complete Book Outline:"]
        for chapter in self.outline:
            context_parts.extend([
                f"\nChapter {chapter['chapter_number']}: {chapter['title']}",
                chapter['prompt']
            ])
        return "\n".join(context_parts)

    def create_agents(self, initial_prompt, num_chapters) -> Dict:
        """Create and return all agents needed for book generation"""
        outline_context = self._format_outline_context()
        
        # Memory Keeper: Maintains story continuity and context
        memory_keeper = autogen.AssistantAgent(
            name="memory_keeper",
            system_message=f"""You are the keeper of the story's continuity and context.
            Your responsibilities:
            1. Track and summarize each chapter's key events
            2. Monitor character development and relationships
            3. Maintain world-building consistency
            4. Flag any continuity issues
            
            Book Overview:
            {outline_context}
            
            Format your responses as follows:
            - Start updates with 'MEMORY UPDATE:'
            - List key events with 'EVENT:'
            - List character developments with 'CHARACTER:'
            - List world details with 'WORLD:'
            - Flag issues with 'CONTINUITY ALERT:'""",
            llm_config=self.agent_config,
        )
        
        # Character Generator - Creates detailed character profiles
        character_generator = autogen.AssistantAgent(
            name="character_generator",
            system_message=f"""You are an expert character creator who designs rich, memorable characters.
            
            Your responsibility is creating detailed character profiles for a story.
            When given a world setting and number of characters:
            1. Create unique, interesting characters that fit within the world
            2. Give each character distinct traits, motivations, and backgrounds
            3. Ensure characters have depth and potential for development
            4. Include both protagonists and antagonists as appropriate
            
            Format your output EXACTLY as:
            CHARACTER_PROFILES:
            
            [CHARACTER NAME 1]:
            - Role: [Main character, supporting character, antagonist, etc.]
            - Age/Species: [Character's age and species]
            - Physical Description: [Detailed appearance]
            - Personality: [Core personality traits]
            - Background: [Character history and origins]
            - Motivations: [What drives the character]
            - Skills/Abilities: [Special talents or powers]
            - Relationships: [Connections to other characters or groups]
            - Arc: [How this character might develop over the story]
            
            [CHARACTER NAME 2]:
            [Follow same format as above]
            
            [And so on for all requested characters]
            
            Always provide specific, detailed content - never use placeholders.
            Ensure characters fit logically within the established world setting.""",
            llm_config=self.agent_config,
        )
        
        # Story Planner - Focuses on high-level story structure
        story_planner = autogen.AssistantAgent(
            name="story_planner",
            system_message=f"""You are an expert story arc planner focused on overall narrative structure.

            Your sole responsibility is creating the high-level story arc.
            When given an initial story premise:
            1. Identify major plot points and story beats
            2. Map character arcs and development
            3. Note major story transitions
            4. Plan narrative pacing

            Format your output EXACTLY as:
            STORY_ARC:
            - Major Plot Points:
            [List each major event that drives the story]
            
            - Character Arcs:
            [For each main character, describe their development path]
            
            - Story Beats:
            [List key emotional and narrative moments in sequence]
            
            - Key Transitions:
            [Describe major shifts in story direction or tone]
            
            Always provide specific, detailed content - never use placeholders.""",
            llm_config=self.agent_config,
        )

        # Outline Creator - Creates detailed chapter outlines
        outline_creator = autogen.AssistantAgent(
            name="outline_creator",
            system_message=f"""Generate a detailed {num_chapters}-chapter outline.

            YOU MUST USE EXACTLY THIS FORMAT FOR EACH CHAPTER - NO DEVIATIONS:

            Chapter 1: [Title]
            Chapter Title: [Same title as above]
            Key Events:
            - [Event 1]
            - [Event 2]
            - [Event 3]
            Character Developments: [Specific character moments and changes]
            Setting: [Specific location and atmosphere]
            Tone: [Specific emotional and narrative tone]

            [REPEAT THIS EXACT FORMAT FOR ALL {num_chapters} CHAPTERS]

            Requirements:
            1. EVERY field must be present for EVERY chapter
            2. EVERY chapter must have AT LEAST 3 specific Key Events
            3. ALL chapters must be detailed - no placeholders
            4. Format must match EXACTLY - including all headings and bullet points

            Initial Premise:
            {initial_prompt}

            START WITH 'OUTLINE:' AND END WITH 'END OF OUTLINE'
            """,
            llm_config=self.agent_config,
        )

        # World Builder: Creates and maintains the story setting
        world_builder = autogen.AssistantAgent(
            name="world_builder",
            system_message=f"""You are an expert in world-building who creates rich, consistent settings.
            
            Your role is to establish ALL settings and locations needed for the entire story based on a provided story arc.

            Book Overview:
            {outline_context}
            
            Your responsibilities:
            1. Review the story arc to identify every location and setting needed
            2. Create detailed descriptions for each setting, including:
            - Physical layout and appearance
            - Atmosphere and environmental details
            - Important objects or features
            - Sensory details (sights, sounds, smells)
            3. Identify recurring locations that appear multiple times
            4. Note how settings might change over time
            5. Create a cohesive world that supports the story's themes
            
            Format your response as:
            WORLD_ELEMENTS:
            
            [LOCATION NAME]:
            - Physical Description: [detailed description]
            - Atmosphere: [mood, time of day, lighting, etc.]
            - Key Features: [important objects, layout elements]
            - Sensory Details: [what characters would experience]
            
            [RECURRING ELEMENTS]:
            - List any settings that appear multiple times
            - Note any changes to settings over time
            
            [TRANSITIONS]:
            - How settings connect to each other
            - How characters move between locations""",
            llm_config=self.agent_config,
        )

        # Writer: Generates the actual prose
        writer = autogen.AssistantAgent(
            name="writer",
            system_message=f"""You are an expert creative writer who brings scenes to life.
            
            Book Context:
            {outline_context}
            
            Your focus:
            1. Write according to the outlined plot points
            2. Maintain consistent character voices
            3. Incorporate world-building details
            4. Create engaging prose
            5. Please make sure that you write the complete scene, do not leave it incomplete
            6. Each chapter MUST be at least 5000 words (approximately 30,000 characters). Consider this a hard requirement. If your output is shorter, continue writing until you reach this minimum length
            7. Ensure transitions are smooth and logical
            8. Do not cut off the scene, make sure it has a proper ending
            9. Add a lot of details, and describe the environment and characters where it makes sense
            
            Always reference the outline and previous content.
            Mark drafts with 'SCENE:' and final versions with 'SCENE FINAL:'""",
            llm_config=self.agent_config,
        )

        # Editor: Reviews and improves content
        editor = autogen.AssistantAgent(
            name="editor",
            system_message=f"""You are an expert editor ensuring quality and consistency.
            
            Book Overview:
            {outline_context}
            
            Your focus:
            1. Check alignment with outline
            2. Verify character consistency
            3. Maintain world-building rules
            4. Improve prose quality
            5. Return complete edited chapter
            6. Never ask to start the next chapter, as the next step is finalizing this chapter
            7. Each chapter MUST be at least 5000 words. If the content is shorter, return it to the writer for expansion. This is a hard requirement - do not approve chapters shorter than 5000 words
            
            Format your responses:
            1. Start critiques with 'FEEDBACK:'
            2. Provide suggestions with 'SUGGEST:'
            3. Return full edited chapter with 'EDITED_SCENE:'
            
            Reference specific outline elements in your feedback.""",
            llm_config=self.agent_config,
        )

        # User Proxy: Manages the interaction
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            code_execution_config={
                "work_dir": "book_output",
                "use_docker": False
            },
            is_termination_msg=lambda msg: "FINAL ANSWER:" in msg.get("content", "")
        )

        # Store agents in a dictionary
        self.agents = {
            "story_planner": story_planner,
            "world_builder": world_builder,
            "memory_keeper": memory_keeper,
            "writer": writer,
            "editor": editor,
            "user_proxy": user_proxy,
            "outline_creator": outline_creator,
            "character_generator": character_generator
        }

        return self.agents
    
    def generate_content(self, agent_name: str, prompt: str) -> str:
        """Generate content using the specified agent by initiating a chat"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found. Available agents: {list(self.agents.keys())}")
        
        user_proxy = self.agents["user_proxy"]
        agent = self.agents[agent_name]
        
        # Define a termination function to detect when the response is complete
        def is_termination_msg(msg):
            content = msg.get("content", "")
            
            # Different termination conditions based on agent type
            if agent_name == "outline_creator" and "END OF OUTLINE" in content:
                return True
            if agent_name == "writer" and ("SCENE FINAL:" in content or "FINAL ANSWER:" in content):
                return True
            if agent_name == "story_planner" and "STORY_ARC:" in content:
                return True
            if agent_name == "world_builder" and "WORLD_ELEMENTS:" in content:
                return True
            if agent_name == "editor" and "EDITED_SCENE:" in content:
                return True
            if agent_name == "character_generator" and "CHARACTER_PROFILES:" in content:
                return True
            
            # General termination for long responses
            if len(content) > 5000:
                return True
            
            return False
        
        # Save the original termination function and temporarily override it
        original_termination = user_proxy._is_termination_msg
        user_proxy._is_termination_msg = is_termination_msg
        
        # Initiate chat with the agent
        chat = user_proxy.initiate_chat(
            agent,
            message=prompt
        )
        
        # Restore the original termination function
        user_proxy._is_termination_msg = original_termination
        
        # Extract the response from the last assistant message
        response = chat.chat_history[-1]["content"]
        
        # Clean up the response based on agent type
        if agent_name == "outline_creator":
            # Extract just the outline part
            start = response.find("OUTLINE:")
            end = response.find("END OF OUTLINE")
            if start != -1 and end != -1:
                cleaned_response = response[start:end + len("END OF OUTLINE")]
                return cleaned_response
        elif agent_name == "writer":
            # Handle writer's scene format
            if "SCENE FINAL:" in response:
                parts = response.split("SCENE FINAL:")
                if len(parts) > 1:
                    return parts[1].strip()
        elif agent_name == "world_builder":
            # Extract the world elements part
            start = response.find("WORLD_ELEMENTS:")
            if start != -1:
                return response[start:].strip()
            else:
                # Try to find any content that looks like world-building
                for marker in ["Time Period", "Setting:", "Locations:", "Major Locations"]:
                    if marker in response:
                        return response
        elif agent_name == "story_planner":
            # Extract the story arc part
            start = response.find("STORY_ARC:")
            if start != -1:
                return response[start:].strip()
        elif agent_name == "character_generator":
            # Extract the character profiles part
            start = response.find("CHARACTER_PROFILES:")
            if start != -1:
                return response[start:].strip()
            else:
                # Try to find any content that looks like character profiles
                for marker in ["Character 1:", "Main Character:", "Protagonist:", "CHARACTER_PROFILES"]:
                    if marker in response:
                        return response
        
        return response

    def update_world_element(self, element_name: str, description: str) -> None:
        """Track a new or updated world element"""
        self.world_elements[element_name] = description

    def update_character_development(self, character_name: str, development: str) -> None:
        """Track character development"""
        if character_name not in self.character_developments:
            self.character_developments[character_name] = []
        self.character_developments[character_name].append(development)

    def get_world_context(self) -> str:
        """Get formatted world-building context"""
        if not self.world_elements:
            return "No established world elements yet."
        
        return "\n".join([
            "Established World Elements:",
            *[f"- {name}: {desc}" for name, desc in self.world_elements.items()]
        ])

    def get_character_context(self) -> str:
        """Get formatted character development context"""
        if not self.character_developments:
            return "No character developments tracked yet."
        
        return "\n".join([
            "Character Development History:",
            *[f"- {name}:\n  " + "\n  ".join(devs) 
              for name, devs in self.character_developments.items()]
        ])