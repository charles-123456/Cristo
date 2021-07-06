import datetime
import json
import jwt
import odoo
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, \
                      serialize_exception as _serialize_exception
from datetime import datetime
import pytz

databases = http.db_list()
db = False
if databases:
    db = databases[0]

req_env = request.httprequest.environ

class UserController(http.Controller):
    
    @http.route('/api/user/get_token', type='json', auth="none", methods=['POST'], csrf=False)
    def get_token(self, debug=False, **kw):
        result = {}
        username = kw.get('username', False)
        password = kw.get('password', False)
        try:
            uid = request.session.authenticate(db, username, password)
            user_id = request.env['res.users'].sudo().search([('id', '=', uid)])
            tz = user_id.tz
            partner_id = user_id.partner_id
            if uid:
                role_name = request.env['base64.imageurl'].user_role()
                token = jwt.encode({'uid': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, 'secret', algorithm='HS256', headers={'uid': uid})
                if token:
                    result.update({'status':True,'user': role_name, 'uid':uid, 'access_token': token, 'message':'Logged in Successfully'})
                    request.env['res.user.token'].sudo().create({'user_id':uid, 'access_token':token, 'last_request':datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S") if tz else datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")})
                    request.env['rest.api.access.history'].sudo().create({'user_id':uid, 'origin':req_env['REMOTE_ADDR'], 'access_token':token, 'accessed_on':datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S") if tz else datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")})
                else:
                    result.update({'token': 'Invalid Token'})
        except:
            result.update({
                'status': 'error',
                'code': 401,
                'message': 'The authorization credentials provided for the request are invalid.',
                })
        return result
    
    @http.route('/api/user/delete_token', type='json', auth="none", methods=['GET'], csrf=False)
    def delete_token(self, debug=False, **kw):
        result = {}
        token = False
        headers = dict(request.httprequest.headers.items())
        header = headers.get('Authorization', False)
        if header:
            token = header[7:]
        else:
            result.update({'status':False, 'message':'Invalid Token'})
            return json.dumps(result)
        user_id = request.env['res.user.token'].sudo().search([('access_token', '=', token)], limit=1).user_id
        if token:
            record = request.env['res.user.token'].sudo().search([('access_token', '=', token)], limit=1)
            if record:
                request.env['rest.api.access.history'].sudo().create({'user_id':user_id.id, 'origin':req_env['REMOTE_ADDR'], 'access_token':token, 'accessed_on':datetime.now(pytz.timezone(user_id.tz)).strftime("%Y-%m-%d %H:%M:%S") if user_id.tz else datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")})
                record = record.sudo().unlink()
                result.update({'status':record, 'message':"Logged out successfully"})
            else:
                result.update({'status':False, 'message':"Record Not Found!"})
        else:
            result.update({'status':False, 'message':"Token Not Found!"})
        return result

