from odoo import models, fields, api, _
from datetime import datetime, date

class ReportReligiousCommunityProfile(models.AbstractModel):
    _name = 'report.cristo.report_rel_community_profile'
    _description = "Report Religious Community"
    
    def get_institute_count(self, community_id):
        institute_count = self.env['res.institution'].search_count([('community_id', '=', community_id)])
        return institute_count
    
    def get_institutions(self, community_id):
        instituion_ids = self.env['res.institution'].search([('community_id', '=', community_id)])
        return instituion_ids
    
    def get_superior_name(self, institution_id):
        superior_id = self.env['res.superior.details'].search([('institution_id', '=', institution_id)], order="year_from desc",limit=1)
        return superior_id.name
     
#     def get_community_member(self, community_id):
#         member_ids = self.env['res.religious.assignment'].search([('community_id', '=', community_id)])
#         return member_ids
        
#     def get_institute_member(self, institution_id):
#         member_ids = self.env['res.religious.assignment'].search([('institution_id', '=', institution_id)])
#         print member_ids
#         return member_ids
        
    @api.model
    def _get_report_values(self, docids, data=None):
        Report = self.env['ir.actions.report']
        report = Report._get_report_from_name('cristo.report_rel_community_profile')
        docargs = {
            'doc_ids': self.id,
            'doc_model': 'res.community',
            'docs': self.env['res.community'].browse(docids),
            'data': data,
            'get_institute_count':self.get_institute_count,
            'get_institutions':self.get_institutions,
#             'get_superior_name':self.get_superior_name,
#             'get_community_member':self.get_community_member,
#             'get_institute_member':self.get_institute_member,
        }
        return docargs