# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import Warning
from datetime import datetime, date, timedelta
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

# This is for User License and its Expiry Functionality
class Users(models.Model):
    _inherit = 'res.users'
    
    is_license_user = fields.Boolean(string="Is License User?")
    user_creation_limit = fields.Integer(string="User Creation Limit")
    expiry_date = fields.Date(string='Expiry Date')

    
class UserLicenseExpirt(models.Model):
    _name = 'user.license.expiry'
    _description = "User License Expiry"
    _rec_name = "main_category_id"
    
    main_category_id = fields.Many2one('res.main.category',string="Main Category")
    mc_code = fields.Char(related='main_category_id.code', string="Main Category Code")
    next_expiry_date = fields.Date(string="Next Expiry Date")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict")
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province", ondelete="restrict")   
    community_id = fields.Many2one('res.community', string="House/Community", ondelete="restrict")
    institution_id = fields.Many2one('res.institution', string="Institution", ondelete="restrict")
    member_ids = fields.Many2many('res.member', string="Members", ondelete="restrict")
    is_empty_date = fields.Boolean(string="Is empty Date?")
    
    @api.model
    def get_license_notification(self):
        data = {'enable_notification':False}
        if self.env.user.expiry_date:
            month_before = self.env.user.expiry_date - timedelta(days=30) 
            if month_before <= datetime.today().date() <= self.env.user.expiry_date:
                date = self.env.user.expiry_date.strftime('%d-%b-%Y')
                data.update({
                    'enable_notification':True,
                    'message':'Your License expires on <b>%s</b>. We request you to renew it by contacting System Admin.' % (date)
                    })
        return data
    
    def action_update_license_details(self):
        if not self.next_expiry_date:
            raise Warning(_("Please enter the Next Expiry Date in the form."))
        if self.mc_code == 'RC':
            users = self.env['res.users'].search([('institute_id','=',self.institute_id.id)])
        elif self.mc_code == 'RP':
            users = self.env['res.users'].search([('rel_province_id','=',self.rel_province_id.id)])
        elif self.mc_code == 'HC':
            users = self.env['res.users'].search([('community_id','=',self.community_id.id)])
        elif self.mc_code == 'RI':
            users = self.env['res.users'].search([('institution_id','=',self.institution_id.id)])
        elif self.mc_code == 'MR':
            users = self.env['res.users'].search([('member_id','in',self.member_ids.ids)])
        else:
            raise Warning(_("Sorry! Can't update the date with this main category."))
            
        if users:
            if self.is_empty_date:
                users.write({'expiry_date':False})
            else:
                users.write({'expiry_date':self.next_expiry_date})

    def user_license_inactive_cron(self):
        user_ids = self.env['res.users'].search([('expiry_date','<',date.today())])
        for user_id in user_ids:
            user_id.write({'active':False})
            user = self.env['cristo.users'].search([('user_id','=',user_id.id)])
            if user:
                user.write({'state': 'deactivated'})
        self.user_license_expiry()

    def user_license_expiry(self):
        user_ids = self.env['res.users'].search([('expiry_date','>=',date.today())])
        for user_id in user_ids:
            month_before = user_id.expiry_date - timedelta(days=30)
            week_before = user_id.expiry_date - timedelta(days=5)
            days = False
            date_format =  datetime.strftime(user_id.expiry_date, '%d-%B-%Y')
            if month_before == date.today():
                days = "after 30 Days"
            elif week_before == date.today():
                days = "after 5 Days"
            elif user_id.expiry_date == date.today():
                days = "Today" 
            template_id = self.env.ref('cristo_users.email_template_user_license_expire_notification', raise_if_not_found=False)
            if days and template_id:
                try:
                    template_id.with_context(days=days,date_format=date_format).send_mail(user_id.id,force_send=True, raise_exception=True)
                except MailDeliveryException:
                    print("Mail Delivery Failed.")
                    continue
       
