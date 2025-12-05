import streamlit as st
import os
import sys
import pandas as pd
import numpy as np
from openai import OpenAI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
st.set_page_config(page_title="Multi-Intelligence Domain Platform", page_icon="📊",layout="wide")

from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.data.load import load_all_csv_data
from app.data.users import update_user_role,delete_user
from app.data.incidents import insert_incident,update_incident_status,delete_incident,get_incidents_by_category,get_bottleneck_categories_by_status,get_resolution_status_breakdown
from app.data.datasets import insert_dataset,update_dataset,delete_dataset
from app.data.it_tickets import insert_tickets,update_tickets,delete_ticket

#________________________________-
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

#connection section
#___________________________-
if "conn" not in st.session_state:
    st.session_state.conn = connect_database()
conn = st.session_state.conn

create_all_tables(st.session_state.conn) 
load_all_csv_data(st.session_state.conn)

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""
    
# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")

    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()

# If logged in, show dashboard content
st.title("📊 Multi-Intelligence Domain Platform")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

##initializing client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
#initializing chat session 
if "messages" not in st.session_state:
    st.session_state.messages =[
        {"role": "system", "content": "You are a helpful assistant"}]
    
if "clear_chat" not in st.session_state:
    st.session_state.clear_chat = False
#---------------------------------------------------

# Sidebar filters

with st.sidebar:
    st.header("Navigation")
    category = st.radio(
        "Choose a domain:",
        ("Users","Cyber Security","Data Science","IT Operations")
    )

    st.subheader("Filters")
    if category == "Cyber Security":
        severity_filter = st.multiselect(
            "Severity",
            ["Low","Medium","High","Critical"]
        )

        status_filter = st.multiselect(
            "Status",
            ["Open","In Progress","Resolved","Closed"]
        )


    elif category == "Data Science":
        uploader_filter = st.text_input("Uploader")
        row_range = st.sidebar.slider("Row Range", 0, 100000, (0, 50000))

    
    elif category == "IT Operations":
        priority_filter = st.multiselect(
            "Priority",
            ["Low","Medium","High","Critical"]
        )

        status_filter_IT = st.multiselect(
            "Status",
            ["Open","In Progress","Resolved","Closed"]
        )
        assigned_filter = st.text_input("Assigned_to")

    st.header("AI Assitant")

    if st.button("Clear AI Chat"): 
        st.session_state.messages = [ 
            {"role": "system","content":"You are a helpful assistant"} ]
            
        #clear chat
        st.session_state.chat_input =""
        st.session_state.clear_chat = True

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


# Fetch data from database based on selected category
if category== "Users":
    st.subheader("Users")
    try:
        users = pd.read_sql_query("SELECT * FROM users", st.session_state.conn)
        st.dataframe(users)
    except Exception as e:
        st.error(f"Error fetching Users table:{e}")
    
    st.markdown("---")
    st.subheader("Insights on Users")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Users", len(users)) 

    with col2:
        st.metric("Admins", (users["role"] == "Admin").sum()) 

    with col3:
        st.metric("Analysts", (users["role"] == "Analyst").sum())  

    with col4:
        st.metric("Viewers",(users["role"] == "Viewer").sum())

    st.subheader("Search/Filter Users")
    search_username = st.text_input("Search by Username")
    filter_role = st.selectbox("Filter by Role", ["All"] + users["role"].unique().tolist())

    filtered_users = users.copy()
    if search_username:
        filtered_users = filtered_users[filtered_users["username"].str.contains(search_username, case=False)]
    
    if filter_role != "All":
        filtered_users = filtered_users[filtered_users["role"] == filter_role]

    st.dataframe(filtered_users)

    st.markdown("---")
    st.subheader("Manage Users")

        #this will be for updating user role
    with st.expander("Update user role"):
        with st.form("Update_Role_Form"):
            username = st.text_input("Username")
            role = st.selectbox("New role",["Admin","Analyst","User","Viewer"])
            submit_update = st.form_submit_button("Update role")
                
            if submit_update:
                try:
                    rows = update_user_role(st.session_state.conn,username,role)
                    if rows > 0:
                        st.success(f"User {username} role updated to {role}")

                    else:
                        st.warning(f"No user found with ID {username}")

                except Exception as e:
                        st.error(f"Failed to update role: {e}")

        #this will be for deleting a user
    with st.expander("Delete user"):
        with st.form("Delete_User_Form"):
            user_id = st.number_input("Enter the user ID to be deleted", min_value=1, step=1)
            submit_delete = st.form_submit_button("Delete user")
                
            if submit_delete:
                try:
                    rows = delete_user(st.session_state.conn,user_id)
                    if rows > 0:
                        st.success(f"User {user_id} deleted successfully")

                    else:
                        st.warning(f"No users found with ID {user_id}")

                except Exception as e:
                    st.error(f"Failed to delete incident: {e}")

