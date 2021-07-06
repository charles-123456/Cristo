# -*- coding: utf-8 -*-
from odoo.tests import common
from odoo import fields

class TestCouncil(common.TransactionCase):
    
    def setUp(self):
        super(TestCouncil, self).setUp()
        
        self.member = self.env['res.member'].search([('name','=', 'Arthur')], limit=1)
        self.member_role = self.env['res.member.role'].search([('name','=', 'Archbishop')], limit=1)
        
        self.council = self.env['res.council'].create(
            {'name':'Test','status':'active','user_id':self.env.user.id,'institute_id':self.env.user.institute_id.id,
             'rel_province_id':self.env.user.rel_province_id.id,'community_id':self.env.user.community_id.id,
            'institution_id':self.env.user.institution_id.id,
            'member_ids':[
                (0, 0, {'role_id':self.member_role.id,
                        'member_id':self.member.id,
                        'date_from':fields.Date.from_string('2020-01-02'),
                        'date_to':fields.Date.from_string('2020-01-01'),
                        'status':'active',
                        })
                    ]
            })
        
        self.council1 = self.env['res.council'].create(
            {'name':'Test1','status':'active','user_id':self.env.user.id,'institute_id':self.env.user.institute_id.id,
             'rel_province_id':self.env.user.rel_province_id.id,'community_id':self.env.user.community_id.id,
            'institution_id':self.env.user.institution_id.id,
            'member_ids':[
                (0, 0, {'role_id':self.member_role.id,
                        'member_id':self.member.id,
                        'date_from':fields.Date.from_string('2020-01-02'),
                        'date_to':fields.Date.from_string('2020-05-31'),
                        'status':'active',
                        })
                    ]
            })
        
    def test_check_council(self):
        self.assertEqual(self.council.name,'Test')
        self.assertEqual(self.council.status,'active')
        self.assertEqual(self.council.user_id, self.env.user)
        self.assertEqual(self.council.institute_id.id, self.env.user.institute_id.id)
        self.assertEqual(self.council.rel_province_id.id, self.env.user.rel_province_id.id)
        self.assertEqual(self.council.community_id.id, self.env.user.community_id.id)
        self.assertEqual(self.council.institution_id.id,  self.env.user.institution_id.id)
        self.assertEqual(self.council.member_ids.role_id.id, self.member_role.id)
        self.assertEqual(self.council.member_ids.member_id.id, self.member.id)
        self.assertEqual(self.council.member_ids.date_from, fields.Date.from_string('2020-01-02'))
        self.assertEqual(self.council.member_ids.date_to, fields.Date.from_string('2020-05-31'))
        self.assertEqual(self.council.member_ids.status, 'active')
        
        