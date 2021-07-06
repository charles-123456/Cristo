# -*- coding: utf-8 -*-
from odoo.tests import common,new_test_user
from odoo import fields
from odoo.exceptions import AccessError

class TestCustomRoles(common.TransactionCase):
    
    def setUp(self):
        super(TestCustomRoles, self).setUp()
        
        self.groups = self.env['res.groups'].create({'name': 'Test group'})
        self.custom_roles = self.env['custom.user.role'].create({'name': 'Test user role', 'code': 'code', 'group_ids': self.groups.ids})
        
    def test_check_custom_roles(self):
        self.assertEqual(self.custom_roles.name,'Test user role')
        self.assertEqual(self.custom_roles.code,'code')
        self.assertEqual(self.custom_roles.group_ids.ids,self.groups.ids)

class TestUsersListMember(common.TransactionCase):
    def setUp(self):
        super(TestUsersListMember, self).setUp()
        
        self.main_category = self.env['res.main.category'].search([('code', '=', 'MR')], limit=1)
        
        self.contact = self.env['res.partner'].create({'name': 'Test name', 'main_category_id': self.main_category.id})
        self.groups = self.env['res.groups'].create({'name': 'Test group'})
        self.congregation = self.env['res.religious.institute'].create({'name': 'Test Congregation'})
        self.cristo_users = self.env['cristo.users'].create({'main_category_id': self.main_category.id, 'login': 'test', 'password': 'test', 
                                                             'main_role_id': self.groups.id, 'institute_id': self.congregation.id})
        
    def test_check_member_user(self):
        self.assertEqual(self.cristo_users.main_category_id.id,self.main_category.id)
        self.assertEqual(self.cristo_users.login, 'test')
        self.assertEqual(self.cristo_users.password, 'test')
        self.assertEqual(self.cristo_users.main_role_id.id, self.groups.id)
        self.assertEqual(self.cristo_users.institute_id.id, self.congregation.id)
        
        

class TestUsersListCongregation(common.TransactionCase):
    def setUp(self):
        super(TestUsersListCongregation, self).setUp()
        
        self.main_category = self.env['res.main.category'].search([('code', '=', 'RC')], limit=1)
        
        self.contact = self.env['res.partner'].create({'name': 'Test name', 'main_category_id': self.main_category.id})
        self.groups = self.env['res.groups'].create({'name': 'Test group'})
        self.congregation = self.env['res.religious.institute'].create({'name': 'Test Congregation'})
        self.cristo_users = self.env['cristo.users'].create({'main_category_id': self.main_category.id, 'login': 'test', 'password': 'test', 
                                                             'main_role_id': self.groups.id, 'institute_id': self.congregation.id})
        
    def test_check_congregation_user(self):
        self.assertEqual(self.cristo_users.main_category_id.id,self.main_category.id)
        self.assertEqual(self.cristo_users.login, 'test')
        self.assertEqual(self.cristo_users.password, 'test')
        self.assertEqual(self.cristo_users.main_role_id.id, self.groups.id)
        self.assertEqual(self.cristo_users.institute_id.id, self.congregation.id)
        
        
class TestUsersListProvince(common.TransactionCase):
    def setUp(self):
        super(TestUsersListProvince, self).setUp()
        
        self.main_category = self.env['res.main.category'].search([('code', '=', 'RP')], limit=1)
        
        self.contact = self.env['res.partner'].create({'name': 'Test name', 'main_category_id': self.main_category.id})
        self.groups = self.env['res.groups'].create({'name': 'Test group'})
        self.congregation = self.env['res.religious.institute'].create({'name': 'Test Congregation'})
        self.rel_province = self.env['res.religious.province'].create({'name': 'Test Province', 'institute_id': self.congregation.id})
        self.cristo_users = self.env['cristo.users'].create({'main_category_id': self.main_category.id, 'login': 'test', 'password': 'test', 
                                                             'main_role_id': self.groups.id, 'institute_id': self.congregation.id, 'rel_province_id': self.rel_province.id})
        
    def test_check_rel_province_user(self):
        self.assertEqual(self.cristo_users.main_category_id.id,self.main_category.id)
        self.assertEqual(self.cristo_users.login, 'test')
        self.assertEqual(self.cristo_users.password, 'test')
        self.assertEqual(self.cristo_users.main_role_id.id, self.groups.id)
        self.assertEqual(self.cristo_users.institute_id.id, self.congregation.id)
        self.assertEqual(self.cristo_users.rel_province_id.id, self.rel_province.id)
        
