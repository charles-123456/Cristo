from odoo.tests import common, new_test_user
from odoo.exceptions import AccessError

class TestAssetUser(common.TransactionCase):

    def setUp(self):
        super(TestAssetUser, self).setUp()

        self.institute = self.env['res.religious.institute'].create(
            {'name': 'Test Congregation', 'founder': 'Augustin', 'motto': 'Thinking about Motto'})
        self.province = self.env['res.religious.province'].create({'institute_id': self.institute.id, 'name': 'Test Province'})
        self.community_id = self.env['res.community'].create({'rel_province_id': self.province.id,'name': 'Test Community',})
        self.ecclesia_region = self.env['res.ecclesia.region'].create({'name':'Test Region','code':'TST22'})
        self.ecclesia_province = self.env['res.ecclesia.province'].create({'name':'Test eccprovice','ecc_reg_id':self.ecclesia_region.id})
        self.ecclesia_diocese = self.env['res.ecclesia.diocese'].create({'ecc_province_id':self.ecclesia_province.id,'name':'Test Diocese'})
        self.ecclesia_vicariate = self.env['res.vicariate'].create({'diocese_id':self.ecclesia_diocese.id,'name':'Test Vicariate','code':'TST'})
        self.ecclesia_parish = self.env['res.parish'].create({'name':'Test Parish','code':'TST'})
        
        self.user = new_test_user(self.env, login='charles', groups='cristo_asset.group_asset_user',
                                   institute_id=self.institute.id, rel_province_id=self.province.id,
                                   community_id=self.community_id.id,diocese_id=self.ecclesia_diocese.id,
                                   vicariate_id=self.ecclesia_vicariate.id,parish_id=self.ecclesia_parish.id)
        self.asset = self.env['res.asset'].create({
             'name': 'Test Asset', 'value':'24.44','asset_type':'immovable','institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id,'community_id':self.user.community_id.id,
             'diocese_id':self.user.diocese_id.id,'vicariate_id':self.user.vicariate_id.id,'parish_id':self.user.parish_id.id})
        
    def test_check_asset_user_read(self):
        with self.assertRaises(AccessError):
            self.asset.with_user(self.user).read()

    def test_check_asset_user_unlink(self):
        with self.assertRaises(AccessError):
            self.asset.with_user(self.user).unlink()

    def test_check_asset_user_create(self):
        with self.assertRaises(AccessError):
            self.asset.with_user(self.user).create({
                        'name': 'Create Asset', 'value':'24.44','asset_type':'immovable','institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id,'community_id':self.user.community_id.id,
                        'diocese_id':self.user.diocese_id.id,'vicariate_id':self.user.vicariate_id.id,'parish_id':self.user.parish_id.id})

    def test_check_asset_user_write(self):
        with self.assertRaises(AccessError):
            self.asset.with_user(self.user).write({
                        'name': 'Write Asset', 'value':'24,33.44','asset_type':'immovable','institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id,'community_id':self.user.community_id.id,
                        'diocese_id':self.user.diocese_id.id,'vicariate_id':self.user.vicariate_id.id,'parish_id':self.user.parish_id.id})


class TestAssetBaseuser(common.TransactionCase):

    def setUp(self):
        super(TestAssetBaseuser, self).setUp()

        self.user = new_test_user(self.env, login='charles', groups='base.group_user')
        self.asset = self.env['res.asset'].create({
             'name': 'Test Asset', 'value':'24.44','asset_type':'immovable','institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id,'community_id':self.user.community_id.id,
             'diocese_id':self.user.diocese_id.id,'vicariate_id':self.user.vicariate_id.id,'parish_id':self.user.parish_id.id})
        
    def test_asset_base_user(self):
        with self.assertRaises(AccessError):
            self.asset.with_user(self.user).read()