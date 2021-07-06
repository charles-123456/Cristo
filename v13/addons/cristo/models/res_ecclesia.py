# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.addons.cristo.models.res_common import Partner_Excluded_Fields, Mail_Excluded_Fields
from odoo.addons.cristo.tools import cris_tools
from lxml import etree

DAYS = []
for d in range(1, 32):
    DAYS.append((str(d), str(d)))

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
    ('12', 'December'),
]

Common_Excluded_Fields = Partner_Excluded_Fields + Mail_Excluded_Fields

class EcclesiaRegion(models.Model):
    _name = 'res.ecclesia.region'
    _description = 'Ecclesia Region'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Common_Excluded_Fields

    @api.model
    def default_get(self, fields):
        data = super(EcclesiaRegion, self).default_get(fields)
        main_category = self.env['res.main.category'].search([('code', '=', 'ER')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        return data
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete = "cascade", required=True)
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(EcclesiaRegion, self).unlink()
        return contacts.unlink()
    
class EcclesiaProvince(models.Model):
    _name = 'res.ecclesia.province'
    _description = 'Ecclesia Province'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Common_Excluded_Fields
    
    @api.model
    def default_get(self, fields):
        data = super(EcclesiaProvince, self).default_get(fields)
        mc_code = self._context.get('mc_code')
        user = self.env.user
        main_category = self.env['res.main.category'].search([('code', '=', 'EP')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['ecc_reg_id'] = user.ecc_reg_id.id
        return data    
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete = "cascade", required=True)
    ecc_reg_id = fields.Many2one('res.ecclesia.region',string="Region", ondelete="restrict",required=True, tracking=True)
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(EcclesiaProvince, self).unlink()
        return contacts.unlink()
    
class EcclesiaDiocese(models.Model):
    _name = 'res.ecclesia.diocese'
    _description = 'Ecclesia Diocese'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading','mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Common_Excluded_Fields
    _order = 'name'
    
    @api.model
    def default_get(self, fields):
        data = super(EcclesiaDiocese, self).default_get(fields)
        user = self.env.user
        main_category = self.env['res.main.category'].search([('code', '=', 'DI')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['ecc_province_id'] = user.ecc_province_id.id
        return data
    
    @api.constrains('establishment_date')
    def _validate_future_establishment_date(self):
        if self.establishment_date:
            cris_tools.future_date_validation(self.establishment_date,field_name="Establishment Date")
    
    
    def open_vicariates(self):
        action = self.env.ref('cristo.action_vicariate').read()[0]
        action.update({
            'domain': [('diocese_id','=',self.id)],
            'context': "{'default_diocese_id':%d}" % (self.id),
        })
        return action
    
    def open_parishes(self):
        action = self.env.ref('cristo.action_parish').read()[0]
        action.update({
            'domain': [('diocese_id','=',self.id)],
            'context': "{'default_diocese_id':%d}" % (self.id),
        })
        return action
    
    def open_communities(self):
        action = self.env.ref('cristo.action_ecclesia_community').read()[0]
        action.update({
            'domain': [('diocese_id','=',self.id),('owned_by','=','diocese')],
            'context': "{'default_diocese_id':%d}" % (self.id),
        })
        return action
    
    def open_institutions(self):
        action = self.env.ref('cristo.action_ecclesia_institution').read()[0]
        action.update({
            'domain': [('diocese_id','=',self.id)],
            'context': "{'default_diocese_id':%d}" % (self.id),
        })
        return action
    
    def open_families(self):
        action = self.env.ref('cristo.action_res_family').read()[0]
        action.update({
            'domain': [('diocese_id','=',self.id)],
            'context': "{'default_diocese_id':%d}" % (self.id),
        })
        return action
    
    def open_members(self):
        action = self.env.ref('cristo.action_res_member').read()[0]
        action.update({
            'domain': [('diocese_id','=',self.id),('member_type','=','member'),('membership_type','=','LT')],
            'context': "{'default_diocese_id':%d}" % (self.id),
        })
        return action
    
    def _compute_vicariate_count(self):
        for rec in self:
            rec.vicariate_count = self.env['res.vicariate'].sudo().search_count([('diocese_id', '=', rec.id)])
    
    def _compute_parish_count(self):
        self.parish_count = self.env['res.parish'].sudo().search_count([('diocese_id', '=', self.id)])
        
    def _compute_community_count(self):
        self.community_count = self.env['res.community'].sudo().search_count([('diocese_id', '=', self.id),('owned_by','=','diocese')])
    
    def _compute_institution_count(self):
        self.institution_count = self.env['res.institution'].sudo().search_count([('diocese_id', '=', self.id)])
        
    def _compute_family_count(self):
        self.family_count = self.env['res.family'].sudo().search_count([('diocese_id', '=', self.id)])
        
    def _compute_member_count(self):
        self.member_count = self.env['res.member'].sudo().search_count([('diocese_id', '=', self.id),('member_type', '=', 'member'),('membership_type','=','LT')])
        
    vicariate_count = fields.Integer(compute="_compute_vicariate_count", string="Vicariates")
    parish_count = fields.Integer(compute='_compute_parish_count', string='Parishes')
    community_count = fields.Integer(compute='_compute_community_count', string='Communities')
    institution_count = fields.Integer(compute='_compute_institution_count', string='Institutions')
    family_count = fields.Integer(compute='_compute_family_count', string='Families')
    member_count = fields.Integer(compute='_compute_member_count', string='Members')
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete = "cascade", required=True)
    diocese_motto = fields.Char(string="Motto")
    vicariate_ids = fields.One2many('res.vicariate', 'diocese_id', string="Vicariates")
    parish_ids = fields.One2many('res.parish', 'diocese_id', string="Parishes")
    establishment_date = fields.Date(string="Establishment Date")
    cathedral = fields.Char(string="Cathedral")
    current_bishop_id = fields.Many2one('res.member', string="Bishop", tracking=True)
    history = fields.Html(string="History")
    language_ids = fields.Many2many('res.languages', string="Languages")
    ecc_province_id = fields.Many2one('res.ecclesia.province', string="Province", ondelete="restrict", required=True, tracking=True)
    diocese_logo = fields.Binary(string="Diocese Logo")
    income_type = fields.Selection([('income','Income Range'),('exact','Exact Range')], string="Income Type")
    patron_id = fields.Many2one('res.patron', string="Patron Saint")
    feast_day = fields.Selection(DAYS, string="Feast Day")
    feast_month = fields.Selection(MONTHS, string="Feast Month")
    is_archdiocese = fields.Boolean(string="Is Archdiocese?")
    deputy_bishop_role_id = fields.Many2one('res.member.role', string='Deputy Bishop called as')
    bishop_emeritus_id = fields.Many2one('res.member', string='Bishop Emeritus')
    generalate = fields.Integer(string="No. of Generalate", tracking=True)
    provincialate = fields.Integer(string="No. of Provincialate", tracking=True)
    regionalate = fields.Integer(string="No. of Regionalate", tracking=True)
    
    data_source = fields.Selection([('static','Static'),('extract','Extract')], string="Data Source")
    total_dio_priest = fields.Integer(string="No. of Diocesian Priest")
    total_rel_priest = fields.Integer(string="No. of Religious Priest ")
    total_parish = fields.Integer(string="No. of Parishes")
    total_dio_institutions = fields.Integer(string="No. of Diocese Institutions")
    total_rel_institutions = fields.Integer(string="No. of Religious Institutions")
    total_dio_health_center = fields.Integer(string="No. of Diocesian Health Center")
    total_rel_health_center = fields.Integer(string="No. of Religious Health Center")
    total_dio_formation_house = fields.Integer(string="No. of Diocesian Formation House")
    total_rel_formation_house = fields.Integer(string="No. of Religious Formation House")
    total_centers = fields.Integer(string="No. of Centers")
    total_cong_fathers = fields.Integer(string="Congregation of Fathers")
    total_cong_sisters = fields.Integer(string="Congregation of Sisters")
    total_cong_brothers = fields.Integer(string="Congregation of Brothers")
    total_rel_sisters = fields.Integer(string="No. of Religious - Sisters")
    total_rel_priest = fields.Integer(string="No. of Religious - Priest/Brothers")
    total_deaneries = fields.Integer(string="No. of Deaneries")
    total_dio_deaneries = fields.Integer(string="No. of Deaneries - Run by Diocese")
    total_rel_deaneries = fields.Integer(string="No. of Deaneries - Run by Religious")
    family_ids = fields.One2many('res.family','diocese_id', string="Family")
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(EcclesiaDiocese, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_province,cristo.group_role_cristo_religious_institute_admin'):
            for view in doc.xpath("//" + view_type):
                view.attrib['edit'] = 'false'
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(EcclesiaDiocese, self).unlink()
        return contacts.unlink()
    
class Vicariate(models.Model):
    _name = 'res.vicariate'
    _description = 'Vicariate'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading', 'mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Common_Excluded_Fields
    
    @api.constrains('establishment_date')
    def _validate_future_establishment_date(self):
        if self.establishment_date:
            cris_tools.future_date_validation(self.establishment_date,field_name="Establishment Date")
    
    @api.model
    def default_get(self, fields):
        data = super(Vicariate, self).default_get(fields)
        user = self.env.user
        main_category = self.env['res.main.category'].search([('code', '=', 'VI')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['diocese_id'] = user.diocese_id.id
        return data    
    
    def open_parishes(self):
        action = self.env.ref('cristo.action_parish').read()[0]
        action.update({
            'domain': [('vicariate_id','=',self.id)],
            'context': "{'default_vicariate_id':%d,'default_diocese_id': %d}" % (self.id,self.diocese_id.id),
        })
        return action
    
    def open_communities(self):
        action = self.env.ref('cristo.action_religious_community').read()[0]
        action.update({
            'domain': [('diocese_id','=',self.diocese_id.id)],
            'context': "{'default_diocese_id':%d}" % (self.diocese_id.id),
            
        })
        return action
    
    def open_families(self):
        action = self.env.ref('cristo.action_res_family').read()[0]
        action.update({
            'domain': [('vicariate_id','=',self.id)],
            'context': "{'default_vicariate_id':%d}" % (self.id),
        })
        return action
    
    def open_members(self):
        action = self.env.ref('cristo.action_res_member').read()[0]
        action.update({
            'domain': [('vicariate_id','=',self.id),('member_type','=','member'),('membership_type','=','LT')],
            'context': "{'default_vicariate_id':%d}" % (self.id),
        })
        return action
    
    def _compute_parish_count(self):
        self.parish_count = self.env['res.parish'].sudo().search_count([('vicariate_id', '=', self.id)])
        
    def _compute_community_count(self):
        self.community_count = self.env['res.community'].sudo().search_count([('diocese_id', '=', self.id)])
    
    def _compute_institution_count(self):
        self.institution_count = self.env['res.institution'].sudo().search_count([('diocese_id', '=', self.id)])
        
    def _compute_family_count(self):
        self.family_count = self.env['res.family'].sudo().search_count([('vicariate_id', '=', self.id)])
        
    def _compute_member_count(self):
        self.member_count = self.env['res.member'].sudo().search_count([('vicariate_id', '=', self.id),('member_type','=','member'),('membership_type','=','LT')])
        
    parish_count = fields.Integer(compute='_compute_parish_count', string='Parishes')
    community_count = fields.Integer(compute='_compute_community_count', string='Communities')
    institution_count = fields.Integer(compute='_compute_institution_count', string='Institutions')
    family_count = fields.Integer(compute='_compute_family_count', string='Families')
    member_count = fields.Integer(compute='_compute_member_count', string='Members')
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete = "cascade", required=True)
    establishment_date = fields.Date(string="Establishment Date")
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", required=True, ondelete="restrict", tracking=True)
    parish_ids = fields.One2many('res.parish','vicariate_id', string="Parish")
    current_vicar_forane_id = fields.Many2one('res.member',string="Vicar Forane", required=False, ondelete="restrict", tracking=True)
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(Vicariate, self).unlink()
        return contacts.unlink()
    
class Parish(models.Model):
    _name = 'res.parish'
    _description = 'Parish/Mission Station'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading', 'mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Common_Excluded_Fields
    _order = 'name'
    
    
    @api.constrains('establishment_date')
    def _validate_future_establishment_date(self):
        if self.establishment_date:
            cris_tools.future_date_validation(self.establishment_date,field_name="Establishment Date")
    
    @api.model
    def default_get(self, fields):
        data = super(Parish, self).default_get(fields)
        user = self.env.user
        main_category = self.env['res.main.category'].search([('code', '=', 'PA')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['diocese_id'] = user.diocese_id.id
        data['vicariate_id'] = user.vicariate_id.id
        return data
    
    def open_communities(self):
        action = self.env.ref('cristo.action_ecclesia_community').read()[0]
        action.update({
            'domain': [('parish_id','=',self.id),('owned_by','=','diocese')],
            'context': "{'default_parish_id':%d}" % (self.id),
        })
        return action
    
    def open_institutions(self):
        action = self.env.ref('cristo.action_ecclesia_institution').read()[0]
        action.update({
            'domain': [('parish_id','=',self.id)],
            'context': "{'default_parish_id':%d,'default_diocese_id':%d}" % (self.id,self.diocese_id.id),
        })
        return action
    
    def open_families(self):
        action = self.env.ref('cristo.action_res_family').read()[0]
        action.update({
            'domain': [('parish_id','=',self.id)],
            'context': "{'default_parish_id':%d}" % (self.id),
        })
        return action
    
    def open_members(self):
        action = self.env.ref('cristo.action_res_member').read()[0]
        action.update({
            'domain': [('parish_id','=',self.id),('member_type','=','member'),('membership_type','=','LT')],
            'context': "{'default_parish_id': %d,'default_member_type': '%s','default_membership_type': '%s'}" % (self.id,'member','LT'),
        })
        return action  
    
    def open_bccs(self):
        action = self.env.ref('cristo.action_parish_bcc').read()[0]
        action.update({
            'domain': [('parish_id','=',self.id)],
            'context': "{'default_parish_id':%d,'default_diocese_id':%d,'default_vicariate_id':%d}" % (self.id,self.diocese_id.id,self.vicariate_id.id),
        })
        return action
    
    def _compute_community_count(self):
        self.community_count = self.env['res.community'].sudo().search_count([('parish_id', '=', self.id),('owned_by','=','diocese')])
    
    def _compute_institution_count(self):
        self.institution_count = self.env['res.institution'].sudo().search_count([('parish_id', '=', self.id)])
        
    def _compute_family_count(self):
        self.family_count = self.env['res.family'].sudo().search_count([('parish_id', '=', self.id)])
        
    def _compute_member_count(self):
        self.member_count = self.env['res.member'].sudo().search_count([('parish_id', '=', self.id),('member_type','=','member'),('membership_type','=','LT')])
    
    def _compute_bcc_count(self):
        self.bcc_count = self.env['res.parish.bcc'].sudo().search_count([('parish_id', '=', self.id)])
       
    community_count = fields.Integer(compute='_compute_community_count', string='Communities')
    institution_count = fields.Integer(compute='_compute_institution_count', string='Institutions')
    family_count = fields.Integer(compute='_compute_family_count', string='Families')
    member_count = fields.Integer(compute='_compute_member_count', string='Members')
    bcc_count = fields.Integer(compute='_compute_bcc_count', string='BCCs')
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete = "cascade", required=True)
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict", tracking=True)
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate", tracking=True)
    establishment_date = fields.Date(string="Establishment Date")
    current_parishpriest_id = fields.Many2one('res.member', string="Parish Priest", tracking=True)
    history = fields.Html(string="History")
    parish_logo = fields.Binary(string="Parish Logo")
    church_in_regional_lang_ids = fields.Many2many('res.languages', string="Church in Regional Language")
    patron_id = fields.Many2one('res.patron', string="Patron", tracking=True)
    rite_id = fields.Many2one('res.rite', string="Rite")
    member_ids = fields.One2many('res.member', 'parish_id', string="Members")
    institution_ids = fields.One2many('res.institution', 'parish_id', string="Institutions")
    community_ids = fields.One2many('res.community', 'parish_id', string="Houses")
    bapt_cert_report_temp_id = fields.Many2one('ir.actions.report',string="Baptism Certificate Report Template")
    fam_card_report_temp_id = fields.Many2one('ir.actions.report',string="Family Card Report Template")    
    bcc_ids = fields.One2many('res.parish.bcc','parish_id', string="BCC")
    sub_station_ids = fields.One2many('res.parish.sub.station','parish_id', string="Sub Station")
    zone_ids = fields.One2many('res.ecclesia.zone','parish_id', string="Zone")
    family_ids = fields.One2many('res.family','parish_id', string="Family")
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(Parish, self).unlink()
        return contacts.unlink()
    
class ParishSubStation(models.Model):
    _name = 'res.parish.sub.station'
    _description = 'Parish Sub Station'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading', 'mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Common_Excluded_Fields
    
    @api.constrains('establishment_date')
    def _validate_future_establishment_date(self):
        if self.establishment_date:
            cris_tools.future_date_validation(self.establishment_date,field_name="Establishment Date")
    
    @api.model
    def default_get(self, fields):
        data = super(ParishSubStation, self).default_get(fields)
        user = self.env.user
        main_category = self.env['res.main.category'].search([('code', '=', 'SS')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['diocese_id'] = user.diocese_id.id
        data['vicariate_id'] = user.vicariate_id.id
        data['parish_id'] = user.parish_id.id
        return data 
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete = "cascade", required=True)
    parish_id = fields.Many2one('res.parish', required=True, ondelete="restrict", string="Parish", tracking=True)
    diocese_id = fields.Many2one('res.ecclesia.diocese', required=True, ondelete="restrict", string="Diocese", tracking=True)
    vicariate_id = fields.Many2one('res.vicariate', ondelete="restrict", string="Vicariate", tracking=True)
    establishment_date = fields.Date(string="Establishment Date")
    history = fields.Html(string="History")
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(ParishSubStation, self).unlink()
        return contacts.unlink()
    
class BasicChristianCommunity(models.Model):
    _name = 'res.parish.bcc'
    _description = "Parish Basic Christian Community"
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Common_Excluded_Fields
    
    @api.model
    def default_get(self, fields):
        data = super(BasicChristianCommunity, self).default_get(fields)
        user = self.env.user
        main_category = self.env['res.main.category'].search([('code', '=', 'BC')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['diocese_id'] = user.diocese_id.id
        data['vicariate_id'] = user.vicariate_id.id
        data['parish_id'] = user.parish_id.id
        return data 
    @api.constrains('establishment_date')
    def _validate_future_establishment_date(self):
        if self.establishment_date:
            cris_tools.future_date_validation(self.establishment_date,field_name="Establishment Date")
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete = "cascade", required=True)
    areas_covered = fields.Text(string="Parish Areas")
    establishment_date = fields.Date(string="Establishment Date")
    parish_id = fields.Many2one('res.parish', required=True, ondelete="restrict", string="Parish", tracking=True)
    diocese_id = fields.Many2one('res.ecclesia.diocese', required=True, ondelete="restrict", string="Diocese", tracking=True)
    vicariate_id = fields.Many2one('res.vicariate', ondelete="restrict", string="Vicariate", tracking=True)
    sub_station_id = fields.Many2one('res.parish.sub.station', required=False, ondelete="restrict", string="Sub Station")
    zone_id = fields.Many2one('res.ecclesia.zone', required=False, ondelete="restrict", string="Zone")
    bcc_head_id = fields.Many2one('res.member', required=False, ondelete="restrict", string="BCC Head")
    in_charge = fields.Char(string="In-Charge")
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(BasicChristianCommunity, self).unlink()
        return contacts.unlink()
    
class EcclesiaZone(models.Model):
    _name = 'res.ecclesia.zone'
    _description = "Ecclesia Zone"
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Common_Excluded_Fields
    
    @api.model
    def default_get(self, fields):
        data = super(EcclesiaZone, self).default_get(fields)
        user = self.env.user
        main_category = self.env['res.main.category'].search([('code', '=', 'EZ')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['diocese_id'] = user.diocese_id.id
        data['vicariate_id'] = user.vicariate_id.id
        data['parish_id'] = user.parish_id.id
        return data 
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete = "cascade", required=True)
    parish_id = fields.Many2one('res.parish', required=True, ondelete="restrict", string="Parish", tracking=True)
    category_id = fields.Many2one('res.ecclesia.zone.category', ondelete="restrict", string="Group")
    diocese_id = fields.Many2one('res.ecclesia.diocese', required=True, ondelete="restrict", string="Diocese", tracking=True)
    vicariate_id = fields.Many2one('res.vicariate', ondelete="restrict", string="Vicariate", tracking=True)

    in_charge = fields.Char(string="In-Charge")
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(EcclesiaZone, self).unlink()
        return contacts.unlink()
    
class EcclesiaZoneCategory(models.Model):
    _name = 'res.ecclesia.zone.category'
    _description = 'Ecclesia Zone Category'
    _order = 'name asc'
    
    name = fields.Char(string="Name")
    