elif category == "Cyber Security":
    st.subheader("Cyber Security")
  
    try:

        #CSV uploading section
        uploaded_file = st.file_uploader("###Upload your Cyber Incidents CSV file here please📥",type=["csv"], key="cyber_incidents.csv")
        
        if uploaded_file:
        
            try: 
                df = pd.read_csv(uploaded_file)
                df_filtered = df.copy()

                if severity_filter:
                    df_filtered = df_filtered[df_filtered["severity"].isin(severity_filter)]

                if status_filter:
                    df_filtered = df_filtered[df_filtered["status"].isin(status_filter)]

                st.success("Cyber Incidents file uploaded sucessfully!")
                st.dataframe(df_filtered)

                df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"], errors="coerce")
            
            except Exception as e:
                st.error(f"Failed to load file:{e}")

            st.markdown("---")
            st.subheader("Manage Incidents")

            #this will be for the inserting new incident
            with st.expander("Add new incident"):
                with st.form("Insert_Incident_Form"):
                    timestamp = st.date_input("Timestamp")
                    severity = st.selectbox("Severity",["Low","Medium","High","Critical"])
                    category = st.text_input("Category")
                    status = st.selectbox("Status",["Open","In Progress","Resolved","Closed"])
                    description = st.text_area("Description")
                    created_by = st.text_input("Created_by")
                    submit_add = st.form_submit_button("Add incident")

                    if submit_add:
                        try:
                            incident_id = insert_incident(
                                st.session_state.conn,
                                timestamp,
                                severity,
                                category,
                                status,
                                description,
                                created_by
                            )
                            st.success(f"Incident added successfully! ID: {incident_id}")
                        except Exception as e:
                            st.error(f"Failed to add incident: {e}")
                
                #this will be for updating incident status
            with st.expander("Update incident status"):
                with st.form("Update_Incident_Form"):
                    incident_id = st.number_input("Incident ID", min_value=1, step=1)
                    status = st.selectbox("New status",["Open","In Progress","Resolved","Closed"])
                    submit_update = st.form_submit_button("Update status")
                    
                    if submit_update:
                        try:
                            rows = update_incident_status(st.session_state.conn,incident_id,status)
                            if rows > 0:
                                st.success(f"Incident {incident_id} status updated to {status}")

                            else:
                                st.warning(f"No incident found with ID {incident_id}")

                        except Exception as e:
                            st.error(f"Failed to update incident: {e}")

            #this will be for deleting an incident
            with st.expander("Delete incident"):
                with st.form("Delete_incident_Form"):
                    incident_id = st.number_input("Enter the incident ID to be deleted", min_value=1, step=1)
                    submit_delete = st.form_submit_button("Delete incident")
                    
                    if submit_delete:
                        try:
                            rows = delete_incident(st.session_state.conn,incident_id)
                            if rows > 0:
                                st.success(f"Incident {incident_id} deleted successfully")

                            else:
                                st.warning(f"No incident found with ID {incident_id}")

                        except Exception as e:
                            st.error(f"Failed to delete incident: {e}")
            
            st.markdown("---")
            
            col1, col2, col3= st.columns(3)

            with col1:
                st.subheader("Incidents by Type(category)")
                incidents_by_category = get_incidents_by_category(st.session_state.conn)
                fig_cat = px.bar(
                    incidents_by_category,
                    x="category",
                    y="count"
                )
                st.plotly_chart(fig_cat, use_container_width=True)


            with col2:
                st.subheader("Bottleneck Categories/Unresolved incidents)")
                bottlenecks = get_bottleneck_categories_by_status(st.session_state.conn)
                fig_bottleneck = px.bar(
                    bottlenecks,
                    x="category",
                    y="unresolved_count",
                    color="unresolved_count",
                    text="unresolved_count"
                )
                st.plotly_chart(fig_bottleneck, use_container_width=True)

            with col3:
                st.subheader("Resolution Performance")
                resolution_status = get_resolution_status_breakdown(st.session_state.conn)
                pivot = resolution_status.pivot(index="category", columns="status", values="count").fillna(0)
                
                fig_res = go.Figure()
                for status in pivot.columns:
                    fig_res.add_trace(
                        go.Bar(
                            x=pivot.index,
                            y=pivot[status],
                            name=status
                        )
                    )
                fig_res.update_layout(
                    barmode="stack", 
                    xaxis_title="Category",
                    yaxis_title="Count"
                )

                st.plotly_chart(fig_res, use_container_width=True)

            st.markdown("Cyber Security Analytics Dashboard")   

            #-----KPI
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Total Incidents", len(df_filtered)) 

            with col2:
                st.metric("Open Incidents", (df_filtered["status"] == "Open").sum()) 

            with col3:
                st.metric("In Progress", (df_filtered["status"] == "In Progress").sum())  

            with col4:
                st.metric("Resolved",(df_filtered["status"] == "Resolved").sum())   

            with col5:
                st.metric("Critical Severity", (df_filtered["severity"] == "Critical").sum())   
            
            st.markdown("--")

            #------recent incident tables
            st.subheader("Recent Incidents")
            recent = df_filtered.sort_values("timestamp", ascending=False).head(10)
            st.dataframe(recent)
            
            #------incident trend 
            st.subheader("Incident Trend Over Time")
            df_filtered["Timestamp"] = pd.to_datetime(df_filtered["timestamp"], errors= "coerce")
            fig_trend = px.line(df_filtered.sort_values("timestamp"), x="timestamp", y="severity", color="severity", markers=True)
            st.plotly_chart(fig_trend,use_container_width=True)

            #------high severity alerts
            st.subheader("High & Critical Alerts")
            alerts = df_filtered[df_filtered["severity"].isin(["High","Critical"])].sort_values("timestamp", ascending=False)
            st.dataframe(alerts)

            #----------severity distribution
            st.subheader("Severity Distribution")
            fig_sev = px.pie(df_filtered, names="severity")
            st.plotly_chart(fig_sev,use_container_width=True)
            
            st.markdown("---")

            st.header("Incident Comparision Section")

            cat1_name = st.selectbox("Select Category 1", df_filtered["category"].unique())
            cat2_name = st.selectbox("Select Category 2", df_filtered["category"].unique())

            if cat1_name and cat2_name:
                c1 = df_filtered[df_filtered["category"] == cat1_name]
                c2 = df_filtered[df_filtered["category"] == cat2_name]


            st.subheader("Comparison Table")

            comp = pd.DataFrame({
                "Metric":["Total incidents","Open","In Progress","Resolved","Critical Severity"],
                cat1_name:[len(c1), (c1["status"] == "Open").sum(), (c1["status"] == "In Progress").sum(), (c1["status"] == "Resolved").sum(),(c1["severity"] == "Critical").sum()],
                cat2_name:[len(c2), (c2["status"] == "Open").sum(), (c2["status"] == "In Progress").sum(), (c2["status"] == "Resolved").sum(),(c2["severity"] == "Critical").sum()],
            })
            st.dataframe(comp)

            with st.expander("View Raw Data"):
                st.dataframe(df_filtered)

    except Exception as e:
            st.error(f"Failed to load data: {e}")
    else:
        st.info("Please upload a CSV file to view charts and tables")


