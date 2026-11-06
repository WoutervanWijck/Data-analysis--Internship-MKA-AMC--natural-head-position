import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


path = r"Add your path to the main csv file from the roll angle macro"

df = pd.read_csv(path, sep=",", skip_blank_lines=True, quoting=3)

# %% Difference in roll angles between sessions per condition from session 1 #######
df_pat = pd.read_csv(path, sep=",", skip_blank_lines=True, quoting=3)
df_pat['Patient'] = df_pat['Bestandsnaam'].str.extract(r'_(P\d+)_')
df_relevant = df_pat[['Patient', 'Sessie', 'Conditie', 'RollAngle']].copy()

df_cond = df_relevant[
    (df_relevant['Sessie'] == 'session 1') &
    (df_relevant['Patient'] != 'P4')        #excluding p4 as one picture was not assessable
].copy()

#print(df_cond.groupby('Conditie').size())

# %% Making the difference plot
# Making the dataframes with the differences per condition
df_diff = df_cond.pivot(columns='Conditie', index='Patient', values='RollAngle').reset_index()
# Extending the dataset with the differences
df_diff['Closed - Open'] = df_diff['closed'].abs() - df_diff['open'].abs()
df_diff['Closed - Mirror'] = df_diff['closed'].abs() - df_diff['mirror'].abs()
df_diff['Open - Mirror'] = df_diff['open'].abs() - df_diff['mirror'].abs()

#print (df_diff.head())


# %%
## Plotting Bland-Altman plots 
# Extracting all relevant data on patient level
df['Patient'] = df['Bestandsnaam'].str.extract(r'_(P\d+)_')
df_patient = df[['Patient', 'Sessie', 'Conditie', 'RollAngle']].copy()

# Selecting patients who have attended both sessions
patients_2sessions = df_patient.groupby('Patient')['Sessie'].nunique() # all unique sessions per patient
patients_2sessions = patients_2sessions[patients_2sessions == 2].index # include only patients with session 2
df_ses = df_patient[df_patient['Patient'].isin(patients_2sessions)].copy()

#Shifting the data to wide format for easier plotting
df_wide = df_ses.pivot(index=['Patient', 'Conditie'], columns='Sessie', values='RollAngle').reset_index()

# Preparing data for the scatterplot
df_mirror = df_wide[df_wide['Conditie'] == 'mirror'].copy()
df_closed = df_wide[df_wide['Conditie'] == 'closed'].copy()
df_open = df_wide[df_wide['Conditie'] == 'open'].copy()

#print(df_mirror.head())

# Making variables to loop easier through the conditions and dataframes
condities = ['eyes closed','eyes open', 'mirror feedback']
dataframes = [df_closed, df_open, df_mirror]

## Creating the data for the bland altman plot
for df_ba_cond in dataframes:
    df_ba_cond['Mean'] = (
        df_ba_cond['session 1'] + df_ba_cond['session 2']
    ) / 2

    df_ba_cond['Difference'] = (
        df_ba_cond['session 2'] - df_ba_cond['session 1']
    )


# %%Intra observer variability
path_intra = r"Add your path to the second time  using the roll angle macro"

df_intra = pd.read_csv(path_intra, sep=",", skip_blank_lines=True, quoting=3)

df_intra['Patient'] = df_intra['Bestandsnaam'].str.extract(r'_(P\d+)_')
df_intra_patient = df_intra[['Patient', 'Sessie', 'Conditie', 'RollAngle']].copy()

df_original = df_patient[(df_patient['Sessie'] == 'session 1')
                         &
                         (df_patient['Patient'] != 'P4')].copy()

# Creating one new dataframe with the original and intra observer measurements
df_intra_wide = pd.merge(
    df_original[['Patient', 'Conditie', 'RollAngle']],
    df_intra_patient[['Patient', 'Conditie', 'RollAngle']],
    on=['Patient', 'Conditie'],
    suffixes=('_original', '_repeat'),
    validate='one_to_one'
)


# Calculating the differences and visualizing the results
df_intra_wide['Difference'] = (df_intra_wide['RollAngle_repeat'] - df_intra_wide['RollAngle_original'])
df_intra_wide['Absolute Difference'] = df_intra_wide['Difference'].abs()

#mean (absolute) difference
mean_diff = df_intra_wide['Difference'].mean()
sd_diff = df_intra_wide['Difference'].std()
mean_abs_diff = df_intra_wide['Absolute Difference'].mean()
max_abs_diff = df_intra_wide['Absolute Difference'].max()

results_intra = pd.DataFrame({
    'Statistic': [
        'Number of measurements',
        'Mean difference (°)',
        'SD of differences (°)',
        'Mean Absolute Difference (°)',
        'Maximum absolute difference (°)'
    ],
    'Value': [
        len(df_intra_wide),
        mean_diff,
        sd_diff,
        mean_abs_diff,
        max_abs_diff
    ]
})

# Afronden op 3 decimalen
results_intra['Value'] = results_intra['Value'].round(2)

## Making the comparison between conditions for the intra observer variability
results_intra_cond = df_intra_wide.groupby('Conditie').agg(
    N=('Difference', 'count'),
    Mean_Difference=('Difference', 'mean'),
    SD_Difference=('Difference', 'std'),
    Mean_Absolute_Difference=('Absolute Difference', 'mean'),
    Max_Absolute_Difference=('Absolute Difference', 'max')
)


# %% Calibration plate
path_bord = r"Add your path to the roll angle macro from the calibration plate"
bord = pd.read_csv(path_bord, sep=",", skip_blank_lines=True, quoting=3)
df_bord = bord[['Opmerking', 'RollAngle']].copy()
#print(df_bord.head())

