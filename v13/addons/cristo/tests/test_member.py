# -*- coding: utf-8 -*-
from odoo.tests import common
from odoo import fields

class TestMember(common.TransactionCase):
    
    def setUp(self):
        super(TestMember, self).setUp() 
        
        self.study_level = self.env['res.study.level'].search([('name','=', 'Pre-Primary')], limit=1)
        self.program = self.env['res.member.program'].search([('name','=', 'LKG')], limit=1)
        self.community = self.env['res.community'].search([('name','=', 'Raipur - IV (Raipur)')], limit=1)
        self.formaion_stage = self.env['res.formation.stage'].create({'name': 'Test'})
        self.disease = self.env['res.disease.disorder'].search([('name','=', 'Blood Pressure')], limit=1)
        
        self.member = self.env['res.member'].create(
            {'name':'Test','unique_code':'TST','member_type':'priest','membership_type':'RE',
             'dob': fields.Date.from_string('2020-01-02'),
            'member_education_ids':[
                (0, 0, {'study_level_id': self.study_level.id,
                        'program_id': self.program.id,
                        'mode': 'regular',
                        })
                    ],
            'profession_ids':[
                (0, 0, {'profession_date': fields.Date.from_string('2020-01-02'),
                        'type':'first',
                    })
                ],
            'formation_ids':[
                (0, 0, {'house_id': self.community.id,
                        'formation_stage_id': self.formaion_stage.id,
                        'start_year':'2014',
                    })
                ],
            'holyorder_ids':[
                (0, 0, {'date': fields.Date.from_string('2020-01-02'),
                        'order': 'priest',
                    })
                ],
            'religious_family_ids':[
                (0, 0, {'name': 'Test',
                        'gender': 'male',
                        'relationship': 'parent',
                    
                    })
                ],
            'member_health_ids':[
                (0, 0, {'disease_disorder_id': self.disease.id,
                        'start_date': fields.Date.from_string('2020-01-02'),
                        'end_date': fields.Date.from_string('2020-01-10'),
                    })
                ],
            'publication_ids':[
                (0, 0, {'title': 'Testing',
                        'publication_date': fields.Date.from_string('2020-01-02'),
                    })
                ],
            'award_recognition_ids':[
                (0, 0, {'title': 'Testing',
                        'date': fields.Date.from_string('2020-01-02'),
                    })
                ],
            'house_member_ids':[
                (0, 0, {'house_id': self.community.id,
                        'date_from': fields.Date.from_string('2020-01-02'),
                    })
                ],
            'statutory_renewal_ids':[
                (0, 0, {'no': '123456',
                        'document': 'Testing Document',
                    })
                ]
            })
        
    def test_check_member(self):
        print("test Members")
        self.assertEqual(self.member.name,'Test')
        self.assertEqual(self.member.unique_code,'TST')
        self.assertEqual(self.member.member_type,'priest')
        self.assertEqual(self.member.membership_type,'RE')
        self.assertEqual(self.member.dob, fields.Date.from_string('2020-01-02'))
    
    def test_check_education(self):
        self.assertEqual(self.member.member_education_ids.study_level_id.id, self.study_level.id)  
        self.assertEqual(self.member.member_education_ids.program_id.id, self.program.id)
        self.assertEqual(self.member.member_education_ids.mode,'regular')
        
    def test_check_profession(self):
        self.assertEqual(self.member.profession_ids.profession_date, fields.Date.from_string('2020-01-02'))   
        self.assertEqual(self.member.profession_ids.type,'first')
        
    def test_check_formation(self):
        self.assertEqual(self.member.formation_ids.house_id.id, self.community.id)  
        self.assertEqual(self.member.formation_ids.formation_stage_id.id, self.formaion_stage.id)
        self.assertEqual(self.member.formation_ids.start_year,'2014')
        
    def test_check_holyorder(self):   
        self.assertEqual(self.member.holyorder_ids.date, fields.Date.from_string('2020-01-02'))   
        self.assertEqual(self.member.holyorder_ids.order, 'priest')
        
    def test_check_family(self):
        self.assertEqual(self.member.religious_family_ids.name, 'Test')  
        self.assertEqual(self.member.religious_family_ids.gender, 'male')
        self.assertEqual(self.member.religious_family_ids.relationship,'parent')
        
    def test_check_disease(self):
        self.assertEqual(self.member.member_health_ids.disease_disorder_id.id, self.disease.id)  
        self.assertEqual(self.member.member_health_ids.start_date, fields.Date.from_string('2020-01-02'))
        self.assertEqual(self.member.member_health_ids.end_date, fields.Date.from_string('2020-01-10'))
        
    def test_check_publication(self):
        self.assertEqual(self.member.publication_ids.title, 'Testing')   
        self.assertEqual(self.member.publication_ids.publication_date, fields.Date.from_string('2020-01-02'))   
        
    def test_check_awards(self):
        self.assertEqual(self.member.award_recognition_ids.title, 'Testing')   
        self.assertEqual(self.member.award_recognition_ids.date, fields.Date.from_string('2020-01-02'))
        
    def test_check_house_member(self):
        self.assertEqual(self.member.house_member_ids.house_id.id, self.community.id)   
        self.assertEqual(self.member.house_member_ids.date_from, fields.Date.from_string('2020-01-02'))
        
    def test_check_statutory_renewal(self):
        self.assertEqual(self.member.statutory_renewal_ids.no, '123456')   
        self.assertEqual(self.member.statutory_renewal_ids.document, 'Testing Document')  