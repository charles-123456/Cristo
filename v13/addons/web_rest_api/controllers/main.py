import re
import uuid
import base64
import json
# import jwt
import pytz
import ast
import traceback
import logging

import odoo
from odoo import api, http, release, tools
from odoo.http import Controller, Response, request, route
from datetime import datetime
from werkzeug import exceptions
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils

#----------------------------------------------------------
# General
#----------------------------------------------------------

def _get_db():
    databases = http.db_list()
    db = False
    if databases:
        db = databases[0]
    return db

def _get_last_login(uid):
    last_login = False
    tz = request.env['res.users'].sudo().search([('id','=',uid)]).tz
    if tz:
        last_login = datetime.now(pytz.timezone(tz)).astimezone(pytz.utc)
    else:
        last_login = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    return last_login

def _check_token():
    try:
        http_authorization = request.httprequest.environ['HTTP_AUTHORIZATION']
    except:
        result = {
            'status': 'error',
            'code': 400,
            'message': 'The request failed because it contained an invalid value. The value could be a parameter value, a header value, or a property value.',
        }
        exceptions.abort(Response(json.dumps(result), content_type='application/json;charset=utf-8', status=401))
    access_token_prefix, access_token = http_authorization[:7], http_authorization[7:]
    if access_token_prefix.strip().lower() == 'bearer':
        token_id = request.env['res.user.token'].sudo().search([('access_token','=', access_token)], limit=1)
        if token_id:
            uid = token_id.user_id.id or False
            request._uid = uid
            request.session.context.update({'access_token':access_token})
            request._env = api.Environment(request.cr, uid, request.session.context or {})
#             token_id.write({'last_request':_get_last_login(uid)})
            ICPSudo = request.env['ir.config_parameter'].sudo()
            traceability = ICPSudo.get_param('hgp_base.api_access_history', False)
#             if traceability == '1.0':
#                 request.env['rest.api.access.history'].sudo().create({'user_id':uid,'origin':request.httprequest.environ['REMOTE_ADDR'],'api_path':request.context.get('api_path',False),'access_token':access_token,'accessed_on':_get_last_login(uid)})
        else:
            result = {
                'status': 'error',
                'code': 401,
                'message': 'The user is not authorized to make the request.',
            }
            exceptions.abort(Response(json.dumps(result), content_type='application/json;charset=utf-8', status=401))
    else:
        result = {
            'status': 'error',
            'code': 400,
            'message': 'The request failed because it contained an invalid value. The value could be a parameter value, a header value, or a property value.',
        }
        exceptions.abort(Response(json.dumps(result), content_type='application/json;charset=utf-8', status=401))
        
def _get_data(data):
    if data and isinstance(data, list):
        for val in data:
            if isinstance(val, dict):
                for v in list(val):
                    if isinstance(val[v], bytes):
                        val[v] = val[v].decode('utf-8')
    return data

def _get_data_read(data,bool_fields,float_fields,many2one_fields,many2many_fields):
    if data and isinstance(data, list):
        for val in data:
            if isinstance(val, dict):
                for v in list(val):
                    if isinstance(val[v], bytes):
                        val[v] = val[v].decode('utf-8')
                    if not v in bool_fields and val[v] == False:
                        val[v] = ''
                    if v in bool_fields:
                        val[v] = 'Yes' if val[v] == True else 'No'
                    if v in float_fields and val[v] != '':
                        val[v] = round(val[v])
                    if v in many2one_fields and val[v] == '':
                        val[v] = []
                    if v in many2many_fields and val[v] == '':
                        val[v] = []
    return data

def _get_relation_data(data,many2many_fields,relation_model):
    if data and isinstance(data, list):
        for val in data:
            if isinstance(val, dict):
                for v in list(val):
                    if v in many2many_fields:
                        m2m_ids = request.env[relation_model[many2many_fields.index(v)]].browse(val[v])
                        x = []
                        for m in m2m_ids:
                            x.append({'id':m.id,'name':m.display_name})
                        val[v] = x
    return data

