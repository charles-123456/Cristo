# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError,ValidationError

class ResDirectory(models.Model):
    _name = 'res.directory'
    _description = "Directory" 

    @api.model
    def default_get(self, fields):
        data = super(ResDirectory, self).default_get(fields)
        user = self.env.user
        if user:
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                data['institute_id'] = user.institute_id.id
                data['rel_province_id'] = False
            if self.user_has_groups('cristo.group_role_cristo_religious_province'):
                data['institute_id'] = user.institute_id.id
                data['rel_province_id'] = user.rel_province_id.id
        return data

    name = fields.Char(string="Name", required="True")
    sheet_ids = fields.One2many('res.directory.sheet', 'directory_id', string="Sheets")
    active = fields.Boolean(string="Active?", default=True)
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict")
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province", ondelete="restrict")
    user_id = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user)

    @api.constrains('active','rel_province_id')
    def _active_directory_validation(self):
        if self.active and self.rel_province_id:
            directory_id = self.env['res.directory'].search_count([('active', '=', True),('rel_province_id', '=', self.rel_province_id.id)])
            if directory_id > 1:
                raise ValidationError(_("Sorry! You can create only one active directory."))

    def get_m2o_field_values(self,sub,record):
        values = {}
        sb_name = str(sub.field_id.name)
        smv = self.env[sub.sub_model].search([('id', '=', record[sb_name].id)])
        for sb_field in sub.field_ids:
            sb_field_name = sb_field.field_id.name
            value = smv[sb_field_name]
            if sb_field.field_id.ttype in ("one2many", "many2many"):
                try:
                    value = ','.join(value.mapped('name')) or ','.join(value.mapped('display_name')) or '-'
                    values.update({sb_field_name: value})
                except:
                    values.update({sb_field_name: '-'})
            if sb_field.field_id.ttype == "many2one":
                try:
                    value = value['name'] or value['display_name'] or '-'
                    values.update({sb_field_name: value})
                except:
                    values.update({sb_field_name: '-'})
            if sb_field.field_id.ttype == "selection":
                try:
                    sel_dic = dict(smv._fields[sb_field_name].selection)
                    values.update({sb_field_name: sel_dic[value]})
                except:
                    values.update({sb_field_name: '-'})
            if sb_field.field_id.ttype == "boolean":
                try:
                    values.update({sb_field_name: 'Yes' if value else 'No'})
                except:
                    values.update({sb_field_name: '-'})
            if sb_field.field_id.ttype in ("date", "datetime"):
                value = value.strftime("%d-%b-%Y") if value else '-'
                values.update({sb_field_name: value})
            if sb_field.field_id.ttype not in ("one2many", "many2many", "many2one", "selection","date", "datetime","boolean"):
                values.update({sb_field_name: value or '-'})
        return {'values':values,'smv':smv}
    def get_o2m_field_values(self,sub,record):
        values = {}
        sb_name = str(sub.field_id.name)
        sub_model = sub.sub_model
        try:
            sb_records = self.env[sub_model].search(safe_eval(sub.domain))
        except:
            sb_records = False
        if sb_records:
            smv = sb_records.filtered(lambda sb_rec: sb_rec.id in record[sb_name].ids)
        else:
            smv = self.env[sub_model].search([('id', 'in', record[sb_name].ids)])
        for sb_field in sub.field_ids:
                sb_field_name = sb_field.field_id.name
                if sb_field.field_id.ttype in ("one2many", "many2many"):
                    try:
                        value = ','.join(smv.sb_field_name.mapped('name')) or ','.join(value.mapped('display_name')) or '-'
                        values.update({sb_field_name: value})
                    except:
                        values.update({sb_field_name: '-'})
                if sb_field.field_id.ttype == "many2one":
                    try:
#                         mo_value = []
#                         for mo_smv in smv:
                        mo_value = smv[sb_field_name].mapped('name') or smv[sb_field_name].mapped('display_name') or False
