# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


GENERATE_YEAR = []
cur_year = datetime.now().year
while(cur_year >= 1800):
    GENERATE_YEAR.append((str(cur_year), str(cur_year)))
    cur_year -= 1

class ResReligiousInstitute(models.Model):
    _inherit = 'res.religious.institute'
    
    @api.depends('institute_category_ids')
    def _compute_ministry_statistics(self):
        self.is_formation = False; self.is_education = False; self.is_health_care = False; self.is_welfare = False; self.is_retreat_animation = False; self.is_pastoral = False; self.is_media = False; self.is_ecclesiastical = False;
        for institute_category_id in self.institute_category_ids:
            if institute_category_id.code == 'EDU':
                self.is_education = True
            if institute_category_id.code == 'ECC':
                self.is_ecclesiastical = True
            if institute_category_id.code == 'FOR':
                self.is_formation = True
            if institute_category_id.code == 'HC':
                self.is_health_care = True
            if institute_category_id.code == 'ME':
                self.is_media = True 
            if institute_category_id.code == 'PAS':
                self.is_pastoral = True
            if institute_category_id.code == 'RA':
                self.is_retreat_animation = True
            if institute_category_id.code == 'WF':
                self.is_welfare = True 
            
    cri_code = fields.Char(string="CRI Code")
    member_statistics_ids = fields.One2many('member.statistics', 'institute_id', string="Member Statistics")
    education_statistics_ids = fields.One2many('education.statistics', 'institute_id', string="Education Statistics")
    ecclesiastical_statistics_ids = fields.One2many('ecclesiastical.statistics', 'institute_id', string="Ecclesiastical Statistics")
    formation_statistics_ids = fields.One2many('formation.statistics', 'institute_id', string="Formation Statistics")
    healthcare_statistics_ids = fields.One2many('healthcare.statistics', 'institute_id', string="Health Care Statistics")
    media_statistics_ids = fields.One2many('media.statistics', 'institute_id', string="Media Statistics")
    pastoral_statistics_ids = fields.One2many('pastoral.statistics', 'institute_id', string="Pastoral Statistics")
    retreat_animation_statistics_ids = fields.One2many('retreat.animation.statistics', 'institute_id', string="Retreat Animation Statistics")
    welfare_statistics_ids = fields.One2many('welfare.statistics', 'institute_id', string="Welfare Statistics")
    
    is_education = fields.Boolean(compute='_compute_ministry_statistics', string='Is Education?')
    is_ecclesiastical = fields.Boolean(compute='_compute_ministry_statistics', string='Is Ecclesiastical?')
    is_formation = fields.Boolean(compute='_compute_ministry_statistics', string='Is Formation?')
    is_health_care = fields.Boolean(compute='_compute_ministry_statistics', string='Is Health Care?')
    is_media = fields.Boolean(compute='_compute_ministry_statistics', string='Is Media?')
    is_pastoral = fields.Boolean(compute='_compute_ministry_statistics', string='Is Pastoral?')
    is_retreat_animation = fields.Boolean(compute='_compute_ministry_statistics', string='Is Retreat and Animation?')
    is_welfare = fields.Boolean(compute='_compute_ministry_statistics', string='Is Welfare?')
    