df_bord['RollAngle'] = df_bord['RollAngle'] - df_bord.iloc[0, 1]  # Subtract the first measurement, theta_zero, from all measurements
df_bord['Opmerking'] = df_bord['Opmerking'].str.replace('"', '', regex=False).astype(int)
#print(df_bord.head())

df_bord['Error'] = df_bord['RollAngle'] - df_bord['Opmerking']
df_bord['AbsError'] = df_bord['Error'].abs()

error_mean = df_bord['Error'].mean()
error_abs_mean = df_bord['AbsError'].mean()

print("Calibration plate results:")
#print(f"Mean error: {error_mean:.2f} degrees")
print(f"Mean absolute error: {error_abs_mean:.2f} degrees")


patienten = sorted(df_patient['Patient'].unique(),
                   key=lambda x: int(x[1:]))

kleuren = plt.get_cmap('tab20', len(patienten))

patient_kleuren = {
    patient: kleuren(i)
    for i, patient in enumerate(patienten)
}

#plot for the results: 
plt.figure(figsize=(6, 6))

plt.scatter(df_bord['Opmerking'], df_bord['RollAngle'])

plt.plot(
    [-5, 5], [-5, 5],
    'k--',
    label='Complete agreement'
)

plt.xlabel('Reference angle (°)')
plt.ylabel('Measured angle (°)')
plt.xlim(-5.5, 5.5)
plt.ylim(-5.5, 5.5)
plt.xticks(np.arange(-5, 6, 1))
plt.yticks(np.arange(-5, 6, 1))
plt.axis('equal')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()


print("Intra-observer variability overal results:")
print(results_intra)
print("\nIntra-observer variability by condition:")
print(results_intra_cond.round(2))
# %% PLOTTING BLAND-ALTMAN
fig, axes = plt.subplots(
    1, 3, figsize=(15, 5),
    sharex=True, sharey=True)

for i, conditie in enumerate(condities):

    data = dataframes[i]

    # Calculate Bland-Altman statistics
    bias = data['Difference'].mean()
    sd = data['Difference'].std()

    upper_loa = bias + 1.96 * sd
    lower_loa = bias - 1.96 * sd

    # Scatterplot
    for _, row in data.iterrows():
        axes[i].scatter(
        row['Mean'],
        row['Difference'],
        color=patient_kleuren[row['Patient']],
        s=80,
        alpha=0.85,
        edgecolors='black',
        linewidth=0.7
    )

    # Bias
    axes[i].axhline(
        bias,
        color='blue',
        linestyle='-',
        linewidth=1.5,
        label='Mean difference (bias)'
    )

    # Upper limit of agreement
    axes[i].axhline(
        upper_loa,
        color='red',
        linestyle='--',
        linewidth=1.5,
        label='95% Limits of Agreement'
    )

    # Lower limit of agreement
    axes[i].axhline(
        lower_loa,
        color='red',
        linestyle='--',
        linewidth=1.5
    )

    # Zero reference line
    axes[i].axhline(
        0,
        color='black',
        linewidth=0.8,
        alpha=0.5
    )

    # Formatting
    axes[i].set_title(conditie.capitalize(), fontsize=15)
    axes[i].set_xlabel('Mean roll angle across both sessions (°)', fontsize=15)
    axes[i].set_ylabel('Session 2 - Session 1 (°)', fontsize=15)

    axes[i].grid(True, linestyle=':', alpha=1)

axes[0].legend(loc='best', fontsize=13)

plt.rcParams.update({'font.size': 15})
plt.tight_layout()
plt.show()

# %% Difference in roll angles between sessions per condition from session 1 #######
condities_csv = ['closed', 'open', 'mirror'] #as these are the conditions in the csv file
fig, ax = plt.subplots(figsize=(9, 7))

# Plot each patient separately
for patient, data in df_cond.groupby('Patient'):

    # Sort measurements by condition
    data = data.set_index('Conditie').reindex(condities_csv)

    # Plot connected points
    ax.plot(
        condities,
        data['RollAngle'],
        marker='o',
        markersize=7,
        linewidth=1.5,
        alpha=0.7,
        color=patient_kleuren[patient]
    )

# Horizontal reference line
ax.axhline(0, color='black', linestyle='--', linewidth=1)

# Formatting
ax.set_xlabel('Condition',labelpad=15)
ax.set_xticklabels(['Eyes closed', 'Eyes open', 'Mirror feedback'])
ax.set_ylabel('Roll angle (°)')
ax.grid(axis='y', linestyle=':', alpha=0.5)
plt.tight_layout()
plt.show()

# Plotting differences between conditions
fig, ax = plt.subplots(figsize=(9, 7))

vergelijkingen = ['Closed - Open', 'Closed - Mirror', 'Open - Mirror']

for i, vergelijking in enumerate(vergelijkingen):
    
    # Individual patients
    for _, row in df_diff.iterrows():
        ax.scatter(
            i,
            row[vergelijking],
            color=patient_kleuren[row['Patient']],
            s=70,
            alpha=0.85,
            edgecolors='black',
            linewidth=0.7
        )


# Reference 0 line
ax.axhline(0, color='black', linestyle='--', alpha=0.6)

ax.set_xticks(range(len(vergelijkingen)))

labels = [
    rf'$\bf{{{v.replace(" ", r"\ ")}}}$' + '\n' +
    f'MAD = {(
        df_diff[v.split(" - ")[0].lower()] -
        df_diff[v.split(" - ")[1].lower()]
    ).abs().mean():.2f}°'
    for v in vergelijkingen
]
ax.set_xticklabels(labels, fontsize=10)

ax.set_ylabel('Difference in absolute roll angle (°)')
ax.set_title('Differences in absolute roll angle between conditions')

ax.grid(axis='y', linestyle=':', alpha=0.4)

plt.tight_layout()
plt.show()


