#!/usr/bin/env python
# coding: utf-8

# In[106]:


from pymongo import MongoClient
import pandas as pd
import plotly.express as px


# In[2]:


mongo_uri = "mongodb+srv://ms9876:mongodb_1234@cluster0.mfmcl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Use secure handling for credentials


# In[3]:


client = MongoClient(mongo_uri)


# In[4]:


db = client['Data_Dat']


# In[5]:


collection = db['Drug']


# In[6]:


data = list(collection.find())


# In[7]:


df=pd.DataFrame(data)


# In[44]:


df.columns=df.columns.str.lower()


# In[45]:


#df


# In[39]:


def flatten_selected_column(df, column, sep="_"):
    def flatten(row, parent_key=""):
        items = []
        if isinstance(row, dict):
            for key, value in row.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                if isinstance(value, dict):
                    items.extend(flatten(value, new_key).items())
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        items.extend(flatten({f"{new_key}[{i}]": item}).items())
                else:
                    items.append((new_key, value))
        elif isinstance(row, list):
            for i, item in enumerate(row):
                items.extend(flatten({f"{parent_key}[{i}]": item}).items())
        else:
            items.append((parent_key, row))
        return dict(items)

    # Normalize the selected column
    expanded_data = df[column].apply(lambda x: flatten(x) if isinstance(x, (dict, list)) else x)
    
    # Create a new DataFrame from the expanded column
    normalized_df = pd.DataFrame(expanded_data.tolist())
    
    # Combine the normalized data with the original DataFrame
    df = df.drop(columns=[column]).reset_index(drop=True)
    result_df = pd.concat([df, normalized_df], axis=1)
    
    return result_df


# In[48]:


def flatten_column(df,column_name):
    new_df=pd.DataFrame(df[column_name])
    new_flattened = flatten_selected_column(new_df,column_name)
    new_flattened.columns = new_flattened.columns.str.lower()
    return new_flattened
    


# In[51]:


df['user_type'] = df['user_id'].apply(lambda x: 'Free user' if x.startswith('unknown') else 'Logged In')
df1 = df[df['user_type'] == 'Logged In']


# In[101]:


user_df=flatten_column(df1,'userinfo')
user_details=user_df.groupby(['userid', 'userprofile_firstname', 'userprofile_lastname',
       'userprofile_email']).size().reset_index(name='value_counts').rename(columns={
        'user_id': 'UserID', 
        'userinfo_userprofile_firstname': 'First Name', 
        'userinfo_userprofile_lastname': 'Last Name', 
        'userinfo_userprofile_email': 'Email', 
        'value_counts': 'ThreadList Counts'})
#user_details


# In[100]:


sub_status=[col for col in user_df.columns if 'subscription_status' in col.lower()]
sub_status_count = user_df['subscriptiondetails_subscription_status'].value_counts()
#sub_status_count


# In[58]:


input_df=flatten_column(df1,'input')
#input_df


# In[67]:


gene_phenotype_option = [col for col in input_df.columns if 'gene_phenotype_option' in col.lower()]
gene = [col for col in gene_phenotype_option if col.lower().count("_gene") >= 2]
gene_count=pd.Series(input_df[gene].values.flatten()).dropna()


# In[96]:


total_gene=gene_count.value_counts()
#total_gene


# In[71]:


thread_list=flatten_column(df1,'threadlist')
#thread_list


# In[97]:


drug_list = [col for col in thread_list.columns if 'current_drug' in col.lower()]
drug_count=pd.Series(thread_list[drug_list].values.flatten()).dropna()
drug_total_count =drug_count.value_counts()


# In[78]:


date_columns = [col for col in thread_list.columns if 'date' in col.lower()]
#date_columns


# In[79]:


for col in date_columns:
    # Convert timestamps to datetime, handling null values
    thread_list[col] = pd.to_datetime(thread_list[col], unit='ms', errors='coerce')  # Convert timestamps
    thread_list[f"{col}_time"] = thread_list[col].dt.time  # Create new column for time
    thread_list[col] = thread_list[col].dt.date  # Replace original column with date


# In[92]:


date_count=pd.DataFrame(pd.Series(thread_list[date_columns].values.flatten()).dropna())
#date_count


# In[94]:


date_count = date_count.rename(columns={0:'date'})
date_count['date'] = pd.to_datetime(date_count['date'])
date_count['week'] = date_count['date'].dt.isocalendar().week
date_count['month'] = date_count['date'].dt.month
date_count['month'] = date_count['date'].dt.strftime('%B')
month_order = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
]
date_count['month'] = pd.Categorical(date_count['month'], categories=month_order, ordered=True)
#date_count


# In[108]:


import streamlit as st
import plotly.express as px


# In[110]:


st.title("Interactive Dashboard")

# Buttons for Gene and Drug Count Bar Charts
st.header("Gene Count Chart")
fig_gene = px.bar(
    x=total_gene.index,
    y=total_gene.values,
    title="Gene Count",
    labels={"x": "Gene", "y": "Count"}
)
st.plotly_chart(fig_gene)

st.header("Drug Count Chart")
fig_drug = px.bar(
    x=drug_total_count.index,
    y=drug_total_count.values,
    title="Drug Count",
    labels={"x": "Drug", "y": "Count"}
)
st.plotly_chart(fig_drug)

# Button for Subscription Count Pie Chart
st.header(" Subscription Count Chart")
fig_subscription = px.bar(
    x=sub_status_count.index,
    y=sub_status_count.values,
    title="Subscription Count",
    labels={"x":"Subscription Type", "y":"Count"}
)
st.plotly_chart(fig_subscription)

st.header("Show Month Bar Chart")
month_count = date_count["month"].value_counts().sort_index()
fig_month = px.bar(
    x=month_count.index,
    y=month_count.values,
    title="Month Distribution",
    labels={"x": "Month", "y": "Count"}
)
st.plotly_chart(fig_month)


st.header("User Info")
st.dataframe(user_details)


# In[ ]:




