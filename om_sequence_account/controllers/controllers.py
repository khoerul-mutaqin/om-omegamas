# -*- coding: utf-8 -*-
# from odoo import http


# class OmSequenceAccount(http.Controller):
#     @http.route('/om_sequence_account/om_sequence_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/om_sequence_account/om_sequence_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('om_sequence_account.listing', {
#             'root': '/om_sequence_account/om_sequence_account',
#             'objects': http.request.env['om_sequence_account.om_sequence_account'].search([]),
#         })

#     @http.route('/om_sequence_account/om_sequence_account/objects/<model("om_sequence_account.om_sequence_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('om_sequence_account.object', {
#             'object': obj
#         })