elif category == "Data Science":
    st.subheader("Data Science Datasets")
   
    try:

        uploaded_file = st.file_uploader("###Upload your Datasets Metasets CSV file here please📥",type=["csv"], key="datasets_metasets.csv")
        
        if uploaded_file:
        
            try: 
                df = pd.read_csv(uploaded_file)

                df_filtered = df.copy()

                if uploader_filter:
                    df_filtered = df_filtered[df_filtered["uploaded_by"].str.contains(uploader_filter, case=False, na=False)]

                    df_filtered = df_filtered[
                        (df_filtered["rows"] >= row_range[0]) &
                        (df_filtered["rows"] <= row_range[1])

                    ]
                st.success("Datasets metasets file uploaded sucessfully!")
                st.dataframe(df_filtered)

         
            except Exception as e:
                st.error(f"Error fetching Dataset table:{e}")
            
            st.markdown("Data Science Analytics Dashboard")   

            #-----KPI
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Datasets", len(df_filtered)) 

            with col2:
                st.metric("Total Rows",int(df_filtered["rows"].sum()))

            with col3:
                st.metric("Average Rows",int(df_filtered["rows"].mean()))

    
            st.markdown("---")
            st.subheader("Manage Datasets")

            #this will be for the inserting a new dataset
            with st.expander("Add new dataset"):
                with st.form("Insert_Dataset_Form"):

                    dataset_name = st.text_input("Dataset Name")
                    rows = st.number_input("Rows", min_value= 0, step=1)
                    columns = st.number_input("Columns", min_value= 0, step=1)
                    uploaded_by = st.text_input("Uploaded_by")
                    upload_date = st.date_input("Upload_date")
                    submit_add = st.form_submit_button("Add dataset")

                    if submit_add:
                        try:
                            dataset_id = insert_dataset(
                                st.session_state.conn,
                                dataset_name,
                                rows,
                                columns,
                                uploaded_by,
                                upload_date
                            )
                            st.success(f"Dataset added successfully! ID: {dataset_id}")
                        except Exception as e:
                            st.error(f"Failed to add dataset: {e}")
                
                #this will be for updating dataset category
            with st.expander("Update dataset category"):
                with st.form("Update_Dataset_Form"):
                    dataset_id = st.number_input("Dataset ID", min_value=1, step=1)
                    category = st.selectbox("New category",["Threat Intelligence","Network Logs","Fraud Detection","Machine Learning","Human Resources","Customer Analytics"])
                    submit_update = st.form_submit_button("Update dataset")
                    
                    if submit_update:
                        try:
                            rows = update_dataset(st.session_state.conn,dataset_id,category)
                            if rows > 0:
                                st.success(f"Dataset {dataset_id} category updated to {category}")

                            else:
                                st.warning(f"No dataset found with ID {dataset_id}")

                        except Exception as e:
                            st.error(f"Failed to update dataset: {e}")

            #this will be for deleting a dataset
            with st.expander("Delete dataset"):
                with st.form("Delete_Dataset_Form"):
                    dataset_id = st.number_input("Enter the dataset ID to be deleted", min_value=1, step=1)
                    submit_delete = st.form_submit_button("Delete dataset")
                    
                    if submit_delete:
                        try:
                            rows = delete_dataset(st.session_state.conn,dataset_id)
                            if rows > 0:
                                st.success(f"Dataset {dataset_id} deleted successfully")

                            else:
                                st.warning(f"No dataset found with ID {dataset_id}")

                        except Exception as e:
                            st.error(f"Failed to delete dataset: {e}")
                    
            st.markdown("---")
            #Largest datasets
            st.subheader("Largest Datasets(by rows)")
            largest = df_filtered.sort_values("rows", ascending=False).head(5)
            st.dataframe(largest)
            st.bar_chart(largest.set_index("name")["rows"]) 

            #top dataset contributors
            st.subheader("Top Dataset Contributors")
            contributors = df_filtered["uploaded_by"].value_counts().reset_index()                
            contributors.columns = ["uploaded_by", "total_datasets"]
            st.dataframe(contributors)
            st.bar_chart(contributors.set_index("uploaded_by")["total_datasets"])

            st.markdown("--")

            #------recent datasets
            st.subheader("Recently Uploaded Datasets")
            recent = df_filtered.sort_values("upload_date", ascending=False).head(10)
            st.dataframe(recent)

            #------viewing upload trend over time
            st.subheader("Uploads Over Time")
            df_filtered["upload_date"] = pd.to_datetime(df_filtered["upload_date"], errors= "coerce")
            fig2 = px.line(df_filtered.sort_values("upload_date"), x="upload_date", y= "rows", markers= True)
            st.plotly_chart(fig2, use_container_width=True)

            #------candidates who must be archived
            st.subheader("Candidates Who Must Be Archived")
            archive = df_filtered.sort_values("upload_date", ascending=False).head(5)
            st.dataframe(archive)

            #------dataset volume
            st.subheader("Dataset Volume Share")
            fig1 = px.pie(df_filtered, values="rows", names="name")
            st.plotly_chart(fig1, use_container_width=True)

            
            st.markdown("---")

            st.header("Dataset Comparision Section")

            ds1_name = st.selectbox("Select Dataset 1", df_filtered["name"])
            ds2_name = st.selectbox("Select Dataset 2", df_filtered["name"])

        
            ds1_row = df_filtered[df_filtered["name"] == ds1_name].iloc[0]
            ds2_row = df_filtered[df_filtered["name"] == ds2_name].iloc[0]


            st.subheader("Comparison Table")
            comp = pd.DataFrame({
                "Metric":["Rows","Columns","Uploader","Upload Date"],
                ds1_name:[ds1_row["rows"], ds1_row["columns"], ds1_row["uploaded_by"], ds1_row["upload_date"]],
                ds2_name:[ds1_row["rows"], ds2_row["columns"], ds2_row["uploaded_by"], ds2_row["upload_date"]],
            })
            st.dataframe(comp)

            with st.expander("View Raw Data"):
                st.dataframe(df_filtered)

    except Exception as e:
            st.error(f"Failed to load data: {e}")
    else:
        st.info("Please upload a CSV file to view charts and tables")


