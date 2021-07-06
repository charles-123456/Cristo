# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.addons.cristo.tools import cris_tools

class Baptism(models.Model):
    _name = 'res.baptism'
    _description = 'Baptism'
    _order = 'name asc'
    _inherit = ['mail.thread']

    @api.model
    def default_get(self, fields):
        data = super(Baptism, self).default_get(fields)
        user = self.env.user
        data['diocese_id'] = user.diocese_id.id
        data['vicariate_id'] = user.vicariate_id.id
        data['parish_id'] = user.parish_id.id
        return data

    @api.constrains('gender')
    def _validate_gender(self):
        if not self.gender:
            raise ValidationError(_("Please Choose Gender."))
        
    @api.constrains('dob')
    def _validate_dob(self):
        if self.dob:
            cris_tools.future_date_validation(self.dob)
            
    name = fields.Char(string="First Name", required=True,tracking=True)
    last_name = fields.Char(string="Last Name",tracking=True)
    gender = fields.Selection([('male','Male'),('female','Female'),('transgender','Transgender')], string="Gender")
    dob = fields.Date(string="Date of Birth",tracking=True)
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict", required=True, tracking=True)
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate", ondelete="restrict", tracking=True)
    parish_id = fields.Many2one('res.parish', string="Parish", ondelete="restrict", required=True, tracking=True)
    is_dob_or_age = fields.Selection([('dob','DOB'),('age','Age')], default="dob", string="Is DOB/Age?")
    age = fields.Integer(string="Age")
    birth_place = fields.Char(string="Place of Birth",Tracking=True)
    note = fields.Text(string="Note")
    family_id = fields.Many2one('res.family', string="Family Reference")
    member_id = fields.Many2one('res.member', string="Member Reference")
    parish_priest = fields.Char(string="Parish Priest",tracking=True)
    chronological_order = fields.Integer(string="Chronological Order") 
#   Baptism Details
    bapt_register_ref = fields.Char(string="Baptism Register",tracking=True)
    bapt_date = fields.Date(string="Date of Baptism",tracking=True)
    bapt_place = fields.Char(string="Place of Baptism",tracking=True)
    bapt_minister = fields.Char(string="Minister ")
    bapt_country_id = fields.Many2one('res.country', string="Country of Baptism",tracking=True)
    bapt_god_father = fields.Char(string="God Father’s Name",tracking=True)
    bapt_god_mother = fields.Char(string="God Mother’s Name",tracking=True)
    bapt_god_parents_place = fields.Char(string="God Parents Place",tracking=True)
    bapt_god_partent_place2 = fields.Char(string="God Parents Place2",tracking=True)
#   Parents
    father_name = fields.Char(string="Father’s Name",tracking=True)
    father_domicile = fields.Char(string="Domicile")
    father_religion_id  = fields.Many2one('res.member.religion', string="Father’s Religion", ondelete="restrict")
    father_occupation_id = fields.Many2one('res.occupation', string="Father’s Occupation", ondelete="restrict")
    mother_name = fields.Char(string="Mother’s Name",tracking=True)
    mother_domicile = fields.Char(string="Mother's Domicile")
    mother_religion_id  = fields.Many2one('res.member.religion', string="Mother’s Religion", ondelete="restrict")
    mother_occupation_id = fields.Many2one('res.occupation', string="Mother's Occupation", ondelete="restrict")
#   Grand Parents
    paternal_grandfather = fields.Char(string="Paternal Grand Father")
    paternal_grandmother = fields.Char(string="Paternal Grand Mother")
    maternal_grandfather = fields.Char(string="Maternal Grand Father")
    maternal_grandmother = fields.Char(string="Maternal Grand Mother")
    
    @api.onchange('dob', 'is_dob_or_age')
    def onchange_dob(self):
        if self.dob and self.is_dob_or_age == 'dob':
            self.age = datetime.now().year - self.dob.year
        else:
            self.age = False
            self.dob = False
            
    @api.constrains('bapt_date')
    def _validate_baptism_date(self):
        if self.bapt_date:
            cris_tools.future_date_validation(self.bapt_date,field_name="Baptism Date")
            
    @api.constrains('bapt_date','dob')
    def _validate_bapt_date(self):
        if self.bapt_date and self.dob:
            if self.bapt_date < self.dob:
                raise UserError(_("Baptism date should not be lesser than Date of Birth."))
            
    def print_baptism_certificate_report(self):
        if self.parish_id.bapt_cert_report_temp_id:
            return self.parish_id.bapt_cert_report_temp_id.report_action(self)
        else:
            return self.env.ref('cristo.baptism_certificate_report').report_action(self)
        
