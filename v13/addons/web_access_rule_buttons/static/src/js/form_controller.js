/* Copyright 2016 Camptocamp SA
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("web_access_rule_buttons.main", function (require) {
    "use strict";
    var FormController = require("web.FormController");
    FormController.include({

        _update: function (state) {
            return this._super(state).then(this.show_hide_buttons(state));
        },
        /*renderSidebar: function ($node) {
            var self = this;
            this._super();
            alert("newly called");
        },*/
        show_hide_buttons : function (state) {
            var self = this;
            return self._rpc({
                model: this.modelName,
                method: 'check_access_rule_all',
                args: [[state.data.id], ["write"]],
            }).then(function (accesses) {
                self.show_hide_edit_button(accesses.write);
                /*self.show_hide_create_button(accesses.create);*/
            });
        },
        show_hide_edit_button : function (access) {
            if (this.$buttons) {
                var edit_button = this.$buttons.find(".o_form_button_edit");
                if (edit_button && access == true) {
                	edit_button.show();
                }else{
                	edit_button.hide();
                }
            }
        },
        /*show_hide_create_button : function (access) {
            if (this.$buttons) {
                var create_button = this.$buttons.find(".o_form_button_create");
                if (create_button && access == true) {
                	create_button.show();
                }else{
                	create_button.hide();
                }
            }
        },*/
    });
});
