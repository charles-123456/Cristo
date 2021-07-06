from odoo import models, fields, api, _
from odoo import tools, api
from odoo.exceptions import UserError

class ResAsset(models.Model):
    _name = 'res.asset'
    _inherit = ["common.rel.fields",'attachment.size']
    _description = "Asset"
    
    name = fields.Char(string='Name of the Asset', required=True)
    asset_code = fields.Char(string='Asset Code', size=8)
    location_id = fields.Many2one('asset.location', string='Location')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, default=lambda self: self.env.user.company_id.currency_id.id)
    value = fields.Float(string='Value', required=True)
    asset_type = fields.Selection([
                            ('immovable','Immovable'),
                            ('movable','Movable'),
                            ])
    asset_category_id = fields.Many2one('asset.category', string='Asset Category')
    sub_asset_category_id = fields.Many2one('asset.category', string="Sub Asset Category")
    attachment_ids = fields.Many2many('ir.attachment', string='Files')
    diocese_id = fields.Many2one('res.ecclesia.diocese', string = 'Diocese')
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate", domain="[('diocese_id','=',diocese_id)]" )
    parish_id = fields.Many2one('res.parish', string="Parish", domain="[('vicariate_id','=',vicariate_id)]")
    land_ref_no = fields.Char(string = 'Ref.No')
    land_no = fields.Char(string = "LD NO")
    land_village_name = fields.Char(string = 'Village Name')
    total_area = fields.Float(string="Area(Cent/Acres)")
    tax_payable = fields.Float(string="Annual Tax Payable")
    land_classification_id = fields.Many2one('land.classification', string="Land Classification")
    purchase_date = fields.Date(string="Purchase Date")
    purchase_price = fields.Float(string="Orginal Purchase Price")
    date_of_disposal = fields.Date(string="Date of Disposal")
    sold_price = fields.Float(string="Sold Price")
    building_type_id = fields.Many2one('building_type', string="Building Type")
    plinth_area = fields.Char(string="Plinth Area")
    date_of_commencement = fields.Date(string="Date of Commencement")
    construction_cost = fields.Float(string="Construction Cost")
    species_id = fields.Many2one('tree.species', string="Species")
    number_species = fields.Char(string="Number of Species")
    where_situated = fields.Char(string="Where Situated")
    yiels = fields.Char(string="Approximate Yiels Annum")
    date_of_destruction = fields.Date("Date of Destruction")
    amount = fields.Char(string="Amount")
    machinery_id = fields.Many2one('machinery.type', string="Machinery Name")
    number_of_machinery = fields.Char(string="Number of Machinery")
    date_of_purchase = fields.Date(string="Date of Purchase")
    paid_amount = fields.Float(string="Paid Amount")
    date_of_repair = fields.Date(string="Date of Repair")
    repair_cost = fields.Float(string="Repair Cost")
    
    
    land_taluk_name = fields.Char(string = 'Taluk Name') 
    land_location = fields.Char(string = 'Land Location')
    land_survey_no = fields.Char(string = 'Survey No')
    land_subdivision_no = fields.Char(string = "Sub-Division No")
    ta_hectare = fields.Float(string = 'Hectare')
    ta_are = fields.Float(string = "Are")
    ta_acre = fields.Float(string = 'Acre')
    ta_cent = fields.Float(string = 'Cent')
    tpa_hectare = fields.Float(string = 'Hectare')
    tpa_are = fields.Float(string = "Are")
    tpa_acre = fields.Float(string = 'Acre')
    tpa_cent = fields.Float(string = 'Cent')
    land_doc_no = fields.Char(string = 'Document No')
    land_doc_date = fields.Date(string = 'Date')
    land_patta_no = fields.Char(string = 'Patta No')
    land_volume = fields.Char(string = 'Volume')
    land_doc_page = fields.Integer(string = "Page No")
    seller_name = fields.Char(string = "Seller Name")
    seller_street = fields.Char("Address line 1", help="Address line 1")
    seller_street2 = fields.Char("Area/Street", help="Area/Street")
    seller_place = fields.Char('Place', help="Place")
    seller_zip = fields.Char("Zip", help="ZIP")
    seller_city = fields.Char("City", help="City/Town/Taluk")
    seller_state_id = fields.Many2one("res.country.state", "State", help="State")
    seller_country_id = fields.Many2one('res.country', "Country", help="Country")
    seller_website = fields.Char("Website")
    seller_phone = fields.Char("Phone(Landline)")
    seller_mobile = fields.Char("Mobile")
    seller_email = fields.Char("Email")
    seller_district_id = fields.Many2one('res.state.district', 'District')
    buyer_name = fields.Char(string = "Buyer Name")
    buyer_street = fields.Char("Address line 1", help="Address line 1")
    buyer_street2 = fields.Char("Area/Street", help="Area/Street")
    buyer_place = fields.Char('Place', help="Place")
    buyer_zip = fields.Char("Zip", help="ZIP")
    buyer_city = fields.Char("City", help="City/Town/Taluk")
    buyer_state_id = fields.Many2one("res.country.state", "State", help="State")
    buyer_country_id = fields.Many2one('res.country', "Country", help="Country")
    buyer_website = fields.Char("Website")
    buyer_phone = fields.Char("Phone(Landline)")
    buyer_mobile = fields.Char("Mobile")
    buyer_buyer_email = fields.Char("Email")
    buyer_district_id = fields.Many2one('res.state.district', 'District')
    land_register_at = fields.Char(string = 'Register at')
    name_of_the_priest = fields.Char(string = 'Name of the Religious Member')
    remark = fields.Text(string = 'Remark')
    user_id = fields.Many2one('res.users','User',default=lambda self: self.env.user)

    @api.constrains('attachment_ids')
    def _check_attachment_size(self):
        print(self.attachment_max_size)
        self.env['ir.attachment']._check_size(self.attachment_ids)
        
    @api.onchange('asset_type')
    def onchange_asset_type(self):
        if self.asset_type:
            self.asset_category_id = ''
            self.sub_asset_category_id = ''
    
    @api.onchange('seller_district_id', 'seller_state_id', 'seller_country_id')
    def onchange_seller_address(self):
        if self.seller_district_id:
            self.seller_state_id = self.seller_district_id.state_id.id
            self.seller_country_id = self.seller_district_id.state_id.country_id.id
            
    @api.onchange('buyer_district_id', 'buyer_state_id', 'buyer_country_id')
    def onchange_buyer_address(self):
        if self.buyer_district_id:
            self.buyer_state_id = self.buyer_district_id.state_id.id
            self.buyer_country_id = self.buyer_district_id.state_id.country_id.id
            
    @api.onchange('ta_hectare')
    def onchange_ta_hectare(self):
        if self.ta_hectare:
            self.ta_are = self.ta_hectare * 100
            self.ta_acre = self.ta_hectare * 2.47
            self.ta_cent = self.ta_hectare * 247.10
            
    @api.onchange('ta_are')
    def onchange_ta_are(self):
        if self.ta_are:
            self.ta_hectare = self.ta_are * 0.01
            self.ta_acre = self.ta_are * 0.0247106
            self.ta_cent = self.ta_are * 2.47067686
            
    @api.onchange('ta_acre')
    def onchange_ta_acre(self):
        if self.ta_acre:
            self.ta_hectare = self.ta_acre * 0.404686
            self.ta_are = self.ta_acre * 40.4686
            self.ta_cent = self.ta_acre * 100
            
    @api.onchange('ta_cent')
    def onchange_ta_cent(self):
        if self.ta_cent:
            self.ta_hectare = self.ta_cent * 0.004046857
            self.ta_acre = self.ta_cent * 0.01
            self.ta_are = self.ta_cent * 0.40468564225
            
    @api.onchange('tpa_hectare')
    def onchange_tpa_hectare(self):
        if self.tpa_hectare:
            self.tpa_are = self.tpa_hectare * 100
            self.tpa_acre = self.tpa_hectare * 2.47
            self.tpa_cent = self.tpa_hectare * 247.10
            
    @api.onchange('tpa_are')
    def onchange_tpa_are(self):
        if self.tpa_are:
            self.tpa_hectare = self.tpa_are * 0.01
            self.tpa_acre = self.tpa_are * 0.0247106
            self.tpa_cent = self.tpa_are * 2.47067686
            
    @api.onchange('tpa_acre')
    def onchange_tpa_acre(self):
        if self.tpa_acre:
            self.tpa_hectare = self.tpa_acre * 0.404686
            self.tpa_are = self.tpa_acre * 40.4686
            self.tpa_cent = self.tpa_acre * 100
            
    @api.onchange('tpa_cent')
    def onchange_tpa_cent(self):
        if self.tpa_cent:
            self.tpa_hectare = self.tpa_cent * 0.004046857
            self.tpa_acre = self.tpa_cent * 0.01
            self.tpa_are = self.tpa_cent * 0.40468564225
    
ResAsset()
