odoo.define('custom_filters.CustomFilterMenu', function (require) {
"use strict";

var FilterMenu = require('web.FilterMenu');

var CustomFilter = FilterMenu.include({
	
//	This function is overridden to pass the model model name to the start function
	init: function (parent, filters, fields) {
		this._super.apply(this, arguments)
		this.filter_model = parent.action.res_model;
	},

//	This function is used to provide the necessary custom filter fields from the every Model.	
	start: function () {
		var self = this;
		if (this.filter_model != undefined) {
			var def = this._rpc({
	            model: this.filter_model,
	            method: 'get_custom_filter_fields',
	            args: [[]],
	        }).then(function (result) {
	        	result['exclude_fields'].map(field => {
	        		if (field in self.fields){
	        			delete self.fields[field]
	        		}
	        	})
	        	Object.keys(result.extra_kwargs).map(field => {
	        		if (field in self.fields){
	        			self.fields[field] = {...self.fields[field], string: result.extra_kwargs[field]['string'] }
	        		}
	        	})
	        	
	        	if( ! result['is_all'] ){
	                var fields = {};
	                result.view_fields.map(field => {
	    	        	if (field in self.fields){
	    	        		fields[field] = self.fields[field]
	    	        	}
	    	        });
	    	        self.fields = fields;
	        	} 
	        	
	        });
			return $.when(def, this._super());
		} else {
			return $.when(this._super());
		}
    },
});

return CustomFilter;

});
