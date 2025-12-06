import streamlit as st
from openai import OpenAI

#initializing ai client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) 


def sidebar_navigation():
    st.sidebar.header("Navigation")

    category = st.sidebar.radio(
        "Choose a domain:",
        ("Users","Cyber Security","Data Science","IT Operations")
    )

    filters = {}

    if category == "Cyber Security":
        filters["severity"] = st.sidebar.multiselect(
            "Severity",
            ["Low","Medium","High","Critical"]
        
        )
        filters["status"] = st.sidebar.multiselect(
            "Status",
            ["Open","In Progress","Resolved","Closed"]
        
        )

    elif category == "Data Science":
        filters["uploader"] = st.sidebar.text_input("Uploader")
        filters["row_range"] = st.sidebar.slider("Row Range", 0, 100000, (0, 50000))

    
    elif category == "IT Operations":
       filters["priority"] = st.sidebar.multiselect(
            "Priority",
            ["Low","Medium","High","Critical"]
        )
       filters["status_IT"] = st.sidebar.multiselect(
            "Status",
            ["Open","In Progress","Resolved","Closed"]
        )
       filters["assigned"] = st.sidebar.text_input("Assigned_to")


    return category, filters

def sidebar_ai_assistant():
    st.sidebar.header("AI Assistant")

    #initializing chat session 
    if "messages" not in st.session_state:
        st.session_state.messages =[
            {"role": "system", 
             "content": "You are a cybersecurity, datascience and IT operation expert assistant "}]
        
    if "chat_input" not in st.session_state:
        st.session_state.chat_input = ""

        
    #clearing ai chat
    if st.sidebar.button("Clear AI Chat"): 
        st.session_state.messages = [ 
            {"role": "system","content":"You are a cybersecurity, datascience and IT operation expert assistant"} ]
        #clear chat
        st.session_state.chat_input = ""
    
    st.session_state.messages = [
        m for m in st.session_state.messages
        if not (m["role"] == "assistant" and 
                m["content"].strip().startswith("Hello! How can i assist you today?"))
    ]

    #this will be displaying old chat messages 
    for msg in st.session_state.messages: 
        if msg["role"] == "system": 
            continue 

        with st.sidebar.chat_message(msg["role"]): 
                st.markdown(msg.get("content",""))
                
    #the input box 
    prompt = st.sidebar.chat_input("Ask AI something?", key = "chat_input") 
    #resetting  
    if prompt: 
    #displaying the user's message 
        with st.sidebar.chat_message("user"): 
            st.markdown(prompt) 
            #saving the message 
            st.session_state.messages.append({"role": "user", "content":prompt}) 

    #streaming AI response part 
                                
        with st.spinner("Thinking..."): 
            completion = client.chat.completions.create( 
                model="gpt-4o", 
                messages=st.session_state.messages, 
                temperature=1.0, 
                stream=True
            ) 
                                        
        #streaming the messages
        full_reply = ""  
        with st.sidebar.chat_message("assistant"): 
            container = st.empty() 
            for chunk in completion:
                delta = chunk.choices[0].delta 
                if delta.content: 
                    full_reply += delta.content 
                    container.markdown(full_reply + "▌") 
            container.markdown(full_reply) 
        
    
        st.session_state.messages.append({"role": "assistant", "content": full_reply})    




