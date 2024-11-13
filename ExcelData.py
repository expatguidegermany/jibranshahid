import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import google.auth
from googleapiclient.errors import HttpError
import time

class ExcelData:
    def __init__(self, sheetid, range_name):

        self.read_google_sheet(sheetid, range_name)

    def load_excel_data(self, excel_file_path):
        # Load the Excel file
        self.data = pd.read_excel(excel_file_path)
        
        # Set each column as a property of the class
        for column in self.data.columns:
            setattr(self, column, self.data[column].tolist())

    def get_the_row(self,row_number):
        row = self.data[row_number]
        return row
    
    def read_google_sheet(self,spreadsheet_id, range_name):
        # Load credentials from the service account JSON file
        creds = Credentials.from_service_account_file('liveingermany-1699367027361-3149fe002aa5.json')
        
        # Create a service object for the API
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        self.data = values

        
        # Assume first row is headers
        headers = values[0]
        data = []
        for row in values[1:]:
            # Create a dictionary for each row
            row_data = dict(zip(headers, row))
            data.append(row_data)

        self.data = data
        return data
    
    def append_values(self, spreadsheet_id, range_name, value_input_option, values):
        # Load credentials from the service account JSON file
        creds = Credentials.from_service_account_file('liveingermany-1699367027361-3149fe002aa5.json')
        
        
        try:
            service = build("sheets", "v4", credentials=creds)

            body = {"values": values}
            result = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )
            print(f"{result.get('updates').get('updatedCells')} cells appended.")
            return result

        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

# Usage:
if __name__ == "__main__":

    # Define your Google Sheets' spreadsheet_id and range_name
    google_sheets_spreadsheet_id = '1nE8Mg0R3QX_GIZbYJv_3wSdZ6QsxJlMGfDaJ3t_IBgU'
    google_sheets_range_name = 'A1:C'

    # Initialize the ExcelData class for Google Sheets
    excel_data = ExcelData(google_sheets_spreadsheet_id, google_sheets_range_name)

    # Access the properties (columns of the Excel file)
    # For example, to access the data in a column named 'title':
    # titles = excel_data.title  # Assuming there's a column named 'title' in the Excel file
    # print(titles)
    # Pass: spreadsheet_id, range_name, and thread_id
    # Get the current timestamp
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    # Create a list with data to append to Google Sheets
    data_to_append = [[current_time, "check123"]]

    # Append the data to Google Sheets
    excel_data.append_values(google_sheets_spreadsheet_id, google_sheets_range_name, "USER_ENTERED", data_to_append)
