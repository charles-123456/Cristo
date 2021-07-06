# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, Warning, ValidationError
from lxml import etree
import json

class MemberAssignment(models.Model):
    _name = 'member.assignment'
    _description = 'Assignment'
    
    @api.model
    def default_get(self, fields):
        data = super(MemberAssignment, self).default_get(fields)
        data['institute_id'] = self.env.user.institute_id.id
        data['rel_province_id'] = self.env.user.rel_province_id.id
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or self.user_has_groups('cristo.group_role_cristo_religious_province'):
            data['membership_type'] = 'RE'
        else:
            if self.env.user.member_id:
                data['membership_type'] = self.env.user.member_id.membership_type
        return data
    
    def print_assignment_report_excel(self):
        return self.env.ref('cristo_assignment.report_assignment_xlsx').report_action(self)
    
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict")
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province", ondelete="restrict")
    membership_type = fields.Selection([('LT','Lay Person'),('RE','Religious'),('SE','Secular Clergy')],string="Membership Type",required=True)
    transfer_start_date = fields.Date(string="Transfer Start Date")
    active = fields.Boolean(string="Active?",default=True)
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('completed','Completed'),('cancelled','Cancelled')],string="Stage",default='draft')
    user_id = fields.Many2one('res.users', string="Responsible", default = lambda self: self.env.user)
    assignment_due_ids = fields.One2many('member.assignment.due','assignment_id',string="Due List")
    assignment_all_ids = fields.One2many('member.assignment.all','assignment_id',string="List All")
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MemberAssignment, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or self.user_has_groups('cristo.group_role_cristo_religious_province'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='membership_type']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    def name_get(self):
        res = []
        for record in self:
            if record.membership_type == 'RE' and record.transfer_start_date:
                res.append((record.id, record.rel_province_id.name + ' [' + str(record.transfer_start_date) + ']'))
            elif record.membership_type == 'RE':
                res.append((record.id, record.rel_province_id.name))
            else:
                res.append((record.id,dict(record._fields['membership_type'].selection).get(record.membership_type)))
        return res

    @api.constrains('assignment_due_ids')
    def _validate_role(self):
        for rec in self:
            for member in rec.assignment_due_ids:
                if member.pre_house_id == member.new_community_id:
                    if member.old_role_ids in member.new_role_ids:
                        raise ValidationError(_("%s's New Role cannot be same as a Current Role in same House")%(member.member_id.full_name))
    
#     @api.onchange('membership_type')
#     def onchange_membership_type(self):
#         self.institute_id = False
#         self.rel_province_id = False
    
    def action_upload_due_list(self):
        return self.env.ref('cristo_assignment.action_upload_assignment').read()[0]
    
    def action_cancel(self):
        self.state = 'cancelled'
        request_ids = self.env['member.assignment.request'].search([('due_id','in',self.assignment_due_ids.ids),('state','=','pro_due_list')])
        if request_ids:
            for request in request_ids:
                request.state = 'cancelled'
    
    def action_confirm(self):
        if not self.assignment_due_ids:
            raise UserError(_("Please Select Member(s) to Confirm."))
        
        self.state = "confirmed"
        
    def action_transfer(self):
        due_ids = self.assignment_due_ids.filtered(lambda id:id.is_selected and not id.is_transfered)
        if not due_ids:
            raise UserError(_("Please Select Member(s) to Transfer."))
        if not self.transfer_start_date:
            raise UserError(_("Please provide the Transfer Start Date."))
        
        role_ids = due_ids.mapped('new_role_ids')
        if not role_ids:
            raise UserError(_("Please define the Role for the selected Members."))

        for due_id in due_ids:
            if not due_id.new_community_id:
                raise UserError(_("Please define the Community for the Member: %s") %(due_id.member_id.full_name))
            if not due_id.new_role_ids:
                raise UserError(_("Please define the Roles for the Member: %s") % (due_id.member_id.full_name))

            hm_id = self.env['house.member'].search([('member_id','=',due_id.member_id.id),('status','=','active')])
            if hm_id:
                hm_id.write({'date_to':datetime.now(),'status': 'completed'})
                member_role_ids = []
                house_mem = self.env['house.member'].search([('member_id','=',due_id.member_id.id),('status','=','active'),('date_from','=',self.transfer_start_date)])
                if house_mem:
                    self.env['house.member'].write({'member_role_ids':[(0,0,{'role_ids':[(6,0,due_id.new_role_ids.ids)]})],
                                                 })
                else:
                    self.env['house.member'].create({'member_id':hm_id.member_id.id,
                                                     'house_id':due_id.new_community_id.id,
                                                     'date_from': self.transfer_start_date,
                                                     'status': 'active',
                                                     'member_role_ids': [(0,0,{'role_ids':[(6,0,due_id.new_role_ids.ids)]})],
                                                     })
                transfer_role = self.env['member.assignment.role'].search([('role_id','in',due_id.new_role_ids.ids),('institute_id','=',due_id.assignment_id.institute_id.id)],limit=1)
                if transfer_role:
                    if transfer_role.term == 'year':
                        if transfer_role.term_value <= 0:
                            raise UserError(_("Please define the Term Value for the Role: %s") % (transfer_role.role_id.name))
                        next_tran_date = self.transfer_start_date + relativedelta(years=+transfer_role.term_value)
                        due_id.member_id.write({'next_transfer_date':next_tran_date,'community_id':due_id.new_community_id.id})
                    else:
                        raise UserError(_("Please define the Term for the Role: %s") % (transfer_role.role_id.name))
                else:
                    due_id.member_id.write({'community_id': due_id.new_community_id.id})
            due_id.write({'is_transfered':True})
        self.state = "completed"
        
        request_ids = self.env['member.assignment.request'].search([('due_id','in',self.assignment_due_ids.ids),('state','=','pro_due_list')])
        if request_ids:
            for request in request_ids:
                request.state = 'completed'
                request.completed_date = date.today()
        
    def action_generate_due_list(self):
    