#                         if value:
#                             mo_value.append(value)
                        mo_value = ', '.join(mo_value)
                        values.update({sb_field_name: mo_value})
                    except:
                        values.update({sb_field_name: '-'})
                if sb_field.field_id.ttype in ("integer", "float"):
                    try:
                        value = smv.mapped(sb_field_name) or '-'
                        values.update({sb_field_name: value})
                    except:
                        values.update({sb_field_name: '-'})
                if sb_field.field_id.ttype in ("date", "datetime"):
                    try:
                        value = smv[-1][sb_field_name]
                        value = value.strftime("%d-%b-%Y") if value else '-'
                        values.update({sb_field_name: value})
                    except:
                        values.update({sb_field_name: '-'})

                if sb_field.field_id.ttype == "selection":
                    try:
                        sel_val = smv[-1][sb_field_name]
                        sel_dic = dict(smv[-1]._fields[sb_field_name].selection)
                        values.update({sb_field_name: sel_dic[sel_val]})
                    except:
                        values.update({sb_field_name: '-'})
                if sb_field.field_id.ttype == "boolean":
                    values.update({sb_field_name: '-'})

                if sb_field.field_id.ttype not in ("one2many", "many2many", "many2one", "integer", "float", "datetime",
                                                   "date", "selection","boolean"):
                    try:
                        value = ', '.join(smv.mapped(sb_field_name)) or '-'
                        values.update({sb_field_name: value})
                    except:
                        values.update({sb_field_name: '-'})
        return {'values':values,'smv':smv}
    @api.model
    def get_sheet_values(self,directory, option):
        data = {}
        result = []
        directory_id = self.env['res.directory'].search([('id','=',directory)], limit=1)
        sheet_id = self.env['res.directory.sheet'].search([('id','=',option),('directory_id','=',directory_id.id)],limit=1)

        if sheet_id:
            if sheet_id.type == 'filter':
                Model = self.env[sheet_id.model_id.model]
                rec = []
                field_string = []

                if sheet_id.main_sheet_field_ids:
                    for field in sheet_id.main_sheet_field_ids:
                        rec.append(field.field_id.name)
                        if field.name:
                            field_string.append(field.name)
                        else:
                            field_string.append(field.field_id.field_description)

                try:
                    records = Model.search(safe_eval(sheet_id.domain))
                except Exception as e:
                    raise UserError(_("Error In Filter Options in Sheet : {} \nPlease correct it.").format(sheet_id.name))
                if records:
                    if sheet_id.is_date_filter:
                        if sheet_id.sheet_field_ids and sheet_id.date_field_ids:
                            data.update({'date_filter': 1,'filter':0,'statistic':0})
                            date_string = []
                            date_name = []
                            for dt_fld in sheet_id.date_field_ids:
                                date_name.append(dt_fld.field_id.name)
                                if dt_fld.name:
                                    date_string.append(dt_fld.name)
                                else:
                                    date_string.append(dt_fld.field_id.field_description)
                            months_dic = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                             9: 'September',
                             10: 'Octobar', 11: 'November', 12: 'December'}
                            field_values = []
                            # fie_name = sheet_id.field_name
                            # print(fie_name)
                            for mon in range(1,13):
                                month = months_dic[mon]
                                for day in range(1, 32):
                                    val = False
                                    if sheet_id.date_field_ids:
                                        date_values = {}
                                        date_values.update({'month': month, 'day': day})
                                        # month = ''
                                        for date_field in sheet_id.date_field_ids:
                                            values = {}
                                            fie_name = date_field.field_id.name
                                            date_fil = records.filtered(lambda rec:(rec[fie_name].month == mon and rec[fie_name].day == day) if rec[fie_name] else '')
                                            if date_fil:
                                                val = True
                                                for field in sheet_id.sheet_field_ids:
                                                    field_name = field.field_id.name
                                                    if field.field_id.model_id.model == sheet_id.model_id.model:
                                                        value = date_fil[-1][field_name]
                                                        if field.field_id.ttype in ("one2many", "many2many"):
                                                            try:
                                                                value = ','.join(date_fil.field_name.mapped('name')) or '-'
                                                                values.update({field_name: value})
                                                            except:
                                                                values.update({field_name: '-'})
                                                        if field.field_id.ttype == "many2one":
                                                            try:
                                                                value = ','.join(date_fil.field_name.mapped('name')) or '-'
                                                                values.update({field_name: value})
                                                            except:
                                                                values.update({field_name: '-'})
                                                        if field.field_id.ttype in ("integer", "float"):
                                                            try:
                                                                value = ','.join(str(date_fil.mapped(field_name))) or '-'
                                                                values.update({field_name: value})
                                                            except:
                                                                values.update({field_name: '-'})
                                                        if field.field_id.ttype in ("date", "datetime"):
                                                            try:
                                                                value = date_fil[0][field_name] or '-'
                                                                value = value.strftime("%d-%b-%Y") if value else '-'
                                                                values.update({field_name: value})
                                                            except:
                                                                values.update({field_name: '-'})

                                                        if field.field_id.ttype  == "selection":
                                                            try:
                                                                sel_dic = dict(date_fil[0]._fields[field_name].selection)
                                                                values.update({field_name: sel_dic[value]})
                                                            except:
                                                                values.update({field_name: '-'})
                                                        if field.field_id.ttype  == "boolean":
                                                            values.update({field_name: '-'})

                                                        if field.field_id.ttype not in ("one2many", "many2many", "many2one","integer", "float","datetime","date","selection","boolean"):
                                                            try:
                                                                value = date_fil.mapped(field_name) or '-'
                                                                values.update({field_name: value})
                                                            except:
                                                                values.update({field_name: '-'})

                                                    else:
                                                        # relation = self.env['ir.model.fields'].search([('model_id.relation','=',field.model_id.model),('model_id','=',sheet.model_id.id)])
                                                        # print(relation)
                                                        values.update({field_name: '-'})

                                            else:
                                                for field in sheet_id.sheet_field_ids:
                                                    values.update({field.field_id.name:'-'})
                                            date_values.update({fie_name: values})
                                        if val:
                                            field_values.append(date_values)
                            data.update({'no_rec': 0, 'fields': rec, 'date_name': date_name,'name': sheet_id.name,
                                     'datas': field_values, 'id': sheet_id.id, 'date_string': date_string,'head_table': 0})
                        else:
                            data.update({'no_rec': 1})
                    else:
                        if sheet_id.sheet_field_ids or sheet_id.sub_model_ids.field_ids:
                            data.update({'filter': 1,'date_filter':0,'statistic':0})
                            data.update({'head_table': 0})
                            ri_fields = []
                            ri_string = []
                            ri_value = {}
                            field_values = []
                            if sheet_id.religious_field_ids:
                                data.update({'head_table': 1,'head_name':sheet_id.religious_field_ids[0].name})
                                model_id = sheet_id.religious_field_ids[0].institute_id or sheet_id.religious_field_ids[0].rel_province_id or sheet_id.religious_field_ids[0].community_id or sheet_id.religious_field_ids[0].institution_id
                                for ri_field in sheet_id.religious_field_ids[0].field_ids:

                                    name = ri_field.field_id.name
                                    ri_fields.append(ri_field.field_id.name)
                                    if ri_field.name:
                                        ri_string.append(ri_field.name)
                                    else:
                                        ri_string.append(ri_field.field_id.field_description)
                                    if ri_field.field_id.ttype in ("one2many", "many2many"):
                                        ri_value.update({ri_field.field_id.name: '-'})
                                    if ri_field.field_id.ttype == "many2one":
                                        ri_value.update({ri_field.field_id.name: model_id[name].name or '-'})
                                    if ri_field.field_id.ttype == "selection":
                                        sel_dic = dict(model_id._fields[name].selection)
                                        sel_val = model_id[name]
                                        ri_value.update({ri_field.field_id.name: sel_dic[sel_val]})
                                    if ri_field.field_id.ttype in ("date", "datetime"):
                                        ri_val = model_id[name]
                                        ri_val = ri_val.strftime("%d-%b-%Y") if ri_val else '-'
                                        ri_value.update({ri_field.field_id.name: ri_val})
                                    if ri_field.field_id.ttype == "boolean":
                                        ri_val = model_id[name]
                                        ri_value.update({ri_field.field_id.name: 'Yes' if ri_val else 'No'})
                                    if ri_field.field_id.ttype not in ("one2many", "many2many", "many2one", "selection","date", "datetime","boolean"):
                                        ri_value.update({ri_field.field_id.name: model_id[name] or '-'})
                            else:
                                data.update({'head_table': 0})
                            for record in records:
                                values = {}
                                for field in sheet_id.sheet_field_ids:
                                    field_name = field.field_id.name
                                    if field.field_id.model_id.model == sheet_id.model_id.model:
                                        value = record[field_name]
                                        if field.field_id.ttype in ("one2many", "many2many"):
                                            try:
                                                value = ','.join(value.mapped('name')) or '-'
                                                values.update({field_name: value})
                                            except:
                                                values.update({field_name: '-'})
                                        if field.field_id.ttype == "many2one":
                                            try:
                                                value = value['name'] or '-'
                                                values.update({field_name: value})
                                            except:
                                                values.update({field_name: '-'})
                                        if field.field_id.ttype in ("date", "datetime"):
                                            value = value.strftime("%d-%b-%Y") if value else '-'
                                            values.update({field_name: value})
                                        if field.field_id.ttype == "boolean":
                                            value = 'Yes' if value else 'No'
                                            values.update({field_name: value})
                                        if field.field_id.ttype == "selection":
                                            try:
                                                sel_dic = dict(record._fields[field_name].selection)
                                                values.update({field_name: sel_dic[value]})
                                            except:
                                                values.update({field_name: '-'})
                                        if field.field_id.ttype not in ("one2many", "many2many", "many2one","selection","date", "datetime"):
                                            values.update({field_name: value or '-'})
                                    else:
                                        # relation = self.env['ir.model.fields'].search([('model_id.relation','=',field.model_id.model),('model_id','=',sheet.model_id.id)])
                                        # print(relation)
                                        values.update({field_name: '-'})

                                if sheet_id.sub_model_ids:
                                    for sub in sheet_id.sub_model_ids:
                                        if sub.type == 'many2one':
                                            dic = self.get_m2o_field_values(sub,record)
                                            values.update(dic['values'])
                                            smv = dic['smv']
                                            if sub.relation_model_ids:
                                                for rel_sub in sub.relation_model_ids:
                                                    if rel_sub.type == 'many2one':
                                                        dic = self.get_m2o_field_values(rel_sub, smv)
                                                        values.update(dic['values'])
                                                    elif rel_sub.type == 'one2many':
                                                        dic = self.get_o2m_field_values(rel_sub,smv)
                                                        values.update(dic['values'])
                                        elif sub.type == 'one2many':
                                            dic = self.get_o2m_field_values(sub,record)
                                            values.update(dic['values'])
                                field_values.append(values)

                            data.update({'no_rec': 0, 'fields': rec, 'field_name': field_string, 'name': sheet_id.name,
                                         'datas': field_values, 'id': sheet_id.id, 'ri_fields':ri_fields,
                                         'ri_string':ri_string,'ri_value':ri_value})
                        else:
                            data.update({'no_rec': 1})
                else:
                    data.update({'no_rec': 1})

            if sheet_id.type == 'statistic':
                data.update({'filter': 0, 'statistic': 1, 'date_filter':0})
                if not sheet_id.custom_statistic:
                    data.update({'cus_stat': 0,})
                    rec = []
                    field_values = []
                    if sheet_id.statistic_ids:
                        names = sheet_id.statistic_ids.mapped('name') or []
                        counts = []
                        for co in sheet_id.statistic_ids:
                            counts.append(str(co.count))
    
                        for index in range(0, len(names)):
                            val = {}
                            val.update({'name': names[index], 'count': counts[index]})
                            field_values.append(val)
    
                        data.update({'no_rec': 0,'fields': rec, 'name': sheet_id.name,
                             'datas': field_values,'id':sheet_id.id,'head_table': 0})
                    else:
                        data.update({'no_rec': 1})
                else:
                    statistic_data = self.get_custom_statistic_count(sheet_id)
                    data.update(statistic_data)
        result.append(data)
        return result
    
    def get_custom_statistic_count(self, sheet_id):
        if sheet_id.custom_statistic_ids:
            values = []
            statistic_id = sheet_id.custom_statistic_ids[-1]
            titles = [statistic_id.name]
            for title in statistic_id.title_ids:
                titles.append(title.name)
            titles.append("Total")
            MODEL = statistic_id.based_on
            DOMAIN = statistic_id.domain
            records = self.env[MODEL].search(safe_eval(DOMAIN))
            if records:
                if statistic_id.custom_description_ids:
                    for desc in statistic_id.custom_description_ids:
                        vals = []
                        vals.append(desc.name) 
                        DOMAIN = desc.domain
                        if records:
                            desc_rec = self.env[MODEL].search(safe_eval(DOMAIN))
                            desc_rec = desc_rec.filtered(lambda rec:rec.id in records.ids)
                        else:
                            desc_rec = False
                        total_count = 0
                        for title in statistic_id.title_ids:
                            DOMAIN = title.domain
                            if desc_rec:
                                title_rec = self.env[MODEL].search(safe_eval(DOMAIN))
                                title_count = len(title_rec.filtered(lambda rec:rec.id in desc_rec.ids))
                            else:
                                title_count = 0
                            total_count = total_count + title_count
                            vals.append(title_count)
                        vals.append(total_count)
                        values.append(vals)
                    count_list = ["Total"]
                    for index in range(1, len(statistic_id.title_ids) + 2):
                        count = 0
                        for list in values:
                            count = count + list[index]
                        count_list.append(count)
                    values.append(count_list)
                    return {'no_rec':0,'name': sheet_id.name,'datas': values,'id':sheet_id.id,
                            'head_table': 0,'fields': titles,'cus_stat': 1,}
                else:
                    return {'no_rec':1}
            else:
                return {'no_rec':1}
  
    def directory_view(self):
        name = self.name or "Cristo"
        if self.sheet_ids:
            return{
                'name': name,
                'type': 'ir.actions.client',
                'tag': 'directory_report_dashboard'
            }
        else:
            raise UserError(_("Sorry! No sheets found in this directory"))

    def directory_download(self):
        if self.sheet_ids:
            values = []
            data = {}
            directory = self.id
            sheets = self.sheet_ids
            for sheet in sheets:
                result = self.get_sheet_values(directory,sheet.id)
                values.append(result)
            data.update({'directory':values})
            return self.env.ref('cristo_directory.directory_report_xlsx').report_action(self, data=data)
        else:
            raise UserError(_("Sorry! No sheets found in this directory"))

    @api.model
    def get_directory_report_details(self, directory):
        data = {}
        directory_files = []
        uid = request.session.uid
        user = self.env['res.users'].sudo().browse(uid)
        if user:
            result = self.env['res.users'].sudo().search_read([('id', '=', user.id)], fields=['id','name'], limit=1)
            directory_id = self.env['res.directory'].search([('id','=',directory)],limit=1)
            sheet_ids = self.env['res.directory.sheet'].search([('directory_id','=',directory_id.id)])
            name = directory_id.name
            sheets = []
            for sheet in sheet_ids:
                sheets.append({'id':sheet.id,'name':sheet.name})
            if directory_id.rel_province_id:
                directories = self.env['res.directory.file'].search([('rel_province_id','=',directory_id.rel_province_id.id),('status','!=','active')])
                for directory in directories:
                    directory_files.append({'id':directory.id,'name':directory.name})
            data.update({
                "dir":1,
                "directory" :directory_id,
                "sheets":sheets,
                "name":name,
                "province":directory_id.rel_province_id.id,
                "directory_files":directory_files if directory_files else False,
            })
            result[0].update(data)
            return result


