# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import expression
import base64
import tempfile
import os, sys, time
import subprocess
import imghdr
from odoo.http import request
import odoo

class PhysicalStatus(models.Model):
    _name = "res.member.physical.status"
    _description = 'Member Physical Status'
    _order = 'name'
    
    name = fields.Char(string="Name", required=True)
    
class Citizenship(models.Model):
    _name = "res.member.citizenship"
    _description = "Member Citizenship Status"
    
    name = fields.Char(string="Name", required=True)
    
class BloodGroup(models.Model):
    _name = "res.blood.group"
    _description = "Member Blood Group"
    _order = 'name'
    
    name = fields.Char(string="Name", required=True)

class MaritalStatus(models.Model):
    _name = "res.member.marital.status"
    _description = " Member Marital Status"
    
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')], string="Gender")
    
class Relationship(models.Model):
    _name = "res.member.relationship"
    _description = "Member Relationship"
    
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')], string="Gender")

class Occupation(models.Model):
    _name = 'res.occupation'
    _description = " Occupations"
    
    name = fields.Char(string="Name", required=True)
    
class HouseType(models.Model):
    _name = "res.house.type"
    _description = "House Type"
    
    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence")

class ResStudyLevel(models.Model):
    _name = 'res.study.level'
    _description = "Study Level"
    
    name = fields.Char(string="Name", required=True)
    study_level_code = fields.Char(string="Code", required=True, size=3)
    sequence = fields.Integer(string="Sequence")
    study_level_ids = fields.Many2many('study.level.member', string="Study Level hide for")
    
class ResMemberProgram(models.Model):
    _name = 'res.member.program'
    _description = "Member Program"
    
    name = fields.Char(string="Name", required=True)
    abbreviation = fields.Char(string="Abbreviation")
    study_level_id = fields.Many2one('res.study.level', string="Study Level")
    
  
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', operator, name), ('abbreviation', operator, name)]
        rec = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(rec).with_user(name_get_uid))        

class Religion(models.Model):
    _name = "res.member.religion"
    _description = "Member Religion"
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    
class MemberRole(models.Model):
    _name = "res.member.role"
    _description = "Member Role"
    
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('transgender', 'Transgender')], string="Gender")
    abbreviation = fields.Char(string="Abbreviation")
    color = fields.Integer(string="Color Index")
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
#         if operator == 'ilike' and not (name or '').strip():
#             domain = []
        if self._context.get('search_all_role',False):
            domain = ['|', ('name', operator, name), ('abbreviation', operator, name)]
        else:
            domain = ['|', ('name', '=ilike', name), ('abbreviation', operator, name)]
        rec = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(rec).with_user(name_get_uid))
    
class Patron(models.Model):
    _name = "res.patron"
    _description = "Patron"
    
    name = fields.Char(string="Name", required=True)
    feast_date = fields.Date(string="Feast Date")
    
class InstitutionCategory(models.Model):
    _name = "res.institution.category"
    _description = "Institution Category"
    _order = "name asc"
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    parent_id = fields.Many2one("res.institution.category", string="Parent")
    color = fields.Integer(string="Color Index")
    
class CoreDisiplines(models.Model):
    _name = "res.core.disiplines"
    _description = "Core Disiplines"
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")

class Rite(models.Model):
    _name = "res.rite"
    _description = "Rite"
    
    name = fields.Char(string="Name", required=True)
    
class District(models.Model):
    _name = "res.state.district"
    _description = "District"
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    state_id = fields.Many2one('res.country.state', string="State")    

class DiseaseDisorder(models.Model):
    _name = 'res.disease.disorder'
    _description = "Disease Disorder"
    
    name = fields.Char(string="Name", required=True)
    
class FormationStages(models.Model):
    _name = "res.formation.stage"
    _description = "Formation Stage"
    
    name = fields.Char(string="Name", required=True)
    institute_ids = fields.Many2many("res.religious.institute", string="Congregation")
    
class Languages(models.Model):
    _name = "res.languages"
    _description = "Languages"
    _order = 'name'
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    enable_medium = fields.Boolean(string="Enable Medium")

class MainCategory(models.Model):
    _name = "res.main.category"
    _description = "Main Category"
    _order = "sequence asc"
    
    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    
