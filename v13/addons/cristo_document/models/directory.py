# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class Directory(models.Model):
    _name = 'muk_dms.directory'
    _inherit = ['common.rel.fields','common.ecc.fields','muk_dms.directory']
    
    @api.model
    def default_get(self, fields):
        data = super(Directory, self).default_get(fields)
        if not self._context.get('default_parent_directory',False):
            data['parent_directory'] = self.env.user.directory_id.id or False
        return data
    
    is_main_directory = fields.Boolean("Is Main Directory?")
    show_main_dir = fields.Boolean(compute="_compute_show_main_directory",string="Show main dir",store=True)
    shared_ids = fields.Many2many('res.partner',string="Shared with")
    view_cong_low_lev = fields.Boolean(string="View for Cong. Lower Level")
    view_pro_low_lev = fields.Boolean(string="View for Prov. Lower Level")
    view_house_low_lev = fields.Boolean(string="View for House Lower Level")
    
    @api.depends('parent_directory')
    def _compute_show_main_directory(self):
        self.show_main_dir = False
        for rec in self:
            if self.env.user.directory_id:
                if rec.parent_directory.id == self.env.user.directory_id.id:
                    rec.show_main_dir = True
    