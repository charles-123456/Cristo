import odoo, xlwt
from odoo import models

def _sample_data(self):
    user = self.env.user
    if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
        mem_data = self.env['res.member'].search([('institute_id', '=', user.institute_id.id)])
    elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
        mem_data = self.env['res.member'].search([('rel_province_id', '=', user.rel_province_id.id)])
    elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
        mem_data = self.env['res.member'].search([('community_id', '=', user.community_id.id)])
    else:
        mem_data = False
    return mem_data

class EducationTemplate(models.AbstractModel):
    _name = 'report.member_import_data.education_template'
    _description = "Import Education Template"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Education Template')
        fields = ['Name','Unique Code','Study Level','Program','Institution','Year of Passing','Core Disciplines',
                  'Particulars','Duration(in Years)','Mode','Result','Remarks'
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})

        for i, fieldname in enumerate(fields):
            worksheet.set_column(1, i, 30)
            worksheet.write(0, i, fieldname, header_format)

        mem_data = _sample_data(self)
        if mem_data:
            row = 1
            for mem in mem_data:
                worksheet.write(row, 0, mem.full_name)
                worksheet.write(row, 1, mem.unique_code)
                row = row + 1

class FormationTemplate(models.AbstractModel):
    _name = 'report.member_import_data.formation_template'
    _description = "Import Formation Template"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Formation Template')
        fields = ['Name','Unique Code','House Code/Name','Stage','Start Year','End Year','Any Study Done','House Name'
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})
        for i, fieldname in enumerate(fields):
            worksheet.set_column(1, i, 30)
            worksheet.write(0, i, fieldname, header_format)

        mem_data = _sample_data(self)
        if mem_data:
            row = 1
            for mem in mem_data:
                worksheet.write(row, 0, mem.full_name)
                worksheet.write(row, 1, mem.unique_code)
                row = row + 1

class HolyOrderTemplate(models.AbstractModel):
    _name = 'report.member_import_data.holyorder_template'
    _description = "Import Holyorder Template"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Holy Order Template')
        fields = ['Name','Unique Code','Date','Place','Order','minister','State'
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})
        for i, fieldname in enumerate(fields):
            worksheet.set_column(1, i, 30)
            worksheet.write(0, i, fieldname, header_format)

        mem_data = _sample_data(self)
        if mem_data:
            row = 1
            for mem in mem_data:
                worksheet.write(row, 0, mem.full_name)
                worksheet.write(row, 1, mem.unique_code)
                row = row + 1

class ProfessionTemplate(models.AbstractModel):
    _name = 'report.member_import_data.profession_template'
    _description = "Import Profession Template"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Profession Template')
        fields = ['Name','Unique Code','Date','Place','Type','Years','State'
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})
        for i, fieldname in enumerate(fields):
            worksheet.set_column(1, i, 30)
            worksheet.write(0, i, fieldname, header_format)

        mem_data = _sample_data(self)
        if mem_data:
            row = 1
            for mem in mem_data:
                worksheet.write(row, 0, mem.full_name)
                worksheet.write(row, 1, mem.unique_code)
                row = row + 1

class MemberHealthTemplate(models.AbstractModel):
    _name = 'report.member_import_data.memberhealth_template'
    _description = "Import Memberhealth Template"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('Member Health Template')
        fields = ['Name','Unique Code','Disease Type','Start Date','End Date','Medical Concern','Referred Physician'
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})
        for i, fieldname in enumerate(fields):
            worksheet.set_column(1, i, 30)
            worksheet.write(0, i, fieldname, header_format)

        mem_data = _sample_data(self)
        if mem_data:
            row = 1
            for mem in mem_data:
                worksheet.write(row, 0, mem.full_name)
                worksheet.write(row, 1, mem.unique_code)
                row = row + 1

class PublicationTemplate(models.AbstractModel):
    _name = 'report.member_import_data.publication_template'
    _description = "Import Publication Template"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, members):
        worksheet = workbook.add_worksheet('publication Template')
        fields = ['Name','Unique Code','Publication Date','Title','Publication Type','Publisher','Royalty'
                  ]
        header_format = workbook.add_format({'bold': True, 'font_color': 'black','bg_color':'#A9A9A9','border':2})
        for i, fieldname in enumerate(fields):
            worksheet.set_column(1, i, 30)
            worksheet.write(0, i, fieldname, header_format)

        mem_data = _sample_data(self)
        if mem_data:
            row = 1
            for mem in mem_data:
                worksheet.write(row, 0, mem.full_name)
                worksheet.write(row, 1, mem.unique_code)
                row = row + 1