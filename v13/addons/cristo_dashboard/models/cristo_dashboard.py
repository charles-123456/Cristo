# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from datetime import date,datetime,timedelta

class Member(models.Model):
    _inherit = 'res.member'
    
    def get_return_action(self):
        '''
            This function is used to navigate Confrere based on Religious or Secular. (Called from Javascript)
        '''
        if self.user_has_groups('base.group_erp_manager') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin') or self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or\
        self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            return {'action':'cristo.action_res_religious_priest'}
        else:
            return {'action':'cristo.action_res_secular_priest'}
    
    def institution_category(self):
        school_cat_ids = self.env['res.institution.category'].search(['|',('name','ilike','school'),('name','ilike','secondary')])
        college_cat_ids = self.env['res.institution.category'].search([('name','ilike','college'),('name','not ilike','hostel'),('name','not ilike','secondary')])
        parish_cat_ids = self.env['res.institution.category'].search([('name','ilike','parish')])
        boarding_cat_ids = self.env['res.institution.category'].search([('name','ilike','boarding')])
        formation_cat_ids = self.env['res.institution.category'].search([('name','ilike','formation')])
        health_cat_ids = self.env['res.institution.category'].search([('name','ilike','health')])
        retreat_cat_ids = self.env['res.institution.category'].search([('name','ilike','retreat')])
        technical_cat_ids = self.env['res.institution.category'].search([('name','ilike','technical')])
        return (school_cat_ids,college_cat_ids,parish_cat_ids,boarding_cat_ids,formation_cat_ids,health_cat_ids,retreat_cat_ids,technical_cat_ids)
    
    def member_type_count(self,domain):
        bishop = self.env['res.member'].search_count(domain+[('member_type','=','bishop')])
        priest = self.env['res.member'].search_count(domain+[('member_type','=','priest')])
        lay_brother = self.env['res.member'].search_count(domain+[('member_type','=','lay_brother')])
        deacon = self.env['res.member'].search_count(domain+[('member_type','=','deacon')])
        brother = self.env['res.member'].search_count(domain+[('member_type','=','brother')])
        sister = self.env['res.member'].search_count(domain+[('member_type','=','sister')])
        novice = self.env['res.member'].search_count(domain+[('member_type','=','novice')])
        user = self.env.user
        if user.institute_id.institute_type in ['priest','lay_brother','brother']:
            lt = [('Bishop',bishop),('Priest',priest),('Lay Brother',lay_brother),('Deacon',deacon),('Brothers',brother),('Novice',novice)]
            return (lt,bishop+priest+lay_brother+deacon+brother+novice)
        elif user.institute_id.institute_type in ['sister_apostolic','sister_contemplative']:
            lt = [('Bishop',bishop),('Deacon',deacon),('Sister',sister),('Novice',novice)]
            return (lt,bishop+deacon+sister+novice)
        else:
            lt = [('Bishop',bishop),('Priest',priest),('Lay Brother',lay_brother),('Deacon',deacon),('Brothers',brother),('Sister',sister),('Novice',novice)]
            return (lt,bishop+priest+lay_brother+deacon+brother+sister+novice)
    
    @api.model
    def get_member_statistics(self):
        members = self.member_type_count([])
        lbl = []
        val = []
        for m in members[0]:
            lbl.append(m[0])
            val.append(m[1])
        return {'labels':lbl,'values':val}
    
    def get_image_data(self, partner_id):
        partner = self.env['res.partner'].with_user(self.env.ref('base.group_erp_manager')).search([('id','=',partner_id)])
        if partner.image_1920:
            return "data:image/png;base64,{}".format(partner.image_1920.decode('utf-8'))
        else:
            return False
    
    def get_birthday_list(self,params):
        query = """select *, 
            (to_char(dob,'ddd')::int-to_char(now(),'ddd')::int+total_days)%total_days as dif
            from (select he.id, rp.id as partner_id, concat(rpt.name,' ',concat(rp.name,' ',he.last_name)) as name, trim(to_char(he.dob, 'dd - Month')) as birthday,he.dob as dob,he.institute_id as cong,he.rel_province_id as prov,
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
            from (select he.id, rp.id as partner_id, concat(rpt.name,' ',concat(rp.name,' ',he.last_name)) as name, trim(to_char(he.dob, 'dd - Month')) as birthday,he.dob as dob,he.institute_id as cong,he.rel_province_id as prov,
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
    
    def get_anniversary_list(self,params):
        query = """select rm.partner_id,ho.id,ho.date,ho."order",concat(rpt.name,' ',concat(rp.name,' ',rm.last_name)) as name,to_char(ho.date,'dd - Month') as od,(to_char(ho.date,'ddd')::int-to_char(now(),'ddd')::int) as days 
            from res_holyorder ho
            join res_member rm ON(rm.id=ho.member_id)
            join res_partner rp ON(rp.id=rm.partner_id)
            left join res_partner_title rpt on rpt.id=rp.title
            where (to_char(ho.date,'ddd')::int-to_char(now(),'ddd')::int) between 0 and 30 AND ho."order" = 'priest' {}
            order by days asc""".format(params)
        self.env.cr.execute(query)
        anniversary_results = self.env.cr.dictfetchall()
        return anniversary_results
    
    def get_communities(self,field):
        query = """select rp.name,count(rc.id) from res_community rc
                    join res_religious_zone rz on (rz.id=rel_zone_id)
                    join res_partner rp on (rp.id=rz.partner_id)
                    where rc.rel_province_id is not null and rc.rel_province_id=%d group by rc.rel_zone_id,rp.name;""" % (field.id)
        
        self.env.cr.execute(query)
        com = self.env.cr.dictfetchall()
        if com:
            total_com = self.env['res.community'].search_count([('rel_province_id','=',field.id)])
            return (com,total_com)
        else:
            query = """select rp.name,count(rc.id) from res_community rc
                    join res_partner rp on (rp.id=rc.partner_id)
                    where rc.rel_province_id=%d and rp.active=True group by rp.name;"""  % (field.id)
            self.env.cr.execute(query)
            com = self.env.cr.dictfetchall()
            total_com = self.env['res.community'].search_count([('rel_province_id','=',field.id)])
            return (com,total_com)
    
    @api.model
    def get_user_member_details(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().browse(uid)
        member = self.env['res.member'].sudo().search_read([('partner_id','=',user.partner_id.id)],fields=['id','name','rel_province_id'],limit=1)
        if member or user:
            if not member:
                member = self.env['res.users'].sudo().search_read([('id','=',user.id)],fields=['id','name','rel_province_id'],limit=1)
            bday_param = ann_param = ''
            data = {}
            data.update({'valid_user':1,'view_holyorder':0,'user':self.env['res.users'].sudo().search_read([('id','=',uid)],fields=['id','name'])})
            mem_domain = []
            if self.user_has_groups('base.group_erp_manager') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
#                 Congregation
                cong_results = self.env['res.religious.institute'].search_read([],fields=['name'])
                total_cong = self.env['res.religious.institute'].search_count([])

#               Provinces
                pro_results = self.env['res.religious.province'].search_read([],fields=['name'])
                total_pro = self.env['res.religious.province'].search_count([])

#               House/Community  
                query = """select rp.name,count(rc.id) from res_community rc
                    join res_religious_zone rz on (rz.id=rel_zone_id)
                    join res_partner rp on (rp.id=rz.partner_id) group by rp.name;"""
                self.env.cr.execute(query)
                com_results = self.env.cr.dictfetchall()
                total_com = self.env['res.community'].search_count([])
                
#               Institution
                ins_category = self.institution_category()
                school_count = self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[0].ids)])
                college_count = self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[1].ids)])
                parish_count = self.env['res.institution'].search_count(['|',('ministry_category_id','in',ins_category[2].ids),('category_type_id','in',ins_category[2].ids)])
                boarding_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[3].ids)])
                format_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[4].ids)])
                health_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[5].ids)])
                retreat_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[6].ids)])
                technical_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[7].ids)])
                total_insti = self.env['res.institution'].search_count([])

#               Confreres
                mem = self.member_type_count(mem_domain)
                
#               Slider
                image_ids = self.env['org.image'].search([('rel_province_id','=',self.env.user.rel_province_id.id),('video_url','=',False)]).ids
                msg = "Welcome to {}".format("CristO")
                
#               Renewal Members data
                renewals = []
                deadline_date = datetime.today() + timedelta(30)
                renewal_data = self.env['member.statutory.renewals'].search([('valid_to','>=',datetime.today()),('valid_to','<=',deadline_date)])
                for i, dt in enumerate(renewal_data):
                    if dt.valid_to:
                        renewals.append({'sno':i+1,'member':dt.member_id.member_name,'doc_type':dt.document_type_id.name,'valid_to':dt.valid_to.strftime("%d-%b-%Y")})

                data.update({'all':1,'view_holyorder':1,'institute':1,'total_cong':total_cong,'congregations':cong_results,'total_pro':total_pro,'provinces':pro_results,'total_com':total_com,'communities':com_results,'school_count':school_count,'college_count':college_count,'parish_count':parish_count,'boarding_co':boarding_co,'format_co':format_co,'health_co':health_co,'retreat_co':retreat_co,'technical_co':technical_co,'tot_insti':total_insti,'members':mem[0],'tot_members':mem[1],'slider_ids':image_ids,'default_img': 1,'sl_msg':msg,'renewals':renewals if renewals else 0,'feast_dates':0})
            elif self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                bday_param = 'AND cong = %d' % (self.env.user.institute_id.id)
                ann_param = 'AND rm.institute_id = %d' % (self.env.user.institute_id.id)
#               Provinces
                pro_results = self.env['res.religious.province'].search_read([('institute_id','=',self.env.user.institute_id.id)],fields=['name'])
                total_pro = self.env['res.religious.province'].search_count([('institute_id','=',self.env.user.institute_id.id)])

#               House/Community  
                query = """select rp.name,count(rc.id) from res_community rc
                    join res_religious_zone rz on (rz.id=rel_zone_id)
                    join res_partner rp on (rp.id=rz.partner_id)
                    where rc.institute_id is not null and rc.institute_id=%d group by rc.rel_zone_id,rp.name;""" % (self.env.user.institute_id.id)
                self.env.cr.execute(query)
                com_results = self.env.cr.dictfetchall()
                total_com = self.env['res.community'].search_count([('institute_id','=',self.env.user.institute_id.id)])
                
#               Institution
                ins_category = self.institution_category()
                school_count = self.env['res.institution'].search_count([('institute_id','=',self.env.user.institute_id.id),('ministry_category_id','in',ins_category[0].ids)])
                college_count = self.env['res.institution'].search_count([('institute_id','=',self.env.user.institute_id.id),('ministry_category_id','in',ins_category[1].ids)])
                parish_count = self.env['res.institution'].search_count(['|',('ministry_category_id','in',ins_category[2].ids),('category_type_id','in',ins_category[2].ids),('rel_province_id','=',self.env.user.rel_province_id.id)])
                boarding_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[3].ids)])
                format_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[4].ids)])
                health_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[5].ids)])
                retreat_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[6].ids)])
                technical_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[7].ids)])
                total_insti = self.env['res.institution'].search_count([('institute_id','=',self.env.user.institute_id.id)])

#               Confreres
                mem_domain += ['|', ('id', '=', self.env.user.member_id.id), ('institute_id','=',self.env.user.institute_id.id),('membership_type','=','RE')]
                mem = self.member_type_count(mem_domain)
                
#               Slider
                image_ids = self.env['org.image'].search([('institute_id','=',self.env.user.institute_id.id),('video_url','=',False)]).ids
                msg = self.env.user.institute_id.welcome_msg or "Welcome to {}".format(self.env.user.institute_id.name or "CristO")
                
#                 Renewal Members data
                renewals = []
                deadline_date = datetime.today() + timedelta(30)
                renewal_data = self.env['member.statutory.renewals'].search([('member_id.institute_id','=',self.env.user.institute_id.id),('valid_to','>=',datetime.today()),('valid_to','<=',deadline_date)])
                for i, dt in enumerate(renewal_data):
                    if dt.valid_to:
                        renewals.append({'sno':i+1,'member':dt.member_id.member_name,'doc_type':dt.document_type_id.name,'valid_to':dt.valid_to.strftime("%d-%b-%Y")})
                
                if self.env.user.institute_id.institute_type in ['priest','lay_brother','brother']:
                    data.update({'view_holyorder':1})

#                Feast Dates
                query = """select name, (to_char(((to_char(now(),'yyyy')||'-'||month||'-'||day)::date),'ddd')::int-to_char(now(),'ddd')::int+365)%365 as dif,
                            trim(to_char(((to_char(now(),'yyyy')||'-'||month||'-'||day)::date), 'dd - Month')) as day
                                from res_important_date where type = 'feast_date' and institute_id = {0} and type='feast_date' order by dif""".format(
                                    self.env.user.institute_id.id)
                self.env.cr.execute(query)
                feast_dates = self.env.cr.dictfetchall()

#            Store My Profile Action for Navigation
                action_id = self.env.ref('cristo.action_religious_institute').id or ''
                menu_id = self.env.ref('cristo.organization_main_menu').id or ''
                goto_my_profile = ('res.religious.institute','Congregation',self.env.user.institute_id.id,str(action_id),str(menu_id))
                data.update({'ri':1,'total_pro':total_pro,'provinces':pro_results,'goto_my_profile':goto_my_profile,'total_com':total_com,'communities':com_results,'school_count':school_count,'college_count':college_count,'parish_count':parish_count,'boarding_co':boarding_co,'format_co':format_co,'health_co':health_co,'retreat_co':retreat_co,'technical_co':technical_co,'tot_insti':total_insti,'members':mem[0],'tot_members':mem[1],'slider_ids':image_ids,'default_img': 1 if not image_ids else 0,'sl_msg':msg,'renewals':renewals if renewals else 0,'feast_dates':feast_dates if feast_dates else 0})
            elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
                province = 1
                bday_param = 'AND prov = %d' % (self.env.user.rel_province_id.id)
                ann_param = 'AND rm.rel_province_id = %d' % (self.env.user.rel_province_id.id)
#               House/Community
                com = self.get_communities(self.env.user.rel_province_id)
                
#               Institution
                ins_category = self.institution_category()
                school_count = self.env['res.institution'].search_count([('rel_province_id','=',self.env.user.rel_province_id.id),('ministry_category_id','in',ins_category[0].ids)])
                college_count = self.env['res.institution'].search_count([('rel_province_id','=',self.env.user.rel_province_id.id),('ministry_category_id','in',ins_category[1].ids)])
                parish_count = self.env['res.institution'].search_count(['|',('ministry_category_id','in',ins_category[2].ids),('category_type_id','in',ins_category[2].ids),('rel_province_id','=',self.env.user.rel_province_id.id)])
                boarding_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[3].ids)])
                format_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[4].ids)])
                health_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[5].ids)])
                retreat_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[6].ids)])
                technical_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[7].ids)])
                total_insti = self.env['res.institution'].search_count([('rel_province_id','=',self.env.user.rel_province_id.id)])

#               Confreres
                mem_domain += ['|', ('id', '=', self.env.user.member_id.id), ('rel_province_id','=',self.env.user.rel_province_id.id),('membership_type','=','RE')]
                mem = self.member_type_count(mem_domain)
                
#               Slider
                image_ids = self.env['org.image'].search([('rel_province_id','=',self.env.user.rel_province_id.id),('video_url','=',False)]).ids
                msg = self.env.user.rel_province_id.welcome_msg or "Welcome to {}".format(self.env.user.rel_province_id.name or "CristO")
                
#               Renewal Members data
                renewals = []
                sno = 0
                deadline_date = datetime.today() + timedelta(30)
                renewal_data = self.env['member.statutory.renewals'].search([('member_id.rel_province_id','=',self.env.user.rel_province_id.id),('valid_to','>=',datetime.today()),('valid_to','<=',deadline_date)])
                org_renewal = self.env['res.renewals'].search([('rel_province_id', '=', self.env.user.rel_province_id.id),('valid_to', '>=', datetime.today()),('valid_to', '<=', deadline_date)])
                for i, dt in enumerate(renewal_data):
                    if dt.valid_to:
                        renewals.append({'sno':sno+1,'member':dt.member_id.member_name,'doc_type':dt.document_type_id.name,'valid_to':dt.valid_to.strftime("%d-%b-%Y")})
                        sno += 1
                for i, dt in enumerate(org_renewal):
                    name = '-'
                    if dt.institution_id:
                        name = dt.institution_id.name
                    elif dt.community_id:
                        name = dt.community_id.name
                    elif dt.rel_province_id:
                        name = dt.rel_province_id.name
                    if dt.valid_to:
                        renewals.append({'sno':sno+1,'member':name,'doc_type':dt.document_type_id.name,'valid_to':dt.valid_to.strftime("%d-%b-%Y")})
                        sno += 1
                if self.env.user.institute_id.institute_type in ['priest','lay_brother','brother']:
                    data.update({'view_holyorder':1})

                #               Feast Dates
                query = """select name,(to_char(((to_char(now(),'yyyy')||'-'||month||'-'||day)::date),'ddd')::int-to_char(now(),'ddd')::int+365)%365 as dif,
                            trim(to_char(((to_char(now(),'yyyy')||'-'||month||'-'||day)::date), 'dd - Month')) as day
                            from res_important_date where type = 'feast_date' and rel_province_id = {0} and type='feast_date' order by dif""".format(
                            self.env.user.rel_province_id.id)
                self.env.cr.execute(query)
                feast_dates = self.env.cr.dictfetchall()

#            Store My Profile Action for Navigation
                action_id = self.env.ref('cristo.action_religious_province').id or ''
                menu_id = self.env.ref('cristo.organization_main_menu').id or ''
                goto_my_profile = ('res.religious.province','Province',self.env.user.rel_province_id.id,str(action_id),str(menu_id))
                data.update({'rp':province,'total_com':com[1],'communities':com[0],'goto_my_profile':goto_my_profile,'school_count':school_count,'college_count':college_count,'parish_count':parish_count,'boarding_co':boarding_co,'format_co':format_co,'health_co':health_co,'retreat_co':retreat_co,'technical_co':technical_co,'tot_insti':total_insti,'members':mem[0],'tot_members':mem[1],'slider_ids':image_ids,'default_img': 1 if not image_ids else 0,'sl_msg':msg,'renewals':renewals if renewals else 0,'feast_dates':feast_dates if feast_dates else 0})
            elif self.user_has_groups('cristo.group_role_cristo_religious_house'):
                house = 1
                bday_param = 'AND prov = %d' % (self.env.user.rel_province_id.id)
                ann_param = 'AND rm.rel_province_id = %d' % (self.env.user.rel_province_id.id)
#               House/Community  
                com = self.get_communities(self.env.user.rel_province_id)
                
#               Institution
                ins_category = self.institution_category()
                school_count = self.env['res.institution'].search_count([('community_id','=',self.env.user.community_id.id),('ministry_category_id','in',ins_category[0].ids)])
                college_count = self.env['res.institution'].search_count([('community_id','=',self.env.user.community_id.id),('ministry_category_id','in',ins_category[1].ids)])
                parish_count = self.env['res.institution'].search_count(['|',('ministry_category_id','in',ins_category[2].ids),('category_type_id','in',ins_category[2].ids),('rel_province_id','=',self.env.user.rel_province_id.id)])
                boarding_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[3].ids)])
                format_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[4].ids)])
                health_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[5].ids)])
                retreat_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[6].ids)])
                technical_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[7].ids)])
                total_insti = self.env['res.institution'].search_count([('community_id','=',self.env.user.community_id.id)])

#               Confreres
                mem_domain += ['|',('id', '=', self.env.user.member_id.id),('community_id','=',self.env.user.community_id.id),('membership_type','=','RE')]
                mem = self.member_type_count(mem_domain)
#               Slider
                image_ids = self.env['org.image'].search([('house_id','=',self.env.user.community_id.id),('video_url','=',False)]).ids
                msg = self.env.user.community_id.welcome_msg or "Welcome to {}".format(self.env.user.community_id.name or "CristO")
                
#                 Renewal Members data
                renewals = []
                sno = 0
                deadline_date = datetime.today() + timedelta(30)
                renewal_data = self.env['member.statutory.renewals'].search([('member_id.community_id','=',self.env.user.community_id.id),('valid_to','>=',datetime.today()),('valid_to','<=',deadline_date)])
                org_renewal = self.env['res.renewals'].search([('community_id','=',self.env.user.community_id.id),('valid_to','>=',datetime.today()),('valid_to','<=',deadline_date)])
                for i, dt in enumerate(renewal_data):
                    if dt.valid_to:
                        renewals.append({'sno':sno+1,'member':dt.member_id.member_name,'doc_type':dt.document_type_id.name,'valid_to':dt.valid_to.strftime("%d-%b-%Y")})
                        sno += 1
                for i, dt in enumerate(org_renewal):
                    name = '-'
                    if dt.community_id:
                        name = dt.community_id.name
                    elif dt.rel_province_id:
                        name = dt.rel_province_id.name
                    if dt.valid_to:
                        renewals.append({'sno':sno+1,'member':name,'doc_type':dt.document_type_id.name,'valid_to':dt.valid_to.strftime("%d-%b-%Y")})
                        sno += 1
                if self.env.user.institute_id.institute_type in ['priest','lay_brother','brother']:
                    data.update({'view_holyorder':1})
                #               Feast Dates
                query = """select name,(to_char(((to_char(now(),'yyyy')||'-'||month||'-'||day)::date),'ddd')::int-to_char(now(),'ddd')::int+365)%365 as dif,
                                trim(to_char(((to_char(now(),'yyyy')||'-'||month||'-'||day)::date), 'dd - Month')) as day
                                from res_important_date where type = 'feast_date' and community_id = {0} and type='feast_date' order by dif""".format(
                    self.env.user.community_id.id)
                self.env.cr.execute(query)
                feast_dates = self.env.cr.dictfetchall()

#            Store My Profile Action for Navigation
                action_id = self.env.ref('cristo.action_religious_community').id or ''
                menu_id = self.env.ref('cristo.organization_main_menu').id or ''
                goto_my_profile = ('res.community','House/Community',self.env.user.community_id.id,str(action_id),str(menu_id))
                data.update({'rh':house,'total_com':com[1],'communities':com[0],'goto_my_profile':goto_my_profile,'school_count':school_count,'college_count':college_count,'parish_count':parish_count,'boarding_co':boarding_co,'format_co':format_co,'health_co':health_co,'retreat_co':retreat_co,'technical_co':technical_co,'tot_insti':total_insti,'members':mem[0],'tot_members':mem[1],'slider_ids':image_ids,'default_img': 1 if not image_ids else 0,'sl_msg':msg,'renewals':renewals if renewals else 0,'feast_dates':feast_dates if feast_dates else 0})
            elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
                bday_param = 'AND prov = %d' % (self.env.user.rel_province_id.id)
                ann_param = 'AND rm.rel_province_id = %d' % (self.env.user.rel_province_id.id)
#               Institution
                ins_category = self.institution_category()
                school_count = self.env['res.institution'].search_count([('community_id','=',self.env.user.community_id.id),('ministry_category_id','in',ins_category[0].ids)])
                college_count = self.env['res.institution'].search_count([('community_id','=',self.env.user.community_id.id),('ministry_category_id','in',ins_category[1].ids)])
                parish_count = self.env['res.institution'].search_count(['|',('ministry_category_id','in',ins_category[2].ids),('category_type_id','in',ins_category[2].ids),('rel_province_id','=',self.env.user.rel_province_id.id)])
                boarding_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[3].ids)])
                format_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[4].ids)])
                health_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[5].ids)])
                retreat_co =  self.env['res.institution'].search_count([('institution_category_id','in',ins_category[6].ids)])
                technical_co =  self.env['res.institution'].search_count([('ministry_category_id','in',ins_category[7].ids)])
                total_insti = self.env['res.institution'].search_count([('community_id','=',self.env.user.community_id.id)])

#               Confreres
                mem_domain += ['|', ('id', '=', self.env.user.member_id.id),('community_id','=',self.env.user.institution_id.community_id.id),('membership_type','=','RE')]
                mem = self.member_type_count(mem_domain)

#               Slider
                image_ids = self.env['org.image'].search([('institution_id','=',self.env.user.institution_id.id),('video_url','=',False)]).ids
                msg = self.env.user.institution_id.welcome_msg or "Welcome to {}".format(self.env.user.institution_id.name or 'CristO')
                
#                 Renewal Members data
                renewals = []
                sno = 0
                deadline_date = datetime.today() + timedelta(30)
                renewal_data = self.env['member.statutory.renewals'].search([('member_id.community_id','=',self.env.user.institution_id.community_id.id),('valid_to','>=',datetime.today()),('valid_to','<=',deadline_date)])
                org_renewal = self.env['res.renewals'].search([('institution_id', '=', self.env.user.institution_id.id),('valid_to', '>=', datetime.today()),('valid_to', '<=', deadline_date)])
                for i, dt in enumerate(renewal_data):
                    if dt.valid_to:
                        renewals.append({'sno':sno+1,'member':dt.member_id.member_name,'doc_type':dt.document_type_id.name,'valid_to':dt.valid_to.strftime("%d-%b-%Y")})
                        sno += 1
                for i, dt in enumerate(org_renewal):
                    if dt.valid_to:
                        renewals.append({'sno':sno+1,'member':'My Institution','doc_type':dt.document_type_id.name,'valid_to':dt.valid_to.strftime("%d-%b-%Y")})
                        sno += 1
                if self.env.user.institute_id.institute_type in ['priest','lay_brother','brother']:
                    data.update({'view_holyorder':1})
#            Store My Profile Action for Navigation
                action_id = self.env.ref('cristo.action_institution').id or ''
                menu_id = self.env.ref('cristo.organization_main_menu').id or ''
                goto_my_profile = ('res.institution','Institution',self.env.user.institution_id.id,str(action_id),str(menu_id))
                data.update({'ra':1,'school_count':school_count,'college_count':college_count,'goto_my_profile':goto_my_profile,'parish_count':parish_count,'boarding_co':boarding_co,'format_co':format_co,'health_co':health_co,'retreat_co':retreat_co,'technical_co':technical_co,'tot_insti':total_insti,'members':mem[0],'tot_members':mem[1],'slider_ids':image_ids,'default_img': 1 if not image_ids else 0,'sl_msg':msg,'renewals':renewals if renewals else 0,'feast_dates':0})
            elif self.user_has_groups('cristo.group_role_cristo_individual'):
                bday_param = 'AND prov = %d' % (self.env.user.rel_province_id.id)
                ann_param = 'AND rm.rel_province_id = %d' % (self.env.user.rel_province_id.id)
                
#           Slider
                image_ids = self.env['org.image'].search([('house_id','=',self.env.user.community_id.id),('video_url','=',False)]).ids
                msg = self.env.user.community_id.welcome_msg or "Welcome to {}".format(self.env.user.community_id.name or "CristO")
                
#           Ordination Day
                if self.env.user.institute_id.institute_type in ['priest','lay_brother','brother']:
                    data.update({'view_holyorder':1})
                    
#           Renewal Members data               
                renewals = []
                deadline_date = datetime.today() + timedelta(30)
                renewal_data = self.env['member.statutory.renewals'].search([('valid_to','>=',datetime.today()),('valid_to','<=',deadline_date)])
                for i, dt in enumerate(renewal_data):
                    if dt.valid_to:
                        renewals.append({'sno':i+1,'member':dt.member_id.member_name,'doc_type':dt.document_type_id.name,'valid_to':dt.valid_to.strftime("%d-%b-%Y")})
                
#           Store My Profile Action for Navigation
                goto_my_profile = ('res.member','Member',self.env.user.member_id.id)
                
                data.update({'member':1,'slider_ids':image_ids,'default_img': 1 if not image_ids else 0,'sl_msg':msg,'renewals':renewals if renewals else 0,'goto_my_profile':goto_my_profile,'feast_dates':0})
            else:
                data.update({'valid_user':0})
                member[0].update(data)
                return member
            
#           Birthdays
            birthdays_results = self.get_birthday_list(bday_param)
            for bd in birthdays_results:
                bd['img_data'] = self.get_image_data(bd['partner_id'])
            anniversay_result = self.get_anniversary_list(ann_param)
            for an in anniversay_result:
                an['img_data'] = self.get_image_data(an['partner_id'])
                ho_id = self.env['res.holyorder'].sudo().browse(an['id'])
                an['order'] = dict(ho_id._fields['order'].selection).get(ho_id.order)

            cong_act_id = self.env.ref("cristo.action_religious_institute").id
            prov_act_id = self.env.ref("cristo.action_religious_province").id
            com_act_id = self.env.ref("cristo.action_religious_community").id
            ins_act_id = self.env.ref("cristo.action_institution").id
            mem_act_id = self.env.ref("cristo.action_all_member").id
            ins_menu_id = self.env.ref("cristo.organization_main_menu").id
            mem_menu_id = self.env.ref("cristo.members_main_menu").id
            
            data.update({'birthdays':birthdays_results or 0,'anniversary':anniversay_result or 0,'today':datetime.today().strftime("%d - %B")})
            member[0].update({'institute_id':user.institute_id.id,'rel_province_id':user.rel_province_id.id,'house_id':user.community_id.id,'institution_id':user.institution_id.id,'navigation':[str(cong_act_id),str(prov_act_id),str(com_act_id),str(ins_act_id),str(mem_act_id),str(ins_menu_id),str(mem_menu_id)]})
            member[0].update(data)
            return member
        else:
            return False
        
# This is For REST API 

    def api_get_birthday_details(self,args):
        bday_param = 'AND prov = %d' % (int(args) or 0)
        birthday_list = self.get_birthday_list(bday_param)
        for bd in birthday_list:
            del bd['dob']
            del bd['total_days']
            del bd['dif']
            del bd['cong']
            del bd['prov']
        return birthday_list
    
    def api_get_ordination_details(self,args):
        ann_param = 'AND rm.rel_province_id = %d' % (int(args) or [])
        anniversay_result = self.get_anniversary_list(ann_param)
        for oa in anniversay_result:
            del oa['date']
            del oa['days']
        return anniversay_result
