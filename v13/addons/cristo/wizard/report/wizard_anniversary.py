from odoo import models, fields, api
from odoo.exceptions import UserError

class AnniversaryReport(models.TransientModel):
    _name = 'anniversary.report'
    _description = 'Anniversary Report'
    
    birth_day = fields.Boolean(string="Birth Day", default=True)
#     feast_day = fields.Boolean(string="Feast Day")
    ordination_day = fields.Boolean(string="Ordination Day")
    month_ids = fields.Many2many('res.month', string="Month", required=True)
    
    def birthday_list(self, params):
        query = """ 
                select 
                    rm.member_name as name
                from 
                    res_member rm
                    left join res_partner as rp on rp.id = rm.partner_id
                where {0}
            """.format(params)
        self.env.cr.execute(query)
        data = self.env.cr.fetchall()
        return data
    
    def feastday_list(self, params):
        query = """
                select
                    rm.member_name as name
                from  res_member as rm
                    left join res_partner as rp on rp.id = rm.partner_id
                where rm.feast_month is not null and {0}
            """.format(params)
        self.env.cr.execute(query)
        data = self.env.cr.fetchall()
        return data
    
    def ordinationday_list(self, params):
        query = """
                select
                    rm.member_name as name
                from res_member as rm
                    left join res_partner as rp on rp.id = rm.partner_id
                    left join res_holyorder as rh on rh.member_id = rm.id
                where rh.order ilike 'priest' and {0}
            """.format(params)
        self.env.cr.execute(query)
        data = self.env.cr.fetchall()
        return data

    def anniversary_list(self):
        user = self.env.user
#         query = []
        if self.month_ids:
            months = self.env['res.month'].search([('id','in',self.month_ids.ids)])
            if self.birth_day:
                month_cond = " AND extract(month from rm.dob) in ({})".format(str(months.ids).strip('[]'))
#             if self.feast_day:
#                 month_cond = " AND rm.feast_month::double precision in ({})".format(str(months.ids).strip('[]'))
            if self.ordination_day:
                month_cond = " AND extract(month from rh.date) in ({})".format(str(months.ids).strip('[]'))
        else:
            month_cond = ""
            months = self.env['res.month'].search([])
        data = []
        for m in months:
            for d in range(1,31):
                s = {'month':m.name,'day':d}
                bday = ''
                fday = ''
                oday = ''
                if self.birth_day:
                    params = "extract(day from rm.dob) = {0} and extract(month from rm.dob) = {1}".format(d,m.id)
                    rec = self.birthday_list(params)
                    if rec:
                        bday = True
                    s.update({'birth_members':', '.join(r[0] for r in rec)})
#                 if self.feast_day:
#                     params = "rm.feast_day::int = {0} and rm.feast_month::double precision = {1}".format(d,m.id)
#                     rec = self.feastday_list(params)
#                     if rec:
#                         fday = True
#                     s.update({'feast_members':', '.join(r[0] for r in rec)})
                if self.ordination_day:
                    params = "extract(day from rh.date) = {0} and extract(month from rh.date) = {1}".format(d,m.id)
                    rec = self.ordinationday_list(params)
                    if rec:
                        oday = True
                    s.update({'ordi_members':', '.join(r[0] for r in rec)})
                if bday or fday or oday:
                    data.append(s)
        return data
        
        
        if self.user_has_groups('base.group_erp_manager') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            params = "rm.membership_type is not null" + month_cond
        elif self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
            params = "rm.membership_type = 'RE' and rm.institute_id=%d" % (user.institute_id.id) + month_cond
        elif self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution') or  self.user_has_groups('cristo.group_role_cristo_individual'):
            params = "rm.membership_type = 'RE' and rm.institute_id=%d and rm.rel_province_id=%d" % (user.institute_id.id,user.rel_province_id.id) + month_cond
        elif self.user_has_groups('cristo.group_role_cristo_ec_region') or self.user_has_groups('cristo.group_role_cristo_ec_province') or self.user_has_groups('cristo.group_role_cristo_diocese') or self.user_has_groups('cristo.group_role_cristo_vicarate') or self.user_has_groups('cristo.group_role_cristo_parish_ms') or self.user_has_groups('cristo.group_role_cristo_bcc'):
            membership_type = "rm.membership_type = 'SE'" + month_cond
                    

