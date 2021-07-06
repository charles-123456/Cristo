from odoo import models

class DirectoryXlsx(models.AbstractModel):
    _name = 'report.cristo_directory.report_directory'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Directory"

    def generate_xlsx_report(self, workbook, data, directory):
        if data['directory']:
            index_head = workbook.add_format(
                    {'bold': True, 'font_color': 'black','align':'center','bg_color': '#87CEFA', 'border': 2})
            index_body = workbook.add_format(
                    {'bold': True, 'font_color': 'black','align':'left','border': 1})
            worksheet = workbook.add_worksheet('Index')
            worksheet.write(1, 1, 'S No.',index_head)
            worksheet.set_column(1,2, 50)
            worksheet.write(1, 2, 'Name',index_head)
            s_no = 1
            for topic in data['directory']:
                if not topic[0]['no_rec']:
                    worksheet.write(s_no+1, 1, s_no, index_body)
                    worksheet.write(s_no+1, 2, topic[0]['name'], index_body)
                    s_no = s_no + 1

            for sheet in data['directory']:
                sheet = sheet[0]
                header_format = workbook.add_format(
                    {'bold': True, 'font_color': 'black','align':'center','bg_color': '#F0F8FF', 'border': 2})
                head_format = workbook.add_format(
                    {'bold': True, 'font_color': 'white', 'align':'center', 'bg_color': '#2F4F4F', 'border': 2})
                head_table_format = workbook.add_format(
                    {'bold': True, 'font_color': 'white', 'align': 'center', 'bg_color': '#B22222', 'border': 2})
                text_format = workbook.add_format({'border':1})

                if not sheet['no_rec']:
                    if sheet['filter']:
                        worksheet = workbook.add_worksheet(sheet['name'])
                        row = 0
                        if sheet['head_table']:
                            hfields = sheet['ri_string']
                            worksheet.merge_range(0, 0, 0, len(hfields) - 1, sheet['head_name'], head_table_format)
                            for i, fieldname in enumerate(hfields):
                                worksheet.set_column(1, i, 30)
                                worksheet.write(1, i, fieldname, header_format)
                            col = 0
                            for hname in sheet['ri_fields']:
                                worksheet.write(2, col, sheet['ri_value'][hname], text_format)
                                col = col + 1
                            row = 4
                        fields = sheet['field_name']
                        if fields:
                            worksheet.merge_range(row,0,row,len(fields)-1,sheet['name'],head_format)
                            row = row + 1
                            for i, fieldname in enumerate(fields):
                                worksheet.set_column(row,i,30)
                                worksheet.write(row, i, fieldname, header_format)
                            row = row + 1
                            for record in sheet['datas']:
                                col = 0
                                for field in sheet['fields']:
                                    worksheet.write(row, col, record[field],text_format)
                                    col = col + 1
                                row = row + 1
                    if sheet['date_filter']:
                        worksheet = workbook.add_worksheet(sheet['name'])
                        if sheet['date_string']:
                            fields = ['Month','Day'] + sheet['date_string']
                            worksheet.merge_range(0,0,0,len(fields)-1,sheet['name'],head_format)
                            for i, fieldname in enumerate(fields):
                                worksheet.set_column(1, i, 30)
                                worksheet.write(1, i, fieldname, header_format)
                            row = 2
                            for record in sheet['datas']:
                                worksheet.write(row, 0, record['month'],text_format)
                                worksheet.write(row, 1, record['day'],text_format)
                                col = 2
                                for name in sheet['date_name']:
                                    for field in sheet['fields']:
                                        val = record[name][field]
                                        values = ', '.join(map(str, val))
                                        worksheet.write(row, col, values,text_format)
                                        col = col + 1
                                row = row + 1

                    if sheet['statistic']:
                        if not sheet['cus_stat']:
                            worksheet = workbook.add_worksheet(sheet['name'])
                            fields = ['S No','Description','Total']
                            worksheet.merge_range(0,0,0, len(fields)-1, sheet['name'], head_format)
                            for i, fieldname in enumerate(fields):
                                worksheet.set_column(1, i, 20)
                                worksheet.write(1, i, fieldname, header_format)
                            row = 2
                            val = 1
                            for record in sheet['datas']:
                                worksheet.write(row, 0, val,text_format)
                                worksheet.write(row, 1, record['name'],text_format)
                                worksheet.write(row, 2, record['count'],text_format)
                                row = row + 1
                                val = val + 1
                        else:
                            worksheet = workbook.add_worksheet(sheet['name'])
                            fields = sheet['fields']
                            worksheet.merge_range(0,0,0, len(fields)-1, sheet['name'], head_format)
                            for i, fieldname in enumerate(fields):
                                worksheet.set_column(1, i, 20)
                                worksheet.write(1, i, fieldname, header_format)
                            row = 2
                            for record in sheet['datas']:
                                col = 0
                                for val in record:
                                    worksheet.write(row, col, val,text_format)
                                    col = col + 1
                                row = row + 1
                            