from odoo.tests import common,new_test_user
from odoo.exceptions import AccessError

class TestAssociate(common.TransactionCase):
    
    def setUp(self):
        super(TestAssociate,self).setUp()
        
        self.associate = self.env['res.partner'].create({'name':'Durai','code':'TST123',
                                                              'mobile':'1234567890','phone':'123456',
                                                              })
        self.user = new_test_user(self.env, login='charles', groups='base.group__admin')

      
    def test_check_associate_user_read(self):
        with self.assertRaises(AccessError):
            self.associate.with_user(self.user).read()

    def test_check_associate_user_unlink(self):
        with self.assertRaises(AccessError):
            self.associate.with_user(self.user).unlink()

    def test_check_associate_user_create(self):
        with self.assertRaises(AccessError):
            self.associate.with_user(self.user).create({'name':'Durai','code':'TST123',
                                                              'mobile':'1234567890','phone':'123456',
                                                              })
    def test_check_associate_user_write(self):
        with self.assertRaises(AccessError):
            self.associate.with_user(self.user).write({'name':'Durai','code':'TST123',
                                                              'mobile':'1234567890','phone':'123456',
                                                              })

class TestAssociateBaseuser(common.TransactionCase):

    def setUp(self):
        super(TestAssociateBaseuser, self).setUp()

        self.user = new_test_user(self.env, login='charles', groups='base.group_user')
        self.associate = self.env['res.partner'].create({'name':'Durai','code':'TST123',
                                                              'mobile':'1234567890','phone':'123456',
                                                              })
    def test_associate_base_user(self):
        with self.assertRaises(AccessError):
            self.associate.with_user(self.user).read()