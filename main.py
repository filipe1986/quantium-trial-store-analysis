
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
pd.set_option('display.max_columns', None)

#creating the dataframes
df = pd.read_csv('qvi_data.csv')

df.columns = df.columns.str.lower() # making the column names all lowercase

df['date'] = pd.to_datetime(df['date']) # changing the column datatype

df['month'] = df['date'].dt.to_period('M') # creating a column for month

# --- Creating some metrics to analyse the stores behavior ---

revenue = df.groupby(['store_nbr', 'month'])['tot_sales'].sum().reset_index(name='montly_revenue')
customers = df.groupby(['store_nbr', 'month'])['lylty_card_nbr'].count().reset_index(name='monthly_customers')
transactions = df.groupby(['store_nbr', 'month'])['txn_id'].count().reset_index(name='monthly_txns')

#print(revenue.head(3))
#print(customers.head(3))
#print(transactions.head(3))

store_counts = revenue['store_nbr'].value_counts() # checking how many months that store made sells
#print(store_counts.head(20))

full_months = store_counts[store_counts == 12].index # filtering only stores with revenue during all period

df_filtered = revenue[revenue['store_nbr'].isin(full_months)]



# there are 272 unique stores
#print(f'the are {unique_stores} unique stores.')

# how many unique customers?
# there are 72636 unique customers



