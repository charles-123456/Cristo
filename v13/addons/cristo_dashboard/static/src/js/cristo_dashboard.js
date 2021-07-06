odoo.define('cristo_dashboard.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var framework = require('web.framework');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var CristoDashboard = AbstractAction.extend({
    template: 'CristoDashboardMain',
    cssLibs: [
         '/cristo_dashboard/static/src/css/lib/nv.d3.css'
	],
	jsLibs: [
	    '/cristo_dashboard/static/src/js/lib/d3.min.js'
	],
    events: {
    	'click .cr_congregation':'cr_congregation',
    	'click .cr_province':'cr_province',
    	'click .cr_house':'cr_house',
    	'click .cr_institution':'cr_institution',
    	'click .cr_conferer':'cr_conferer',
    	'click .goto_my_profile':'goto_my_profile'
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['LoginMemberDetails'];
//        console.log("INIT FUNCTION 1")
    },

    willStart: function() {
//        console.log("WILLSTART FUNCTION")
        var self = this;
        return self.fetch_data();
    },

    start: function() {
//        console.log("START FUNCTION")
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            self.update_cp();
            self.render_dashboards();
            self.render_graphs();
            self.$el.parent().addClass('oe_background_grey');
        });
    },

    fetch_data: function() {
//        console.log("FETCH_DATE FUNCTION")
        var self = this;
        var def1 =  this._rpc({
                model: 'res.member',
                method: 'get_user_member_details'
        }).then(function(result) {
            console.log(result[0])
            self.login_member =  result[0];
        });
        var def2 =  this._rpc({
            model: 'res.member',
            method: 'get_member_statistics'
        }).then(function(data) {
        	self.mem_statistics = data;
        });
        return $.when(def1,def2);
    },

    render_dashboards: function() {
//    	console.log("RENDER_DASHBOARD")
        var self = this;
        if (this.login_member['valid_user']){
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_dashboard').append(QWeb.render(template, {widget: self}));
            });
            }
        else{
            self.$('.o_dashboard').append(QWeb.render('MemberWarning', {widget: self}));
            }
    },
    
    render_graphs: function(){
//    	console.log("RENDER_GRAPHS")
        var self = this;
        if (this.login_member['valid_user']) {
            self.render_member_statistics();
        }
    },
    on_reverse_breadcrumb: function() {
//    	console.log("ON_REVERSE_BREADCRUMB")
        var self = this;
        web_client.do_push_state({});
        this.update_cp();
        this.fetch_data().then(function() {
            self.$('.o_dashboard').empty();
            self.render_dashboards();
            self.render_graphs();
        });
    },

    update_cp: function() {
        var self = this;
//        console.log("UPDATE_CP")
//        this.update_control_panel(
//            {breadcrumbs: self.breadcrumbs}, {clear: true}
//        );
    },
    cr_congregation: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        /*this.do_action({
            name: _t("Congregation"),
            type: 'ir.actions.act_window',
            res_model: 'res.religious.institute',
            view_mode: 'tree,form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current'
        }, options)*/
        var url = window.location.origin+'/web#&action='+self.login_member['navigation'][0]+'&model=res.congregation&view_type=tree&cids=1&menu_id='+self.login_member['navigation'][5];
        window.location = url;
    },
    cr_province: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        /*this.do_action({
            name: _t("Province"),
            type: 'ir.actions.act_window',
            res_model: 'res.religious.province',
            view_mode: 'tree,form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current'
        }, options)*/
        var url = window.location.origin+'/web#&action='+self.login_member['navigation'][1]+'&model=res.religious.province&view_type=tree&cids=1&menu_id='+self.login_member['navigation'][5];
        window.location = url;
    },
    cr_house: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        /*this.do_action({
            name: _t("House/Community"),
            type: 'ir.actions.act_window',
            res_model: 'res.community',
            view_mode: 'tree,form,search',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            context: {'search_default_rel_province_id': self.login_member['rel_province_id'],}
        }, options)*/
        var url = window.location.origin+'/web#&action='+self.login_member['navigation'][2]+'&model=res.community&view_type=tree&cids=1&menu_id='+self.login_member['navigation'][5];
        window.location = url;
    },
    cr_institution: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        /*this.do_action({
            name: _t("Institution"),
            type: 'ir.actions.act_window',
            res_model: 'res.institution',
            view_mode: 'tree,form',
            views: [[false, 'list'],[false, 'form']],
            context: {
            	 'search_default_rel_province_id': self.login_member['rel_province_id'],
            },
            target: 'current',
        }, options)*/
        var url = window.location.origin+'/web#&action='+self.login_member['navigation'][3]+'&model=res.institution&view_type=tree&cids=1&menu_id='+self.login_member['navigation'][5];
        window.location = url;
    },
    cr_conferer: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        /*var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };*/
        var url = window.location.origin+'/web#&action='+self.login_member['navigation'][4]+'&model=res.member&view_type=tree&cids=1&menu_id='+self.login_member['navigation'][6];
        window.location = url;
