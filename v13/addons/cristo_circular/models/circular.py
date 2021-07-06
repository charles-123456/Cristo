# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import Warning, ValidationError,UserError
from datetime import datetime
import calendar,re
import base64
from odoo.addons.cristo.models.res_common import Mail_Excluded_Fields

GENERATE_YEAR = []
cur_year = datetime.now().year
while(cur_year >= 1800):
    GENERATE_YEAR.append((str(cur_year), str(cur_year)))
    cur_year -= 1

# DAYS = []
# for d in range(1, 32):
#     DAYS.append((str(d),str(d)))

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
            ('12', 'December')
        ]

class Circular(models.Model):
    _name = 'cristo.circular'
    _description = "Circular"
    _inherit = ["common.rel.fields",'mail.thread']
    _custom_filter_exclude_fields = ['month_value','upload','file_name'] + Mail_Excluded_Fields
    
    @api.model
    def default_get(self, fields):
        data = super(Circular, self).default_get(fields)
        data['member_id'] = self.env.user.member_id.id
        return data
    
    @api.model
    def create(self, vals):
        province = vals.get('rel_province_id' or False)
        province = self.env['res.religious.province'].search([('id','=', province)])
        
        cir_month = vals.get('month' or False)
        cir_year = vals.get('year' or False)
        
        member = vals.get('member_id' or False)
        member = self.env['res.member'].search([('id','=', member)])
        
        count = self.env['cristo.circular'].search_count([('member_id','=',member.id)])
        cir_count = count + 1
        
        vals['cir_code'] = str(province.code or 'PC') + '-' + str(member.alias_name if member.alias_name else member.name) + '/' + 'CIR ' + str(cir_count) + '/' + (str(cir_month) if cir_month else '')  + '-' + (str(cir_year) if cir_month else '')
        return super(Circular, self).create(vals)
    
    name = fields.Char(string='Title', tracking=True)
    cir_code = fields.Char(string='Code')
    theme = fields.Char(string='Theme', tracking=True)
    type = fields.Selection([('upload','Upload'),('create_content','Create Content')],string="Type", tracking=True)
    content = fields.Html(string="Content")
    upload = fields.Binary(string="Upload", attachment=True)
    file_name = fields.Char()
#     day = fields.Selection(DAYS, string="Day")
    month = fields.Selection(MONTHS, string="Month")
    year = fields.Selection(GENERATE_YEAR, string="Year")
    month_value = fields.Char(compute="_compute_month_value", string="Month Value")
    user_id = fields.Many2one('res.users', string="Responsible", default = lambda self: self.env.user)
    member_id = fields.Many2one('res.member', string="Member", tracking=True)

    def check_binary_data(self, binary) :
        if (len(binary) / 1024 / 1024) > 1 :
            raise UserError(_("The maximum attachment upload size is 1 MB."))

    @api.constrains('upload', 'file_name')
    def _check_file(self):
        if self.upload :
            binary = base64.b64decode(self.upload or "")
            self.check_binary_data(binary)
        if self.upload and not self.file_name.endswith('.pdf'):
            raise ValidationError('You can upload only pdf file.')

    @api.onchange('upload')
    def _validate_binary_file(self) :
        if self.upload:
            self._check_file()

    @api.onchange('type','upload')
    def _onchange_type(self):
        if self.type == 'create_content':
            self.upload = False
            self.file_name = ''
        else:
            self.content = ''        
            
    @api.depends('month')
    def _compute_month_value(self):
        self.month_value = False
        month_id = self.month
        self.month_value = calendar.month_name[int(month_id)]
        
    def action_circular_mail(self):
        action = self.env.ref('cristo_circular.action_wizard_circular_mail').read()[0]
        domain = [
            ('res_model', '=', self._name),
            ('res_field', '=', 'upload'),
            ('res_id', '=', self.id),
        ]
        attachment = self.env['ir.attachment'].sudo().search(domain)
        if attachment:
            file_name = re.sub(r'/', '_', self.cir_code)
            attachment.write({'name':file_name})
        action.update({
            'context': {'default_circular_id':self.id,'default_attachment_id':attachment.id}
            })
        return action

    def save_circular(self):
        if self.env.user.directory_id:
            if self.type == "create_content":
                pdf = self.env.ref('cristo_circular.report_circular').render_qweb_pdf(self.ids)
                encoded_pdf = base64.b64encode(pdf[0])
                document = self.create_document(encoded_pdf)
            elif self.type == "upload":
                if self.upload:
                    document = self.create_document(self.upload)
                else:
                    raise Warning(_("You did not upload the document still. Please upload it."))
        else:
            raise Warning(_("Sorry! You don't have main directory. Please contact system Admin"))
        
        message = _("The Circular document created successfully!.")
        self.env['bus.bus'].sendone(
            (self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
            {'type': 'simple_notification', 'title': "Circular Report", 'message': message, 'sticky': False, 'warning': False})
        return document
    
    def create_document(self,encoded_pdf):
        path = self.env['muk_dms.directory'].search([('name','ilike','Circular'),('parent_directory','=',self.env.user.directory_id.id)])
        if not path:
            path = self.env['muk_dms.directory'].create({
                                                'name': 'Circular',
                                                'parent_directory':self.env.user.directory_id.id,
                                                })
        file_name = re.sub(r'/', '_', self.cir_code)
        
#         if self.user_has_groups('cristo.group_role_cristo_religious_province'):
        rec = self.rel_province_id.house_ids.mapped('partner_id').ids
        institutions = self.rel_province_id.institution_ids.mapped('partner_id').ids
        rec.extend(institutions)
        members = self.rel_province_id.member_ids.mapped('partner_id').ids
        rec.extend(members)
        
        return self.env['muk_dms.file'].create({
                                    'name':file_name+'.pdf',
                                    'document_name':file_name,
                                    'content':encoded_pdf,
                                    'extension':'pdf',
                                    'mimetype': 'application/pdf',
                                    'directory': path[0].id,
                                    'user_id' : self.env.user.id,
                                    'institute_id':self.institute_id.id or False,
                                    'rel_province_id' : self.rel_province_id.id or False,
                                    'community_id' : self.community_id.id or False,
                                    'institution_id' : self.institution_id.id or False,
                                    'shared_ids' : [(6,0,rec)] or False,
                                    'locked_by' : self.env.user.id or False
                                    })
#         else:
#             raise Warning(_("Sorry! Only Province Users has the access to save the Circular to Document."))
