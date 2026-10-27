# Copyright (c) 2026, Beveren Software and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ImplementationModule(Document):
	def validate(self):
		if not self.module_code:
			self.module_code = frappe.scrub(self.module_name)
		else:
			self.module_code = frappe.scrub(self.module_code)

