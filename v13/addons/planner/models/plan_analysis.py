# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectPlanInherit(models.Model):
    _inherit = "project.plan"
    
    def generate_plan_analysis(self):
        return{
            'name': 'Plan Analysis',
            'type': 'ir.actions.client',
            'tag': 'plan_analysis_view',
            'target': 'main'
        }
        
    @api.model
    def get_plan_analysis_details(self,plan_id):
        user = self.env.user
        plan_details = self.env['project.plan'].search_read([('id','=',plan_id)],fields=['id','name','category_id','section1','section2','section3','section4'],limit=1)
        plan_id = self.env['project.plan'].browse(plan_id)
        activity_labels = [('yet to start','Yet to Start'),('inprogress','In-progress'),('completed','Completed')]
        if plan_id.section1 == 'yes':
            sec1_main = []
            sec1_set = []
            sec1_labels = []
            sec1_config_name = self.env['plan.section.config'].search([('section_type','=','section 1'),('user_ids','=',user.id)]).name or 'Section 1'
            sec1_ids = self.env['plan.section1'].search([('plan_id','=',plan_id.id)])
            for sec1 in sec1_ids:
                sec1_labels.append(sec1.name)
            for lbl in activity_labels:
                dt_set = []
                for sec1_id in sec1_ids:
                    tot = 0
                    activities = self.env['plan.activity'].search_count([('plan_id', '=', plan_id.id),('status','=',lbl[0]),('section1_id','=',sec1_id.id)])
                    dt_set.append(activities)
                sec1_set.append({'label':lbl[1],'data_set':dt_set})
            sec1_main.append({'labels':sec1_labels,'overall':sec1_set})
            plan_details[0].update({'sec1_data':sec1_main,'sec1_name':sec1_config_name})
        
        temp_overall_percent = {}
        op_all_p = []
        
        act_data = []
        tot_per = 0
        for lbl in activity_labels:
            activities = self.env['plan.activity'].search_count([('plan_id', '=', plan_id.id),('status','=',lbl[0])])
            act_data.append({'state':lbl[1],'state_count':activities})
            tot_per += activities
            temp_overall_percent.update({lbl[1]:activities})
        
        for i in temp_overall_percent:
            divid_by = str(int((temp_overall_percent[i] / tot_per) * 100)) if tot_per != 0 else 0
            if divid_by != 0:
                op_all_p.append(("{0} {1}% - ({2})".format(i,divid_by,temp_overall_percent[i]),"{0}%".format(divid_by)))
            else:
                op_all_p.append(('0','0'))
        
        plan_details[0].update({'act_data':act_data,'yts_lbl':op_all_p[0][0],'yts':op_all_p[0][1],'inp_lbl':op_all_p[1][0],'inp':op_all_p[1][1],'cmp_lbl':op_all_p[2][0],'cmp':op_all_p[2][1]})
        return plan_details
    
    