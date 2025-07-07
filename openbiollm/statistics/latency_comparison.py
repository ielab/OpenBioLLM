import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np
import textwrap

# Set Chinese font, if your system supports it
try:
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("Warning: may not display Chinese correctly, install Chinese font recommended")

# Set global font size
plt.rcParams['font.size'] = 14  # Base font size
plt.rcParams['axes.titlesize'] = 18  # Title font size
plt.rcParams['axes.labelsize'] = 16  # Axis label font size
plt.rcParams['xtick.labelsize'] = 14  # x-axis tick label font size
plt.rcParams['ytick.labelsize'] = 14  # y-axis tick label font size
plt.rcParams['legend.fontsize'] = 16  # Legend font size

# Read data - use tab separator
df = pd.read_csv('./geneturing_latency_statistics.csv', sep='\t')

def create_latency_plot():
    # Calculate average time for each task
    task_means = df.groupby('Task').agg({
        'qwen2.5:32b': 'mean',
        'multi-agent(32b+32b)': 'mean'
    }).reset_index()
    
    # Calculate overall average
    overall_means = {
        'qwen2.5:32b': df['qwen2.5:32b'].mean(),
        'multi-agent(32b+32b)': df['multi-agent(32b+32b)'].mean()
    }
    
    # Create graph and axis object - increase graph size to accommodate larger font
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Set position of bar chart
    x = np.arange(len(task_means['Task']) + 1)  # +1 to add overall comparison
    width = 0.35
    
    # Draw task comparison bar chart
    bars1 = ax.bar(x[:-1] - width/2, task_means['qwen2.5:32b'], 
                   width, label='Qwen2.5:32b', color='#2ecc71')
    bars2 = ax.bar(x[:-1] + width/2, task_means['multi-agent(32b+32b)'], 
                   width, label='multi-agent(32b+32b)', color='#3498db')
    
    # Draw overall comparison bar chart
    bars3 = ax.bar(x[-1] - width/2, overall_means['qwen2.5:32b'],
                   width, color='#2ecc71')
    bars4 = ax.bar(x[-1] + width/2, overall_means['multi-agent(32b+32b)'],
                   width, color='#3498db')
    
    # Perform statistical test
    for i, task in enumerate(task_means['Task']):
        task_data = df[df['Task'] == task]
        t_stat, p_val = stats.ttest_rel(
            task_data['qwen2.5:32b'],
            task_data['multi-agent(32b+32b)']
        )
        
        if p_val < 0.001:
            symbol = '***'
        elif p_val < 0.01:
            symbol = '**'
        elif p_val < 0.05:
            symbol = '*'
        else:
            symbol = 'ns'
            
        height = max(task_means['qwen2.5:32b'].iloc[i],
                    task_means['multi-agent(32b+32b)'].iloc[i])
        
        # Adjust significance marker position to be within chart
        ax.text(i, height + 1.2, symbol, 
                ha='center', va='bottom', fontsize=16, fontweight='bold')
    
    # Add significance test for overall comparison
    t_stat, p_val = stats.ttest_rel(
        df['qwen2.5:32b'],
        df['multi-agent(32b+32b)']
    )
    
    if p_val < 0.001:
        symbol = '***'
    elif p_val < 0.01:
        symbol = '**'
    elif p_val < 0.05:
        symbol = '*'
    else:
        symbol = 'ns'
        
    height = max(overall_means['qwen2.5:32b'],
                overall_means['multi-agent(32b+32b)'])
    
    # Adjust position of significance marker for overall comparison
    ax.text(len(task_means['Task']), height + 1.2, symbol,
            ha='center', va='bottom', fontsize=16, fontweight='bold')
    
    # Set chart properties
    # ax.set_xlabel('Task Type', labelpad=15, fontsize=16)
    ax.set_ylabel('Average Response Time (seconds)', fontsize=16)
    ax.set_title('Response Time Comparison: Qwen2.5:32b vs multi-agent(32b+32b)', fontsize=18, fontweight='bold')
    
    # Process x-axis label wrapping - do not split words
    def wrap_labels(text, width=10):
        return textwrap.fill(text, width=width, break_long_words=False)
    
    ax.set_xticks(x)
    labels = [wrap_labels(label) for label in task_means['Task']] + ['Overall']
    ax.set_xticklabels(labels, ha='center', fontsize=14)
    
    # Add grid lines
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend - placed inside the chart's upper right corner
    ax.legend(loc='upper right', fontsize=14)
    
    # Add specific value labels for each bar
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., height,
                    f'{height:.1f}s',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    autolabel(bars1)
    autolabel(bars2)
    autolabel(bars3)
    autolabel(bars4)
    
    # Add significance explanation
    fig.text(1.0, 0, 
             '*** p<0.001, ** p<0.01, * p<0.05, ns: not significant',
             ha='right', va='bottom', fontsize=14)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save image
    plt.savefig('geneturing_latency_comparison_new.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Output statistical information
    print("\nAverage response time statistics:")
    print(task_means.to_string(index=False))
    
    # Calculate overall average time
    print("\nOverall average response time:")
    print(f"Qwen2.5:32b: {overall_means['qwen2.5:32b']:.2f}秒")
    print(f"multi-agent(32b+32b): {overall_means['multi-agent(32b+32b)']:.2f}秒")

# Execute plotting
create_latency_plot()