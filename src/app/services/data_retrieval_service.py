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
        print("Using cached data.")
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
    print("Queried data from MySQL and updated cache.")
    return df

def GenerateScatterPlot(response:ClassificationResponse):
    df=query_table_with_cache()
    categories=[]
    time=[]
    numerical=[]

    for entity in response.entities:
        if entity.label in categorical_features:
            categories.append(entity.label)
        elif entity.label in numerical_features:
                    numerical.append(entity.label)
        elif entity.label in time_features:
                    time.append(entity.label)

    # For this example, assume the scatter plot needs a numerical feature on x-axis and a categorical feature on y-axis
     # Default numerical features
    x_feature = "SALES"
    y_feature = "QUANTITY"

    if len(categories) == 0:
        raise ValueError("Need at least one categorical feature for scatter plot.")

    plt.figure(figsize=(10, 6))

    first_category = categories[0]
    unique_values = df[first_category].unique()
    for unique_value in unique_values:
        subset = df[df[first_category] == unique_value]
        plt.scatter(subset[x_feature], subset[y_feature], label=unique_value)

    # Annotate each point with the other categories
    for category in categories[1:]:
        for i in range(df.shape[0]):
            plt.annotate(f"{df[category][i]}: {df[first_category][i]}", (df[x_feature][i], df[y_feature][i]))

    plt.xlabel(x_feature)
    plt.ylabel(y_feature)
    plt.title(f'Scatter Plot of {x_feature} vs {y_feature} by {", ".join(categories)}')
    plt.legend(title=first_category)
   
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    return buf


  
def GenerateBarChart(response:ClassificationResponse):
    df=query_table_with_cache()
    
  # Initialize lists for categories, time, and numerical features
    categories = []
    time = []
    numerical = ["SALES"]

    # Classify entities based on their labels
    for entity in response.entities:
        if entity.label in categorical_features:
            categories.append(entity.label)
        elif entity.label in numerical_features:
            numerical.append(entity.label)
        elif entity.label in time_features:
            time.append(entity.label)

    # Ensure there is at least one categorical feature and one numerical feature
    if len(categories) < 1:
        raise ValueError("At least one categorical feature is required for grouping.")
    # if len(numerical) < 1:
    #     raise ValueError("At least one numerical feature is required for plotting.")
   
    df = df.drop(columns=time_features)
    # Group data by the identified categorical features and sum the numerical feature
    grouped_df = df.groupby(categories).sum()

    # If there is more than one categorical feature, unstack the DataFrame
    if len(categories) > 1:
        grouped_df = grouped_df.unstack()

    # Plotting
    fig, ax = plt.subplots()

    # Define bar width and positions
    bar_width = 0.2
    positions = np.arange(len(grouped_df))

    # Plot bars for each numerical feature
    for i, numerical_feature in enumerate(numerical):
        if len(categories) > 1:
            for j, category in enumerate(grouped_df[numerical_feature].columns):
                ax.bar(positions + j * bar_width, grouped_df[numerical_feature][category], bar_width, label=f'{category} ({numerical_feature})')
        else:
            ax.bar(positions + i * bar_width, grouped_df[numerical_feature], bar_width, label=numerical_feature)

    # Set the position of the x ticks
    ax.set_xticks(positions + bar_width / 2)
    ax.set_xticklabels(grouped_df.index)

    # Set labels and title
    plt.xlabel(categories[0] if len(categories) == 1 else ' & '.join(categories))
    plt.ylabel('Value')
    plt.title('Grouped Bar Chart')
    plt.legend(title='Legend')

    # Show plot
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    return buf


def GeneratePieChart(response):
    df=query_table_with_cache()
    categories = []
    time = []
    numerical = ["SALES"]

    # Classify entities based on their labels
    for entity in response.entities:
        if entity.label in categorical_features:
            categories.append(entity.label)
        elif entity.label in numerical_features:
            numerical.append(entity.label)
        elif entity.label in time_features:
            time.append(entity.label)

    # Ensure there is at least one categorical feature and one numerical feature
    if len(categories) < 1:
        raise ValueError("At least one categorical feature is required for grouping.")
    elif len(categories) != 1:
        raise ValueError("Only one categorical feature is required for a pie chart.")

    df = df.drop(columns=time_features)
    # Group by the categorical feature and sum the numerical values
    grouped_df = df.groupby(categories).sum().reset_index()

    # Extract labels and values for the pie chart
    labels = grouped_df[categories[0]]
    values = grouped_df["SALES"]

    # Create the pie chart with increased size
    fig, ax = plt.subplots(figsize=(10, 7))  # Adjust figsize as needed
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%')

    plt.title(f'Pie Chart of Sales by {categories[0]}')

    # Place the legend outside the pie chart
    ax.legend(wedges, labels, title=categories[0], loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    # Save the plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)

    return buf
