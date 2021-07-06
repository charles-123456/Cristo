odoo.define('cristo_news.NewsDashboard', function (require) {
"use strict";

var session = require('web.session');
var core = require('web.core');
var _t = core._t;
var Dashboard = require('cristo_dashboard.Dashboard');

Dashboard.include({
	events: _.extend({}, Dashboard.prototype.events, {
//		'click .cr_chronicle':'cr_chronicle',
//		'click .other_cr_chronicle':'other_cr_chronicle',
		'click .cr_news':'cr_news',
		'click .popup_news':'popup_news'
    }),

    popup_news: function(e){
        var self = this;
        var news = e.currentTarget.dataset;
         $("#exampleModal .modal-title").html(news.title);
         if (news.description == "false"){
            $("#exampleModal .modal-body").html("");
         }else{
            $("#exampleModal .modal-body").html(news.description);
         }
         $("#exampleModal").modal("show");
        e.stopPropagation();
        e.preventDefault();
    },

    cr_news: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        var url = window.location.origin+'/web#action='+self.login_member['news_action_id']+'&model=res.news&view_type=tree&cids=1&menu_id='+self.login_member['news_menu_id'];
        window.location = url;
    },
});

});
