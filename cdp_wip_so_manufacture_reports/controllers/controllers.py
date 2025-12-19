# -*- coding: utf-8 -*-
# from odoo import http


# class CdpWipSoManufactureReports(http.Controller):
#     @http.route('/cdp_wip_so_manufacture_reports/cdp_wip_so_manufacture_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cdp_wip_so_manufacture_reports/cdp_wip_so_manufacture_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cdp_wip_so_manufacture_reports.listing', {
#             'root': '/cdp_wip_so_manufacture_reports/cdp_wip_so_manufacture_reports',
#             'objects': http.request.env['cdp_wip_so_manufacture_reports.cdp_wip_so_manufacture_reports'].search([]),
#         })

#     @http.route('/cdp_wip_so_manufacture_reports/cdp_wip_so_manufacture_reports/objects/<model("cdp_wip_so_manufacture_reports.cdp_wip_so_manufacture_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cdp_wip_so_manufacture_reports.object', {
#             'object': obj
#         })

