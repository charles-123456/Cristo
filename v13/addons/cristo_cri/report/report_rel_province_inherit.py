from odoo import models, fields, api, _

class ReportReligiousProvinceProfileInherit(models.AbstractModel):
    _inherit = 'report.cristo.report_rel_province_profile'

    def get_province_spread_countries(self, province_id):
        if province_id.house_ids:
            countries = province_id.house_ids.country_id.mapped('name')
            spread_country = ', '.join(countries)
            return spread_country

    def get_province_spread_states(self, province_id):
        if province_id.house_ids:
            states = province_id.house_ids.state_id.mapped('name')
            spread_state = ', '.join(states)
            return spread_state

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super(ReportReligiousProvinceProfileInherit, self)._get_report_values(docids, data=None)
        res['get_province_spread_countries'] = self.get_province_spread_countries
        res['get_province_spread_states'] = self.get_province_spread_states
        return res