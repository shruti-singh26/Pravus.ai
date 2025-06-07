import time
from googletrans import Translator

def summarize_tool(docs, context):
    llm_service = context['llm_service']
    return llm_service.summarize_docs(docs)

def greet_tool(context):
    greetings = {
        'en': "👋 Hi! I'm your Pravus.AI Assistant, ready to help you understand and get the most out of your electronic devices. How can I assist you today?",
        'es': "👋 ¡Hola! Soy tu Asistente Pravus.AI, listo para ayudarte a entender y aprovechar al máximo tus dispositivos electrónicos. ¿Cómo puedo ayudarte hoy?",
        'hi': "👋 नमस्ते! मैं आपका Pravus.AI सहायक हूं, आपके इलेक्ट्रॉनिक उपकरणों को समझने और उनका सर्वोत्तम उपयोग करने में मदद करने के लिए तैयार हूं। मैं आज आपकी कैसे सहायता कर सकता हूं?",
        'pl': "👋 Cześć! Jestem twoim Asystentem Pravus.AI, gotowym pomóc ci zrozumieć i wykorzystać maksymalnie twoje urządzenia elektroniczne. Jak mogę ci dziś pomóc?"
    }
    lang = context.get('response_language', 'en')
    return greetings.get(lang, greetings['en'])

def help_tool(context):
    help_responses = {
        'en': (
            "I'm your dedicated product expert, here to help you with:\n\n"
            "### 🔍 Product Features\n"
            "• Understanding device features and specifications\n"
            "• Getting the best performance from your device\n"
            "• Discovering advanced capabilities\n\n"
            "### 🛠️ Support & Guidance\n"
            "• Setup and installation instructions\n"
            "• Troubleshooting common issues\n"
            "• Step-by-step configuration\n\n"
            "### 💡 Maintenance\n"
            "• Care guidelines and best practices\n"
            "• Optimization tips\n"
            "• Safety recommendations\n\n"
            "*What specific aspect would you like to learn more about?*"
        ),
        # ...other languages...
    }
    lang = context.get('response_language', 'en')
    return help_responses.get(lang, help_responses['en'])

def retrieve_tool(query, context):
    print(f"\n🔍 RETRIEVE: Starting retrieval for query: '{query}'")
    print(f"🔍 RETRIEVE: Context: {context}")
    
    # Get source language and translate query if needed
    source_language = context.get('source_language', 'en')
    print(f"🌐 RETRIEVE: Source language: {source_language}")
    
    if source_language != 'en':
        try:
            translator = Translator()
            print(f"🌐 RETRIEVE: Translating query from {source_language} to English")
            query_en = translator.translate(query, src=source_language, dest='en').text
            print(f"🌐 RETRIEVE: Translated query: '{query_en}'")
            query = query_en
        except Exception as e:
            print(f"❌ RETRIEVE: Translation error: {str(e)}")
            print(f"❌ RETRIEVE: Proceeding with original query")
    
    doc_processor = context['doc_processor']
    brand = context.get('brand')
    model = context.get('model')
    
    print(f"🔍 RETRIEVE: Searching with parameters:")
    print(f"  - Brand: {brand}")
    print(f"  - Model: {model}")
    
    active_manuals = [m for m in doc_processor.metadata.values() if not m.get('is_deleted', False)]
    matching_manuals = [
        m for m in active_manuals 
        if (not brand or m.get('brand') == brand) and 
           (not model or m.get('model') == model)
    ]
    
    print(f"📚 RETRIEVE: Found {len(active_manuals)} active manuals")
    print(f"📚 RETRIEVE: {len(matching_manuals)} manuals match brand/model criteria")
    
    print(f"🔎 RETRIEVE: Performing vector similarity search...")
    docs = doc_processor.similarity_search(
        query=query,
        brand=brand,
        model=model,
        k=4,
        include_deleted=False
    )
    
    print(f"✅ RETRIEVE: Found {len(docs)} relevant documents")
    for i, doc in enumerate(docs):
        print(f"  📄 Doc {i+1}: {doc.metadata.get('brand')} {doc.metadata.get('model')} - Page {doc.metadata.get('page')}")
        print(f"      Preview: {doc.page_content[:100]}...")
    
    return docs, active_manuals, matching_manuals, brand, model

def no_manuals_tool(context):
    return {
        'response': (
            "I don't have any manuals in my database yet. "
            "To help you effectively, please upload your device's manual first. "
            "Once uploaded, I can answer specific questions about your device."
        ),
        'sources': [],
        'timestamp': time.time()
    }

