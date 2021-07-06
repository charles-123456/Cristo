from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FamilyStatiscics(models.TransientModel):
    _name = 'statistics.family'
    _description = 'Statistics Family'

    @api.onchange('all_category', 'all_zone', 'all_bcc', 'category_ids', 'zone_ids', 'bcc_ids')
    def onchange_all(self):
        if self.all_category:
            self.category_ids = False
        else:
            self.all_category = False
        if self.all_zone:
            self.zone_ids = False
        else:
            self.all_zone = False
        if self.all_bcc:
            self.bcc_ids = False
        else:
            self.all_bcc = False

    all_category = fields.Boolean(string="All Group", default=True)
    category_ids = fields.Many2many("res.ecclesia.zone.category", string="Group")
    all_zone = fields.Boolean(string="All Zone", default=True)
    zone_ids = fields.Many2many("res.ecclesia.zone", string="Zone")
    all_bcc = fields.Boolean(string="All BCC", default=True)
    bcc_ids = fields.Many2many("res.parish.bcc", string="BCC")
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", default = lambda self: self.env.user.diocese_id.id)
    parish_id = fields.Many2one('res.parish', string="Parish", default = lambda self: self.env.user.parish_id.id)

    def get_family_list(self):
        zone = ''
        bcc = ''
        diocese = ''
        parish = ''
        result = []
        zone_str = 'zone.id, zpart.name,'

        if self.all_category:
            group = ''
        else:
            group = 'AND lg.id in (%s)' % str(self.category_ids.ids).strip('[]')
        if self.all_zone:
            zone = 'AND bcc.zone_id is not null'
        elif self.zone_ids:
            zone = 'AND bcc.zone_id in (%s)' % str(self.zone_ids.ids).strip('[]')
        q_zone = 'join res_ecclesia_zone zone on (zone.id = bcc.zone_id)'
        if self.all_bcc:
            bcc = 'AND family.parish_bcc_id is not null'
        elif self.bcc_ids:
            bcc = 'AND family.parish_bcc_id in (%s)' % str(self.bcc_ids.ids).strip('[]')
        if self.diocese_id:
            diocese = ' AND family.diocese_id = (%s)' % str(self.diocese_id.id).strip('[]')
        if self.parish_id:
            parish = ' AND family.parish_id = (%s)' % str(self.parish_id.id).strip('[]')
        
        group_by = ' group by lg.id, lg.name, zone.id, zpart.name, bpart.name, bcc.id order by lg.name, zpart.name asc'
        query = "select lg.id, lg.name, " + zone_str + " bpart.name, " \
               "(select count(id) from res_family where parish_bcc_id = bcc.id) from res_parish_bcc bcc " \
               "join res_family family on (bcc.id = family.parish_bcc_id or bcc.id is not null) " \
                + q_zone + " join res_ecclesia_zone_category lg on(lg.id = zone.category_id) " \
               "join res_partner zpart on (zpart.id=zone.partner_id) " \
               "join res_partner bpart on (bpart.id=bcc.partner_id) " \
               "WHERE family.active_in_parish = True " + zone + " " + bcc + " " + group + diocese + parish + ' ' + group_by

        if query:
            self.env.cr.execute(query)
            family_ids = self.env.cr.fetchall()
            if family_ids:
                id = 0
                group_id = 0
                for family_id in family_ids:
                    family_id = list(family_id)
                    if id == family_id[2]:
                        family_id[3] = ''
                        family_id.append('')
                    if family_id[3]:
                        zone_total = self.get_zone_total_family(family_id[2], group, bcc,diocese,parish)
                        family_id.append(zone_total[0])

                    if group_id == family_id[0]:
                        family_id[1] = ''
                        family_id.append('')
                    if family_id[1]:
                        group_total = self.get_group_total_family(family_id[0], zone, bcc,diocese,parish)
                        family_id.append(group_total[0])

                    result.append(family_id)
                    id = family_id[2]
                    group_id = family_id[0]
                return result
            else:
                raise UserError("No record found")

    def get_zone_total_family(self, zone_id, group, bcc,diocese,parish):
        query = "select count(family.id) from res_family family " \
                "join res_parish_bcc bcc on (bcc.id = family.parish_bcc_id) " \
                "join res_ecclesia_zone zone on (zone.id = bcc.zone_id) " \
                "join res_ecclesia_zone_category lg on(lg.id = zone.category_id) " \
                "WHERE family.active_in_parish = True AND zone.id=" + str(zone_id) + " " + bcc + " " + group + \
                diocese + parish + " group by zone.id"
        if query:
            self.env.cr.execute(query)
            return self.env.cr.fetchone() or [0]

    def get_group_total_family(self, group_id, zone, bcc,diocese,parish):
        query = "select count(family.id) from res_family family " \
                "join res_parish_bcc bcc on (bcc.id = family.parish_bcc_id) " \
                "join res_ecclesia_zone zone on (zone.id = bcc.zone_id) " \
                "join res_ecclesia_zone_category lg on(lg.id = zone.category_id) " \
                "WHERE family.active_in_parish = True AND lg.id=" + str(group_id) + " " + bcc + " " + zone + \
                diocese + parish + " group by lg.id"
        if query:
            self.env.cr.execute(query)
            return self.env.cr.fetchone() or [0]

    def _build_contexts(self, data):
        result = {}
        result['all_category'] = 'all_category' in data['form'] and data['form']['all_category'] or ''
        result['category_ids'] = 'category_ids' in data['form'] and data['form']['category_ids'] or ''
        result['all_zone'] = 'all_zone' in data['form'] and data['form']['all_zone'] or ''
        result['zone_ids'] = 'zone_ids' in data['form'] and data['form']['zone_ids'] or ''
        result['all_bcc'] = 'all_bcc' in data['form'] and data['form']['all_bcc'] or ''
        result['bcc_ids'] = 'bcc_ids' in data['form'] and data['form']['bcc_ids'] or ''
        result['diocese_id'] = 'diocese_id' in data['form'] and data['form']['diocese_id'] or ''
        result['parish_id'] = 'parish_id' in data['form'] and data['form']['parish_id'] or ''
        return result

    def print_pdf(self):
        self.ensure_one()
        data = {}
        family_list = self.get_family_list()
        if family_list:
            data['ids'] = self.env.context.get('active_ids', [])
            data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
            data['form'] = self.read(['all_category','category_ids','all_zone','zone_ids','all_bcc','bcc_ids','diocese_id','parish_id'])[0]
            data['family_list'] = family_list
            self._build_contexts(data)
            return self.env.ref('cristo.statistics_family').report_action(self, data=data, config=False)
