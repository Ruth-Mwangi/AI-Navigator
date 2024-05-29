from datetime import timedelta
import io
import json
import pickle
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import sys
import os

import redis

from app.utils.util import create_mysql_connection, get_data_features
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '../../')
sys.path.append(src_path)

from app.models.classification_response import ClassificationResponse
import plotly.graph_objects as go
import plotly.io as pio
import io

categorical_features = set(get_data_features('categorical_features'))
time_features=set(get_data_features('time_features'))

numerical_features=set(get_data_features('numerical_features'))


try:
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_client.ping()  # Test connection
except redis.ConnectionError:
    print("Failed to connect to Redis. Ensure Redis is running on localhost:6379.")
    redis_client = None
def query_table_with_cache():
    cache_key = f"table_cache:'transactions'"
    
    # Check if the table data is in Redis cache
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return pickle.loads(cached_data)
    
    # If cache is not valid, query the table
    conn=create_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    query = f"SELECT * FROM transactions"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    # Convert to pandas DataFrame
    df = pd.DataFrame(data)
    
    # Store the result in Redis cache with an expiration time of 15 minutes
    redis_client.setex(cache_key, timedelta(minutes=15), pickle.dumps(df))
    cached_data = redis_client.get(cache_key)
   
    return pickle.loads(cached_data) 

def classify_entities(response):
    categories = []
    numerical = []
    filter_map = {}

    for entity in response.entities:
        if entity.label in categorical_features:
            categories.append(entity.label)
        elif entity.label in numerical_features:
            numerical.append(entity.label)
        elif entity.label in time_features:
            pass  # You mentioned time features are not needed in this context
        elif 'value' in entity.label.lower():
            entity_label, value_part = entity.label.rsplit("_", 1)
            if entity_label in filter_map:
                filter_map[entity_label].append(entity.text)
            else:
                filter_map[entity_label] = [entity.text]
    if len(numerical)==0:
        numerical = ["SALES"]

    return categories, numerical, filter_map

import plotly.graph_objects as go

def GenerateScatterPlot(response: ClassificationResponse):
    df = query_table_with_cache()
    categories, numerical, filter_map = classify_entities(response)

    for key, values in filter_map.items():
        pattern = '|'.join(values)  # Create a regex pattern for the values
        df = df[df[key].str.contains(pattern, case=False, na=False)]

    if len(categories) < 1:
        raise ValueError("Need at least one categorical feature for scatter plot.")
    if len(numerical) != 2:
        raise ValueError("Need two numerical features (sales, discount, order sizes) for scatter plot.")

    x_feature = numerical[0]
    y_feature = numerical[1]

    fig = go.Figure()
    df=df.sample(n=2000)

    for category_value in df[categories[0]].unique():
        subset = df[df[categories[0]] == category_value]
        fig.add_trace(go.Scatter(
            x=subset[x_feature],
            y=subset[y_feature],
            mode='markers',
            name=str(category_value)
        ))

    fig.update_layout(
        title=f'Scatter Plot of {x_feature} vs {y_feature} by {", ".join(categories)}',
        xaxis_title=x_feature,
        yaxis_title=y_feature,
        legend_title=categories[0].replace("_"," "),
        legend=dict( x=1, y=0.5, traceorder="normal", font=dict(family="Arial, sans-serif")),
        autosize=True,  # Automatically adjust the chart size to fit its contents
        width=1200
    )

    # Format y-axis ticks to display in thousands
    fig.update_yaxes(tickformat=",.0f", tickprefix="$")

    # Return the Plotly figure as HTML
    return fig.to_html(full_html=False)



  
def GenerateBarChart(response: ClassificationResponse):
    df = query_table_with_cache()

    # Initialize lists for categories, time, and numerical features
    categories, numerical, filter_map = classify_entities(response)

    for key, values in filter_map.items():
        pattern = '|'.join(values)  # Create a regex pattern for the values
        df = df[df[key].str.contains(pattern, case=False, na=False)]

    # Ensure there is at least one categorical feature and one numerical feature
    if len(categories) < 1:
        raise ValueError("At least one categorical feature is required for grouping.")
    if len(numerical) < 1:
        raise ValueError("At least one numerical feature is required for plotting.")

    df = df.drop(columns=time_features)

    # Group data by the identified categorical features and sum the numerical feature
    grouped_df = df.groupby(categories).sum()

    # If there is more than one categorical feature, unstack the DataFrame
    if len(categories) > 1:
        grouped_df = grouped_df.unstack()

    # Create Plotly figure
    fig = go.Figure()

    # Add bars for each numerical feature
    if len(categories) > 1:
        for numerical_feature in numerical:
            for category in grouped_df[numerical_feature].columns:
                fig.add_trace(go.Bar(
                    x=grouped_df.index,
                    y=grouped_df[numerical_feature][category],
                    name=f'{numerical_feature} - {category}'
                ))
    else:
        for numerical_feature in numerical:
            fig.add_trace(go.Bar(
                x=grouped_df.index,
                y=grouped_df[numerical_feature],
                name=numerical_feature
            ))

    # Update layout for scrollable plot
    fig.update_layout(
        xaxis={'categoryorder':'total descending'},
        xaxis_title=categories[0].replace("_"," ") if len(categories) == 1 else ' & '.join(categories).replace("_"," "),
        yaxis_title=numerical[0],
        title=f'Bar Chart of {numerical[0].replace("_"," ")} by {", ".join(categories).replace("_"," ")}',
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        xaxis_tickangle=-45,
        width=1200 + len(grouped_df) * 15,  # Adjust width dynamically based on the number of categories
        height=600,
        font=dict(family="Arial, sans-serif"),
        legend=dict( x=1, y=0.5, traceorder="normal", font=dict(family="Arial, sans-serif")),
        

    )

    graph_html = pio.to_html(fig, full_html=False)

    return graph_html



def GeneratePieChart(response):
    df = query_table_with_cache()
    
    categories, numerical, filter_map = classify_entities(response)
    
    for key, values in filter_map.items():
        pattern = '|'.join(values)  # Create a regex pattern for the values
        df = df[df[key].str.contains(pattern, case=False, na=False)]

    # Ensure there is at least one categorical feature and one numerical feature
    if len(categories) < 1:
        raise ValueError("At least one categorical feature is required for grouping.")
    elif len(categories) > 1:
        raise ValueError("Only one categorical feature is required for a pie chart.")

    df = df.drop(columns=time_features)
    
    # Group by the categorical feature and sum the numerical values
    grouped_df = df.groupby(categories).sum().reset_index()

    # Extract labels and values for the pie chart
    labels = grouped_df[categories[0].replace("_"," ")]
    values = grouped_df[numerical[0]]

    # Create the pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='percent')])

    # Update layout
    fig.update_layout(
        title=f'Pie Chart of {numerical[0].replace("_", " ")} by {categories[0].replace("_", " ")}',
        legend=dict(title=categories[0], x=1, y=0.5, traceorder="normal", font=dict(family="Arial, sans-serif")),
        font=dict(family="Arial, sans-serif"),
        autosize=False,  # Disable autosizing
        # width=400  # Set the width of the chart to 400 pixels (adjust as needed)
    )

    # Convert the plot to HTML and return
    return fig.to_html(full_html=False)
