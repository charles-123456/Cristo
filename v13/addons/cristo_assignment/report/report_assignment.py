from odoo import models
import odoo, xlwt

class AssignmentReport(models.AbstractModel):
    _name = "report.cristo_assignment.report_assignment"
    _description = "Report Assignment"
    _inherit = 'report.report_xlsx.abstract'
     
     
    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Member Assignment Report')
        fields = ['Member Name','Member Code','Active House','Active Institution','Active Role','Years of Ministry','New House','New Roles'
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})
        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname, header_format)   
        _row = 1
        for i, member in enumerate(members):
            row = _row
            for assignment_id in member.assignment_due_ids:
                worksheet.write(row,0,assignment_id.member_id.full_name or '-')
                worksheet.set_column('A:A',30)
                worksheet.write(row,1,assignment_id.member_id.unique_code or '-')
                worksheet.set_column('B:B',30)
                worksheet.write(row,2,assignment_id.pre_house_id.name or '-')
                worksheet.set_column('C:C',30)
                worksheet.write(row,3,assignment_id.pre_institution_id.name or '-')
                worksheet.set_column('D:D',30)
                worksheet.write(row,4,', '.join(assignment_id.old_role_ids.mapped('name')) or '-')
                worksheet.set_column('E:E',30)
                worksheet.write(row,5,assignment_id.ministry_years or '-')
                worksheet.set_column('F:F',30)
                worksheet.write(row,6,assignment_id.new_community_id.name or '-')
                worksheet.set_column('G:G',30)
                worksheet.write(row,7,', '.join(assignment_id.new_role_ids.mapped('name')) or '-')
                worksheet.set_column('H:H',30)
               
                row += 1
            _row = row
    

