odoo.define('cristo_users.UserNotification', function (require) {
"use strict";

var session = require('web.session');
var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;
var Dashboard = require('cristo_dashboard.Dashboard');

Dashboard.include({
	init: function(parent, context) {
        this._super(parent, context);
        var self = this;
        this._rpc({
            model: "user.license.expiry",
            method: "get_license_notification",
        }).then(function (data) {
        	self.license = data
        });
	}
});

});