#        To Load All member data 
#         all_hm_ids = self.env['house.member'].search([('member_id.institute_id','=',self.institute_id.id)])
#         all_list = []
#         for h in all_hm_ids:
#             for role_id in h.member_role_ids:
#                 all_list.append((0,0,
#                                  {'member_id':h.member_id.id,
#                                   'house_id':h.house_id.id,
#                                   'institution_id':role_id.institution_id.id,
#                                   'role_ids':[(6,0,role_id.role_ids.ids)]
#                                   }))
#         self.assignment_all_ids.unlink()
#         self.write({'assignment_all_ids':all_list})
        
#         To Load Due List member data
        if self.membership_type == "RE":
            query = """select id from res_member where membership_type = '{0}' and institute_id = {1} and rel_province_id = {2} and next_transfer_date is not null
                and next_transfer_date <= CURRENT_DATE and living_status = 'yes'""".format(self.membership_type,self.institute_id.id,self.rel_province_id.id)
        else:
            query = """select id from res_member where membership_type = '{0}' and next_transfer_date is not null
                    and next_transfer_date <= CURRENT_DATE and living_status = 'yes'""".format(self.membership_type)
        if query:
            self.env.cr.execute(query)
            mem_ids = self.env.cr.fetchall()
        
        if mem_ids:
            mem_ids = [v[0] for v in mem_ids]
            
            hm_ids = self.env['house.member'].search([('member_id','in',mem_ids),('status','=','active')])
            due_list = []
            for h in hm_ids:
                if h.member_role_ids:
                    for mr_id in h.member_role_ids:
                        if h.date_from:
    #                     due_id = self.assignment_due_ids.filtered(lambda id:id.member_id.id == h.member_id.id and id.pre_institution_id.id == mr_id.institution_id.id)
                            due_id = self.assignment_due_ids.filtered(lambda id:id.member_id.id == h.member_id.id)
                            if due_id:
                                pass
    #                         if not due_id.new_community_id:
    #                             self.write({'assignment_due_ids':[(0,due_id.id,{'member_id':h.member_id.id,'pre_house_id':h.house_id.id,'ministry_years':datetime.today().year-fields.Date.from_string(h.date_from).year})]})
                            else:
                                self.write({'assignment_due_ids':[(0,0,
                                                                   {'member_id':h.member_id.id,
                                                                    'pre_house_id':h.house_id.id,
                                                                    'pre_institution_id': mr_id.institution_id.id,
                                                                    'ministry_years':datetime.today().year-fields.Date.from_string(h.date_from).year,
                                                                    'old_role_ids':[(6,0,mr_id.role_ids.ids)],
                                                                    'is_selected': True,
                                                                    })]
                                            })
                else: 
                    if h.date_from:
                        due_id = self.assignment_due_ids.filtered(lambda id:id.member_id.id == h.member_id.id)
                        if due_id:
                            pass
                        else:
                            self.write({'assignment_due_ids':[(0,0,
                                                               {'member_id':h.member_id.id,
                                                                'pre_house_id':h.house_id.id,
                                                                'pre_institution_id': False,
                                                                'ministry_years':datetime.today().year-fields.Date.from_string(h.date_from).year,
                                                                'old_role_ids':[],
                                                                'is_selected': True,
                                                                })]
                                        })
                                        
    def unlink(self):
        for rec in self:
            if rec.state == 'completed':
                raise Warning(_("Sorry! You cannot delete the completed assignment."))
            else:
                rec.assignment_due_ids = [(5,0,0)]
                super(MemberAssignment, rec).unlink()
        
    