class ResReligiousProvince(models.Model):
    _inherit = 'res.religious.province'
    
    @api.depends('institute_category_ids')
    def _compute_ministry_statistics(self):
        self.is_formation = False; self.is_education = False; self.is_health_care = False; self.is_welfare = False; self.is_retreat_animation = False; self.is_pastoral = False; self.is_media = False; self.is_ecclesiastical = False;
        for institute_category_id in self.institute_category_ids:
            if institute_category_id.code == 'EDU':
                self.is_education = True
            if institute_category_id.code == 'ECC':
                self.is_ecclesiastical = True
            if institute_category_id.code == 'FOR':
                self.is_formation = True
            if institute_category_id.code == 'HC':
                self.is_health_care = True
            if institute_category_id.code == 'ME':
                self.is_media = True 
            if institute_category_id.code == 'PAS':
                self.is_pastoral = True
            if institute_category_id.code == 'RA':
                self.is_retreat_animation = True
            if institute_category_id.code == 'WF':
                self.is_welfare = True 
    
    cri_code = fields.Char(string="CRI Code")
    institute_category_ids = fields.Many2many('res.institution.category', string="Main forms of Ministry")
    member_statistics_ids = fields.One2many('member.statistics', 'province_id', string="Member Statistics")
    education_statistics_ids = fields.One2many('education.statistics', 'province_id', string="Education Statistics")
    ecclesiastical_statistics_ids = fields.One2many('ecclesiastical.statistics', 'province_id', string="Ecclesiastical Statistics")
    formation_statistics_ids = fields.One2many('formation.statistics', 'province_id', string="Formation Statistics")
    healthcare_statistics_ids = fields.One2many('healthcare.statistics', 'province_id', string="Health Care Statistics")
    media_statistics_ids = fields.One2many('media.statistics', 'province_id', string="Media Statistics")
    pastoral_statistics_ids = fields.One2many('pastoral.statistics', 'province_id', string="Pastoral Statistics")
    retreat_animation_statistics_ids = fields.One2many('retreat.animation.statistics', 'province_id', string="Retreat Animation Statistics")
    welfare_statistics_ids = fields.One2many('welfare.statistics', 'province_id', string="Welfare Statistics")
    
    is_education = fields.Boolean(compute='_compute_ministry_statistics', string='Is Education?')
    is_ecclesiastical = fields.Boolean(compute='_compute_ministry_statistics', string='Is Ecclesiastical?')
    is_formation = fields.Boolean(compute='_compute_ministry_statistics', string='Is Formation?')
    is_health_care = fields.Boolean(compute='_compute_ministry_statistics', string='Is Health Care?')
    is_media = fields.Boolean(compute='_compute_ministry_statistics', string='Is Media?')
    is_pastoral = fields.Boolean(compute='_compute_ministry_statistics', string='Is Pastoral?')
    is_retreat_animation = fields.Boolean(compute='_compute_ministry_statistics', string='Is Retreat and Animation?')
    is_welfare = fields.Boolean(compute='_compute_ministry_statistics', string='Is Welfare?')
    

# For Congregation and Province Use
class MemberStatistics(models.Model):
    _name = 'member.statistics'
    _description = "Member Statistics"
    
    @api.depends('temporary_count','perpetual_count','novices_count')
    def _compute_total_count(self):
        self.total = False
        for rec in self:
            rec.total = rec.temporary_count + rec.perpetual_count + rec.novices_count
    
    year = fields.Selection(GENERATE_YEAR, string="Year", required=True)
    temporary_count = fields.Integer(string="Temporary")
    perpetual_count = fields.Integer(string="Perpetual")
    novices_count = fields.Integer(string="Novices")
    total = fields.Integer(compute='_compute_total_count', string="Total")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    province_id = fields.Many2one('res.religious.province', string="Province")
    
# For Congregation and Province Use
class EducationStatistics(models.Model):
    _name = 'education.statistics'
    _description = "Education Statistics"
    
    year = fields.Selection(GENERATE_YEAR, string="Year", required=True)
    type_id = fields.Many2one('res.institution.category', string="Type of Institution", required=True)
    institution_count = fields.Integer(string="#Institutions")
    student_count = fields.Integer(string="#Students")
    staff_count = fields.Integer(string="#Staff")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    province_id = fields.Many2one('res.religious.province', string="Province")
    
# For Congregation and Province Use
class EcclesiasticalStatistics(models.Model):
    _name = 'ecclesiastical.statistics'
    _description = "Ecclesiastical Statistics"
    
    year = fields.Selection(GENERATE_YEAR, string="Year", required=True)
    type_id = fields.Many2one('res.institution.category', string="Type of Institution", required=True)
    institution_count = fields.Integer(string="#Institutions")
    beneficiary_count = fields.Integer(string="#Beneficiaries")
    staff_count = fields.Integer(string="#Staff")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    province_id = fields.Many2one('res.religious.province', string="Province")
    
