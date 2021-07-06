# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from datetime import date,datetime,timedelta

class Member(models.Model):
    _inherit = 'res.member'
    
    def get_ecc_birthday_list(self,params):
        query = """select *, 
            (to_char(dob,'ddd')::int-to_char(now(),'ddd')::int+total_days)%total_days as dif
            from (select he.id, rp.id as partner_id, concat(rpt.name,' ',concat(rp.name,' ',he.last_name)) as name, trim(to_char(he.dob, 'dd - Month')) as birthday,he.dob as dob,he.diocese_id as diocese,he.parish_id as parish,he.vicariate_id as vic,he.member_type as mem,he.membership_type as mem_ship,
            (to_char((to_char(now(),'yyyy')||'-12-31')::date,'ddd')::int) as total_days
            FROM res_member he
            join res_partner rp on rp.id=he.partner_id
            left join res_partner_title rpt on rpt.id=rp.title
            ) birth
            where (to_char(dob,'ddd')::int-to_char(now(),'DDD')::int+total_days)%total_days between 0 and 30 {0}
            order by dif,dob desc;""".format(params)
        self.env.cr.execute(query)
        birthdays_results = self.env.cr.dictfetchall()
        query1 = """select *, 
            (to_char(dob,'ddd')::int-to_char(now(),'ddd')::int+total_days)%total_days as dif
            from (select he.id, rp.id as partner_id, concat(rpt.name,' ',concat(rp.name,' ',he.last_name)) as name, trim(to_char(he.dob, 'dd - Month')) as birthday,he.dob as dob,he.diocese_id as diocese,he.parish_id as parish,he.vicariate_id as vic,he.member_type as mem,he.membership_type as mem_ship,
            (to_char((to_char(now(),'yyyy')||'-12-31')::date,'ddd')::int) as total_days
            FROM res_member he
            join res_partner rp on rp.id=he.partner_id
            left join res_partner_title rpt on rpt.id=rp.title
            ) birth
            where (to_char(dob,'ddd')::int-to_char(now(),'DDD')::int+total_days)%total_days = 365 {0}
            order by dif,dob desc;""".format(params)
        self.env.cr.execute(query1)
        today_birth = self.env.cr.dictfetchall()
        for b in today_birth:
            birthdays_results.insert(0,b)
        return birthdays_results
    
    def get_ecc_anniversary_list(self,params):
        query = """select rm.partner_id,ho.id,ho.date,ho."order",concat(rpt.name,' ',concat(rp.name,' ',rm.last_name)) as name,to_char(ho.date,'dd - Month') as od,(to_char(ho.date,'ddd')::int-to_char(now(),'ddd')::int) as days 
            from res_holyorder ho
            join res_member rm ON(rm.id=ho.member_id)
            join res_partner rp ON(rp.id=rm.partner_id)
            left join res_partner_title rpt on rpt.id=rp.title
            where (to_char(ho.date,'ddd')::int-to_char(now(),'ddd')::int) between 0 and 30 AND ho."order" = 'priest' AND rm.member_type = 'priest' AND rm.membership_type = 'SE' {}
            order by days asc""".format(params)
        self.env.cr.execute(query)
        anniversary_results = self.env.cr.dictfetchall()
        return anniversary_results
    
    @api.model
    def get_diocese_parish_details(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().browse(uid)
        member = self.env['res.member'].sudo().search_read([('partner_id','=',user.partner_id.id)],fields=['id','name'],limit=1)
        if member or user:
            if not member:
                member = self.env['res.users'].sudo().search_read([('id','=',user.id)],fields=['id','name','diocese_id','parish_id'],limit=1)
            bday_param = "AND( mem = 'member' or (mem ='priest' AND mem_ship='SE'))"
            ann_param = ''
            data = {}
            data.update({'valid_user':1,'user':self.env['res.users'].sudo().search_read([('id','=',uid)],fields=['id','name'])})
            mem_domain = []
            if self.user_has_groups('base.group_erp_manager') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
#               Diocese
                total_diocese = self.env['res.ecclesia.diocese'].search_count([])
                
#               Vicariate  
                total_vicariate = self.env['res.vicariate'].search_count([])
                
#               Parish
                total_parish = self.env['res.parish'].search_count([])

#               Substation
                total_station = self.env['res.parish.sub.station'].search_count([])
                
#               Family
                total_family = self.env['res.family'].search_count([])
                
#               Members
                total_member = self.env['res.member'].search_count([('member_type','=','member')])
                                                             
#               Baptism            
                total_baptism = self.env['res.baptism'].search_count([])
                
#               First Holy Communion
                total_fhc = self.env['res.communion'].search_count([])
                
#               Confirmation
                total_confirmation = self.env['res.confirmation'].search_count([]) 
                
#               Marriage
                total_marriage = self.env['res.marriage'].search_count([]) 
                 
#               Death     
                total_death = self.env['res.death'].search_count([]) 
                    
#               Slider
                image_ids = self.env['org.image'].search([('diocese_id','=',self.env.user.diocese_id.id),('video_url','=',False)]).ids
                msg='Cristo'
                
                data.update({'all':1,'ecclesia':1,'total_vicariate':total_vicariate,'total_parish':total_parish,
                             'total_station':total_station,'total_family':total_family,
                             'total_member':total_member,'slider_ids':image_ids,'default_img': 1,'sl_msg':msg,
                             'total_diocese':total_diocese,'total_baptism':total_baptism,'total_fhc':total_fhc,'total_confirmation':total_confirmation,
                             'total_marriage':total_marriage,'total_death':total_death})
            elif self.user_has_groups('cristo.group_role_cristo_diocese'):
#                Birthday parameter values
                bday_param = "AND (mem = 'member' or (mem ='priest' AND mem_ship ='SE')) AND diocese = %d" % (self.env.user.diocese_id.id)
                ann_param = 'AND rm.diocese_id = %d' % (self.env.user.diocese_id.id)
                # Diocese Level Counts
                total_diocese = self.env['res.ecclesia.diocese'].search_count([('id', '=', user.diocese_id.id)])
                total_vicariate = self.env['res.vicariate'].search_count([('diocese_id', '=', user.diocese_id.id)])
                total_parish = self.env['res.parish'].search_count([('diocese_id', '=', user.diocese_id.id)])
                total_station = self.env['res.parish.sub.station'].search_count(
                    [('diocese_id', '=', user.diocese_id.id)])
                total_family = self.env['res.family'].search_count([('diocese_id', '=', user.diocese_id.id)])
                total_member = self.env['res.member'].search_count(['&',('diocese_id', '=', user.diocese_id.id),('member_type','=','member')])
                total_baptism = self.env['res.baptism'].search_count(
                    [('parish_id.diocese_id', '=', user.diocese_id.id)])
                total_fhc = self.env['res.communion'].search_count([('parish_id.diocese_id', '=', user.diocese_id.id)])
                total_confirmation = self.env['res.confirmation'].search_count(
                    [('parish_id.diocese_id', '=', user.diocese_id.id)])
                total_marriage = self.env['res.marriage'].search_count(
                    [('parish_id.diocese_id', '=', user.diocese_id.id)])
                total_death = self.env['res.death'].search_count([('parish_id.diocese_id', '=', user.diocese_id.id)])

                # Diocese Slider Images
                default_img = 0
                image_ids = self.env['org.image'].search(
                    [('diocese_id', '=', self.env.user.diocese_id.id), ('video_url', '=', False)]).ids
                if not image_ids:
                    default_img = 1
                msg = user.diocese_id.name 


                data.update({'diocese': 1, 'total_vicariate': total_vicariate, 'total_parish': total_parish,
                             'total_station': total_station, 'total_family': total_family,
                             'total_member': total_member, 'slider_ids': image_ids, 'default_img': default_img,
                             'sl_msg': msg or 'Cristo',
                             'total_diocese': total_diocese, 'total_baptism': total_baptism, 'total_fhc': total_fhc,
                             'total_confirmation': total_confirmation,
                             'total_marriage': total_marriage, 'total_death': total_death})

            elif self.user_has_groups('cristo.group_role_cristo_vicarate'):
#               Birthday parameter values
                bday_param = "AND (mem = 'member' or (mem ='priest' AND mem_ship ='SE')) AND vic = %d" % (self.env.user.vicariate_id.id)
                ann_param = 'AND rm.vicariate_id = %d' % (self.env.user.vicariate_id.id)
                # Vicariate Level Counts
                total_diocese = self.env['res.ecclesia.diocese'].search_count([('id', '=', user.diocese_id.id)])
                total_vicariate = self.env['res.vicariate'].search_count([('id', '=', user.vicariate_id.id)])
                total_parish = self.env['res.parish'].search_count([('vicariate_id', '=', user.vicariate_id.id)])
                total_station = self.env['res.parish.sub.station'].search_count(
                    [('vicariate_id', '=', user.vicariate_id.id)])
                total_family = self.env['res.family'].search_count([('vicariate_id', '=', user.vicariate_id.id)])
                total_member = self.env['res.member'].search_count(['&',('vicariate_id', '=', user.vicariate_id.id),('member_type','=','member')])
                total_baptism = self.env['res.baptism'].search_count(
                    [('parish_id.vicariate_id', '=', user.vicariate_id.id)])
                total_fhc = self.env['res.communion'].search_count(
                    [('parish_id.vicariate_id', '=', user.vicariate_id.id)])
                total_confirmation = self.env['res.confirmation'].search_count(
                    [('parish_id.vicariate_id', '=', user.vicariate_id.id)])
                total_marriage = self.env['res.marriage'].search_count(
                    [('parish_id.vicariate_id', '=', user.vicariate_id.id)])
                total_death = self.env['res.death'].search_count(
                    [('parish_id.vicariate_id', '=', user.vicariate_id.id)])

                # Vicariate Slider Images
                default_img = 0
                image_ids = self.env['org.image'].search(
                    [('vicariate_id', '=', user.vicariate_id.id), ('video_url', '=', False)]).ids
                if not image_ids:
                    default_img = 1
                msg = self.env.user.vicariate_id.name
                if not msg:
                    msg='Cristo'

                data.update({'vicariate': 1, 'total_vicariate': total_vicariate, 'total_parish': total_parish,
                             'total_station': total_station, 'total_family': total_family,
                             'total_member': total_member, 'slider_ids': image_ids, 'default_img': default_img,
                             'sl_msg': msg,
                             'total_diocese': total_diocese, 'total_baptism': total_baptism, 'total_fhc': total_fhc,
                             'total_confirmation': total_confirmation,
                             'total_marriage': total_marriage, 'total_death': total_death})
            elif self.user_has_groups('cristo.group_role_cristo_parish_ms'):
                #Birthday parameter values
                bday_param = "AND (mem = 'member' or (mem ='priest' AND mem_ship ='SE')) AND parish = %d" % (self.env.user.parish_id.id)
                ann_param = 'AND rm.parish_id = %d' % (self.env.user.parish_id.id)
                # Parish Level Counts
                total_diocese = self.env['res.ecclesia.diocese'].search_count([('id', '=', user.diocese_id.id)])
                total_vicariate = self.env['res.vicariate'].search_count([('id', '=', user.vicariate_id.id)])
                total_parish = self.env['res.parish'].search_count([('vicariate_id', '=', user.vicariate_id.id)])
                total_station = self.env['res.parish.sub.station'].search_count([('parish_id', '=', user.parish_id.id)])
                total_family = self.env['res.family'].search_count([('parish_id', '=', user.parish_id.id)])
                total_member = self.env['res.member'].search_count(['&',('parish_id', '=', user.parish_id.id),('member_type','=','member')])
                total_baptism = self.env['res.baptism'].search_count([('parish_id', '=', user.parish_id.id)])
                total_fhc = self.env['res.communion'].search_count([('parish_id', '=', user.parish_id.id)])
                total_confirmation = self.env['res.confirmation'].search_count([('parish_id', '=', user.parish_id.id)])
                total_marriage = self.env['res.marriage'].search_count([('parish_id', '=', user.parish_id.id)])
                total_death = self.env['res.death'].search_count([('parish_id', '=', user.parish_id.id)])

                # Parish Slider Images
                default_img = 0
                image_ids = self.env['org.image'].search(
                    [('parish_id', '=', user.parish_id.id), ('video_url', '=', False)]).ids
                if not image_ids:
                    default_img = 1
                msg = self.env.user.parish_id.name
                if not msg:
                    msg='Cristo'

                data.update({'parish': 1, 'total_vicariate': total_vicariate, 'total_parish': total_parish,
                             'total_station': total_station, 'total_family': total_family,
                             'total_member': total_member, 'slider_ids': image_ids, 'default_img': default_img,
                             'sl_msg': msg,
                             'total_diocese': total_diocese, 'total_baptism': total_baptism, 'total_fhc': total_fhc,
                             'total_confirmation': total_confirmation,
                             'total_marriage': total_marriage, 'total_death': total_death})
#           Birthday
            birthdays_results = self.get_ecc_birthday_list(bday_param)
            for bd in birthdays_results:
                bd['img_data'] = self.get_image_data(bd['partner_id'])
            anniversay_result = self.get_ecc_anniversary_list(ann_param)
            for an in anniversay_result:
                an['img_data'] = self.get_image_data(an['partner_id'])
                ho_id = self.env['res.holyorder'].sudo().browse(an['id'])
                an['order'] = dict(ho_id._fields['order'].selection).get(ho_id.order)
            data.update({'birthdays':birthdays_results or 0,'anniversary':anniversay_result or 0,'today':datetime.today().strftime("%d - %B")})
            member[0].update(data)
            return member or False