class DirectorySheet(models.Model):
    _name = "res.directory.sheet"
    _description = "Directory Sheet"
    _order = 'sequence'

    name = fields.Text(strinng="Sheet Name", required="True")
    sequence = fields.Integer(string="Sequence")
    model_id = fields.Many2one('ir.model', string='Based on model')
    based_on = fields.Char(related='model_id.model', readonly=True, store=True)
    directory_id = fields.Many2one('res.directory', string="Directory")
    domain = fields.Text(string='Domain')
    statistic_ids = fields.One2many('res.statistic.count', 'sheet_id', string="Statistics", ondelete="cascade")
    type = fields.Selection([('filter','Filter'),('statistic','Statistic')], string="Type", default="filter")
    is_date_filter = fields.Boolean(string="Sort by Date",default=False)
    sheet_field_ids = fields.One2many('res.sheet.fields','sheet_id',string="Fields",ondelete="cascade")
    user_id = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user)
    religious_field_ids = fields.One2many('res.religious.fields','sheet_id', string="Religious Fields")
    sub_model_ids = fields.One2many('res.sub.model.fields','sheet_id', string="Sub Model")
    main_sheet_field_ids = fields.One2many('res.sheet.fields', 'main_sheet_id', string="Fields", ondelete="cascade")
    date_field_ids = fields.One2many('res.sheet.fields', 'date_sheet_id', string="Date Fields", ondelete="cascade")
    custom_statistic = fields.Boolean(string="Custom Statistic")
    custom_statistic_ids = fields.One2many('custom.statistic.count','sheet_id', string="Custom Statistic")

    @api.constrains('is_date_filter','sheet_field_ids')
    def field_count_validation(self):
        for rec in self:
            if rec.is_date_filter:
                if len(rec.sheet_field_ids) > 1:
                    raise UserError(_("Sorry! Only one field allowed for sort by date option"))

    @api.onchange('is_date_filter')
    def onchange_date_filter(self):
        for rec in self:
            if rec.is_date_filter:
                rec.sub_model_ids = False

    @api.onchange("type")
    def _onchange_type(self):
        for rec in self:
            if rec.type == "statistic":
                rec.is_date_filter = False
                rec.date_field_ids = False

