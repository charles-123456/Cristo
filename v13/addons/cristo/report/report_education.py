import odoo, xlwt
from odoo import models

class EducationXlsx(models.AbstractModel):
    _name = 'report.cristo.report_education'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Education"

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Member Education Report')
        fields = ['Name','Unique Code','Study Level','Program','Institution','Year of Passing','Core Disciplines',
                  'Particulars','Duration(in Years)','Mode','Result','Remarks'
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})
        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname, header_format)   
        _row = 1
        for i, member in enumerate(members):
            row = _row
            worksheet.write(row,0, member.full_name)
            worksheet.set_column('A:A',20)
            worksheet.write(row,1,member.unique_code or '-')
            worksheet.set_column('B:B',20)
            for education in member.member_education_ids:
                worksheet.write(row,2,education.study_level_id.name or '-')
                worksheet.set_column('C:C',20)
                worksheet.write(row,3,education.program_id.name or '-')
                worksheet.set_column('D:D',20)
                worksheet.write(row,4,education.institution or '-')
                worksheet.set_column('E:E',20)
                worksheet.write(row,5,education.year_of_passing or '-')
                worksheet.set_column('F:F',20)
                worksheet.write(row,6,', '.join(education.core_disiplines_ids.mapped('name')) or '-')
                worksheet.set_column('G:G',20)
                worksheet.write(row,7,education.particulars or '-')
                worksheet.set_column('H:H',20)
                worksheet.write(row,8,education.duration or '-')
                worksheet.set_column('I:I',20)
                worksheet.write(row,9,education.mode or '-')
                worksheet.set_column('J:J',20)
                worksheet.write(row,10,education.result or '-')
                worksheet.set_column('K:K',20)
                worksheet.write(row,11,education.note or '-')
                worksheet.set_column('L:L',20)
               
                row += 1
            _row = row
             
        
        
            