import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

folder_path = "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/"
output_path = "C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/0report/descriptive_statistics_summary.csv"

# folder_path = "/Users/sunny/Library/CloudStorage/Box-Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/"
# output_path = "/Users/sunny/Library/CloudStorage/Box-Box/AI Hackathon/AI_Hackathon/cleaned_data/multiple_records/0report/descriptive_statistics_summary.csv"

# List of file names
file_names = [
    "Somatic Cells Count (SCC).csv", "Time to curd firmness (A30).csv", 
    "Fat.csv", "Protein.csv", "Casein.csv", "Lactose.csv", 
    "Time to curd firmness (K20).csv", "Rennet Coagulation time (R).csv"
]

def descriptive_stats(df):
    print("original length", len(df))
    # Remove negative values
    df = df[df['valoreMisura'] > 0]
    
    mean = df['valoreMisura'].mean()
    std = df['valoreMisura'].std()
    
    # Eliminate outliers based on 3 standard deviations
    eliminate_outlier = df[(0 < df['valoreMisura']) & 
                           (mean - 3 * std < df['valoreMisura']) & 
                           (df['valoreMisura'] < mean + 3 * std)]
    
    print("eliminate_outlier length", len(eliminate_outlier))
    print(f"The proportion for the outlier: {(len(df) - len(eliminate_outlier)) / len(df) * 100:.1f}%")
    
    mean_rpt = round(eliminate_outlier['valoreMisura'].mean(), 2)
    std_rpt = round(eliminate_outlier['valoreMisura'].std(), 2)
    cv_rpt = round((std_rpt / mean_rpt) * 100, 2)  # CV in percentage
    min_rpt = round(eliminate_outlier['valoreMisura'].min(), 2)
    max_rpt = round(eliminate_outlier['valoreMisura'].max(), 2)
    
    return len(eliminate_outlier), mean_rpt, std_rpt, cv_rpt, min_rpt, max_rpt

# Prepare a list to collect results
results = []

for file_name in file_names:
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path)
    
    # Ensure the column 'valoreMisura' exists
    if 'valoreMisura' in df.columns:
        n, mean_rpt, std_rpt, cv_rpt, min_rpt, max_rpt = descriptive_stats(df)
        results.append({
            "Trait": file_name.split(".csv")[0],
            "N": n,
            "Mean": mean_rpt,
            "s.d.": std_rpt,
            "CV (%)": cv_rpt,
            "Minimum": min_rpt,
            "Maximum": max_rpt
        })
    else:
        print(f"Column 'valoreMisura' not found in {file_name}")

# Create a DataFrame to display results
summary_df = pd.DataFrame(results)

print(summary_df)

# Save the summary to the specified output path
summary_df.to_csv(output_path, index=False)

print(f"Summary saved to {output_path}")

#############################################
carcass = pd.read_csv('C:/Users/holic/Box/AI Hackathon/AI_Hackathon/cleaned_data/single_record/Slaughter.csv')
# carcass = pd.read_csv('/Users/sunny/Library/CloudStorage/Box-Box/AI Hackathon/AI_Hackathon/cleaned_data/single_record/Slaughter.csv')

print(carcass['PesoCarcassa'].describe())

carcass = carcass[carcass['PesoCarcassa'] >= 10]

# plt.hist(carcass['PesoCarcassa'], bins=20, edgecolor='black')
# plt.title('Distribution of PesoCarcassa')
# plt.xlabel('PesoCarcassa')
# plt.ylabel('Frequency')
# plt.show()

# mean = carcass['PesoCarcassa'].mean()
# std = carcass['PesoCarcassa'].std()
# filtered_data = carcass[(carcass['PesoCarcassa'] > mean - 3 * std) & (carcass['PesoCarcassa'] < mean + 3 * std)]
# sns.histplot(filtered_data['PesoCarcassa'], kde=True, bins=20, edgecolor='black')
# plt.title('Distribution of PesoCarcassa after removing outliers (3 sd)')
# plt.xlabel('PesoCarcassa')
# plt.ylabel('Density')
# plt.show()


outlier_row = carcass[carcass['PesoCarcassa'] == 30]
print(outlier_row)

# Columns to analyze
columns_to_analyze = ['PesoCarcassa', 'PesoVivo']

# Prepare rows for new data
new_rows = []

for col in columns_to_analyze:
    if col in carcass.columns:
        print(f"\nAnalyzing column: {col}")
        
        # Drop missing values
        df_cleaned = carcass[col].dropna()
        
        # Calculate mean and std
        mean = df_cleaned.mean()
        std = df_cleaned.std()
        
        # Eliminate outliers based on 3 standard deviations
        eliminate_outlier = df_cleaned[(mean - 3 * std < df_cleaned) & (df_cleaned < mean + 3 * std)]
        
        # Calculate descriptive statistics
        mean_rpt = round(eliminate_outlier.mean(), 2)
        std_rpt = round(eliminate_outlier.std(), 2)
        cv_rpt = round((std_rpt / mean_rpt) * 100, 2)  # CV in percentage
        min_rpt = round(eliminate_outlier.min(), 2)
        max_rpt = round(eliminate_outlier.max(), 2)
        
        # Create a dictionary for the new row
        new_rows.append({
            "Trait": col,
            "N": len(eliminate_outlier),
            "Mean": mean_rpt,
            "s.d.": std_rpt,
            "CV (%)": cv_rpt,
            "Minimum": min_rpt,
            "Maximum": max_rpt
        })

# Convert new rows to DataFrame
new_rows_df = pd.DataFrame(new_rows)

# Concatenate new rows on top of summary_df
updated_summary_df = pd.concat([new_rows_df, summary_df], ignore_index=True)

# Save the updated summary
updated_summary_df.to_csv(output_path, index=False)
print(f"Updated summary saved to {output_path}")

# Display the updated DataFrame
print(updated_summary_df)

#############################################