# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 23:54:04 2024

@author: Kkath
"""


import pandas as pd 
import sqlite3
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

#import subprocess
# Download the dataset using Kaggle API
#command = "kaggle datasets download -d ahmedshahriarsakib/usa-real-estate-dataset"
#subprocess.run(command, shell=True)

# Load data
df = pd.read_csv('E:/Personal/MyProject/usa-real-estate-dataset.zip', compression='zip')
# Create a sqlite engine 
engine = create_engine('sqlite://', echo=False)
# Explore the dataframe as a table to the sqlite engine
df.to_sql("realtor", con=engine, index=False)

#Average Price of Real Estate for Sale by Year
with engine.begin() as conn:
    bosquery = text("""
    SELECT *
    FROM realtor
    WHERE city IN ('Boston','New Boston','South Boston','East Boston') AND prev_sold_date BETWEEN '2019-01-01' and '2022-12-31'
    ORDER BY prev_sold_date DESC
    """)
    df2 = pd.read_sql_query(bosquery, conn)        
df2.drop(['state'], axis=1)
# Convert 'prev_sold_date' to datetime and extract year
df2['prev_sold_date'] = pd.to_datetime(df2['prev_sold_date'])
df2['year'] = df2['prev_sold_date'].dt.year
# Group by year and status, and calculate average price
grouped_data = df2.groupby(['year', 'status']).price.mean().reset_index()
# Pivot the data for plotting
pivot_data = grouped_data.pivot(index='year', columns='status', values='price')
# Plotting
ax = pivot_data.plot(kind='bar')
plt.xlabel('Year')
plt.ylabel('Average Price')
plt.title('Average Price of Real Estate for Sale by Year')
# Adding the exact number on each bar
for p in ax.patches:
    ax.text(p.get_x() + p.get_width() / 2., p.get_height(), 
            f'{p.get_height():.2f}', 
            ha='center', va='bottom')
plt.show()

#Correlation
with engine.begin() as conn:
    corquery = text("""
    SELECT bed, bath, acre_lot, house_size, price
    FROM realtor 
    WHERE city IN ('Boston','New Boston','South Boston','East Boston')
    AND prev_sold_date BETWEEN '2019-01-01' and '2022-12-31'
    ORDER BY prev_sold_date DESC
    """)
    df3 = pd.read_sql(corquery, conn)
df3 = df3.dropna(subset=['acre_lot'])
corr = df3.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.show()

#Zipcode
with engine.begin() as conn:
    zipquery = text("""
    SELECT zip_code AS zipcode, AVG(price) AS average_price, strftime('%Y', prev_sold_date) AS year
    FROM realtor
    WHERE city IN ('Boston','New Boston','South Boston','East Boston')
    AND prev_sold_date BETWEEN '2019-01-01' and '2022-12-31'
    GROUP BY strftime('%Y', prev_sold_date), zip_code
    """)
    df4 = pd.read_sql(zipquery, conn)
df4 = df4.dropna()
# Load the shapefile or GeoJSON file for Boston zip codes into a GeoDataFrame
gdf = gpd.read_file('E:/Personal/MyProject/ZIP_Codes.shp')
# Make sure that the 'zipcode' columns are of the same type to allow merging
gdf['zipcode'] = gdf['ZIP5'].astype(str)
df4['zipcode'] = df4['zipcode'].astype(int).astype(str).str.zfill(5)
# Merge the GeoDataFrame with your df4 DataFrame on the 'zipcode' column
merged_gdf = gdf.merge(df4, on='zipcode')


# Plotting the map - 2019
filtered_gdf1 = merged_gdf[merged_gdf['year'] == '2019']
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
# Plot all zip codes with a neutral color to ensure the entire Boston area is covered
gdf.plot(ax=ax, color='lightgrey')
# Overlay the filtered data for 2019
filtered_gdf1.plot(column='average_price', ax=ax, legend=True, cmap='OrRd',
                   legend_kwds={'label': "Average Price by Zip Code"},
                   vmin=filtered_gdf1['average_price'].quantile(0.1),  # 10th percentile
                   vmax=filtered_gdf1['average_price'].quantile(0.9))  # 90th percentile

ax.set_title('Boston Zip Code Areas by Average Price - 2019')
plt.axis('off')
plt.show()

# Plotting the map - 2020
filtered_gdf2 = merged_gdf[merged_gdf['year'] == '2020']
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
# Plot all zip codes with a neutral color to ensure the entire Boston area is covered
gdf.plot(ax=ax, color='lightgrey')
# Overlay the filtered data for 2019
filtered_gdf2.plot(column='average_price', ax=ax, legend=True, cmap='OrRd',
                   legend_kwds={'label': "Average Price by Zip Code"},
                   vmin=filtered_gdf2['average_price'].quantile(0.1),  # 10th percentile
                   vmax=filtered_gdf2['average_price'].quantile(0.9))  # 90th percentile
ax.set_title('Boston Zip Code Areas by Average Price - 2020')
plt.axis('off')
plt.show()

# Plotting the map - 2021
filtered_gdf3 = merged_gdf[merged_gdf['year'] == '2021']
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
# Plot all zip codes with a neutral color to ensure the entire Boston area is covered
gdf.plot(ax=ax, color='lightgrey')
# Overlay the filtered data for 2019
filtered_gdf3.plot(column='average_price', ax=ax, legend=True, cmap='OrRd',
                   legend_kwds={'label': "Average Price by Zip Code"},
                   vmin=filtered_gdf3['average_price'].quantile(0.1),  # 10th percentile
                   vmax=filtered_gdf3['average_price'].quantile(0.9))  # 90th percentile
ax.set_title('Boston Zip Code Areas by Average Price - 2021')
plt.axis('off')
plt.show()