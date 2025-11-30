# %%
import pandas as pd
import numpy as np

from ydata_profiling import ProfileReport

# %%
df = pd.read_excel("../../Data/processed/firearm_data_cleaned.xlsx")

# %%
profile = ProfileReport(df, title="Firearm Data Profiling Report", explorative=True, )
profile.config.html.minify_html = True
profile.to_file("firearm_data_profiling_report.html")