//        this.do_action('cristo.action_all_member');
    },
    goto_my_profile: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        /*var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };*/
        var model = '';
        var action_id = '';
        var menu_id = '';
        if (self.login_member['ri']){
        	model = 'res.religious.institute';
        	action_id = self.login_member['goto_my_profile'][3];
        	menu_id = self.login_member['goto_my_profile'][4];
        }else if (self.login_member['rp']){
        	model = 'res.religious.province';
        	action_id = self.login_member['goto_my_profile'][3];
        	menu_id = self.login_member['goto_my_profile'][4];
        }else if (self.login_member['rh']){
        	model = 'res.community';
        	action_id = self.login_member['goto_my_profile'][3];
        	menu_id = self.login_member['goto_my_profile'][4];
        }else if (self.login_member['ra']){
        	model = 'res.institution';
        	action_id = self.login_member['goto_my_profile'][3];
        	menu_id = self.login_member['goto_my_profile'][4];
        }
        if (self.login_member['goto_my_profile']) {
        	var url = window.location.origin+'/web#id='+self.login_member['goto_my_profile'][2]+'&action='+action_id+'&model='+model+'&view_type=form&cids=1&menu_id='+menu_id;
        	framework.redirect(url);
    		/*this.do_action({
                name: _t(self.login_member['goto_my_profile'][1]),
                type: 'ir.actions.act_window',
                res_model: self.login_member['goto_my_profile'][0],
                view_mode: 'form',
                views: [[false, 'tree'],[false, 'form']],
                res_id:self.login_member['goto_my_profile'][2],
                context: {},
                target: 'current',
            }, options);*/
        }else{
        	return false;
        }
    },
    get_member_image_url: function(member){
        return window.location.origin + '/web/image?model=res.partner&field=image_1920&id='+member;
    },
    get_slider_image_url: function(id){
        return window.location.origin + '/web/image?model=org.image&field=image_1920&id='+id;
    },
    render_member_statistics: function(){
    	var self = this;
    	if (!this.login_member['member']) {
    		var donutChartCanvas = this.$('#donutChart').get(0).getContext('2d');
            var donutData        = {
              labels: self.mem_statistics['labels'],
              datasets: [
                {
                  data: self.mem_statistics['values'],
                  backgroundColor : ['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc','#d2d6de','#f31286'],
                }
              ]
            }
        	var donutOptions     = {
        	      maintainAspectRatio : false,
        	      responsive : true,
        	    }
            //Create pie or douhnut chart
            // You can switch between pie and douhnut using the method below.
        	var donutChart = new Chart(donutChartCanvas, {
    	      type: 'doughnut',
    	      data: donutData,
    	      options: donutOptions      
    	    });
    	}
    }
        
});


core.action_registry.add('cristo_dashboard', CristoDashboard);

return CristoDashboard;

});