# -*- coding: utf-8 -*-
import pandas as pd
import plotly.express as px

df=pd.read_csv("Genes.csv")

#df

#df.info()

#df.describe()

#df.dtypes

#df.columns



df['user_id'].isnull().sum()

df1 = df.dropna(subset=['user_id'])

#df1

df1['user_type'] = df1['user_id'].apply(lambda x: 'Free user' if x.startswith('unknown') else 'Logged In')

#df1

rename_mapping = {df1.columns[i]: f"col_{i}" for i in range(1, 110)}
df1.rename(columns=rename_mapping, inplace=True)

#df1

#df1.columns

df2 = df1.iloc[:, 1:-2]

#df2

all_values = df2.values.flatten()
all_values = pd.Series(all_values).dropna()

all_values_counts=all_values.value_counts()

#all_values_counts

user_type_counts = df1['user_type'].value_counts()

#user_type_counts

api_hit_sum = df1['userInfo.apiHitCount'].sum()

#api_hit_sum

#!pip install streamlit

import streamlit as st

# Streamlit Dashboard
st.title("Dashboard for Gene, User and ApiHit Count")
st.sidebar.header('User Input Parameters')
# Filter for 'user_type'
user_type_filter = st.sidebar.multiselect(
    "Filter by User Type",
    options=df1['user_type'].unique(),
    default=df1['user_type'].unique()
)

# Apply filter to df1
filtered_df1 = df1[df1['user_type'].isin(user_type_filter)]

values = filtered_df1.iloc[:,1:110].values.flatten()
values = pd.Series(values).dropna()

values_counts=values.value_counts()

# Display Bar Chart for Name Counts
st.subheader("Gene Type Counts")
if not all_values_counts.empty:
    bar_chart = px.bar(
        values_counts,
        x=values_counts.index,
        y=values_counts.values,
        labels={"x": "Gene Type", "y": "Count"},
        title="Gene Type Counts"
    )
    st.plotly_chart(bar_chart)

# Display Pie Chart for user_type value counts
st.subheader("User Type Value Counts (Pie Chart)")
user_type_counts = filtered_df1['user_type'].value_counts()
if not user_type_counts.empty:
    pie_chart = px.pie(
        user_type_counts,
        names=user_type_counts.index,
        values=user_type_counts.values,
        title="User Type Distribution"
    )
    st.plotly_chart(pie_chart)

# Display Total API Hit Count
st.subheader("Total API Hit Count")
api_hit_sum = filtered_df1['userInfo.apiHitCount'].sum()
st.write(api_hit_sum)

