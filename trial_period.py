
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


#creating the dataframes
df = pd.read_csv('qvi_data.csv')
df.columns = df.columns.str.lower() # making the column names all lowercase
df['date'] = pd.to_datetime(df['date']) # changing the column datatype
df['month'] = df['date'].dt.to_period('M') # creating a column for month

# --- Creating some metrics to analyse the stores behavior ---
revenue = df.groupby(['store_nbr', 'month'])['tot_sales'].sum().reset_index(name='monthly_revenue')
customers = df.groupby(['store_nbr', 'month'])['lylty_card_nbr'].count().reset_index(name='monthly_customers')
transactions = df.groupby(['store_nbr', 'month'])['txn_id'].count().reset_index(name='monthly_txns')
store_counts = revenue['store_nbr'].value_counts() # checking how many months that store made sells

#print(store_counts.head(20))
full_months = store_counts[store_counts == 12].index # filtering only stores with revenue during all period
df_filtered = revenue[revenue['store_nbr'].isin(full_months)]
monthly_metrics = revenue.merge(customers, on=['store_nbr', 'month']).merge(transactions, on=['store_nbr', 'month'])
'''
    store_nbr    month  montly_revenue  monthly_customers  monthly_txns
0          1  2018-07           206.9                 52            52
1          1  2018-08           176.1                 43            43
2          1  2018-09           278.8                 62            62
3          1  2018-10           188.1                 45            45
4          1  2018-11           192.6                 47            47
'''
monthly_metrics = monthly_metrics[monthly_metrics['store_nbr'].isin(full_months)] # this new merged df will show only the stores that follow the role: sales in all twelve months

#print(monthly_metrics.info())
'''
    <class 'pandas.DataFrame'>
Index: 3120 entries, 0 to 3168
Data columns (total 5 columns):
 #   Column             Non-Null Count  Dtype    
---  ------             --------------  -----    
 0   store_nbr          3120 non-null   int64    
 1   month              3120 non-null   period[M]
 2   montly_revenue     3120 non-null   float64  
 3   monthly_customers  3120 non-null   int64    
 4   monthly_txns       3120 non-null   int64    
dtypes: float64(1), int64(3), period[M](1)
    '''

# The period before the tryal layout is between Jul 2018 and Jan 2019
before_trial = monthly_metrics[monthly_metrics['month'] < '2019-02']
before_trial = before_trial.sort_values(by='month')
'''
How about to use Streamlit to create a website where the user can analise each trial store metrics over each control candidate store metrics?
In that case, the user can choose the trial store, and the grafics will show the metrics before and after the trial period.

'''
before_trial_pivot = before_trial.pivot(index='store_nbr', columns='month', values=['monthly_revenue', 'monthly_customers', 'monthly_txns'])

'''
  monthly_revenue                                                   \
month             2018-07  2018-08 2018-09 2018-10 2018-11 2018-12 2019-01   
store_nbr                                                                    
1                   206.9   176.10   278.8   188.1   192.6   189.6   154.8   
2                   150.8   193.80   154.4   167.8   162.9   136.0   162.8   
3                  1205.7  1079.75  1021.5  1037.9  1008.0  1121.6  1051.7   

          monthly_customers                                                  \
month               2018-07 2018-08 2018-09 2018-10 2018-11 2018-12 2019-01   
store_nbr                                                                     
1                      52.0    43.0    62.0    45.0    47.0    47.0    36.0   
2                      41.0    43.0    37.0    43.0    40.0    38.0    45.0   
3                     138.0   134.0   119.0   119.0   118.0   129.0   121.0   

          monthly_txns                                                  
month          2018-07 2018-08 2018-09 2018-10 2018-11 2018-12 2019-01  
store_nbr                                                               
1                 52.0    43.0    62.0    45.0    47.0    47.0    36.0  
2                 41.0    43.0    37.0    43.0    40.0    38.0    45.0  
3                138.0   134.0   119.0   119.0   118.0   129.0   121.0  
'''

# Correlation tests
trial_stores_nbr = [77, 86, 88] # a list of the trial stores
control_candidates = before_trial[~before_trial['store_nbr'].isin(trial_stores_nbr)] # a new nf with only the stores candidates to be the control
trial_stores = before_trial[before_trial['store_nbr'].isin(trial_stores_nbr)]  # a new df with only the three trial stores

# extracting the Series for two different stores
series_candidate = control_candidates[control_candidates['store_nbr'] == 1]['monthly_revenue']
series_trial = trial_stores[trial_stores['store_nbr'] == 77]['monthly_revenue']

