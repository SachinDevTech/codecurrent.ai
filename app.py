import streamlit as st
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyCOno6CSHAuRFVNDx80C94U7wVaQ9CuY9A")

# Create the model
model = genai.GenerativeModel('gemini-pro')

# Set page configuration
st.set_page_config(
    page_title="codecurrents.ai",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS (keeping the existing styling from the previous script)
st.markdown("""
<style>
/* Previous CSS remains the same */
.chat-history-item {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 8px;
    background-color: #f1f1f1;
}
</style>
""", unsafe_allow_html=True)

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to handle large text generation
def generate_large_text(prompt, model, generation_config):
    """
    Handle generation of large texts by splitting into chunks if needed
    """
    try:
        # First, try generating the entire response
        full_response = model.generate_content(
            prompt, 
            generation_config=generation_config
        )
        
        # If response is incomplete, try a more robust approach
        if len(full_response.text) < len(prompt):
            # Split generation into multiple steps
            chunks = []
            current_chunk = prompt
            
            while current_chunk:
                chunk_response = model.generate_content(
                    current_chunk, 
                    generation_config=generation_config
                )
                chunks.append(chunk_response.text)
                
                # If the response is too short, break to prevent infinite loop
                if len(chunk_response.text) < 50:
                    break
                
                # Prepare for next iteration by using the previous response as context
                current_chunk = chunk_response.text
            
            # Combine chunks
            full_response = " ".join(chunks)
        
        return full_response.text
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Title and description
st.title("🤖 Sachin's Advanced AI Chat Companion")
st.write("Ask anything! I'm ready to help with any type of query, even long or complex inputs.")

# Sidebar for additional controls
st.sidebar.header("Chat Settings")
temperature = st.sidebar.slider(
    "Creativity Level", 
    min_value=0.0, 
    max_value=1.0, 
    value=0.7, 
    step=0.1
)
max_tokens = st.sidebar.number_input(
    "Max Response Length", 
    min_value=50, 
    max_value=4000, 
    value=2000
)

# Chat History Management
st.sidebar.header("Chat History")
clear_history = st.sidebar.button("Clear Chat History")
if clear_history:
    st.session_state.chat_history = []

# Expanded chat history view
show_full_history = st.sidebar.checkbox("Show Full Chat History", value=False)

# Main chat interface
user_prompt = st.text_area(
    "Enter your prompt:", 
    height=250, 
    placeholder="Type your question or prompt here... (supports long inputs)"
)

# Generate button
generate_button = st.button("Generate Response", type="primary")

# Response generation
if generate_button and user_prompt:
    try:
        # Add user message to chat history
        st.session_state.chat_history.append({
            'role': 'user', 
            'content': user_prompt,
            'timestamp': st.session_state.get('message_count', 0)
        })
        
        # Show loading spinner
        with st.spinner('Generating comprehensive response...'):
            # Generation configuration
            generation_config = {
                'temperature': temperature,
                'max_output_tokens': max_tokens
            }
            
            # Generate response with large text handling
            response_text = generate_large_text(
                user_prompt, 
                model, 
                generation_config
            )
            
            # Add AI response to chat history
            st.session_state.chat_history.append({
                'role': 'model', 
                'content': response_text,
                'timestamp': st.session_state.get('message_count', 0) + 1
            })
            
            # Increment message counter
            st.session_state['message_count'] = st.session_state.get('message_count', 0) + 2
            
            # Display generated text
            st.subheader("AI Response")
            st.markdown(f"""
            <div class="output-box">
                {response_text}
            </div>
            """, unsafe_allow_html=True)
            
            # Copy to clipboard button
            st.button("📋 Copy Response", 
                      on_click=lambda: st.write(response_text))
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
elif generate_button and not user_prompt:
    st.warning("Please enter a prompt before generating!")

# Detailed Chat History Display
if show_full_history:
    st.sidebar.header("Detailed Chat History")
    for message in reversed(st.session_state.chat_history):
        if message['role'] == 'user':
            st.sidebar.markdown(f"""
            <div class="chat-history-item" style="background-color: #e6f2ff;">
            **You:** {message['content'][:200]}...
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"""
            <div class="chat-history-item" style="background-color: #f0f0f0;">
            **AI:** {message['content'][:200]}...
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*Sachin's own AI - Powered by Google's Gemini Pro AI*")