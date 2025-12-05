import streamlit as st
import pandas as pd
from openai import OpenAI
import plotly.express as px
from app.data.db import connect_database
from my_app.sidebar import sidebar_navigation, ai_chat
from app.data.datasets import insert_dataset,update_dataset,delete_dataset


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

st.subheader("Data Science Datasets")

  
try:
    df = pd.read_sql_query("SELECT * FROM datasets_metadata", st.session_state.conn)
    
except Exception as e:
    st.error(f"Failed to load data: {e}")
    df = pd.DataFrame()

    

uploaded_file = st.file_uploader("###Upload your Datasets Metasets CSV file here please📥",type=["csv"], key="datasets_metasets.csv")

if uploaded_file:
        try: 
            df = pd.read_csv(uploaded_file)
            st.success("Datasets metasets file uploaded sucessfully!")
         
        except Exception as e:
            st.error(f"Error fetching Dataset table:{e}")

df_filtered = df.copy()

if filters.get("uploader"):
                df_filtered = df_filtered[df_filtered["uploaded_by"].str.contains(filters["uploader_filter"], case=False, na=False)]
                df_filtered = df_filtered[
                    (df_filtered["rows"] >= filters["row_range"][0]) &
                    (df_filtered["rows"] <= filters["row_range"][1])
                    ]
st.dataframe(df_filtered)

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
st.bar_chart(largest.set_index("dataset_name")["rows"]) 

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
fig1 = px.pie(df_filtered, values="rows", names="dataset_name")
st.plotly_chart(fig1, use_container_width=True)

            
st.markdown("---")

st.header("Dataset Comparision Section")

ds1_name = st.selectbox("Select Dataset 1", df_filtered["dataset_name"])
ds2_name = st.selectbox("Select Dataset 2", df_filtered["dataset_name"])

        
ds1_row = df_filtered[df_filtered["dataset_name"] == ds1_name].iloc[0]
ds2_row = df_filtered[df_filtered["dataset_name"] == ds2_name].iloc[0]


st.subheader("Comparison Table")
comp = pd.DataFrame({
     "Metric":["Rows","Columns","Uploader","Upload Date"],
    ds1_name:[ds1_row["rows"], ds1_row["columns"], ds1_row["uploaded_by"], ds1_row["upload_date"]],
    ds2_name:[ds1_row["rows"], ds2_row["columns"], ds2_row["uploaded_by"], ds2_row["upload_date"]],
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
