# -*- coding: utf-8 -*-
import base64

from odoo import fields, api, models, _
from datetime import datetime,date,timedelta
from odoo.addons.cristo.tools import cris_tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from lxml import etree
import json
from odoo.addons.cristo.models.res_common import Partner_Excluded_Fields, Mail_Excluded_Fields

YEAR = []
current_year = datetime.now().year
while(current_year >= 1900):
    YEAR.append((str(current_year), str(current_year)))
    current_year -= 1

DAYS = []
for d in range(1, 32):
    DAYS.append((str(d),str(d)))
    
MONTHS = [
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]
Member_Excluded_Fields = ['remembrance_ids','attachment_ids','is_dob_or_age','aadhar_proof','pan_proof','voter_proof','passport_proof','store_name','member_code',
                          'award_recognition_ids','formation_ids','holyorder_ids','house_member_ids','member_education_ids','member_health_ids','profession_ids','publication_ids',
                          'religious_family_ids','statutory_renewal_ids']
Excluded_Fields = Partner_Excluded_Fields + Mail_Excluded_Fields + Member_Excluded_Fields

proof_file_extensions = ['jpeg','jpg','png','pdf']

class Member(models.Model):
    _name = 'res.member'
    _description = "Member"
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading','mail.thread','partner.clear.cache','attachment.size']
    _custom_filter_exclude_fields = Excluded_Fields
#     _custom_filter_view_fields = ['name','age','unique_code','last_name','parish_id','membership_type']
#     _custom_filter_extra_kwargs = {'name':{'string':'Member Name'},'age':{'string':'Member Age'}}
    
    @api.model
    def default_get(self, fields):
        data = super(Member, self).default_get(fields)
        user = self.env.user
        if user.institute_id.institute_type in ['priest','lay_brother','brother']:
            data['gender'] = 'male'
        elif user.institute_id.institute_type in ['sister_apostolic','sister_contemplative']:
            data['gender'] = 'female'
        main_category = self.env['res.main.category'].search([('code', '=', 'MR')], limit=1)
        membership_type = self._context.get('membership_type')
        if membership_type:
            data['membership_type'] = membership_type
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            data['membership_type'] = "RE"
        religion_id = self.env['res.member.religion'].search([('code','=', 'CAT')], limit=1)
        passport_country_id = self.env['res.country'].search([('code', '=', 'IN')], limit=1)
        citizenship_id = self.env['res.member.citizenship'].search([('name', '=', 'Indian')], limit=1)
        data['religion_id'] = religion_id.id
        data['passport_country_id'] = passport_country_id.id
        data['citizenship_id'] = citizenship_id.id
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'person'
        data['institute_id'] = self.env.user.institute_id.id
        data['rel_province_id'] = self.env.user.rel_province_id.id or self._context.get('default_rel_province_id')
        return data
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Member, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='gender']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='membership_type']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
            