class FirstHolyCommunion(models.Model):
    _name = 'res.communion'
    _description = 'First Holy Communion'
    _order = 'name asc'
    _inherit = ['mail.thread']

    @api.model
    def default_get(self, fields):
        data = super(FirstHolyCommunion, self).default_get(fields)
        user = self.env.user
        data['diocese_id'] = user.diocese_id.id
        data['vicariate_id'] = user.vicariate_id.id
        data['parish_id'] = user.parish_id.id
        return data

    @api.constrains('gender')
    def _validate_gender(self):
        if not self.gender:
            raise ValidationError(_("Please Choose Gender."))
        
    @api.constrains('dob')
    def _validate_dob(self):
        if self.dob:
            cris_tools.future_date_validation(self.dob)

    @api.onchange('bapt_register_id')
    def onchange_bapt_register_id(self) :
        if self.bapt_register_id:
            self.bapt_diocese_id = self.bapt_register_id.diocese_id
            self.bapt_parish_id = self.bapt_register_id.parish_id
            self.bapt_date = self.bapt_register_id.bapt_date
            self.dob = self.bapt_register_id.dob
            self.father_name = self.bapt_register_id.father_name
            self.mother_name = self.bapt_register_id.mother_name


    name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name",tracking=True)
    gender = fields.Selection([('male','Male'),('female','Female'),('transgender','Transgender')], string="Gender")
    dob = fields.Date(string="Date of Birth",tracking=True)
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict", required=True, tracking=True)
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate", ondelete="restrict", tracking=True)
    parish_id = fields.Many2one('res.parish', string="Parish", ondelete="restrict", required=True,tracking=True)
    is_dob_or_age = fields.Selection([('dob','DOB'),('age','Age')], default="dob", string="Is DOB/Age?")
    age = fields.Integer(string="Age")
    father_name = fields.Char(string="Father’s Name",tracking=True)
    mother_name = fields.Char(string="Mother’s Name",tracking=True)
    bapt_date = fields.Date(string="Date of Baptism",tracking=True)
    bapt_parish_id = fields.Many2one('res.parish', string="Parish of Baptism")
    bapt_diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese of Baptism")
    bapt_register_id = fields.Many2one('res.baptism', string="Baptism Register Link")
    fhc_register_ref = fields.Char(string="Register Number", help="Only for those who receive Communion in the respective church.",tracking=True)
    fhc_date = fields.Date(string="Date of FHC",tracking=True)
    fhc_place = fields.Char(string="Place",tracking=True)
    fhc_minister = fields.Char(string="Minister")
    fhc_church = fields.Char(string="Church")
    fhc_country_id = fields.Many2one('res.country', string="Country of FHC",tracking=True)
    parish_priest = fields.Char(string="Parish Priest")
    note = fields.Text(string="Note")
    
    @api.onchange('dob', 'is_dob_or_age')
    def onchange_dob(self):
        if self.dob and self.is_dob_or_age == 'dob':
            self.age = datetime.now().year - self.dob.year
        else:
            self.age = False
            self.dob = False
            
    @api.constrains('fhc_date')
    def _validate_fhc_date(self):
       if self.fhc_date:
           cris_tools.future_date_validation(self.fhc_date,field_name="First Holy Communion Date")
            
    @api.constrains('fhc_date','dob')
    def _validate_fhc_dob_dates(self):
        if self.fhc_date and self.dob:
            if self.fhc_date <= self.dob:
                raise UserError(_("First Holy Communion date should not be lesser than Date of Birth."))
            
    @api.constrains('dob','bapt_date') 
    def _validate_bapt_date(self):
        if self.bapt_date and self.dob:
            if self.bapt_date < self.dob:
                raise UserError(_("Baptism date should not be lesser than Date of Birth."))
            
    @api.constrains('fhc_date','bapt_date')
    def _validate_fhc_and_bapt_dates(self):
        if self.fhc_date and self.bapt_date:
            if self.fhc_date < self.bapt_date:
                raise UserError(_("First Holy Communion date should not be lesser than Baptism Date."))
            
    def print_fhc_certificate_report(self):
        if self.parish_id.bapt_cert_report_temp_id:
            return self.parish_id.bapt_cert_report_temp_id.report_action(self)
        else:
            return self.env.ref('cristo.fhc_certificate_report').report_action(self)
        
