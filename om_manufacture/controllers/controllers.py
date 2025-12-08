# -*- coding: utf-8 -*-
# from odoo import http


# class OmManufacture(http.Controller):
#     @http.route('/om_manufacture/om_manufacture', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/om_manufacture/om_manufacture/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('om_manufacture.listing', {
#             'root': '/om_manufacture/om_manufacture',
#             'objects': http.request.env['om_manufacture.om_manufacture'].search([]),
#         })

#     @http.route('/om_manufacture/om_manufacture/objects/<model("om_manufacture.om_manufacture"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('om_manufacture.object', {
#             'object': obj
#         })

