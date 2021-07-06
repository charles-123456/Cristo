# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from odoo.addons.cristo.tools import cris_tools
from odoo.addons.cristo.models.res_common import Mail_Excluded_Fields

class Concern(models.Model):
    _name = 'cristo.concern'
    _description = "Concern"
    _inherit = ["common.rel.fields","mail.thread",'attachment.size']
    _custom_filter_exclude_fields = ['concern_history_ids','concern_team_ids'] + Mail_Excluded_Fields
    
    name = fields.Char(string='Name', required=1, tracking=True)
    assigned_id = fields.Many2one('res.partner', string="Assigned To", tracking=True)
    tag_ids = fields.Many2many('concern.tags', string="Tags", tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Attach Files")
    concern_team_ids = fields.One2many('concern.team', 'concern_id', string="Concern Team")
    concern_history_ids = fields.One2many('concern.history', 'concern_id', string="Concern History")
    state = fields.Selection([('open', 'Opened'),('in_progress', 'In Progress'),('reject', 'Rejected'),('ignore', 'Ignored'),('cancel', 'Canceled'),('close', 'Closed')], default='open', tracking=True)
    user_id = fields.Many2one('res.users',compute="_compute_user",store=True,readonly=False)
    description_html = fields.Html(string="Description")
    
    @api.constrains('attachment_ids')
    def _check_attachment_size(self):
        self.env['ir.attachment']._check_size(self.attachment_ids)
     
    @api.depends('assigned_id')
    def _compute_user(self):
        for rec in self:
            if rec.assigned_id:
                rec.user_id = self.env['res.users'].search([('partner_id','=',rec.assigned_id.id)],limit=1)
    
    def action_open(self):
        self.state = 'open'
        
    def action_inprogress(self):
        self.state = 'in_progress'
        
    def action_reject(self):
        self.state = 'reject'
        
    def action_ignore(self):
        self.state = 'ignore'
        
    def action_cancel(self):
        self.state = 'cancel'
        
    def action_close(self):
        self.state = 'close'
    
    def write(self, vals):
        if vals and self.user_has_groups('cristo_concern.group_concern_user') and not self.user_has_groups('cristo_concern.group_concern_unit_head') and not self.user_has_groups('cristo_concern.group_concern_admin'):
            if self.assigned_id.id != self.env.user.partner_id.id and self.env.user.partner_id.id in self.concern_team_ids.mapped('partner_id.id'):
                raise ValidationError(_("Sorry! You cannot edit this concern."))
        return super(Concern, self).write(vals)
     
class ConcernTeam(models.Model):
    _name = 'concern.team'
    _description = "Concern Team"
    _rec_name = "partner_id"
    
    @api.constrains('date_from','date_to')
    def date_validation(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                cris_tools.date_validation(rec.date_from, rec.date_to)

    partner_id = fields.Many2one('res.partner',string='Name', required=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    purpose = fields.Text(string="Purpose")
    is_active = fields.Boolean(string="Active")
    concern_id = fields.Many2one('cristo.concern', string="Concern", ondelete='cascade')
    
class ConcernHistory(models.Model):
    _name = 'concern.history'
    _description = "Concern History"
    _inherit = ['attachment.size']
    
    description = fields.Char(string='Description')
    date = fields.Date(string="Date", required=True)
    follow_up_date = fields.Date(string="Next Follow-up Date")
    reminder = fields.Text(string="Reminder")
    concern_id = fields.Many2one('cristo.concern', string="Concern", ondelete='cascade')
    attachment_ids = fields.Many2many('ir.attachment', string="Attach Files")
    
    @api.constrains('attachment_ids')
    def _check_attachment_mass(self):
        self.env['ir.attachment']._check_size(self.attachment_ids)