odoo.define('cristo_chronicle.DocumentDashboard', function (require) {
"use strict";

var session = require('web.session');
var core = require('web.core');
var _t = core._t;
var Dashboard = require('cristo_dashboard.Dashboard');

Dashboard.include({
	events: _.extend({}, Dashboard.prototype.events, {
		'click .cr_document':'open_cr_document',
    }),
    
    open_cr_document: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        //this.do_action('muk_dms.action_dms_file');
        var url = window.location.origin+'/web#action='+self.login_member['doc_action_id']+'&model=muk_dms.file&view_type=tree&cids=1&menu_id='+self.login_member['doc_menu_id'];
        window.location = url;
    },
});

});
