import odoo, xlwt
from odoo import models

class PublicationXlsx(models.AbstractModel):
    _name = 'report.cristo.report_publication'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Publication"

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Member publication Report')
        fields = ['Name','Unique Code','Publication Date','Title','Publication Type','Publisher','Royalty'
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
            for publication in member.publication_ids:
                worksheet.write(row,2,publication.publication_date or '-',date_format)
                worksheet.set_column('C:C',20)
                worksheet.write(row,3,publication.title or '-')
                worksheet.set_column('D:D',20)
                worksheet.write(row,4,publication.publication_type_id.name or '-')
                worksheet.set_column('E:E',20)
                worksheet.write(row,5,publication.publisher or '-')
                worksheet.set_column('F:F',20)
                worksheet.write(row,6,publication.royalty or '-')
                worksheet.set_column('G:G',20)
               
                row += 1
            _row = row
             
        
        
            