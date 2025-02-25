#!/usr/bin/env python
# coding: utf-8

# In[2]:




# In[3]:


from pymongo import MongoClient
import pandas as pd


# In[4]:


mongo_uri = "mongodb+srv://ms9876:mongodb_1234@cluster0.mfmcl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


# In[5]:


client = MongoClient(mongo_uri)


# In[4]:


db = client['pgxApp']


# In[5]:


collection1 = db['userSubscription']


# In[6]:


collection2 = db['pgx_threads']


# In[7]:
gene_pipeline = [
    {"$match": {"user_id": {"$not": {"$regex": "^unknown"}}}},
    {"$unwind": "$input"},
    {"$unwind": "$input.gene_phenotype_options"},
    {"$group": {
        "_id": "$input.gene_phenotype_options.gene",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}}
]
gene_results = list(collection2.aggregate(gene_pipeline))
gene_df = pd.DataFrame(gene_results)
gene_df.rename(columns={"_id": "Gene", "count": "Count"}, inplace=True)
#gene_df


# In[104]:


import pandas as pd
drug_pipeline = [
    {"$match": {"user_id": {"$not": {"$regex": "^unknown"}}}},
    {"$unwind": "$threadList"},
    {"$group": {
        "_id": "$threadList.current_drug",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}}
]
drug_results = list(collection2.aggregate(drug_pipeline))
drug_df = pd.DataFrame(drug_results)
drug_df.rename(columns={"_id": "Drug", "count": "Count"}, inplace=True)
#drug_df


# In[105]:


user_pipeline = [
    {"$match": {"user_id": {"$not": {"$regex": "^unknown"}}}},
    {"$addFields": {"threadListSize": {"$size": "$threadList"}}},
    {"$project": {
        "_id": 0, 
        "user_id": 1,
        "firstname": "$userInfo.userProfile.firstName",
        "lastname": "$userInfo.userProfile.lastName",
        "email": "$userInfo.userProfile.email",
        "threadListSize": 1 
    }}
]
user_results = list(collection2.aggregate(user_pipeline))
user_df = pd.DataFrame(user_results)
user_df.rename(columns={
    "user_id": "UserId",
    "firstname": "FirstName",
    "lastname": "LastName",
    "email": "Email",
    "threadListSize": "ThreadList Count"
}, inplace=True)
user_df=user_df[['UserId','FirstName','LastName','Email','ThreadList Count']]
#user_df


# In[106]:


import pandas as pd
from datetime import datetime
date_pipeline = [
    {"$match": {"user_id": {"$not": {"$regex": "^unknown"}}}},
    {"$unwind": "$threadList"},
    {"$project": {
        "_id": 0,  
        "date": "$threadList.date" 
    }}
]
date_results = list(collection2.aggregate(date_pipeline))


# In[107]:


df_dates = pd.DataFrame(date_results)
#df_dates


# In[108]:


df_dates['Date'] = pd.to_datetime(df_dates['date'],unit='ms', errors='coerce')
df_dates['Date1'] = df_dates['Date'].dt.date
df_dates['MonthYear'] = df_dates['Date'].dt.strftime('%b%y')
df_dates = df_dates[['Date1', 'MonthYear']]
#df_dates


# In[109]:


month_avg = (
    df_dates.groupby('MonthYear')
    .size()  
    .reset_index(name='Count')  
)
month_order = pd.to_datetime(month_avg['MonthYear'], format='%b%y')
month_avg['MonthYear'] = pd.Categorical(month_avg['MonthYear'], categories=month_avg['MonthYear'][month_order.argsort()], ordered=True)

#question&Answers
pipeline_user_ids = [
    {"$match": {"user_id": {"$not": {"$regex": "^unknown"}}}}, 
    {"$group": {"_id": "$user_id"}}, 
    {"$sort": {"_id": 1}}
]
user_ids = list(collection2.aggregate(pipeline_user_ids))
user_ids = [doc["_id"] for doc in user_ids] 
#user_ids

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


# In[8]:


#query_df


# In[9]:


merged_df = pd.merge(user_df, query_df, on='user_id', how='inner')


# In[10]:


question_counts = merged_df.groupby(['role', 'question','answer']).size().reset_index(name='count')


# In[11]:


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


# In[12]:


#merged_df


# In[13]:


#new_df


# In[15]:


#get_ipython().system('pip install streamlit')


# In[16]:



import streamlit as st
import altair as alt


# In[17]:


# Streamlit App
st.title("Role-Based Question Insights")

st.header("Mostly Asked Questions")
roles = question_counts['role'].unique()
selected_role = st.selectbox("Select a Role:", roles)
filtered_df = question_counts[question_counts['role'] == selected_role].sort_values(by='count', ascending=False)
st.dataframe(filtered_df[['question', 'answer', 'count']].reset_index(drop=True))


# In[18]:


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


# In[ ]:
st.header("Gene Count Chart")
chart = alt.Chart(gene_df).mark_bar().encode(
    x=alt.X("Gene:N", sort=None, title="Gene"),  
    y=alt.Y("Count:Q", title="Count"),          
    tooltip=["Gene", "Count"]                   
).properties(
    width=700,                                  
    height=400,                                 
    title="Count of Genes"
)
st.altair_chart(chart, use_container_width=True)

st.header("Drug Count Chart")
chart = alt.Chart(drug_df).mark_bar().encode(
    x=alt.X("Drug:N", sort=None, title="Drug"),  
    y=alt.Y("Count:Q", title="Count"),          
    tooltip=["Drug", "Count"]                   
).properties(
    width=700,                                  
    height=400,                                 
    title="Count of Drugs"
)
st.altair_chart(chart, use_container_width=True)

# Month Bar Chart
st.header("Month Bar Chart")

heatmap = alt.Chart(month_avg).mark_rect().encode(
    x=alt.X('MonthYear:N', sort=list(month_avg['MonthYear'].cat.categories), title='Month-Year'),
    y=alt.Y('Count:Q', title='Count'),
    color=alt.Color('Count:Q', scale=alt.Scale(scheme='viridis'), title='Count'),
    tooltip=['MonthYear', 'Count']
).properties(
    title="Heatmap of Counts by Month-Year",
    width=600,
    height=400
)
st.altair_chart(heatmap, use_container_width=True)

st.header("User Info")
st.dataframe(user_df)


# In[ ]:

# dropdown in Streamlit to select a user ID
selected_user_id = st.selectbox("Select User ID:", user_ids)

#If a user ID is selected, display the corresponding questions and answers
if selected_user_id:
    pipeline_questions_answers = [
        {"$match": {"user_id": selected_user_id}}, 
        {"$unwind": "$input"}, 
        {"$unwind": "$input.input_data"},
        {"$project": {
            "_id": 0,
            "user_id": 1,
            "question": "$input.input_data.question", 
            "answer": "$input.input_data.answer" 
        }}
    ]
    results = list(collection2.aggregate(pipeline_questions_answers))
    if results:
        df = pd.DataFrame(results)
        st.write(f"Questions and Answers for User ID: {selected_user_id}")
        st.dataframe(df)
    else:
        st.warning(f"No data found for User ID: {selected_user_id}")




