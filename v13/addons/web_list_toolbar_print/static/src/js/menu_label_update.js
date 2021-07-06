odoo.define('cristo_concern.SidebarInherited', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;

var Sidebar = require('web.Sidebar');

Sidebar.include({
    init: function (parent, options) {

    this._super.apply(this, arguments);
    this.options = _.defaults(options || {}, {
        'editable': true
    });
    this.env = options.env;
    this.sections = options.sections || [
        {name: 'print', label: _t('Export')},
        {name: 'other', label: _t('Action')},
    ];
    this.items = options.items || {
        print: [],
        other: [],
    };
    if (options.actions) {
        this._addToolbarActions(options.actions);
    }
},

});
});