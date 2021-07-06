# -*- coding: utf-8 -*-
from odoo.tests import common
from odoo import fields

class TestCommission(common.TransactionCase):
    
    def setUp(self):
        super(TestCommission, self).setUp()
        
        self.partner = self.env['res.partner'].search([('name','=', 'Arthur')], limit=1)
        self.member_role = self.env['res.member.role'].search([('name','=', 'Archbishop')], limit=1)

        self.commission = self.env['res.commission'].create({'name':'Test','user_id':self.env.user.id,'institute_id':self.env.user.institute_id.id,
            'rel_province_id':self.env.user.rel_province_id.id,'community_id':self.env.user.community_id.id,
            'institution_id':self.env.user.institution_id.id,
            'commission_member_ids':[
                (0, 0, {'role_id':self.member_role.id,
                        'partner_id':self.partner.id,
                        'date_from':fields.Date.from_string('2020-01-02'),
                        'date_to':fields.Date.from_string('2020-01-01'),
                        'status':'active',
                        })
                    ]
            })
        
    def test_check_commission(self):
        self.assertEqual(self.commission.name,'Test')
        self.assertEqual(self.commission.user_id, self.env.user)
        self.assertEqual(self.commission.institute_id.id, self.env.user.institute_id.id)
        self.assertEqual(self.commission.rel_province_id.id, self.env.user.rel_province_id.id)
        self.assertEqual(self.commission.community_id.id, self.env.user.community_id.id)
        self.assertEqual(self.commission.institution_id.id,  self.env.user.institution_id.id)
        self.assertEqual(self.commission.commission_member_ids.role_id.id, self.member_role.id)
        self.assertEqual(self.commission.commission_member_ids.partner_id.id, self.partner.id)
        self.assertEqual(self.commission.commission_member_ids.date_from, fields.Date.from_string('2020-01-02'))
        self.assertEqual(self.commission.commission_member_ids.date_to, fields.Date.from_string('2020-05-31'))
        self.assertEqual(self.commission.commission_member_ids.status, 'active')
        
        
        