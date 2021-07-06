from odoo import models, fields, api, _
from odoo import tools, api

class AssetCategory(models.Model):
    _name = 'asset.category'
    _description = "Asset Category"
    
    name = fields.Char('Category')
    asset_type = fields.Selection([
                                    ('immovable','Immovable'),
                                    ('movable','Movable'),
                                    ], required=True, string="Asset Type")
    code = fields.Char('Code', size=8)
    parent_id = fields.Many2one('asset.category', string="Parent")
    attribute1 = fields.Char('Attribute 1')
    attribute2 = fields.Char('Attribute 2')
    attribute3 = fields.Char('Attribute 3')
    attribute4 = fields.Char('Attribute 4')
    attribute5 = fields.Char('Attribute 5')
    attribute6 = fields.Char('Attribute 6')
    attribute7 = fields.Char('Attribute 7')
    attribute8 = fields.Char('Attribute 8')
    attribute9 = fields.Char('Attribute 9')
    attribute10 = fields.Char('Attribute 10')
    attribute11 = fields.Char('Attribute 11')
    attribute12 = fields.Char('Attribute 12')
    attribute13 = fields.Char('Attribute 13')
    attribute14 = fields.Char('Attribute 14')
    attribute15 = fields.Char('Attribute 15')
    attribute16 = fields.Char('Attribute 16')

class AssetLocation(models.Model):
    _name = "asset.location"
    _description = "Asset Location"
    
    name = fields.Char('Location')
    street = fields.Char("Address line 1", help="Address line 1")
    street2 = fields.Char("Area/Street", help="Area/Street")
    place = fields.Char('Place', help="Place")
    zip = fields.Char("Zip", help="ZIP")
    city = fields.Char("City", help="City/Town/Taluk")
    state_id = fields.Many2one("res.country.state", "State", help="State")
    country_id = fields.Many2one('res.country', "Country", help="Country")
    website = fields.Char("Website")
    phone = fields.Char("Phone(Landline)")
    mobile = fields.Char("Mobile")
    email = fields.Char("Email")
    district_id = fields.Many2one('res.state.district', 'District')

class LandClassification(models.Model):
    _name = 'land.classification'
    _description = "Land Classification"
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    
class BuildingType(models.Model):
    _name = 'building.type'
    _description = "Building Type"
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")

class TreeSpecies(models.Model):
    _name = 'tree.species'
    _description = "Tree Species"
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")


class MachineryType(models.Model):
    _name = 'machinery.type' 
    _description =  "Machinery Type"      
          
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")      