# -*- coding: utf-8 -*-
from odoo.tests import common

class TestOrganizationCommon(common.TransactionCase):
    
    def setUp(self):
        super(TestOrganizationCommon, self).setUp()

        self.institute = self.env['res.religious.institute'].create({'name': 'Test','founder':'Augustin','motto':'Thinking about Motto'})
        self.region = self.env['res.religious.region'].create({'institute_id':self.institute.id,'name': 'Test'})
        self.province = self.env['res.religious.province'].create({'institute_id':self.institute.id,'name': 'Test'})
        
    def test_check_province(self):
        self.assertEqual(self.institute.id, self.province.institute_id.id)