odoo.define('cristo_document.EcclesiaDocumentDashboard', function (require) {
"use strict";

var session = require('web.session');
var core = require('web.core');
var _t = core._t;
var Dashboard = require('cristo_ecclesia_dashboard.Dashboard');

Dashboard.include({
	events: _.extend({}, Dashboard.prototype.events, {
		'click .open_document':'open_ecc_document',
    }),

    open_ecc_document: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action('muk_dms.action_dms_file');
    },
});

});
