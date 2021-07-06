from odoo.tests import common, new_test_user
from odoo.exceptions import AccessError
from odoo import fields

class TestCircularUser(common.TransactionCase):

    def setUp(self):
        super(TestCircularUser, self).setUp()

        self.institute = self.env['res.religious.institute'].create({
                                'name': 'Test Institute', 'founder': 'Augustin', 'motto': 'Thinking about Motto'})
        self.province = self.env['res.religious.province'].create({'institute_id': self.institute.id, 'name': 'Test Province'})
        self.partner = self.env['res.partner'].create({'name': 'Pardison', 'main_category_id': 19})
        self.user = new_test_user(self.env, login='pradison', groups='cristo_circular.group_circular_user',
                                institute_id=self.institute.id, rel_province_id=self.province.id,partner_id=self.partner.id)
        self.member = self.env['res.member'].create({
                                'name': 'Test Member', 'unique_code': 'TST', 'member_type': 'priest', 'membership_type': 'RE',
                                'dob': fields.Date.from_string('2020-01-02')})
        self.circular = self.env['cristo.circular'].create({
                                'member_id': self.member.id, 'name': 'Test Circular', 'type': 'create_content', 'content': 'Content',
                                'month': '1', 'year': '2019', 'institute_id': self.user.institute_id.id,'rel_province_id': self.user.rel_province_id.id})

    def test_check_circular_user_read(self):
        with self.assertRaises(AccessError):
            self.circular.with_user(self.user).read()

    def test_check_circular_user_unlink(self):
        with self.assertRaises(AccessError):
            self.circular.with_user(self.user).unlink()

    def test_check_circular_user_create(self):
        with self.assertRaises(AccessError):
            self.circular.with_user(self.user).create({
                        'member_id': self.member.id, 'name': 'Create Circular', 'type': 'create_content', 'content': 'Content',
                        'month': '1', 'year': '2019', 'institute_id': self.user.institute_id.id,'rel_province_id': self.user.rel_province_id.id})

    def test_check_circular_user_write(self):
        with self.assertRaises(AccessError):
            self.circular.with_user(self.user).write({
                        'member_id': self.member.id, 'name': 'Write Circular', 'type': 'create_content', 'content': 'Content',
                        'month': '1', 'year': '2019', 'institute_id': self.user.institute_id.id,'rel_province_id': self.user.rel_province_id.id})


class TestCircularBaseuser(common.TransactionCase):

    def setUp(self):
        super(TestCircularBaseuser, self).setUp()

        self.user = new_test_user(self.env, login='pardison', groups='base.group_user')
        self.circular = self.env['cristo.circular'].create({
                            'name': 'Test Circular','member_id':995 , 'month': '1', 'year': '2019','type':'create_content',
                            'institute_id':595,'rel_province_id':1391,})

    def test_circular_base_user(self):
        with self.assertRaises(AccessError):
            self.circular.with_user(self.user).read()