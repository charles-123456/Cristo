odoo.define('custom_filters.CustomGroupByMenu', function (require) {
"use strict";

var GroupByMenu = require('web.GroupByMenu');

var CustomGroupBy = GroupByMenu.include({
	
//	This function is overridden to pass the model model name to the start function
    init: function (parent, groupBys, fields, options) {
    	this._super.apply(this, arguments);
		this.groupby_model = parent.action.res_model;
    },
    
//	This function is used to provide the necessary custom group by fields from the every Model.
    start: function () {
    	var self = this;
    	if (this.groupby_model != undefined) {
			var def = this._rpc({
	            model: this.groupby_model,
	            method: 'get_custom_filter_fields',
	            args: [[]],
	        }).then(function (result) {
	        	self.presentedFields = self.presentedFields.filter(function (field) {
	        		return !_.contains(result['exclude_fields'], field.name)
		        });
	        	
	        	if( ! result['is_all'] ){
	        		self.presentedFields = self.presentedFields.filter(function (field) {
	            		return _.contains(result.view_fields, field.name)
	    	        });
	        	}
	        });
			return $.when(def, this._super());
    	} else {
			return $.when(this._super());
		}
    },

});

return CustomGroupBy;

});