class MemberAssignmentDueList(models.Model):
    _name = 'member.assignment.due'
    _description = 'Assignment Due List'
    
    assignment_id = fields.Many2one('member.assignment',string="Assignment",ondelete="cascade")
    member_id = fields.Many2one('res.member',string="Member",required=True)
    old_role_ids = fields.Many2many('res.member.role',string="Current Role")
    pre_house_id = fields.Many2one('res.community',string="House")
    pre_institution_id = fields.Many2one('res.institution',string="Institution")
    ministry_years = fields.Integer(string="Years of Ministry")
    new_community_id = fields.Many2one('res.community',string="New House")
    new_institution_id = fields.Many2one('res.institution',string="New Institution")
    new_role_ids = fields.Many2many('res.member.role','new_role_assignment_due_rel','role_id','assignment_due_id',string="New Roles")
    is_selected = fields.Boolean(string="Transfer?")
    is_transfered = fields.Boolean(string="Is Transfered?")

    @api.constrains('new_role_ids')
    def new_role_validition(self):
        for rec in self:
            if len(rec.new_role_ids) > 2:
                raise UserError(_("Sorry! Maximum of two new roles only allowed for each Members."))

    def unlink(self):
        for rec in self:
            request = self.env['member.assignment.request'].search([('due_id','=',rec.id)],limit=1)
            if request:
                request.state = "requested"
                request.confirmed_date = False
                request.due_id = False
        super(MemberAssignmentDueList, self).unlink()
    
