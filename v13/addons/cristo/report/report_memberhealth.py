import odoo, xlwt
from odoo import models

class MemberHealthXlsx(models.AbstractModel):
    _name = 'report.cristo.report_memberhealth'
    _description = "Report Memberhealth"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Member Member Health Report')
        fields = ['Name','Unique Code','Disease Type','Start Date','End Date','Medical Concern','Referred Physician'
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
            for memberhealth in member.member_health_ids:
                worksheet.write(row,2,memberhealth.disease_disorder_id.name or '-')
                worksheet.set_column('C:C',20)
                worksheet.write(row,3,memberhealth.start_date or '-',date_format)
                worksheet.set_column('D:D',20)
                worksheet.write(row,4,memberhealth.end_date or '-',date_format)
                worksheet.set_column('E:E',20)
                worksheet.write(row,5,memberhealth.particulars or '-')
                worksheet.set_column('F:F',20)
                worksheet.write(row,6,memberhealth.referred_physician or '-')
                worksheet.set_column('G:G',20)
               
                row += 1
            _row = row
             
        
        
            