#             search_view_id = self.env.ref('cristo.view_res_member_all_search')
#             if view_type == 'search' and view_id == search_view_id.id:
#                 for node in doc.xpath("//filter[@name='female']"):
#                     if node.get('modifiers'):
#                         modifiers = json.loads(node.get('modifiers'))
#                         modifiers['invisible'] = True
#                         node.set("modifiers", json.dumps(modifiers))
                        
        if self.user_has_groups('cristo.group_role_cristo_religious_province'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_province_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_province_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_zone_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='community_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_vicarate'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='diocese_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='vicariate_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_parish_ms'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='diocese_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='vicariate_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='parish_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_individual'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_province_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_zone_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='community_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_parish_ms'):
            for view in doc.xpath("//" + view_type):
                bishop_form_view_id = self.env.ref('cristo.view_res_member_common_form').id
                bishop_tree_view_id = self.env.ref('cristo.view_res_member_common_tree').id
                if view_id in [bishop_form_view_id,bishop_tree_view_id]:
                    view.attrib['create'] = 'false'
                    view.attrib['delete'] = 'false'
                    view.attrib['import'] = 'false'
                    view.attrib['edit'] = 'false'
                    
#         if self._context.get('membership_type', False) == 'LT': 
#             if view_type in ['tree','form']:
#                 toolbar_print = res['toolbar'] and res['toolbar']['print'] and res['toolbar']['print']
#                 res['toolbar']['print'] = list(filter(lambda record: record['report_file'] not in ['member_profession_details','member_formation_details','member_holyorder_details','member_publication_details'], toolbar_print))                               
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    def get_formview_action(self, access_uid=None):
        """ Override this method in order to redirect many2one towards the right form view depending on access_uid """
        res = super(Member, self).get_formview_action(access_uid=access_uid)
        view_id = self.env.ref('cristo.view_res_member_all_form').id
        res['views'] = [(view_id, 'form')]
        return res
    
    def check_binary_data(self,binary):
        if (len(binary) / 1024 / 1024) > 1:
            raise UserError(_("The maximum upload size is 1 MB."))

    @api.constrains('aadhar_proof','store_name')
    def _validate_aadhar_proof(self):
        if self.aadhar_proof:
            binary = base64.b64decode(self.aadhar_proof or "")
            self.check_binary_data(binary)
            if self.store_name:
                file = self.store_name.split('.')[1:]
                if file and file[0] not in proof_file_extensions:
                    raise UserError(_("Sorry! You can upload only the specified format files such as 'jpeg','jpg','png','pdf'."))

    @api.onchange('aadhar_proof')
    def _validate_binary_file(self):
        if self.aadhar_proof :
            self._validate_aadhar_proof()

    @api.constrains('pan_proof')
    def _validate_pan_proof(self):
        if self.pan_proof :
            binary = base64.b64decode(self.pan_proof or "")
            self.check_binary_data(binary)
            if self.pan_proof_name:
                file = self.pan_proof_name.split('.')[1:]
                if file and file[0] not in proof_file_extensions:
                    raise UserError(_("Sorry! You can upload only the specified format files such as 'jpeg','jpg','png','pdf'."))

    @api.onchange('pan_proof')
    def _check_pan_proof_file(self) :
        if self.pan_proof :
            self._validate_pan_proof()

    @api.constrains('passport_proof')
    def _validate_passport_proof(self):
        if self.passport_proof:
            binary = base64.b64decode(self.passport_proof or "")
            self.check_binary_data(binary)
            if self.passport_proof_name:
                file = self.passport_proof_name.split('.')[1:]
                if file and file[0] not in proof_file_extensions:
                    raise UserError(_("Sorry! You can upload only the specified format files such as 'jpeg','jpg','png','pdf'."))

    @api.onchange('passport_proof')
    def _check_passport_file(self) :
        if self.passport_proof :
            self._validate_passport_proof()

    @api.constrains('voter_proof')
    def _validate_voter_proof(self):
        if self.voter_proof :
            binary = base64.b64decode(self.voter_proof or "")
            self.check_binary_data(binary)
            if self.voter_proof_name:
                file = self.voter_proof_name.split('.')[1:]
                if file and file[0] not in proof_file_extensions:
                    raise UserError(_("Sorry! You can upload only the specified format files such as 'jpeg','jpg','png','pdf'."))

    @api.onchange('voter_proof')
    def _check_voter_file(self) :
        if self.voter_proof :
            self._validate_voter_proof()

    @api.constrains('death_certificate')
    def _validate_death_certificate(self):
        if self.death_certificate :
            binary = base64.b64decode(self.death_certificate or "")
            self.check_binary_data(binary)
            if self.death_certificate_name:
                file = self.death_certificate_name.split('.')[1:]
                if file and file[0] not in proof_file_extensions:
                    raise UserError(_("Sorry! You can upload only the specified format files such as 'jpeg','jpg','png','pdf'."))

    @api.onchange('death_certificate')
    def _check_death_certificate_file(self) :
        if self.death_certificate :
            self._validate_death_certificate()

    @api.constrains('attachment_ids')
    def _check_attachment_size(self):
        self.env['ir.attachment']._check_size(self.attachment_ids)
        
    @api.constrains('dob')
    def _validate_dob(self):
        if self.dob:
            cris_tools.future_date_validation(self.dob)
            
    @api.constrains('bapt_date')
    def _validate_futuristic_bapt_date(self):
        if self.bapt_date:
            cris_tools.future_date_validation(self.bapt_date,field_name="Baptism date")
            
    @api.constrains('dob','bapt_date','mrg_date')
    def _validate_bapt_date(self):
        if self.bapt_date and self.dob:
            if self.bapt_date < self.dob:
                raise UserError(_("Baptism date should not be lesser than Date of Birth"))
        if self.mrg_date and self.dob:
            if self.mrg_date < self.dob:
                raise UserError(_("Marriage date should not be lesser than Date of Birth"))
            
    @api.constrains('fhc_date')
    def _validate_fhc_date(self):
        if self.fhc_date:
            cris_tools.future_date_validation(self.fhc_date,field_name="First Holy Communion date")
            
    @api.constrains('fhc_date','bapt_date','dob')
    def _validate_fhc_and_bapt_dates(self):
        if self.fhc_date and self.bapt_date:
            if self.fhc_date < self.bapt_date:
                raise UserError(_("First Holy Communion date should not be lesser than Baptism Date."))
        if self.fhc_date and self.dob:
            if self.fhc_date < self.dob:
                raise UserError(_("First Holy Communion date should not be lesser than Date of Birth"))   
 
    @api.constrains('cnf_date')
    def _validate_cnf_date(self):
       if self.cnf_date:
           cris_tools.future_date_validation(self.cnf_date,field_name="Confirmation Date")
    
    @api.constrains('bapt_date','cnf_date','dob')
    def _validate_bapt_and_cnf_date(self):
        if self.bapt_date and self.cnf_date:
            if self.bapt_date > self.cnf_date:
                raise UserError(_("Confirmation date should not be lesser then Baptism date."))
        if self.cnf_date and self.dob:
            if self.cnf_date < self.dob:
                raise UserError(_("Confirmation date should not be lesser than Date of Birth"))   
            
    @api.constrains('death_date')
    def _validate_future_death_date(self):
        if self.death_date:
            cris_tools.future_date_validation(self.death_date,field_name="Death Date")
            
    @api.constrains('death_date','dob')
    def _validate_death_date(self):
        if self.death_date and self.dob:
            if self.death_date < self.dob:
                raise UserError(_("Death date should not be lesser than Date of Birth."))
            
    @api.constrains('death_date','burial_date')
    def _validate_death_date(self):
        if self.death_date and self.burial_date:
            if self.death_date > self.burial_date.date():
                raise UserError(_("Death date should not be greater than Burial Date."))
            
    @api.onchange('parish_district_id')
    def _onchange_parish_district_id(self):
        if self.parish_district_id:
            self.parish_state_id = self.parish_district_id.state_id.id
                
    @api.onchange('parish_state_id')
    def _onchange_parish_state_id(self):
        if self.parish_state_id:
            self.parish_country_id = self.parish_state_id.country_id.id
            
    @api.depends('profession_ids')        
    def _compute_profession_date(self):
        self.profession_date = False
        for rec in self:
            if rec.profession_ids:
                profession = rec.profession_ids.filtered(lambda prof: prof.type == 'first')
                if profession:
                    rec.profession_date = profession[-1].profession_date
    
    @api.depends('name','last_name','title')
    def _compute_member_full_name(self):
        for mem in self:
            mem.member_name = False
            name = (mem.title.name+' '+mem.name) if mem.title else mem.name
            if name:
                name += ' '+mem.last_name if mem.last_name else ''
                mem.member_name = name
                
    @api.constrains('member_type')
    def _validate_member_type(self):
        if self.member_type:            
            user = self.env.user
            if user.institute_id.institute_type in ['priest','lay_brother','brother']:
                if self.member_type in ['sister','junior_sister']:
                    raise UserError(_("Sorry! please select appropriate member type."))
            elif user.institute_id.institute_type in ['sister_apostolic','sister_contemplative']:
                if self.member_type in ['bishop','priest','lay_brother','brother','deacon']:
                    raise UserError(_("Sorry! please select appropriate member type."))

    @api.constrains('membership_type', 'member_type')
    def _validate_membership_member_type(self):
        for rec in self:
            if self.user_has_groups('cristo.group_role_cristo_diocese') or self.user_has_groups('cristo.group_role_cristo_vicarate') or self.user_has_groups('cristo.group_role_cristo_parish_ms'):
                if rec.membership_type == 'LT' and not rec.member_type == 'member':
                    raise ValidationError(_("Sorry! please select appropriate member type."))
                if rec.membership_type == 'SE' and not rec.member_type in ['bishop', 'priest', 'deacon', 'brother']:
                    raise ValidationError(_("Sorry! please select appropriate member type."))
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_religious_house'):
                if rec.membership_type == 'RE' and not rec.member_type in ['bishop', 'priest', 'deacon', 'lay_brother','brother', 'sister', 'junior_sister','novice']:
                    raise ValidationError(_("Sorry! please select appropriate member type."))
    
    @api.constrains('is_family_head', 'family_id')
    def _validate_is_family_head(self):
        fam_member_ids = self.env['res.family'].search([('id','=',self.family_id.id)]).mapped('child_ids')
        fam_head_ids = fam_member_ids.filtered(lambda member:member.is_family_head == True)
        if len(fam_head_ids) > 1:
            raise UserError(_("Family Head is already assigned."))
        
    @api.constrains('membership_type','family_id')
    def _validate_is_membership_type_with_family_name(self):   
        if self.membership_type == 'LT':
            if not self.family_id:
                raise UserError(_("Please Choose Family Name."))
        
    partner_id = fields.Many2one('res.partner', string="Contacts", required=True, ondelete="cascade")
    member_name = fields.Char(compute="_compute_member_full_name",string="Member Full Name",store=True)
    financial_support = fields.Char(string="Financial Support")
    monthly_income = fields.Float(string="Monthly Income")
    unique_code = fields.Char(string="UID (Aadhar/Passport)", help="UID (Aadhaar Card No)/Passport for non Indians", size=14,tracking=True)
    last_name = fields.Char(string="Last Name",tracking=True)
    family_id = fields.Many2one('res.family',string="Family", tracking=True)
    bcc_family = fields.Many2one(related="family_id.parish_bcc_id",string="Bcc",store=True)
    parish_id = fields.Many2one('res.parish',string="Parish")
    sub_station_id = fields.Many2one('res.parish.sub.station',string="Sub Station")
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate")
    bcc_id = fields.Many2one('res.parish.bcc', string="Basic Christian Community(BCC)")
    zone_id = fields.Many2one('res.ecclesia.zone', string="Zone")
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese")
    province_id = fields.Many2one('res.ecclesia.province', string="Ecc Province")
    religion_id = fields.Many2one('res.member.religion',required=True, ondelete="restrict", string="Religion")
    alias_name = fields.Char(string="Alias/Called As")
    gender = fields.Selection([('male','Male'),('female','Female'),('transgender','Transgender')],string="Gender")
    membership_type = fields.Selection([('LT','Lay Person'),('RE','Religious'),('SE','Secular Clergy')],string="Membership Type")
    living_status = fields.Selection([('yes','Yes'),('no','No')],string="Living Status", default='yes')
    marital_status_id = fields.Many2one('res.member.marital.status',string="Marital Status")
    blood_group_id = fields.Many2one('res.blood.group',string="Blood Group")
    mother_tongue_id = fields.Many2one('res.languages',string="Mother Tongue")
    occupation_status = fields.Selection([('working','Working'),('not working','Not Working'),('retired','Retired'),('other','Other')])
    occupation_id = fields.Many2one('res.occupation',string="Occupation")
    occupation_type  = fields.Selection([('govt','Government'),('pvt','Private'),('self','Self')],string="Occupation Type")
    relationship_id = fields.Many2one('res.member.relationship', string="Relationship")
    dob = fields.Date(string="DOB")
    is_dob_or_age = fields.Selection([('dob','DOB'),('age','Age')],default="dob", string="Is DOB/Age?")
    age = fields.Integer(string="Age")
    is_family_head = fields.Boolean(string="Is Family Head?")
    is_parish_member = fields.Selection([('yes','Yes'),('no','No')], string="Is Parish Member?", default='yes')
    inactive_reason = fields.Char(string="Membership Rationale")
    marriage_parish_id = fields.Many2one('res.parish', string="Parish of Marriage")
    member_code = fields.Char(string="Member #")
    use_parent_address = fields.Boolean(string="Use Family Address")
    present_diocese_id = fields.Many2one('res.ecclesia.diocese',string="Present Diocese")
    bapt_diocese_id = fields.Many2one('res.ecclesia.diocese',string="Diocese of Baptism")
    fhc_diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese of Communion")
    cnf_diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese of Confirmation")
    marriage_diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese of Marriage")
    physical_status_id = fields.Many2one('res.member.physical.status',string="Physical Status",default=lambda self: self.env['res.member.physical.status'].search([('name','=','Normal')],limit=1))
    citizenship_id = fields.Many2one('res.member.citizenship',string="Citizenship")
    member_education_ids = fields.One2many('res.member.education','member_id',string="Education")
    name_in_regional_language = fields.Char(string="Name in Regional Language")
    baptism_parish_id = fields.Many2one('res.parish',string="Parish of Baptism")
    baptism_diocese_id = fields.Many2one(related="baptism_parish_id.diocese_id", string="Bapt Diocese")
    bapt_date =  fields.Date(string="Date of Baptism")
    cnf_parish_id = fields.Many2one('res.parish',string="Parish of Confirmation")
    cnf_diocese_id = fields.Many2one(related="cnf_parish_id.diocese_id", string="CNF Diocese")
    cnf_date = fields.Date(string="Date of Confirmation")
    fhc_parish_id = fields.Many2one('res.parish',string="Parish of First Holy Communion")
    fhc_diocese_id = fields.Many2one(related="fhc_parish_id.diocese_id", string="FHC Diocese")
    fhc_date = fields.Date(string="Date of First Holy Communion")
    mrg_parish_id = fields.Many2one('res.parish', string="Parish of Marriage")
    mrg_diocese_id = fields.Many2one(related="mrg_parish_id.diocese_id", string="MRG Diocese")
    mrg_date = fields.Date(string="Date of Marriage")
    death_parish_id = fields.Many2one('res.parish', string="Parish of Death")
    death_date = fields.Date(string="Date of Death")
    death_certificate_name = fields.Char()
    death_certificate = fields.Binary(string="Upload Death Certificate")
    profession_ids = fields.One2many('res.profession', 'member_id', string="Profession")
    formation_ids = fields.One2many('res.formation', 'member_id', string="Formation")
    holyorder_ids = fields.One2many('res.holyorder', 'member_id', string="Holy Order")
    religious_family_ids = fields.One2many('res.religious.family', 'member_id', string="Family")
    member_health_ids = fields.One2many('res.member.health','member_id',string="Member Health")
    publication_ids = fields.One2many('res.publication','member_id',string="Publication")
    award_recognition_ids = fields.One2many('res.award.recognition','member_id',string="Award and Recognition")
    native_place = fields.Char(string="Native Place")
    native_district_id = fields.Many2one('res.state.district', string="Native District")
    native_diocese_id = fields.Many2one('res.ecclesia.diocese', string="Native Diocese")
    native_parish_id = fields.Many2one('res.parish', string="Native Parish")
    driving_license_no = fields.Char(string="Driving License No.")
    pancard_no = fields.Char(string="PAN No.")
    known_language_ids = fields.Many2many('res.languages', string="Languages Known")
    twitter_account = fields.Char(string="Twitter ID")
    fb_account = fields.Char(string="Facebook ID")
    linkedin_account = fields.Char(string="Linkedin ID")
    whatsapp_no = fields.Char(string="Whatsapp No.")
    personal_mobile = fields.Char(string="Personal Mobile")
    personal_email = fields.Char(string="Personal Email")
    passport_country_id = fields.Many2one('res.country', string="Country of Passport")
    known_popularly_as = fields.Char(string="Known Popularly As")
    member_type = fields.Selection([('member','Member'),('bishop','Bishop'),('priest','Priest'),('deacon','Deacon'),('lay_brother','Lay Brother'),('brother','Brother'),('sister','Sister'),('junior_sister', 'Junior Sister'),('novice','Novice')], string="Member Type")
    certificate_name = fields.Char(string="Certificate Name")
    place_of_birth = fields.Char(string="Place of Birth")
#     feast_day = fields.Selection(DAYS,string="Feast Day")
#     feast_month = fields.Selection(MONTHS,string="Feast Month")
#     place_of_baptism = fields.Char(string="Place of Baptism")
#     place_of_cnf = fields.Char(string="Place of Confirmation")
#     place_of_fhc = fields.Char("Place of Communion")
#     place_of_marriage = fields.Char("Place of Marriage")
    minister_of_baptism = fields.Char(string="Minister of Baptism")
    minister_of_cnf = fields.Char(string="Minister of Confirmation")
    minister_of_fhc = fields.Char(string="Minister of First Holy Communion")
    minister_of_marriage = fields.Char(string="Minister of Marriage")
    place_of_death = fields.Char("Death Place")
    parish_street = fields.Char("Parish Address line 1", help="Parish Address line 1")
    parish_street2 = fields.Char("Parish Area/Street", help="Parish Area/Street")
    parish_place = fields.Char("Parish Place", help="Parish Place")
    parish_zip = fields.Char("Parish Zip", help="Parish ZIP")
    parish_city = fields.Char("Parish City", help="Parish City/Town/Taluk")
    parish_district_id = fields.Many2one('res.state.district', help="Parish District")
    parish_state_id = fields.Many2one("res.country.state", "Parish State", help="Parish State")
    parish_country_id = fields.Many2one('res.country', "Parish Country", help="Parish Country")
    parish_mobile = fields.Char("Parish Mobile")
    parish_email = fields.Char("Parish Email")
    passport_no = fields.Char(string="Passport No.", size=8)
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict")
    community_id = fields.Many2one('res.community', string="House/Community", ondelete="restrict")
    rel_province_id = fields.Many2one('res.religious.province', string="RE Province", ondelete="restrict")
    rel_zone_id = fields.Many2one('res.religious.zone', string="Area", ondelete="restrict")
    house_member_ids = fields.One2many('house.member','member_id',string="Work House")
    rel_parish_id = fields.Many2one('res.parish', string="Home Parish")
    rel_address = fields.Text(string="Home Parish Address")
    attachment_ids = fields.Many2many('ir.attachment', string="Attach Files")
    aadhar_proof = fields.Binary(string="Upload Aadhar Proof")
    pan_proof = fields.Binary(string="Upload Pan Proof")
    pan_proof_name = fields.Char()
    passport_proof = fields.Binary(string="Upload Passport Proof")
    passport_proof_name = fields.Char()
    passport_exp_date = fields.Date(string="Passport Expiration Date")
    voter_id = fields.Char(string="Voter Id")
    voter_proof_name = fields.Char()
    voter_proof = fields.Binary(string="Upload Voter Proof")
    license_exp_date = fields.Date(string="License Expiration Date")
    store_name = fields.Char(string="File Name")
    role_ids = fields.Many2many('res.member.role',string="Role",compute='_compute_member_role', store=True)
    profession_date = fields.Date(string="Profession Date", compute="_compute_profession_date")
    statutory_renewal_ids = fields.One2many('member.statutory.renewals', 'member_id', string="Statutory Renewals")
    member_tag_ids = fields.Many2many('member.tags', string="Member Tags")
    current_edu_prgm = fields.Char(string="Edu. Program", compute='_compute_education_program', store=True)
    current_prof_type = fields.Char(string="Prof. Type", compute='_compute_profession_type', store=True)
    current_form_stage = fields.Char(string="Form. Stage", compute='_compute_formation_stage', store=True)
    current_holyorder = fields.Date(string="Holy Order", compute='_compute_holyorder', store=True)
    emer_name = fields.Char(string="Emergency Person Name")
    emer_phone = fields.Char(string="Emergency Person Phone")
    emer_relationship_id = fields.Many2one('res.member.relationship', string="Emergency Person Relationship")
    remembrance_ids = fields.One2many('anniversary.remembrance','member_id', string="Anniversary Remembrance")
    can_edit = fields.Boolean(compute="_compute_member_special_edit",default=True)
    cause_of_death = fields.Char(string="Cause of Death")
    burial_place = fields.Char(string="Burial Place")
    burial_date = fields.Datetime(string="Burial Date & Time")
    ecc_community_id = fields.Many2one('res.community', string="Ecc Community")
    marital_status = fields.Char(related='marital_status_id.name', string="Marital Status")

    _sql_constraints = [
        ('uid_uniq', 'unique (unique_code)', "UID already exists. UID is Unique for a Member!"),
    ]
    
    @api.constrains('member_education_ids')
    def active_education_state(self):
        for rec in self:
            edu_ids = rec.member_education_ids.filtered(lambda edu: edu.state == 'open')
            if len(edu_ids) > 1:
                raise ValidationError(_("Sorry! You can create only one open record."))
    
    def _compute_member_special_edit(self):
        for rec in self:
            rec.can_edit = False
            if self.user_has_groups('cristo.group_role_cristo_bsa_super_admin,cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_religious_province'):
                rec.can_edit = True
    
    @api.depends('member_education_ids')
    def _compute_education_program(self):
        for rec in self:
            rec.current_edu_prgm = False
            if rec.member_education_ids:
                edu_ids = rec.member_education_ids.filtered(lambda edu: edu.state == 'open')
                if edu_ids:
                    dispaly_val = edu_ids[-1].study_level_id.name
                    if edu_ids[-1].program_id:
                        dispaly_val = dispaly_val + (" (%s)" % (edu_ids[-1].program_id.name))
                    rec.current_edu_prgm = dispaly_val
    
    @api.constrains('profession_ids')
    def active_profession_state(self):
        for rec in self:
            prof_ids = rec.profession_ids.filtered(lambda prof: prof.state == 'open')
            if len(prof_ids) > 1:
                raise ValidationError(_("Sorry! You can create only one open record."))
    
    @api.depends('profession_ids')
    def _compute_profession_type(self):
        for rec in self:
            rec.current_prof_type = False
            if rec.profession_ids:
                profession = rec.profession_ids.filtered(lambda prof: prof.state == 'open')
                if profession:
                    prof = dict(profession._fields['type'].selection)
                    prof_date = datetime.strftime(profession[-1].profession_date, "%d-%m-%Y")
                    rec.current_prof_type = prof[profession[-1].type] + (" (%s)" % (prof_date))

    @api.constrains('formation_ids')
    def active_formation_stage(self):
        for rec in self:
            form_ids = rec.formation_ids.filtered(lambda form: form.state == 'open')
            if len(form_ids) > 1:
                raise ValidationError(_("Sorry! You can create only one open record."))
    
    @api.depends('formation_ids')
    def _compute_formation_stage(self):
        for rec in self:
            rec.current_form_stage = False
            if rec.formation_ids:
                formation = rec.formation_ids.filtered(lambda formation: formation.state == 'open')
                if formation:
                    rec.current_form_stage = formation[-1].house_id.name + (" (%s)" % (formation[-1].formation_stage_id.name))

    @api.constrains('holyorder_ids')
    def active_holyorder(self):
        for rec in self:
            holy_ids = rec.holyorder_ids.filtered(lambda holy: holy.state == 'open')
            if len(holy_ids) > 1:
                raise ValidationError(_("Sorry! You can create only one open record."))
    
    @api.depends('holyorder_ids')
    def _compute_holyorder(self):
        for rec in self:
            rec.current_holyorder = False
            if rec.holyorder_ids:
                holyorder = rec.holyorder_ids.filtered(lambda order: order.order == 'priest')
                if holyorder:
                    rec.current_holyorder = holyorder.date
                    # ord_date = holyorder[-1].date
                    # rec.current_holyorder = "%s" % (ord_date)

    @api.depends('house_member_ids','house_member_ids.role_ids','house_member_ids.status')
    def _compute_member_role(self):
        for rec in self:
            rec.role_ids = False
            if rec.house_member_ids:
                role = rec.house_member_ids.filtered(lambda hmr: hmr.status == 'active')
                rec.role_ids = role.role_ids

    @api.depends('name','last_name', 'title')
    def name_get(self):
        name = lambda val: val or ''
        return [(record.id, name(record.title.name)+' '+ name(record.name)+ ' ' + name(record.last_name)) \
                 for record in self]
    
    @api.constrains('parish_mobile', 'parish_country_id')
    def _check_parish_mobile(self):
        if self.parish_country_id.code == 'IN':
            if self.parish_mobile:
                cris_tools.mobile_validation(self.parish_mobile)
                
     
    @api.constrains('personal_mobile', 'parish_country_id')
    def _check_personal_mobile(self):
        if self.parish_country_id.code == 'IN':
            if self.personal_mobile:
                cris_tools.mobile_validation(self.personal_mobile)
    
    @api.constrains('whatsapp_no', 'country_id')
    def _check_whatsapp_no(self):
        if self.country_id.code == 'IN':
            if self.whatsapp_no:
                cris_tools.mobile_validation(self.whatsapp_no)
            
    @api.constrains('parish_email')
    def _check_parish_email(self):
        if self.parish_email:
            cris_tools.email_validation(self.parish_email)
            
    @api.constrains('personal_email')
    def _check_personal_email(self):
        if self.personal_email:
            cris_tools.email_validation(self.personal_email)
     
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('member_name', operator, name), ('unique_code', operator, name)]
        rec = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(rec).with_user(name_get_uid))

    @api.onchange('member_type')
    def _onchange_member_type(self):
        if self.member_type:
            if self.member_type == 'bishop':
                return {'domain': {'title': [('for_bishop', '=', True)]}}
            elif self.member_type == 'priest':
                return {'domain': {'title': [('for_priest', '=', True)]}}
            elif self.member_type in ['brother','lay_brother']:
                return {'domain': {'title': [('for_brother', '=', True)]}}
            elif self.member_type == 'deacon':
                return {'domain': {'title': [('for_deacon', '=', True)]}}
            elif self.member_type in ['sister','junior_sister']:
                return {'domain': {'title': [('for_sister', '=', True)]}}
            elif self.member_type == 'novice':
                return {'domain': {'title': [('for_novice', '=', True)]}}
            else:
                return {'domain': {'title': [('for_member', '=', True)]}}
        return {'domain': {'title': [('for_member', '=', True)]}}
    
    @api.onchange('unique_code')
    def _onchange_unique_code(self):
        warning = {}
        if self.unique_code:
            self.env.cr.execute("select unique_code,id from res_member where REPLACE(unique_code,' ','') = '%s'" % (self.unique_code.replace(" ","")))
            results = self.env.cr.dictfetchall()
            if results:
                warning = {
                    'title': _("Warning for UID"),
                    'message': "The entered UID(%s) is already exists." % (self.unique_code)
                }
        if warning:
            return {'warning': warning}
                    
    @api.onchange('dob', 'is_dob_or_age')
    def onchange_dob(self):
        if self.dob and self.is_dob_or_age == 'dob':
            self.age = datetime.now().year - self.dob.year - ((datetime.now().month, datetime.now().day) < (self.dob.month, self.dob.day))
        else:
            self.age = False
            self.dob = False    
    
    @api.onchange('use_parent_address')
    def onchange_use_parent_address(self):
        if self.family_id and self.use_parent_address:
            self.street = self.family_id.street
            self.street2 = self.family_id.street2
            self.place = self.family_id.place
            self.city = self.family_id.city
            self.district_id = self.family_id.district_id
            self.state_id = self.family_id.state_id
            self.zip = self.family_id.zip
            self.country_id = self.family_id.country_id
        else:
            self.street = self.street2 = self.place = self.city = self.state_id = self.district_id = self.zip = self.country_id = False
    
    def open_house_members(self):
        action = self.env.ref('cristo.action_house_members').read()[0]
        action.update({
            'domain': [('member_id','=',self.id)],
            'context': "{'default_member_id':%d}" % (self.id),
        })
        return action
    
    def open_life_membership(self):
        action = self.env.ref('cristo.action_res_membership').read()[0]
        context = {}
        if self.membership_type == 'SE':
            context.update({'default_member_id': self.id, 'default_membership_type': '{0}'.format(self.membership_type),'default_diocese_ids': [[6,0,[self.diocese_id.id]]]})
        if self.membership_type == 'RE':
            context.update({'default_member_id': self.id, 'default_membership_type': '{0}'.format(self.membership_type),'default_province_ids': [[6,0,[self.rel_province_id.id]]]})    
        action.update({
            'domain': [('member_id','=',self.id)],
            'context': context,
        })
        return action
    
    @api.model
    def create(self, vals):
        res = super(Member, self).create(vals)
        f_name = vals.get('name', False) or self.name
        l_name = vals.get('last_name', False) or self.last_name
        if f_name:
            res.name = cris_tools.remove_space(f_name)
        if l_name:
            res.last_name = cris_tools.remove_space(l_name)
            
        if not vals.get('code',False):
            member_type = vals.get('member_type', False)
            if member_type == 'bishop':
                code = 'E'
            elif member_type == 'priest':
                code = 'P'
            elif member_type == 'deacon':
                code = 'D'
            elif member_type == 'lay_brother':
                code = 'L'
            elif member_type == 'brother':
                code = 'B'
            elif member_type == 'sister':
                code = 'S'
            elif member_type == 'novice':
                code = 'N'
            else:
                code = ""
            if code:
                res.update({'code':code})                 
        if self._context.get('import_file'):
            if vals.get('dob', False):
                dob = datetime.strptime(vals.get('dob'), '%Y-%m-%d').date()
                res.update({'age':datetime.now().year - dob.year - ((datetime.now().month, datetime.now().day) < (dob.month, dob.day))})
        return res
    
    def write(self, vals):
        f_name = vals.get('name', False) or self.name
        l_name = vals.get('last_name', False) or self.last_name
        if f_name:
            f_name = cris_tools.remove_space(f_name)
        if l_name:
            l_name = cris_tools.remove_space(l_name)
        if self._context.get('import_file'):
            if vals.get('dob', False):
                dob = datetime.strptime(vals.get('dob'), '%Y-%m-%d').date()
                vals.update({'age':datetime.now().year - dob.year - ((datetime.now().month, datetime.now().day) < (dob.month, dob.day))})
        code = vals.get('code', False) or self.code
        if not code:
            member_type = vals.get('member_type', False) or self.member_type
            if member_type == 'bishop':
                code = 'E'
            elif member_type == 'priest':
                code = 'P'
            elif member_type == 'deacon':
                code = 'D'
            elif member_type == 'lay_brother':
                code = 'L'
            elif member_type == 'brother':
                code = 'B'
            elif member_type == 'sister':
                code = 'S'
            elif member_type == 'novice':
                code = 'N'
            else:
                code = ""
            if code:
                vals.update({'code':code})
        return super(Member, self).write(vals)
        
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(Member, self).unlink()
        return contacts.unlink()
    
    @api.model
    def get_import_templates(self):
        member_type = self._context.get('default_member_type',False)
        membership_type = self._context.get('membership_type',False)
        
        if member_type == "priest" and membership_type == 'RE':
            label = _('Priest\'s Template')
            template = 'cristo/static/xls/Religious Priest.xlsx'
        elif member_type == "deacon" and membership_type == 'RE':
            label = _('Deacon\'s Template')
            template = 'cristo/static/xls/Religious Deacon.xlsx'
        elif member_type == "brother" and membership_type == 'RE':
            label = _('Brother\'s Template')
            template = 'cristo/static/xls/Religious Brother.xlsx'
        elif member_type == "lay_brother" and membership_type == 'RE':
            label = _('Lay Brother\'s Template')
            template = 'cristo/static/xls/Religious Lay Brother.xlsx'
        elif member_type == "bishop" and membership_type == 'RE':
            label = _('Bishop\'s Template')
            template = 'cristo/static/xls/Religious Bishop.xlsx'
        elif member_type == "sister" and membership_type == 'RE':
            label = _('Sister\'s Template')
            template = 'cristo/static/xls/Religious Sister.xlsx'
        elif member_type == "junior_sister" and membership_type == 'RE':
            label = _('Junior Sister\'s Template')
            template = 'cristo/static/xls/Religious Junior Sister.xlsx'
        elif member_type == "novice" and membership_type == 'RE':
            label = _('Novice\'s Template')
            template = 'cristo/static/xls/Religious Novice.xlsx'          
        elif member_type == "priest" and membership_type == 'SE':
            label = _('Priest\'s Template')
            template = 'cristo/static/xls/Secular Priest.xlsx'
        elif member_type == "deacon" and membership_type == 'SE':
            label = _('Deacon\'s Template')
            template = 'cristo/static/xls/Secular Deacon.xlsx'
        elif member_type == "brother" and membership_type == 'SE':
            label = _('Brother\'s Template')
            template = 'cristo/static/xls/Secular Brother.xlsx'
        elif member_type == "bishop" and membership_type == 'SE':
            label = _('Bishop\'s Template')
            template = 'cristo/static/xls/Secular Bishop.xlsx'
        elif member_type == "member":
            label = _('Parish Member\'s Template')
            template = 'cristo/static/xls/Parish Member.xlsx'
        else:
            label = _('Common Member Template')
            template = 'cristo/static/xls/All Member.xlsx'
        return [{
                'label': label,
                'template': template
                }]
        
    # This is For REST API 
    def api_get_member_ministry(self,args):
        result = {}
        role_result =[]
        role_ids = self.env['house.member'].search([('member_id','=',args),('status','=','active')],limit=1)
        for role in role_ids.role_ids:
            roles = {}
            roles['role_id'] = role.id
            roles['role_name'] = role.name
            role_result.append(roles)
        result.update({
                'house_id': role_ids.house_id.id,
                'house_name': role_ids.house_id.name,
                'date_from': role_ids.date_from.strftime('%d/%m/%Y'),
                'date_to': role_ids.date_to.strftime('%d/%m/%Y') if role_ids.date_to else "",
                'role_ids': role_result
                })
        return result
    