class ResStatisticCount(models.Model):
    _name = 'res.statistic.count'
    _description = "Statistics Count"

    name = fields.Char(string="Name", required="True")
    sheet_id = fields.Many2one('res.directory.sheet', string="Sheet Name")
    model_id = fields.Many2one('ir.model', string='Based on model', required=True)
    based_on = fields.Char(related='model_id.model', readonly=True, store=True)
    domain = fields.Text(string="Domain")
    count = fields.Integer(string="Statistic Count", compute="_onchange_domain")

    @api.depends("domain")
    def _onchange_domain(self):
        self.count = False
        for rec in self:
            if rec.model_id:
                Model = self.env[rec.model_id.model]
                rec.count = Model.search_count(safe_eval(rec.domain))

class ResSheetFields(models.Model):
    _name = 'res.sheet.fields'
    _description = "Sheet Fields"
    _order = 'sequence'

    name = fields.Char(string="Display Name")
    sequence = fields.Integer(string="Sequence")
    field_id = fields.Many2one('ir.model.fields', string="Field",ondelete="cascade", required=True)
    sheet_id = fields.Many2one('res.directory.sheet', string="Sheet Name",ondelete="cascade")
    main_sheet_id = fields.Many2one('res.directory.sheet', string="Main Sheet Name",ondelete="cascade")
    religious_field_id = fields.Many2one('res.religious.fields', string="Religious",ondelete="cascade")
    sub_model_id = fields.Many2one('res.sub.model.fields', string="Sub Model",ondelete="cascade")
    rel_sub_model_id = fields.Many2one('res.sub.model.relation.fields',ondelete="cascade")
    date_sheet_id = fields.Many2one('res.directory.sheet', string="Sheet Name",ondelete="cascade")

