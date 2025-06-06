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
        template = """You are a helpful AI assistant that helps users understand their electronic device manuals. 
        Your goal is to provide accurate, helpful information based on the manual content provided.

        CONTEXT:
        {context}

        USER QUESTION:
        {question}

        Please provide a clear, direct answer based on the manual content above. If the context doesn't contain 
        relevant information to answer the question, please say so. Focus on accuracy and clarity.

        ANSWER:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
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
                context=context_text
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