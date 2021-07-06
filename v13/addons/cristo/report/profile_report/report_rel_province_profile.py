from odoo import models, fields, api, _
from datetime import datetime, date

class ReportReligiousProvinceProfile(models.AbstractModel):
    _name = 'report.cristo.report_rel_province_profile'
    _description = "Report Religious Province"
    
    def get_community_count(self, province_id):
        community_count = self.env['res.community'].search_count([('rel_province_id', '=', province_id)])
        return community_count
    
    def get_institute_count(self, province_id):
        institute_count = self.env['res.institution'].search_count([('rel_province_id', '=', province_id)])
        return institute_count
    
    def get_communities_institutions(self, province_id):
        community_ids = self.env['res.community'].search([('rel_province_id', '=', province_id)])
        all_community = [] 
        for community_id in community_ids:
            institute_ids = self.env['res.institution'].search([('community_id', '=', community_id.id)])
            all_community.append({'community': community_id,'institutions': institute_ids})
        return all_community

    def get_provincial_detail(self, province):
        data = []
        for role in province.head_role_ids:
            hm_ids = self.env['house.member'].search([('member_id','in',province.member_ids.ids),('status','=','active')])
            if hm_ids:
                role_id = hm_ids.filtered('member_role_ids').filtered(lambda hmr: role.id in hmr.role_ids.ids)
                if role_id:
                    member_id = self.env['res.member'].browse(role_id[0].member_id.id)
                    data.append([role.name,member_id])
        if data:
            return data
        return False

    def get_council_members(self, province_id):
        active_council = self.env['res.council'].sudo().search([('rel_province_id','=',province_id),('status','=','active')],limit=1)
        if active_council and active_council.member_ids:
            return active_council.member_ids
        return False

    def get_statistic_count(self, province):
        data = []
        if province.institute_id.institute_type in ['priest','lay_brother','brother']:
            priests = self.env['res.member'].sudo().search_count([('member_type','=','priest'),('rel_province_id','=',province.id)])
            lay_brothers = self.env['res.member'].sudo().search_count([('member_type', '=', 'lay_brother'), ('rel_province_id', '=', province.id)])
            brothers = self.env['res.member'].sudo().search_count([('member_type', '=', 'brother'), ('rel_province_id', '=', province.id)])
            deacons = self.env['res.member'].sudo().search_count([('member_type', '=', 'deacon'), ('rel_province_id', '=', province.id)])
            novice = self.env['res.member'].sudo().search_count([('member_type', '=', 'novice'), ('rel_province_id', '=', province.id)])
            data = [['Priests',priests],['Deacons',deacons],['Brothers',brothers],['Lay Brothers',lay_brothers],['Novices',novice]]
        elif province.institute_id.institute_type in ['sister_apostolic', 'sister_contemplative']:
            sisters = self.env['res.member'].sudo().search_count([('member_type', '=', 'sister'), ('rel_province_id', '=', province.id)])
            junior_sisters = self.env['res.member'].sudo().search_count([('member_type', '=', 'junior_sister'), ('rel_province_id', '=', province.id)])
            novice = self.env['res.member'].sudo().search_count([('member_type', '=', 'novice'), ('rel_province_id', '=', province.id)])
            data = [['Sisters',sisters],['Junior Sisters',junior_sisters],['Novices',novice]]
        if data:
            return data
        return False

    def get_other_center_detail(self, province_id):
        other_center = self.env['res.institution'].sudo().search([('rel_province_id','=',province_id),('institution_category_id.name','=','Other Center')])
        if other_center:
            return other_center
        return False

    def get_formation_institution_details(self, province_id):
        data = []
        formation_house = self.env['res.institution'].sudo().search([('rel_province_id','=',province_id),('institution_category_id.name','=','Formation')])
        ministry_ids = self.env['res.institution.category'].sudo().search([('parent_id.name','=','Formation')])
        for min in ministry_ids:
            institution = formation_house.filtered(lambda formation:formation.ministry_category_id.id == min.id)
            if institution:
                ministry = min.name
                institutions = ', '.join(institution.mapped('name'))
                data.append([ministry, institutions])
        unknown_institution = formation_house.filtered(lambda formation:formation.ministry_category_id.id == False)
        if unknown_institution:
            institutions = ', '.join(unknown_institution.mapped('name'))
            data.append(['Unknown', institutions])
        if data:
            return data
        return False

    def get_boarding_institution_count(self, province_id):
        boarding_institution_count = self.env['res.institution'].sudo().search_count([('rel_province_id','=',province_id),('ministry_category_id.code','in',['WBH','WHBB','WHBG','WHOC','WADD','WHS','WHSDD','WHB'])])
        return boarding_institution_count

    def get_parish_count(self, province_id):
        parish_count = 0
        if province_id.diocese_ids:
            parish_count = self.env['res.parish'].search_count([('diocese_id','in',province_id.diocese_ids.ids)])
        return parish_count

    def get_school_college_count(self, province_id):
        categories = self.env['res.institution.category'].search(['|','|',('name','ilike','school'),('name','ilike','secondary'),('name','ilike','college')])
        count = self.env['res.institution'].sudo().search_count([('rel_province_id', '=', province_id),('ministry_category_id','in',categories.ids)])
        return count

    @api.model
    def _get_report_values(self, docids, data=None):
        Report = self.env['ir.actions.report']
        report = Report._get_report_from_name('cristo.report_rel_province_profile')
        docargs = {
            'doc_ids': self.id,
            'doc_model': 'res.religious.province',
            'docs': self.env['res.religious.province'].browse(docids),
            'data': data,
            'get_community_count':self.get_community_count,
            'get_institute_count':self.get_institute_count,
            'get_communities_institutions':self.get_communities_institutions,
            'get_provincial_detail':self.get_provincial_detail,
            'get_council_members':self.get_council_members,
            'get_statistic_count':self.get_statistic_count,
            'get_other_center_detail':self.get_other_center_detail,
            'get_formation_institution_details':self.get_formation_institution_details,
            'get_boarding_institution_count':self.get_boarding_institution_count,
            'get_parish_count':self.get_parish_count,
            'get_school_college_count':self.get_school_college_count,
        }
        return docargs