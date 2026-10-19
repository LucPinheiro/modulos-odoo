from odoo import http
from odoo.http import request


class TmsPortal(http.Controller):

    @http.route(["/my/tms/trips"], type="http", auth="user", website=True)
    def my_tms_trips(self, **kw):
        partner = request.env.user.partner_id
        trips = request.env["tms.trip"].sudo().search([
            ("driver_id", "=", partner.id),
            ("state", "in", ["assigned", "in_transit", "delivered"]),
        ], order="planned_start desc")
        return request.render("tms.portal_my_trips", {"trips": trips})

    @http.route(["/my/tms/trip/<int:trip_id>/start"], type="http", auth="user", website=True)
    def trip_start(self, trip_id, **kw):
        trip = request.env["tms.trip"].sudo().browse(trip_id)
        if trip.exists() and trip.driver_id.id == request.env.user.partner_id.id:
            trip.action_start()
        return request.redirect("/my/tms/trips")

    @http.route(["/my/tms/trip/<int:trip_id>/deliver"], type="http", auth="user", website=True)
    def trip_deliver(self, trip_id, **kw):
        trip = request.env["tms.trip"].sudo().browse(trip_id)
        if trip.exists() and trip.driver_id.id == request.env.user.partner_id.id:
            trip.action_deliver()
        return request.redirect("/my/tms/trips")