class Confirmation(models.Model):
    _name = 'res.confirmation'
    _description = 'Confirmation'
    _order = 'name asc'
    _inherit = ['mail.thread']

    @api.model
    def default_get(self, fields):
        data = super(Confirmation, self).default_get(fields)
        user = self.env.user
        data['diocese_id']= user.diocese_id.id
        data['vicariate_id'] = user.vicariate_id.id
        data['parish_id'] = user.parish_id.id
        return data

    @api.constrains('gender')
    def _validate_gender(self):
        if not self.gender:
            raise ValidationError(_("Please Choose Gender."))
        
    @api.constrains('dob')
    def _validate_dob(self):
        if self.dob:
            cris_tools.future_date_validation(self.dob)

    @api.onchange('bapt_register_id')
    def onchange_bapt_register_id(self) :
        if self.bapt_register_id:
            self.bapt_diocese_id = self.bapt_register_id.diocese_id
            self.bapt_parish_id = self.bapt_register_id.parish_id
            self.bapt_date = self.bapt_register_id.bapt_date
            self.dob = self.bapt_register_id.dob
            self.father_name = self.bapt_register_id.father_name
            self.mother_name = self.bapt_register_id.mother_name

    name = fields.Char(string="First Name", required=True,tracking=True)
    last_name = fields.Char(string="Last Name",tracking=True)
    gender = fields.Selection([('male','Male'),('female','Female'),('transgender','Transgender')], string="Gender")
    dob = fields.Date(string="Date of Birth",tracking=True)
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict", required=True, tracking=True)
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate", ondelete="restrict", tracking=True)
    parish_id = fields.Many2one('res.parish', string="Parish", ondelete="restrict", required=True,tracking=True)
    is_dob_or_age = fields.Selection([('dob','DOB'),('age','Age')], default="dob", string="Is DOB/Age?")
    age = fields.Integer(string="Age")
    father_name = fields.Char(string="Father’s Name",tracking=True)
    mother_name = fields.Char(string="Mother’s Name",tracking=True)
    bapt_date = fields.Date(string="Date of Baptism",tracking=True)
    bapt_parish_id = fields.Many2one('res.parish', string="Parish of Baptism")
    bapt_diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese of Baptism",tracking=True)
    bapt_register_id = fields.Many2one('res.baptism', string="Baptism Register Link")
    cnf_register_ref = fields.Char(string="Register Number", help="Only for those who receive Communion in the respective church.",tracking=True)
    cnf_date = fields.Date(string="Date of Confirmation",tracking=True)
    cnf_place = fields.Char(string="Place")
    cnf_minister = fields.Char(string="Minister")
    cnf_god_father = fields.Char(string="God Father")
    cnf_god_mother = fields.Char(string="God Mother")
    cnf_country_id = fields.Many2one('res.country', string="Country of Confirmation")
    parish_priest = fields.Char(string="Parish Priest",tracking=True)
    sponser = fields.Char(string="Sponser",tracking=True)
    note = fields.Text(string="Note")
    
    @api.onchange('dob', 'is_dob_or_age')
    def onchange_dob(self):
        if self.dob and self.is_dob_or_age == 'dob':
            self.age = datetime.now().year - self.dob.year
        else:
            self.age = False
            self.dob = False
    
    @api.constrains('cnf_date')
    def _validate_cnf_date(self):
       if self.cnf_date:
           cris_tools.future_date_validation(self.cnf_date,field_name="Confirmation Date")
    
    @api.constrains('cnf_date','dob')
    def _validate_cnf_dob_dates(self):
        if self.cnf_date and self.dob:
            if self.cnf_date < self.dob:
                raise UserError(_("Confirmation date should not be lesser than Date of Birth."))
            
    @api.constrains('dob','bapt_date')
    def _validate_bapt_dates(self):
        if self.bapt_date and self.dob:
            if self.bapt_date < self.dob:
                raise UserError(_("Baptism date should not be lesser than Date of Birth."))
            
    @api.constrains('bapt_date','cnf_date')
    def _validate_bapt_and_cnf_date(self):
        if self.bapt_date and self.cnf_date:
            if self.bapt_date > self.cnf_date:
                raise UserError(_("Confirmation date should not be lesser then Baptism date.")) 
                       
    def print_confirmation_certificate_report(self):
        if self.parish_id.bapt_cert_report_temp_id:
            return self.parish_id.bapt_cert_report_temp_id.report_action(self)
        else:
            return self.env.ref('cristo.confirmation_certificate_report').report_action(self)
        
