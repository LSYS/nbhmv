# ---
# jupyter:
#   jupytext:
#     formats: ipynb,logs//py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python (venv_nbhmv)
#     language: python
#     name: venv_nbhmv
# ---

# %%
import pandas as pd
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sns.set_theme(context="notebook", font_scale=1.1, style="white", palette="deep")
from tqdm.notebook import tqdm
from utilities import save_mpl_fig

# %%
df = pd.read_csv("./out/pa-price.csv")
df.head(3)

# %%
NBOOTSTRAP = 10_000

r2_array = []

for i in tqdm(range(NBOOTSTRAP)):
    _df = (
        df.query("wpsm==wpsm")
        .query("income==income")
        .sample(frac=1, replace=True, random_state=i)
    )

    rho, pval = stats.pearsonr(_df.income, _df.wpsm)

    r2_array.append(rho**2)

# %%
alpha = 95

ordered = sorted(r2_array)
lower = np.percentile(ordered, (100 - alpha) / 2)
upper = np.percentile(ordered, alpha + (100 - alpha) / 2)

lower, upper

# %%
# Plot
fig, ax = plt.subplots()

sns.histplot(x=r2_array, ax=ax, stat="density", alpha=0.5)
sns.kdeplot(x=r2_array, ax=ax)

Y_LOW_LIM, Y_UPP_LIM = ax.get_ylim()

ax.set_xlim(left=0.3)

NEG_VERT_BUFFER = -0.7  # Buffer to get text closer to tip of vert lines
TEXT_SIZE = 13

# Plot vert ref line for lower CI bound
plt.axvline(
    x=lower, ymin=Y_LOW_LIM, ymax=Y_UPP_LIM, color="dimgray", linestyle="dashdot"
)

# Add text for lower CI bound
plt.text(
    x=lower + 0.01,
    y=Y_UPP_LIM + NEG_VERT_BUFFER * 1.7,
    s=f"lower CI\n bound\n = {lower:.2g}",
    horizontalalignment="left",
    fontweight="bold",
    size=TEXT_SIZE,
)

# Plot vert ref line for upper CI bound
plt.axvline(
    x=upper, ymin=Y_LOW_LIM, ymax=Y_UPP_LIM, color="dimgray", linestyle="dashdot"
)

# Add text for upper CI bound
plt.text(
    x=upper + 0.01,
    y=Y_UPP_LIM + NEG_VERT_BUFFER * 1.7,
    s=f"upper CI\n bound\n = {upper:.2g}",
    horizontalalignment="left",
    fontweight="bold",
    size=TEXT_SIZE,
)

# Plot vert ref line for original R-square
plt.axvline(x=0.79, ymin=Y_LOW_LIM, ymax=Y_UPP_LIM, color="r", linewidth=2.5)

# Add text for original sample estimate
plt.text(
    x=0.79 - 0.01,
    y=Y_UPP_LIM + NEG_VERT_BUFFER,
    s="[$\hat{R}^2$ = 0.79]",
    horizontalalignment="right",
    fontweight="bold",
    size=TEXT_SIZE,
)

sns.despine(left=True, bottom=True)


plt.xlabel("Bootstrapped $\hat{R}^2$", fontsize=15)
plt.yticks([])
plt.tight_layout()
plt.margins(0, 0)
save_mpl_fig("../results/figures/supplementary/bootstrap-r2")

# %%
