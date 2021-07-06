# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import Warning
from datetime import datetime
from lxml import etree
import json
from odoo.addons.cristo.models.res_common import Mail_Excluded_Fields

class CristoCustomRole(models.Model):
    _name = 'custom.user.role'
    _description = "Custom User Roles"
    
    name = fields.Char(string="Name",required=True)
    code = fields.Char(string="Code",required=True,size=5)
    group_ids = fields.Many2many('res.groups',string="Module User Roles")
    
class Users(models.Model):
    _inherit = 'res.users'
    
    user_created_by = fields.Many2one('res.users',string="User created by")

class CristoUsers(models.Model):
    _name = 'cristo.users'
    _inherit = ['mail.thread','common.rel.fields']
    _description = "Cristo Users"
    _custom_filter_exclude_fields = ['password'] + Mail_Excluded_Fields
    
    @api.depends('main_category_id','main_role_id')
    def _compute_module_roles(self):
        self.module_roles = False
        mr_id = self.env['custom.user.role'].search([('code','=','MR')],limit=1)
        if mr_id:
            self.module_roles = [(6,0,mr_id.group_ids.ids)]
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CristoUsers, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        groups = []
        if view_type == 'form':
            if self.user_has_groups('cristo.group_role_cristo_bsa_super_admin') or self.user_has_groups('base.group_erp_manager'):