class Marriage(models.Model):
    _name = 'res.marriage'
    _description = 'Marriage'
    # _order = 'name asc'
    _inherit = ['mail.thread']

    @api.model
    def default_get(self, fields):
        data = super(Marriage, self).default_get(fields)
        user = self.env.user
        data['diocese_id']= user.diocese_id.id
        data['vicariate_id'] = user.vicariate_id.id
        data['parish_id'] = user.parish_id.id
        return data

    @api.constrains('bride_dob')
    def _validate_bride_dob(self):
        if self.bride_dob:
            cris_tools.future_date_validation(self.bride_dob,'Bride Date of Birth')
            
    @api.constrains('bridegroom_dob')
    def _validate_bridegroom_dob(self):
        if self.bridegroom_dob:
            cris_tools.future_date_validation(self.bridegroom_dob,'Bridegroom Date of Birth')
            
    def name_get(self):
        result = []
        for record in self:
            if record.bridegroom_name and record.bride_name:
                name = record.bridegroom_name + '-' + record.bride_name
                result.append((record.id, name))
        return result
    
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict", required=True, tracking=True)
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate", ondelete="restrict", tracking=True)
    parish_id = fields.Many2one('res.parish', string="Parish", ondelete="restrict", required=True,tracking=True)
#     name = fields.Char(string="Family Name", required=True)
    mrg_register_ref = fields.Char(string="Register Number",tracking=True)
    mrg_date = fields.Date(string="Date of Marriage",tracking=True)
    mrg_place = fields.Char(string="Place of Marriage")
    mrg_minister = fields.Char(string="Minister of Marriage")
    mrg_church = fields.Char(string="Church of Marriage",tracking=True)
    parish_priest = fields.Char(string="Parish Priest",tracking=True)
    civil_reg_office = fields.Char(string="Civil Registration Office",tracking=True)
    civil_reg_date = fields.Date(string="Civil Registration Date")
    banns = fields.Selection([('banns','Banns'),('licence','Licence')], string="By Bann / Licence")
    bann_date1 = fields.Date(string="Bann Date-1",tracking=True)
    bann_date2 = fields.Date(string="Bann Date-2",tracking=True)
    bann_date3 = fields.Date(string="Bann Date-3",tracking=True)
    rectification = fields.Char(string="Rectification")
    impediments = fields.Char(string="Impediments")
    note = fields.Text(string="Note")
