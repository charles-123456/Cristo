odoo.define('cristo_directory.directory_report', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var DirectoryReports = AbstractAction.extend({
    template: 'DirectoryReportsView',
    events: {
            'click .sheet_one': 'onclick_sheet_name',
            'click .active_file':'dr_active_file_download',
            'click .file_download': 'dr_directory_file_download',
    },
    cssLibs: [
	],
	jsLibs: [
	],

    init: function(parent, action) {
        this._super(parent, action);
        this.dashboards_templates = ['DirectoryReportDetails',];
        this.result = [];
        this.value = [];
        this.sheet = [];
        this.province;
        this.directory_id = action.context.active_id || action.params.active_id;
    },

    willStart: function() {
        var self = this;
//        return $.when(ajax.loadLibs(this), this._super()).then(function() {console.log("test")
            return self.fetch_data();
//        });
    },

    start: function() {
        var self = this;
        this.set("title", 'Directory View');
        return this._super().then(function() {
            self.update_cp();
            self.render_dashboards();
//            self.$el.parent().addClass('oe_background_grey');
        });
    },

    fetch_data: function() {
        var self = this;
        var def1 =  this._rpc({
                model: 'res.directory',
                method: 'get_directory_report_details',
                args: [self.directory_id],
        }).then(function(result) {
            self.result =  result[0];
            self.province = self.result.province
        });
        return $.when(def1);
    },

    render_dashboards: function() {
        var self = this;
        if (this.result){
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_dr_dashboard').append(QWeb.render(template, {widget: self}));
            });
            }
//        else{
//            self.$('.o_hr_dashboard').append(QWeb.render('EmployeeWarning', {widget: self}));
//            }
    },

    on_reverse_breadcrumb: function() {
        var self = this;
        web_client.do_push_state({});
        this.update_cp();
        this.fetch_data().then(function() {
            self.$('.o_dr_dashboard').empty();
            self.render_dashboards();
        });
    },

    update_cp: function() {
        var self = this;
//        this._update_control_panel(
//            {breadcrumbs: self.breadcrumbs}, {clear: true}
//        );
    },

    dr_active_file_download:function(){
            var self = this
            rpc.query({
                model: "res.directory.file",
                method: "download_active_file",
                args: [self.province],
            }).then(function (url) {
                 window.location = url[0];
//                 ajax.jsonRpc('/file/download', 'call', {'url': url[0]})
                });
    },

    dr_directory_file_download:function(events){
        var file_id = $(events.target).val();
        var self = this
            rpc.query({
                model: "res.directory.file",
                method: "download_directory_file",
                args: [file_id],
            }).then(function (url) {
                 window.location = url[0];
                });
    },

    onclick_sheet_name:function(events){
        var option = $(events.target).val();
       var self = this
            rpc.query({
                model: "res.directory",
                method: "get_sheet_values",
                args: [self.directory_id, option],
            }).then(function (arrays) {
            self.name = arrays[0].name;
            self.$('.sheetview').html(QWeb.render('SheetData', {widget: arrays[0]}));
            self.previewTable();
            });
        },
       previewTable: function() {
       $('#sheet_details').DataTable( {
            dom: 'Bfrtip',
            ordering: true,
            buttons: [
                {
                    extend: 'pdf',
                    footer: 'true',
                    orientation: 'portrait',
                    title:this.name,
                    text: 'PDF',
                    exportOptions: {
                        modifier: {
                            selected: true
                        }
                    }
                },
                ],
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
            pageLength: 30,
        } );
    },
});


core.action_registry.add('directory_report_dashboard', DirectoryReports);

return DirectoryReports;

});
