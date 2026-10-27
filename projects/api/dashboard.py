# Copyright (c) 2026, Beveren Software and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.utils import getdate, nowdate, flt, cint


@frappe.whitelist()
def get_portfolio_dashboard():
	"""Comprehensive portfolio-level metrics for All Projects Tracking Dashboard."""
	today_date = getdate(nowdate())

	# 1. Projects overview
	projects = frappe.get_all(
		"Project",
		fields=[
			"name",
			"project_name",
			"project_type",
			"status",
			"percent_complete",
			"expected_start_date",
			"expected_end_date",
			"client_poc_name",
			"client_poc_email",
			"partner_poc",
			"project_manager",
			"implementation_stage",
			"_assign",
			"_user_tags",
			"modified",
		],
		order_by="modified desc",
	)

	total_projects = len(projects)
	active_projects = sum(1 for p in projects if p.status in ("Open", "Working"))
	completed_projects = sum(1 for p in projects if p.status == "Completed")

	# Fetch tasks statistics across all projects
	all_tasks_stats = frappe.db.sql(
		"""
		SELECT
			COUNT(*) as total,
			SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
			SUM(CASE WHEN status IN ('Open', 'Working', 'Pending Review') THEN 1 ELSE 0 END) as open,
			SUM(CASE WHEN status != 'Completed' AND status != 'Cancelled' AND exp_end_date IS NOT NULL AND exp_end_date < %s THEN 1 ELSE 0 END) as overdue,
			SUM(CASE WHEN status != 'Completed' AND status != 'Cancelled' AND exp_end_date = %s THEN 1 ELSE 0 END) as due_today,
			SUM(CASE WHEN is_milestone = 1 THEN 1 ELSE 0 END) as milestones,
			SUM(CASE WHEN is_milestone = 1 AND status = 'Completed' THEN 1 ELSE 0 END) as completed_milestones
		FROM `tabTask`
		""",
		(today_date, today_date),
		as_dict=True,
	)[0]

	total_tasks = cint(all_tasks_stats.total)
	completed_tasks = cint(all_tasks_stats.completed)
	overall_completion_pct = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

	# 2. Enrich each project with module badges and completion
	for p in projects:
		modules = frappe.get_all(
			"Project Implementation Module",
			filters={"parent": p.name},
			fields=["module", "module_name", "status", "progress"],
		)
		for m in modules:
			mod_info = frappe.db.get_value("Implementation Module", m.module, ["icon", "color"], as_dict=True)
			if mod_info:
				m["icon"] = mod_info.icon
				m["color"] = mod_info.color
		p["modules"] = modules

		# Calculate project task counts
		p_stats = frappe.db.sql(
			"""
			SELECT
				COUNT(*) as total,
				SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
				SUM(CASE WHEN status != 'Completed' AND status != 'Cancelled' AND exp_end_date IS NOT NULL AND exp_end_date < %s THEN 1 ELSE 0 END) as overdue
			FROM `tabTask`
			WHERE project = %s
			""",
			(today_date, p.name),
			as_dict=True,
		)[0]
		p["total_tasks"] = cint(p_stats.total)
		p["completed_tasks"] = cint(p_stats.completed)
		p["overdue_tasks"] = cint(p_stats.overdue)
		p["is_at_risk"] = p["overdue_tasks"] > 0
		if p["total_tasks"] > 0:
			p["percent_complete"] = round((p["completed_tasks"] / p["total_tasks"]) * 100, 1)

	# 3. Module Health Matrix (aggregate across all projects)
	modules_health = frappe.db.sql(
		"""
		SELECT
			im.module_code,
			im.module_name,
			im.icon,
			im.color,
			COUNT(DISTINCT pim.parent) as active_in_projects,
			COUNT(t.name) as total_tasks,
			SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
			SUM(CASE WHEN t.status != 'Completed' AND t.status != 'Cancelled' AND t.exp_end_date IS NOT NULL AND t.exp_end_date < %s THEN 1 ELSE 0 END) as overdue_tasks
		FROM `tabImplementation Module` im
		LEFT JOIN `tabProject Implementation Module` pim ON pim.module = im.module_code
		LEFT JOIN `tabTask` t ON t.implementation_module = im.module_code
		WHERE im.is_active = 1
		GROUP BY im.module_code, im.module_name, im.icon, im.color
		ORDER BY im.sequence_order asc
		""",
		today_date,
		as_dict=True,
	)

	for mh in modules_health:
		mh["total_tasks"] = cint(mh["total_tasks"])
		mh["completed_tasks"] = cint(mh["completed_tasks"])
		mh["overdue_tasks"] = cint(mh["overdue_tasks"])
		mh["active_in_projects"] = cint(mh["active_in_projects"])
		mh["progress"] = round((mh["completed_tasks"] / mh["total_tasks"] * 100), 1) if mh["total_tasks"] > 0 else 0

	# 4. Upcoming Key Milestones
	upcoming_milestones = frappe.db.sql(
		"""
		SELECT
			t.name,
			t.subject,
			t.project,
			p.project_name,
			t.status,
			t.priority,
			t.exp_end_date as due_date,
			t.implementation_module,
			im.module_name,
			im.color as module_color
		FROM `tabTask` t
		JOIN `tabProject` p ON p.name = t.project
		LEFT JOIN `tabImplementation Module` im ON im.module_code = t.implementation_module
		WHERE t.is_milestone = 1 AND t.status != 'Completed' AND t.status != 'Cancelled'
		ORDER BY t.exp_end_date asc
		LIMIT 8
		""",
		as_dict=True,
	)

	return {
		"kpis": {
			"total_projects": total_projects,
			"active_projects": active_projects,
			"completed_projects": completed_projects,
			"overall_completion_pct": overall_completion_pct,
			"total_tasks": total_tasks,
			"completed_tasks": completed_tasks,
			"overdue_tasks": cint(all_tasks_stats.overdue),
			"due_today_tasks": cint(all_tasks_stats.due_today),
			"total_milestones": cint(all_tasks_stats.milestones),
			"completed_milestones": cint(all_tasks_stats.completed_milestones),
			"projects_at_risk": sum(1 for p in projects if p.get("is_at_risk")),
		},
		"projects": projects,
		"modules_health": modules_health,
		"upcoming_milestones": upcoming_milestones,
	}


@frappe.whitelist()
def get_calendar_events(start=None, end=None, assigned_to=None, project=None):
	"""Return tasks formatted as calendar events."""
	today_date = getdate(nowdate())

	filters = [
		["status", "not in", ["Cancelled"]]
	]

	if project and project != "All":
		filters.append(["project", "=", project])

	if start:
		filters.append(["exp_end_date", ">=", start])
	if end:
		filters.append(["exp_start_date", "<=", end])

	tasks = frappe.get_all(
		"Task",
		filters=filters,
		fields=[
			"name",
			"subject",
			"project",
			"implementation_module",
			"status",
			"priority",
			"progress",
			"is_milestone",
			"exp_start_date",
			"exp_end_date",
			"_assign",
		],
		order_by="exp_start_date asc",
	)

	# Module lookups
	modules = {
		m.name: m for m in frappe.get_all(
			"Implementation Module",
			fields=["name", "module_name", "icon", "color"]
		)
	}

	events = []
	for t in tasks:
		assignee_emails = json.loads(t.get("_assign") or "[]")
		if assigned_to and assigned_to != "All":
			if assigned_to not in assignee_emails:
				continue

		mod = modules.get(t.get("implementation_module"))
		color = mod.color if mod else "#3B82F6"

		# If overdue, tint or mark
		is_overdue = bool(
			t.status not in ("Completed", "Cancelled")
			and t.exp_end_date
			and getdate(t.exp_end_date) < today_date
		)

		events.append({
			"id": t.name,
			"title": t.subject,
			"start": str(t.exp_start_date or t.exp_end_date or today_date),
			"end": str(t.exp_end_date or t.exp_start_date or today_date),
			"project": t.project,
			"status": t.status,
			"priority": t.priority,
			"is_milestone": bool(t.is_milestone),
			"is_overdue": is_overdue,
			"module_title": mod.module_name if mod else None,
			"color": color,
			"assignees": assignee_emails,
		})

	return events