#   Bride  
    bride_name = fields.Char(string="Bride Name", required=True)
    bride_last_name = fields.Char(string="Bride Surname",tracking=True)
    bride_dob = fields.Date(string="Bride Date of Birth",tracking=True)
    is_dob_or_age_bride = fields.Selection([('dob','DOB'),('age','Age')], default="dob", string="Bride Is DOB/Age?")
    bride_age = fields.Integer(string="Bride Age")
    bride_birth_parish_id = fields.Many2one('res.parish', string="Bride Parish of Birth",tracking=True)
    bride_status = fields.Selection([('spinster','Spinster'),('widow','Widow'),('divorced','Divorced'),('married','Married')], string="Bride Status",tracking=True)
    bride_parish_id = fields.Many2one('res.parish', string="Bride Parish of Baptism",tracking=True)
    bride_diocese_id = fields.Many2one('res.ecclesia.diocese', string=" Bride Diocese",tracking=True)
    bride_religion_id = fields.Many2one('res.member.religion', string="Bride Religion",tracking=True)
    bride_bapt_date = fields.Date(string="Bride Date of Batptism",tracking=True)
    bride_bapt_church = fields.Char(string="Bride Church of Baptism")
    bride_domicile = fields.Char(string="Bride Domicile")
    bride_occupation_id = fields.Many2one('res.occupation', string="Bride Occupation")
    bride_taluk = fields.Char(string="Bride Taluk")
    bride_residential_address = fields.Char(string="Bride Residential Address")
    bride_country_id = fields.Many2one('res.country', string="Bride Country")
    bride_father_name = fields.Char(string="Bride Father’s Name",tracking=True)
    bride_mother_name = fields.Char(string="Bride Mother’s Name",tracking=True)
    is_bride_course_attended = fields.Selection([('yes','Yes'),('no','No')], string="Bride Attended Course?")
#   Bridegroom  
    bridegroom_name = fields.Char(string="Bridegroom Name", required=True,tracking=True)
    bridegroom_last_name = fields.Char(string="Bridegroom Surname",tracking=True)
    bridegroom_dob = fields.Date(string="Bridegroom Date of Birth",tracking=True)
    is_dob_or_age_bridegroom = fields.Selection([('dob','DOB'),('age','Age')], default="dob", string="Bridegroom Is DOB/Age?")
    bridegroom_age = fields.Integer(string="Bridegroom Age")
    bridegroom_birth_parish_id = fields.Many2one('res.parish', string="Bridegroom Parish of Birth",tracking=True)
    bridegroom_status = fields.Selection([('bachelor','Bachelor'),('widower','Widower'),('divorced','Divorced'),('married','Married')], string="Bridegroom Status",tracking=True)
    bridegroom_parish_id = fields.Many2one('res.parish', string="Bridegroom Parish of Baptism",tracking=True)
    bridegroom_diocese_id = fields.Many2one('res.ecclesia.diocese', string="Bridegroom Diocese",tracking=True)
    bridegroom_religion_id = fields.Many2one('res.member.religion', string="Bridegroom Religion")
    bridegroom_bapt_date = fields.Date(string="Bridegroom Date of Batptism",tracking=True)
    bridegroom_bapt_church = fields.Char(string="Bridegroom Church of Baptism")
    bridegroom_domicile = fields.Char(string="Bridegroom Domicile")
    bridegroom_occupation_id = fields.Many2one('res.occupation', string="Bridegroom Occupation")
    bridegroom_taluk = fields.Char(string="Bridegroom Taluk")
    bridegroom_residential_address = fields.Char(string="Bridegroom Residential Address")
    bridegroom_country_id = fields.Many2one('res.country', string="Bridegroom Country")
    bridegroom_father_name = fields.Char(string="Bridegroom Father’s Name",tracking=True)
    bridegroom_mother_name = fields.Char(string="Bridegroom Mother’s Name",tracking=True)
    is_bridegroom_course_attended = fields.Selection([('yes','Yes'),('no','No')], string="Bridegroom Attended Course?")
#   Witness 1
    witness1_name = fields.Char(string="Witness1 Name",tracking=True)
    witness1_age = fields.Integer(string="Witness1 Age")
    witness1_profession = fields.Char(string="Witness1 Profession")
    witness1_address = fields.Char(string="Witness1 Address")
    witness1_domicile = fields.Char(string="Witness1 Domicile")
