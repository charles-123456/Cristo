# -*- coding: utf-8 -*-
from odoo.tests import common
import datetime
from datetime import datetime, timedelta, time

class TestMeeting(common.TransactionCase):
    
    def setUp(self):
        super(TestMeeting, self).setUp()

        self.meeting = self.env['calendar.event'].create({'name': 'Test','partner_ids':'Augustin','duration':2.5})
        
    def test_check_meeting(self):
        self.assertEqual(self.meeting.name,'Test')