class MemberTransferRequest(models.Model):
    _name = 'member.assignment.request'
    _description = "Member Transfer Request"
    _rec_name = 'member_id'
    
    @api.model
    def default_get(self, fields):
        data = super(MemberTransferRequest, self).default_get(fields)
        if not self.user_has_groups('cristo_assignment.group_assignment_manager'):
            data['type'] = 'transfer_request'
            if self.env.user.member_id:
                data['member_id'] = self.env.user.member_id.id
        else:
            data['type'] = 'need_based'
        return data
    
    member_id = fields.Many2one('res.member', string="Member", required=True)
    type = fields.Selection([('transfer_request','Transfer Request'),('need_based','Need Based')], string="Type")
    user_id = fields.Many2one('res.users', string="Responsible", default = lambda self: self.env.user)
    requested_date = fields.Date(string='Requested Date',readonly=1)
    confirmed_date = fields.Date(string='Confirmed Date',readonly=1)
    completed_date = fields.Date(string='Completed Date',readonly=1)
    reason = fields.Text(string="Reason",required=True)
    due_id = fields.Many2one('member.assignment.due',string="Due",readonly='1')
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('pro_due_list','Pro-Due list'),('completed','Completed'),('cancelled','Cancelled')], string="Stage", default='draft')

    @api.constrains('member_id')
    def check_user_access(self):
        user = self.env.user
        if not self.user_has_groups('cristo_assignment.group_assignment_manager'):
            if user.member_id:
                if not self.member_id == user.member_id:
                    raise UserError(_("Sorry! You are not allowed to create a request for other Members."))
            else:
                raise UserError(_("Sorry! You didn't have access to create a request. Contact system Admin."))

    def action_request_confirm(self):
        for rec in self:
            if rec.state == "requested":
                rec.action_confirm()

    def action_request(self):
        self.requested_date = date.today()
        self.state = "requested"
        
    def action_cancel(self):
        self.state = "cancelled"
        
    def action_confirm(self):
        if self.member_id.membership_type == "RE":
            assignment_ids = self.env['member.assignment'].search([('membership_type','=', 'RE'),('institute_id','=', self.member_id.institute_id.id),('rel_province_id','=', self.member_id.rel_province_id.id),('state','in',('draft','confirmed'))])
        else:
            assignment_ids = self.env['member.assignment'].search([('membership_type','=', self.member_id.membership_type),('state','in',('draft','confirmed'))])
        if assignment_ids:
            for assignment_id in assignment_ids:
                due_id = assignment_id.assignment_due_ids.filtered(lambda id:id.member_id.id == self.member_id.id)
                if due_id:
                    raise Warning(_("Sorry! The member ({}) is already available in the Due list.").format(self.member_id.full_name))
                
            house = self.member_id.house_member_ids.filtered(lambda hmr: hmr.status == 'active')
            if house:
                institution_id = False
                role_ids = False
                if house[0].member_role_ids:
                    institution_id = house[0].member_role_ids[0].institution_id
                    role_ids = house[0].role_ids
                    
                due_id = self.env['member.assignment.due'].create({
                                    'assignment_id':assignment_ids[0].id,
                                    'member_id':self.member_id.id,
                                    'is_selected' : True,
                                    'pre_house_id': (house[0].house_id.id) if house else False,
                                    'pre_institution_id': (institution_id.id) if institution_id else False,
                                    'old_role_ids': (role_ids) if role_ids else False,
                                    'ministry_years':(datetime.today().year-fields.Date.from_string(house[0].date_from).year) if house else False,
                                    })
            if due_id:
                self.due_id = due_id.id
                self.state = "pro_due_list"
                self.confirmed_date = date.today()
                return due_id
        else:
            raise Warning(_("Sorry! There is no active Transfers currently available.\nYou can create a new Transfer and confirm this member request."))
            
    def unlink(self):
        for rec in self:
            if self.user_has_groups('base.group_erp_manager') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin') or self.user_has_groups('cristo_assignment.group_assignment_admin'):
                super(MemberTransferRequest, rec).unlink()
            elif self.user_has_groups('cristo_assignment.group_assignment_manager'):
                if rec.state in ('completed','pro_du_list','cancelled'):
                    raise Warning(_("Sorry! You cannot delete the confirmed assignment."))
                else:
                    super(MemberTransferRequest, rec).unlink()
            else:
                if not self.state == 'draft':
                    raise Warning(_("Sorry! You cannot delete the requested assignment."))
                else:
                    super(MemberTransferRequest, rec).unlink()

class MemberAssignmentRole(models.Model):
    _name = 'member.assignment.role'
    _description = 'Member Assignment Role'
    _rec_name = 'institute_id'

    @api.model
    def default_get(self, fields):
        data = super(MemberAssignmentRole, self).default_get(fields)
        data['institute_id'] = self.env.user.institute_id.id
        return data

    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict")
    role_id = fields.Many2one('res.member.role', string="Member Role", required=True, ondelete="restrict")
    term = fields.Selection([('year','Year(s)')], string="Term", default="year")
    term_value = fields.Integer(string="Term Value")

class MemberAssignmentListAll(models.Model):
    _name = 'member.assignment.all'
    _description = 'Assignment List All'
    
    assignment_id = fields.Many2one('member.assignment',string="Assignment")
    member_id = fields.Many2one('res.member',string="Member",required=True)
    house_id = fields.Many2one('res.community',string="House")
    institution_id = fields.Many2one('res.institution',string="Institution")
    role_ids = fields.Many2many('res.member.role',string="Role")
    avail_in_due = fields.Boolean(compute="_compute_avail_in_due",string="Available in Due List") 
    
#     def _compute_avail_in_due(self):
#         for rec in self:
#             if rec.member_id:
#                 due_id = self.env['member.assignment.due'].search([('member_id','=',rec.member_id.id)])
#                 if due_id:
#                     rec.avail_in_due = True
#                 else:
#                     rec.avail_in_due = False
            
    
#     def add_member_to_due(self):
#         due_id = self.env['member.assignment.due'].search([('member_id','=',self.member_id.id),('pre_house_id','=',self.house_id.id)])
#         if due_id:
#             raise UserError(_("The member is already available in the due list."))
#         else:
#             self.assignment_id.write({'assignment_due_ids':[(0,0,{'member_id':self.member_id.id,'pre_house_id':self.house_id.id,'pre_institution_id':self.institution_id.id,'old_role_ids':[(6,0,self.role_ids.ids)]})]})
    
    