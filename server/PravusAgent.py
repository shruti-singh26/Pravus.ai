from typing import List, Dict, Any, Optional, Tuple
import time
import re
from WarrantyAgent import WarrantyAgent

class ConversationMemory:
    """Memory system for tracking conversation history"""
    
    def __init__(self, retriever, max_history: int = 100):
        self.max_history = max_history
        self.conversations = []  # List of conversation turns
        self.topics = {}  # Track topics discussed
        self.devices = {}  # Track devices mentioned
        self.issues = {}  # Track issues discussed
        self.warranty_agent = WarrantyAgent(retriever)

    def add_turn(self, user_input: str, response: str, metadata: Dict = None):
        """Add a conversation turn to memory"""
        turn = {
            'timestamp': time.time(),
            'user_input': user_input,
            'response': response,
            'metadata': metadata or {}
        }
        
        self.conversations.append(turn)
        
        # Keep only recent conversations
        if len(self.conversations) > self.max_history:
            self.conversations = self.conversations[-self.max_history:]
        
        # Update topic tracking
        self._update_topics(user_input, metadata)
        self._update_devices(user_input, metadata)
        self._update_issues(user_input, metadata)
        
        print(f"💾 MEMORY: Added turn #{len(self.conversations)}, total turns: {len(self.conversations)}")
    
    def _update_topics(self, user_input: str, metadata: Dict):
        """Track topics discussed in conversation"""
        category = metadata.get('query_category')
        if category:
            if category not in self.topics:
                self.topics[category] = []
            self.topics[category].append({
                'input': user_input,
                'timestamp': time.time()
            })
    
    def _update_devices(self, user_input: str, metadata: Dict):
        """Track devices mentioned in conversation"""
        device_type = metadata.get('device_type')
        if device_type:
            if device_type not in self.devices:
                self.devices[device_type] = []
            self.devices[device_type].append({
                'input': user_input,
                'timestamp': time.time()
            })
    
    def _update_issues(self, user_input: str, metadata: Dict):
        """Track issues discussed in conversation"""
        device_details = metadata.get('device_details', {})
        if device_details is None:
            device_details = {}
        issues = device_details.get('issues', [])
        for issue in issues:
            if issue not in self.issues:
                self.issues[issue] = []
            self.issues[issue].append({
                'input': user_input,
                'timestamp': time.time(),
                'device_type': metadata.get('device_type')
            })
    
    def get_recent_turns(self, count: int = 5) -> List[Dict]:
        """Get recent conversation turns"""
        return self.conversations[-count:] if self.conversations else []
    
    def get_all_turns(self) -> List[Dict]:
        """Get all conversation turns"""
        return self.conversations.copy()
    
    def find_similar_questions(self, current_input: str, threshold: float = 0.3) -> List[Dict]:
        """Find similar questions asked before"""
        current_words = set(current_input.lower().split())
        similar = []
        
        for turn in self.conversations:
            turn_words = set(turn['user_input'].lower().split())
            # Simple similarity based on word overlap
            overlap = len(current_words.intersection(turn_words))
            total_words = len(current_words.union(turn_words))
            similarity = overlap / total_words if total_words > 0 else 0
            
            if similarity > threshold:
                similar.append({
                    'turn': turn,
                    'similarity': similarity
                })
        
        # Sort by similarity
        similar.sort(key=lambda x: x['similarity'], reverse=True)
        return similar[:3]  # Return top 3 similar questions
    
    def get_device_history(self, device_type: str) -> List[Dict]:
        """Get conversation history for a specific device type"""
        return self.devices.get(device_type, [])
    
    def get_topic_history(self, topic: str) -> List[Dict]:
        """Get conversation history for a specific topic"""
        return self.topics.get(topic, [])
    
    def get_context_summary(self) -> str:
        """Generate a summary of conversation context"""
        if not self.conversations:
            return "No previous conversation history."
        
        recent_turns = self.get_recent_turns(3)
        summary_parts = []
        
        # Recent conversation summary
        if recent_turns:
            summary_parts.append("**Recent conversation:**")
            for i, turn in enumerate(recent_turns, 1):
                summary_parts.append(f"{i}. User asked: {turn['user_input'][:50]}...")
        
        # Devices discussed
        if self.devices:
            devices_list = list(self.devices.keys())
            summary_parts.append(f"**Devices discussed:** {', '.join(devices_list)}")
        
        # Topics covered
        if self.topics:
            topics_list = list(self.topics.keys())
            summary_parts.append(f"**Topics covered:** {', '.join(topics_list)}")
        
        return "\n".join(summary_parts)
    
    def is_followup_question(self, user_input: str) -> bool:
        """Check if this might be a follow-up question"""
        followup_indicators = [
            'also', 'and', 'what about', 'how about', 'additionally',
            'furthermore', 'moreover', 'in addition', 'another question',
            'one more thing', 'by the way'
        ]
        
        pronouns = ['it', 'that', 'this', 'them', 'those', 'these']
        
        lower_input = user_input.lower()
        
        # Check for follow-up indicators
        has_followup_words = any(indicator in lower_input for indicator in followup_indicators)
        
        # Check for pronouns without clear context
        has_pronouns = any(pronoun in lower_input.split() for pronoun in pronouns)
        
        return has_followup_words or (has_pronouns and len(self.conversations) > 0)
    
    def clear_memory(self):
        """Clear all conversation memory"""
        self.conversations.clear()
        self.topics.clear()
        self.devices.clear()
        self.issues.clear()
        print("💾 MEMORY: Cleared all conversation history")

    def get_latest_problem_context(self):
        """Return the most recent device, issue, and warranty info from conversation."""
        context = {}
        for turn in reversed(self.conversations):
            meta = turn.get('metadata', {})
            for key in ['device_type', 'brand', 'model', 'issue', 'bill_number', 'purchase_date']:
                if key in meta and key not in context:
                    context[key] = meta[key]
        return context
    def has_prompted_for_warranty(self) -> bool:
        """Check if warranty prompt was already given in the current problem context."""
        for turn in reversed(self.conversations):
            meta = turn.get('metadata', {})
            if meta.get('prompted_for') == 'warranty':
                return True
            # Optionally, stop searching if a new device/problem context is detected
            # if meta.get('device_type') != self.get_latest_problem_context().get('device_type'):
            #     break
        return False   