elif category == "IT Operations":
    st.subheader("IT tickets")
    
    uploaded_file = st.file_uploader("###Upload your IT tickets CSV file here please📥",type=["csv"], key="it_tickets.csv")
        
    if uploaded_file:
        
        try: 
            df = pd.read_csv(uploaded_file,parse_dates=["created_at"])
            df_filtered = df.copy()

            if priority_filter:
                df_filtered = df_filtered[df_filtered["priority"].isin(priority_filter)]

            if status_filter_IT:
                df_filtered = df_filtered[df_filtered["status"].isin(status_filter_IT)]

            if assigned_filter:
                df_filtered = df_filtered[df_filtered["assigned_to"].str.contains(assigned_filter, case=False, na=False)]


            st.success("IT tickets file uploaded sucessfully!")
            st.dataframe(df_filtered)

        except Exception as e:
            st.error(f"Failed to load file: {e}")

        st.markdown("---")

        st.markdown("IT Operations Analytics Dashboard")   

            #-----KPI
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Tickets", len(df_filtered)) 

        with col2:
            st.metric("Open Tickets", (df_filtered["status"] == "Open").sum()) 

        with col3:
            st.metric("In Progress", (df_filtered["status"] == "In Progress").sum())  

        with col4:
            st.metric("Resolved",(df_filtered["status"] == "Resolved").sum())   

        with col5:
            st.metric("Critical Priority", (df_filtered["priority"] == "Critical").sum())   
                
        st.markdown("--")
        st.subheader("Manage IT tickets")

        #this will be for the inserting a new ticket
        with st.expander("Add new ticket"):
            with st.form("Insert_Ticket_Form"):

                ticket_id = st.number_input("Ticket ID", min_value=1, step=1)
                priority = st.selectbox("Priority",["Low","Medium","High","Critical"])
                description = st.text_area("Description")
                status = st.selectbox("Status",["Open","In Progress","Resolved","Closed"])
                assigned_to = st.text_input("Assigned To")
                created_at = st.date_input("Created_at")
                resolution_time_hours = st.number_input("Resolution time hours", min_value=0.0, step=0.1)
                submit_add = st.form_submit_button("Add ticket")

                if submit_add:
                    try:
                        ticket_id = insert_tickets(
                            st.session_state.conn,
                            ticket_id,
                            priority,
                            description,                                
                            status,
                            assigned_to,
                            created_at,
                            resolution_time_hours

                        )
                        st.success(f"Ticket added successfully! ID: {ticket_id}")
                    except Exception as e:
                        st.error(f"Failed to add ticket: {e}")
                
            #this will be for updating ticket status
        with st.expander("Update ticket status"):
            with st.form("Update_Ticket_Form"):
                ticket_id = st.number_input("Ticket ID", min_value=1, step=1)
                status = st.selectbox("New Status",["Open","In Progress","Resolved","Closed"])
                submit_update = st.form_submit_button("Update ticket")
                    
                if submit_update:
                    try:
                        rows = update_tickets(st.session_state.conn,ticket_id,status)
                        if rows > 0:
                            st.success(f"Ticket {ticket_id} status updated to {status}")

                        else:
                            st.warning(f"No ticket found with ID {ticket_id}")

                    except Exception as e:
                        st.error(f"Failed to update ticket: {e}")

        #this will be for deleting a dataset
        with st.expander("Delete ticket"):
            with st.form("Delete_Ticket_Form"):
                ticket_id = st.number_input("Enter the ticket ID to be deleted", min_value=1, step=1)
                submit_delete = st.form_submit_button("Delete ticket")
                    
                if submit_delete:
                    try:
                        rows = delete_ticket(st.session_state.conn,ticket_id)
                        if rows > 0:
                            st.success(f"Ticket {ticket_id} deleted successfully")

                        else:
                            st.warning(f"No ticket found with ID {ticket_id}")

                    except Exception as e:
                        st.error(f"Failed to delete ticket: {e}")
                    
        st.markdown("---")

        col1, col2, col3= st.columns(3)

        with col1:
            st.subheader("Tickets by Status")
            by_status = df_filtered["status"].value_counts().reset_index()
            by_status.columns = ["status", "count"]
            fig1 = px.bar(by_status, x="status",  y="count", text="count")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Tickets by Priority")
            by_priority= df_filtered["priority"].value_counts().reset_index()
            by_priority.columns = ["priority", "count"]
            fig2 = px.bar(by_priority, x="priority",y="count", text="count")
            st.plotly_chart(fig2, use_container_width=True)

        with col3:
            st.subheader("Slowest Resolution By Status")
            avg_time= df_filtered.groupby("status")["resolution_time_hours"].mean().reset_index()
            fig3 = px.line(avg_time, x="status",y="resolution_time_hours", markers= True)
            st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Ticket Status Distribution")
        figp = px.pie(df_filtered, names="status")
        st.plotly_chart(figp, use_container_width=True)


        st.subheader("Additional Insights")


        #--------tickets with long resolution time
        st.subheader("Tickets with Long Resolution Times")
        long_tickets = df_filtered[df_filtered["resolution_time_hours"]> 48].sort_values("resolution_time_hours", ascending=False)
        st.dataframe(long_tickets)  

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Average Resolution Time(hrs)", round(df_filtered["resolution_time_hours"].mean(),2)) 

        with col2:
            st.metric("Max Resolution Time(hrs",df_filtered["resolution_time_hours"].max()) 

        with col3:
            st.metric("Min Resolution Time(hrs", df_filtered["resolution_time_hours"].min())

        #------tickets by assigned  person
        st.subheader("Tickets by Assigned To")
        by_person = df_filtered["assigned_to"].value_counts().reset_index()
        by_person.columns = ["assigned_to", "count"]
        fig4 = px.bar(by_person, x="assigned_to", y="count", text="count")
        st.plotly_chart(fig4, use_container_width=True)     

        #------recent tickets 
        st.subheader("Recent Tickets")
        recent = df_filtered.sort_values("created_at", ascending=False).head(10)
        st.dataframe(recent)

        #----------tickets over time
        st.subheader("Tickets Created Over Time")
        df_filtered["created_date"] = df_filtered["created_at"].dt.date 
        tickets_over_time = df_filtered.groupby("created_date").size().reset_index(name="count")
        fig5 = px.line(tickets_over_time, x="created_date", y="count", markers= True)
        st.plotly_chart(fig5, use_container_width=True)        
                
        #------high priority alerts
        st.subheader("High & Critical Tickets")
        alerts = df_filtered[df_filtered["priority"].isin(["High","Critical"])].sort_values("created_at", ascending=False)
        st.dataframe(alerts)

        st.markdown("---")
        st.header("IT Tickets Comparision Section")

        priority1 = st.selectbox("Select Priority 1", df_filtered["priority"].unique())
        priority2 = st.selectbox("Select Priority 2", df_filtered["priority"].unique())

        if priority1 and priority2:
            t1 = df_filtered[df_filtered["priority"] == priority1]
            t2 = df_filtered[df_filtered["priority"] == priority2]


            st.subheader("Comparison Table")

            comp = pd.DataFrame({
                "Metric":["Total tickets","Open","In Progress","Resolved","Critical Tickets"],
                priority1:[len(t1), (t1["status"] == "Open").sum(), (t1["status"] == "In Progress").sum(), (t1["status"] == "Resolved").sum(),(t1["priority"] == "Critical").sum()],
                priority2:[len(t2), (t2["status"] == "Open").sum(), (t2["status"] == "In Progress").sum(), (t2["status"] == "Resolved").sum(),(t2["priority"] == "Critical").sum()],
            })
            st.dataframe(comp)

        with st.expander("View Raw Data"):
                st.dataframe(df_filtered)

    else:
        st.info("Please upload a CSV file to view charts and tables")
    

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")

if not st.session_state.logged_in:
    st.error("You must be logged in...")
    st.switch_page("Home.py")
st.stop()