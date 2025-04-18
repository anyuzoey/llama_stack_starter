import os
import pandas as pd
import numpy as np

def process_experiment_logs(logs_dir="experiment_logs"):
    """
    Process experiment log files and extract the second last line from each file.
    
    Args:
        logs_dir (str): Directory containing the experiment log files
        
    Returns:
        pd.DataFrame: DataFrame containing aggregated results
    """
    # Initialize list to store results
    results = []
    
    # Ensure directory exists
    if not os.path.exists(logs_dir):
        print(f"Directory {logs_dir} does not exist!")
        return None
    
    # Process each CSV file
    for filename in os.listdir(logs_dir):
        if filename.startswith("results_") and filename.endswith(".csv"):
            file_path = os.path.join(logs_dir, filename)
            try:
                # Read the file using a more robust method
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if len(lines) >= 2:  # Need at least 2 lines
                    # Get the second last line and parse it
                    second_last_line = lines[-2].strip()
                    # Convert the line to a dictionary
                    values = second_last_line.split(',')
                    
                    # Read header from first line
                    headers = lines[0].strip().split(',')
                    
                    # Create a dictionary with header-value pairs
                    row_dict = {
                        header: value for header, value in zip(headers, values)
                    }
                    
                    # Add metadata
                    row_dict['Experiment_Name'] = filename
                    row_dict['Timestamp'] = filename.split('_')[-1].replace('.csv', '')
                    
                    results.append(row_dict)
                    print(f"Successfully processed {filename}")
                else:
                    print(f"Skipping {filename} - insufficient lines")
                    
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
    
    if not results:
        print("No valid results found!")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Save aggregated results
    output_path = os.path.join(logs_dir, "aggregated_results.csv")
    df.to_csv(output_path, index=False)
    print(f"\nResults saved to {output_path}")
    
    return df

if __name__ == "__main__":
    # Process the logs
    results_df = process_experiment_logs()
    
    if results_df is not None:
        print("\nSummary of processed results:")
        print(f"Total experiments processed: {len(results_df)}")
        print("\nColumns found:")
        for col in results_df.columns:
            print(f"- {col}") 