from odoo.tests import common,new_test_user

class TestAssociateUsers(common.TransactionCase):
    
    def setUp(self):
        super(TestAssociateUsers,self).setUp()
        
        self.associate = self.env['res.partner'].create({'name':'Durai','code':'TST123',
                                                              'mobile':'1234567890','phone':'123456',
                                                              })
        self.user = new_test_user(self.env, login='charles', groups='base.group__admin')
    
    def test_check_associate(self):
        self.assertEqual(self.associate.name,'Durai')
        self.assertEqual(self.associate.code,'TST123')
        self.assertEqual(self.associate.mobile,'1234567890')
        self.assertEqual(self.associate.phone,'123456')

      
