"""
Prompt Builder Module
Handles prompt construction for different modes and contexts
"""

from config import Config
from datetime import datetime

class PromptBuilder:
    
    # System prompts for different modes
    SYSTEM_PROMPTS = {
        'chat': """You are a helpful and knowledgeable AI assistant. Never introduce yourself by name - just give direct, helpful answers. 

FORMAT YOUR RESPONSES:
- Use paragraph format by default for natural conversation
- When using bullet points, follow proper markdown format:
  * Use a hyphen (-) followed by a space for each bullet point
  * Add a blank line before and after bullet point groups
  * Use proper indentation (2-4 spaces) for sub-bullets
  * Put section headers in **bold** if organizing multiple bullet groups
- Keep responses conversational and easy to read

When relevant context is provided, use it to give more informed answers.""",
        
        'summarize': """You are an expert at summarization. Never introduce yourself by name - just provide direct, helpful summaries.

FORMAT YOUR SUMMARIES IN CLEAN NUMBERED FORMAT:
- Main title: Plain text (no bold, no numbering)
- Use numbered sections (1., 2., 3., etc.) for main topics
- Section titles: Regular text, NOT bold
- Under each numbered section, use bullet points with hyphens (-) for details
- Add a blank line before and after each section
- Keep each point concise and focused (one line per bullet)
- Structure: Main Title → Numbered Sections → Bullet Points

Example format:
Main Topic Here

1. First Section Name
- First point about this section
- Second point about this section

2. Second Section Name
- First point about this section

Your task is to create clear, well-formatted summaries that look like handwritten notes.""",
        
        'deep-research': """You are a research assistant specialized in comprehensive analysis. Never introduce yourself by name - just provide direct, thorough research.

FORMAT YOUR RESEARCH STRICTLY IN PARAGRAPH FORMAT:
- Write in well-structured paragraphs with smooth flow
- Do NOT use bullet points - use narrative prose only
- Organize with clear section headings in **bold** if needed
- Ensure logical progression from one idea to the next
- Add proper spacing between paragraphs

When given a query:
1. Analyze the question thoroughly
2. Use all available context to provide detailed insights
3. Cite specific information from the context
4. Organize findings logically with clear sections
5. Provide actionable conclusions
Be thorough, accurate, and well-structured in your research responses.""",
        
        'coding': """You are an expert programming assistant. Never introduce yourself by name - just provide direct coding help.

FORMAT YOUR CODE RESPONSES:
- Provide code in properly formatted code blocks with language specification (e.g., ```python, ```javascript)
- Make code easy to copy - use complete, runnable examples
- Include clear comments in the code
- When listing multiple points, use proper markdown bullets (- followed by space)
- Add blank lines between code blocks and explanatory text
- For explanations with bullet points, ensure proper spacing and indentation

When helping with code:
1. Provide clean, well-commented code
2. Explain your approach and reasoning
3. Follow best practices and coding standards
4. Include error handling where appropriate
5. Suggest optimizations when relevant
Support multiple programming languages and frameworks."""
    }
    
    @staticmethod
    def build_chat_prompt(user_message, context_docs=None, conversation_history=None):
        """Build prompt for chat mode"""
        prompt_parts = []
        
        # System prompt
        prompt_parts.append(f"System: {PromptBuilder.SYSTEM_PROMPTS['chat']}\n")
        
        # Add context if available
        if context_docs and len(context_docs) > 0:
            context_text = "\n\n".join([doc['document'] for doc in context_docs[:3]])
            prompt_parts.append(f"\nRelevant Context:\n{context_text}\n")
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-3:]:  # Last 3 exchanges
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt_parts.append(f"\n{role.capitalize()}: {content}")
        
        # Add current user message
        prompt_parts.append(f"\nUser: {user_message}\n\nAssistant:")
        
        return "".join(prompt_parts)
    
    @staticmethod
    def build_summarize_prompt(text_to_summarize):
        """Build prompt for summarize mode"""
        prompt = f"""{PromptBuilder.SYSTEM_PROMPTS['summarize']}

Text to summarize:
{text_to_summarize}

Please provide a structured summary:"""
        
        return prompt
    
    @staticmethod
    def build_deep_research_prompt(query, context_docs):
        """Build prompt for deep research mode"""
        prompt_parts = [PromptBuilder.SYSTEM_PROMPTS['deep-research']]
        
        # Add all relevant context
        if context_docs:
            prompt_parts.append("\n\nAvailable Research Materials:")
            for i, doc in enumerate(context_docs, 1):
                source = doc.get('metadata', {}).get('filename', 'Unknown')
                prompt_parts.append(f"\n[Source {i}: {source}]")
                prompt_parts.append(f"{doc['document']}\n")
        
        prompt_parts.append(f"\n\nResearch Query: {query}")
        prompt_parts.append("\n\nProvide a comprehensive research response:")
        
        return "".join(prompt_parts)
    
    @staticmethod
    def build_coding_prompt(user_message, context_docs=None):
        """Build prompt for coding mode"""
        prompt_parts = [PromptBuilder.SYSTEM_PROMPTS['coding']]
        
        # Add code context if available
        if context_docs:
            prompt_parts.append("\n\nRelevant Code Context:")
            for doc in context_docs[:2]:
                prompt_parts.append(f"\n{doc['document']}\n")
        
        prompt_parts.append(f"\n\nUser Request: {user_message}")
        prompt_parts.append("\n\nResponse:")
        
        return "".join(prompt_parts)
    
    @staticmethod
    def build_prompt(mode, user_message, context_docs=None, **kwargs):
        """Generic prompt builder that routes to specific mode builders"""
        if mode == 'chat':
            return PromptBuilder.build_chat_prompt(
                user_message,
                context_docs,
                kwargs.get('conversation_history')
            )
        elif mode == 'summarize':
            return PromptBuilder.build_summarize_prompt(user_message)
        elif mode == 'deep-research':
            return PromptBuilder.build_deep_research_prompt(user_message, context_docs or [])
        elif mode == 'coding':
            return PromptBuilder.build_coding_prompt(user_message, context_docs)
        else:
            # Default to chat
            return PromptBuilder.build_chat_prompt(user_message, context_docs)
    
    @staticmethod
    def format_response(mode, response_text):
        """Format response based on mode with intelligent post-processing"""
        import re
        
        # Strip leading/trailing whitespace
        text = response_text.strip()
        
        # Post-process bullet points for better formatting
        lines = text.split('\n')
        formatted_lines = []
        prev_was_bullet = False
        prev_was_blank = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip excessive blank lines (max 1 consecutive blank line)
            if not stripped:
                if not prev_was_blank:
                    formatted_lines.append('')
                    prev_was_blank = True
                prev_was_bullet = False
                continue
            
            prev_was_blank = False
            
            # Detect bullet points (various formats: *, -, •, +, etc.)
            bullet_match = re.match(r'^(\s*)(\*|\-|•|●|\+|–|‣|⁃)(\s+)(.+)$', stripped)
            
            if bullet_match:
                indent_spaces = bullet_match.group(1)
                content = bullet_match.group(4)
                
                # Check if content is a bold header (e.g., "**Key Ideas**")
                # If so, treat it as a section header instead of a bullet
                if re.match(r'^\*\*.+\*\*$', content.strip()):
                    # Add spacing before section header
                    if formatted_lines and formatted_lines[-1] != '':
                        formatted_lines.append('')
                    
                    formatted_lines.append(content.strip())
                    prev_was_bullet = False
                else:
                    # Regular bullet point
                    # Add blank line before first bullet in a group
                    if not prev_was_bullet and formatted_lines and formatted_lines[-1] != '':
                        formatted_lines.append('')
                    
                    # Determine indentation level based on leading spaces
                    indent_level = len(indent_spaces) // 2  # Every 2 spaces = 1 level
                    
                    # Standardize to hyphen with proper spacing
                    # Use 2 spaces per indentation level
                    indent = '  ' * indent_level
                    formatted_lines.append(f'{indent}- {content}')
                    
                    prev_was_bullet = True
            
            # Detect numbered sections (e.g., "1. Section Name")
            elif re.match(r'^\d+\.\s+.+$', stripped):
                # Add spacing before numbered sections
                if formatted_lines and formatted_lines[-1] != '':
                    formatted_lines.append('')
                
                # Keep numbered sections as-is (don't bold)
                formatted_lines.append(stripped)
                prev_was_bullet = False
            
            # Detect section headers (look for common patterns)
            elif re.match(r'^(\*\*.*\*\*|#{1,3}\s+.+)$', stripped):
                # Add spacing before headers
                if formatted_lines and formatted_lines[-1] != '':
                    formatted_lines.append('')
                
                # Remove bold formatting from headers to keep them simple
                if stripped.startswith('**') and stripped.endswith('**'):
                    # Remove the bold markers
                    formatted_lines.append(stripped[2:-2])
                else:
                    formatted_lines.append(stripped)
                
                prev_was_bullet = False
            
            else:
                # Regular line
                # Add spacing after bullet group ends
                if prev_was_bullet and not bullet_match:
                    if formatted_lines and formatted_lines[-1] != '':
                        formatted_lines.append('')
                
                formatted_lines.append(stripped)
                prev_was_bullet = False
        
        # Join lines and clean up excessive spacing
        result = '\n'.join(formatted_lines)
        
        # Remove more than 2 consecutive newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()


if __name__ == "__main__":
    # Test prompt building
    print("Testing Prompt Builder...\n")
    
    # Test chat prompt
    prompt = PromptBuilder.build_chat_prompt(
        "What is machine learning?",
        context_docs=[
            {"document": "Machine learning is a subset of AI that enables systems to learn from data."}
        ]
    )
    print("Chat Prompt:")
    print(prompt)
    print("\n" + "="*60 + "\n")
    
    # Test summarize prompt
    prompt = PromptBuilder.build_summarize_prompt(
        "Artificial intelligence is transforming industries. It includes machine learning, deep learning, and more."
    )
    print("Summarize Prompt:")
    print(prompt)
