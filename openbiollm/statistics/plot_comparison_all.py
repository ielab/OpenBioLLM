import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

# Set Chinese font, if your system supports it
try:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Used to display Chinese labels
    plt.rcParams['axes.unicode_minus'] = False  # Used to display negative sign
except:
    print("Warning: may not display Chinese correctly, install Chinese font recommended")

# Read data
df = pd.read_csv('./genehop_accuracy_statistics.csv')

# Define all models to compare
models = [
    'genegpt',  # Baseline model
    # 'genegpt-slim',  # Baseline model
    'qwen2.5:32b',
    'qwen2.5:72b',
    'multi-agent(14b+7b)',
    'multi-agent(14b+14b)',
    'multi-agent(32b+14b)', 
    'multi-agent(32b+32b)'
]

# Calculate average score for each task
task_means = df.groupby('TaskName')[models].mean().reset_index()

# Calculate overall average
overall_means = df[models].mean()

# Create graph and axis object
fig, ax = plt.subplots(figsize=(15, 8))

# Set position of bar chart
x = np.arange(len(task_means['TaskName']) + 1)  # +1 to add overall comparison
width = 0.13  # Adjust width to accommodate number of bars
n_models = len(models)

# Color scheme
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e28bc2']

# Draw task comparison bar chart
bars = []
for i, (model, color) in enumerate(zip(models, colors)):
    position = x[:-1] + (i - n_models/2 + 0.5) * width
    bar = ax.bar(position, task_means[model], width, label=model, color=color, alpha=0.8)
    bars.append(bar)

# Draw overall comparison bar chart
for i, (model, color) in enumerate(zip(models, colors)):
    position = x[-1] + (i - n_models/2 + 0.5) * width
    bar = ax.bar(position, overall_means[model], width, color=color, alpha=0.8)
    bars.append(bar)

# Perform significance test and add markers
# baseline_model = 'genegpt-slim'
baseline_model = 'genegpt'
for i, task in enumerate(task_means['TaskName']):
    task_data = df[df['TaskName'] == task]
    max_height = task_means.iloc[i][models].max()
    
    # Perform significance test for each model
    for j, model in enumerate(models[1:], 1):  # Skip baseline model
        t_stat, p_val = stats.ttest_rel(
            task_data[baseline_model],
            task_data[model]
        )
        
        # Determine significance marker
        if p_val < 0.001:
            symbol = '***'
        elif p_val < 0.01:
            symbol = '**'
        elif p_val < 0.05:
            symbol = '*'
        else:
            symbol = 'ns'
        
        # Add significance marker
        position = i + (j - n_models/2 + 0.5) * width
        ax.text(position, max_height + 0.02, symbol, ha='center', va='bottom', fontsize=8)

# Add significance test for overall comparison
max_height = overall_means[models].max()
for j, model in enumerate(models[1:], 1):  # Skip baseline model
    t_stat, p_val = stats.ttest_rel(
        df[baseline_model],
        df[model]
    )
    
    # Determine significance marker
    if p_val < 0.001:
        symbol = '***'
    elif p_val < 0.01:
        symbol = '**'
    elif p_val < 0.05:
        symbol = '*'
    else:
        symbol = 'ns'
    
    # Add significance marker
    position = len(task_means) + (j - n_models/2 + 0.5) * width
    ax.text(position, max_height + 0.02, symbol, ha='center', va='bottom', fontsize=8)

# Set chart properties
ax.set_xlabel('Task Type', fontsize=12)
ax.set_ylabel('Average Accuracy', fontsize=12)
ax.set_title('Performance Comparison Across All Models', fontsize=14, pad=20)
ax.set_xticks(x)
labels = list(task_means['TaskName']) + ['Overall']
ax.set_xticklabels(labels, rotation=45, ha='right')

# Modify legend position and style
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., frameon=True)

# Add grid lines
ax.yaxis.grid(True, linestyle='--', alpha=0.7)

# Set y-axis range, leave space for significance markers
ax.set_ylim(0, 1.1)

# Add significance explanation
fig.text(0.99, 0.02, 
         'Significance vs GeneGPT: *** p<0.001, ** p<0.01, * p<0.05, ns: not significant',
         ha='right', va='bottom', fontsize=8)

# Adjust layout, ensure legend is not truncated
plt.tight_layout()

# Save image, ensure legend is fully displayed
plt.savefig('genehop_all_models_comparison_new.png', dpi=300, bbox_inches='tight')
plt.close()

print("All models comparison graph generated")