#   Witness 2
    witness2_name = fields.Char(string="Witness2 Name",tracking=True)
    witness2_age = fields.Integer(string="Witness2 Age")
    witness2_profession = fields.Char(string="Witness2 Profession")
    witness2_address = fields.Char(string="Witness2 Address")
    witness2_domicile = fields.Char(string="Witness2 Domicile")
    
    @api.onchange('bride_dob', 'is_dob_or_age_bride')
    def onchange_bride_dob(self):
        if self.bride_dob and self.is_dob_or_age_bride == 'dob':
            self.bride_age = datetime.now().year - self.bride_dob.year
        else:
            self.bride_age = False
            self.bride_dob = False
     
    @api.constrains('witness1_age','witness2_age')
    def validate_age(self):
        if self.witness1_age > 110 or self.witness2_age > 110:
             raise UserError(_("Maximum Age will be only in 3 digits"))
            
    @api.constrains('mrg_date')
    def _validate_marriage_date(self):
       if self.mrg_date:
           cris_tools.future_date_validation(self.mrg_date,field_name="Marriage Date")
    
    @api.onchange('bridegroom_dob', 'is_dob_or_age_bridegroom')
    def onchange_bridegroom_dob(self):
        if self.bridegroom_dob and self.is_dob_or_age_bridegroom == 'dob':
            self.bridegroom_age = datetime.now().year - self.bridegroom_dob.year
        else:
            self.bridegroom_age = False
            self.bridegroom_dob = False
            
    @api.constrains('bride_bapt_date','bride_dob')
    def _validate_bride_bapt_dob_dates(self):
        if self.bride_bapt_date and self.bride_dob:
            if self.bride_bapt_date < self.bride_dob:
                raise UserError(_("Bride baptism date should not be lesser than Date of Birth."))
        if self.bride_bapt_date:
            cris_tools.future_date_validation(self.bride_bapt_date,field_name="Bride Baptism Date")
                
    @api.constrains('bridegroom_dob','bridegroom_bapt_date')       
    def _validate_bridegroom_bapt_dob_dates(self):
        if self.bridegroom_bapt_date and self.bridegroom_dob:
            if self.bridegroom_bapt_date < self.bridegroom_dob:
                raise UserError(_("Bridegroom baptism date should not be lesser than Date of Birth."))
        if self.bridegroom_bapt_date:
            cris_tools.future_date_validation(self.bridegroom_bapt_date,field_name="Bridegroom Baptism Date")
               
    @api.constrains('mrg_date','bride_dob')   
    def _validate_mrg_date(self):
        if self.mrg_date and self.bride_dob:
            if self.mrg_date < self.bride_dob:
                raise UserError(_("Marriage date should not be lesser than  Bride Date of Birth."))
            
    @api.constrains('mrg_date','bridegroom_dob')
    def _validate_mrg_date_bridegroom(self):
        if self.mrg_date and self.bridegroom_dob:
            if self.mrg_date < self.bridegroom_dob:
                raise UserError(_("Marriage date should not be lesser than Bridegroom Date of Birth."))
          
    def print_marriage_certificate_report(self):
        if self.parish_id.bapt_cert_report_temp_id:
            return self.parish_id.bapt_cert_report_temp_id.report_action(self)
        else:
            return self.env.ref('cristo.report_marriage_action').report_action(self) 
    
