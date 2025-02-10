#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pymongo import MongoClient
import pandas as pd


# In[2]:


mongo_uri = "mongodb+srv://ms9876:mongodb_1234@cluster0.mfmcl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  


# In[3]:


client = MongoClient(mongo_uri)


# In[4]:


db = client['Data_Dat']


# In[5]:


collection1 = db['User_Info']


# In[6]:


collection2 = db['Drug']


# In[7]:
user_pipeline = [
    {"$match": {"user_id": {"$not": {"$regex": "^unknown"}}}},
    {"$project": {
        "_id": 0, 
        "user_id": 1,
        "role" : "$role"
    }}
]
user_results = list(collection1.aggregate(user_pipeline))
user_df = pd.DataFrame(user_results)

pipeline_questions_answers = [
        {"$match": {"user_id": {"$not": {"$regex": "^unknown"}}}}, 
        {"$unwind": "$input"}, 
        {"$unwind": "$input.input_data"},
        {"$project": {
            "_id": 0,
            "user_id": 1,
            "question": "$input.input_data.question", 
            "answer": "$input.input_data.answer" 
}}
]
query_results = list(collection2.aggregate(pipeline_questions_answers))
query_df = pd.DataFrame(query_results)


# In[17]:


merged_df = pd.merge(user_df, query_df, on='user_id', how='inner')

# In[22]:


question_counts = merged_df.groupby(['role', 'question','answer']).size().reset_index(name='count')

new_pipeline = [
    {"$project": {
        "_id": 0, 
        "user_id": "$user_id",
        "role" : "$role",
        "affiliation" : "$affiliation",
        "jobTitle" : "$jobTitle",
        "country" : "$country"
    }}
]
new_results = list(collection1.aggregate(new_pipeline))
new_df = pd.DataFrame(new_results)
# In[24]:


import streamlit as st


# In[25]:


# Streamlit App
st.title("Role-Based Question Insights")

st.header("Mostly Asked Questions")
roles = question_counts['role'].unique()
selected_role = st.selectbox("Select a Role:", roles)
filtered_df = question_counts[question_counts['role'] == selected_role].sort_values(by='count', ascending=False)
st.dataframe(filtered_df[['question', 'answer', 'count']].reset_index(drop=True))

st.header("Role Based")
import matplotlib.pyplot as plt

selected_role = st.multiselect("Select Role(s):", new_df['role'].unique())
selected_affiliation = st.multiselect("Select Affiliation(s):", new_df['affiliation'].unique())
selected_job_title = st.multiselect("Select Job Title(s):", new_df['jobTitle'].unique())
selected_country = st.multiselect("Select Country(ies):", new_df['country'].unique())
filtered_df = new_df.copy()
if selected_role:
    filtered_df = filtered_df[filtered_df['role'].isin(selected_role)]
if selected_affiliation:
    filtered_df = filtered_df[filtered_df['affiliation'].isin(selected_affiliation)]
if selected_job_title:
    filtered_df = filtered_df[filtered_df['jobTitle'].isin(selected_job_title)]
if selected_country:
    filtered_df = filtered_df[filtered_df['country'].isin(selected_country)]

filtered_df = filtered_df.drop(columns=['user_id'])
st.subheader(f"Total Users Matching Filters: {len(filtered_df)}")

st.subheader("Count of Users by Role")
role_counts = filtered_df['role'].value_counts().reset_index()
role_counts.columns = ['Role', 'Count']

st.bar_chart(role_counts.set_index('Role'))


