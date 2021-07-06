from odoo.tests import common,new_test_user
from odoo import fields



class TestEcclesia(common.TransactionCase):
    
    def setUp(self):
        super(TestEcclesia,self).setUp()
        
        
        self.district = self.env['res.state.district'].search([('name','=', 'Bangalore')], limit=1)
        
        self.state = self.env['res.country.state'].search([('name','=', 'Tamil Nadu')], limit=1)
        
        self.country = self.env['res.country'].search([('name','=', 'India')], limit=1)

        self.region = self.env['res.ecclesia.region'].create({'name':'TamilNadu',
                                                              'code':'TN',
                                                              })
        self.province = self.env['res.ecclesia.province'].create({'ecc_reg_id':'self.region.id',
                                                                  'name':'Salesian',
                                                                  })
        self.diocese = self.env['res.ecclesia.diocese'].create({'name':'Vellore',
                                                                'code':'V',
                                                                'ecc_province_id':'self.province.id',
                                                                'date':fields.Date.from_string('2020-01-03'),
                                                                'street':'vellore Circle',
                                                                'city':'Vellore',
                                                                'zip':'123',
                                                                'district_id':'self.district.id',
                                                                'state_id':'self.state.id',
                                                                'country_id':'self.country.id',
                                                             })
       
        self.vicariate = self.env['res.vicariate'].create({'name':'Arni',
                                                           'code':'AR',
                                                           'diocese_id':'self.diocese.id',
                                                           'street':'vellore Circle',
                                                           'city':'Vellore',
                                                           'zip':'123',
                                                           'district_id':'self.district.id',
                                                           'state_id':'self.state.id',
                                                           'country_id':'self.country.id',
                                                              })

        self.parish = self.env['res.parish'].create({'name':'Kolappalur',
                                                     'code':'KPL',
                                                     'diocese_id':'self.diocese.id',
                                                     'vicariate_id':'self.vicariate.id',
                                                     'street':'Annai Nagar',
                                                     'city':'Kolappalur',
                                                     'zip':'12345',
                                                     'district_id':'self.district.id',
                                                     'state_id':'self.state.id',
                                                     'country_id':'self.country.id',
                                                              })
        
        self.substation= self.env['res.parish.sub.station'].create({'name':'Enthiravanam',
                                                                    'diocese_id':'self.diocese.id',
                                                                    'vicariate_id':'self.vicariate.id',
                                                                    'parish_id':'self.parish.id',
                                                                    'street':'Annai Nagar',
                                                                    'city':'Kolappalur',
                                                                    'zip':'12345',
                                                                    'district_id':'self.district.id',
                                                                    'state_id':'self.state.id',
                                                                    'country_id':'self.country.id',
                                                                    })
        
        
        
        self.zone = self.env['res.ecclesia.zone'].create({'name':'Katteri',
                                                          'diocese_id':'self.diocese.id',
                                                          'vicariate_id':'self.vicariate.id',
                                                          'parish_id':'self.parish.id', 
                                                            })
        
        self.bcc = self.env['res.parish.bcc'].create({'name':'ST.Joseph',
                                                      'diocese_id':'self.diocese.id',
                                                      'vicariate_id':'self.vicariate.id',
                                                       'parish_id':'self.parish.id', 
                                                            })

    def test_check_ecclesia(self):
        print("check ecclesia")
        self.assertEqual(self.region.name,'TamilNadu')
#         self.assertEqual(self.institute.id, self.province.ecc_reg_id.id,'Code Executed Successfully ')
#         self.assertEqual(self.diocese.id, self.province.ecc_province_id.id,)
#         self.assertEqual(self.diocese.date, fields.Date.from_string('2020-01-03'))
#         self.assertEqual(self.diocese.id, self.province.ecc_province_id.id,)

        









    
    