#----------------------------------------------------------
# Rest Controller
#----------------------------------------------------------
    
class RestController(http.Controller):
    
    @http.route('/api', auth="none", type='http')
    def api_version(self, **kw):    
        result = {
            'server_version': release.version,
            'server_version_info': release.version_info,
            'server_serie': release.serie,
            'api_version': 2,
        }
        return Response(json.dumps(result), content_type='application/json;charset=utf-8', status=200)
    
#     @http.route('/api/login', type='http', auth="none", methods=['GET','POST'], csrf=False)
#     def api_login(self, debug=False, **kw):
#         result = {}; status = False
#         db = _get_db()
#         username = kw.get('username', False)
#         password = kw.get('password', False)
#         uid = request.session.authenticate(db, username, password)
#         if uid:
#             role_name = request.env['base64.imageurl'].user_role()
#             access_token = str(uuid.uuid4())
#             result.update({
#                 'status': 'success',
#                 'code': 200,
#                 'message': 'OK',
#                 'data':{
#                     'uid': uid,
#                     'user': role_name,
#                     'access_token': str(access_token),
#                 }
#             })
#             status = 200
#             request.env['res.user.token'].sudo().create({'user_id':uid, 'access_token':access_token})#, 'last_request':_get_last_login(uid)
#         else:
#             result.update({
#                 'status': 'error',
#                 'code': 401,
#                 'message': 'The authorization credentials provided for the request are invalid. Check the value of the Authorization HTTP request header.',
#             })
#             status = 401
#         return Response(json.dumps(result), content_type='application/json;charset=utf-8', status=200)
#         
#     @http.route('/api/logout', type='http', auth="none", methods=['GET'], csrf=False)
#     def api_logout(self, debug=False, **kw):
#         result = {}; status = False
#         _check_token()
#         access_token = request.session.context.get('access_token', False)
#         token_id = request.env['res.user.token'].sudo().search([('access_token', '=', access_token)], limit=1)
#         if token_id and token_id.sudo().unlink():
#             result.update({
#                 'status': 'success',
#                 'code': 200,
#                 'message': 'You have been successfully logged out!',
#             })
#             status = 200
#         else:
#             result.update({
#                 'status': 'error',
#                 'code': 400,
#                 'message': 'The request failed because it contained an invalid value. The value could be a parameter value, a header value, or a property value.',
#             })
#             status = 400
#         return Response(json.dumps(result), content_type='application/json;charset=utf-8', status=status)
#         
    @http.route([
        '/api/search/<string:model>',
        '/api/search/<string:model>/<int:id>',
        '/api/search/<string:model>/<int:id>/<int:limit>',
        '/api/search/<string:model>/<int:id>/<int:limit>/<int:offset>'], auth="none", type='http', methods=['GET'], csrf=False)
    def api_search(self, model=None, id=None, limit=25, offset=0, **kw):
        ctx = dict(request.context)
        api_path="/api/search/%s/%s/%s/%s"%(model,id,limit,offset)
        ctx.update({'api_path':api_path })
        request.context = ctx
        _check_token()
        result = {}; status = False
        order = kw.get('order', None)
        count = kw.get('count', 0)
        domain = ast.literal_eval(kw.get('domain', [])) if kw.get('domain', []) else []
        context = ast.literal_eval(kw.get('context', {})) if kw.get('context', {}) else {}
        try:
            if id:
                domain += [('id','=',id)]
            data = request.env[model].with_context(context).search(domain, offset=int(offset), limit=int(limit), order=order, count=int(count)).ids or []
            result.update({
                'status': 'success',
                'code': 200,
                'message': 'OK',
                'data': data
            })
            status = 200
        except Exception as error:
            logging.error(traceback.format_exc())
            result.update({
                'status': 'error',
                'code': 403,
                'message': 'Sorry, you are not allowed to access this document.',
                #'message': traceback.format_exc(),
                
            })
            status = 403
        return Response(json.dumps(result), content_type='application/json;charset=utf-8', status=status)
    
    @http.route([
        '/api/search_read/<string:model>',
        '/api/search_read/<string:model>/<int:id>',
        '/api/search_read/<string:model>/<int:id>/<int:limit>',
        '/api/search_read/<string:model>/<int:id>/<int:limit>/<int:offset>'], auth="none", type='http', methods=['GET'], csrf=False)
    def api_search_read(self, model=None, id=None, limit=25, offset=0, **kw):
        ctx = dict(request.context)
        api_path="/api/search_read/%s/%s/%s/%s"%(model,id,limit,offset)
        ctx.update({'api_path':api_path })
        request.context = ctx
        _check_token()
        result = {}; status = False
        order = kw.get('order', None)
        domain = ast.literal_eval(kw.get('domain', [])) if kw.get('domain', []) else []
        fields = ast.literal_eval(kw.get('fields', [])) if kw.get('fields', []) else []
        context = ast.literal_eval(kw.get('context', {})) if kw.get('context', {}) else {}
        bool_fields = []
        float_fields = []
        many2one_fields = []
        many2many_fields = []
        relation_model = []
        ir_model_obj=request.env['ir.model.fields']
        for field in fields:
            ir_model_field=ir_model_obj.search([('model','=',model),('name','=',field)])
            field_type=ir_model_field.ttype
            if field_type=='boolean':
                bool_fields.append(field)
            if field_type=='float':
                float_fields.append(field)
            if field_type=='many2one':
                many2one_fields.append(field)
            if field_type=='many2many':
                relation_field = ir_model_field.relation
                many2many_fields.append(field)
                relation_model.append(relation_field)
        try:
            if id:
                domain += [('id','=',id)]
            data = request.env[model].with_context(context).search_read(domain, fields=fields, offset=int(offset), order=order) or []
            data = _get_data_read(data,bool_fields,float_fields,many2one_fields,many2many_fields)
            data = _get_relation_data(data,many2many_fields,relation_model)
            if data:
                for i in range(len(data)):
                    for key, value in data[i].items():
                        if key in ["image_256","image_512","image_1024","image_1920","image_128","pan_proof","passport_proof","voter_proof","aadhar_proof","content","img"]:
                            image_url = request.env['base64.imageurl'].base64_url(value)
                            data[i].update({key:image_url})