#         if query:
#             self.env.cr.execute(query)
#             member_ids = self.env.cr.fetchall()
#             if member_ids:
#                 return member_ids
#             else:
#                 raise UserError("No record found")
#         else:
#             raise UserError("Please select the Report Option.")
    
    def _build_contexts(self, data):
        result = {}
        result['birth_day'] = 'birth_day' in data['form'] and data['form']['birth_day'] or ''
#         result['feast_day'] = 'feast_day' in data['form'] and data['form']['feast_day'] or ''
        result['ordination_day'] = 'ordination_day' in data['form'] and data['form']['ordination_day'] or ''
        result['month_ids'] = 'month_ids' in data['form'] and data['form']['month_ids'] or ''
        return result
    
    def print_pdf(self):
        self.ensure_one()
        data = {}
        anniversary_list = self.anniversary_list()
        if anniversary_list:
            data['ids'] = self.env.context.get('active_ids', [])
            data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
            data['form'] = self.read(['birth_day','ordination_day','month_ids'])[0]
#             data['form'] = self.read(['birth_day','feast_day','ordination_day','month_ids'])[0]
            used_context = self._build_contexts(data)
            data['anniversary_list'] = anniversary_list
            data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
            return self.env.ref('cristo.anniversary_report').report_action(self, data=data)
    


#     def all_anniversary_list(self,params):
#         query = """
#                 select 
#                     ani.id,
#                     ani.month,
#                     ani.day,
#                     ani.mon,
#                     max(case 
#                         when ani.flag='dob' then ani.name
#                              else ''
#                            end) as dob,
#                     max(case 
#                         when ani.flag='feast' then ani.name
#                              else ''
#                            end) as feast,
#                     max(case 
#                         when ani.flag='ordination' then ani.name
#                              else ''
#                            end) as ordination
#                 from
#                     (select 
#                           rm.id,
#                          to_char(rm.dob,'Mon') as month,
#                           extract(month from rm.dob) as mon,
#                          extract(day from rm.dob) as day,
#                          rm.member_name as name,
#                          'dob' as flag
#                     from 
#                         res_member rm
#                         left join res_partner as rp on rp.id = rm.partner_id
#                     where {0}
#                     union all
#                     select
#                         rm.id,
#                         to_char(to_timestamp(rm.feast_month, 'MM'), 'Mon') as month,
#                          rm.feast_month::double precision as mon,
#                         rm.feast_day::int as day, 
#                         rm.member_name as name,
#                         'feast' as flag
#                     from  res_member as rm
#                         left join res_partner as rp on rp.id = rm.partner_id
#                     where {0} and rm.feast_month is not null
#                     union all
#                     select
#                          rm.id,
#                          to_char(rh.date,'Mon') as month,
#                          extract(month from rh.date) as mon,
#                          extract(day from rh.date) as day,
#                          rm.member_name as name,
#                          'ordination' as flag
#                     from  res_member as rm
#                         left join res_partner as rp on rp.id = rm.partner_id
#                         left join res_holyorder as rh on rh.member_id = rm.id
#                     where {0} and rh.order ilike 'priest') as ani
#                 group by ani.id, ani.month, ani.day, ani.mon
#                 order by ani.mon, ani.day
#             """.format(params)
#         return query    
    
#     def birthday_feastday_list(self,params):
#         query = """
#                 select 
#                     ani.id,
#                     ani.month,
#                     ani.day,
#                     ani.mon,
#                     max(case 
#                         when ani.flag='dob' then ani.name
#                              else ''
#                            end) ordinationday_listas dob,
#                     max(case 
#                         when ani.flag='feast' then ani.name
#                              else ''
#                            end) as feast
#             
#                 from
#                     (select 
#                           rm.id,
#                          to_char(rm.dob,'Mon') as month,
#                           extract(month from rm.dob) as mon,
#                          extract(day from rm.dob) as day,
#                          rm.member_name as name,
#                          'dob' as flag
#                     from 
#                         res_member rm
#                         left join res_partner as rp on rp.id = rm.partner_id
#                     where {0}ordination_day
#                     union all
#                     select
#                         rm.id,
#                         to_char(to_timestamp(rm.feast_month, 'MM'), 'Mon') as month,
#                          rm.feast_month::double precision as mon,
#                         rm.feast_day::int as day, 
#                         rm.member_name as name,
#                         'feast' as flag
#                     from  res_member as rm
#                         left join res_partner as rp on rp.id = rm.partner_id
#                     where {0} and rm.feast_month is not null) as ani
#                 group by ani.id, ani.month, ani.day, ani.mon
#                 order by ani.mon, ani.day
#             """.format(params)
#         return query
    