# calculating the correlation (returns a number between -1 and 1)
correlation = series_trial.reset_index(drop=True).corr(series_candidate.reset_index(drop=True), method='pearson')
# calculating the average absolute distance
distance = np.mean(np.abs(series_trial.values - series_candidate.values))

# --- function to returns a list of complete dictionaries containing a store number, correlation, raw distance, scaled distance and composite score ---
'''
def store_search(store, df, metric):
    series_trial = df[df['store_nbr'] == store][metric].reset_index(drop=True)
    results = []
    all_stores = df['store_nbr'].unique()
    for candidate in all_stores:
        if candidate == store:
            continue
        
        series_candidate = df[df['store_nbr'] == candidate][metric].reset_index(drop=True)

        raw_corr = series_trial.corr(series_candidate, method='pearson')

        raw_dist = np.mean(np.abs(series_trial.values - series_candidate.values))

        results.append({
            'store_nbr': candidate,
            'correlation': raw_corr,
            'raw_distance': raw_dist
        })
   
    distances = []
    for item in results:
        distances.append(item['raw_distance'])

    min_dist = min(distances)
    max_dist = max(distances)

    for item in results:
        # calculating the scaled distance
        scaled_dist = 1 - ((item['raw_distance'] - min_dist) / (max_dist - min_dist))

        # adding scaled_distance to the item dictinary
        item['scaled_distance'] = scaled_dist

        # calculating the composite score:
        composite = (item['correlation'] + scaled_dist) / 2

        # adding composite_score to the item dictionary
        item['composite_score'] = composite

    return results


# function to display the prvious result clearly

def get_top_matches(results_list):
    # creating a df from the list of dictionaries
    df_results = pd.DataFrame(results_list)

    # sorting the df by 'composite_score' in descending order, so the highest score/best match is at the very top
    df_sorted = df_results.sort_values(by='composite_score', ascending=False)

    # returning the sorted df
    return df_sorted.head(10)

# metrics to be visualized
metrics = ['monthly_revenue', 'monthly_customers', 'monthly_txns']

# trial loop
for trial in [77, 86, 88]:

    print(f"\n Finding the best Control Store for Trial Store {trial}")

    metric_dfs = []

    for metric in metrics:
        # getting raw list of results for the specific metric

        raw_results = store_search(store=trial, df=before_trial, metric=metric)

        # converting to a DataFrame
        df_metric = pd.DataFrame(raw_results)

        # Keeping only the store_nbr and the composite_score for this metric
        # renaming the composite_score column so we know which metric it belongs to
        df_metric = df_metric[['store_nbr', 'composite_score']].rename(columns={'composite_score': f"score_{metric}"})

        metric_dfs.append(df_metric)

    # Merging the three metric dataframes together on store_nbr
    final_df = metric_dfs[0]
    for df_m in metric_dfs[1:]:
        final_df = pd.merge(final_df, df_m, on='store_nbr')

    # calculating the ultimate score across all metrics
    score_columns = [f'score_{m}' for m in metrics]
    final_df['ultimate_score'] = final_df[score_columns].mean(axis=1)

    # sort and display the top matches
    final_df = final_df.sort_values(by='ultimate_score', ascending=False)
    #print(final_df.head(5))
'''
# ---
'''
Finding the best Control Store for Trial Store 77
     store_nbr  score_monthly_revenue  score_monthly_customers  score_monthly_txns  ultimate_score
175        233               0.951887                 0.982320            0.982320        0.972176
212         41               0.880579                 0.936174            0.936174        0.917642
50          17               0.864397                 0.911242            0.911242        0.895627
14         254               0.754326                 0.925547            0.925547        0.868473
67         115               0.815929                 0.892925            0.892925        0.867260

 Finding the best Control Store for Trial Store 86
     store_nbr  score_monthly_revenue  score_monthly_customers  score_monthly_txns  ultimate_score
92         138               0.859483                 0.916353            0.916353        0.897396
103        155               0.938423                 0.826063            0.826063        0.863517
16         147               0.744843                 0.877096            0.877096        0.833011
200        166               0.744243                 0.866033            0.866033        0.825436
151        247               0.752913                 0.834398            0.834398        0.807236

 Finding the best Control Store for Trial Store 88
     store_nbr  score_monthly_revenue  score_monthly_customers  score_monthly_txns  ultimate_score
10           7               0.731151                 0.883068            0.883068        0.832429
35         123               0.647417                 0.909730            0.909730        0.822292
147        237               0.654240                 0.838279            0.838279        0.776932
124        178               0.728884                 0.787164            0.787164        0.767737
232        203               0.750972                 0.750969            0.750969        0.750970
'''
    
# --- Trial period

trial_period = monthly_metrics[monthly_metrics['month'].between('2019-02', '2019-04')]

