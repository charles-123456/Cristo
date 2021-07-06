from odoo.tests import common, new_test_user
from odoo.exceptions import AccessError

class TestCouncilUser(common.TransactionCase):
    
    def setUp(self):
        super(TestCouncilUser, self).setUp()
        
        self.institute = self.env['res.religious.institute'].create({'name': 'Vasanth','founder':'Vasanth Jagani','motto':'Thinking about Motto'})
        self.province = self.env['res.religious.province'].create({'institute_id':self.institute.id,'name': 'Eluru'})
        self.partner = self.env['res.partner'].create({'name':'Vasanth','main_category_id':19})
        
        self.user = new_test_user(self.env, login='jagani', groups='cristo_council.group_role_enable_council', institute_id=self.institute.id, rel_province_id=self.province.id, partner_id=self.partner.id)
        
        self.council = self.env['res.council'].create({'name':'Durai','user_id':self.user.id,'institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id})
    
    def test_ckeck_council_user_read(self):
        with self.assertRaises(AccessError):
            self.council.with_user(self.user).read()
    
    def test_check_council_user_unlink(self):
        with self.assertRaises(AccessError):
            self.council.with_user(self.user).unlink()
            
    def test_check_council_user_create(self):
        with self.assertRaises(AccessError):
            self.council.with_user(self.user).create({'name':'Paulo','user_id':self.user.id,'institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id})
    
    def test_check_council_user_write(self):
        with self.assertRaises(AccessError):
            self.council.with_user(self.user).write({'name':'Antony Paulo','user_id':self.user.id,'institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id})
    
class TestCouncilBaseuser(common.TransactionCase):
    
    def setUp(self):
        super(TestCouncilBaseuser, self).setUp()
        
        self.user = new_test_user(self.env, login='jagani', groups='base.group_user')
        self.council = self.env['res.council'].create({'name':'Durai','user_id':self.user.id})  
        
    def test_council_base_user(self):
        with self.assertRaises(AccessError):
            self.council.with_user(self.user).read()   
                 