#     def birthday_ordinationday_list(self,params):
#         query = """
#                 select 
#                     ani.id,
#                     ani.month,
#                     ani.day,
#                     ani.mon,
#                     max(case 
#                         when ani.flag='dob' then ani.name
#                              else ''
#                          + month_cond   end) as dob,
#                     max(case 
#                         when ani.flag='feast' then ani.name
#                              else ''
#                            end) as feast,
#                     max(case 
#                         when ani.flag='ordination' then ani.name
#                              else ''
#                            end) as ordination
#                 from
#                     (select 
#                           rm.id,
#                          to_char(rm.dob,'Mon') as month,
#                           extract(month from rm.dob) as mon,
#                          extract(day from rm.dob) as day,
#                          rm.member_name as name,
#                          'dob' as flagprint(months)
#                     from 
#                         res_member rm
#                         left join res_partner as rp on rp.id = rm.partner_id
#                     where {0}
#                     union all
#                     select
#                          rm.id,
#                          to_char(rh.date,'Mon') as month,
#                          extract(month from rh.date) as mon,
#                          extract(day from rh.date) as day,
#                          rm.member_name as name,
#                          'ordination' as flag
#                     from  res_member as rm
#                         left join res_partner as rp on rp.id = rm.partner_id
#                         left join res_holyorder as rh on rh.member_id = rm.id
#                     where {0} and rh.order ilike 'priest') as ani
#                 group by ani.id, ani.month, ani.day, ani.mon
#                 order by ani.mon, ani.day
#             """.format(params)
#         return query
    
#     def feastday_ordinationday_list(self,params):
#         query = """
#                 select 
#                     ani.id,
#                     ani.month,
#                     ani.day,
#                     ani.mon,
#                     max(case 
#                         when ani.flag='dob' then ani.name
#                              else ''
#                            end) as dob,
#                     max(case 
#                         when ani.flag='feast' then ani.name
#                              else ''
#                            end) as feast,
#                     max(case 
#                        #         if query:
# #             self.env.cr.execute(query)
# #             member_ids = self.env.cr.fetchall()
# #             if member_ids:
# #                 return member_ids
# #             else:
# #                 raise UserError("No record found")
# #         else:
# #             raise UserError("Please select the Report Option.") when ani.flag='ordination' then ani.name
#                              else ''
#                            end) as ordination
#                 from
#                     (select rm.id,
#                         to_char(to_timestamp(rm.feast_month, 'MM'), 'Mon') as month,
#                          rm.feast_month::double precision as mon,
#                         rm.feast_day::int as day, 
#                         rm.member_name as name,
#                         'feast' as flag
#                     from  res_member as rm
#                         left join res_partner as rp on rp.id = rm.partner_id
#                     where {0} and rm.feast_month is not null
#                     union all
#                     select
#                          rm.id,
#                          to_char(rh.date,'Mon') as month,
#                          extract(month from rh.date) as mon,
#                          extract(day from rh.date) as day,
#                          rm.member_name as name,
#                          'ordination' as flag
#                     from  res_member as rm
#                         left join res_partner as rp on rp.id = rm.partner_id
#                         left join res_h    olyorder as rh on rh.member_id = rm.id
#                     where {0} and rh.order iliordination_dayke 'priest') as ani
#                 group by ani.id, ani.month, ani.day, ani.mon
#                 order by ani.mon, ani.day
#             """.format(params)
#         return query
    
    
    
#         if self.birth_day == True and self.feast_day == True and self.ordination_day == True:
#             query = self.all_anniversary_list(params)
#         elif self.birth_day == True and self.feast_day == True:
#             query = self.birthday_feastday_list(params)
#         elif self.birth_day == True and self.ordination_day == True:
#             query = self.birthday_ordinationday_list(params)
#         elif self.feast_day == True and self.ordination_day == True:
#             query = self.feastday_ordinationday_list(params)
#         
#         
#         elif self.birth_day == True:
#             query = self.birthday_list(params)
#         elif self.feast_day == True:
#             query = self.feastday_list(params)
#         elif self.ordination_day == True:
#             query = self.ordinationday_list(params)  
        