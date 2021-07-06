# -*- coding: utf-8 -*-
from odoo import fields, api, models, tools, _
from odoo.addons.cristo.tools import cris_tools
from odoo.exceptions import UserError, Warning
import base64, os
from odoo.modules.module import get_module_resource
from lxml import etree
from odoo.addons.cristo.models.res_common import Partner_Excluded_Fields, Mail_Excluded_Fields

Excluded_Fields = Partner_Excluded_Fields + Mail_Excluded_Fields

class AddressLoading(models.AbstractModel):
    _name = "address.loading"
    _description = "Address Loading"
    
    @api.onchange('district_id')
    def _onchange_district(self):
        if self.district_id:
            self.state_id = self.district_id.state_id.id
                
    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id

class PartnerClearCache(models.AbstractModel):
    _name = "partner.clear.cache"
    _description = "Partner Clear Cache"
    
    @api.model_create_multi
    def create(self, vals):
        partner = super(PartnerClearCache, self.sudo()).create(vals)
        self.clear_caches()
        return partner    
    
    def write(self, vals): 
        partner = super(PartnerClearCache, self.sudo()).write(vals)
        self.clear_caches()
        return partner     
    
class ResPartnerInherited(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner','address.loading']
    _rec_name = "full_name"
    _order = "name asc"
    _custom_filter_exclude_fields = Excluded_Fields
    
#     To Hide 'Merge' menu from actions menus
    @api.model
    def hide_merge_from_actions_menu(self):
        if self.env.ref('base.action_partner_merge',False):
            self.env.ref('base.action_partner_merge').unlink()
            
    @api.model
    def default_get(self, fields):
        data = super(ResPartnerInherited, self).default_get(fields)
        data['user_id'] = self.env.user.id
        main_category_id = self._context.get('default_is_outsider', False)
        if main_category_id:
            data['main_category_id'] = self.env['res.main.category'].search([('code','=', 'MR')], limit=1).id or False
        return data
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResPartnerInherited, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_individual') and self._context.get('is_member',False):
            for view in doc.xpath("//"+view_type):
                view.attrib['create'] = 'false'
                view.attrib['delete'] = 'false'
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
#     @api.model
#     def default_get(self, fields):
#         data = super(ResPartnerInherited, self).default_get(fields)
#         mc_code = self._context.get('mc_code')
#         if mc_code:
#             main_category = self.env['res.main.category'].search([('code', '=', mc_code)], limit=1)
#             data['main_category_id'] = main_category and main_category.id
#             if not self._context.get('import_file'):
#                 if mc_code in ['ER','EP','RR','RP']:
#                     data['image_1920'] = self._get_image('region_province.png')
#                 elif mc_code == "DI":
#                     data['image_1920'] = self._get_image('diocese.png')
#                 elif mc_code == "VI":
#                     data['image_1920'] = self._get_image('vicariate.png')
#                 elif mc_code == "PA":
#                     data['image_1920'] = self._get_image('parish.png')
#                 elif mc_code == "SS":
#                     data['image_1920'] = self._get_image('substation.png')
#                 elif mc_code == "EZ":
#                     data['image_1920'] = self._get_image('zone.png')
#                 elif mc_code == "BC":
#                     data['image_1920'] = self._get_image('bcc.png')
#                 elif mc_code == "FA":
#                     data['image_1920'] = self._get_image('family.png')
#                 elif mc_code == "MR":
#                     data['image_1920'] = self._get_image('member.png')
#                 elif mc_code == 'RC':
#                     data['image_1920'] = self._get_image('congregation.png')    
#                 elif mc_code == 'RZ':
#                     data['image_1920'] = self._get_image('zone.png')          
#         return data
#      
#     @api.model
#     def _get_image(self, image):
#         image_path = get_module_resource('cristo', 'static/img/', image)
#         if not image_path:
#             print("No Image Found")
#         else:
#             return base64.b64encode(open(image_path, 'rb').read())

    def _compute_full_name(self):
        for partner in self:
            name = partner.name 
            if partner.main_category_code == 'MR':
                member_id = self.env['res.member'].search([('partner_id','=',partner.id)],limit=1)
                name = (partner.title.name + ' ' + partner.name) if partner.title else partner.name
                name += ' ' + member_id.last_name if member_id.last_name else ''
            partner.full_name = name
            partner.display_name = name
            
    name = fields.Char(index=True,tracking=True)
    full_name = fields.Char(compute='_compute_full_name')
    email = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    website = fields.Char(tracking=True)
    street = fields.Char(tracking=True)
    city = fields.Char(tracking=True)
    place = fields.Char(string="Place", tracking=True)
    district_id = fields.Many2one('res.state.district', string="District", tracking=True)
    known_as = fields.Char(string="Known As")
    code = fields.Char(string="Code",tracking=True)
    fax = fields.Char(string="Fax")
    main_category_id = fields.Many2one('res.main.category', string="Main Category")
    main_category_code = fields.Char(related='main_category_id.code', string="Main Category Code")
    comment = fields.Text(string='Remarks')
    is_outsider = fields.Boolean(string="Outsider?")
    
    def name_get(self):
        return [(rec.id, ("%s" % (rec.full_name)) + (" (%s)" % rec.main_category_code if rec.main_category_code not in ['MR', False] else "" )) \
                for rec in self]
               
    @api.constrains('mobile')
    def _check_mobile(self):
        if self.country_id.code == 'IN':
            if self.mobile:
                cris_tools.mobile_validation(self.mobile)

    @api.constrains('phone')
    def _check_phone(self):
        if self.phone:
            pass
#             cris_tools.phone_validation(self.phone)
            
    @api.constrains('email')
    def _check_email(self):
        if self.email:
            cris_tools.email_validation(self.email)
    
    def explore_the_view(self):
        main_category = {
            'RR': ('cristo.action_religious_region', 'res.religious.region'),
            'RP': ('cristo.action_religious_province', 'res.religious.province'),
            'RC': ('cristo.action_religious_institute', 'res.religious.institute'),
            'RZ': ('cristo.action_religious_zone', 'res.religious.zone'),
            'HC': ('cristo.action_religious_community', 'res.community'),
            'CN': ('cristo.action_religious_community', 'res.community'),
            'RI': ('cristo.action_institution', 'res.institution'),
            'AS': ('cristo.action_association', 'res.association'),
            'ER': ('cristo.action_ecclesia_region', 'res.ecclesia.region'),
            'EP': ('cristo.action_ecclesia_province', 'res.ecclesia.province'),
            'DI': ('cristo.action_ecclesia_diocese', 'res.ecclesia.diocese'),
            'VI': ('cristo.action_vicariate', 'res.vicariate'),
            'PA': ('cristo.action_parish', 'res.parish'),
            'SS': ('cristo.action_parish_sub_station', 'res.parish.sub.station'),
            'EZ': ('cristo.action_ecclesia_zone', 'res.ecclesia.zone'),
            'BC': ('cristo.action_parish_bcc', 'res.parish.bcc'),
            'FA': ('cristo.action_res_family', 'res.family'),
            'MR': ('cristo.action_res_member', 'res.member'),
            'LE': ('cristo.action_legal_entity', 'res.legal.entity'),
        }
        if self.main_category_id:
            res_id = self.env[main_category[self.main_category_code][1]].search([('partner_id','=',self.id)], limit=1)
            if res_id:
                if self.main_category_code == 'MR':
                    if res_id.member_type == 'member':
                        action = self.env.ref('cristo.action_res_member').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_form').id
                    elif res_id.member_type == 'bishop' and res_id.membership_type == 'SE':
                        action = self.env.ref('cristo.action_res_bishop').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id
                    elif res_id.member_type == 'priest' and res_id.membership_type == 'SE':
                        action = self.env.ref('cristo.action_res_secular_priest').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id
                    elif res_id.member_type == 'deacon' and res_id.membership_type == 'SE':
                        action = self.env.ref('cristo.action_res_deacon').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id
                    elif res_id.member_type == 'brother' and res_id.membership_type == 'SE':
                        action = self.env.ref('cristo.action_res_secular_brother').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id    
                    elif res_id.member_type == 'bishop' and res_id.membership_type == 'RE':
                        action = self.env.ref('cristo.action_res_religious_bishop').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id
                    elif res_id.member_type == 'priest' and res_id.membership_type == 'RE':
                        action = self.env.ref('cristo.action_res_religious_priest').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id
                    elif res_id.member_type == 'lay_brother' and res_id.membership_type == 'RE':
                        action = self.env.ref('cristo.action_res_laybrother').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id
                    elif res_id.member_type == 'deacon' and res_id.membership_type == 'RE':
                        action = self.env.ref('cristo.action_res_religious_deacon').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id
                    elif res_id.member_type == 'brother' and res_id.membership_type == 'RE':
                        action = self.env.ref('cristo.action_res_brother').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id            
                    elif res_id.member_type == 'sister' and res_id.membership_type == 'RE':
                        action = self.env.ref('cristo.action_res_sister').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id
                    elif res_id.member_type == 'junior_sister' and res_id.membership_type == 'RE':
                        action = self.env.ref('cristo.action_res_junior_sister').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id
                    elif res_id.member_type == 'novice' and res_id.membership_type == 'RE':
                        action = self.env.ref('cristo.action_novice').read()[0]
                        view_id = self.env.ref('cristo.view_res_member_common_form').id                               
                    return {
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': main_category[self.main_category_code][1],
                        'view_id': view_id,
                        'res_id': res_id.id,
                        'context': action['context'],
                    }
                else:
                    action = self.env.ref(main_category[self.main_category_code][0]).read()[0]
                    action.update({
                        'views': [[False, 'form']],
                        'res_id': res_id.id
                        })
                    return action
            else:
                raise Warning("Record not accessible/found!")
        else:
            raise Warning("Main Category not found!")

    def get_formview_action(self, access_uid=None):
        res = super(ResPartnerInherited, self).get_formview_action(access_uid=access_uid)
        view_id = self.env.ref('cristo.view_cristo_res_partner_form').id
        res['views'] = [(view_id, 'form')]
        return res
    
#     @api.model_create_multi
#     def create(self, vals):
#         partner = super(ResPartnerInherited, self.sudo()).create(vals)
#         self.clear_caches()
#         return partner
#     
#     def write(self, vals): 
#         partner = super(ResPartnerInherited, self.sudo()).write(vals)
#         self.clear_caches()
#         return partner