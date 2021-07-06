# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.addons.cristo.tools import cris_tools
from odoo.addons.calendar.models import calendar
from lxml import etree
import json
import itertools
from odoo.addons.cristo.models.res_common import Mail_Excluded_Fields

class Chronicle(models.Model):
    _name = 'cristo.chronicle'
    _description = "Chronicle"
    _inherit = ['common.rel.fields','mail.thread','attachment.size']
    _rec_name = 'keywords'
    _custom_filter_exclude_fields = ['org_image_ids','attachment_ids'] + Mail_Excluded_Fields
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Chronicle, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if not self._context.get('my_chr',False):
            for view in doc.xpath("//"+view_type):
                view.attrib['create'] = 'false'
                view.attrib['edit'] = 'false'
                view.attrib['delete'] = 'false'
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    name = fields.Char(string="Title")
    description = fields.Html(string="Description")
    date = fields.Date(string="Date", required=True, tracking=True, default=fields.Date.context_today)
    keywords = fields.Text(string="Keywords", tracking=True)
    user_id = fields.Many2one('res.users', string="Responsible", default = lambda self: self.env.user)
    org_image_ids = fields.Many2many('org.image','chronicle_id', string="Extra Org Media", copy=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Attach Files")
    meeting_ref_ids = fields.Many2many('calendar.event','chronicle_meeting_rel','chronicle_id','meeting_id', string="Meeting")
    calendar_ref_ids = fields.Many2many('calendar.event','chronicle_calendar_rel','chronicle_id','calendar_id', string="Calendar")
    type = fields.Selection([('calendar','Calendar'),('meeting','Meeting'),('other','Other')])
    
    @api.constrains('org_image_ids')
    def validate_images(self):
        if len(self.org_image_ids) > 8:
            raise ValidationError(_("Sorry! You can only add 8 media."))
    
    @api.constrains('attachment_ids')
    def _check_attachment_size(self):
        self.env['ir.attachment']._check_size(self.attachment_ids)
    
    @api.onchange('type','date')
    def onchange_type(self):
        res = {}
        # my_time = datetime.min.time()
        # date = datetime.combine(self.date, my_time)
        # from_time = date.replace(hour=0, minute=59)
        # to_time = date.replace(hour=23, minute=59)
        if not self.type == 'calendar':
            self.calendar_ref_ids = False
        else:
            query = []
            calendar_ids = False
            query = """select id from calendar_event as ce where ce.category = 'calendar' and (ce.start_datetime::date = '{0}' or ce.start_date = '{0}')""".format(self.date)
            if query:
                self.env.cr.execute(query)
                calendar_ids = self.env.cr.fetchall()
            calendar_ids = list(itertools.chain(*calendar_ids))
            res['domain'] = {'calendar_ref_ids':[('id','in',calendar_ids)]}
            # res['domain'] = {'calendar_ref_ids': ['|','|',('start_datetime','>=',from_time),('start_datetime','<=',to_time),('start_date', '=',self.date),('category','=','calendar')]}
        if not self.type == 'meeting':
            self.meeting_ref_ids = False
        else:
            query = []
            meeting_ids = False
            query = """select id from calendar_event as ce where ce.category = 'meeting' and (ce.start_datetime::date = '{0}' or ce.start_date = '{0}') """.format(
                self.date)
            if query:
                self.env.cr.execute(query)
                meeting_ids = self.env.cr.fetchall()
            meeting_ids = list(itertools.chain(*meeting_ids))
            res['domain'] = {'meeting_ref_ids': [('id','in',meeting_ids)]}
            # res['domain'] = {'meeting_ref_ids': ['|','|',('start_datetime','>=',from_time),('start_datetime','<=',to_time),('start_date', '=',self.date),('category','=','meeting')]}
        if not self.type == 'other':
            self.name = False
        return res
    
    @api.onchange('calendar_ref_ids','meeting_ref_ids')
    def onchange_calendar_meeting_ref_ids(self):
        main_desc = ''
        if self.calendar_ref_ids:
            keys=[]
            for cal_id in self.calendar_ref_ids:
                keys.append(cal_id.display_name)
                self.keywords = ", ".join(keys)
                content = "<ul>{}</ul>".format(cal_id.description_html or '')
                main_desc += content
        if self.meeting_ref_ids:
            keys=[]
            for meet_id in self.meeting_ref_ids:
                keys.append(meet_id.display_name)
                self.keywords = ", ".join(keys)
                cont = "<h5>{}:</h5><ul>{}</ul>".format(meet_id.display_name, meet_id.description_html or '') + "<h5>Agenda:</h5><ul>{}</ul>".format(meet_id.agenda or '') + "<h5>Proceedings:</h5><ul>{}</ul>".format(meet_id.proceedings or '') + "<h5>Decision:</h5><ul>{}</ul>".format(meet_id.decision or '')
                main_desc += cont
        main_desc += "<br/>"
        self.description = main_desc
        