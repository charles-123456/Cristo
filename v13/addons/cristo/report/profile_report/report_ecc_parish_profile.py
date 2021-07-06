import odoo
from odoo import models, fields, api
from datetime import datetime, date

class ReportEcclesiaParishProfile(models.AbstractModel):
    _name = 'report.cristo.report_ecc_parish_profiles'
    _description = "Report Ecclesia Parish"
    

    def get_parish_house_type_count(self, parish_id):
        if parish_id:
            house_type = []
            user = self.env['res.users'].browse(self._uid)
            house_type_ids = self.env['res.house.type'].search([])
            for house_type_id in house_type_ids:
                house_type_count = self.env['res.family'].search_count([('parish_id', '=', parish_id), ('house_type_id', '=', house_type_id.id), ('active_in_parish', '=', 'true')])
                house_type.append({'house_type_name' : str(house_type_id.name), 'house_type_count': str(house_type_count)})
            uncategarized_count = self.env['res.family'].search_count([('parish_id', '=', parish_id), ('house_type_id', '=', False), ('active_in_parish', '=', 'true')])
            if uncategarized_count:
                house_type.append({'house_type_name' : 'Unspecified', 'house_type_count': str(uncategarized_count)})
            return house_type
        
    def get_parish_study_status(self,parish_id):
        study_status=[]
        study_status_ids = self.env['res.study.level'].search([])
        for study_status_id in study_status_ids:
            count = self.env['res.member.education'].search_count([('member_id.parish_id', '=', parish_id), ('study_level_id', '=', study_status_id.id), ('member_id.is_parish_member', '=', 'yes'),('state','=','open')])
            study_status.append({'study_name' : study_status_id.name, 'count': count})
        return study_status
        
    def get_parish_physical_status_count(self, parish_id):
        if parish_id:
            physical_status = []
            user = self.env['res.users'].browse(self._uid)
            physical_status_ids = self.env['res.member.physical.status'].search([])
            for physical_status_id in physical_status_ids:
                physical_status_count = self.env['res.member'].search_count([('parish_id', '=', parish_id), ('physical_status_id', '=', physical_status_id.id), ('is_parish_member', '=', 'yes')])
                physical_status.append({'physical_status_name' : str(physical_status_id.name), 'physical_status_count': str(physical_status_count)})
            uncategarized_count = self.env['res.member'].search_count([('parish_id', '=', parish_id), ('physical_status_id', '=', False),('is_parish_member', '=', 'yes')])
            if uncategarized_count:
                physical_status.append({'physical_status_name' : 'Unspecified', 'physical_status_count': str(uncategarized_count)})
            return physical_status
        
    def get_parish_Blood_group_count(self, parish_id):
        if parish_id:
            Blood_group_status = []
            user = self.env['res.users'].browse(self._uid)
            Blood_group_status_ids = self.env['res.blood.group'].search([])
            for blood_group_id in Blood_group_status_ids:
                Blood_group_count = self.env['res.member'].search_count([('parish_id', '=', parish_id), ('blood_group_id', '=', blood_group_id.id), ('is_parish_member', '=', 'yes')])
                Blood_group_status.append({'Blood_group_name' : str(blood_group_id.name), 'Blood_group_count': str(Blood_group_count)})
            uncategarized_count = self.env['res.member'].search_count([('parish_id', '=', parish_id), ('blood_group_id', '=',False),('is_parish_member', '=', 'yes')])
            if uncategarized_count:
                Blood_group_status.append({'Blood_group_name' : 'Unspecified', 'Blood_group_count': str(uncategarized_count)})
            return Blood_group_status
        

    def get_parish_member_status(self, parish_id):
        if parish_id:
            member = []
            members_ids = ['LT','RE','SE']
            for members_id in members_ids:
                member_count = self.env['res.member'].search_count([('parish_id', '=', parish_id), ('membership_type', '=', members_id), ('living_status', '=', 'yes'), ('is_parish_member', '=', 'yes')])
                if members_id in 'LT':
                    membership = 'Lay Person' 
                if members_id in 'RE':
                    membership = 'Religious' 
                if members_id in 'SE':
                    membership = 'Secular Clergy' 
                member.append({'membership':membership, 'members_count':member_count})
            return member
        
        
    def get_parish_employment_status(self, parish_id):
        if parish_id:
            emp_member = []
            occupation_type = ['govt','pvt','self']
            for members_id in occupation_type:
                occupation_type_count = self.env['res.member'].search_count([('parish_id', '=', parish_id), ('occupation_type', '=', members_id), ('living_status', '=', 'yes'), ('is_parish_member', '=', 'yes')])
                if members_id in 'govt':
                    memberships = 'Government' 
                if members_id in 'pvt':
                    memberships = 'Private' 
                if members_id in 'self':
                    memberships = 'Self' 
                emp_member.append({'memberships':memberships, 'occupation_type_count':occupation_type_count})
            return emp_member
        
    def get_gender_details(self,domain):
        return self.env['res.member'].search_count(domain)
        
    def get_members_gender_count(self, parish_id):
        gtype = ['male','female','transgender']
        result = []
        for t in gtype:
            domain = [('parish_id', '=', parish_id),('gender','=',t)]
            less_5 = self.get_gender_details(domain+[('age','<',5)])
            btn_6_13 = self.get_gender_details(domain+[('age','>',6),('age','<',13)])
            btn_14_18 = self.get_gender_details(domain+[('age','>',14),('age','<',18)])
            btn_19_25 = self.get_gender_details(domain+[('age','>',19),('age','<',25)])
            btn_26_40 = self.get_gender_details(domain+[('age','>',26),('age','<',40)])
            abv_40 = self.get_gender_details(domain+[('age','>',40)])
            total = less_5 + btn_6_13 + btn_14_18 + btn_19_25 + btn_26_40 + abv_40
            result.append([t,less_5,btn_6_13,btn_14_18,btn_19_25,btn_26_40,abv_40,total])
        print(result)
        return result
   
    def get_income_details(self,domain):
        return self.env['res.member'].search_count(domain)
    
    def parish_member_incomes(self, parish_id):
        result = []
        domain = [('parish_id', '=', parish_id)]
        less_5k = self.get_income_details(domain+[('monthly_income','<',5000)])
        btn_5k_10k = self.get_income_details(domain+[('monthly_income','>',5001),('monthly_income','<',10000)])
        btn_10k_20k = self.get_income_details(domain+[('monthly_income','>',10001),('monthly_income','<',20000)])
        btn_20k_30k = self.get_income_details(domain+[('monthly_income','>',20001),('monthly_income','<',30000)])
        btn_30k_50k = self.get_income_details(domain+[('monthly_income','>',30001),('monthly_income','<',50000)])
        btn_50k_75k = self.get_income_details(domain+[('monthly_income','>',50001),('monthly_income','<',75000)])
        abv_75k = self.get_income_details(domain+[('monthly_income','>',75000)])
        total = less_5k + btn_10k_20k + btn_20k_30k + btn_30k_50k + btn_50k_75k + abv_75k
        result.append(['Income',less_5k,btn_5k_10k,btn_10k_20k,btn_20k_30k,btn_30k_50k,btn_50k_75k,abv_75k,total])
        print(result)
        return result
    
    
    
    def get_parish_register_count(self, parish_id):
        if parish_id:
            current_year = datetime.now().year + 1
            bf_year = current_year - 5
            between_year = range(bf_year, current_year)
            return between_year
        
    def get_parish_register_baptism_count(self, parish_id):
        bapt_count = []
        if parish_id:
            current_year = datetime.now().year + 1
            bf_year = current_year - 5
            between_year = range(bf_year, current_year)
            for year in between_year:
                query = "SELECT id FROM res_member WHERE parish_id = " + str(parish_id) + " AND Extract(Year from bapt_date) = " + str(year)
                self.env.cr.execute(query)
                bapt_count.append(len(self.env.cr.fetchall()))
            return bapt_count
        
    def get_parish_register_fhc_count(self, parish_id):
        fhc_count = []
        if parish_id:
            current_year = datetime.now().year + 1
            bf_year = current_year - 5
            between_year = range(bf_year, current_year)
            for year in between_year:
                query = "SELECT id FROM res_member WHERE parish_id = " + str(parish_id) + " AND Extract(Year from fhc_date) = " + str(year)
                self.env.cr.execute(query)
                fhc_count.append(len(self.env.cr.fetchall()))
            return fhc_count
            
    def get_parish_register_cnf_count(self, parish_id):
        cnf_count = []
        if parish_id:
            current_year = datetime.now().year + 1
            bf_year = current_year - 5
            between_year = range(bf_year, current_year)
            for year in between_year:
                query = "SELECT id FROM res_member WHERE parish_id = " + str(parish_id) + " AND Extract(Year from cnf_date) = " + str(year)
                self.env.cr.execute(query)
                cnf_count.append(len(self.env.cr.fetchall()))
            return cnf_count
        
    def get_parish_register_mrg_count(self, parish_id):
        mrg_count = []
        if parish_id:
            current_year = datetime.now().year + 1
            bf_year = current_year - 5
            between_year = range(bf_year, current_year)
            for year in between_year:
                query = "SELECT id FROM res_member WHERE parish_id = " + str(parish_id) + " AND Extract(Year from mrg_date) = " + str(year)
                self.env.cr.execute(query)
                mrg_count.append(len(self.env.cr.fetchall()))
            return mrg_count
        
    def get_parish_register_death_count(self, parish_id):
        death_count = []
        if parish_id:
            current_year = datetime.now().year + 1
            bf_year = current_year - 5
            between_year = range(bf_year, current_year)
            for year in between_year:
                query = "SELECT id FROM res_member WHERE parish_id = " + str(parish_id) + " AND Extract(Year from death_date) = " + str(year)
                self.env.cr.execute(query)
                death_count.append(len(self.env.cr.fetchall()))
            return death_count
        
    
    @api.model
    def _get_report_values(self, docids, data):
        docargs = {
            'doc_ids': self.id,
            'doc_model': 'res.parish',
            'docs': self.env['res.parish'].browse(docids),
            'get_parish_house_type_count': self.get_parish_house_type_count,
            'get_parish_physical_status_count':self.get_parish_physical_status_count,
            'get_parish_Blood_group_count':self.get_parish_Blood_group_count,
            'get_parish_member_status':self.get_parish_member_status,
            'get_parish_employment_status':self.get_parish_employment_status,
            'get_members_gender_count':self.get_members_gender_count,
            'parish_member_incomes':self.parish_member_incomes,
            'get_parish_study_status':self.get_parish_study_status,
            'get_parish_register_count':self.get_parish_register_count,
            'get_parish_register_baptism_count':self.get_parish_register_baptism_count,
            'get_parish_register_fhc_count':self.get_parish_register_fhc_count,
            'get_parish_register_cnf_count':self.get_parish_register_cnf_count,
            'get_parish_register_mrg_count':self.get_parish_register_mrg_count,
            'get_parish_register_death_count':self.get_parish_register_death_count,
         
        }
        return  docargs