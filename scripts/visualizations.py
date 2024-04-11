import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Data
processes = [2, 3, 1, 4, 5, 6]
execution_times = [59.3911, 53.123, 70.357, 51.0872, 61.3629, 65.6088]

# Create a DataFrame for better handling of the data
df = pd.DataFrame({'Processes': processes, 'Execution Time': execution_times})

# 1. Bar Plot
plt.figure(figsize=(10, 6))
sns.barplot(x='Processes', y='Execution Time', data=df, ci=None)
plt.title('Average Execution Time for Each Number of Processes')
plt.xlabel('Number of Processes')
plt.ylabel('Average Execution Time (seconds)')
plt.grid(True)
plt.show()

# 2. Box Plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='Processes', y='Execution Time', data=df)
plt.title('Distribution of Execution Times for Each Number of Processes')
plt.xlabel('Number of Processes')
plt.ylabel('Execution Time (seconds)')
plt.grid(True)
plt.show()

# 3. Scatter Plot
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Processes', y='Execution Time', data=df, s=100)
plt.title('Individual Execution Times for Each Number of Processes')
plt.xlabel('Number of Processes')
plt.ylabel('Execution Time (seconds)')
plt.grid(True)
plt.show()

# 4. Line Plot with Regression
plt.figure(figsize=(10, 6))
sns.regplot(x='Processes', y='Execution Time', data=df)
plt.title('Execution Time vs. Number of Processes with Regression')
plt.xlabel('Number of Processes')
plt.ylabel('Execution Time (seconds)')
plt.grid(True)
plt.show()