class PartnerTitle(models.Model):
    _inherit = "res.partner.title"
    _description = "Partner Title"
    
#     member_type = fields.Selection([('member','Member'),('bishop','Bishop'),('priest','Priest'),('deacon','Deacon'),('lay_brother','Lay Brother'),('brother','Brother'),('sister','Sister'),('junior_sister', 'Junior Sister'),('novice','Novice')], string="Member Type")
    name = fields.Char(string="Title")
    shortcut = fields.Char(string="Abbreviation")
    for_bishop = fields.Boolean(string="For Bishop")
    for_priest = fields.Boolean(string="For Priest")
    for_brother = fields.Boolean(string="For Brother")
    for_deacon = fields.Boolean(string="For Deacon")
    for_sister = fields.Boolean(string="For Sister")
    for_novice = fields.Boolean(string="For Novice")
    for_member = fields.Boolean(string="For Member")
       
class PublicationType(models.Model):
    _name = "publication.type"
    _description = "Publication Type"
    
    name = fields.Char(string="Name")
    
class StudyLevelMember(models.Model):
    _name = "study.level.member"
    _description = "Study Level Member"
    
    name = fields.Char(string="Name")

class RenewalDocumentType(models.Model):
    _name = "renewal.doc.type"
    _description = "Renewal Document Type"
    
    name = fields.Char(string="Name",required=True)
    mail_template_id = fields.Many2one('mail.template',string="Mail Template")
    is_member = fields.Boolean(string="Is Member?")
    is_org = fields.Boolean(string="Is Org?")

class EntityNature(models.Model):
    _name = "entity.nature"
    _description = "Entity Nature"

    name = fields.Char(string="Name", required=True)

class FiscalYear(models.Model):
    _name = "fiscal.year"
    _description = "Fiscal Year"

    name = fields.Char(string="Name", required=True)
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    
class AnniversaryType(models.Model):
    _name = "anniversary.type"
    _description = "Anniversary Type"

    name = fields.Char(string="Name", required=True)
    is_priest = fields.Boolean(string="Is Priest")
    is_sister = fields.Boolean(string="Is Sister")
    is_layperson = fields.Boolean(string="Is Layperson")
    
class InstitutionBoard(models.Model):
    _name = "institution.board"
    _description = "Institution Board"

    name = fields.Char(string="Name", required=True)
    
    
class base64_imageurl(models.TransientModel):
    _name = 'base64.imageurl'
        
    def base64_url(self, base64_str):
        if base64_str:
            addons_path = os.path.abspath(os.path.join(odoo.tools.config['root_path'], '../addons'))
            data = base64.decodestring(bytes(base64_str, 'utf-8'))
            with tempfile.NamedTemporaryFile(dir = addons_path +'/web/static/src/img/', delete=False, mode='wb', suffix=self.get_img_extension(data)) as fobj:
                fname = fobj.name
                fobj.write(data)
                image = fname.split("/")
            subprocess.call(['chmod', '-R', '755', addons_path +'/web/static/src/img/'])
            return request.httprequest.host_url+"web/static/src/img/"+ image[len(image) - 1]
        
    def get_img_extension(self, data):
        img_ext = ""
        for tf in imghdr.tests:
            ext = tf(data, None)
            if ext:
                img_ext = "." + ext
                break 
            if data[0:4] == b'%PDF':
                img_ext = "%s.pdf" % ext
                break 
            if data[0:4] == b'PK\x03\x04':
                img_ext = "%s.docx" % ext
                break
        return img_ext
    
    def user_role(self):
        if self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            user = "Admin(BSA)"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
            user = "Congregation"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
            user = "Religious Province"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
            user = "House/Community"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            user = "Institution"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_individual'):
            user = "Member"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_ec_province'):
            user = "Ecclesia Province"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_diocese'):
            user = "Diocese"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_vicarate'):
            user = "Vicarate"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_parish_ms'):
            user = "Parish/Mission"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_bcc'):
            user = "BCC"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_family'):
            user = "Family"
            return user
        elif self.user_has_groups('cristo.group_role_cristo_apostolic_association'):
            user = "Association"
            return user
            
class ResMonth(models.Model):
    _name = "res.month"
    _description = "Month"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    sequence = fields.Integer(string="Sequence")
        

          
   
   
            
   
    
