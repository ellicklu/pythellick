import pandas as pd
import numpy as np
import seaborn as sns
import warnings
import matplotlib.pyplot as plt



csv_data = pd.read_csv("D:\\Projects\\CPX_Stats.csv", usecols=[0,1])
csv_data["Date"] = pd.to_datetime(csv_data["Date"])
csv_data = csv_data.set_index("Date")
success_data = csv_data[csv_data['Scheduler'] != 'na'].resample('1Min').count().rename(columns={'Scheduler':'Succeeds'})
fail_data = csv_data[csv_data['Scheduler'] == 'na'].resample('1Min').count().rename(columns={'Scheduler':'Fails'})
result_data = success_data.join(fail_data, on='Date', how='inner')
print(result_data)

f, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10), sharex=True)
sns.set(style="white", context="talk")
warnings.filterwarnings('ignore')
sns.barplot(x=result_data.index.tolist(), y=result_data['Succeeds'], palette="rocket", ax=ax1)
ax1.axhline(0, color="g", clip_on=False)
ax1.set_ylabel("Succeeds")
sns.barplot(x=result_data.index.tolist(), y=result_data['Fails'], palette="rocket", ax=ax2)
ax2.axhline(0, color="r", clip_on=False)
ax2.set_ylabel("Fails")
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=-60)
# Finalize the plot
sns.despine(bottom=True)
plt.setp(f.axes, yticks=[])
plt.tight_layout(h_pad=2)
#plt.show()
plt.savefig('d:\\projects\hr\\stat.png', dpi=100, bbox_inches='tight')
