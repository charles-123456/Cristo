# -*- coding: utf-8 -*-
import tempfile
import binascii
import math
import xlrd
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging
from passlib import exc
_logger = logging.getLogger(__name__)
from datetime import datetime
import os
import io
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
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

class UpdateMemberHealth(models.TransientModel):
    _name = 'update.member.health'
    _description = 'To update the Member Health for members'
    
    file = fields.Binary(string='File')
    import_option = fields.Selection([('xls', 'XLS File'),('csv', 'CSV File')],string='Select',default='xls')

    def memberhealth_template(self):
        data = {'view_id':True}
        return self.env.ref('member_import_data.memberhealth_template_xlsx').report_action(self,data=data)

    def imoport_file(self):
        if not self.file:
            raise UserError(_("File not found."))
        li = 0
        if self.import_option == 'csv':
            keys = ['unique_code']            
            try:
                csv_data = base64.b64decode(self.file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                values = {}
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except:
                raise Warning(_("Invalid file!"))
            for i in range(len(file_reader)):
                li = li + 1
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        if not field[1] == "":
                            try:
                                values.update({
                                    'member_code' : field[1],
                                    'disease' : field[2],
                                    'st_date' : field[3],
                                    'en_date'  : field[4],
                                    'concern'  : field[5],
                                    'physician' : field[6],
                                    })
                            except:
                                raise Warning(_("Row No:{} \nError: File Fields are Missing or Mismatched".format(li)))
                            res = self.create_member_health(values,li)
                        else:
                            if field[0] == "" and field[2] == "":
                                res = True
                            else:
                                raise Warning(_("Row No:{} \nError: Member Code should not be Empty".format(li)))
        elif self.import_option == 'xls':
            try:
                fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except:
                raise Warning(_("Invalid file!"))
            for row_no in range(sheet.nrows):
                li = li + 1
                records = []
                val = {}
                if row_no <= 0:
                    fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    if not line[1] == "":
                        if line[3] and not type(line[3]) == 'date':
                            try:
                                line[3] = datetime(*xlrd.xldate_as_tuple(float(line[3]), workbook.datemode)).date()
                            except:
                                pass
                        if line[4] and not type(line[4]) == 'date':
                            try:
                                line[4] = datetime(*xlrd.xldate_as_tuple(float(line[4]), workbook.datemode)).date()
                            except:
                                pass
                        try:
                            values.update( {
                                    'member_code' : line[1],
                                    'disease' : line[2],
                                    'st_date' : line[3],
                                    'en_date'  : line[4],
                                    'concern'  : line[5],
                                    'physician' : line[6],
                                })
                        except:
                            if line[0] == "" and line[2] == "":
                                res = True
                            else:
                                raise Warning(_("Row No:{} \nError: Member Code should not be Empty".format(li)))
                        res = self.create_member_health(values,li)
                    else:
                        raise Warning(_("Row No:{} \nError: Member Code should not be Empty".format(li)))
        else:
            raise Warning(_("Please select any one from xls or csv format!"))
        message = _("The records imported successfully.")
        self.env['bus.bus'].sendone(
            (self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
            {'type': 'simple_notification', 'title': "Member Profile Updation", 'message': message, 'sticky': False, 'warning': False})
        return res
    
    def create_member_health(self,values,li):
        if not values.get("member_code") or values.get("member_code") == "-":
            raise Warning(_('Row No: {}\nError: Member Code cannot be empty.'.format(li)) )
        if not values.get("disease") or values.get("disease") == "-":
            raise Warning(_('Row No: {}\nError: Disease Disorder cannot be empty.'.format(li)) )
        
        member_code = values.get('member_code')
        disease = values.get('disease')
        
        try:
            mem_code = math.floor(float(member_code))
        except:
            mem_code = member_code
            
        member_id = self.env['res.member'].search([('unique_code','=',mem_code)])
        health_obj = self.env['res.member.health']
        
        if member_id:
            data = {
                    'member_id': member_id.id,
                    'disease_disorder_id': self.find_disease_id(disease),
                    'start_date': values.get('st_date') if not values.get('st_date') == "-" else False,
                    'end_date' : values.get('en_date') if not values.get('en_date') == "-" else False,
                    'particulars': values.get('concern') if not values.get('concern') == "-" else False,
                    'referred_physician': values.get('physician') if not values.get('physician') == "-" else False,
                    }
            try:
                return health_obj.create(data)
            except Exception as e:
                if ',' in str(e):
                    e = str(e).split(',')
                    e = e[0]
                raise Warning(_("Row No:{} \nImport Error: {}".format(li,e)))
        else:
            raise Warning(_("Row No: {} \nError: Member code Missing or Mismatched".format(li)))

    def find_disease_id(self,disease):
        disease_ids = self.env['res.disease.disorder'].search([('name','ilike',disease)])
        if disease_ids:
            return disease_ids[0].id
    