# -*- coding: utf-8 -*-
# from odoo import http


# class EximBellona(http.Controller):
#     @http.route('/exim_bellona/exim_bellona/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/exim_bellona/exim_bellona/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('exim_bellona.listing', {
#             'root': '/exim_bellona/exim_bellona',
#             'objects': http.request.env['exim_bellona.exim_bellona'].search([]),
#         })

#     @http.route('/exim_bellona/exim_bellona/objects/<model("exim_bellona.exim_bellona"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('exim_bellona.object', {
#             'object': obj
#         })
