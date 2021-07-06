# -*- coding: utf-8 -*-
from odoo.tests import common,new_test_user
from odoo import fields
from odoo.exceptions import AccessError

class TestUserLicense(common.TransactionCase):
    
    def setUp(self):
        super(TestUserLicense, self).setUp()
        
        self.main_category = self.env['res.main.category'].create({'sequence': 100, 'name': 'Test category', 'code': 'Test code'})
        self.congregation = self.env['res.religious.institute'].search([('code', '=', 'Sl')], limit=1)
        self.rel_province = self.env['res.religious.province'].create({'name': 'Test Province', 'institute_id': self.congregation.id})
        self.community = self.env['res.community'].create({'name': 'Test Community', 'institute_id': self.congregation.id, 'rel_province_id': self.rel_province.id})
        
        self.ecc_region = self.env['res.ecclesia.region'].create({'name': 'Test Ecc region', 'code': 'Code'})
        self.ecc_province_id = self.env['res.ecclesia.province'].create({'name': 'Test Ecc Province', 'ecc_reg_id': self.ecc_region.id})
        self.diocese_id = self.env['res.ecclesia.diocese'].create({'name': 'Test Diocese', 'code': 'Test code', 'ecc_province_id': self.ecc_province_id.id})
        
        self.institution = self.env['res.institution'].create({'name': 'Test Institution', 'community_id': self.community.id,'diocese_id': self.diocese_id.id, 'street': 'Test street', 'city': 'City', 'zip': '5205200'})
        
        self.member_re = self.env['res.member'].create(
                {'name':'Test','unique_code':'TSTRE','member_type':'priest','membership_type':'RE',
                 'dob': fields.Date.from_string('2020-01-02')
                })
        self.member_se = self.env['res.member'].create(
                {'name':'Test','unique_code':'TSTSE','member_type':'priest','membership_type':'SE',
                 'dob': fields.Date.from_string('2020-01-02')
                })
        self.member_lt = self.env['res.member'].create(
                {'name':'Test lay person','unique_code':'TSTLT','member_type':'priest','membership_type':'LT',
                 'dob': fields.Date.from_string('2020-01-02')
                })
        
        self.user_license_re = self.env['user.license.expiry'].create(
            {'main_category_id': self.main_category.id, 'next_expiry_date': fields.Date.from_string('2021-08-02'), 
             'is_empty_date': False, 'institute_id': self.congregation.id, 'rel_province_id': self.rel_province.id, 
             'community_id': self.community.id, 'institution_id': self.institution.id, 'member_ids': self.member_re.ids})
        
        
        self.user_license_se = self.env['user.license.expiry'].create(
            {'main_category_id': self.main_category.id, 'next_expiry_date': fields.Date.from_string('2021-08-02'), 
             'is_empty_date': False, 'member_ids': self.member_se.ids})
        
        self.user_license_lt = self.env['user.license.expiry'].create(
            {'main_category_id': self.main_category.id, 'next_expiry_date': fields.Date.from_string('2021-08-02'), 
             'is_empty_date': True, 'member_ids': self.member_lt.ids})
        
        
    def test_check_user_license_re(self):
        self.assertEqual(self.user_license_re.main_category_id.id,self.main_category.id)
        self.assertEqual(self.user_license_re.next_expiry_date, fields.Date.from_string('2021-08-02'))
        self.assertEqual(self.user_license_re.is_empty_date, False)
        self.assertEqual(self.user_license_re.institute_id.id, self.congregation.id)
        self.assertEqual(self.user_license_re.rel_province_id.id, self.rel_province.id)
        self.assertEqual(self.user_license_re.community_id.id, self.community.id)
        self.assertEqual(self.user_license_re.institution_id.id, self.institution.id)
        self.assertEqual(self.user_license_re.member_ids.ids, self.member_re.ids)

    def test_check_user_license_se(self):
        self.assertEqual(self.user_license_se.main_category_id.id,self.main_category.id)
        self.assertNotEqual(self.user_license_se.next_expiry_date, fields.Date.from_string('2021-09-02'))
        self.assertFalse(self.user_license_se.is_empty_date)
        self.assertEqual(self.user_license_se.member_ids.ids, self.member_se.ids)

    def test_check_user_license_lt(self):
        self.assertEqual(self.user_license_lt.main_category_id.id,self.main_category.id)
        self.assertEqual(self.user_license_lt.next_expiry_date, fields.Date.from_string('2021-08-02'))
        self.assertTrue(self.user_license_lt.is_empty_date)
        self.assertEqual(self.user_license_lt.member_ids.ids, self.member_lt.ids)
