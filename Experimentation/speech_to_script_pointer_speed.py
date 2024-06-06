import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Matplotlib to use LaTeX for text rendering
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "font.size": 18,
    "axes.titlesize": 18,
    "axes.labelsize": 18,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
    "legend.fontsize": 18,
    "figure.titlesize": 18,
    "text.latex.preamble": r"\usepackage{amsmath}"
})

# Data
data = {
    "Fetch buffer": [
        0.01007175446, 0.01220583916, 0.009603261948, 0.01023197174, 0.104829073,
        0.01054692268, 0.009299278259, 0.01579165459, 0.008280992508, 0.1069886684,
        0.009749650955, 0.01116418839, 0.007652997971, 0.008293390274, 0.2391963005,
        0.009230852127, 0.01514196396, 0.00871515274, 0.01170825958, 0.1091651917,
        0.01496076584, 0.009783744812, 0.008356809616, 0.01111102104
    ],
    "ASR": [
        2.695336103, 2.899138212, 3.107230902, 2.792598963, 4.658910275,
        2.780912161, 2.899060011, 5.901638985, 3.212939978, 4.569012165,
        2.402813911, 2.598181248, 2.63525486, 2.628170967, 4.585154057,
        4.089136124, 3.735254049, 3.223296165, 2.823484898, 4.351235867,
        2.956062078, 2.829329729, 2.904309988, 2.915719986
    ],
    "Window search": [
        0.001641988754, 0.001670837402, 0.001358032227, 0.003301143646, 0.001801252365,
        0.001640081406, 0.001871109009, 0.001602172852, 0.02634906769, 0.003570795059,
        0.004283905029, 0.004087924957, 0.003261804581, 0.03476309776, 0.003292322159,
        0.002996921539, 0.003784179688, 0.003394842148, 0.004261732101, 0.003596067429,
        0.003304958344, 0.003793001175, 0.002614021301, 0.003216028214
    ]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Calculate the means and standard deviations
means = df.mean()
stds = df.std()

# Create a bar plot with error bars
plt.figure(figsize=(12, 8))
plt.bar(means.index, means.values, yerr=stds.values, capsize=10, color='skyblue')

plt.xlabel(r'\textbf{Steps}', labelpad=14)
plt.ylabel(r'\textbf{Mean Time (seconds)}', labelpad=14)
# plt.title(r'\textbf{Mean Execution Time with Standard Deviation}')
plt.title("")
plt.grid(True)
plt.tight_layout()
plt.savefig('mean_execution_times_with_std.png')
plt.show()
