from odoo import http
from odoo.tools import pycompat
import functools
import logging
import werkzeug
import io
import json
import operator
from odoo.exceptions import UserError
from odoo.http import content_disposition,request,serialize_exception as _serialize_exception
from odoo.addons.web.controllers import main as export
# from odoo.addons.web.controllers.main.ExcelExport import from_data
_logger = logging.getLogger(__name__)

def serialize_exception(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            _logger.exception("An exception occured during an http request")
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))
    return wrap

class ExportFormat(export.ExportFormat):

    @property
    def content_type(self):
        """ Provides the format's content type """
        raise NotImplementedError()

    def filename(self, base):
        """ Creates a valid filename for the format (with extension) from the
         provided base name (exension-less)
        """
        raise NotImplementedError()

    def from_data(self, fields, rows):
        """ Conversion method from Odoo's export data to whatever the
        current export class outputs

        :params list fields: a list of fields to export
        :params list rows: a list of records to export
        :returns:
        :rtype: bytes
        """
        raise NotImplementedError()

    def from_group_data(self, fields, groups):
        raise NotImplementedError()

    def base(self, data, token):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)

        field_names = [f['name'] for f in fields]
        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]

        Model = request.env[model].with_context(**params.get('context', {}))
        groupby = params.get('groupby')
        if not import_compat and groupby:
            domain = [('id', 'in', ids)] if ids else domain
            groups_data = Model.read_group(domain, field_names, groupby, lazy=False)

            # read_group(lazy=False) returns a dict only for final groups (with actual data),
            # not for intermediary groups. The full group tree must be re-constructed.
            tree = GroupsTreeNode(Model, field_names, groupby)
            for leaf in groups_data:
                tree.insert_leaf(leaf)

            response_data = self.from_group_data(fields, tree)
        else:
            Model = Model.with_context(import_compat=import_compat)
            records = Model.browse(ids) if ids else Model.search(domain, offset=0, limit=False, order=False)

            if not Model._is_an_ordinary_table():
                fields = [field for field in fields if field['name'] != 'id']

            export_data = records.export_data(field_names).get('datas',[])
            response_data = self.from_data(columns_headers, export_data, model, import_compat)
        return request.make_response(response_data,
            headers=[('Content-Disposition',
                            content_disposition(self.filename(model))),
                     ('Content-Type', self.content_type)],
            cookies={'fileToken': token})

class ExcelExport(ExportFormat, export.ExcelExport):
    @http.route()
    @serialize_exception
    def index(self, data, token):
        return self.base(data, token)

    @property
    def content_type(self):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def filename(self, base):
        return base + '.xlsx'

    def from_group_data(self, fields, groups):
        with export.GroupExportXlsxWriter(fields, groups.count) as xlsx_writer:
            x, y = 1, 0
            for group_name, group in groups.children.items():
                x, y = xlsx_writer.write_group(x, y, group_name, group)

        return xlsx_writer.value

    def from_data(self, fields, rows, model, import_compat):
        with export.ExportXlsxWriter(fields, len(rows)) as xlsx_writer:
            for row_index, row in enumerate(rows):
                for cell_index, cell_value in enumerate(row):
                    if import_compat:
                        field_id = request.env['ir.model.fields'].search([('name','=',fields[cell_index]),('model_id.model','=',model)],limit=1)
                    else:
                        field_id = request.env['ir.model.fields'].search([('field_description','=',fields[cell_index]),('model_id.model','=',model)],limit=1)
                    if field_id.ttype != 'boolean':
                        cell_value = pycompat.to_text(cell_value)
                    xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)

        return xlsx_writer.value

class CSVExport(ExportFormat, export.CSVExport):
    @http.route()
    @serialize_exception
    def index(self, data, token):
        return self.base(data, token)

    @property
    def content_type(self):
        return 'text/csv;charset=utf8'

    def filename(self, base):
        return base + '.csv'

    def from_group_data(self, fields, groups):
        raise UserError(_("Exporting grouped data to csv is not supported."))

    def from_data(self, fields, rows, model, import_compat):
        fp = io.BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1)

        writer.writerow(fields)

        for data in rows:
            row = []
            for i, d in enumerate(data):
                # Spreadsheet apps tend to detect formulas on leading =, + and -
                if isinstance(d, str) and d.startswith(('=', '-', '+')):
                    d = "'" + d
                if import_compat:
                    field_id = request.env['ir.model.fields'].search([('name','=',fields[i]),('model_id.model','=',model)],limit=1)
                else:
                    field_id = request.env['ir.model.fields'].search([('field_description','=',fields[i]),('model_id.model','=',model)],limit=1)
                if field_id.ttype == 'boolean':
                    row.append(d)
                else:
                    row.append(pycompat.to_text(d))
            writer.writerow(row)

        return fp.getvalue()
    