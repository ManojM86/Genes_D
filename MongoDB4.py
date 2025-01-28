#!/usr/bin/env python
# coding: utf-8

# In[97]:


from pymongo import MongoClient
import pandas as pd


# In[98]:


mongo_uri = "mongodb+srv://ms9876:mongodb_1234@cluster0.mfmcl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  


# In[99]:


client = MongoClient(mongo_uri)


# In[100]:


db = client['Data_Dat']


# In[101]:


collection = db['Drug']


# In[102]:


#collection


# In[103]:


import pandas as pd
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
gene_results = list(collection.aggregate(gene_pipeline))
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
drug_results = list(collection.aggregate(drug_pipeline))
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
user_results = list(collection.aggregate(user_pipeline))
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
date_results = list(collection.aggregate(date_pipeline))


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
    {"$match": {"user_id": {"$not": {"$regex": "^unknown"}}}},  # Exclude unknown user_ids
    {"$group": {"_id": "$user_id"}},  # Group by user_id to get unique IDs
    {"$sort": {"_id": 1}}  # Sort user IDs alphabetically
]
user_ids = list(collection.aggregate(pipeline_user_ids))
user_ids = [doc["_id"] for doc in user_ids] 
#user_ids

# In[110]:


import streamlit as st
import altair as alt
st.title("Interactive Dashboard")

# Gene and Drug Count Bar Charts
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

# Step 2: Create a dropdown in Streamlit to select a user ID
selected_user_id = st.selectbox("Select User ID:", user_ids)

# Step 3: If a user ID is selected, fetch and display the corresponding questions and answers
if selected_user_id:
    pipeline_questions_answers = [
        {"$match": {"user_id": selected_user_id}},  # Filter for the selected user ID
        {"$unwind": "$input"},  # Unwind the input array
        {"$unwind": "$input.input_data"},  # Unwind the input_data array
        {"$project": {
            "_id": 0,
            "user_id": 1,
            "question": "$input.input_data.question",  # Extract the question
            "answer": "$input.input_data.answer"  # Extract the answer
        }}
    ]

    # Execute the pipeline to fetch questions and answers
    results = list(collection.aggregate(pipeline_questions_answers))

    # Convert results to a DataFrame
    if results:
        df = pd.DataFrame(results)

        # Display the DataFrame in Streamlit
        st.write(f"Questions and Answers for User ID: {selected_user_id}")
        st.dataframe(df)
    else:
        st.warning(f"No data found for User ID: {selected_user_id}")




# In[ ]:





# In[ ]:




