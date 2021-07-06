import odoo, xlwt
from odoo import models

class HolyOrderXlsx(models.AbstractModel):
    _name = 'report.cristo.report_holyorder'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Holyorder"

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Member Holy Order Report')
        fields = ['Name','Unique Code','Date','Place','Order','minister','State'
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
            for holyorder in member.holyorder_ids:
                worksheet.write(row,2,holyorder.date or '-',date_format)
                worksheet.set_column('C:C',20)
                worksheet.write(row,3,holyorder.place or '-')
                worksheet.set_column('D:D',20)
                worksheet.write(row,4,holyorder.order or '-')
                worksheet.set_column('E:E',20)
                worksheet.write(row,5,holyorder.minister or '-')
                worksheet.set_column('F:F',20)
                worksheet.write(row,6,holyorder.state or '-')
                worksheet.set_column('G:G',20)
               
                row += 1
            _row = row
             
        
        
            