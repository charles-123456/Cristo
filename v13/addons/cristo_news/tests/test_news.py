# -*- coding: utf-8 -*-
from odoo.tests import common,new_test_user
from odoo import fields
from odoo.exceptions import AccessError

class TestNews(common.TransactionCase):
    
    def setUp(self):
        super(TestNews, self).setUp()
        
        self.user = new_test_user(self.env, login='bsaadmin', groups='cristo.group_role_cristo_bsa_super_admin')        
        self.congregation = self.env['res.religious.institute'].create({'name': 'Test Congregation'})
        self.rel_province_id = self.env['res.religious.province'].create({'name': 'Test Province', 'institute_id': self.congregation.id})
        
        self.ecc_region = self.env['res.ecclesia.region'].create({'name': 'Test Ecc region', 'code': 'Code'})
        self.ecc_province_id = self.env['res.ecclesia.province'].create({'name': 'Test Ecc Province', 'ecc_reg_id': self.ecc_region.id})
        self.diocese_id = self.env['res.ecclesia.diocese'].create({'name': 'Test Diocese', 'code': 'Test code', 'ecc_province_id': self.ecc_province_id.id})
        
        self.community_id = self.env['res.community'].create({'name': 'Test Community', 'institute_id': self.congregation.id, 'rel_province_id': self.rel_province_id.id})       
        self.news = self.env['res.news'].create({'name': 'Test', 
                                                 'state': 'publish', 
                                                 'is_house': False,
                                                 'institute_id':self.congregation.id,
                                                 'rel_province_id':self.rel_province_id.id,
                                                 'community_id': self.community_id.id,  
                                                 'description': 'Test_Description'})
    
    def test_check_news(self):
        self.assertEqual(self.news.name,'Test')
        self.assertEqual(self.news.state,'publish')
        self.assertEqual(self.news.is_house,False)
        self.assertEqual(self.news.institute_id.id, self.congregation.id)
        self.assertEqual(self.news.rel_province_id.id, self.rel_province_id.id)
        self.assertEqual(self.news.community_id.id, self.community_id.id)
        
    def test_with_bsa_admin_read(self):
        with self.assertRaises(AccessError):
            self.news.with_user(self.user).read()

    def test_with_bsa_admin_create(self):
        with self.assertRaises(AccessError):
            self.news.with_user(self.user).create({'name': 'Test BSA Create'})
    
    def test_with_bsa_admin_write(self):
        with self.assertRaises(AccessError):
            self.news.with_user(self.user).write({'name': 'Test BSA'})
            
    def test_with_bsa_admin_unlink(self):
        with self.assertRaises(AccessError):
            self.news.with_user(self.user).unlink()
