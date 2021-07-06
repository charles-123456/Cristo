odoo.define('cristo_chronicle.ChDashboard', function (require) {
"use strict";

var session = require('web.session');
var core = require('web.core');
var _t = core._t;
var Dashboard = require('cristo_dashboard.Dashboard');

Dashboard.include({
	events: _.extend({}, Dashboard.prototype.events, {
		'click .cr_chronicle':'cr_chronicle',
		'click .other_cr_chronicle':'other_cr_chronicle',
    }),
    
    cr_chronicle: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        /*this.do_action('calendar.action_calendar_event', {
            additional_context: {
                default_mode: 'day',
                search_default_mymeetings: 1,
            }
        });*/
        //this.do_action('cristo_chronicle.action_my_chronicle');
        var url = window.location.origin+'/web#action='+self.login_member['mychr_action_id']+'&model=cristo.chronicle&view_type=tree&cids=1&menu_id='+self.login_member['chr_menu_id'];
        window.location = url;
    },
    other_cr_chronicle: function(e){
    	var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
    	//this.do_action('cristo_chronicle.action_other_chronicle');
    	var url = window.location.origin+'/web#action='+self.login_member['chr_action_id']+'&model=cristo.chronicle&view_type=tree&cids=1&menu_id='+self.login_member['chr_menu_id'];
        window.location = url;
    },
});

});
