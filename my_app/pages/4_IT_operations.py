import streamlit as st
import pandas as pd
from openai import OpenAI
from app.data.db import connect_database
from my_app.sidebar import sidebar_navigation, ai_chat
import plotly.express as px
from app.data.it_tickets import insert_tickets,update_tickets,delete_ticket


#
# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
        
# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")

    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()


#connection section
#___________________________-
conn = st.session_state.conn

if "username" not in st.session_state:
    st.session_state.username = ""

##initializing client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

#sidebar with its contents
category, filters = sidebar_navigation()
ai_chat(client)

# If logged in, show dashboard content
st.title("📊 Multi-Intelligence Domain Platform")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

st.subheader("IT tickets")

 
try:
    df = pd.read_sql_query("SELECT * FROM it_tickets", st.session_state.conn)
    
except Exception as e:
    st.error(f"Failed to load data: {e}")
    df = pd.DataFrame()
    
uploaded_file = st.file_uploader("###Upload your IT tickets CSV file here please📥",type=["csv"], key="it_tickets.csv")
if uploaded_file:
        
    try: 
        df = pd.read_csv(uploaded_file,parse_dates=["created_at"])
        st.success("IT tickets file uploaded sucessfully!")

    except Exception as e:
        st.error(f"Failed to load file: {e}")



df_filtered = df.copy()

if filters.get("priority"):
    df_filtered = df_filtered[df_filtered["priority"].isin(filters["priority"])]

if filters.get("status_IT"):
    df_filtered = df_filtered[df_filtered["status"].isin(filters["status_IT"])]

if filters.get("assigned"):
    df_filtered = df_filtered[df_filtered["assigned_to"].str.contains(filters["assigned"], case=False, na=False)]

st.dataframe(df_filtered)

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
df_filtered["created_at"] = pd.to_datetime(df_filtered["created_at"])
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