# For Congregation and Province Use
class FormationStatistics(models.Model):
    _name = 'formation.statistics'
    _description = "Formation Statistics"
    
    year = fields.Selection(GENERATE_YEAR, string="Year", required=True)
    type_id = fields.Many2one('res.institution.category', string="Type of Institution", required=True)
    institution_count = fields.Integer(string="#Institutions")
    members_count = fields.Integer(string="#Members")
    staff_count = fields.Integer(string="#Staff")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    province_id = fields.Many2one('res.religious.province', string="Province")
    
# For Congregation and Province Use
class HealthCareStatistics(models.Model):
    _name = 'healthcare.statistics'
    _description = "Health Care Statistics" 
    
    year = fields.Selection(GENERATE_YEAR, string="Year", required=True)
    type_id = fields.Many2one('res.institution.category', string="Type of Institution", required=True)
    institution_count = fields.Integer(string="#Institutions")
    avg_patient_count = fields.Integer(string="Avg. #Patients per day")
    out_patient_count = fields.Integer(string="#Out Patient")
    bed_strength_count = fields.Integer(string="#Bed Strength")
    staff_count = fields.Integer(string="#Staff")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    province_id = fields.Many2one('res.religious.province', string="Province")

# For Congregation and Province Use  
class MediaStatistics(models.Model):
    _name = 'media.statistics'
    _description = "Media Statistics" 
    
    year = fields.Selection(GENERATE_YEAR, string="Year", required=True)
    type_id = fields.Many2one('res.institution.category', string="Type of Institution", required=True)
    institution_count = fields.Integer(string="#Institutions")
    staff_count = fields.Integer(string="#Staff")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    province_id = fields.Many2one('res.religious.province', string="Province")

# For Congregation and Province Use   
class PastoralStatistics(models.Model):
    _name = 'pastoral.statistics'
    _description = "Pastoral Statistics" 
    
    year = fields.Selection(GENERATE_YEAR, string="Year", required=True)
    type_id = fields.Many2one('res.institution.category', string="Type of Institution", required=True)
    institution_count = fields.Integer(string="#Institutions")
    family_count = fields.Integer(string="#Families")
    members_count = fields.Integer(string="#Members")
    baptism_count = fields.Integer(string="#Bapisms")
    confirmation_count = fields.Integer(string="#Confirmations")
    marriage_count = fields.Integer(string="#Marriages")
    association_count = fields.Integer(string="#Associations")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    province_id = fields.Many2one('res.religious.province', string="Province")
    
# For Congregation and Province Use
class RetreatAnimationStatistics(models.Model):
    _name = 'retreat.animation.statistics'
    _description = "Retreat Animation Statistics" 
    
    year = fields.Selection(GENERATE_YEAR, string="Year", required=True)
    type_id = fields.Many2one('res.institution.category', string="Type of Institution", required=True)
    institution_count = fields.Integer(string="#Institutions")
    beneficiary_count = fields.Integer(string="#Beneficiaries")
    staff_count = fields.Integer(string="#Staff")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    province_id = fields.Many2one('res.religious.province', string="Province")
    
# For Congregation and Province Use
class WelfareStatistics(models.Model):
    _name = 'welfare.statistics'
    _description = "Welfare Statistics" 
    
    year = fields.Selection(GENERATE_YEAR, string="Year", required=True)
    type_id = fields.Many2one('res.institution.category', string="Type of Institution", required=True)
    institution_count = fields.Integer(string="#Institutions")
    beneficiary_count = fields.Integer(string="#Beneficiaries")
    staff_count = fields.Integer(string="#Staff")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    province_id = fields.Many2one('res.religious.province', string="Province")
    
    