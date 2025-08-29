import pandas as pd
from utils.exceptions import ExcelConversionError


def convert_excel_to_dict(file_path: str) -> list[dict]:
    """
    Read an Excel file into a pandas DataFrame.
    """
    try:
        data = pd.read_excel(file_path)
        df = pd.DataFrame(data)

        # clean the data
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)

        # convert the data to a list of dictionaries
        return df.to_dict(orient="records")
    except Exception as e:
        raise ExcelConversionError(f"Error converting Excel file to dictionary: {e}")
