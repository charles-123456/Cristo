import odoo, xlwt
from odoo import models

class FormationXlsx(models.AbstractModel):
    _name = 'report.cristo.report_formation'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Formation'
    
    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Member Formation Report')
        fields = ['Name','Unique Code','House Code/Name','Stage','Start Year','End Year','Any Study Done','House Name'
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
            for formation in member.formation_ids:
                house = formation.house_id.code if formation.sudo().house_id.code else formation.sudo().house_id.name
                worksheet.write(row,2,house or '-')
                worksheet.set_column('C:C',20)
                worksheet.write(row,3,formation.formation_stage_id.name or '-')
                worksheet.set_column('D:D',20)
                worksheet.write(row,4,formation.start_year or '-')
                worksheet.set_column('E:E',20)
                worksheet.write(row,5,formation.end_year or '-')
                worksheet.set_column('F:F',20)
                worksheet.write(row,6,formation.study_info or '-')
                worksheet.set_column('G:G',20)
                worksheet.write(row,7,formation.house_id.name or '-')
                worksheet.set_column('H:H',20)
               
                row += 1
            _row = row
             
        
        
            