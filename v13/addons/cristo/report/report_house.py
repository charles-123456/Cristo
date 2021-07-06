import odoo, xlwt
from odoo import models

class PublicationXlsx(models.AbstractModel):
    _name = 'report.cristo.report_house'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, houses):
        worksheet = workbook.add_worksheet('House Report')
        fields = ['Name','Code','Patron','Congregation','Province','Area','Parish','Year Of Establishment',
                  'Year Of Canonical Erection','Superior Name','Position','Founder','Address','Email','Phone',
                  'Mobile','Website Link','Benefactors','Current Member/Member','Current Member/Roles','Current Member/From',
                  'Current Member/To',
                  
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname, header_format)   
        _row = 1
        for i,house in enumerate(houses):
            address = [(house.street) or '',(house.street2) or '',(house.place) or '',(house.city) or '',(house.district_id.name) or '',(house.state_id.name) or '',(house.zip) or '',(house.country_id.name) or '']
            print('address',address)
            row = _row
            worksheet.write(row,0, house.name or '-')
            worksheet.set_column('A:A',20)
            worksheet.write(row,1,house.code or '-')
            worksheet.set_column('B:B',20)
            worksheet.write(row,2,house.patron_id.name or '-')
            worksheet.set_column('C:C',20)
            worksheet.write(row,3,house.institute_id.name or '-')
            worksheet.set_column('D:D',20)
            worksheet.write(row,4,house.rel_province_id.name or '-')
            worksheet.set_column('E:E',20)
            worksheet.write(row,5,house.rel_zone_id.name or '-')
            worksheet.set_column('F:F',20)
            worksheet.write(row,6,house.parish_id.name or '-')
            worksheet.set_column('G:G',20)
            worksheet.write(row,7,house.establishment_year or '-')
            worksheet.set_column('H:H',20)
            worksheet.write(row,8,house.canonical_year or '-')
            worksheet.set_column('I:I',20)
            worksheet.write(row,9,house.superior_id.name or '-')
            worksheet.set_column('J:J',20)
            worksheet.write(row,10,','.join(house.position_ids.mapped('name')) or '-')
            worksheet.set_column('K:K',20)
            worksheet.write(row,11,house.founder or '-')
            worksheet.set_column('L:L',20)
            worksheet.write(row,12,','.join(address)or '-')
            worksheet.set_column('M:M',20)
            print('address',address)
#             worksheet.write(row,12,house.state_id.name or '')
#             worksheet.set_column('N:N',20)
            worksheet.write(row,13,house.email or '-')
            worksheet.set_column('N:N',20)
            worksheet.write(row,14,house.phone or '-')
            worksheet.set_column('O:O',20)
            worksheet.write(row,15,house.mobile or '-')
            worksheet.set_column('P:P',20)
            worksheet.write(row,16,house.website or '-')
            worksheet.set_column('Q:Q',20)
            worksheet.write(row,17,house.benefactors or '-')
            worksheet.set_column('R:R',20)
            for House in house.house_member_ids:
                worksheet.write(row,18,House.member_id.full_name or '-')
                worksheet.set_column('S:S',20)
                worksheet.write(row,19,','.join(House.member_role_ids.role_ids.mapped('name')))
                worksheet.set_column('T:T',20)
                worksheet.write(row,20,House.date_from or '-',date_format)
                worksheet.set_column('U:U',20)
                worksheet.write(row,21,House.date_to or '-',date_format)
                worksheet.set_column('V:V',20)
                row += 1
            _row = row
             
        
        
            