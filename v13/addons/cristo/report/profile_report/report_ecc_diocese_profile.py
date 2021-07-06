from odoo import models, fields, api, _

class ReportEcclesiaDioceseProfile(models.AbstractModel):
    _name = 'report.cristo.report_ecc_diocese_profile'
    _description = "Report Ecclesia Diocese"

    def get_priest_count(self, diocese_id):
        priest_count = self.env['res.member'].search_count([('diocese_id', '=', diocese_id),('member_type', '=', 'priest')])
        return priest_count

    def get_diocesen_priest_count(self, diocese_id):
        diocesen_priest_count = self.env['res.member'].search_count([('diocese_id', '=', diocese_id),('member_type', '=', 'priest'),('membership_type', '=', 'SE')])
        return diocesen_priest_count

    def get_religious_priest_count(self, diocese_id):
        religious_priest_count = self.env['res.member'].search_count([('diocese_id', '=', diocese_id),('member_type', '=', 'priest'),('membership_type', '=', 'RE')])
        return religious_priest_count

    def get_congregation_sister_count(self):
        cong_of_sis = self.env['res.religious.institute'].sudo().search_count([('institute_type','in',['sister_apostolic','sister_contemplative'])])
        return cong_of_sis

    def get_congregation_brother_count(self):
        cong_of_bro = self.env['res.religious.institute'].sudo().search_count([('institute_type', 'in', ['brother', 'lay_brother'])])
        return cong_of_bro

    def get_congregation_father_count(self):
        cong_of_father = self.env['res.religious.institute'].sudo().search_count([('institute_type', '=', 'priest')])
        return cong_of_father

    def get_institution_count(self, diocese_id):
        diocese_institution = self.env['res.institution'].search_count([('community_id.owned_by','=','diocese'),('community_id.diocese_id','=',diocese_id)])
        religious_institution = self.env['res.institution'].search_count([('community_id.owned_by', '=', 'religious'),('community_id.diocese_id', '=', diocese_id)])
        return [diocese_institution,religious_institution]

    def get_deputy_bishop_detail(self, diocese_id, role_id):
        data = {'name': '', 'phone': '', 'email': '', 'birthday': '', 'feastday': ''}
        diocese_member_ids = self.env['house.member'].search([('date_to', '=', False), ('member_id.diocese_id', '=', diocese_id)])
        house_member_ids= diocese_member_ids.mapped('member_role_ids').filtered(lambda hmr:role_id in hmr.role_ids.ids)
        if house_member_ids:
            feastday = False
            birthday = False
            member_id = house_member_ids[0].house_member_id.member_id
            if member_id.feast_day and member_id.feast_month:
                feastday = str(member_id.feast_day)+'-'+str(member_id.feast_month)
            if member_id.dob:
                birthday = member_id.dob.strftime("%d-%b-%Y")
            data.update({'name':member_id.name,'phone':member_id.mobile,'email':member_id.email,'birthday':birthday,'feastday':feastday})
            return data
        return False

    def get_formation_institution_detail(self, diocese_id):
        data = []
        formation_house = self.env['res.institution'].sudo().search([('diocese_id','=',diocese_id),('institution_category_id.name','=','Formation')])
        category_ids = self.env['res.institution.category'].sudo().search([('parent_id.name','=','Formation')])
        for category in category_ids:
            institution = formation_house.filtered(lambda formation:formation.ministry_category_id.id == category.id)
            if institution:
                category_name = category.name
                institutions = ', '.join(institution.mapped('name'))
                data.append([category_name, institutions])
        unknown_institution = formation_house.filtered(lambda formation: formation.ministry_category_id.id == False)
        if unknown_institution:
            institutions = ', '.join(unknown_institution.mapped('name'))
            data.append(['Unknown', institutions])
        if data:
            return data
        return False

    def get_health_center_detail(self, diocese_id):
        data = []
        health_center = self.env['res.institution'].sudo().search(
            [('diocese_id', '=', diocese_id), ('institution_category_id.name', '=', 'Health Care')])
        category_ids = self.env['res.institution.category'].sudo().search([('parent_id.name', '=', 'Health Care')])
        for category in category_ids:
            institution = health_center.filtered(lambda formation: formation.ministry_category_id.id == category.id)
            if institution:
                category_name = category.name
                institutions = ', '.join(institution.mapped('name'))
                data.append([category_name, institutions])
        unknown_health_center = health_center.filtered(lambda health: health.ministry_category_id.id == False)
        if unknown_health_center:
            institutions = ', '.join(unknown_health_center.mapped('name'))
            data.append(['Unknown', institutions])
        if data:
            return data
        return False

    @api.model
    def _get_report_values(self, docids, data=None):
        Report = self.env['ir.actions.report']
        report = Report._get_report_from_name('cristo.report_ecc_diocese_profile')
        docargs = {
            'doc_ids': self.id,
            'doc_model': 'res.ecclesia.diocese',
            'docs': self.env['res.ecclesia.diocese'].browse(docids),
            'data': data,
            'get_priest_count': self.get_priest_count,
            'get_diocesen_priest_count': self.get_diocesen_priest_count,
            'get_religious_priest_count': self.get_religious_priest_count,
            'get_congregation_sister_count': self.get_congregation_sister_count,
            'get_congregation_brother_count': self.get_congregation_brother_count,
            'get_congregation_father_count': self.get_congregation_father_count,
            'get_institution_count': self.get_institution_count,
            'get_deputy_bishop_detail': self.get_deputy_bishop_detail,
            'get_formation_institution_detail' : self.get_formation_institution_detail,
            'get_health_center_detail':self.get_health_center_detail,
        }
        return docargs