# -*- coding: utf-8 -*-
"""Untitled8.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1u8wV96WarctO0ElrakZTTaheqE4fOHY6
"""

import pandas as pd
import plotly.express as px

df=pd.read_csv("Genes.csv")

df

df.info()

df.describe()

df.dtypes

df.columns



df['user_id'].isnull().sum()

df1 = df.dropna(subset=['user_id'])

df1

df1['user_type'] = df1['user_id'].apply(lambda x: 'Free user' if x.startswith('unknown') else 'Logged In')

df1

rename_mapping = {df1.columns[i]: f"col_{i}" for i in range(1, 110)}
df1.rename(columns=rename_mapping, inplace=True)

df1

df1.columns

df2 = df1.iloc[:, 1:-2]

df2

all_values = df2.values.flatten()
all_values = pd.Series(all_values).dropna()

all_values_counts=all_values.value_counts()

all_values_counts

user_type_counts = df1['user_type'].value_counts()

user_type_counts

api_hit_sum = df1['userInfo.apiHitCount'].sum()

api_hit_sum

#!pip install streamlit

import streamlit as st

import streamlit as st
import pandas as pd
import plotly.express as px

# Example DataFrames (replace with actual data)
data1 = {
    'user_type': ['Free user', 'Logged In', 'Free user', 'Logged In', 'Free user'],
    'userInfo.apiHitCount': [5, 10, 15, 20, 25],
    'col3': [1, 2, 3, 4, 5]
}
df1 = pd.DataFrame(data1)

# Streamlit Dashboard
st.title("Data Dashboard")

# Filter for 'user_type'
user_type_filter = st.sidebar.multiselect(
    "Filter by User Type",
    options=df1['user_type'].unique(),
    default=df1['user_type'].unique()
)

# Apply filter to df1
filtered_df1 = df1[df1['user_type'].isin(user_type_filter)]

# Update all_value_counts and api_hit_sum based on filter
if 'col3' in filtered_df1:
    filtered_col3 = filtered_df1['col3']
    all_values_counts = pd.Series(filtered_col3).value_counts()
else:
    all_values_counts = pd.Series(dtype=int)

api_hit_sum = filtered_df1['userInfo.apiHitCount'].sum()

# Display Bar Chart for all_value_counts
st.subheader("Flattened df2 Value Counts (Bar Chart)")
if not all_values_counts.empty:
    bar_chart = px.bar(
        all_values_counts,
        x=all_values_counts.index,
        y=all_values_counts.values,
        labels={"x": "Value", "y": "Count"},
        title="All Value Counts"
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
st.write(api_hit_sum)

filtered_df1

filtered_col3

all_values_counts
