odoo.define('siard_web_debranding.AbstractWebClient', function(require) {
	var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    
    var WebClient = require('web.AbstractWebClient');
    
    WebClient.include({
    init: function(parent, client_options) {
        this._super(parent, client_options);
        this.set('title_part', {"zopenerp": "CristO"});
    },
 }); 
    
});
