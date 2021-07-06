# -*- coding: utf-8 -*-
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
    'name': 'Cristo Document',
    'version': '2.0',
    'category': '',
    'sequence': 4,
    'summary': 'Document',
    'description': """Cristo Document""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'cristo_dashboard','cristo','muk_dms','base','auth_signup',
                'cristo_ecclesia_dashboard',
               ],
    'data': [
            'security/document_security.xml',
            'security/ir.model.access.csv',

            'data/file.xml',
             
            'views/res_users_views.xml',
            'views/directory_views.xml',
            'views/file_views.xml',
            'views/category_views.xml',
            'views/tag_views.xml',
            'views/dashboard_views.xml',
            'views/ecc_dashboard_views.xml',
            ],
    'qweb': ["static/src/xml/*.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}