class TestUsersListCommunity(common.TransactionCase):
    def setUp(self):
        super(TestUsersListCommunity, self).setUp()
        
        self.main_category = self.env['res.main.category'].search([('code', '=', 'HC')], limit=1)
        
        self.contact = self.env['res.partner'].create({'name': 'Test name', 'main_category_id': self.main_category.id})
        self.groups = self.env['res.groups'].create({'name': 'Test group'})
        self.congregation = self.env['res.religious.institute'].create({'name': 'Test Congregation'})
        self.rel_province = self.env['res.religious.province'].create({'name': 'Test Province', 'institute_id': self.congregation.id})
        self.community = self.env['res.community'].create({'name': 'Test Community', 'institute_id': self.congregation.id, 'rel_province_id': self.rel_province.id})
        self.cristo_users = self.env['cristo.users'].create({'main_category_id': self.main_category.id, 'login': 'test', 'password': 'test', 
                                                             'main_role_id': self.groups.id, 'institute_id': self.congregation.id, 'rel_province_id': self.rel_province.id, 'community_id': self.community.id})
        
    def test_check_housecommunity_user(self):
        self.assertEqual(self.cristo_users.main_category_id.id,self.main_category.id)
        self.assertEqual(self.cristo_users.login, 'test')
        self.assertEqual(self.cristo_users.password, 'test')
        self.assertEqual(self.cristo_users.main_role_id.id, self.groups.id)
        self.assertEqual(self.cristo_users.institute_id.id, self.congregation.id)
        self.assertEqual(self.cristo_users.rel_province_id.id, self.rel_province.id)
        self.assertEqual(self.cristo_users.community_id.id, self.community.id)
        
class TestUsersListInstitution(common.TransactionCase):
    def setUp(self):
        super(TestUsersListInstitution, self).setUp()
        
        self.main_category = self.env['res.main.category'].search([('code', '=', 'RI')], limit=1)
        
        self.contact = self.env['res.partner'].create({'name': 'Test name', 'main_category_id': self.main_category.id})
        self.groups = self.env['res.groups'].create({'name': 'Test group'})
        self.congregation = self.env['res.religious.institute'].create({'name': 'Test Congregation'})
        self.rel_province = self.env['res.religious.province'].create({'name': 'Test Province', 'institute_id': self.congregation.id})
        self.community = self.env['res.community'].create({'name': 'Test Community', 'institute_id': self.congregation.id, 'rel_province_id': self.rel_province.id})
        self.institution = self.env['res.institution'].create({'name': 'Test Institution', 'community_id': self.community.id, 'street': 'Test street', 'city': 'City', 'zip': '5205200'})
        self.cristo_users = self.env['cristo.users'].create({'main_category_id': self.main_category.id, 'login': 'test', 'password': 'test', 
                                                             'main_role_id': self.groups.id, 'institute_id': self.congregation.id, 'rel_province_id': self.rel_province.id, 'community_id': self.community.id, 'institution_id': self.institution.id})
        
    def test_check_institution_user(self):
        self.assertEqual(self.cristo_users.main_category_id.id,self.main_category.id)
        self.assertEqual(self.cristo_users.login, 'test')
        self.assertEqual(self.cristo_users.password, 'test')
        self.assertEqual(self.cristo_users.main_role_id.id, self.groups.id)
        self.assertEqual(self.cristo_users.institute_id.id, self.congregation.id)
        self.assertEqual(self.cristo_users.rel_province_id.id, self.rel_province.id)
        self.assertEqual(self.cristo_users.community_id.id, self.community.id)
        self.assertEqual(self.cristo_users.institution_id.id, self.institution.id)
        