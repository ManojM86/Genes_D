#!/usr/bin/env python
# coding: utf-8

# In[97]:


from pymongo import MongoClient
import pandas as pd


# In[98]:


mongo_uri = "mongodb+srv://ms9876:mongodb_1234@cluster0.mfmcl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Use secure handling for credentials


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
        "_id": 0,  # Exclude the MongoDB default _id field
        "user_id": 1,
        "firstname": "$userInfo.userProfile.firstName",
        "lastname": "$userInfo.userProfile.lastName",
        "email": "$userInfo.userProfile.email",
        "threadListSize": 1  # Include the threadList count
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
        "_id": 0,  # Exclude MongoDB default _id
        "date": "$threadList.date"  # Include the threadList.date field only
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


month_counts = df_dates['MonthYear'].value_counts().sort_index()
chart_data = pd.DataFrame({
    'MonthYear': month_counts.index,
    'Count': month_counts.values
})
month_order = pd.to_datetime(chart_data['MonthYear'], format='%b%y')
chart_data['MonthYear'] = pd.Categorical(chart_data['MonthYear'], categories=chart_data['MonthYear'][month_order.argsort()], ordered=True)


# In[110]:


import streamlit as st
import altair as alt
st.title("Interactive Dashboard")

# Buttons for Gene and Drug Count Bar Charts
st.header("Gene Count Chart")
chart = alt.Chart(gene_df).mark_bar().encode(
    x=alt.X("Gene:N", sort=None, title="Gene"),  # X-axis: Genes
    y=alt.Y("Count:Q", title="Count"),          # Y-axis: Counts
    tooltip=["Gene", "Count"]                   # Tooltip with Gene and Count
).properties(
    width=700,                                  # Chart width
    height=400,                                 # Chart height
    title="Count of Genes"
)

# Display the chart in Streamlit
st.altair_chart(chart, use_container_width=True)

st.header("Drug Count Chart")
chart = alt.Chart(drug_df).mark_bar().encode(
    x=alt.X("Drug:N", sort=None, title="Drug"),  # X-axis: Genes
    y=alt.Y("Count:Q", title="Count"),          # Y-axis: Counts
    tooltip=["Drug", "Count"]                   # Tooltip with Gene and Count
).properties(
    width=700,                                  # Chart width
    height=400,                                 # Chart height
    title="Count of Drugs"
)

# Display the chart in Streamlit
st.altair_chart(chart, use_container_width=True)

# Button for Month Bar Chart
st.header("Show Month Bar Chart")

chart = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X('MonthYear:N', sort=list(chart_data['MonthYear'].cat.categories), title='Month-Year'),
    y=alt.Y('Count:Q', title='Count'),
    tooltip=['MonthYear', 'Count']
).properties(
    title="Month-Year Counts"
)

# Display the chart in Streamlit
st.altair_chart(chart, use_container_width=True)

st.header("User Info")
st.dataframe(user_df)


# In[ ]:





# In[ ]:





# In[ ]:




