from odoo.tests import common, new_test_user
from odoo.exceptions import AccessError

class TestConcernUser(common.TransactionCase):
    
    def setUp(self):
        super(TestConcernUser, self).setUp()
        
        self.institute = self.env['res.religious.institute'].create({'name': 'Vasanth','founder':'Vasanth Jagani','motto':'Thinking about Motto'})
        self.province = self.env['res.religious.province'].create({'institute_id':self.institute.id,'name': 'Eluru'})
        self.partner = self.env['res.partner'].create({'name':'Vasanth','main_category_id':19})
        self.user = new_test_user(self.env, login='jagani', groups='cristo_concern.group_concern_user',institute_id=self.institute.id,rel_province_id=self.province.id, partner_id=self.partner.id)
        self.concern = self.env['cristo.concern'].create({'name':'Durai','assigned_id':self.partner.id,'institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id})
    
    def test_ckeck_concern_user_read(self):
        with self.assertRaises(AccessError):
            self.concern.with_user(self.user).read()
    
    def test_check_concern_user_unlink(self):
        with self.assertRaises(AccessError):
            self.concern.with_user(self.user).unlink()
            
    def test_check_concern_user_create(self):
        with self.assertRaises(AccessError):
            self.concern.with_user(self.user).create({'name':'Paulo','assigned_id':self.partner.id,'institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id})
    
    def test_check_concern_user_write(self):
        with self.assertRaises(AccessError):
            self.concern.with_user(self.user).write({'name':'Antony Paulo','assigned_id':self.partner.id,'institute_id':self.user.institute_id.id,'rel_province_id':self.user.rel_province_id.id})
    
    def test_change_state(self):
        self.concern.write({'state':'reject'})
        
class TestConcernBaseuser(common.TransactionCase):
    
    def setUp(self):
        super(TestConcernBaseuser, self).setUp()
        
        self.user = new_test_user(self.env, login='jagani', groups='base.group_user')
        self.concern = self.env['cristo.concern'].create({'name':'Durai','assigned_id':38530})  
        
        
    def test_concern_base_user(self):
        with self.assertRaises(AccessError):
            self.concern.with_user(self.user).read()  