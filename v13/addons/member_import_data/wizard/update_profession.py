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
import os
import io
from datetime import datetime
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

class UpdateProfession(models.TransientModel):
    _name = 'update.profession'
    _description = 'To update the profession for members'
    
    file = fields.Binary(string='File')
    import_option = fields.Selection([('xls', 'XLS File'),('csv', 'CSV File')],string='Select',default='xls')

    def profession_template(self):
        data = {'view_id':True}
        return self.env.ref('member_import_data.profession_template_xlsx').report_action(self,data=data)

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
                                    'unique_code': field[1],
                                    'profession_date': field[2],
                                    'place': field[3],
                                    'type': field[4],
                                    'years': field[5],
                                    'state': field[6],
                                    })
                            except:
                                raise Warning(_("Row No:{} \nError: File Fields are Missing or Mismatched".format(li)))
                            res = self.create_profession(values,li)
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
                        if line[2] and not type(line[2]) == 'date':
                            try:
                                line[2] = datetime(*xlrd.xldate_as_tuple(float(line[2]), workbook.datemode)).date()
                            except:
                                pass
                        try:
                            values.update({
                                    'unique_code': line[1],
                                    'profession_date': line[2],
                                    'place': line[3],
                                    'type': line[4],
                                    'years': line[5],
                                    'state':line[6],
                                })
                        except:
                            raise Warning(_("Row No:{} \nError: File Fields are Missing or Mismatched".format(li)))
                        res = self.create_profession(values,li)
                    else:
                        if line[0] == "" and line[2] == "":
                            res = True
                        else:
                            raise Warning(_("Row No:{} \nError: Member Code should not be Empty".format(li)))
        else:
            raise Warning(_("Please select any one from xls or csv format!"))
        message = _("The records imported successfully.")
        self.env['bus.bus'].sendone(
            (self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
            {'type': 'simple_notification', 'title': "Member Profile Updation", 'message': message, 'sticky': False, 'warning': False})
        return res
    
    def create_profession(self,values,li):
        if not values.get("unique_code") or values.get("unique_code") == "-":
            raise Warning(_('Row No: {}\nError: Code field cannot be empty.'.format(li)) )
        if not values.get("profession_date") or values.get("profession_date") == "-":
            raise Warning(_('Row No: {}\nError: Date field cannot be empty.'.format(li)) )
        if not values.get("type") or values.get("type") == "-":
            raise Warning(_('Row No: {}\nError: Type field cannot be empty.'.format(li)) )
        
        unique_code = values.get('unique_code')
        try:
            code = math.floor(float(unique_code))
        except:
            code = unique_code
            
        try:
            if not values.get('state') or values.get('state') == "-":
                state = False
            else:
                state = values.get('state').lower()
        except:
            raise Warning(_("Row No: {}\nError: Wrong value in State Column".format(li)))
         
        try:   
            if not values.get('years') or values.get('years') == '-':
                years = False
            else:
                years = str(math.floor(float(values.get('years'))))
        except:
            raise Warning(_("Row No: {}\nError: Year field is Mismatched or Incorrect Value".format(li)))
    
        
        profession_obj = self.env['res.profession']
        member_id = self.env['res.member'].search([('unique_code','=',code)])
        
        if member_id:
            data = {
                    'member_id': member_id.id,
                    'profession_date': values.get('profession_date'),
                    'place': values.get('place') if not values.get('place') == "-" else False,
                    'type': values.get('type').lower(),
                    'years': years,
                    'state': state,
                    }
            try:
                return profession_obj.create(data)
            except Exception as e:
                if ',' in str(e):
                    e = str(e).split(',')
                    e = e[0]
                raise Warning(_("Row No:{} \nImport Error: {}".format(li,e)))
        else:
            raise Warning(_(" Row No: {} \n Error: Member code is Missing or Mismatched".format(li)))
