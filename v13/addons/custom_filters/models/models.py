# -*- coding: utf-8 -*-
from odoo import models, api, _

class CustomBase(models.AbstractModel):
    _inherit = "base"
    _custom_filter_view_fields = '__all__'
    _custom_filter_exclude_fields = []
    _custom_filter_extra_kwargs = {}
    
    
    def custom_filter_exclude(self):
        ''' This function is used to exclude the given fields in the Control panel custom filters.
            And added the built-in fields such as 'write_uid', 'create_uid', 'create_date', 'write_date'
        '''
        exclude_field = self._custom_filter_exclude_fields
        return exclude_field
    
    def custom_filter_extra_kwargs(self):
        ''' This function is used to show the field name with the customized field's string name passed from the Model as a Dictionary 
            and shows in under 'Add Custom Filter'
        '''
        return self._custom_filter_extra_kwargs
    
    def  custom_filter_view_fields(self):
        ''' This function is used to view the model fields in the Control panel custom filters. Necessary fields are passed from the respective model with class variable
        '''
        return self._custom_filter_view_fields
        
    def get_custom_filter_fields(self):
        '''This function is used to call from the javascript to get the necessary fields to show/hide against a Model.
        '''
        custom_filter_view_fields = self.custom_filter_view_fields()
        custom_filter_extra_kwargs = self.custom_filter_extra_kwargs()
        is_all = type(custom_filter_view_fields) == str and custom_filter_view_fields == '__all__' 
        view_fields = type(custom_filter_view_fields) == list and custom_filter_view_fields + list(custom_filter_extra_kwargs.keys())
        return {
            'is_all': is_all,
            'view_fields': view_fields,
            'exclude_fields': self.custom_filter_exclude(),
            'extra_kwargs': custom_filter_extra_kwargs
        }