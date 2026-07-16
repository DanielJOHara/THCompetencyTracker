"""Utility to load TH Competency Tracker data from an Excel spreadsheet to a SQLite database."""
import argparse
import os
import sqlite3
import pandas as pd


def import_excel_to_sqlite(excel_path: str, sqlite_path: str) -> None:
    """Read an Excel spreadsheet and write each sheet to a SQLite database table."""
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Source Excel file not found: {excel_path}")

    print(f"Reading Excel spreadsheet: {excel_path}")
    
    # Standard tables used in TH Competency Tracker
    tables = [
        'Service', 'Role', 'Staff', 'Competency', 'Role Service',
        'Competency Service', 'Staff Role', 'Role Competency', 'Staff Competency'
    ]

    print(f"Connecting to SQLite database: {sqlite_path}")
    conn = sqlite3.connect(sqlite_path)
    try:
        for table in tables:
            try:
                # Read sheet from Excel
                df = pd.read_excel(excel_path, sheet_name=table, keep_default_na=False)
                print(f"Read {len(df)} rows from sheet '{table}'")

                # Parse date/datetime columns so they are stored as standard datetime/date strings in SQLite
                if table == 'Staff' and 'Start Date' in df.columns:
                    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
                elif table == 'Staff Competency':
                    for col in ['Prerequisite Date', 'Competency Date']:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                
                if 'Change Date' in df.columns:
                    df['Change Date'] = pd.to_datetime(df['Change Date'], errors='coerce')

                # Save to SQLite table
                df.to_sql(table, conn, if_exists='replace', index=False)
                print(f"  Successfully wrote table '{table}' to database")
            except ValueError as e:
                # Sheet name not found in the excel file
                print(f"  Warning: Sheet '{table}' was not found in Excel file. Skipping. (Detail: {e})")
            except Exception as e:
                print(f"  Error importing table '{table}': {e}")
                raise
    finally:
        conn.close()
        
    print("Import completed successfully!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import TH Competency Tracker Excel sheets into a SQLite database.")
    parser.add_argument('-i', '--input', required=True, help="Path to the source Excel file (.xlsx)")
    parser.add_argument('-o', '--output', required=True, help="Path to the target SQLite database file (.db)")
    args = parser.parse_args()
    
    import_excel_to_sqlite(args.input, args.output)
