# Copyright (c) 2026, Beveren Software and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, get_system_timezone

no_cache = 1


def get_context():
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	context = frappe._dict()
	context.boot = get_boot()
	return context


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
	return get_boot()


def get_boot():
	user = frappe.session.user
	user_doc = frappe.get_doc("User", user) if user != "Guest" else None
	csrf_token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""

	return frappe._dict({
		"frappe_version": frappe.__version__,
		"default_route": "/projects",
		"site_name": frappe.local.site,
		"csrf_token": csrf_token,
		"session_user": user,
		"user_info": {
			"email": user,
			"full_name": user_doc.full_name if user_doc else user,
			"user_image": user_doc.user_image if user_doc else None,
		},
		"timezone": {
			"system": get_system_timezone(),
			"user": frappe.db.get_value("User", user, "time_zone") or get_system_timezone(),
		},
	})
