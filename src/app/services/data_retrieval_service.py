import io
import json
from matplotlib import pyplot as plt
import pandas as pd
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '../../')
sys.path.append(src_path)

from app.models.classification_response import ClassificationResponse

categorical_features = set([
  "AGE",
  "GENDER",
  "DEVICE_TYPE",
  "CUSTOMER_LOGIN_TYPE",
  "PRODUCT_CATEGORY",
  "PRODUCT",
  "ORDER_PRIORITY",
  "PAYMENT_METHOD",
  "COUNTRY"
])
time_features=set([
  "ORDER_DATE"
])

numerical_features=set([
  "SALES",
  "QUANTITY",
  "DISCOUNT",
  "PROFIT",
  "SHIPPING_COST"
])

# GenerateBarChart
# GenerateLineChart
# GeneratePieChart
# GenerateScatterPlot
# GenerateHeatmap
# GenerateHistogram
data = {
    "COUNTRY": ["Kenya", "Kenya", "USA", "USA", "Germany", "Germany", "India", "India"],
    "PRODUCT": ["Tshirt", "Shoes", "Dress", "Shoes", "Tshirt", "Shoes", "Tshirt", "Shoes"],
    "SALES": [150, 200, 300, 250, 180, 220, 260, 210],
    "QUANTITY": [500, 700, 1200, 950, 600, 750, 1100, 800]
}

# Create DataFrame
df = pd.DataFrame(data)

def GenerateScatterPlot(response:ClassificationResponse):
    categories=[]
    time=[]
    numerical=[]

    for entity in response.entities:
        if entity.label in categorical_features:
            print(entity.label)
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
    # for category in categories:
    #     if category in df.columns:  # Check if the category is in the DataFrame columns
    #         unique_values = df[category].unique()
    #         for unique_value in unique_values:
    #             subset = df[df[category] == unique_value]
    #             plt.scatter(subset[x_feature], subset[y_feature], label=f"{category}: {unique_value}")

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
    # for i in range(df.shape[0]):
    #     plt.annotate(f"{df['COUNTRY'][i]}: {df['PRODUCT'][i]}", (df['SALES'][i], df['QUANTITY'][i]))
    # plt.show()
    # Save the plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    return buf


  

