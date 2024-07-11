class ReportGenerator:
    def __init__(self, spreadsheet, gpt_client, max_col, answers, system_input):
        self.spreadsheet = spreadsheet
        self.gpt_client = gpt_client
        self.max_col = max_col
        self.answers = answers
        self.system_input = system_input
    
    def create_columns(self):
        return [chr(65 + idx) for idx in range(self.max_col + 1)]
    
    def process_row(self, row):
        columns = self.create_columns()
        cells = self.spreadsheet.get_cells(columns, row)
        cells_value = self.spreadsheet.get_cells_value(cells)
        update_cell = cells[-1]

        question = "".join(self.answers[idx] + str(cells_value[idx + 3]) + "\n" for idx in range(len(self.answers)))
        response = self.gpt_client.generate_response(self.system_input, question)
        
        self.spreadsheet.update_cell(update_cell, response)
        print(f"{row}행 작업 완료")