trial_period = trial_period.sort_values(by='month')

#print(trial_period.sample(5))
'''
 store_nbr    month  monthly_revenue  monthly_customers  monthly_txns
261          23  2019-02            867.8                127           127
2297        197  2019-04            262.2                 42            42
2550        220  2019-02            202.9                 43            43
1237        108  2019-02            321.4                 41            41
575          50  2019-03            227.0                 45            45
'''

# mapping trial stores to their absolute best multi-metric control matches
control_mapping = {
    77: 233,
    86: 138,
    88: 7
}

trial_results = []

for k, v in control_mapping.items():
    metrics = ['monthly_revenue', 'monthly_customers', 'monthly_txns']

    for metric in metrics:
        # Calculating the scaling factor:
        pre_trial = before_trial[before_trial['store_nbr'] == k][metric].sum()

        pre_control = before_trial[before_trial['store_nbr'] == v][metric].sum()

        scaling_factor = pre_trial / pre_control

        # getting the unique months available in the trial period
        trial_months = trial_period['month'].unique()

        for month in trial_months:
            # isolating the row for the trial store and control store for this specific month
            trial_row = trial_period[(trial_period['store_nbr'] == k) & (trial_period['month'] == month)]
            control_row = trial_period[(trial_period['store_nbr'] == v) & (trial_period['month'] == month)]

            # checking to make sure rows exists for both stores in this month
            if not trial_row.empty and not control_row.empty:
                actual_trial_val = trial_row[metric].values[0]
                actual_control_val = control_row[metric].values[0]

                # applying the scaling factor to the control value
                scaled_control_val = actual_control_val * scaling_factor

                # calculating porcentage uplift
                percentage_diff = ((actual_trial_val - scaled_control_val) / scaled_control_val) * 100

                # saving everything to our results list
                trial_results.append({
                    'trial_store': k,
                    'control_store': v,
                    'metric': metric,
                    'month': month,
                    'trial_actual': actual_trial_val,
                    'control_scaled': scaled_control_val,
                    'uplift_pct': percentage_diff
                })

df_uplift = pd.DataFrame(trial_results)

print(f"\n{'==' * 18}Trial period uplift analysis{'==' * 18}")

#print(df_uplift.to_string())
'''
====================================Trial period uplift analysis====================================
    trial_store  control_store             metric    month  trial_actual  control_scaled  uplift_pct
0            77            233    monthly_revenue  2019-02         235.0      249.762622   -5.910661
1            77            233    monthly_revenue  2019-03         278.5      203.802205   36.652103
2            77            233    monthly_revenue  2019-04         263.5      162.345704   62.307960
3            77            233  monthly_customers  2019-02          45.0       47.906752   -6.067521
4            77            233  monthly_customers  2019-03          55.0       41.790997   31.607294
5            77            233  monthly_customers  2019-04          48.0       33.636656   42.701463
6            77            233       monthly_txns  2019-02          45.0       47.906752   -6.067521
7            77            233       monthly_txns  2019-03          55.0       41.790997   31.607294
8            77            233       monthly_txns  2019-04          48.0       33.636656   42.701463
9            86            138    monthly_revenue  2019-02         913.2      724.548428   26.037124
10           86            138    monthly_revenue  2019-03        1026.8      910.379711   12.788102
11           86            138    monthly_revenue  2019-04         848.2      807.398208    5.053491
12           86            138  monthly_customers  2019-02         139.0      107.960656   28.750607
13           86            138  monthly_customers  2019-03         142.0      133.022951    6.748497
14           86            138  monthly_customers  2019-04         127.0      123.383607    2.931016
15           86            138       monthly_txns  2019-02         139.0      107.960656   28.750607
16           86            138       monthly_txns  2019-03         142.0      133.022951    6.748497
17           86            138       monthly_txns  2019-04         127.0      123.383607    2.931016
18           88              7    monthly_revenue  2019-02        1370.2     1316.924460    4.045451
19           88              7    monthly_revenue  2019-03        1477.2     1470.120856    0.481535
20           88              7    monthly_revenue  2019-04        1439.4     1209.148101   19.042489
21           88              7  monthly_customers  2019-02         154.0      152.058072    1.277096
22           88              7  monthly_customers  2019-03         170.0      174.678281   -2.678227
23           88              7  monthly_customers  2019-04         162.0      136.977933   18.267225
24           88              7       monthly_txns  2019-02         154.0      152.058072    1.277096
25           88              7       monthly_txns  2019-03         170.0      174.678281   -2.678227
26           88              7       monthly_txns  2019-04         162.0      136.977933   18.267225
'''