#                         if key in ["position_ids"]:
#                             role_of_position = request.env['res.community'].api_get_community_position(value)
#                             data[i].update({key:role_of_position})
#                         if key in ["ministry_ids"]:
#                             ministry = request.env['res.community'].api_get_ministry(value)
#                             data[i].update({key:ministry})
#                         if key in ["parish_id"]:
#                             if value == "":
#                                 data[i].update({key:[]})
                        if value == False:
                            data[i].update({key:''})
            result.update({
                'status': 'success',
                'code': 200,
                'message': 'OK',
                'count': request.env[model].search_count([]),
                'data': data
            })
            status = 200
        except Exception as error:
            logging.error(traceback.format_exc())
            result.update({
                'status': 'error',
                'code': 403,
                'message': 'Sorry, you are not allowed to access this document.',
                #'message': traceback.format_exc(),
            })
            status = 403
        return Response(json.dumps(result,default=date_utils.json_default), content_type='application/json;charset=utf-8;', status=status)
    
    @http.route('/api/search_count/<string:model>', auth="none", type='http', methods=['GET'], csrf=False)
    def api_search_count(self, model=None, **kw):
        ctx = dict(request.context)
        api_path="/api/search_count/%s/"%(model)
        ctx.update({'api_path':api_path })
        request.context = ctx
        _check_token()
        result = {}; status = False
        domain = ast.literal_eval(kw.get('domain', [])) if kw.get('domain', []) else []
        context = ast.literal_eval(kw.get('context', {})) if kw.get('context', {}) else {}
        try:
            data = request.env[model].with_context(context).search_count(domain) 
            data = _get_data(data)
            result.update({
                'status': 'success',
                'code': 200,
                'message': 'OK',
                'data': {'count': data}
            })
            status = 200
        except Exception as error:
            logging.error(traceback.format_exc())
            result.update({
                'status': 'error',
                'code': 400,
                'message': 'The request failed because it contained an invalid value. The value could be a parameter value, a header value, or a property value.',
                #'message': traceback.format_exc(),
            })
            status = 403
        return Response(json.dumps(result), content_type='application/json;charset=utf-8;', status=status)
    
    @http.route('/api/create/<string:model>', auth="none", type='http', methods=['POST'], csrf=False)
    def api_create(self, model=False, **kw):
        _check_token()
        result = {}; status = False
        values = ast.literal_eval(kw.get('values', {})) if kw.get('values', {}) else {}
        context = ast.literal_eval(kw.get('context', {})) if kw.get('context', {}) else {}
        try:
            if values:
                data = request.env[model].with_context(context).create(values)
                result.update({
                    'status': 'success',
                    'code': 303,
                    'message': 'Your request was processed successfully.',
                    'data': {'id': data.id or False}
                })
                status = 200
            else:
                logging.error(traceback.format_exc())
                result.update({
                    'status': 'error',
                    'code': 400,
                    'message': 'The API request is missing required information. The required information could be a parameter or resource property.',
                    #'message': traceback.format_exc(),
                })
                status = 400
        except ValidationError as e:
            result.update({
                'status': 'error',
                'code': 400,
                'message': e.args[0],
            })
        except UserError as e:
            result.update ({
                'status': 'error',
                'code': 400,
                'message': e.name,
                    })
            status = 400
        except Exception as error:
            logging.error(traceback.format_exc())
            result.update({
                'status': 'error',
                'code': 400,
                'message': 'The request failed because it contained an invalid value. The value could be a parameter value, a header value, or a property value.',
                #'message': traceback.format_exc(),
            })
            status = 400
        return Response(json.dumps(result), content_type='application/json;charset=utf-8;', status=status)
    
    @http.route('/api/write/<string:model>', auth="none", type='http', methods=['PUT'], csrf=False)
    def api_write(self, model=False, **kw):
        _check_token()
        result = {}; status = False
        ids = ast.literal_eval(kw.get('ids', [])) if kw.get('ids', []) else []
        values = ast.literal_eval(kw.get('values', {})) if kw.get('values', {}) else {}
        context = ast.literal_eval(kw.get('context', {})) if kw.get('context', {}) else {}
        try:
            if ids and values:
                records = request.env[model].with_context(context).search([('id','in', ids)])
                if records:
                    data = records.write(values)
                    result.update({
                        'status': 'success',
                        'code': 303,
                        'message': 'Your request was processed successfully.',
                        'data': data,
                    })
                    status = 200
                else:
                    
                    logging.error(traceback.format_exc())
                    result.update({
                        'status': 'error',
                        'code': 404,
                        'message': 'The requested operation failed because a resource associated with the request could not be found.',
                        #'message': traceback.format_exc(),
                    })
                    status = 404
            else:
                logging.error(traceback.format_exc())
                result.update({
                    'status': 'error',
                    'code': 400,
                    'message': 'The API request is missing required information. The required information could be a parameter or resource property.',
                    #'message': traceback.format_exc(),
                })
                status = 400
                
        except Exception as error:
            logging.error(traceback.format_exc())
            result.update({
                'status': 'error',
                'code': 400,
                'message': 'The request failed because it contained an invalid value. The value could be a parameter value, a header value, or a property value.',
                #'message': traceback.format_exc(),
            })
            status = 400
        return Response(json.dumps(result), content_type='application/json;charset=utf-8;', status=status)
    
    @http.route('/api/unlink/<string:model>', auth="none", type='http', methods=['DELETE'], csrf=False)
    def api_unlink(self, model=None, **kw):
        _check_token()
        result = {}; status = False
        ids = ast.literal_eval(kw.get('ids', [])) if kw.get('ids', []) else []
        context = ast.literal_eval(kw.get('context', {})) if kw.get('context', {}) else {}
        try:
            records = request.env[model].with_context(context).search([('id','in', ids)])
            if records:
                data = records.unlink()
                result.update({
                    'status': 'success',
                    'code': 303,
                    'message': 'Your request was processed successfully.',
                    'data': data,
                })
                status = 200
            else:
                logging.error(traceback.format_exc())
                result.update({
                    'status': 'error',
                    'code': 404,
                    'message': 'The requested operation failed because a resource associated with the request could not be found.',
                    #'message': traceback.format_exc(),
                })
                status = 404
        except Exception as error:
            logging.error(traceback.format_exc())
            result.update({
                'status': 'error',
                'code': 410,
                'message': 'The request failed because the resource associated with the request has not been deleted.',
                #'message': traceback.format_exc(),
            })
            status = 410
        return Response(json.dumps(result), content_type='application/json;charset=utf-8;', status=status)
    
    @http.route('/api/call/<string:model>/<string:method>', auth="none", type='http', methods=['GET'], csrf=False)
    def api_call(self, model=False, method=None, context=None, **kw):
        _check_token()
        result = {}; status = False; api_call = False
        args = ast.literal_eval(kw.get('args', [])) if kw.get('args', []) else []
        context = ast.literal_eval(kw.get('context', {})) if kw.get('context', {}) else {}
        try:
            if args:
                api_call = "request.env['{}'].with_context({}).{}{}".format(model,context,method,tuple(args))
            else:
                api_call = "request.env['{}'].with_context({}).{}()".format(model,context,method)
            data = eval(api_call)
            result.update({
                'status': 'success',
                'code': 303,
                'message': 'Your request was processed successfully.',
                'data': data,
            })
            status = 200
        except Exception as error:
            logging.error(traceback.format_exc())
            result.update({
                'status': 'error',
                'code': 400,
                'message': 'The API request is missing required information. The required information could be a parameter or resource property.',
                #'message': traceback.format_exc(),
            })
            status = 400
        return Response(json.dumps(result), content_type='application/json;charset=utf-8;', status=status)
    
    @http.route('/api/report/<string:model>/<string:report>', auth="none", type='http', methods=['GET'], csrf=False)
    def api_report(self, model=False, report=False, **kw):
        _check_token()
        result = {}; status = False; api_call = False
        ids = ast.literal_eval(kw.get('ids', [])) if kw.get('ids', []) else []
        type = kw.get('type', 'pdf')
        context = ast.literal_eval(kw.get('context', {})) if kw.get('context', {}) else {}
        try:
            if ids:
                if type == "html":
                    data = request.env.ref(report).render_qweb_html(ids)[0]
                    headers = [
                        ('Content-Type', 'text/html'),
                        ('Content-Length', len(data)),
                    ]
                    return request.make_response(data, headers=headers)
                else:
                    data = request.env.ref(report).render_qweb_pdf(ids)[0]
                    headers = [
                        ('Content-Type', 'application/pdf'),
                        ('Content-Length', len(data)),
                    ]
                    return request.make_response(data, headers=headers)
            else:
                logging.error(traceback.format_exc())
                result.update({
                    'status': 'error',
                    'code': 404,
                    'message': 'The requested operation failed because a resource associated with the request could not be found.',
                    #'message': traceback.format_exc(),
                })
                status = 404
        except Exception as error:
            logging.error(traceback.format_exc())
            result.update({
                'status': 'error',
                'code': 400,
                'message': 'The API request is missing required information. The required information could be a parameter or resource property.',
                #'message': traceback.format_exc(),
            })
            status = 400
        return Response(json.dumps(result), content_type='application/json;charset=utf-8;', status=status)
