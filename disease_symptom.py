import os
import streamlit as st
import requests
import json
from datetime import datetime



# Configuration
API_KEY = "AIzaSyDamjarOk0mM1E2eInflLsZYefGHaLqoWg"
MODEL = 'gemini-1.5-pro'
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# Domain configurations
DOMAINS = {
    "Medical": {
        "icon": "🏥",
        "placeholder": "Describe your symptoms...",
        "examples": ["headache and fever", "persistent cough for 3 weeks", "stomach pain after eating"],
        "prompt_template": """You are a medical expert system designed to provide preliminary symptom analysis.
        
User Input: {user_input}

Please provide:
1. Possible conditions (ranked by likelihood)
2. Recommended next steps (home care, see a doctor immediately, etc.)
3. Red flag symptoms to watch for
4. A reminder that this is not a substitute for professional medical advice

Use simple language and keep the response under 300 words."""
    },
    "Legal": {
        "icon": "⚖️",
        "placeholder": "Describe your legal question...",
        "examples": ["tenant rights in California", "small claims court process", "copyright infringement notice"],
        "prompt_template": """You are a legal information assistant providing general guidance.
        
User Question: {user_input}

Please provide:
1. Relevant legal principles
2. Potential courses of action
3. When to consult an attorney
4. A disclaimer that this is not legal advice

Use plain language and keep the response under 300 words."""
    },
    "Tech Support": {
        "icon": "💻",
        "placeholder": "Describe your tech issue...",
        "examples": ["printer won't connect", "slow computer performance", "website not loading"],
        "prompt_template": """You are an IT support expert assisting with technical issues.
        
User Problem: {user_input}

Please provide:
1. Likely causes of the problem
2. Step-by-step troubleshooting
3. When to seek professional help
4. Preventive measures for the future

Use non-technical language where possible and keep the response under 300 words."""
    },
    "Mental Health": {
        "icon": "🧠",
        "placeholder": "Describe what you're experiencing...",
        "examples": ["trouble sleeping", "constant anxiety", "loss of interest in activities"],
        "prompt_template": """You are a mental health first aid assistant providing supportive guidance.
        
User Concern: {user_input}

Please provide:
1. Possible explanations for these experiences
2. Coping strategies
3. When to seek professional help
4. Crisis resources if needed
5. A reminder that this is not therapy

Use compassionate language and keep the response under 300 words."""
    }
}

# Session state initialization
if 'history' not in st.session_state:
    st.session_state.history = []

def call_gemini_api(prompt, domain):
    headers = {"Content-Type": "application/json"}
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}],
            "role": "user"
        }],
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ],
        "generationConfig": {
            "temperature": 0.7 if domain == "Creative" else 0.3,
            "topP": 0.9,
            "topK": 40,
            "maxOutputTokens": 1024
        }
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        # Extract the response text
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                return result['candidates'][0]['content']['parts'][0]['text']
        
        st.error("Unexpected API response format")
        return None
        
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None

def save_to_history(domain, query, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append({
        "timestamp": timestamp,
        "domain": domain,
        "query": query,
        "response": response
    })

# UI Layout
st.set_page_config(page_title="Multi-Domain Expert Assistant", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🔍 Expert Domains")
    selected_domain = st.radio(
        "Select expert domain:",
        options=list(DOMAINS.keys()),
        format_func=lambda x: f"{DOMAINS[x]['icon']} {x}"
    )
    
    st.markdown("---")
    st.markdown("### Examples")
    domain_examples = DOMAINS[selected_domain]["examples"]
    for example in domain_examples:
        if st.button(example, use_container_width=True):
            st.session_state.user_input = example

# Main Content
st.title(f"{DOMAINS[selected_domain]['icon']} {selected_domain} Expert Assistant")
st.caption("Get expert guidance in various domains. Remember this is not a substitute for professional advice.")

# User Input
user_input = st.text_area(
    "Describe your question or issue:",
    placeholder=DOMAINS[selected_domain]["placeholder"],
    key="user_input",
    height=150
)

col1, col2 = st.columns([1, 3])
with col1:
    submit_btn = st.button("Get Expert Advice", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("Clear Input", use_container_width=True)

if clear_btn:
    st.session_state.user_input = ""
    st.rerun()

# Process Input
if submit_btn and user_input:
    with st.spinner(f"Consulting {selected_domain} expert..."):
        prompt = DOMAINS[selected_domain]["prompt_template"].format(user_input=user_input)
        response = call_gemini_api(prompt, selected_domain)
        
        if response:
            save_to_history(selected_domain, user_input, response)
            
            st.subheader("Expert Analysis")
            st.markdown(response)
            
            st.markdown("---")
            with st.expander("⚠️ Important Disclaimer"):
                if selected_domain == "Medical":
                    st.warning("This is not medical advice. Always consult a qualified healthcare professional for medical concerns.")
                elif selected_domain == "Legal":
                    st.warning("This is not legal advice. Consult a licensed attorney for legal matters.")
                elif selected_domain == "Mental Health":
                    st.warning("This is not therapy. For crisis support, contact your local emergency services or crisis hotline.")
                else:
                    st.warning("This information is provided for general guidance only.")

# History Section
if st.session_state.history:
    st.markdown("---")
    st.subheader("Consultation History")
    
    for i, entry in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{entry['domain']} - {entry['timestamp']}"):
            st.caption(f"**You asked:** {entry['query']}")
            st.markdown(f"**Expert response:**\n\n{entry['response']}")
            
            if st.button(f"Delete this entry", key=f"delete_{i}"):
                del st.session_state.history[len(st.session_state.history) - 1 - i]
                st.rerun()

# Footer
st.markdown("---")
st.caption("This expert system uses Google's Gemini AI for information. Responses may not always be accurate.")
