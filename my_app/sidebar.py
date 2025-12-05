import streamlit as st

def sidebar_navigation():
    st.sidebar.header("Navigation")
    category = st.radio(
        "Choose a domain:",
        ("Users","Cyber Security","Data Science","IT Operations")
    )

    st.sidebar.subheader("Filters")
    filters = {}

    if category == "Cyber Security":
        filters["severity"] = st.sidebar.multiselect((
            "Severity",
            ["Low","Medium","High","Critical"]
        )
        )
        filters["status"] = st.sidebar.multiselect((
            "Status",
            ["Open","In Progress","Resolved","Closed"]
        )
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

    st.sidebar.header("AI Assitant")

    if st.button("Clear AI Chat"): 
        st.session_state.messages = [ 
            {"role": "system","content":"You are a helpful assistant"} ]
            
        #clear chat
        st.session_state.chat_input =""
        st.session_state.clear_chat = True
    
    return category, filters

def ai_chat(client):
    #initializing chat session 
    if "messages" not in st.session_state:
        st.session_state.messages =[
        {"role": "system", "content": "You are a helpful assistant"}]
    
    if "clear_chat" not in st.session_state:
        st.session_state.clear_chat = False

    #this will be displaying old chat messages 
    for msg in st.session_state.messages: 
        if msg["role"] == "system": 
                continue 

        with st.chat_message(msg["role"]): 
            st.markdown(msg.get("content",""))
            
    #the input box 
    prompt = st.chat_input("Ask AI something?") 
    #resetting  
    if prompt: 
            #displaying the user's message 
            with st.chat_message("user"): 
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
                    with st.chat_message("assistant"): 
                        container = st.empty() 
                        full_reply = "" 
                        for chunk in completion:
                            delta = chunk.choices[0].delta 
                            if delta.content: 
                                full_reply += delta.content 
                                container.markdown(full_reply + "▌") 
                                container.markdown(full_reply) 
                        st.session_state.messages.append({"role": "assistant", "content": full_reply})    

