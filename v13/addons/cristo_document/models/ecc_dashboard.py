# -*- coding: utf-8 -*-
from odoo import models, api, _


class EcclesiaMember(models.Model):
    _inherit = 'res.member'

    @api.model
    def get_diocese_parish_details(self):
        res = super(EcclesiaMember, self).get_diocese_parish_details()
        if self.user_has_groups('muk_dms.group_dms_user') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            files_count = self.env['muk_dms.file'].search_count([])
            if self.user_has_groups('cristo.group_role_cristo_diocese'):
                files_count = self.env['muk_dms.file'].search_count(
                    ['|',('shared_ids', '=', self.env.user.partner_id.id), ('diocese_id', '=', self.env.user.diocese_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_vicarate'):
                files_count = self.env['muk_dms.file'].search_count(
                    ['|',('shared_ids', '=', self.env.user.partner_id.id), ('vicariate_id', '=', self.env.user.vicariate_id.id)])
            elif self.user_has_groups('cristo.group_role_cristo_parish_ms'):
                files_count = self.env['muk_dms.file'].search_count(
                    ['|',('shared_ids', '=', self.env.user.partner_id.id), ('parish_id', '=', self.env.user.parish_id.id)])
            res[0].update({'files': 1, 'files_count': files_count})
        return res