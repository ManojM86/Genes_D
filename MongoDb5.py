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


def pipeline(a):
    pipeline = [
    {"$group": {"_id":  f"${a}",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}}
    ]
    results = list(collection1.aggregate(pipeline))
    df = pd.DataFrame(results)
    df.rename(columns={"_id": a, "count": "Count"}, inplace=True)
    return df


# In[8]:


pipeline('role')


# In[9]:


pipeline('affiliation')


# In[10]:


pipeline('jobTitle')


# In[11]:


pipeline("country")


# In[12]:


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
#user_df


# In[15]:


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
#query_df


# In[17]:


merged_df = pd.merge(user_df, query_df, on='user_id', how='inner')
#merged_df


# In[22]:


question_counts = merged_df.groupby(['role', 'question','answer']).size().reset_index(name='count')

# Step 3: Sort by count in descending order
#sorted_df = question_counts.sort_values(by='count', ascending=False)

#sorted_df
new_pipeline = [
    {"$project": {
        "_id": 0, 
        "user_id": "$user_id",
        "role" : "$role",
        "affiliation" : "$affiliation",
        "jontitle" : "$jobTitle",
        "country" : "$country"
    }}
]
new_results = list(collection1.aggregate(new_pipeline))
new_df = pd.DataFrame(new_results)
#new_df

# In[24]:


import streamlit as st


# In[25]:


# Streamlit App
st.title("Role-Based Question Insights")

st.header("Mostly Asked Questions")
# Role Filter
roles = question_counts['role'].unique()
selected_role = st.selectbox("Select a Role:", roles)

# Filter data based on selected role and sort by count in descending order
filtered_df = question_counts[question_counts['role'] == selected_role].sort_values(by='count', ascending=False)

# Display the filtered DataFrame
st.dataframe(filtered_df[['question', 'answer', 'count']].reset_index(drop=True))


# In[ ]:
import matplotlib.pyplot as plt

st.header(" Count")
selected_role = st.multiselect("Select Role(s):", new_df['role'].unique())
selected_affiliation = st.multiselect("Select Affiliation(s):", new_df['affiliation'].unique())
selected_job_title = st.multiselect("Select Job Title(s):", new_df['jobTitle'].unique())
selected_country = st.multiselect("Select Country(ies):", new_df['country'].unique())

# Applying Filters
filtered_df = new_df.copy()

if selected_role:
    filtered_df = filtered_df[filtered_df['role'].isin(selected_role)]
if selected_affiliation:
    filtered_df = filtered_df[filtered_df['affiliation'].isin(selected_affiliation)]
if selected_job_title:
    filtered_df = filtered_df[filtered_df['jobTitle'].isin(selected_job_title)]
if selected_country:
    filtered_df = filtered_df[filtered_df['country'].isin(selected_country)]

# Display Filtered Data
st.dataframe(filtered_df)

# Bar Chart
st.subheader("Count of Users by Role")
role_counts = filtered_df['role'].value_counts()

fig, ax = plt.subplots()
role_counts.plot(kind='bar', ax=ax)
ax.set_xlabel('Role')
ax.set_ylabel('Count')
ax.set_title('User Count by Role')
st.pyplot(fig)



