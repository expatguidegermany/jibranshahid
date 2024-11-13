
from ExcelData import ExcelData
import time



# Define your Google Sheets' spreadsheet_id and range_name
google_sheets_spreadsheet_id = '1nE8Mg0R3QX_GIZbYJv_3wSdZ6QsxJlMGfDaJ3t_IBgU'
google_sheets_range_name = 'A1:C'

# Initialize the ExcelData class for Google Sheets
excel_data = ExcelData(google_sheets_spreadsheet_id, google_sheets_range_name)




# Define your Google Sheets' spreadsheet_id and range_name
google_sheets_spreadsheet_id = '1nE8Mg0R3QX_GIZbYJv_3wSdZ6QsxJlMGfDaJ3t_IBgU'
google_sheets_range_name = 'A1:C'

# Initialize the ExcelData class for Google Sheets
excel_data = ExcelData(google_sheets_spreadsheet_id, google_sheets_range_name)

thread_id = "test"
prompt = "check check"

# Get the current timestamp
current_time = time.strftime("%Y-%m-%d %H:%M:%S")

# Create a list with data to append to Google Sheets
data_to_append = [[current_time, thread_id, prompt]]

# Append the data to Google Sheets
excel_data.append_values(google_sheets_spreadsheet_id, google_sheets_range_name, "USER_ENTERED", data_to_append)