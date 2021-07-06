# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.addons.cristo.tools import cris_tools
from datetime import datetime
from odoo.exceptions import UserError

class Family(models.Model):
    _name = 'res.family'
    _description = "Family"
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading', 'mail.thread','partner.clear.cache']
    
    @api.model
    def default_get(self, fields):
        data = super(Family, self).default_get(fields)
        user = self.env.user
        main_category = self.env['res.main.category'].search([('code', '=', 'FA')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['parish_id'] = user.parish_id.id
        return data 
    
    def open_members(self):
        action = self.env.ref('cristo.action_res_member').read()[0]
        action.update({
            'domain': [('family_id','=',self.id)],
            'context': {'default_family_id':self.id,'default_membership_type':'LT','default_member_type':'member'}
        })
        return action
    
    def _compute_member_count(self):
        self.member_count = self.env['res.member'].sudo().search_count([('family_id', '=', self.id)])
    
    @api.depends('child_ids')
    def _compute_family_head(self):
        for rec in self:
            rec.family_head_id = self.env['res.member'].sudo().search([('family_id', '=', rec.id),('is_family_head','=',True)])
    
    member_count = fields.Integer(compute='_compute_member_count', string='Members')
    partner_id = fields.Many2one('res.partner', string="Contacts", required=True, ondelete="cascade")
    reference = fields.Char(string='Family Card Number', tracking=True)
    child_ids = fields.One2many('res.member', 'family_id', string='Members')
    diocese_id = fields.Many2one('res.ecclesia.diocese', string='Diocese')
    vicariate_id = fields.Many2one('res.vicariate', string='Vicariate')
    parish_id = fields.Many2one('res.parish', string='Parish', tracking=True, required=True)
    sub_station_id = fields.Many2one('res.parish.sub.station', string="Sub Station")
    family_head_id = fields.Many2one('res.member',compute='_compute_family_head', string='Family Head', tracking=True)
    house_type_id = fields.Many2one('res.house.type', string='House Type')
    is_civil_marriage = fields.Boolean(string='Civil Marriage?')
    is_church_marriage = fields.Boolean(string='Church Marriage?', default=False)
    civil_marriage_date = fields.Date(string='Civil Marriage Date')
    church_marriage_date = fields.Date(string='Church Marriage Date')
    lang_community_id = fields.Many2one('res.languages', string='Language Community', tracking=True)
    family_register_number = fields.Char(string='Register Number', required=True, tracking=True)
    parish_bcc_id = fields.Many2one('res.parish.bcc', string='Basic Christian Community (BCC)', required=True,
                                    help="Basic Christian Community (BCC)", tracking=True)
    house_ownership = fields.Selection([('own', 'Own'), ('rent', 'Rent')], string='House Ownership', default="own")
    rent_amt = fields.Float(string='Rent Amount')
    family_income = fields.Float(string='Family Income', help="Family Income")
    income_type = fields.Selection([('monthly', 'Monthly'), ('annual', 'Annual')], string='Income Type', default='annual')
    settlement_status = fields.Selection([('family-permanent', 'Family-Permanent'), ('family-temporary', 'Family-Temporary'), ('single-permanent', 'Single-Permanent'), ('single-temporary', 'Single-Temporary')], default='family-permanent', required=True, string='Settled as')
    rite_id = fields.Many2one('res.rite', string="Rite")
    # Address
    same_as_above_address = fields.Boolean(string="Same as above")
    permanent_street = fields.Char("Permanent Address line 1", help="Permanent Address line 1")
    permanent_street2 = fields.Char("Permanent Area/Street", help="Permanent Area/Street")
    permanent_place = fields.Char("Permanent Place", help="Permanent Place")
    permanent_zip = fields.Char("Permanent Zip", help="Permanent ZIP")
    permanent_city = fields.Char("Permanent City", help="Permanent City/Town/Taluk")
    permanent_district_id = fields.Many2one('res.state.district', help="Permanent District")
    permanent_state_id = fields.Many2one("res.country.state", "Permanent State", help="Permanent State")
    permanent_country_id = fields.Many2one('res.country', "Permanent Country", help="Permanent Country")
    permanent_website = fields.Char("Permanent Website")
    permanent_phone = fields.Char("Permanent Phone(Landline)")
    permanent_mobile = fields.Char("Permanent Mobile")
    permanent_email = fields.Char("Permanent Email")
    register_date = fields.Date(string='Date of Registration', required=True, default=fields.Date.context_today)
    active_in_parish = fields.Boolean('Active in parish?', default=True, tracking=True)
    date_of_exit = fields.Date('Date of Exit', help="Date of exit from parish", default=fields.Date.context_today)
    inactive_parish_reason = fields.Char(string='Reason', help="Reason for inactive in parish")
    zone_id = fields.Many2one('res.ecclesia.zone', string="Zone", store=True)
    marriage_type = fields.Selection([
    ('C', 'Both Catholic'),
    ('F', 'Husband Catholic'),
    ('W', 'Wife Catholic'),
    ('E', 'Non Catholic but Christianism')
    ],string='Marriage Type')
    
    @api.onchange('same_as_above_address')
    def onchange_same_as_above_address(self):
        if  self.same_as_above_address:
            self.permanent_street = self.street
            self.permanent_street2 = self.street2
            self.permanent_place = self.place
            self.permanent_city = self.city
            self.permanent_district_id = self.district_id
            self.permanent_state_id = self.state_id
            self.permanent_zip = self.zip
            self.permanent_country_id = self.country_id
        else:
            self.permanent_street = self.permanent_street2 = self.permanent_place = self.permanent_city = self.permanent_district_id = self.permanent_state_id = self.permanent_zip = self.permanent_country_id = False
            
    @api.onchange('register_date')
    def _validate_regiter_date(self):
        if self.register_date:
            cris_tools.future_date_validation(self.register_date,field_name="Registration Date")
            
    @api.constrains('permanent_mobile', 'permanent_country_id')
    def _check_permanent_mobile(self):
        if self.permanent_country_id.code == 'IN':
            if self.permanent_mobile:
                cris_tools.mobile_validation(self.permanent_mobile)
            
    @api.constrains('permanent_email')
    def _check_permanent_email(self):
        if self.permanent_email:
            cris_tools.email_validation(self.permanent_email)
    
    @api.constrains('civil_marriage_date','church_marriage_date')
    def _check_marriage_date(self):
        if self.civil_marriage_date:
            cris_tools.future_date_validation(self.civil_marriage_date,field_name="Civil Marriage Date")
        if self.church_marriage_date:
            cris_tools.future_date_validation(self.church_marriage_date,field_name="Church Marriage Date")
                           
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(Family, self).unlink()
        return contacts.unlink()
    
    def print_family_card_report(self):
        if self.parish_id.fam_card_report_temp_id:
            return self.parish_id.fam_card_report_temp_id.report_action(self)
        else:
            return self.env.ref('cristo.family_card_report').report_action(self)    