#                 group_ids = self.env['res.groups'].search([('category_id','=',self.env.ref('cristo.module_category_cristo_role').id)])
                groups.extend([self.env.ref('cristo.group_role_cristo_religious_institute_admin').id,self.env.ref('cristo.group_role_cristo_religious_province').id,self.env.ref('cristo.group_role_cristo_religious_house').id,self.env.ref('cristo.group_role_cristo_apostolic_institution').id,self.env.ref('cristo.group_role_cristo_individual').id])
                for node in doc.xpath("//field[@name='main_role_id']"):
                    node.set("domain", "[('id','in',%s)]"%groups)
                for node in doc.xpath("//field[@name='main_category_id']"):
                    node.set("domain", "[('code','in',['RC','RP','HC','RI','MR'])]")
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                groups.extend([self.env.ref('cristo.group_role_cristo_religious_province').id,self.env.ref('cristo.group_role_cristo_religious_house').id,self.env.ref('cristo.group_role_cristo_apostolic_institution').id,self.env.ref('cristo.group_role_cristo_individual').id])
                for node in doc.xpath("//field[@name='main_role_id']"):
                    node.set("domain", "[('id','in',%s)]"%groups)
                for node in doc.xpath("//field[@name='main_category_id']"):
                    node.set("domain", "[('code','in',['RP','HC','RI','MR'])]")
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                groups.extend([self.env.ref('cristo.group_role_cristo_religious_house').id,self.env.ref('cristo.group_role_cristo_apostolic_institution').id,self.env.ref('cristo.group_role_cristo_individual').id])
                for node in doc.xpath("//field[@name='main_role_id']"):
                    node.set("domain", "[('id','in',%s)]"%groups)
                for node in doc.xpath("//field[@name='main_category_id']"):
                    node.set("domain", "[('code','in',['HC','RI','MR'])]")
            elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
                groups.extend([self.env.ref('cristo.group_role_cristo_apostolic_institution').id,self.env.ref('cristo.group_role_cristo_individual').id])
                for node in doc.xpath("//field[@name='main_role_id']"):
                    node.set("domain", "[('id','in',%s)]"%groups)
                for node in doc.xpath("//field[@name='main_category_id']"):
                    node.set("domain", "[('code','in',['RI','MR'])]")
            elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
                groups.extend([self.env.ref('cristo.group_role_cristo_individual').id])
                for node in doc.xpath("//field[@name='main_role_id']"):
                    node.set("domain", "[('id','in',%s)]"%groups)
                for node in doc.xpath("//field[@name='main_category_id']"):
                    node.set("domain", "[('code','=','MR')]")
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    name = fields.Char(string="Name")
    main_category_id = fields.Many2one('res.main.category',string="Main Category")
    mc_code = fields.Char(related='main_category_id.code', string="Main Category Code")
    partner_id = fields.Many2one('res.partner',string="Contact",domain="[('main_category_id','=',main_category_id),('main_category_id','!=',False)]",tracking=True)
    member_id = fields.Many2one('res.member',string="Member")
    login = fields.Char(string="Username",required=True,size=64, help="Used to log into the system")
    password = fields.Char(string="Password",size=64,copy=False,required=True)
    user_id = fields.Many2one('res.users', string="User", ondelete="restrict")
    state = fields.Selection([('draft','Draft'),('activated','Activated'),('deactivated','Deactivated')],string="Status",default='draft',tracking=True)
    main_role_id = fields.Many2one('res.groups',string='Main Role')
    module_access_role_ids = fields.Many2many('res.groups',string="Module Access Roles")
    module_roles = fields.Many2many('res.groups',compute="_compute_module_roles")
    
    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            self.name = self.partner_id.name
        res = {'domain': {'member_id': []}}
        if self.partner_id and self.mc_code == 'MR':
            res['domain']['member_id'] = [('partner_id', '=', self.partner_id.id)]
        return res
     
    def validate_login(self, login):
        user_ids = self.env['res.users'].search([('login', '=', login)])
        if user_ids:
            raise Warning(_("Access Denied! Someone already has that username. Try another?"))
        
    @api.onchange('login')
    def onchange_login(self):
        self.validate_login(self.login)
    
    @api.onchange('main_category_id')
    def onchange_main_category(self):
        self.partner_id = False
        self.member_id = False
    
    def get_access_groups(self):
        vals = {}
        base_user_ids = self.env['res.users']._default_groups().ids
        base_user_ids.append(self.main_role_id.id)
        menu_groups = []
        if self.institute_id.institute_type in ['priest','lay_brother','brother']:
            menu_groups.append(self.env.ref('cristo.group_role_cristo_priest_menu').id or False)
            menu_groups.append(self.env.ref('cristo.group_role_cristo_lay_brother_menu').id or False)
        elif self.institute_id.institute_type in ['sister_apostolic','sister_contemplative']:
            menu_groups.append(self.env.ref('cristo.group_role_cristo_sisters_menu').id or False)
        base_user_ids.extend(self.module_access_role_ids.ids)
        base_user_ids.extend(menu_groups)
        
        vals.update({'groups_id':[(6,0,base_user_ids)],
                     'member_id': self.member_id.id or False,
                     'institute_id':self.institute_id.id or False,
                     'rel_province_id':self.rel_province_id.id or False,
                     'community_id':self.community_id.id or False,
                     'institution_id':self.institution_id.id or False,})
        return vals
        
    
    def action_update_rights(self):
        vals = self.get_access_groups()
        self.user_id.write(vals)
    
    def create_user(self):
        if self.env.user.is_license_user:
            user_count = self.env['res.users'].search_count([('user_created_by','=',self.env.user.id)])
            if user_count >= self.env.user.user_creation_limit:
                raise Warning(_("Sorry! You have already used the user creation limit: %d. \n For more information contact System Admin.")%user_count)
        vals = {
            'login' : self.login,
            'password' : self.password,
            'partner_id': self.partner_id.id,
            'user_created_by': self.env.user.id,
            'action_id': self.env.ref('cristo_dashboard.cristo_action_dashboard').id or False,
            'odoobot_state': 'disabled'
            }
        groups = self.get_access_groups()
        vals.update(groups)
        return self.env['res.users'].sudo().create(vals)    
        
    def action_draft_activate(self):
        if self.user_id:
            pass
        else:
            user = self.create_user()
            if user:
                return self.write({'state':'activated', 'user_id': user.id})
    
    def action_deactivate(self):
        self.user_id.write({'active':False})
        self.write({'state':'deactivated'})
    
    def action_deact_activate(self):
        self.user_id.write({'active':True})
        self.write({'state':'activated'})
      
    def unlink(self):
#         if self.user_has_groups('base.group_erp_manager') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
        users = self.mapped('user_id')
        super(CristoUsers, self).unlink()
        return users.sudo().unlink()
#         else:
#             raise Warning(_("Sorry! You are not allowed to delete.Please contact Admin."))
        