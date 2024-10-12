# import numpy as np
# import matplotlib.pyplot as plt 
 
# # creating the dataset
# data = {'Weather Conditions':6, 'Zoning Laws':7, 'Soil Type':8, 'Site Topography':7, 'Environmental Conditions':8, 'Water Resources':8, 'Utility Access':9 ,'Terrain History':6 , 'Safety Standards':8 ,'Pollution and Noise':7 }
# factors = list(data.keys())
# values = list(data.values())
 
# # creating the bar plot
# plt.bar(factors, values, color ='maroon', width = 0.2)

# plt.xlabel("Factors")
# plt.ylabel("Score")
# plt.title("Evaluation Report")
# plt.show()


# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# import json
# # Function to read data from CSV or JSON
# def read_data(file_path):
#     if file_path.endswith('.csv'):
#         df = pd.read_csv(file_path)
#         data = dict(zip(df['Factors'], df['Score']))
#     elif file_path.endswith('.json'):
#         with open(file_path, 'r') as f:
#             data = json.load(f)
#     else:
#         raise ValueError("File format not supported. Use CSV or JSON.")
#     return data
# # Adjust this file path as needed
# file_path = 'data.json'
# # Read the dataset from CSV or JSON
# data = read_data(file_path)
# factors = list(data.keys())
# values = list(data.values())
# # Create the bar plot
# plt.bar(factors, values, color='maroon', width=0.4)
# # Fixing overlapping labels by rotating them
# plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels by 45 degrees
# plt.xlabel("Factors")
# plt.ylabel("Score")
# plt.title("Evaluation Report")
# # Adjust layout to prevent cutoff
# plt.tight_layout()
# # Show the plot
# plt.show()




import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
# Function to read data from CSV or JSON
def read_data(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        data = dict(zip(df['Factors'], df['Score']))
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        raise ValueError("File format not supported. Use CSV or JSON.")
    return data
# Adjust this file path as needed
file_path = 'data.json'
# Read the dataset from CSV or JSON
data = read_data(file_path)
factors = list(data.keys())
values = list(data.values())
# Create the bar plot
bars = plt.bar(factors, values, color='maroon', width=0.4)
# Fixing overlapping labels by rotating them
plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels by 45 degrees
# Display values on top of each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', va='bottom')
# Set y-axis ticks to reflect a scale of 10
plt.yticks(np.arange(0, 11, 1))  # Sets the scale from 0 to 10 with a step of 1
plt.xlabel("Factors")
plt.ylabel("Score (Out of 10)")
plt.title("Evaluation Report (Scale of 10)")
# Adjust layout to prevent cutoff
plt.tight_layout()
# Show the plot
plt.show()


# # Create a pie chart
# plt.pie(values, labels=factors, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
# plt.title("Evaluation Report (Pie Chart)")
# plt.tight_layout()
# plt.show()


# #Heatmap
# import seaborn as sns
# import numpy as np
# import matplotlib.pyplot as plt
# # Create a heatmap-style visualization
# plt.figure(figsize=(8, 2))  # Adjust the figure size
# heatmap_data = np.array(values).reshape(1, -1)
# sns.heatmap(heatmap_data, annot=True, cmap="Reds", xticklabels=factors, yticklabels=['Score'], cbar=False)
# plt.title("Evaluation Report (Heatmap)")
# plt.tight_layout()
# plt.show()


# #Radar
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# import json
# # Function to read data from CSV or JSON
# def read_data(file_path):
#     if file_path.endswith('.csv'):
#         df = pd.read_csv(file_path)
#         data = dict(zip(df['Factors'], df['Score']))
#     elif file_path.endswith('.json'):
#         with open(file_path, 'r') as f:
#             data = json.load(f)
#     else:
#         raise ValueError("File format not supported. Use CSV or JSON.")
#     return data
# # Adjust this file path as needed
# file_path = 'data.json'
# # Read the dataset
# data = read_data(file_path)
# factors = list(data.keys())
# values = list(data.values())
# # Add the first value at the end to close the radar chart
# values += values[:1]
# factors += factors[:1]
# # Create a radar chart
# fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
# # Calculate the angle for each axis
# angles = np.linspace(0, 2 * np.pi, len(factors), endpoint=False).tolist()
# # Plot and fill the radar chart
# ax.fill(angles, values, color='maroon', alpha=0.25)
# ax.plot(angles, values, color='maroon', linewidth=2)
# # Add labels
# ax.set_yticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
# ax.set_yticklabels(['2', '4', '6', '8', '10'])
# ax.set_xticks(angles[:-1])
# ax.set_xticklabels(factors, rotation=45, ha="right")
# # Title
# plt.title('Evaluation Report (Scale of 10)', size=15)
# plt.tight_layout()
# plt.show()