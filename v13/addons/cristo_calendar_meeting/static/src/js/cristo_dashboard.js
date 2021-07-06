odoo.define('cristo_calendar_meeting.CMDashboard', function (require) {
"use strict";

var session = require('web.session');
var core = require('web.core');
var _t = core._t;
var Dashboard = require('cristo_dashboard.Dashboard');

Dashboard.include({
	events: _.extend({}, Dashboard.prototype.events, {
		'click .cr_calendar':'open_cr_calendar',
		'click .cr_meeting':'open_cr_meeting',
    }),
    
    open_cr_calendar: function(e){
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
       // this.do_action('cristo_calendar_meeting.action_calendar');
        var url = window.location.origin+'/web#action='+self.login_member['cal_action_id']+'&model=calendar.event&view_type=tree&cids=1&menu_id='+self.login_member['cal_menu_id'];
        window.location = url;
    },
    open_cr_meeting: function(e){
    	var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
    //	this.do_action('cristo_calendar_meeting.action_meeting');
        var url = window.location.origin+'/web#action='+self.login_member['met_action_id']+'&model=calendar.event&view_type=tree&cids=1&menu_id='+self.login_member['met_menu_id'];
        window.location = url;
    },
});

});
