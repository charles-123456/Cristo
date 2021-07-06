# -*- coding: utf-8 -*-
#Required Python-docx package for MOM Report
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Cristo Calendar Meeting',
    'version': '2.0',
    'category': '',
    'sequence': 2,
    'summary': 'Parish Management Software',
    'description': """ """,
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
               'base','cristo','calendar','mail','cristo_dashboard','cristo_email',
                'cristo_ecclesia_dashboard',
               ],
    'data': [   
                'security/cristo_calendar_meeting_security.xml',
                'security/ir.model.access.csv',
                
                'data/meeting_template.xml',
                
                'wizard/wizard_meeting.xml',
                'views/calendar_meeting_views.xml',
                'views/res_religious_views.xml',
                'views/res_member.xml',
                'views/dashboard_assets.xml',
                'views/res_ecclesia_views.xml',
                'views/ecc_dashboard_assets.xml',
                'views/menus.xml',
                
            ],
    'qweb': ["static/src/xml/*.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}
