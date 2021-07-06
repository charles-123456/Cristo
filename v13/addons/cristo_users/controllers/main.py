import odoo
from odoo import http, tools
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.web.controllers.main import Home, ensure_db


class Home(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        super().web_login(redirect=redirect,**kw)
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            license_user = request.env['res.users'].sudo().search(
                [('login', '=', values['login']), ('expiry_date', '!=', False), ('active', '!=', True)], limit=1)
            if license_user:
                values['error'] = _("Sorry! Your License is expired.")
            else:
                old_uid = request.uid
                try:
                    uid = request.session.authenticate(request.session.db, request.params['login'],
                                                       request.params['password'])
                    request.params['login_success'] = True
                    return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                except odoo.exceptions.AccessDenied as e:
                    request.uid = old_uid
                    if e.args == odoo.exceptions.AccessDenied().args:
                        values['error'] = _("Wrong login/password")
                    else:
                        values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
