# Copyright (c) 2026, Beveren Software and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def check_app_permission():
	return frappe.session.user != "Guest"

