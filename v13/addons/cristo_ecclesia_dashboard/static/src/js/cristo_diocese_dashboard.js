odoo.define('cristo_ecclesia_dashboard.Dashboard', function(require) {
	"use strict";

	var AbstractAction = require('web.AbstractAction');
	var ajax = require('web.ajax');
	var core = require('web.core');
	var rpc = require('web.rpc');
	var session = require('web.session');
	var web_client = require('web.web_client');
	var _t = core._t;
	var QWeb = core.qweb;

	var CristoDioceseDashboard = AbstractAction.extend({
		template : 'CristoDioceseDashboardMain',
		cssLibs : [ '/cristo_ecclesia_dashboard/static/src/css/lib/nv.d3.css' ],
		jsLibs : [ '/cristo_ecclesia_dashboard/static/src/js/lib/d3.min.js' ],
		events: {
            'click .open_family':'open_family',
            'click .open_family_members':'open_family_members',
            'click .open_baptism':'open_baptism',
            'click .open_first_holy_communion':'open_first_holy_communion',
            'click .open_confirmation':'open_confirmation',
            'click .open_marriage':'open_marriage',
            'click .open_death':'open_death',
        },
		init : function(parent, context) {
			this._super(parent, context);
			this.dashboards_templates = [ 'DioceseParishDetails' ];
			console.log("INIT FUNCTION 1")
		},
		willStart : function() {
			console.log("WILLSTART FUNCTION")
			var self = this;
			return self.fetch_data();
		},

		start : function() {
			console.log("START FUNCTION")
			var self = this;
			this.set("title", 'Dashboard');
			return this._super().then(function() {
				self.render_dashboards();
				self.$el.parent().addClass('oe_background_grey');
			});
		},
		fetch_data : function() {
			console.log("FETCH_DATE FUNCTION")
			var self = this;
			var def1 = this._rpc({
				model : 'res.member',
				method : 'get_diocese_parish_details'
			}).then(function(result) {
				self.login_member = result[0];
			});
			return $.when(def1);
		},
		render_dashboards : function() {
			console.log("RENDER_DASHBOARD")
			var self = this;
			if (this.login_member['valid_user']) {
				_.each(this.dashboards_templates, function(template) {
					self.$('.o_dashboard').append(QWeb.render(template, {
						widget : self
					}));
				});
			} else {
				self.$('.o_dashboard').append(QWeb.render('DiocesParishWarning', {
					widget : self
				}));
			}
		},
		on_reverse_breadcrumb : function() {
			console.log("ON_REVERSE_BREADCRUMB")
			var self = this;
			web_client.do_push_state({});
			this.update_cp();
			this.fetch_data().then(function() {
				self.$('.o_dashboard').empty();
				self.render_dashboards();
			});
		},
		update_cp : function() {
			var self = this;
			// console.log("UPDATE_CP")
			// this.update_control_panel(
			// {breadcrumbs: self.breadcrumbs}, {clear: true}
			// );
		},
		open_family: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action('cristo.action_res_family');
        },
        open_family_members: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action('cristo.action_res_member');
        },
        open_baptism: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action('cristo.action_baptism');
        },
        open_first_holy_communion: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action('cristo.action_first_holy_communion');
        },
        open_confirmation: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action('cristo.action_confirmation');
        },
        open_marriage: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action('cristo.action_marriage');
        },
        open_death: function(e){
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action('cristo.action_death');
        },
		    get_slider_image_url: function(id){
		        return window.location.origin + '/web/image?model=org.image&field=image_1920&id='+id;
		    },
		    
	});
	core.action_registry.add('cristo_ecclesia_dashboard', CristoDioceseDashboard);
	return CristoDioceseDashboard;

});
