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

class UpdatePublication(models.TransientModel):
    _name = 'update.publication'
    _description = 'To update the Publication for members'
    
    file = fields.Binary(string='File')
    import_option = fields.Selection([('xls', 'XLS File'),('csv', 'CSV File')],string='Select',default='xls')

    def publication_template(self):
        data = {'view_id':True}
        return self.env.ref('member_import_data.publication_template_xlsx').report_action(self,data=data)

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
                                    'date' : field[2],
                                    'title' : field[3],
                                    'type'  : field[4],
                                    'publisher'  : field[5],
                                    'royalty' : field[6],
                                    })
                            except:
                                raise Warning(_("Row No:{} \nError: File Fields are Missing or Mismatched".format(li)))
                                res = self.create_publication(values,li)
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
                                    'member_code' : line[1],
                                    'date' : line[2],
                                    'title' : line[3],
                                    'type'  : line[4],
                                    'publisher'  : line[5],
                                    'royalty' : line[6],
                                })
                        except:
                            raise Warning(_("Row No:{} \nError: File Fields are Missing or Mismatched".format(li)))
                        res = self.create_publication(values,li)
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
    
    def create_publication(self,values,li):
        if not values.get("member_code") or values.get("member_code") == "-":
            raise Warning(_('Row No: {}\nError: Member Code cannot be empty.'.format(li)) )
        if not values.get("date") or values.get("date") == "-":
            raise Warning(_('Row No: {}\nError: Publication Date cannot be empty.'.format(li)) )
        if not values.get("title") or values.get("title") == "-":
            raise Warning(_('Row No: {}\nError: Title cannot be empty.'.format(li)) )
        
        
        member_code = values.get('member_code')
        type = values.get('type')
        
        try:
            mem_code = math.floor(float(member_code))
        except:
            mem_code = member_code
            
        member_id = self.env['res.member'].search([('unique_code','=',mem_code)])
        publication_obj = self.env['res.publication']
        
        if member_id:
            data = {
                    'member_id': member_id.id,
                    'publication_date': values.get('date'),
                    'title': values.get('title').title(),
                    'publication_type_id' : self.find_publication_type(type,li) if type else False,
                    'publisher': values.get('publisher') if not values.get('publisher') == "-" else False,
                    'royalty': values.get('royalty') if not values.get('royalty') == "-" else False,
                    }
            try:
                print(li)
                return publication_obj.create(data)
            except Exception as e:
                if ',' in str(e):
                    e = str(e).split(',')
                    e = e[0]
                raise Warning(_("Row No:{} \nImport Error: {}".format(li,e)))
        else:
            raise Warning(_("Row No: {} \nError: Member code Missing or Mismatched".format(li)))

    def find_publication_type(self,type_name,li):
        if not type == "-":
            type_ids = self.env['publication.type'].search([('name','like',type_name)])
            if type_ids:
                return type_ids[0].id
        else:
            return False
        
