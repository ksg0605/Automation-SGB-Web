import openpyxl

class Spreadsheet:
    def __init__(self, file_path, sheet_name):
        self.wb = openpyxl.load_workbook(file_path)
        self.sheet = self.wb[sheet_name]
        self.file_path = file_path
    
    def get_cells(self, columns, row):
        return [column + str(row) for column in columns]
    
    def get_cells_value(self, cells):
        return [self.sheet[cell].value for cell in cells]
    
    def update_cell(self, cell, value):
        self.sheet[cell].value = value
    
    def save(self, output_path):
        self.wb.save(output_path)
        
    def get_max_row(self):
        return self.sheet.max_row