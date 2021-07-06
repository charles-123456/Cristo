# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Member(models.Model):
    _inherit = 'res.member'

    def get_news_format(self,news_ids):
        news_list=[]
        for news in news_ids:
            news_list.append((news.id,news.name,news.description))
        return news_list

    @api.model
    def get_user_member_details(self):
        res = super(Member, self).get_user_member_details()
        rec = []
        total_news= 0
        #Navigation
        news_action_id = self.env.ref("cristo_news.action_news_report").id
        news_menu_id = self.env.ref("cristo.organization_main_menu").id
        res[0].update({'news_action_id' : str(news_action_id),'news_menu_id' : str(news_menu_id)})

        news_ids = False
        if self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            rec = ['Greetings!!! Welcome to CristO.']
            ls_id = ['#']
            rec = list(zip(ls_id, rec))
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') :
            news_ids = self.env['res.news'].search(
                [('institute_id', '=', self.env.user.institute_id.id), ('state', '=', 'publish')], order='sequence')
            total_news = len(news_ids)
            if news_ids :
                rec = (self.get_news_format(news_ids))
            else :
                rec = ['Greetings!!! Welcome to CristO.']
                ls_id = ['#']
                rec = list(zip(ls_id, rec))
        elif self.user_has_groups('cristo.group_role_cristo_religious_province'):
            news_ids = self.env['res.news'].search(
                [('rel_province_id', '=', self.env.user.rel_province_id.id), ('state', '=', 'publish')], order='sequence')
            total_news = len(news_ids)
            if news_ids :
                rec = self.get_news_format(news_ids)
            else :
                rec = ['Greetings!!! Welcome to CristO.']
                ls_id = ['#']
                rec = list(zip(ls_id, rec))
        elif self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_individual') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            pro_news_ids = self.env['res.news'].search(
                [('rel_province_id', '=', self.env.user.community_id.rel_province_id.id), ('state', '=', 'publish'),
                 ('is_house', '=', True)], order='sequence')
            news_ids = self.env['res.news'].search(
                [('community_id', '=', self.env.user.community_id.id), ('state', '=', 'publish')], order='sequence')
            total_news = len(news_ids)
            res[0].update({'is_frm_prov' : 0})
            if pro_news_ids :
                res[0].update({'province_news' : self.get_news_format(pro_news_ids), 'is_frm_prov' : 1})
            if news_ids :

                rec = self.get_news_format(news_ids)
            else :
                rec = ['Greetings!!! Welcome to CristO.']
                ls_id = ["#"]
                rec = list(zip(ls_id, rec))
        res[0].update({'news_content': rec, 'total_news': total_news})
        return res