class ReligiousFields(models.Model):
    _name = 'res.religious.fields'
    _description = "Religious Fields"

    name = fields.Char(string='Header Name',required=True)
    type = fields.Selection([('cong','Congregation'),('prov','Province'),('house','House/Community'),('inst','Institution')], string="Type")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict")
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province", ondelete="restrict")
    community_id = fields.Many2one('res.community', string="House/Community", ondelete="restrict")
    institution_id = fields.Many2one('res.institution', string="Institution", ondelete="restrict")
    field_ids = fields.One2many('res.sheet.fields', 'religious_field_id', string="Fields", ondelete="cascade")
    model_id = fields.Char(string="Model Name")
    sheet_id = fields.Many2one('res.directory.sheet', string="Sheet Name")


    @api.onchange('type')
    def _onchange_type(self):
        self.institute_id = False
        self.rel_province_id = False
        self.community_id = False
        self.institution_id = False
        self.field_ids = False
        self.model_id = False
        for rec in self:
            if rec.type == 'cong':
                rec.model_id = rec.institute_id._name
            if rec.type == 'prov':
                rec.model_id = rec.rel_province_id._name
            if rec.type == 'house':
                rec.model_id = rec.community_id._name
            if rec.type == 'inst':
                rec.model_id = rec.institution_id._name

