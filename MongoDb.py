#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().system('pip install pymongo')


# In[17]:


from pymongo import MongoClient
import pandas as pd
import plotly.express as px


# In[44]:


mongo_uri = "mongodb://localhost:27017"  # Use Streamlit secrets for secure handling
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)


# In[45]:


client = MongoClient(mongo_uri)


# In[46]:


db = client['Data_Dat']


# In[47]:


collection = db['Genes']


# In[48]:


data = list(collection.find())


# In[49]:


def flatten_nested_json(data, sep="_"):
    """Recursively flattens nested JSON fields."""
    def flatten(row, parent_key=""):
        items = []
        for key, value in row.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(flatten(value, new_key).items())
            elif isinstance(value, list):
                # Optional: Normalize lists or join them
                for i, item in enumerate(value):
                    items.extend(flatten({f"{new_key}[{i}]": item}).items())
            else:
                items.append((new_key, value))
        return dict(items)

    return pd.DataFrame([flatten(record) for record in data])


# In[50]:


df = flatten_nested_json(data)


# In[51]:


#df


# In[52]:


#df.columns


# In[53]:


#df.shape


# In[54]:


df['user_id'].isnull().value_counts()


# In[55]:


df['user_type'] = df['user_id'].apply(lambda x: 'Free user' if x.startswith('unknown') else 'Logged In')


# In[56]:


#df.shape


# In[57]:


#df['user_type'].value_counts()


# In[73]:


df.columns = df.columns.str.lower()


# In[74]:


#df


# In[75]:


df1 = df[df['user_type'] == 'Logged In']


# In[76]:


#df1


# In[79]:


date_columns = [col for col in df1.columns if 'date' in col.lower()]


# In[80]:


#len('date_columns')


# In[81]:


#date_columns


# In[84]:


timestamp_columns = [col for col in date_columns if 'threadlist' in col.lower()]


# In[85]:


#timestamp_columns


# In[86]:


for col in timestamp_columns:
    # Convert timestamps to datetime, handling null values
    df1[col] = pd.to_datetime(df1[col], unit='ms', errors='coerce')  # Convert timestamps
    df1[f"{col}_time"] = df1[col].dt.time  # Create new column for time
    df1[col] = df1[col].dt.date  # Replace original column with date


# In[88]:


#df1['threadlist[0]_date']


# In[89]:


date_count=df1[['threadlist[0]_date',
 'threadlist[1]_date',
 'threadlist[2]_date',
 'threadlist[3]_date',
 'threadlist[4]_date',
 'threadlist[5]_date',
 'threadlist[6]_date',
 'threadlist[7]_date',
 'threadlist[8]_date',
 'threadlist[9]_date',
 'threadlist[10]_date',
 'threadlist[11]_date',
 'threadlist[12]_date',
 'threadlist[13]_date',
 'threadlist[14]_date',
 'threadlist[15]_date',
 'threadlist[16]_date',
 'threadlist[17]_date',
 'threadlist[18]_date',
 'threadlist[19]_date',
 'threadlist[20]_date',
 'threadlist[21]_date',
 'threadlist[22]_date',
 'threadlist[23]_date',
 'threadlist[24]_date',
 'threadlist[25]_date',
 'threadlist[26]_date',
 'threadlist[27]_date',
 'threadlist[28]_date',
 'threadlist[29]_date',
 'threadlist[30]_date',
 'threadlist[31]_date',
 'threadlist[32]_date',
 'threadlist[33]_date',
 'threadlist[34]_date',
 'threadlist[35]_date',
 'threadlist[36]_date',
 'threadlist[37]_date',
 'threadlist[38]_date',
 'threadlist[39]_date',
 'threadlist[40]_date',
 'threadlist[41]_date',
 'threadlist[42]_date',
 'threadlist[43]_date',
 'threadlist[44]_date',
 'threadlist[45]_date',
 'threadlist[46]_date',
 'threadlist[47]_date',
 'threadlist[48]_date',
 'threadlist[49]_date',
 'threadlist[50]_date',
 'threadlist[51]_date',
 'threadlist[52]_date',
 'threadlist[53]_date',
 'threadlist[54]_date',
 'threadlist[55]_date',
 'threadlist[56]_date',
 'threadlist[57]_date',
 'threadlist[58]_date',
 'threadlist[59]_date',
 'threadlist[60]_date',
 'threadlist[61]_date',
 'threadlist[62]_date',
 'threadlist[63]_date',
 'threadlist[64]_date',
 'threadlist[65]_date',
 'threadlist[66]_date',
 'threadlist[67]_date',
 'threadlist[68]_date',
 'threadlist[69]_date',
 'threadlist[70]_date']].values.flatten()