class Death(models.Model):
    _name = 'res.death'
    _description = 'Death'
    _order = 'name asc'
    _inherit = ['mail.thread']

    @api.model
    def default_get(self, fields):
        data = super(Death, self).default_get(fields)
        user = self.env.user
        data['diocese_id']= user.diocese_id.id
        data['vicariate_id'] = user.vicariate_id.id
        data['parish_id'] = user.parish_id.id
        return data

    @api.constrains('gender')
    def _validate_gender(self):
        if not self.gender:
            raise ValidationError(_("Please Choose Gender."))
        
    @api.constrains('dob')
    def _validate_dob(self):
        if self.dob:
            cris_tools.future_date_validation(self.dob)

    @api.onchange('bapt_register_id')
    def onchange_bapt_register_id(self):
        if self.bapt_register_id:
            self.dob = self.bapt_register_id.dob
            self.father_name = self.bapt_register_id.father_name
            self.mother_name = self.bapt_register_id.mother_name

    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict", required=True, tracking=True)
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate", ondelete="restrict", tracking=True)
    parish_id = fields.Many2one('res.parish', string="Parish", ondelete="restrict", required=True,tracking=True)
    name = fields.Char(string="First Name", required=True,tracking=True)
    last_name = fields.Char(string="Last Name",tracking=True)
    gender = fields.Selection([('male','Male'),('female','Female'),('transgender','Transgender')], string="Gender")
    dob = fields.Date(string="Date of Birth",tracking=True)
    birth_place = fields.Char(string="Place of Birth")
    is_dob_or_age = fields.Selection([('dob','DOB'),('age','Age')], default="dob", string="Is DOB/Age?")
    age = fields.Integer(string="Age")
    father_name = fields.Char(string="Father’s Name",tracking=True)
    mother_name = fields.Char(string="Mother’s Name",tracking=True)
    bapt_register_id = fields.Many2one('res.baptism', string="Baptism Register Link")
    marital_status_id = fields.Many2one('res.member.marital.status', string="Marital Status",tracking=True)
    parish_priest = fields.Char(string="Parish Priest",tracking=True) 
    occupation_id = fields.Many2one('res.occupation', string="Occupation")
    spouse = fields.Char(string="Spouse",tracking=True)
    relation_name = fields.Char(string="Relation  Name",tracking=True)
    relationship_id = fields.Many2one('res.member.relationship', string="Relationship",tracking=True)
    note = fields.Text(string="Note")
    marital_status = fields.Char(related='marital_status_id.name', string="Marital Status")
#   Death Details
    death_register_ref = fields.Char(string="Register Number",tracking=True)  
    death_date = fields.Date(string="Date of Death",tracking=True)
    death_place = fields.Char(string="Place of Death",tracking=True)
    death_cause = fields.Char(string="Cause of Death",tracking=True)
    death_country_id = fields.Many2one('res.country', string="Country of Death",tracking=True)
#   burial Details
    burial_date = fields.Date(string="Date of Burial",tracking=True)
    burial_place = fields.Char(string="Place of Burial",tracking=True)
    burial_minister = fields.Char(string="Minister",tracking=True) 
    burial_parish = fields.Char(string="Parish of Burial",tracking=True)  
    cemetery_code = fields.Char(string="Cemetery",tracking=True)
#   Sacraments Details
    received_baptism = fields.Boolean(string="Baptism")
    received_communion = fields.Boolean(string="Communion")
    received_confirmation = fields.Boolean(string="Confirmation")
    received_marriage = fields.Boolean(string="Marriage")
    
    @api.onchange('dob', 'is_dob_or_age')
    def onchange_dob(self):
        if self.dob and self.is_dob_or_age == 'dob':
            self.age = datetime.now().year - self.dob.year
        else:
            self.age = False
            self.dob = False
            
    @api.constrains('death_date')
    def _validate_future_death__date(self):
        if self.death_date:
            cris_tools.future_date_validation(self.death_date,field_name="Death Date")
            
    @api.constrains('death_date','dob','burial_date')
    def _validate_death_date(self):
        if self.death_date and self.dob and self.burial_date:
            if self.death_date < self.dob:
                raise UserError(_("Death date should not be lesser than Date of Birth."))
            if self.burial_date < self.death_date:
                raise UserError(_("Burial Date should be greater than Death date."))
            
    def print_death_certificate_report(self):
        if self.parish_id.bapt_cert_report_temp_id:
            return self.parish_id.bapt_cert_report_temp_id.report_action(self)
        else:
            return self.env.ref('cristo.report_death_action').report_action(self) 
    