class ResMemberEducation(models.Model):
    _name = "res.member.education"
    _description = "Member Education"
    
    def check_binary_data(self,binary):
        if (len(binary) / 1024 / 1024) > 1:
            raise UserError(_("The maximum attachment upload size is 1 MB."))
        
    @api.constrains('attachment')
    def _validate_attachment(self):
        for rec in self:
            if rec.attachment:
                binary = base64.b64decode(rec.attachment or "")
                rec.check_binary_data(binary)
    
    @api.constrains('year_of_passing','member_id.dob')
    def _validate_year_of_passing(self):
        member_dob = self.member_id.dob.year
        for rec in self:
            if rec.year_of_passing < str(member_dob):
                raise UserError(_("Year of Passing should not be lesser than Date of Birth"))
    
    member_id = fields.Many2one('res.member', string='Member', ondelete='cascade')
    study_level_id = fields.Many2one('res.study.level', string='Study Level', required=True)
    program_id = fields.Many2one('res.member.program', string='Program', domain="[('study_level_id', '=', study_level_id)]")
    year_of_passing = fields.Selection(YEAR, string='Year of Passing')
    institution = fields.Char(string="Institution")
    note = fields.Text(string='Note')
    core_disiplines_ids = fields.Many2many('res.core.disiplines', string="Core Disiplines")
    particulars = fields.Char(string="Particulars")
    duration = fields.Float(string="Duration (in Years)")
    mode = fields.Selection([('regular','Regular'),('private','Private'),('not_applicable','Not Applicable')], string="Mode")
    result = fields.Char(string="Result")
    state = fields.Selection([('open','Active'),('done','Completed')],string="Status")
    member_type = fields.Char(string="Member Type")
    attachment = fields.Binary(string="Attachment")
    store_name = fields.Char(string="Name")
#     board_id = fields.Many2one('institution.board', string="Board")
#     study_level_code_id = fields.Char(related="study_level_id.study_level_code")
    board_or_university = fields.Char(string="Board / University")

    
class ReligiousFamily(models.Model):
    _name = 'res.religious.family'
    _description = "Religious Family"
    
    member_id = fields.Many2one('res.member', ondelete="cascade",string="Member")
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([('male','Male'),('female','Female'),('transgender','Transgender')],string="Gender")
    relationship = fields.Selection([('parent','Parent'),('siblings','Siblings')], string="Relationship")
    birth_date = fields.Date(string="Date of Birth")
    death_info = fields.Char(string="Death Info(if applicable)")
#     occupation_id = fields.Many2one('res.occupation', string="Occupation", ondelete="restrict")
    occupation = fields.Char(string="Occupation")
    contact_number = fields.Char(string="Contact Number")
    family_id = fields.Many2one('res.family', string="Family")

class MemberHelath(models.Model):
    _name = 'res.member.health'
    _description = "Member Health"
    _inherit = ['attachment.size']
     
    member_id = fields.Many2one('res.member', ondelete="cascade",string="Member")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    disease_disorder_id = fields.Many2one('res.disease.disorder', string="Disease Type")
    particulars = fields.Char(string="Medical Concern")
    referred_physician = fields.Char(string="Referred Physician")
    insurance_details = fields.Html(string="Insurance Details")
    attachment_ids = fields.Many2many('ir.attachment', string="Attach Files")
    disease_description = fields.Text(string="Description")
    
    @api.constrains('attachment_ids')
    def _check_attachment_size(self):
        self.env['ir.attachment']._check_size(self.attachment_ids)
        
    @api.constrains('start_date','end_date')
    def date_validation(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.end_date < rec.start_date:
                    raise UserError(_("End date should not be lesser than the Start date."))
            if rec.start_date:
                cris_tools.future_date_validation(rec.start_date,field_name="Disease date")
                
class ResProfession(models.Model):
    _name = "res.profession"
    _description = "Profession"
    
    member_id = fields.Many2one('res.member', string='Member',ondelete="cascade")
    profession_date = fields.Date(string="Date", required=True)
    place = fields.Char(string="Place", required=False)
    type = fields.Selection([('first', 'First'),('renewal','Renewal'),('final','Final')], string="Type", required=True)
    years = fields.Integer(string="Years")
    state = fields.Selection([('open','Active'),('done','Completed')],string="Status")
    
class ResFormation(models.Model):
    _name = "res.formation"
    _description = "Formation"
    
    @api.constrains('start_year','end_year')
    def _validate_year(self):
        for rec in self:
            if rec.end_year:
                if rec.end_year < rec.start_year:
                    raise UserError(_("Formation End year should not be lesser than start year"))
        
    member_id = fields.Many2one('res.member', string='Member',ondelete="cascade")
    institute_id = fields.Many2one('res.religious.institute',related="house_id.institute_id", string="Congregation", required=False)
    house_id = fields.Many2one('res.community', string="House Name", required=False)
    start_year = fields.Selection(YEAR, string="Start Year", required=False)
    end_year = fields.Selection(YEAR, string="End Year")
    study_info = fields.Text(string="Any Study Done")
    formation_stage_id = fields.Many2one('res.formation.stage', string="Stage")
    state = fields.Selection([('open','Active'),('done','Completed')],string="Status")
    
class ResHolyOrder(models.Model):
    _name = "res.holyorder"
    _description = "HolyOrder"
    
    member_id = fields.Many2one('res.member', string="Member",ondelete="cascade")
    date = fields.Date(string="Date", required=True)
    place = fields.Char(string="Place")
    order = fields.Selection([('lector','Lector'),('acolyte','Acolyte'),('deacon','Deacon'),('priest','Priest'),('bishop','Bishop')], string="Order", required=True)
    minister = fields.Char(string="Minister")    
    state = fields.Selection([('open','Active'),('done','Completed')],string="Status")
     
class ResPublication(models.Model):
    _name = "res.publication"
    _description = "Publication"
    
    member_id = fields.Many2one('res.member', string="Member",ondelete="cascade")
    publication_date = fields.Date(string="Publication Date")
    title = fields.Char(string="Title", required=True)
    publisher = fields.Char(string="Publisher")
    royalty = fields.Char(string="Royalty")
    publication_type_id = fields.Many2one('publication.type', string="Publication Type")
    
class ResAwardRecognition(models.Model):
    _name = "res.award.recognition"
    _description = "Award and Recognitions"
    
    member_id = fields.Many2one('res.member', string="Member",ondelete="cascade")
    date = fields.Date(string="Date", required=True)
    title = fields.Char(string="Title", required=True)
    agency = fields.Char(string="Agency", required=False)
    level = fields.Char(string="Level")
    details = fields.Char(srting="Details")

class StatutoryRenewals(models.Model):
    _name = "member.statutory.renewals"
    _description = "Statutory Renewals"
    
    no = fields.Char(string="Number")
    document = fields.Char(string="Document Name")
    document_type_id = fields.Many2one('renewal.doc.type',string="Document Type")
    agency = fields.Char(string="Agency")
    valid_from = fields.Date(string="Valid From")
    valid_to = fields.Date(string="Valid To")
    next_renewal = fields.Date(string="Next Renewal Date")
    member_id = fields.Many2one('res.member', string="Member")
    proof = fields.Binary(string="Proof")
    store_name = fields.Char(string="File Name")
    
    @api.constrains('valid_from','valid_to')
    def date_validation(self):
        for rec in self:
            if rec.valid_from and rec.valid_to:
                if rec.valid_to < rec.valid_from:
                    raise UserError(_("Valid from date should not be lesser than the Valid Start date."))

    def member_renewal_notification_send(self):
        mail_server_id = self.env['ir.mail_server'].search([], limit=1)
        if mail_server_id:
            email_from = mail_server_id.smtp_user
            notificatiton_date = date.today() + timedelta(days=30)
            statutory_ids = self.env['member.statutory.renewals'].search([('valid_to','=',notificatiton_date)])
            for statutory_id in statutory_ids:
                email_to = statutory_id.member_id.email
                if statutory_id.member_id.community_id.email:
                    email_cc = statutory_id.member_id.community_id.email
                else:
                    email_cc = ''
                if email_to:
                    member_name = statutory_id.member_id.full_name
                    template_id = self.env.ref('cristo.email_template_member_renewal_notification', raise_if_not_found=False)
                    if template_id:
                        try:
                            template_id.with_context(email_from=email_from,email_to=email_to,email_cc=email_cc,member_name=member_name).send_mail(
                                statutory_id.id, raise_exception=True)
                        except MailDeliveryException:
                            raise MailDeliveryException(_("Mail Delivery Failed"), '')
    
class MemberTags(models.Model):
    _name = "member.tags"
    _description = "Member Tags"
    
    name = fields.Char(string="Name")
    color = fields.Integer(string="Color Index")

class AnniversaryRemembrance(models.Model):
    _name = 'anniversary.remembrance'
    _description = "Anniversary Remembrance"

    name = fields.Char(string="Note", required=True)
    anniversary_day = fields.Selection(DAYS,string="Anniversary Day")
    anniversary_month = fields.Selection(MONTHS,string="Anniversary Month")
    anniversary_type_id = fields.Many2one('anniversary.type', string="Anniversary Type")
    anniversary_type_ids = fields.Many2many('anniversary.type',compute='_compute_anniversary_type')
    is_mine = fields.Boolean(string="Is Mine")
    member_id = fields.Many2one('res.member', string="Member")
    
    @api.depends('member_id')
    def _compute_anniversary_type(self):
        for rec in self:
            rec.anniversary_type_ids = False
            if rec.member_id.member_type in ['bishop','priest','lay_brother','brother','deacon']:
                recs = self.env['anniversary.type'].sudo().search([('is_priest','=',True)])
                rec.anniversary_type_ids = [(6, 0, recs.ids)]
            if rec.member_id.member_type in ['sister','junior_sister']:
                recs = self.env['anniversary.type'].sudo().search([('is_sister','=',True)])
                rec.anniversary_type_ids = [(6, 0, recs.ids)]
            if rec.member_id.membership_type == 'LT':
                recs = self.env['anniversary.type'].sudo().search([('is_layperson','=',True)])
                rec.anniversary_type_ids = [(6, 0, recs.ids)]
               
    def get_holy_order_dates(self,holy_order,anniver_type,name):
        holy_order_ids = self.env['res.holyorder'].search(holy_order)
        anniversary_type = self.env['anniversary.type'].search(anniver_type,limit=1)
        for holy_order_id in holy_order_ids:
            anniversary_rem_holy_id = self.env['anniversary.remembrance'].search([('member_id', '=', holy_order_id.member_id.id), ('anniversary_type_id', '=', anniversary_type.id), ('is_mine', '=', True)])
            if anniversary_rem_holy_id:
                anniversary_rem_holy_id.write({'anniversary_day': str(int(holy_order_id.date.strftime("%d"))),
                                               'anniversary_month': str(int(holy_order_id.date.strftime("%m")))
                                               })
            elif anniversary_type:
                vals = {
                    'name': name,
                    'anniversary_day': str(int(holy_order_id.date.strftime("%d"))),
                    'anniversary_month': str(int(holy_order_id.date.strftime("%m"))),
                    'member_id': holy_order_id.member_id.id,
                    'anniversary_type_id': anniversary_type.id,
                    'is_mine': True
                }
                self.env['anniversary.remembrance'].sudo().create(vals)

    def get_anniversary_dates(self):
        member_ids = self.env['res.member'].search([('dob','!=',False)])
        anniversary_type_dob = self.env['anniversary.type'].search([('name','=ilike','Birth Day')], limit=1)
        for member_id in member_ids:
            anniversary_rem_dob_id = self.env['anniversary.remembrance'].search([('member_id','=',member_id.id),('anniversary_type_id','=',anniversary_type_dob.id),('is_mine','=',True)])
            if anniversary_rem_dob_id:
                anniversary_rem_dob_id.write({'anniversary_day': str(int(member_id.dob.strftime("%d"))), 
                                           'anniversary_month': str(int(member_id.dob.strftime("%m")))
                                           })
            elif anniversary_type_dob:    
                vals = {
                    'name': 'Birthday Anniversary', 
                    'anniversary_day': str(int(member_id.dob.strftime("%d"))), 
                    'anniversary_month': str(int(member_id.dob.strftime("%m"))),
                    'member_id': member_id.id,
                    'anniversary_type_id': anniversary_type_dob.id,
                    'is_mine': True
                    }
                self.env['anniversary.remembrance'].sudo().create(vals)
                
#       Member Feast Day        
#         member_ids = self.env['res.member'].search([('feast_day','!=',False),('feast_month','!=',False)])
#         anniversary_type_feast = self.env['anniversary.type'].search([('name','=ilike','Feast Day')], limit=1)        
#         for member_id in member_ids:
#             anniversary_rem_feast_id = self.env['anniversary.remembrance'].search([('member_id','=',member_id.id),('anniversary_type_id','=',anniversary_type_feast.id),('is_mine','=',True)])
#             if anniversary_rem_feast_id:
#                 anniversary_rem_feast_id.write({'anniversary_day': member_id.feast_day, 
#                                            'anniversary_month': member_id.feast_month
#                                            })
#             elif anniversary_type_feast:    
#                 vals = {
#                     'name': 'Feast Day Anniversary',
#                     'anniversary_day': member_id.feast_day, 
#                     'anniversary_month': member_id.feast_month,
#                     'member_id': member_id.id,
#                     'anniversary_type_id': anniversary_type_feast.id,
#                     'is_mine': True
#                     }
#                 self.env['anniversary.remembrance'].sudo().create(vals)
                
#       Priest        
        priest_domain = [('date','!=',False),('order','=','priest')]
        priest_type = [('name','=ilike','Priest Ordination')]
        priest_str = 'Priest Ordination Anniversary'
        self.get_holy_order_dates(priest_domain,priest_type,priest_str)
    
#       Lector   
        lector_domain = [('date','!=',False),('order','=','lector')]
        lector_type = [('name','=ilike','Lector Ordination')]
        lector_str = 'Lector Ordination Anniversary'
        self.get_holy_order_dates(lector_domain,lector_type,lector_str)     
                
#       Deacon
        deacon_domain = [('date','!=',False),('order','=','deacon')]
        deacon_type = [('name','=ilike','Deacon Ordination')]
        deacon_str = 'Deacon Ordination Anniversary'
        self.get_holy_order_dates(deacon_domain,deacon_type,deacon_str)
                
#       Bishop
        bishop_domain = [('date','!=',False),('order','=','bishop')]
        bishop_type = [('name','=ilike','Bishop Ordination')]
        bishop_str = 'Bishop Ordination Anniversary'
        self.get_holy_order_dates(bishop_domain,bishop_type,bishop_str)
       
