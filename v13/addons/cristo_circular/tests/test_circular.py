# -*- coding: utf-8 -*-
from odoo.tests import common, new_test_user
from odoo import fields

class TestCircular(common.TransactionCase):

    def setUp(self):
        super(TestCircular, self).setUp()

        self.institute = self.env['res.religious.institute'].create(
            {'name': 'Test Congregation', 'founder': 'Augustin', 'motto': 'Thinking about Motto'})
        self.province = self.env['res.religious.province'].create({'institute_id': self.institute.id, 'name': 'Test Province'})
        self.partner = self.env['res.partner'].create({'name': 'Pradison', 'main_category_id': 19})
        self.user = new_test_user(self.env, login='pradison', groups='cristo_circular.group_circular_user',
                                  institute_id=self.institute.id, rel_province_id=self.province.id,
                                  partner_id=self.partner.id)
        self.member = self.env['res.member'].create(
            {'name': 'Test Member','unique_code':'TST','member_type':'priest','membership_type':'RE',
             'dob': fields.Date.from_string('2020-01-02')})
        self.circular = self.env['cristo.circular'].create({
            'member_id': self.member.id, 'name': 'Test Circular', 'type':'create_content','content':'Content',
            'month':'1', 'year':'2019','institute_id':self.user.institute_id.id, 'rel_province_id':self.user.rel_province_id.id})

    def test_check_circular(self):
        self.assertEqual(self.member.id, self.circular.member_id.id)
        self.assertEqual(self.institute.id, self.circular.institute_id.id)
        self.assertEqual(self.province.id, self.circular.rel_province_id.id)
        self.assertEqual(self.circular.name,'Test Circular')
        self.assertEqual(self.circular.type, 'create_content')
        self.assertEqual(self.circular.content, 'Content')
        self.assertEqual(self.circular.month, '1')
        self.assertEqual(self.circular.year, '2019')

    def test_check_circular_upload_file_type_pdf(self):
        self.circular =  self.env['cristo.circular'].create({
            'member_id': self.member.id, 'name': 'Test Circular', 'type':'upload','file_name':'PDF.pdf',
            'month':'1', 'year':'2019','institute_id':self.user.institute_id.id, 'rel_province_id':self.user.rel_province_id.id})
        self.assertTrue(self.circular.file_name.endswith('.pdf'))

    def test_check_circular_upload_file_type_other(self):
        self.circular =  self.env['cristo.circular'].create({
            'member_id': self.member.id, 'name': 'Test Circular', 'type':'upload','file_name':'WORD.docx',
            'month':'1', 'year':'2019','institute_id':self.user.institute_id.id, 'rel_province_id':self.user.rel_province_id.id})
        self.assertFalse(self.circular.file_name.endswith('.pdf'))