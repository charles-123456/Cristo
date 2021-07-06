odoo.define('cristo_circular.CircularDashboard', function (require) {
"use strict";

var session = require('web.session');
var core = require('web.core');
var _t = core._t;
var Dashboard = require('cristo_dashboard.Dashboard');

Dashboard.include({
	events: _.extend({}, Dashboard.prototype.events, {
		'click .cr_circular':'open_cr_circular',
    }),
    
    open_cr_circular: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
       // this.do_action('cristo_circular.action_circular');
       var url = window.location.origin+'/web#action='+self.login_member['cir_action_id']+'&model=cristo.circular&view_type=tree&cids=1&menu_id='+self.login_member['cir_menu_id'];
       window.location = url;
    },
});

});