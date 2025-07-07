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
df = pd.read_csv('../geneturing_statistics.csv')

# Calculate average score for each task
def create_comparison_plot(model_column, output_filename):
    # Calculate average score for each task
    task_means = df.groupby('TaskName').agg({
        'genegpt-slim': 'mean',  # GeneGPT-slim's score
        model_column: 'mean'  # Score of the model to compare
    }).reset_index()
    
    # Perform significance test
    p_values = []
    for task in task_means['TaskName'].unique():
        task_data = df[df['TaskName'] == task]
        # Perform paired t-test
        t_stat, p_val = stats.ttest_rel(
            task_data['genegpt-slim'],
            task_data[model_column]
        )
        p_values.append(p_val)
    
    task_means['p_value'] = p_values
    
    # Create graph and axis object
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Set position of bar chart
    x = np.arange(len(task_means['TaskName']))
    width = 0.35
    
    # Draw bar chart
    bars1 = ax.bar(x - width/2, task_means['genegpt-slim'], 
                   width, label='GeneGPT-slim', color='lightblue')
    bars2 = ax.bar(x + width/2, task_means[model_column], 
                   width, label=model_column, color='lightgreen')
    
    # Add significance marker
    for i, p in enumerate(p_values):
        if p < 0.001:
            symbol = '***'
        elif p < 0.01:
            symbol = '**'
        elif p < 0.05:
            symbol = '*'
        else:
            symbol = 'ns'
        
        # Get the maximum height of two bars
        height = max(task_means['genegpt-slim'].iloc[i],
                    task_means[model_column].iloc[i])
        
        ax.text(i, height + 0.02, symbol, 
                ha='center', va='bottom')
    
    # Set chart properties
    ax.set_xlabel('Task Type')
    ax.set_ylabel('Average Accuracy')
    ax.set_title(f'GeneGPT-slim vs {model_column} in different tasks')
    ax.set_xticks(x)
    ax.set_xticklabels(task_means['TaskName'], rotation=45, ha='right')
    ax.legend()
    
    # Add significance explanation
    fig.text(0.99, 0.01, 
             'Significance: *** p<0.001, ** p<0.01, * p<0.05, ns: not significant',
             ha='right', va='bottom', fontsize=8)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save image
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()

# Create comparison graph for each model
models = [
    'qwen2.5:32b',
    'qwen2.5:72b',
    'multi-agent(14b+7b)',
    'multi-agent(14b+14b)',
    'multi-agent(32b+14b)', 
    'multi-agent(32b+32b)'
]

for model in models:
    create_comparison_plot(model, f'geneturing_comparison_{model}.png')
    print(f"Comparison graph for {model} generated")