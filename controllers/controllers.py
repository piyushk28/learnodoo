# -*- coding: utf-8 -*-
from flectra import http

# class Recycle(http.Controller):
#     @http.route('/recycle/recycle/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/recycle/recycle/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('recycle.listing', {
#             'root': '/recycle/recycle',
#             'objects': http.request.env['recycle.recycle'].search([]),
#         })

#     @http.route('/recycle/recycle/objects/<model("recycle.recycle"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('recycle.object', {
#             'object': obj
#         })