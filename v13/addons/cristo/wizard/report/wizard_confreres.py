 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import date_utils
from lxml import etree
import json,io
from datetime import datetime
from odoo.exceptions import UserError
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class Confreres(models.TransientModel):
    _name = 'statistics.confreres'
    _description = 'Statistics Confreres'
    
    @api.model
    def default_get(self, fields):
        data = super(Confreres, self).default_get(fields)
        sortby_id = self.env['ir.model.fields'].search([('field_description', '=', 'Name'), ('model_id', '=', 'res.member')], limit=1)
        if sortby_id:
            data['sortby_id'] = sortby_id.id
        return data
        
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Confreres, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            for node in doc.xpath("//field[@name='rel_province_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    confreres_type = fields.Selection([('summary','Summary'),('detail','Detail'),('mobile_email','Mobile & Email')], default='detail')
    rel_province_id = fields.Many2one('res.religious.province', string="Province", default = lambda self: self.env.user.rel_province_id.id)
    sortby_id = fields.Many2one('ir.model.fields', string="Sort By")
    sort_rule = fields.Selection([('asc','Ascending'),('desc','Descending')], string="Sort Rule", default='asc')
    community_all = fields.Boolean(string="Community All")
    community_ids = fields.Many2many('res.community',string="House/Community")
    living_status = fields.Selection([('yes','Yes'),('no','No')],string="Living Status", default='yes')
    member_type = fields.Selection([('member','Member'),('bishop','Bishop'),('priest','Priest'),('deacon','Deacon'),('lay_brother','Lay Brother'),('brother','Brother'),('sister','Sister'),('junior_sister', 'Junior Sister'),('novice','Novice')],string="Member Type")
    blood_group_id = fields.Many2one('res.blood.group',string="Blood Group")
    
    def get_report_values(self):
        member_ids = self.env['res.member'].search([('rel_province_id','=',self.rel_province_id.id),('living_status','=',self.living_status)],order = self.sortby_id.name if self.sortby_id else 'name')
        priests_count = deacons_count = brothers_count = lay_brothers_count = novices_count = False
        if not self.community_all:
            member_ids = member_ids.search([('community_id','in',self.community_ids.ids)],order = self.sortby_id.name if self.sortby_id else 'name')
        if self.blood_group_id.name:
            if not self.community_all:
                member_ids = member_ids.search([('community_id','in',self.community_ids.ids),('blood_group_id','=',self.blood_group_id.id)])
            else:
                member_ids = member_ids.search([('blood_group_id','=',self.blood_group_id.id)])
        if self.confreres_type == 'detail' or 'mobile_email':
            if self.member_type:
                if not self.community_all:
                    member_ids = member_ids.search([('community_id','in',self.community_ids.ids),('blood_group_id','=',self.blood_group_id.id)],order = self.sortby_id.name if self.sortby_id else 'name')
                else:
                    member_ids = member_ids.search([('member_type','=',self.member_type)],order = self.sortby_id.name if self.sortby_id else 'name')
        if not member_ids:
            raise UserError(_("No data found."))
        if self.confreres_type == 'summary':
            if not self.community_all:
                priests_count = member_ids.search_count([('member_type','=','priest'),('community_id','in',self.community_ids.ids),('living_status','=',self.living_status)])
                deacons_count = member_ids.search_count([('member_type','=','deacon'),('community_id','in',self.community_ids.ids),('living_status','=',self.living_status)])
                brothers_count = member_ids.search_count([('member_type','=','brother'),('community_id','in',self.community_ids.ids),('living_status','=',self.living_status)])
                lay_brothers_count = member_ids.search_count([('member_type','=','lay_brother'),('community_id','in',self.community_ids.ids),('living_status','=',self.living_status)])
                novices_count = member_ids.search_count([('member_type','=','novice'),('community_id','in',self.community_ids.ids),('living_status','=',self.living_status)])
            else:
                priests_count = member_ids.search_count([('member_type','=','priest'),('rel_province_id','=',self.rel_province_id.id),('living_status','=',self.living_status)])
                deacons_count = member_ids.search_count([('member_type','=','deacon'),('rel_province_id','=',self.rel_province_id.id),('living_status','=',self.living_status)])
                brothers_count = member_ids.search_count([('member_type','=','brother'),('rel_province_id','=',self.rel_province_id.id),('living_status','=',self.living_status)])
                lay_brothers_count = member_ids.search_count([('member_type','=','lay_brother'),('rel_province_id','=',self.rel_province_id.id),('living_status','=',self.living_status)])
                novices_count = member_ids.search_count([('member_type','=','novice'),('rel_province_id','=',self.rel_province_id.id),('living_status','=',self.living_status)])
        return [member_ids.ids,priests_count,deacons_count,brothers_count,lay_brothers_count,novices_count,self.sortby_id.name, self.community_ids.ids]
    
    def _build_contexts(self, data):
        result = {}
        result['confreres_type'] = 'confreres_type' in data['form'] and data['form']['confreres_type'] or ''
        result['rel_province_id'] = 'rel_province_id' in data['form'] and data['form']['rel_province_id'] or ''
        result['sortby_id'] = 'sortby_id' in data['form'] and data['form']['sortby_id'] or ''
        result['sort_rule'] = 'sort_rule' in data['form'] and data['form']['sort_rule'] or ''
        return result
    
    def print_pdf(self):
        self.ensure_one()
        data = {}
        data['values'] = self.get_report_values()
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['confreres_type','rel_province_id','sortby_id','sort_rule', 'blood_group_id', 'member_type', 'living_status', 'community_all', 'community_ids'])[0]
        self._build_contexts(data)
        return self.env.ref('cristo.statistics_confreres').report_action(self, data=data, config=False)
    
    def print_xls(self):
        data = {'confreres_type':self.confreres_type,'rel_province_id':self.rel_province_id.id,'sort_rule':self.sort_rule,'community_ids':self.community_ids.ids,'living_status':self.living_status,'community_all':self.community_all,'member_type':self.member_type,'sortby_id':self.sortby_id}
        data['values'] = self.get_report_values()
        return {
                'type': 'ir_actions_xlsx_download',
                'data': {'model': 'statistics.confreres',
                         'options': json.dumps(data, default=date_utils.json_default),
                         'output_format': 'xlsx',
                         'report_name': 'Members List',
                         }
            }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': '10px','bold': True})
        cell_format.set_bg_color('silver')
        head = workbook.add_format({'align': 'center', 'bold': True,'font_size':'16px'})
        head1 = workbook.add_format({'align': 'vcenter','bold': True,'font_size':'14px'})
        txt = workbook.add_format({'font_size': '10px'})
        sheet.merge_range('A1:P2', 'List of Members', head)
        members = data['values'][0]
        member_ids = self.env['res.member'].browse(members)
        if data['confreres_type'] == 'detail':
            field_heads = ['S.No.','Name','Member Type','Village','Parish','Arch/Diocese','DOB','Blood Group','First Profession','Priestly Ord...','Physical Status','House','Mother Tongue','Blood Group','Mobile','Email']
            for i,head in enumerate(field_heads):
                sheet.write(3,i, head, cell_format)
                sheet.set_column(0,0,5)
                sheet.set_column(1,1,20)
                sheet.set_column(2,2,10)
                sheet.set_column(3,3,10)
                sheet.set_column(4,4,15)
                sheet.set_column(5,5,10)
                sheet.set_column(6,6,15)
                sheet.set_column(7,7,15)
                sheet.set_column(8,8,10)
                sheet.set_column(9,9,11)
                sheet.set_column(10,10,10)
                sheet.set_column(11,11,11)
                sheet.set_column(12,12,12)
                sheet.set_column(13,13,13)
                sheet.set_column(14,14,14)
            s_no = 1
            for r, member_id in enumerate(member_ids,4):
                sheet.write(r,0,s_no or '-', txt)
                sheet.write(r,1,member_id.partner_id.full_name or '-', txt)
                sheet.write(r,2,dict(member_id._fields['member_type'].selection).get(member_id.member_type) or '-', txt)
                sheet.write(r,3,member_id.native_place or '-', txt)
                sheet.write(r,4,member_id.native_parish_id.sudo().name or '-', txt)
                sheet.write(r,5,member_id.native_diocese_id.sudo().name or '-', txt)
                sheet.write(r,6,member_id.dob.strftime("%d/%m/%Y") if member_id.dob else '-', txt)
                sheet.write(r,7,member_id.blood_group_id.sudo().name or '-', txt)
                date = False
                for rec in member_id.profession_ids:
                    if rec.type == "first":
                        date = rec.profession_date
                sheet.write(r,8,date.strftime("%d/%m/%Y") if date else '-', txt)
                           
                date = False
                for rec in member_id.holyorder_ids:
                    if rec.order.lower() == "Priest".lower():
                        date = rec.date
                    sheet.write(r,9,date.strftime("%d/%m/%Y") if date else '-', txt)
                sheet.write(r, 10, member_id.physical_status_id.sudo().name or '-', txt)
                sheet.write(r, 11, member_id.community_id.sudo().name or '-', txt)
                sheet.write(r, 12, member_id.mother_tongue_id.sudo().name or '-', txt)
                sheet.write(r, 13, member_id.blood_group_id.sudo().name or '-', txt)
                sheet.write(r, 14, member_id.sudo().personal_mobile or '-', txt)
                sheet.write(r, 15, member_id.sudo().personal_email or '-', txt)
                
                s_no += 1

        if data['confreres_type'] == 'summary':
            sheet.merge_range('A1:C2', self.env['res.religious.province'].browse(data['rel_province_id']).name, head)
            field_heads = ['S.NO.','DESIGNATION','TOTAL']
            sheet.merge_range('A10:B11','GRAND TOTAL', head1)
            priests_count = data['values'][1]
            deacons_count = data['values'][2]
            brothers_count = data['values'][3]
            lay_brothers_count = data['values'][4]
            novices_count = data['values'][5]
            for i,head in enumerate(field_heads):
                sheet.write(3,i, head, cell_format)
                sheet.set_column(0,0,5)
                sheet.set_column(1,1,15)
                sheet.set_column(2,2,10)
            s_no = 1
            sheet.write(4,0,s_no or '-', txt)
            sheet.write(4,1,'Priests', txt)
            sheet.write(4,2,priests_count, txt)
            s_no += 1
            sheet.write(5,0,s_no or '-', txt)
            sheet.write(5,1,'Deacons', txt)
            sheet.write(5,2,deacons_count, txt)
            s_no += 1
            sheet.write(6,0,s_no or '-', txt)
            sheet.write(6,1,'Brothers', txt)
            sheet.write(6,2,brothers_count, txt)
            s_no += 1
            sheet.write(7,0,s_no or '-', txt)
            sheet.write(7,1,'Lay Brothers', txt)
            sheet.write(7,2,lay_brothers_count, txt)
            s_no += 1
            sheet.write(8,0,s_no or '-', txt)
            sheet.write(8,1,'Novices', txt)
            sheet.write(8,2,novices_count, txt)
            
            total = priests_count + deacons_count + brothers_count + lay_brothers_count + novices_count 
            sheet.merge_range('C10:C11',total, head1)
            
        if data['confreres_type'] == 'mobile_email': 
            sheet.merge_range('A1:D2', 'MOBILE NUMBER & EMAIL ADDRESS', head)
            field_heads = ['S.NO.','CONFRERES','MEMBER TYPE','MOBILE NO.','EMAIL ADDRESS']
            for i,head in enumerate(field_heads):
                sheet.write(3,i, head, cell_format)
                sheet.set_column(0,0,5)
                sheet.set_column(1,1,20)
                sheet.set_column(2,2,15)
                sheet.set_column(3,3,20)
                sheet.set_column(4,4,10)
                
            s_no = 1
            for r, member_id in enumerate(member_ids,4):
                sheet.write(r,0,s_no or '-', txt)
                sheet.write(r,1,member_id.partner_id.full_name or '-', txt)
                sheet.write(r,2,dict(member_id._fields['member_type'].selection).get(member_id.member_type) or '-', txt)
                sheet.write(r,3,member_id.mobile or '-', txt)
                sheet.write(r,4,member_id.email or '-', txt)
                
                s_no += 1
            
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
