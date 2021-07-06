# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Member(models.Model):
    _inherit = 'res.member'

    def get_ecclesia_news_format(self, news_ids):
        news = '  <i class="fa fa-asterisk" style="font-size:16px"></i>  '.join(
            news_ids.mapped('name'))
        return news

    @api.model
    def get_diocese_parish_details(self):
        res = super(Member, self).get_diocese_parish_details()
        rec = []
        news_ids = False
        if self.user_has_groups('cristo.group_role_cristo_diocese'):
            news_ids = self.env['res.news'].search(
                [('diocese_id', '=', self.env.user.diocese_id.id), ('state', '=', 'publish')], order='sequence')
            if news_ids:
                rec.append(self.get_ecclesia_news_format(news_ids))
            else:
                rec.append(" Greetings!!! Welcome to CristO.")
            
        elif self.user_has_groups('cristo.group_role_cristo_parish_ms'):
            news_ids = self.env['res.news'].search([('parish_id','=',self.env.user.parish_id.id),('state','=','publish')], order='sequence')
            if news_ids:
                rec.append(self.get_ecclesia_news_format(news_ids))
            else:
                rec.append(" Greetings!!! Welcome to CristO.")
        else:
            rec.append(" Greetings!!! Welcome to CristO.")
            
        res[0].update({'news_lines': rec})
        return res
