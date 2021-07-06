# -*- coding: utf-8 -*-
import tempfile
import binascii
import xlrd
import math
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
import logging
_logger = logging.getLogger(__name__)
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class UploadAssignment(models.TransientModel):
    _name = 'upload.assignment'
    _description = 'To upload the assignment'
    
    file = fields.Binary(string='File',required=True)
    assignment_id = fields.Many2one('member.assignment',string='Assignment',readonly=True)
    
    def upload_new_assignment(self):
        try:
            fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
        except:
            raise Warning(_("Invalid file!"))
        records = []
        for row_no in range(sheet.nrows):
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                if not line[0] == "":
                    role = []
                    if ',' in line[7]:
                        roles = line[7].split(',')
                        for li in roles:
                            role.append(li.strip())
                    else:
                        role.append(line[7].strip())
                    pre_role = []
                    if ',' in line[4]:
                        pre_roles = line[4].split(',')
                        for pre_li in pre_roles:
                            pre_role.append(pre_li.strip())
                    else:
                        pre_role.append(line[4].strip())
                    try:    
                        if line[1]:
                            line[1] = math.floor(float(line[1]))
                    except:
                        pass
                    try:
                        if line[5]:
                            years = math.floor(float(line[5]))
                    except:
                        years = 0
                    values = {
                            'name' : line[0],
                            'code' : line[1],
                            'pre_house':line[2].strip(),
                            'pre_roles':pre_role,
                            'years':years,
                            'house' : line[6].strip(),
                            'roles'  : role,
                        }
                    records.append(values)
        if records:
            self.update_new_assignment(records,self.assignment_id)
            
    def update_new_assignment(self,records,assignment):
        assignment_due_obj = self.env['member.assignment.due']
        for rec in records:
            member_id = self.env['res.member'].search([('unique_code','=',rec['code'])])
            house_id = self.env['res.community'].search([('name','=',rec['house'])])
            role_ids = self.env['res.member.role'].search([('name','in',rec['roles'])])
            pre_house = self.env['res.community'].search([('name','=',rec['pre_house'])],limit=1)
            pre_roles = self.env['res.member.role'].search([('name','in',rec['pre_roles'])])
            if member_id:
                due_id = assignment_due_obj.search([('assignment_id','=',assignment.id),('member_id','=',member_id.id)],limit=1)
                if due_id:
                    due_id.update({
                        'new_community_id':house_id[0].id if house_id else False,
                        'new_role_ids': role_ids if role_ids else False,
                        'is_selected' : True,
                        })
                else:
                    assignment_due_obj.create({
                                    'member_id':member_id.id,
                                    'pre_house_id':pre_house.id if pre_house else False,
                                    'old_role_ids':pre_roles if pre_roles else False,
                                    'ministry_years':rec['years'],
                                    'new_community_id':house_id[0].id if house_id else False,
                                    'new_role_ids': role_ids if role_ids else False,
                                    'is_selected': True,
                                    })