class ResRelationFields(models.Model):
    _name = 'res.sub.model.fields'
    _description = "Sub Model Filelds"

    type = fields.Selection([('one2many','One2many'),('many2one','Many2one')],string="Field Type")
    field_id = fields.Many2one('ir.model.fields', string="Field Name")
    sub_model = fields.Char(string="Sub Model")
    domain = fields.Text(string="Domain")
    field_ids = fields.One2many('res.sheet.fields','sub_model_id', string="Field Names")
    sheet_id = fields.Many2one('res.directory.sheet', string="Sheet Name")
    relation_model_ids = fields.One2many('res.sub.model.relation.fields','sub_model_id',string="Relation Model")

    @api.onchange('field_id')
    def _onchange_field_id(self):
        self.sub_model = False
        if self.field_id:
            self.sub_model = self.field_id.relation
            self.type = self.field_id.ttype

class ResSubRelationFields(models.Model):
    _name = 'res.sub.model.relation.fields'
    _description = "Sub Model Relation Fields"

    type = fields.Selection([('one2many', 'One2many'), ('many2one', 'Many2one')], string="Field Type")
    field_id = fields.Many2one('ir.model.fields', string="Field Name")
    sub_model = fields.Char(string="Sub Model")
    domain = fields.Text(string="Domain")
    field_ids = fields.One2many('res.sheet.fields', 'rel_sub_model_id', string="Field Names")
    sub_model_id = fields.Many2one('res.sub.model.fields', string="Sub Model Name")

    @api.onchange('field_id')
    def _onchange_field_id(self):
        self.sub_model = False
        if self.field_id:
            self.sub_model = self.field_id.relation
            self.type = self.field_id.ttype
            
