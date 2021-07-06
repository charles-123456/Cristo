# -*- coding: utf-8 -*-
import tempfile
import binascii
import math
import xlrd
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging
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

class UpdateEducation(models.TransientModel):
    _name = 'update.education'
    _description = 'To update the Education for members'
    
    file = fields.Binary(string='File')
    import_option = fields.Selection([('xls', 'XLS File'),('csv', 'CSV File')],string='Select',default='xls')

    def education_template(self):
        data = {'view_id':True}
        return self.env.ref('member_import_data.education_template_xlsx').report_action(self,data=data)

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
                                    'study_code' : field[2],
                                    'program' : field[3],
                                    'place' : field[4],
                                    'disciplines'  : field[6],
                                    'particulars'  : field[7],
                                    'year' : field[5],
                                    'duration' : field[8],
                                    'mode' : field[9],
                                    'result':field[10],
                                    'remarks':field[11],
                                
                                    })
                            except:
                                raise Warning(_("Row No:{} \nError: File Fields are Missing or Mismatched".format(li)))
                            res = self.create_education(values,li)
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
                        try:
                            values.update( {
                                    'member_code' : line[1],
                                    'study_code' : line[2],
                                    'program' : line[3],
                                    'place':line[4],
                                    'disciplines'  : line[6],
                                    'particulars'  : line[7],
                                    'year' : line[5],
                                    'duration' : line[8],
                                    'mode' : line[9],
                                    'result':line[10],
                                    'remarks':line[11],
                     
                                })
                        except:
                            raise Warning(_("Row No:{} \nError: File Fields are Missing or Mismatched".format(li)))
                        res = self.create_education(values,li)
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
    
    def create_education(self,values,li):
        if not values.get("member_code") or values.get("member_code") == "-":
            raise Warning(_('Line No: {}\nError: Member Code cannot be empty.'.format(li)) )
        if not values.get("study_code") or values.get("study_code") == "-":
            raise Warning(_('Line No: {}\nError: Study Code cannot be empty.'.format(li)) )
        if not values.get("program") or values.get("program") == "-":
            raise Warning(_('Line No: {}\nError: Program cannot be empty.'.format(li)) )
        if not values.get("mode") or values.get("mode") == "-":
            raise Warning(_('Line No: {}\nError: Mode of Education cannot be empty.'.format(li)) )
        
        
        member_code = values.get('member_code')
        program = values.get('program')
        disciplines = values.get('disciplines')
        
        try:
            mem_code = math.floor(float(member_code))
        except:
            mem_code = member_code
        try:   
            study_code = values.get('study_code').upper()
            mode = values.get('mode').lower()
        except:
            raise Warning(_("Line No: {}\nError: Study Code or Mode of Contact field is Mismatched or Incorrect Value".format(li)))
        try:   
            if not values.get('year') or values.get('year') == '-':
                year = False
            else:
                year = str(math.floor(float(values.get('year'))))
        except:
            raise Warning(_("Line No: {}\nError: Year field is Mismatched or Incorrect Value".format(li)))
        
        member_id = self.env['res.member'].search([('unique_code','=',mem_code)])
        study_level_id = self.env['res.study.level'].search([('study_level_code','=',study_code)])
        if not study_level_id:
            study_level_id = self.env['res.study.level'].search(['|',('name','=',study_code.title()),('name','=',study_code.upper())])
        education_obj = self.env['res.member.education']
        
        if member_id and study_level_id:
            data = {
                    'member_id': member_id.id,
                    'study_level_id': study_level_id[0].id,
                    'program_id': self.find_program_id(study_level_id[0],program,li),
                    'core_disiplines_ids' : self.find_disciplines(disciplines) if disciplines else False,
                    'particulars': values.get('particulars') if not values.get('particulars') == "-" else False,
                    'institution': values.get('place') if not values.get('place') == "-" else False,
                    'year_of_passing': year,
                    'duration': values.get('duration') if not values.get('duration') == "-" else False,
                    'mode': mode,
                    'result': values.get('result') if not values.get('result') == "-" else False,
                    'note': values.get('remarks') if not values.get('remarks') == "-" else False,
                     
                    }
            try:
                return education_obj.create(data)
            except Exception as e:
                if ',' in str(e):
                    e = str(e).split(',')
                    e = e[0]
                raise Warning(_("Row No:{} \nImport Error: {}".format(li,e)))
        else:
            raise Warning(_("Line No: {} \nError: Member code or Study Level code is Missing or Mismatched".format(li)))

    def find_program_id(self,study_level_id,program,li):
        program_ids = self.env['res.member.program'].search([('study_level_id','=',study_level_id.id)])
        program = program.lower()
        for rec in program_ids:
            code = rec.name.lower()
            if code == program:
                return rec.id
        raise Warning(_("Line No: {} \n Error: Program Name is Mismatched or Incorrect".format(li)))
        
    def find_disciplines(self,disciplines):
        if not disciplines == '-':
            discipline_ids = []
            if ',' in  disciplines:
                dicipline_names = disciplines.split(',')
                for name in dicipline_names:
                    name = name.title()
                    discipline = self.env['res.core.disiplines'].search([('name', '=', name)])
                    if not discipline:
                        raise Warning(_('Name Like [%s] Discipline not in your system') % name)
                    for rec in discipline:
                        discipline_ids.append(rec.id)
            else:
                name = disciplines.title()
                discipline = self.env['res.core.disiplines'].search([('name', '=', name)])
                if not discipline:
                    raise Warning(_('Name Like [%s] Discipline is not in your system') % name)
                for rec in discipline:
                    discipline_ids.append(rec.id)
                    
            return discipline_ids
        else:
            return False    