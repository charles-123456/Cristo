import odoo, xlwt
from odoo import models

class ProfessionXlsx(models.AbstractModel):
    _name = 'report.cristo.report_profession'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Profession"

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Member Profession Report')
        fields = ['Name','Unique Code','Date','Place','Type','Years','State'
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname, header_format)   
        _row = 1
        for i, member in enumerate(members):
            row = _row
            worksheet.write(row,0, member.full_name)
            worksheet.set_column('A:A',20)
            worksheet.write(row,1,member.unique_code or '-')
            worksheet.set_column('B:B',20)
            for profession in member.profession_ids:
                worksheet.write(row,2,profession.profession_date or '-',date_format)
                worksheet.set_column('C:C',20)
                worksheet.write(row,3,profession.place or '-')
                worksheet.set_column('D:D',20)
                worksheet.write(row,4,profession.type or '-')
                worksheet.set_column('E:E',20)
                worksheet.write(row,5,profession.years or '-')
                worksheet.set_column('F:F',20)
                worksheet.write(row,6,profession.state or '-')
                worksheet.set_column('G:G',20)
               
                row += 1
            _row = row
             
        
        
            