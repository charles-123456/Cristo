odoo.define('cristo_calendar_meeting.EcclesiaDocumentDashboard', function (require) {
"use strict";

var session = require('web.session');
var core = require('web.core');
var _t = core._t;
var Dashboard = require('cristo_ecclesia_dashboard.Dashboard');

Dashboard.include({
	events: _.extend({}, Dashboard.prototype.events, {
		'click .open_calendar':'open_ecc_calendar',
		'click .open_meeting':'open_ecc_meeting',
    }),

    open_ecc_calendar: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action('cristo_calendar_meeting.action_calendar');
    },
    open_ecc_meeting: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action('cristo_calendar_meeting.action_meeting');
    },
});

});