def no_matching_manuals_tool(context, active_manuals, brand, model):
    available_manuals = "\n".join([
        f"- {m.get('brand', 'Unknown')} {m.get('model', 'Unknown')}"
        for m in active_manuals
    ])
    return {
        'response': (
            f"I don't have a manual for {brand or ''} {model or ''}. "
            f"Here are the manuals I currently have:\n\n{available_manuals}\n\n"
            "Please select one of these manuals or upload a new one."
        ),
        'sources': [],
        'timestamp': time.time()
    }

def no_context_tool(context, active_manuals, brand, model):
    if brand or model:
        return {
            'response': (
                f"I couldn't find relevant information about that in the "
                f"{brand or ''} {model or ''} manual. Could you rephrase your question?"
            ),
            'sources': [],
            'timestamp': time.time()
        }
    else:
        manuals_list = "\n".join([
            f"- {m.get('brand', 'Unknown')} {m.get('model', 'Unknown')}"
            for m in active_manuals
        ])
        return {
            'response': (
                "I couldn't find relevant information about that. "
                f"I have these manuals available:\n\n{manuals_list}\n\n"
                "Please specify which manual you'd like to learn about."
            ),
            'sources': [],
            'timestamp': time.time()
        }

def generate_tool(question, docs, context):
    llm_service = context['llm_service']
    if not docs:
        return "Sorry, I couldn't find any relevant information to answer your question."
    
    manual_contexts = {}
    for doc in docs:
            manual_key = f"{doc.metadata.get('brand', 'Unknown')} {doc.metadata.get('model', 'Unknown')}"
            if manual_key not in manual_contexts:
                manual_contexts[manual_key] = {
                    'brand': doc.metadata.get('brand', 'Unknown'),
                    'model': doc.metadata.get('model', 'Unknown'),
                    'docs': []
                }
            manual_contexts[manual_key]['docs'].append(doc)

    # --- Add system instruction ---
    system_instruction = (
        "You are a helpful assistant. The following is a conversation between a user and you, the assistant. "
        "Always use the conversation history below to answer the user's question, especially if they refer to previous questions or say things like 'what did I ask before?'. "
        "If the question is about the manual, use the manual context provided after the conversation history. "
        "If you do not know the answer, say 'I don't know' rather than saying you don't have access to the conversation."
    )
        
        # Format context with clear manual separation and metadata
    context_text = ""
    for manual_key, manual_data in manual_contexts.items():
            context_text += f"\n## Manual Information:\n"
            context_text += f"Brand: {manual_data['brand']}\n"
            context_text += f"Model: {manual_data['model']}\n\n"
            context_text += f"Content from {manual_key} manual:\n"
            
            # Sort documents by page number for better context flow
            sorted_docs = sorted(manual_data['docs'], key=lambda x: x.metadata.get('page', 0))
            for doc in sorted_docs:
                context_text += f"\nPage {doc.metadata.get('page', 'N/A')}:\n{doc.page_content}\n"
            
            context_text += "\n---\n"  # Add separator between manuals
        
            # --- Add conversation history to the prompt ---
    conversation = context.get('conversation', [])
    conversation_text = ""
    for turn in conversation:
        conversation_text += f"User: {turn.get('user', '')}\n"
        conversation_text += f"Assistant: {turn.get('response', '')}\n"
    conversation_text += f"User: {question}\nAssistant:"

    # Combine system instruction, conversation, and manual context
    full_prompt = f"{system_instruction}\n\n{conversation_text}\n\n{context_text}"


    print(f"📝 Generated context text length: {len(context_text)} characters")
    print(f"📝 Generated conversation text length: {len(conversation_text)} characters")

    response_data = llm_service.generate_response(
        question=full_prompt,
        context_docs=docs,
        brand=context.get('brand'),
        model=context.get('model'),
        response_language=context.get('response_language', 'en'),
        use_fallback=False
    )
    return response_data.get('response', "Sorry, I couldn't generate an answer.")

def translate_tool(text, context):
    translator = context.get('translator')
    lang = context.get('response_language', 'en')
    if lang == 'en' or not translator:
        return text
    try:
        return  translator.translate(text, dest=lang).text
        
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text
    
def clarify_tool(context):
    return "Can you please provide more details about your issue or question? For example, what are you trying to do, what error or problem are you facing, or what outcome do you expect?"
