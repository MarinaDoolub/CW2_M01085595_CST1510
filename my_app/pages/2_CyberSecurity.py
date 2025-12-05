import streamlit as st
import pandas as pd
from openai import OpenAI
from app.data.db import connect_database
from my_app.sidebar import sidebar_navigation, ai_chat
import plotly.express as px
import plotly.graph_objects as go
from app.data.incidents import insert_incident,update_incident_status,delete_incident,get_incidents_by_category,get_bottleneck_categories_by_status,get_resolution_status_breakdown

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
    
# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")

    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()


##initializing client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

#sidebar with its contents
category, filters = sidebar_navigation()
ai_chat(client)


# If logged in, show dashboard content
st.title("📊 Multi-Intelligence Domain Platform")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

st.subheader("Cyber Security")
  
try:
    df = pd.read_sql_query("SELECT * FROM cyber_incidents", st.session_state.conn)
    
except Exception as e:
    st.error(f"Failed to load data: {e}")
    df = pd.DataFrame()

#CSV uploading section
uploaded_file = st.file_uploader("###Upload your Cyber Incidents CSV file here please📥",type=["csv"], key="cyber_incidents.csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Cyber Incidents file uploaded sucessfully!")
    except Exception as e:
        st.error(f"Failed to load file:{e}")

df_filtered = df.copy()
if not df_filtered.empty:
     df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"], errors="coerce")
            
if filters.get("severity"):
    df_filtered = df_filtered[df_filtered["severity"].isin(filters["severity"])]

if filters.get("status"):
    df_filtered = df_filtered[df_filtered["status"].isin(filters["status"])]


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
    

