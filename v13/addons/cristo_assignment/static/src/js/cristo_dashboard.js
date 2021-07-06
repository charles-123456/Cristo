odoo.define('cristo_assignment.AssignmentDashboard', function (require) {
"use strict";

var session = require('web.session');
var core = require('web.core');
var framework = require('web.framework');
var _t = core._t;
var Dashboard = require('cristo_dashboard.Dashboard');

Dashboard.include({
	events: _.extend({}, Dashboard.prototype.events, {
		'click .cr_transfer':'open_cr_transfer',
		'click .cr_request':'open_cr_request',
    }),
    open_cr_transfer: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        var url = window.location.origin+'/web#action='+self.login_member['transfer_action_id']+'&model=member.assignment&view_type=tree&cids=1&menu_id='+self.login_member['transfer_menu_id'];
        window.location = url;
     //   this.do_action('cristo_assignment.action_assignment');
    },
    open_cr_request: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        var url = window.location.origin+'/web#action='+self.login_member['request_action_id']+'&model=member.assignment.request&view_type=tree&cids=1&menu_id='+self.login_member['transfer_menu_id'];
        window.location = url;
     //   this.do_action('cristo_assignment.action_assignment_request');
    },
});

});