class CustomTitle(models.Model):
    _name = "directory.title"
    
    name = fields.Char(string="Name")
    custom_title_id = fields.Many2one('custom.statistic.count',string="Custom Title")
    domain = fields.Text(string="Domain")
    model_id = fields.Many2one('ir.model', string='Based on model', required=True)
    based_on = fields.Char(related='model_id.model', readonly=True, store=True)
    
class CustomStatisticCount(models.Model):
    _name = "statistic.description"
     
    name = fields.Char(string="Description")
    domain = fields.Text(string="Domain")
    model_id = fields.Many2one('ir.model', string='Based on model', required=True)
    based_on = fields.Char(related='model_id.model', readonly=True, store=True)
    title_id = fields.Many2one('custom.statistic.count', string="Custom Title")
            
class CustumStatisticTitle(models.Model):
    _name = "custom.statistic.count"
     
    name = fields.Char(string="Description Title")
    model_id = fields.Many2one('ir.model', string='Based on model', required=True)
    based_on = fields.Char(related='model_id.model', readonly=True, store=True)
    domain = fields.Text(string="Domain")
    title_ids =fields.One2many('directory.title','custom_title_id',string="Title")
    custom_description_ids = fields.One2many('statistic.description','title_id', string="Custom Count")
    sheet_id = fields.Many2one('res.directory.sheet',string="Sheet")
     
             
     
    