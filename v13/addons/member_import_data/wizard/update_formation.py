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

class UpdateFormation(models.TransientModel):
    _name = 'update.formation'
    _description = 'To update the formation for members'
    
    file = fields.Binary(string='File')
    import_option = fields.Selection([('xls', 'XLS File'),('csv', 'CSV File')],string='Select',default='xls')

    def formation_template(self):
        data = {'view_id':True}
        return self.env.ref('member_import_data.formation_template_xlsx').report_action(self,data=data)

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
                                    'house_code' : field[2],
                                    'stage_name' : field[3],
                                    'st_year' : field[4],
                                    'en_year'  : field[5],
                                    'study_done'  : field[6],
                                    'house_name' : field[7],
                                    })
                            except:
                                raise Warning(_("Row No:{} \nError: File Fields are Missing or Mismatched".format(li)))
                            res = self.create_formation(values,li)
                        else:
                            if field[0] == "" and field[2] == "" and field[7] == "":
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
                        try:
                            values.update( {
                                    'member_code' : line[1],
                                    'house_code' : line[2],
                                    'stage_name' : line[3],
                                    'st_year' : line[4],
                                    'en_year'  : line[5],
                                    'study_done'  : line[6],
                                    'house_name' : line[7],
                     
                                })
                        except:
                            raise Warning(_("Row No:{} \nError: File Fields are Missing or Mismatched".format(li)))
                        res = self.create_formation(values,li)
                    else:
                        if line[0] == "" and line[2] == "" and line[7] == "":
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
    
    def create_formation(self,values,li):
        if not values.get("member_code") or values.get("member_code") == "-":
            raise Warning(_('Row No: {}\nError: Member Code cannot be empty.'.format(li)) )
        if not values.get("house_code") or values.get("house_code") == "-":
            if not values.get("house_name") or values.get("house_name") == "-":
                raise Warning(_('Row No: {}\nError: House Code or House Name is must for Formation Update'.format(li)) )
        if not values.get("st_year") or values.get("st_year") == "-":
            raise Warning(_('Row No: {}\nError: Start Year column cannot be empty.'.format(li)) )
        
        member_code = values.get('member_code')
        house_code = values.get('house_code')
        house_name = values.get('house_name')
        
        try:
            mem_code = math.floor(float(member_code))
        except:
            mem_code = member_code
        try:   
            st_year = str(math.floor(float(values.get('st_year'))))
        except:
            raise Warning(_("Row No: {}\nError: Start Year field is Mismatched or Incorrect Value".format(li)))
        
        try:   
            if not values.get('en_year') or values.get('en_year') == '-':
                en_year = False
            else:
                en_year = str(math.floor(float(values.get('en_year'))))
        except:
            raise Warning(_("Row No: {}\nError: End Year field is Mismatched or Incorrect Value".format(li)))
            
        member_id = self.env['res.member'].search([('unique_code','=',mem_code)])
        house_id = self.env['res.community'].search([('code','=',house_code)])
        if not house_id:
            house_id = self.env['res.community'].search([('name','=',house_name)])
        
        formation_obj = self.env['res.formation']
        
        
        if member_id:
            if house_id:
                data = {
                        'member_id' : member_id[0].id,
                        'house_id' : house_id[0].id,
                        'start_year'  : st_year,
                        'end_year'  : en_year,
                        'study_info' : values.get('study_done') if not values.get('study_done') == "-" else "",
                        'formation_stage_id' : self.find_formation_stage(values.get('stage_name')) if values.get('stage_name') else False,
                        }
                try:
                    return formation_obj.create(data)
                except Exception as e:
                    if ',' in str(e):
                        e = str(e).split(',')
                        e = e[0]
                    raise Warning(_("Row No:{} \nImport Error: {}".format(li,e)))
            else:
                raise Warning(_("Row No: {} \nError: House Code or House name field Missing or Mismatched".format(li)))
        else:
            raise Warning(_("Row No: {} \nError: Member code is Missing or Mismatched".format(li)))

    def find_formation_stage(self,name):
        if not name == "-":
            stage_id = self.env['res.formation.stage'].search([('name','=',name)])
            if stage_id:
                return stage_id[0].id
            else:
                return False
        else:
            return False
