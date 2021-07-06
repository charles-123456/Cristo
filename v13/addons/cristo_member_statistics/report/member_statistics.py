# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api


class MemberStatisticsReport(models.Model):
    """ Member Statistics """
    _name = "member.statistics.report"
    _auto = False
    _description = "Member Statistics"
    _rec_name = 'id'
    
    member_type = fields.Selection([('member','Member'),('bishop','Bishop'),('priest','Priest'),('deacon','Deacon'),('lay_brother','Lay Brother'),('brother','Brother'),('sister','Sister'),('junior_sister', 'Junior Sister'),('novice','Novice')], string="Member Type", readonly=True)
    gender = fields.Selection([('male','Male'),('female','Female'),('transgender','Transgender')],string="Gender", readonly=True)
    blood_group_id = fields.Many2one('res.blood.group',string="Blood Group", readonly=True)
    mother_tongue_id = fields.Many2one('res.languages',string="Mother Tongue", readonly=True)
    member_name = fields.Char(string='Member',readonly=True)
    program_id = fields.Many2one('res.member.program',string="Program",readonly=True)
    study_level_id = fields.Many2one('res.study.level',string="Study Level",readonly=True)
    member_age = fields.Integer(string="Member Age",readonly=True)
    holyorder_name = fields.Char(string="Holy Order",readonly=True)
        
    def _select(self):
        return """
            SELECT
                m.id,
                m.member_type,
                m.gender,
                m.blood_group_id,
                m.mother_tongue_id,
                m.member_name,
                m.age as member_age,
                edu.program_id,
                edu.study_level_id,
                rho."order" as holyorder_name
        """

    def _from(self):
        return """
            FROM res_member as m
        """

    def _join(self):
        return """
            LEFT JOIN res_member_education as edu ON(edu.member_id=m.id)
            LEFT JOIN res_holyorder as rho ON(rho.member_id=m.id)
        """

    def _where(self):
        return """
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where())
        )