class PravusAgent:
    def __init__(self, retriever, llm, tools: Dict[str, Any]):
        self.retriever = retriever
        self.llm = llm
        self.tools = tools
        self.memory = ConversationMemory(retriever, max_history=100)  # Enhanced memory system

    def detect_device_type(self, user_input: str) -> Dict:
        """Detect device type and extract relevant information"""
        print(f"🔍 DETECT_DEVICE_TYPE: Starting detection for: '{user_input}'")
        lower_msg = user_input.lower()
        
        # Device type patterns
        device_patterns = {
            'washing_machine': {
                'terms': ['washing machine', 'washer', 'laundry machine', 'wash machine', 'machine'],
                'problems': ['not starting', 'not spinning', 'not draining', 'leaking', 'making noise', 
                           'vibrating', 'beep beep', 'beeping', 'smells bad', 'not completing cycle'],
                'components': ['drum', 'door', 'filter', 'hose', 'seal', 'agitator', 'control panel'],
                'maintenance': ['clean', 'cleaning', 'maintenance', 'descale', 'unclog', 'replace filter'],
                'usage': ['how to use', 'settings', 'cycle selection', 'temperature', 'water level']
            },
            'refrigerator': {
                'terms': ['refrigerator', 'fridge', 'freezer', 'ice maker'],
                'problems': ['not cooling', 'too warm', 'ice not making', 'water leaking', 'strange noise'],
                'components': ['compressor', 'thermostat', 'door seal', 'ice maker', 'water filter'],
                'maintenance': ['defrost', 'clean coils', 'replace filter', 'clean interior'],
                'usage': ['temperature setting', 'ice making', 'water dispenser', 'humidity control']
            },
            'dishwasher': {
                'terms': ['dishwasher', 'dish washer'],
                'problems': ['not cleaning', 'not draining', 'spots on dishes', 'strange smell'],
                'components': ['spray arm', 'filter', 'door seal', 'heating element'],
                'maintenance': ['clean filter', 'descale', 'rinse aid', 'detergent'],
                'usage': ['loading dishes', 'cycle selection', 'rinse aid', 'detergent amount']
            },
            'microwave': {
                'terms': ['microwave', 'microwave oven'],
                'problems': ['not heating', 'sparking', 'turntable not turning', 'display not working'],
                'components': ['magnetron', 'turntable', 'door seal', 'control panel'],
                'maintenance': ['clean interior', 'clean turntable', 'check door seal'],
                'usage': ['power levels', 'timing', 'defrosting', 'sensor cooking']
            }
        }
        
        detected_device = None
        detected_category = None
        detected_details = {}
        
        print(f"🔍 DETECT_DEVICE_TYPE: Checking against {len(device_patterns)} device types")
        
        # Check each device type
        for device_type, patterns in device_patterns.items():
            print(f"  📱 Checking {device_type}...")
            
            # Check direct device terms
            matching_terms = [term for term in patterns['terms'] if term in lower_msg]
            if matching_terms:
                detected_device = device_type
                print(f"  ✅ Device detected via terms: {matching_terms}")
                break
            
            # Check context terms (problems, components, etc.)
            all_context_terms = patterns['problems'] + patterns['components'] + patterns['maintenance'] + patterns['usage']
            matching_context = [term for term in all_context_terms if term in lower_msg]
            if matching_context:
                detected_device = device_type
                print(f"  ✅ Device detected via context: {matching_context}")
                break
        
        if not detected_device:
            print(f"  ❌ No device type detected")
        
        # Categorize query type
        if detected_device:
            patterns = device_patterns[detected_device]
            print(f"🔍 DETECT_DEVICE_TYPE: Categorizing query for {detected_device}")
            
            problem_matches = [term for term in patterns['problems'] if term in lower_msg]
            maintenance_matches = [term for term in patterns['maintenance'] if term in lower_msg]
            usage_matches = [term for term in patterns['usage'] if term in lower_msg]
            component_matches = [term for term in patterns['components'] if term in lower_msg]
            
            if problem_matches:
                detected_category = 'troubleshooting'
                detected_details['issues'] = problem_matches
                print(f"  🚨 Category: troubleshooting (problems: {problem_matches})")
            elif maintenance_matches:
                detected_category = 'maintenance'
                detected_details['maintenance_type'] = maintenance_matches
                print(f"  🔧 Category: maintenance (tasks: {maintenance_matches})")
            elif usage_matches:
                detected_category = 'usage'
                detected_details['usage_type'] = usage_matches
                print(f"  📖 Category: usage (topics: {usage_matches})")
            else:
                detected_category = 'general'
                print(f"  📋 Category: general")
            
            detected_details['components'] = component_matches
            if component_matches:
                print(f"  🔩 Components mentioned: {component_matches}")
            
            # Determine severity for urgent issues
            urgent_keywords = ['broken', 'emergency', 'urgent', 'help', 'immediately', 'flooded']
            if any(keyword in lower_msg for keyword in urgent_keywords):
                detected_details['severity'] = 'urgent'
            elif detected_details.get('issues'):
                detected_details['severity'] = 'high'
            else:
                detected_details['severity'] = 'normal'
        
        result = {
            'device_type': detected_device,
            'category': detected_category,
            'details': detected_details
        }
        
        print(f"🔍 DETECT_DEVICE_TYPE: Final result: {result}")
        return result

    def enhance_context_with_memory(self, user_input: str, context: Dict, monitor_state: Dict) -> Dict:
        """Enhance context with conversation history and memory"""
        enhanced_context = context.copy()
        
        print(f"🧠 MEMORY_ENHANCE: Enhancing context with memory...")
        
        # Extract entities (brands, models, numbers, etc.)
        entities = self.extract_entities(user_input)
        enhanced_context.update(entities)
        
        # Check if this is a follow-up question
        is_followup = self.memory.is_followup_question(user_input)
        enhanced_context['is_followup'] = is_followup
        
        if is_followup:
            print(f"🧠 MEMORY_ENHANCE: Detected follow-up question")
            recent_turns = self.memory.get_recent_turns(3)
            if recent_turns:
                # Get context from recent conversation
                last_turn = recent_turns[-1]
                enhanced_context['previous_device'] = last_turn['metadata'].get('device_type')
                enhanced_context['previous_category'] = last_turn['metadata'].get('query_category')
                enhanced_context['recent_context'] = [turn['user_input'] for turn in recent_turns]
                print(f"🧠 MEMORY_ENHANCE: Added previous context: {enhanced_context.get('previous_device')}")
        
        # Find similar questions from memory
        similar_questions = self.memory.find_similar_questions(user_input)
        if similar_questions:
            enhanced_context['similar_questions'] = similar_questions
            print(f"🧠 MEMORY_ENHANCE: Found {len(similar_questions)} similar questions")
        
        # Add device history if current query is about a device
        current_device = monitor_state.get('device_type')
        if current_device:
            device_history = self.memory.get_device_history(current_device)
            if device_history:
                enhanced_context['device_history'] = device_history
                print(f"🧠 MEMORY_ENHANCE: Added {len(device_history)} previous {current_device} queries")
        
        # Add conversation summary
        context_summary = self.memory.get_context_summary()
        enhanced_context['conversation_summary'] = context_summary
        
        # Persist device context across conversation
        if monitor_state.get('device_type'):
            enhanced_context['current_device'] = monitor_state['device_type']
        elif enhanced_context.get('previous_device') and enhanced_context.get('is_followup'):
            enhanced_context['current_device'] = enhanced_context['previous_device']
            # Also update monitor_state for consistency
            monitor_state['device_type'] = enhanced_context['previous_device']
            print(f"🧠 MEMORY_ENHANCE: Inherited device context: {enhanced_context['current_device']}")
        
        return enhanced_context
    
    def extract_entities(self, user_input: str) -> Dict:
        """Extract entities like brands, models, error codes, etc."""
        entities = {}
        lower_msg = user_input.lower()
        
        # Common appliance brands
        brands = ['samsung', 'lg', 'whirlpool', 'ge', 'maytag', 'bosch', 'kenmore', 
                 'electrolux', 'frigidaire', 'haier', 'siemens', 'miele']
        
        # Error code patterns
        error_pattern = r'\b[A-Z]{1,3}\d{1,3}\b|\b\d{1,3}[A-Z]{1,3}\b'
        
        # Extract brand
        for brand in brands:
            if brand in lower_msg:
                entities['brand'] = brand.title()
                break
        
        # Extract error codes
        error_codes = re.findall(error_pattern, user_input.upper())
        if error_codes:
            entities['error_codes'] = error_codes
        
        # Extract model patterns (simplified)
        model_pattern = r'\bmodel\s+([A-Z0-9\-]{3,})\b'
        models = re.findall(model_pattern, user_input.upper())
        if models:
            entities['model'] = models[0]
        
        return entities

    def is_conversation_history_query(self, user_input: str) -> bool:
        """Check if user is asking about conversation history"""
        history_keywords = [
            'first question', 'last question', 'previous question', 'earlier question',
            'what did i ask', 'what was my question', 'conversation history', 
            'chat history', 'our conversation', 'before', 'previously',
            'what did we discuss', 'what have we talked about', 'earlier conversation',
            'my questions', 'questions i asked', 'what have i asked'
        ]
        
        lower_input = user_input.lower()
        return any(keyword in lower_input for keyword in history_keywords)
    
    def handle_conversation_history_query(self, user_input: str) -> str:
        """Handle questions about conversation history using memory"""
        lower_input = user_input.lower()
        
        # Get conversation history
        all_turns = self.memory.get_all_turns()
        if not all_turns:
            return "We haven't had any previous conversation yet. This is our first interaction!"
        
        # Handle specific history queries
        if 'first' in lower_input:
            first_turn = all_turns[0]
            return f"Your first question was: \"{first_turn['user_input']}\"\n\nI responded with: {first_turn['response'][:100]}..."
        
        elif 'last' in lower_input or 'previous' in lower_input:
            if len(all_turns) > 1:
                last_turn = all_turns[-2]  # Previous turn (current is being processed)
                return f"Your last question was: \"{last_turn['user_input']}\"\n\nI responded with: {last_turn['response'][:100]}..."
            else:
                return "This is our first conversation!"
        
        elif any(word in lower_input for word in ['all', 'history', 'everything', 'discussed']):
            # Provide summary of all questions
            if len(all_turns) <= 5:
                summary = "Here's our complete conversation:\n\n"
                for i, turn in enumerate(all_turns, 1):
                    summary += f"{i}. You asked: \"{turn['user_input']}\"\n"
            else:
                summary = f"We've had {len(all_turns)} exchanges. Here are your recent questions:\n\n"
                recent_turns = all_turns[-5:]
                for i, turn in enumerate(recent_turns, len(all_turns)-4):
                    summary += f"{i}. You asked: \"{turn['user_input']}\"\n"
            
            # Add topics summary
            memory_stats = self.get_memory_stats()
            if memory_stats['devices_discussed']:
                summary += f"\n**Devices we've discussed:** {', '.join(memory_stats['devices_discussed'])}\n"
            if memory_stats['topics_covered']:
                summary += f"**Topics covered:** {', '.join(memory_stats['topics_covered'])}\n"
            
            return summary
        
        elif 'count' in lower_input or 'how many' in lower_input:
            return f"You've asked {len(all_turns)} questions in our conversation so far."
        
        else:
            # General conversation history
            recent_turns = self.memory.get_recent_turns(3)
            if recent_turns:
                response = "Here are your recent questions:\n\n"
                for i, turn in enumerate(recent_turns, 1):
                    response += f"{i}. \"{turn['user_input']}\"\n"
                return response
            else:
                return "We haven't had any previous conversation yet."

    def monitor(self, user_input: str, context: Dict) -> Dict:
        print(f"\n📊 MONITOR: Analyzing input: '{user_input}'")
        
        # Extract facts, intent, missing info, etc.
        lower_msg = user_input.lower()
        intent = None
        device_type = None
        query_category = None
        
        # Check for conversation history queries first
        if self.is_conversation_history_query(user_input):
            intent = 'conversation_history'
            print(f"📊 MONITOR: ✅ Detected conversation history query")
            result = {
                'intent': intent,
                'device_type': None,
                'query_category': 'conversation_history',
                'device_details': None,
                'missing_info': [],
                'user_input': user_input
            }
            print(f"📊 MONITOR: Final result: {result}")
            return result
        
        print(f"📊 MONITOR: Checking greeting patterns...")
        # Detect greeting patterns
        greeting_pattern = r'\b(?:hello|hi|hey|greetings)\b'
        if re.search(greeting_pattern, lower_msg, re.IGNORECASE):
            intent = 'greet'
            print(f"📊 MONITOR: ✅ Detected greeting intent")
        # Detect help/capability questions
        elif any(help_query in lower_msg for help_query in ['what can you do', 'what can you help with', 'how can you help']):
            intent = 'help'
            print(f"📊 MONITOR: ✅ Detected help intent")
        # Everything else is treated as a device query - be permissive!
        else:
            intent = 'query'
            print(f"📊 MONITOR: ✅ Detected query intent")

        # For electronic manual chatbot, missing brand/model shouldn't block queries
        # The system can work with available manuals and ask for specifics only if needed
        missing_info = []
        # Only flag as missing if context specifically indicates we need them and don't have them
        if context.get('require_brand', False) and not context.get('brand'):
            missing_info.append('brand')
        if context.get('require_model', False) and not context.get('model'):
            missing_info.append('model')

        # Extract detailed device information if detected (for all device types)
        device_details = None
        if intent == 'query':
            print(f"📊 MONITOR: Running device detection...")
            device_info = self.detect_device_type(user_input)
            device_type = device_info.get('device_type')
            query_category = device_info.get('category')
            device_details = device_info.get('details')

        result = {
            'intent': intent,
            'device_type': device_type,
            'query_category': query_category,
            'device_details': device_details,
            'missing_info': missing_info,
            'user_input': user_input
        }
        
        print(f"📊 MONITOR: Final result: {result}")
        return result

    def critic(self, monitor_state: Dict, context: Dict) -> Tuple[str, bool, float]:
        """Evaluate query quality and determine confidence score"""
        print(f"\n🎯 CRITIC: Evaluating query quality...")
        print(f"🎯 CRITIC: Monitor state: {monitor_state}")
        
        # Calculate confidence score based on multiple factors
        confidence_score = 0.0
        critique_message = ""
        needs_revision = False
        
        if monitor_state['intent'] == 'query':
            device_type = monitor_state.get('device_type')
            query_category = monitor_state.get('query_category')
            
            print(f"🎯 CRITIC: Processing query intent...")
            print(f"🎯 CRITIC: Device type: {device_type}, Category: {query_category}")
            
            # Base confidence from device detection
            if device_type:
                confidence_score += 0.4
                critique_message = f"Device detected: {device_type}"
                print(f"🎯 CRITIC: +0.4 for device detection: {device_type}")
                
                if query_category:
                    confidence_score += 0.3
                    critique_message += f", Category: {query_category}"
                    print(f"🎯 CRITIC: +0.3 for category: {query_category}")
            else:
                confidence_score += 0.1
                critique_message = "Generic device query"
                print(f"🎯 CRITIC: +0.1 for generic query")
            
            # Boost confidence for specific details
            details = monitor_state.get('device_details', {})
            if details:
                print(f"🎯 CRITIC: Found device details: {details}")
                if details.get('issues'):
                    confidence_score += 0.2
                    print(f"🎯 CRITIC: +0.2 for specific issues")
                if details.get('components'):
                    confidence_score += 0.1
                    print(f"🎯 CRITIC: +0.1 for component mentions")
                if details.get('error_codes'):
                    confidence_score += 0.3
                    print(f"🎯 CRITIC: +0.3 for error codes")
            
            # Context enhancement
            context_bonus = 0
            if context.get('brand'):
                confidence_score += 0.1
                context_bonus += 0.1
            if context.get('model'):
                confidence_score += 0.1
                context_bonus += 0.1
            if context.get('error_codes'):
                confidence_score += 0.2
                context_bonus += 0.2
            if context_bonus > 0:
                print(f"🎯 CRITIC: +{context_bonus} for context info")
            
            # Memory-based confidence boost
            if context.get('is_followup'):
                confidence_score += 0.2
                print(f"🎯 CRITIC: +0.2 for follow-up question with context")
            
            if context.get('similar_questions'):
                confidence_score += 0.1
                print(f"🎯 CRITIC: +0.1 for similar questions found in memory")
            
            # Check for ambiguity
            vague_patterns = ['it', 'this', 'that', 'stuff', 'thing', 'something']
            words = monitor_state['user_input'].lower().split()
            
            if len(words) <= 3 and any(vague in words for vague in vague_patterns):
                if not context.get('is_followup'):  # Allow vague terms in follow-ups
                    print(f"🎯 CRITIC: ⚠️ Vague query detected: {words}")
                    confidence_score *= 0.3
                    needs_revision = True
                    critique_message = "Query too vague without context"
                else:
                    print(f"🎯 CRITIC: Vague terms allowed in follow-up")
            
            # Urgent queries get processed regardless of completeness
            severity = details.get('severity') if details else 'normal'
            if severity in ['urgent', 'high'] and confidence_score >= 0.3:
                print(f"🎯 CRITIC: 🚨 Urgent/high priority issue detected, overriding revision need")
                needs_revision = False
                critique_message += " - Urgent issue, proceeding"
            
            # Final confidence check
            if confidence_score < 0.3 and not needs_revision:
                print(f"🎯 CRITIC: ⚠️ Low confidence score: {confidence_score}")
                needs_revision = True
                critique_message = "Low confidence in query understanding"
                
        else:
            # Greet/Help intents have full confidence
            confidence_score = 1.0
            critique_message = f"Clear {monitor_state['intent']} intent"
            print(f"🎯 CRITIC: Full confidence for {monitor_state['intent']} intent")
        
        result = (critique_message, needs_revision, confidence_score)
        print(f"🎯 CRITIC: Final assessment: {result}")
        return result

    def planner(self, monitor_state: Dict, critique: Tuple[str, bool, float], context: Dict) -> List[Dict]:
        print(f"\n📋 PLANNER: Creating execution plan...")
        
        steps = []
        critique_message, needs_revision, confidence_score = critique
        
        print(f"📋 PLANNER: Critique: {critique_message}")
        print(f"📋 PLANNER: Needs revision: {needs_revision}")
        print(f"📋 PLANNER: Confidence: {confidence_score}")
        
        if monitor_state['intent'] == 'greet':
            steps.append({'tool': 'greet', 'args': {}})
            print(f"📋 PLANNER: Added greet step")
        elif monitor_state['intent'] == 'help':
            steps.append({'tool': 'help', 'args': {}})
            print(f"📋 PLANNER: Added help step")
        elif monitor_state['intent'] == 'conversation_history':
            steps.append({'tool': 'conversation_history', 'args': {'user_input': monitor_state['user_input']}})
            print(f"📋 PLANNER: Added conversation_history step")
        elif needs_revision:  # needs_revision - only for truly problematic queries
            steps.append({'tool': 'clarify', 'args': {}})
            context['awaiting_clarification'] = True
            print(f"📋 PLANNER: Added clarify step due to revision need")
        else:
            print(f"📋 PLANNER: Creating device query plan...")
            # For any device query, always try to help by retrieving and generating
            # Add device-specific context for better retrieval
            query_args = {
                'query': monitor_state['user_input'], 
                'context': context,
                'confidence_score': confidence_score
            }
            
            generate_args = {
                'question': monitor_state['user_input'], 
                'context': context,
                'confidence_score': confidence_score
            }
            
            # Add device-specific context
            device_type = monitor_state.get('device_type')
            if device_type:
                print(f"📋 PLANNER: Adding device-specific context for {device_type}")
                query_args['device_type'] = device_type
                query_args['query_category'] = monitor_state.get('query_category')
                generate_args['device_type'] = device_type
                generate_args['query_category'] = monitor_state.get('query_category')
                
                # Add detailed device context
                device_details = monitor_state.get('device_details', {})
                if device_details:
                    print(f"📋 PLANNER: Adding device details: {device_details}")
                    query_args['device_details'] = device_details
                    generate_args['device_details'] = device_details
                    
                    # Set priority based on severity and issues
                    severity = device_details.get('severity', 'normal')
                    if severity == 'urgent':
                        query_args['priority'] = 'urgent'
                        generate_args['priority'] = 'urgent'
                        print(f"📋 PLANNER: Set URGENT priority")
                    elif severity == 'high':
                        query_args['priority'] = 'high'
                        generate_args['priority'] = 'high'
                        print(f"📋 PLANNER: Set HIGH priority")
                
                # For troubleshooting, prioritize problem-solving docs
                if monitor_state.get('query_category') == 'troubleshooting':
                    query_args['priority'] = query_args.get('priority', 'troubleshooting')
                    generate_args['priority'] = generate_args.get('priority', 'troubleshooting')
                    print(f"📋 PLANNER: Set troubleshooting priority")
            
            steps.append({'tool': 'retrieve', 'args': query_args})
            steps.append({'tool': 'generate', 'args': generate_args})
            context['awaiting_clarification'] = False
            print(f"📋 PLANNER: Added retrieve and generate steps")
            
        print(f"📋 PLANNER: Final plan: {len(steps)} steps")
        return steps

    def act(self, user_input: str, context: Dict) -> Dict:
        print(f"\n🚀 ACT: Starting to process user input: '{user_input}'")
        
        print(f"📊 ACT: Calling monitor...")
        monitor_state = self.monitor(user_input, context)
        print(f"📊 ACT: Monitor result: {monitor_state}")
        
        # Enhanced device detection using the new system
        print(f"🔍 ACT: Running enhanced device detection...")
        device_info = self.detect_device_type(user_input)
        if device_info['device_type']:
            print(f"🔍 ACT: Overriding monitor with enhanced detection results")
            monitor_state['device_type'] = device_info['device_type']
            monitor_state['query_category'] = device_info['category']
            monitor_state['device_details'] = device_info['details']
        else:
            print(f"🔍 ACT: No device detected by enhanced system, keeping monitor results")
        
        # Enhance context with memory and conversation tracking
        print(f"🧠 ACT: Enhancing context with memory...")
        enhanced_context = self.enhance_context_with_memory(user_input, context, monitor_state)
        print(f"🧠 ACT: Enhanced context keys: {list(enhanced_context.keys())}")


        # Get latest problem context from memory
        latest_problem_context = self.memory.get_latest_problem_context()
        # Merge into enhanced_context if missing
        for key, value in latest_problem_context.items():
            if key not in enhanced_context or not enhanced_context[key]:
                enhanced_context[key] = value

        # Optionally, detect if this is a follow-up (no device/brand/model/issue in input)
        is_followup = len(user_input.split()) < 5 or not any(
            kw in user_input.lower()
            for kw in [enhanced_context.get('device_type', ''), enhanced_context.get('brand', ''), enhanced_context.get('model', ''), enhanced_context.get('issue', '')]
            if kw
        )
        enhanced_context['is_followup'] = is_followup

        # --- NEW PROBLEM CONTEXT RESET LOGIC ---
        if (
        'device_type' in monitor_state
        and monitor_state['device_type']
        and monitor_state['device_type'] != latest_problem_context.get('device_type')
        and latest_problem_context.get('device_type') is not None
            ):
            print("🔄 Detected new device/problem context. Optionally clearing or updating memory/context.")
        # Optionally clear or update context for new problem
        # self.memory.clear_memory()  # Uncomment if you want to clear all memory for new device
        # Or, implement a more granular reset if needed
        # --- END NEW PROBLEM CONTEXT RESET LOGIC ---
        
        # --- WARRANTY END DATE QUERY HANDLING ---
        if self.memory.warranty_agent.is_end_date_query(user_input):
         memory_context = self.memory.get_latest_problem_context()
         response = self.memory.warranty_agent.act(user_input, memory=memory_context)
         self.memory.add_turn(user_input, response, {'agent': 'warranty', **memory_context})
         return {
         'response': response,
         'sources': [],
         'timestamp': time.time(),
         'awaiting_clarification': False,
         'monitor': monitor_state,
         'critique': "Answered warranty end date",
         'confidence': 1.0,
         'device_type': monitor_state.get('device_type'),
         'query_category': monitor_state.get('query_category'),
         'conversation': [],
         'memory_summary': self.memory.get_context_summary(),
         'is_followup': enhanced_context.get('is_followup', False),
         'conversation_length': len(self.memory.conversations)
            }
        # --- END WARRANTY END DATE QUERY HANDLING ---

        # --- INSERT WARRANTY PROMPT LOGIC HERE ---
        device_type = monitor_state.get('device_type')
        # already_asked_warranty = context.get('asked_warranty', False)
        has_bill_number = 'bill_number' in enhanced_context
        has_purchase_date = 'purchase_date' in enhanced_context

        if (
            device_type
            and not self.memory.has_prompted_for_warranty()
            and not (has_bill_number and has_purchase_date)):
            response = (
                "Before we proceed, could you please provide your bill number and purchase date? "
                "This will help me check if your product is under warranty and give you the best support."
                )
            self.memory.add_turn(
            user_input,
            response,
              {
                'prompted_for': 'warranty',
                'agent': 'warranty',
                'last_prompt': 'ask_purchase_date'
              }
           )
            return {
            'response': response,
            'sources': [],
            'timestamp': time.time(),
            'awaiting_clarification': True,
            'monitor': monitor_state,
            'critique': "Prompted for warranty info",
            'confidence': 1.0,
            'device_type': device_type,
            'query_category': monitor_state.get('query_category'),
            'conversation': [],
            'memory_summary': self.memory.get_context_summary(),
            'is_followup': enhanced_context.get('is_followup', False),
            'conversation_length': len(self.memory.conversations)
            }
        # --- END WARRANTY PROMPT LOGIC ---
        
        

        print(f"🎯 ACT: Running critic...")
        critique = self.critic(monitor_state, enhanced_context)
        print(f"🎯 ACT: Critique result: {critique}")
        
        print(f"📋 ACT: Running planner...")
        steps = self.planner(monitor_state, critique, enhanced_context)
        print(f"📋 ACT: Planned steps: {steps}")

        response = None
        sources = []
        intermediate = {}

        print(f"🛠️ ACT: Executing {len(steps)} planned steps...")
        try:
            for i, step in enumerate(steps):
                tool = step['tool']
                args = step['args']
                print(f"  🔧 Step {i+1}: Executing tool '{tool}'")
                
                if tool == 'greet':
                    response = self.tools['greet'](enhanced_context)
                    print(f"  ✅ Greet tool returned: {response[:50]}...")
                elif tool == 'help':
                    response = self.tools['help'](enhanced_context)
                    print(f"  ✅ Help tool returned: {response[:50]}...")
                elif tool == 'conversation_history':
                    response = self.handle_conversation_history_query(args['user_input'])
                    print(f"  ✅ Conversation history tool returned: {response[:50]}...")
                elif tool == 'clarify':
                    response = self.tools['clarify'](enhanced_context)
                    print(f"  ✅ Clarify tool returned: {response}")
                    break
                elif tool == 'retrieve':
                    print(f"  🔍 Retrieve args: query='{args['query']}', context keys={list(args['context'].keys())}")
                    docs, active_manuals, matching_manuals, brand, model = self.tools['retrieve'](args['query'], args['context'])
                    intermediate['docs'] = docs
                    sources = [getattr(doc, 'metadata', {}) for doc in docs]
                    print(f"  ✅ Retrieved {len(docs)} documents, {len(sources)} sources")
                elif tool == 'generate':
                    docs = intermediate.get('docs', [])
                    print(f"  💭 Generate with {len(docs)} docs for question: '{args['question']}'")
                    response = self.tools['generate'](args['question'], docs, enhanced_context)
                    print(f"  ✅ Generate tool returned: {response[:100] if response else 'None'}...")
                elif tool == 'translate':
                    print(f"  🌐 Translating response...")
                    response = self.tools['translate'](response, enhanced_context)
                    print(f"  ✅ Translate tool returned: {response[:50] if response else 'None'}...")
                    
        except Exception as e:
            print(f"❌ ACT: Error executing tool '{tool}': {str(e)}")
            response = "I encountered an error while processing your request. Please try again."

        if not response:
            print(f"⚠️ ACT: No response generated, using fallback")
            response = "Sorry, I couldn't generate a response. Please try rephrasing your question."

        # Store conversation in memory with metadata
        conversation_metadata = {
        'device_type': monitor_state.get('device_type'),
        'query_category': monitor_state.get('query_category'),
        'confidence': critique[2] if len(critique) > 2 else 0.0,
        'device_details': monitor_state.get('device_details'),
        'is_followup': enhanced_context.get('is_followup', False),
         'bill_number': enhanced_context.get('bill_number'),
         'purchase_date': enhanced_context.get('purchase_date')
        }
        
        self.memory.add_turn(user_input, response, conversation_metadata)

        # Also maintain backward compatibility with context conversation
        conversation = enhanced_context.get('conversation', [])
        conversation_entry = {
            'user': user_input, 
            'response': response, 
            'sources': sources,
            'device_type': monitor_state.get('device_type'),
            'category': monitor_state.get('query_category'),
            'confidence': critique[2] if len(critique) > 2 else 0.0,
            'timestamp': time.time()
        }
        conversation.append(conversation_entry)

        final_result = {
            'response': response,
            'sources': sources,
            'timestamp': time.time(),
            'awaiting_clarification': enhanced_context.get('awaiting_clarification', False),
            'monitor': monitor_state,
            'critique': critique[0],
            'confidence': critique[2] if len(critique) > 2 else 0.0,
            'device_type': monitor_state.get('device_type'),
            'query_category': monitor_state.get('query_category'),
            'conversation': conversation[-5:],  # Return recent conversation for backward compatibility
            'memory_summary': self.memory.get_context_summary(),
            'is_followup': enhanced_context.get('is_followup', False),
            'conversation_length': len(self.memory.conversations)
        }
        
        print(f"🎉 ACT: Final response: '{response}'")
        print(f"🎉 ACT: Confidence: {final_result['confidence']:.2f}")
        print(f"🎉 ACT: Device type: {final_result['device_type']}")
        print(f"🎉 ACT: Query category: {final_result['query_category']}")
        print(f"🎉 ACT: Is followup: {final_result['is_followup']}")
        print(f"🎉 ACT: Total conversation turns: {final_result['conversation_length']}")
        
        return final_result
    
    def get_conversation_history(self, count: int = None) -> List[Dict]:
        """Get conversation history from memory"""
        if count is None:
            return self.memory.get_all_turns()
        return self.memory.get_recent_turns(count)
    
    def clear_conversation_memory(self):
        """Clear conversation memory"""
        self.memory.clear_memory()
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about conversation memory"""
        return {
            'total_turns': len(self.memory.conversations),
            'devices_discussed': list(self.memory.devices.keys()),
            'topics_covered': list(self.memory.topics.keys()),
            'issues_discussed': list(self.memory.issues.keys()),
            'memory_summary': self.memory.get_context_summary()
        }