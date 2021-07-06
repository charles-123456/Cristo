# -*- coding: utf-8 -*-
from odoo.tests import common

class TestConcern(common.TransactionCase):
    
    def setUp(self):
        super(TestConcern, self).setUp()
        
        self.assigned = self.env['res.partner'].search([('main_category_code', '=', 'MR'), ('id', '=', 38009)], limit=1)
        self.concern = self.env['cristo.concern'].create({'name': 'Test','assigned_id': self.assigned.id})
        
    def test_check_concern(self):
        self.assertEqual(self.concern.name,'Test')
       