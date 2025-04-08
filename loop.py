import pandas as pd
import os # Used for joining path components safely

def generate_prompts_from_excel(excel_filepath: str, output_prompt_file: str, 
                                sheet_index: int = 1, 
                                prompt_columns: list = ['C', 'D', 'E'], 
                                max_rows: int = 100) -> pd.DataFrame:
    """
    Reads data from a specific sheet and columns of an Excel file, generates LLM prompts,
    prints them, saves them to a file, and prepares for response collection.

    Args:
        excel_filepath (str): The full path to the input Excel (.xlsx) file.
        output_prompt_file (str): The full path for the output text file to save prompts.
        sheet_index (int): The index of the sheet to read (default is 1 for the second sheet).
                           Pandas uses 0-based indexing for sheets.
        prompt_columns (list): A list of column names to use in the prompt generation.
        max_rows (int): The maximum number of rows to read from the Excel sheet.

    Returns:
        pd.DataFrame: The original DataFrame augmented with 'GeneratedPrompt' 
                      and placeholder 'LLM_Response' columns. Returns None if 
                      file reading fails.
    """
    print(f"--- Starting prompt generation from {excel_filepath} ---")

    # --- 1) Read the data ---
    try:
        # Read the specified sheet (sheet_name=1 means the second sheet)
        # Read only up to max_rows
        df = pd.read_excel(excel_filepath, sheet_name=sheet_index, nrows=max_rows)
        print(f"Successfully read {len(df)} rows from sheet index {sheet_index}.")

        # Verify required columns exist
        missing_cols = [col for col in prompt_columns if col not in df.columns]
        if missing_cols:
            print(f"Error: Missing required columns in sheet: {missing_cols}")
            return None

    except FileNotFoundError:
        print(f"Error: File not found at {excel_filepath}")
        return None
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

    prompts_list = []
    responses_list = [] # Placeholder for LLM responses

    # Ensure the directory for the output file exists
    output_dir = os.path.dirname(output_prompt_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # --- 3) Write prompts to screen and a file ---
    try:
        with open(output_prompt_file, 'w', encoding='utf-8') as f_out:
            print(f"Opened {output_prompt_file} for writing prompts.")
            
            # --- 2) Loop the data ---
            print("\n--- Generating and Printing Prompts ---")
            for index, row in df.iterrows():
                # Extract data, handle potential missing values (NaN) by converting to string
                try:
                    col_c_val = str(row[prompt_columns[0]]) if pd.notna(row[prompt_columns[0]]) else ""
                    col_d_val = str(row[prompt_columns[1]]) if pd.notna(row[prompt_columns[1]]) else ""
                    col_e_val = str(row[prompt_columns[2]]) if pd.notna(row[prompt_columns[2]]) else ""
                except IndexError:
                    print(f"Warning: Row {index} seems to have fewer columns than expected in prompt_columns list. Skipping.")
                    continue
                except KeyError as ke:
                    # This should be caught earlier, but as a safeguard
                    print(f"Error accessing column {ke} in row {index}. Check column names.")
                    continue


                # Create the prompt - using f-string for easy formatting
                prompt = f"Given this information about a person's employment, assign a SIC and SOC code - {col_c_val}, {col_d_val}, {col_e_val}."

                # Store prompt
                prompts_list.append(prompt)

                # Print prompt to screen
                print(f"Row {index}: {prompt}")

                # Write prompt to file
                f_out.write(prompt + '\n')

                # --- 4) Collate responses (Placeholder) ---
                # TODO: Add your LLM API call here using the 'prompt' variable
                # For now, we just add a placeholder
                placeholder_response = {"SIC": "PENDING", "SOC": "PENDING", "Row": index}
                responses_list.append(placeholder_response)

            print("\n--- Finished processing rows ---")

    except IOError as e:
        print(f"Error writing to output file {output_prompt_file}: {e}")
        return None # Return None as we couldn't write the prompts
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")
        return None

    # Add generated prompts and placeholder responses back to the DataFrame
    if len(prompts_list) == len(df): # Ensure lists match DataFrame length
        df['GeneratedPrompt'] = prompts_list
        df['LLM_Response'] = responses_list
    else:
        print("Warning: Number of generated prompts/responses does not match DataFrame rows. Skipping column addition.")

    print(f"--- Prompt generation complete. Prompts saved to {output_prompt_file} ---")
    return df

# --- Configuration ---
# Replace with the actual path to your Excel file
EXCEL_FILE = 'path/to/your/input_data.xlsx' 
# Replace with the desired path for your prompts debug file
PROMPT_OUTPUT_FILE = 'output/prompts_debug.txt' 
# Specify columns if they are not literally 'C', 'D', 'E'
# e.g., PROMPT_COLUMNS = ['Job Title', 'Duties', 'Industry'] 
PROMPT_COLUMNS = ['C', 'D', 'E'] 
SHEET_INDEX_TO_READ = 1 # Second sheet
MAX_ROWS_TO_PROCESS = 100

# --- Run the function ---
if __name__ == "__main__":
    # Check if the placeholder path needs changing
    if EXCEL_FILE == 'path/to/your/input_data.xlsx':
        print("!!! Please update the EXCEL_FILE variable in the script with the correct path to your Excel file !!!")
    else:
        processed_df = generate_prompts_from_excel(
            excel_filepath=EXCEL_FILE, 
            output_prompt_file=PROMPT_OUTPUT_FILE,
            sheet_index=SHEET_INDEX_TO_READ,
            prompt_columns=PROMPT_COLUMNS,
            max_rows=MAX_ROWS_TO_PROCESS
        )

        if processed_df is not None:
            print("\n--- First 5 rows of processed DataFrame ---")
            print(processed_df.head())
            # You can now work with 'processed_df'
            # For example, iterate through df['LLM_Response'] later 
            # when you integrate the actual LLM calls.
