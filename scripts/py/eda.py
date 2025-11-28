# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# %%
df = pd.read_excel("../../Data/processed/firearm_data_cleaned.xlsx")

df.head()

# Basic Descriptive Statistics

## Key Variables Summary
df[["year", "rate", "deaths", "law_strength_score", "restrictive_laws", "permissive_laws"]].describe()

## Categorical Table Counts
df['year'].value_counts()
df['state_name'].value_counts()

## Categorical Distribution Plots
sns.countplot(x='year', data=df)
sns.countplot(x='state_name', data=df)

## Numeric Distribution Plots
sns.displot(df['rate'], kde=True)
sns.displot(df['deaths'], kde=True)
sns.displot(df['law_strength_score'], kde=True)
sns.displot(df['restrictive_laws'], kde=True)
sns.displot(df['permissive_laws'], kde=True)
# %%

# Boxplot of Year by Rate
sns.boxplot(x='year', y='rate', data=df)
plt.show()


# %% 
# NA Values
df[['state_name','year', 'deaths', 'rate', 'law_strength_score', 'restrictive_laws', 'permissive_laws']].isna().sum()

# %%
# Correlation Heatmap
correlation_matrix = df[['year', 'rate', 'law_strength_score', 'restrictive_laws', 'permissive_laws']].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.show()

# %%
# Average Firearm Death Rate by State and plot
rate_by_state_top = df.groupby('state_name')['rate'].mean().sort_values(ascending=False).head(10)
rate_by_state_bottom = df.groupby('state_name')['rate'].mean().sort_values(ascending=False).tail(10)
ax = sns.barplot(x=rate_by_state_top.values, y=rate_by_state_top.index, orient='h')
ax.set(xlabel='Average Firearm Death Rate', ylabel='State')

ax2 = sns.barplot(x=rate_by_state_bottom.values, y=rate_by_state_bottom.index, orient='h')
ax2.set(xlabel='Average Firearm Death Rate', ylabel='State')
plt.show()

# %% 
# Average Law Strength Score by State and plot
strength_by_state_top = df.groupby('state_name')['law_strength_score'].mean().sort_values(ascending=False).head(10)
strength_by_state_bottom = df.groupby('state_name')['law_strength_score'].mean().sort_values(ascending=False).tail(10)
ax = sns.barplot(x=strength_by_state_top.values, y=strength_by_state_top.index, orient='h')
ax.set(xlabel='Average Law Strength Score', ylabel='State')

ax2 = sns.barplot(x=strength_by_state_bottom.values, y=strength_by_state_bottom.index, orient='h')
ax2.set(xlabel='Average Law Strength Score', ylabel='State')
plt.show()

# %% 
# Average Firearm Death Rate Over Time Line Plot
# Average Law Strength Score Over Time Line Plot
ax = sns.lineplot(x='year', y='rate', data=df, marker='o')
ax.set(xlabel='Year', ylabel='Average Firearm Death Rate')

ax2 = sns.lineplot(x='year', y='law_strength_score', data=df, marker='o')
ax2.set(xlabel='Year', ylabel='Average Law Strength Score')

plt.show()

# %% Gun Law Strength vs Firearm Death Rate
sns.scatterplot(x='law_strength_score', y='rate', data=df, )
plt.show()