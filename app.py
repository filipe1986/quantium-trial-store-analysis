import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Quantium Trial Store Analysis", layout="wide")
st.title("📊 Quantium Trial Store Performance Dashboard")
st.markdown("Interactive charts for trial stores 77, 86, and 88 vs. their control stores.")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("qvi_data.csv")
    df.columns = df.columns.str.lower()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    
    revenue = df.groupby(['store_nbr', 'month'])['tot_sales'].sum().reset_index(name='monthly_revenue')
    customers = df.groupby(['store_nbr', 'month'])['lylty_card_nbr'].count().reset_index(name='monthly_customers')
    transactions = df.groupby(['store_nbr', 'month'])['txn_id'].count().reset_index(name='monthly_txns')
    
    monthly_metrics = revenue.merge(customers, on=['store_nbr', 'month']).merge(transactions, on=['store_nbr', 'month'])
    return monthly_metrics

data = load_data()

# Controls
trial_stores = [77, 86, 88]
metrics = {
    'Revenue': 'monthly_revenue',
    'Customers': 'monthly_customers',
    'Transactions': 'monthly_txns'
}

col1, col2 = st.columns(2)
with col1:
    selected_trial = st.selectbox("Select Trial Store", trial_stores)
with col2:
    selected_metric_label = st.selectbox("Select Metric", list(metrics.keys()))
    selected_metric = metrics[selected_metric_label]

# Control mapping
control_mapping = {77: 233, 86: 138, 88: 7}
control_store = control_mapping[selected_trial]

# Filter data
trial_data = data[data['store_nbr'] == selected_trial].copy()
control_data = data[data['store_nbr'] == control_store].copy()

# Calculate scaling factor (pre-trial)
before_trial = data[data['month'] < '2019-02']
pre_trial_sum = before_trial[before_trial['store_nbr'] == selected_trial][selected_metric].sum()
pre_control_sum = before_trial[before_trial['store_nbr'] == control_store][selected_metric].sum()
scaling_factor = pre_trial_sum / pre_control_sum if pre_control_sum != 0 else 1

control_data['scaled_' + selected_metric] = control_data[selected_metric] * scaling_factor

# Merge for plotting
plot_df = trial_data.merge(
    control_data[['month', 'scaled_' + selected_metric]], 
    on='month', 
    suffixes=('_trial', '_control')
)

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=plot_df, x='month', y=selected_metric, label=f'Trial Store {selected_trial}', marker='o', ax=ax)
sns.lineplot(data=plot_df, x='month', y='scaled_' + selected_metric, label=f'Scaled Control Store {control_store}', marker='s', ax=ax)

ax.axvline(pd.Period('2019-02'), color='red', linestyle='--', label='Trial Period Start')
ax.set_title(f"{selected_metric_label} - Trial Store {selected_trial} vs Control {control_store}")
ax.set_ylabel(selected_metric_label)
ax.set_xlabel("Month")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

# Show uplift table
st.subheader("Uplift During Trial Period")
trial_period = plot_df[plot_df['month'] >= '2019-02']
trial_period['uplift_pct'] = ((trial_period[selected_metric] - trial_period['scaled_' + selected_metric]) / 
                              trial_period['scaled_' + selected_metric]) * 100
st.dataframe(trial_period[['month', selected_metric, 'scaled_' + selected_metric, 'uplift_pct']].round(2))

st.caption("Built by Philip Vieira")

