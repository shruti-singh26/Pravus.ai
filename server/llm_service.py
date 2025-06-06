from typing import Dict, List, Optional
import requests
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
import openai

from config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_CHAT_MODEL,
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_BASE,
    DEEPSEEK_MODEL,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_LLM_MAX_TOKENS
)

class OpenAILLM(LLM):
    """Custom LLM for OpenAI ChatGPT API."""
    
    api_key: str
    model: str = "gpt-3.5-turbo"
    temperature: float = DEFAULT_LLM_TEMPERATURE
    max_tokens: int = DEFAULT_LLM_MAX_TOKENS
    
    @property
    def _llm_type(self) -> str:
        return "openai_chat"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> str:
        """Call OpenAI ChatGPT API."""
        
        if not self.api_key:
            return self._generate_fallback_response(prompt)
        
        try:
            # Set the API key
            openai.api_key = self.api_key
            
            # Prepare the messages
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            print(f"Calling OpenAI ChatGPT with model: {self.model}")
            
            # Call OpenAI ChatCompletion API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=stop
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when API calls fail."""
        print("Generating fallback response without API")
        
        # Extract the question from the prompt
        question_match = None
        if "USER QUESTION:" in prompt:
            question_match = prompt.split("USER QUESTION:")[-1].strip()
        elif "USER:" in prompt:
            question_match = prompt.split("USER:")[-1].strip()
        
        # See if we can extract some context
        context_text = ""
        if "CONTEXT:" in prompt and question_match:
            context_parts = prompt.split("CONTEXT:")[1].split(question_match)[0].strip()
            # Extract a sample from the context
            if len(context_parts) > 200:
                context_text = context_parts[:200] + "..."
            else:
                context_text = context_parts
        
        # Create a basic response
        if question_match:
            if context_text:
                return (
                    f"I found some information that might help answer your question. "
                    f"The relevant part from the manual states: '{context_text}'\n\n"
                    f"Please note that I'm currently running in fallback mode due to API connectivity issues. "
                    f"For more detailed information, please try again later."
                )
            else:
                return (
                    f"I'm currently having trouble accessing the full response capabilities. "
                    f"Please check that your API key is correctly configured."
                )
        else:
            return (
                "I'm unable to generate a complete response at the moment due to API connectivity issues. "
                "Please ensure your API key is correctly set up or try again later."
            )

class DeepseekLLM(LLM):
    """Custom LLM for Deepseek API."""
    
    api_key: str
    api_base: str
    model: str = "deepseek-chat"
    temperature: float = DEFAULT_LLM_TEMPERATURE
    max_tokens: int = DEFAULT_LLM_MAX_TOKENS
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> str:
        """Call Deepseek API."""
        
        if not self.api_key:
            return self._generate_fallback_response(prompt)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            if stop:
                payload["stop"] = stop
            
            print(f"Calling Deepseek API with model: {self.model}")
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"Deepseek API error: {str(e)}")
            return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when API calls fail."""
        print("Generating fallback response without API")
        
        # Extract the question from the prompt
        question_match = None
        if "USER QUESTION:" in prompt:
            question_match = prompt.split("USER QUESTION:")[-1].strip()
        elif "USER:" in prompt:
            question_match = prompt.split("USER:")[-1].strip()
        
        # See if we can extract some context
        context_text = ""
        if "CONTEXT:" in prompt and question_match:
            context_parts = prompt.split("CONTEXT:")[1].split(question_match)[0].strip()
            # Extract a sample from the context
            if len(context_parts) > 200:
                context_text = context_parts[:200] + "..."
            else:
                context_text = context_parts
        
        # Create a basic response
        if question_match:
            if context_text:
                return (
                    f"I found some information that might help answer your question. "
                    f"The relevant part from the manual states: '{context_text}'\n\n"
                    f"Please note that I'm currently running in fallback mode due to API connectivity issues. "
                    f"For more detailed information, please try again later."
                )
            else:
                return (
                    f"I'm currently having trouble accessing the full response capabilities. "
                    f"Please check that your Deepseek API key is correctly configured."
                )
        else:
            return (
                "I'm unable to generate a complete response at the moment due to API connectivity issues. "
                "Please ensure your Deepseek API key is correctly set up or try again later."
            )

class LLMService:
    """Service for generating responses using either OpenAI or Deepseek based on configuration."""
    
    def __init__(self):
        # Initialize LLM based on provider selection
        if LLM_PROVIDER == 'deepseek':
            self.llm = DeepseekLLM(
                api_key=DEEPSEEK_API_KEY,
                api_base=DEEPSEEK_API_BASE,
                model=DEEPSEEK_MODEL
            )
            
            # Log configuration status
            if DEEPSEEK_API_KEY:
                print(f"✅ Deepseek LLM configured with model: {DEEPSEEK_MODEL}")
            else:
                print("❌ WARNING: DEEPSEEK_API_KEY is not configured. The system will operate in fallback mode.")
                print("To use Deepseek, please set your DEEPSEEK_API_KEY environment variable.")
        
        else:  # Default to OpenAI
            self.llm = OpenAILLM(
                api_key=OPENAI_API_KEY,
                model=OPENAI_CHAT_MODEL
            )
            
            # Log configuration status
            if OPENAI_API_KEY:
                print(f"✅ OpenAI ChatGPT configured with model: {OPENAI_CHAT_MODEL}")
            else:
                print("❌ WARNING: OPENAI_API_KEY is not configured. The system will operate in fallback mode.")
                print("To use OpenAI, please set your OPENAI_API_KEY environment variable.")
        
        print(f"🔧 LLM Provider: {LLM_PROVIDER.upper()}")
        
        # Create prompt templates
        self.qa_template = self._create_qa_template()
    
    def _create_qa_template(self) -> PromptTemplate:
        """Create the Q&A prompt template for OpenAI."""
        template = """You are a professional, highly efficient, and empathetic AI Assistant. Your primary directive is to provide accurate and relevant information to the user based on the manuals and documentation you have been provided.You are helping users with questions about a specific **appliance model**

Beyond simply retrieving information, your critical secondary role is to understand the user's underlying scenario, intent, and emotional state.

To achieve this:

1. Prioritize Manual Feed: Always attempt to find the answer directly within your provided manual feed first. If a direct answer is found, present it clearly and concisely also Format your response for safety.

2. Contextual Understanding:

    Analyze the Current Conversation: Continuously track the user's questions, previous statements, and the overall flow of the dialogue to grasp the full context of their inquiry.
    Identify User Scenario: Based on the conversation, try to infer the specific situation or problem the user is trying to solve. What is their ultimate goal?
    Assess Tonality and Urgency: Pay close attention to the user's language, word choice, and phrasing to detect their emotional state (e.g., frustrated, confused, urgent, calm) and adjust your response accordingly.
     
3. Intelligent Suggestions & Help:
     If a direct answer from the manual feed is insufficient or doesn't fully address the inferred scenario:
     Offer Additional Relevant Information: Provide related details from the manual that might be helpful, even if not directly asked for.
     Suggest Next Steps/Troubleshooting: Propose logical actions or troubleshooting steps based on the user's inferred problem.
    Ask Clarifying Questions: If the user's request is ambiguous or the scenario is unclear, ask precise and helpful questions to gain more context.
    Proactive Problem Solving: If you identify a potential issue based on the conversation, proactively suggest a solution or a path to resolution.
    Acknowledge Emotional State: If the user seems frustrated or confused, acknowledge their feelings gently and reassuringly, e.g., "I understand this can be a bit confusing, let's break it down."
 
4.Communication Style:
    Clear and Concise: Deliver information in an easy-to-understand manner, avoiding jargon where possible unless it's explicitly part of the manual.
    Professional and Respectful: Maintain a polite, helpful, and professional tone at all times.
    Empathetic: Show understanding and patience, especially when dealing with complex or frustrating issues.
    Action-Oriented: Guide the user towards solutions or further actions.
    
5.Handling "Out of Manual" Queries:
   If a question falls completely outside your manual feed and your ability to infer a helpful scenario, politely state that the information is not within your current knowledge base and suggest alternative resources if appropriate (e.g., "This specific detail isn't covered in my current documentation. Would you like me to clarify something else related to [topic]?").
   
   
Constraint: Do not make up information. Always base your answers on your provided manual feed or logical inferences derived from that manual feed and the user's stated context.
         

LANGUAGE REQUIREMENT:
Your response must be written in the following language: {response_language}

Language codes:
- en = English
- hi = Hindi (हिंदी)
- es = Spanish (Español)
- pl = Polish (Polski)

If the response_language is not "en" (English), you MUST write your entire response in that language. Use proper grammar, vocabulary, and cultural context for that language.

EXPERTISE AREAS:
You are trained to assist in the following areas:
- Installation and setup
- Operation and features
- Temperature control and settings
- Energy efficiency tips
- Maintenance and cleaning
- Troubleshooting common issues
- Error codes and diagnostics
- Storage recommendations
- Safety guidelines

FORMATTING RULES:
1. Highlight important terms with **bold**
   Example: **temperature control**, **water filter**
2. Format warnings and cautions with > and ⚠️
   Example:
   > ⚠️ **Warning:** Unplug the unit before cleaning
3. Use numbered steps for procedures
4. Use bullet points for features or options
5. Include page references [Page X] for information sources
6. Keep paragraphs short and focused

RESPONSE GUIDELINES:
- Base answers ONLY on the provided manual content
- If information isn't in the manual, respond in the requested language with an appropriate equivalent of: "I'm sorry, the manual does not provide information on that topic."
- Keep language professional but easy to understand
- Include relevant safety warnings where applicable
- Reference specific features only if mentioned in context
- Organize complex answers with clear sections
- CRITICAL: Write your entire response in the language specified by response_language

MANUAL CONTEXT:
{context}

USER QUESTION: {question}

Remember:
- Stay strictly within the manual's content
- Prioritize safety information
- Be clear and concise
- Use proper formatting for clarity
- Include page references when possible
- RESPOND IN THE LANGUAGE SPECIFIED: {response_language}

Your response (in {response_language}):"""
        
        prompt = PromptTemplate.from_template(template)
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def _create_direct_template(self) -> PromptTemplate:
        """Create a direct question template for when no manual context is available."""
        template = """You are Pravus, an AI assistant specialized in electronic devices and technical documentation.

LANGUAGE REQUIREMENT:
Your response must be written in the following language: {response_language}

Language codes:
- en = English
- hi = Hindi (हिंदी) 
- es = Spanish (Español)
- pl = Polish (Polski)

If the response_language is not "en" (English), you MUST write your entire response in that language.

Answer the user's question about electronic devices based on your general knowledge.
Make it clear to the user that you don't have any specific manuals in your database yet and encourage them to upload one for more specific help.
If you don't know the specific answer, provide helpful general guidance about similar devices or common electronic principles.
Be specific, concise, and practical in your advice.

Format your responses with proper structure:
- Use short paragraphs with clear spacing between them
- Use bullet points for lists of steps, features, or items
- Use bold formatting for important terms with **term**
- Include proper headings with ## for sections if your answer has multiple parts
- Make sure instructions are clear and numbered when providing a sequence of steps

USER QUESTION: {question}

Your answer (in {response_language}):"""
        
        prompt = PromptTemplate.from_template(template)
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def _format_response(self, text: str) -> str:
        """
        Clean up and format the LLM response for better readability.
        """
        # Remove unnecessary blank lines while preserving intentional spacing
        lines = text.split("\n")
        formatted_lines = []
        prev_line_empty = False
        
        for line in lines:
            line = line.rstrip()
            is_empty = not line.strip()
            
            # Special handling for headers and list items
            is_header = line.startswith('#')
            is_list_item = line.strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.'))
            
            # Add spacing before headers
            if is_header and formatted_lines and not prev_line_empty:
                formatted_lines.append('')
            
            # Add spacing before list items if not following another list item
            if is_list_item and formatted_lines and not prev_line_empty and not formatted_lines[-1].strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                formatted_lines.append('')
            
            # Skip multiple empty lines
            if is_empty:
                if not prev_line_empty:
                    formatted_lines.append('')
            else:
                formatted_lines.append(line)
            
            prev_line_empty = is_empty
        
        # Join lines and clean up
        text = '\n'.join(formatted_lines)
        
        # Ensure proper markdown formatting
        text = text.replace('**', '**')  # Fix any broken bold formatting
        text = text.replace('##', '##')  # Fix header formatting
        
        # Add proper spacing around block quotes
        text = text.replace('\n>', '\n\n>')
        
        # Ensure proper list formatting
        text = text.replace('\n- ', '\n\n- ')
        text = text.replace('\n* ', '\n\n* ')
        
        # Fix numbered list formatting
        for i in range(1, 10):
            text = text.replace(f'\n{i}. ', f'\n\n{i}. ')
        
        # Clean up any remaining multiple consecutive new lines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        return text.strip()
    
    def generate_response(
        self, 
        question: str, 
        context_docs: List[Document],
        brand: Optional[str] = None,
        model: Optional[str] = None,
        response_language: str = "en",
        use_fallback: bool = False
    ) -> Dict:
        """
        Generate a response to a question using context documents.
        
        Args:
            question: The user's question
            context_docs: List of context documents from vector search
            brand: Optional brand name to include in response
            model: Optional model name to include in response
            use_fallback: Whether to use direct LLM query when no documents are available
            
        Returns:
            Dict containing the generated response and metadata
        """
        if not context_docs:
            # Handle no context case
            if use_fallback:
                try:
                    # Create the direct template if it doesn't exist yet
                    if not hasattr(self, 'direct_template'):
                        self.direct_template = self._create_direct_template()
                    
                    # Generate response using direct template
                    result = self.direct_template.invoke({
                        "question": question,
                        "response_language": response_language
                    })
                    
                    # Extract text from result
                    if isinstance(result, dict) and 'text' in result:
                        response_text = result['text']
                    else:
                        response_text = str(result)
                    
                    # Format the response
                    formatted_result = self._format_response(response_text)
                    
                    return {
                        "response": formatted_result,
                        "sources": [],
                        "timestamp": None
                    }
                except Exception as e:
                    print(f"Error generating direct response: {str(e)}")
                    return {
                        "response": "I encountered an error processing your request. I can help with electronic device questions - try asking about common troubleshooting steps or device operations.",
                        "sources": [],
                        "timestamp": None
                    }
            else:
                # Traditional "no context" response
                response = "I don't have enough information to answer that question."
                
                if brand and model:
                    response += f" I don't have any manuals for {brand} {model}."
                elif brand:
                    response += f" I don't have any manuals for {brand}."
                elif not context_docs:
                    # If no docs at all, provide general guidance
                    response += " Please contact support if you need assistance with specific device manuals."
                
                return {
                    "response": response,
                    "sources": [],
                    "timestamp": None
                }
        
        try:
            # Get manual info from first document
            manual_info = {
                'brand': context_docs[0].metadata.get('brand', 'Unknown'),
                'model': context_docs[0].metadata.get('model', 'Unknown'),
                'product_type': context_docs[0].metadata.get('product_type', 'Unknown')
            }
            
            # Group content by sections and pages
            sections = {}
            for doc in context_docs:
                section = doc.metadata.get('section', 'General Information')
                page = doc.metadata.get('page', 'N/A')
                
                if section not in sections:
                    sections[section] = {}
                if page not in sections[section]:
                    sections[section][page] = []
                
                sections[section][page].append(doc)
            
            # Format context with clear structure
            context_text = "MANUAL REFERENCE:\n"
            context_text += f"Model: {manual_info['brand']} {manual_info['model']}\n"
            context_text += f"Type: {manual_info['product_type']}\n\n"
            
            # Add content by section and page
            for section_name, pages in sections.items():
                context_text += f"### {section_name}\n"
                
                # Sort pages numerically
                sorted_pages = sorted(pages.items(), key=lambda x: (
                    float('inf') if not str(x[0]).isdigit() else int(x[0])
                ))
                
                for page_num, page_docs in sorted_pages:
                    context_text += f"\n[Page {page_num}]\n"
                    
                    # Sort chunks by their position on the page
                    sorted_chunks = sorted(page_docs, key=lambda x: x.metadata.get('chunk', 0))
                    
                    # Process each chunk
                    for doc in sorted_chunks:
                        content = doc.page_content.strip()
                        
                        # Extract and format any warnings or cautions
                        if any(keyword in content.lower() for keyword in ['warning', 'caution', 'important', 'danger']):
                            lines = content.split('\n')
                            formatted_lines = []
                            for line in lines:
                                if any(keyword in line.lower() for keyword in ['warning', 'caution', 'important', 'danger']):
                                    formatted_lines.append(f"> ⚠️ {line}")
                                else:
                                    formatted_lines.append(line)
                            content = '\n'.join(formatted_lines)
                        
                        # Add context if it provides new information
                        if doc.metadata.get('context_before'):
                            prev = doc.metadata['context_before'].strip()
                            if not content.startswith(prev) and len(prev) > 30:
                                content = f"{prev}... {content}"
                        
                        if doc.metadata.get('context_after'):
                            next = doc.metadata['context_after'].strip()
                            if not content.endswith(next) and len(next) > 30:
                                content = f"{content}... {next}"
                        
                        # Add any subsection headers
                        if doc.metadata.get('subsection'):
                            context_text += f"\n#### {doc.metadata['subsection']}\n"
                        
                        context_text += f"{content}\n\n"
                
                context_text += "---\n"  # Add separator between sections
            
            # Generate response using the formatted context
            result = self.qa_template.invoke({
                "context": context_text,
                "question": question,
                "response_language": response_language
            })
            
            # Extract text from result
            if isinstance(result, dict) and 'text' in result:
                response_text = result['text']
            else:
                response_text = str(result)
            
            # Format the response
            formatted_result = self._format_response(response_text)
            
            # Extract source information
            source = {
                "filename": context_docs[0].metadata.get("filename", "Unknown"),
                "brand": manual_info['brand'],
                "model": manual_info['model'],
                "sections": sorted(set(doc.metadata.get("section", "General Information") for doc in context_docs)),
                "pages": sorted(set(doc.metadata.get("page", "N/A") for doc in context_docs))
            }
            
            return {
                "response": formatted_result,
                "sources": [source],
                "timestamp": None
            }
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                "response": "I encountered an error processing your request. Please try again with a simpler question.",
                "sources": [],
                "timestamp": None
            }
    
    def generate_direct_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a direct response to a prompt without using templates.
        
        Args:
            prompt: The direct prompt to send to the LLM
            max_tokens: Optional max tokens override
            temperature: Optional temperature override
            
        Returns:
            The generated response text
        """
        try:
            # Temporarily override LLM parameters if provided
            original_max_tokens = self.llm.max_tokens
            original_temperature = self.llm.temperature
            
            if max_tokens is not None:
                self.llm.max_tokens = max_tokens
            if temperature is not None:
                self.llm.temperature = temperature
            
            # Call the LLM directly
            response = self.llm._call(prompt)
            
            # Restore original parameters
            self.llm.max_tokens = original_max_tokens
            self.llm.temperature = original_temperature
            
            return response
            
        except Exception as e:
            print(f"Error in direct response generation: {str(e)}")
            # Restore original parameters in case of error
            self.llm.max_tokens = original_max_tokens
            self.llm.temperature = original_temperature
            raise 