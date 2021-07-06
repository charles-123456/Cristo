odoo.define('debranding.public_crash_manager', function (require) {
"use strict";

const core = require('web.core');
const CrashManager = require('web.CrashManager').CrashManager;

const PublicCrashManager = CrashManager.extend({

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _displayWarning(message, title, options) {
    	var title = "Session Expired";
    	var message = "Your session expired. Please refresh the current web page.";
        this.displayNotification(Object.assign({}, options, {
            title,
            message,
            sticky: true,
        }));
    },
});

core.serviceRegistry.add('crash_manager', PublicCrashManager);

return {
    CrashManager: PublicCrashManager,
};

});
