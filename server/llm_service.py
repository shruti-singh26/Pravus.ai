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
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_LLM_MAX_TOKENS
)

class AzureOpenAILLM(LLM):
    """Custom LLM for Azure OpenAI API."""
    
    api_key: str
    endpoint: str
    api_version: str
    deployment_name: str
    temperature: float = DEFAULT_LLM_TEMPERATURE
    max_tokens: int = DEFAULT_LLM_MAX_TOKENS
    
    @property
    def _llm_type(self) -> str:
        return "azure_openai"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> str:
        """Call Azure OpenAI API."""
        
        if not self.api_key or not self.endpoint:
            return self._generate_fallback_response(prompt)
        
        try:
            # Configure the Azure OpenAI client
            openai.api_type = "azure"
            openai.api_version = self.api_version
            openai.api_base = self.endpoint
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=stop if stop else None
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Azure OpenAI API error: {str(e)}")
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
                    f"Please check that your Azure OpenAI API configuration is correct."
                )
        else:
            return (
                "I'm unable to generate a complete response at the moment due to API connectivity issues. "
                "Please ensure your Azure OpenAI configuration is correct or try again later."
            )

class LLMService:
    """Service for generating responses using Azure OpenAI."""
    
    def __init__(self):
        self.llm = AzureOpenAILLM(
            api_key=AZURE_OPENAI_API_KEY,
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            deployment_name=AZURE_OPENAI_CHAT_DEPLOYMENT
        )

        # Log configuration status
        if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
            print(f"✅ Azure OpenAI configured with deployment: {AZURE_OPENAI_CHAT_DEPLOYMENT}")
            print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
            print(f"   API Version: {AZURE_OPENAI_API_VERSION}")
        else:
            print("❌ WARNING: Azure OpenAI is not properly configured. The system will operate in fallback mode.")
            print("To use Azure OpenAI, please set the following environment variables:")
            print("   - AZURE_OPENAI_API_KEY")
            print("   - AZURE_OPENAI_ENDPOINT")
            print("   - AZURE_OPENAI_CHAT_DEPLOYMENT (optional, defaults to 'gpt-35-turbo')")
        
        print(f"🔧 LLM Provider: {LLM_PROVIDER.upper()}")
        
        # Create prompt templates
        self.qa_template = self._create_qa_template()
    
    def _create_qa_template(self) -> PromptTemplate:
        """Create the Q&A prompt template."""
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
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question", "response_language"]
        )
    
    def generate_response(
        self,
        question: str,
        context_docs: List[Document],
        brand: Optional[str] = None,
        model: Optional[str] = None,
        response_language: str = 'en',
        use_fallback: bool = False
    ) -> Dict[str, any]:
        """Generate a response using the LLM."""
        
        # Format context from documents
        context_text = ""
        sources = []
        
        for doc in context_docs:
            # Add document content to context
            context_text += f"\nFrom {doc.metadata.get('brand', 'Unknown')} {doc.metadata.get('model', 'Unknown')} manual (Page {doc.metadata.get('page', 'N/A')}):\n"
            context_text += f"{doc.page_content}\n"
            
            # Add source information
            source = {
                'brand': doc.metadata.get('brand', 'Unknown'),
                'model': doc.metadata.get('model', 'Unknown'),
                'page': doc.metadata.get('page', 'N/A'),
                'filename': doc.metadata.get('filename', 'Unknown'),
                'language': doc.metadata.get('language', 'en')
            }
            if source not in sources:  # Avoid duplicates
                sources.append(source)
        
        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=self.qa_template)
        
        try:
            # Generate response
            response = chain.run(
                question=question,
                context=context_text,
                response_language=response_language
            )
            
            return {
                'response': response.strip(),
                'sources': sources
            }
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            
            if use_fallback:
                return {
                    'response': "I apologize, but I'm having trouble generating a response at the moment. Please try again later.",
                    'sources': sources
                }
            else:
                raise e
    
    def generate_direct_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a direct response without using a chain."""
        try:
            # Create a temporary LLM instance with custom parameters if provided
            llm = AzureOpenAILLM(
                api_key=AZURE_OPENAI_API_KEY,
                endpoint=AZURE_OPENAI_ENDPOINT,
                api_version=AZURE_OPENAI_API_VERSION,
                deployment_name=AZURE_OPENAI_CHAT_DEPLOYMENT,
                max_tokens=max_tokens or DEFAULT_LLM_MAX_TOKENS,
                temperature=temperature or DEFAULT_LLM_TEMPERATURE
            )
            
            return llm(prompt)
            
        except Exception as e:
            print(f"Error generating direct response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response at the moment. Please try again later." 