# In[90]:


date_count=pd.Series(date_count).dropna()


# In[94]:


date_count= pd.DataFrame(date_count)


# In[95]:


#date_count


# In[98]:


date_count = date_count.rename(columns={0: 'date'})


# In[99]:


#date_count


# In[101]:


date_count['date'] = pd.to_datetime(date_count['date'])
date_count['week'] = date_count['date'].dt.isocalendar().week
date_count['month'] = date_count['date'].dt.month


# In[102]:


#date_count


# In[103]:


subscription_type = [col for col in df1.columns if 'subscription_type' in col.lower()]


# In[104]:


#subscription_type


# In[105]:


df1['userinfo_subscriptiondetails_subscription_type'].value_counts()


# In[106]:


subscription_status = [col for col in df1.columns if 'subscription_status' in col.lower()]


# In[107]:


#subscription_status


# In[108]:


df1['userinfo_subscriptiondetails_subscription_status'].value_counts()


# In[109]:


df1['userinfo_subscriptiondetails_subscription_status'].isnull().sum()


# In[110]:


gene_phenotype_option = [col for col in df1.columns if 'gene_phenotype_option' in col.lower()]


# In[111]:


#gene_phenotype_option


# In[115]:


gene = [col for col in gene_phenotype_option if col.lower().count("_gene") >= 2]


# In[116]:


#gene


# In[121]:


gene_count =pd.Series(df1[gene].values.flatten()).dropna()


# In[123]:


gene_total_count = gene_count.value_counts()


# In[124]:


#gene_total_count


# In[125]:


drug_list = [col for col in df1.columns if 'current_drug' in col.lower()]


# In[127]:


current_drug = [col for col in drug_list if 'threadlist' in col.lower()]
#current_drug


# In[129]:


drug_count =pd.Series(df1[current_drug].values.flatten()).dropna().value_counts()
#drug_count


# In[137]:


import streamlit as st


# In[138]:


import plotly.express as px


# In[139]:


st.title("Interactive Dashboard")

# Week Bar Chart (Always Displayed)
st.header("Week Bar Chart")
week_count = date_count["week"].value_counts().sort_index()
fig_week = px.bar(
    x=week_count.index,
    y=week_count.values,
    title="Week Distribution",
    labels={"x": "Week", "y": "Count"}
)
st.plotly_chart(fig_week)

# Buttons for Gene and Drug Count Bar Charts
if st.button("Show Gene and Drug Count Bar Chart"):
    # Gene Count Bar Chart
    fig_gene = px.bar(
        x=gene_total_count.index,
        y=gene_total_count.values,
        title="Gene Count",
        labels={"x": "Gene", "y": "Count"}
    )
    st.plotly_chart(fig_gene)

    # Drug Count Bar Chart
    fig_drug = px.bar(
        x=drug_count.index,
        y=drug_count.values,
        title="Drug Count",
        labels={"x": "Drug", "y": "Count"}
    )
    st.plotly_chart(fig_drug)

# Button for Subscription Count Pie Chart
if st.button("Show Subscription Count Pie Chart"):
    subscription_count= df1['userinfo_subscriptiondetails_subscription_type'].value_counts()
    fig_subscription = px.pie(
        values=subscription_count.values,
        names=subscription_count.index,
        title="Subscription Count"
    )
    st.plotly_chart(fig_subscription)

# Button for Month Bar Chart
if st.button("Show Month Bar Chart"):
    month_count = date_count["Month"].value_counts().sort_index()
    fig_month = px.bar(
        x=month_count.index,
        y=month_count.values,
        title="Month Distribution",
        labels={"x": "Month", "y": "Count"}
    )
    st.plotly_chart(fig_month)


# In[ ]:




