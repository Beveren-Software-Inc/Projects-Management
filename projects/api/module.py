# Copyright (c) 2026, Beveren Software and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _


@frappe.whitelist()
def get_implementation_modules():
	"""Fetch all implementation modules and their default task templates."""
	modules = frappe.get_all(
		"Implementation Module",
		filters={"is_active": 1},
		fields=["name", "module_name", "module_code", "icon", "color", "sequence_order", "description"],
		order_by="sequence_order asc",
	)

	for m in modules:
		tasks = frappe.get_all(
			"Implementation Module Task Template",
			filters={"parent": m.name},
			fields=[
				"name",
				"subject",
				"priority",
				"is_milestone",
				"day_offset",
				"duration_days",
				"expected_hours",
				"task_weight",
				"description",
			],
			order_by="idx asc, day_offset asc",
		)
		m["tasks"] = tasks
		m["task_count"] = len(tasks)

	return modules


@frappe.whitelist()
def save_module_template(module_code, data):
	"""Update task templates for an implementation module."""
	if isinstance(data, str):
		data = json.loads(data)

	if not frappe.db.exists("Implementation Module", module_code):
		frappe.throw(_("Module not found"))

	doc = frappe.get_doc("Implementation Module", module_code)
	if "module_name" in data:
		doc.module_name = data["module_name"]
	if "color" in data:
		doc.color = data["color"]
	if "icon" in data:
		doc.icon = data["icon"]
	if "description" in data:
		doc.description = data["description"]

	if "tasks" in data:
		doc.tasks = []
		for t in data["tasks"]:
			doc.append("tasks", {
				"subject": t.get("subject"),
				"description": t.get("description") or "",
				"day_offset": t.get("day_offset", 0),
				"duration_days": t.get("duration_days", 3),
				"expected_hours": t.get("expected_hours", 8),
				"priority": t.get("priority", "Medium"),
				"is_milestone": t.get("is_milestone", 0),
				"task_weight": t.get("task_weight", 0),
			})

	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return get_implementation_modules()


@frappe.whitelist()
def create_implementation_module(module_name, module_code=None, description=None, icon=None, color=None, sequence_order=None, tasks=None):
	"""Create a new standard or custom implementation module."""
	if not module_name:
		frappe.throw(_("Module Name is required"))

	module_name = module_name.strip()
	code = frappe.scrub(module_code or module_name)

	if frappe.db.exists("Implementation Module", code):
		frappe.throw(_("A module with code '{0}' already exists").format(code))
	if frappe.db.exists("Implementation Module", {"module_name": module_name}):
		frappe.throw(_("A module with name '{0}' already exists").format(module_name))

	if not sequence_order:
		max_seq = frappe.db.sql("select max(sequence_order) from `tabImplementation Module`")[0][0] or 0
		sequence_order = int(max_seq) + 1

	doc = frappe.get_doc({
		"doctype": "Implementation Module",
		"module_name": module_name,
		"module_code": code,
		"description": description or "",
		"icon": icon or "Package",
		"color": color or "#3B82F6",
		"sequence_order": sequence_order,
		"is_active": 1,
	})

	if tasks and isinstance(tasks, str):
		tasks = json.loads(tasks)

	if tasks:
		for t in tasks:
			doc.append("tasks", {
				"subject": t.get("subject"),
				"description": t.get("description") or "",
				"day_offset": t.get("day_offset", 0),
				"duration_days": t.get("duration_days", 3),
				"expected_hours": t.get("expected_hours", 8),
				"priority": t.get("priority", "Medium"),
				"is_milestone": t.get("is_milestone", 0),
				"task_weight": t.get("task_weight", 0),
			})

	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	return get_implementation_modules()


@frappe.whitelist()
def delete_implementation_module(module_code):
	"""Delete an implementation module and its task templates."""
	if not frappe.db.exists("Implementation Module", module_code):
		frappe.throw(_("Module not found"))

	frappe.delete_doc("Implementation Module", module_code, ignore_permissions=True)
	frappe.db.commit()

	return get_implementation_modules()


