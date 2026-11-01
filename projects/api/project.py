# Copyright (c) 2026, Beveren Software and contributors
# For license information, please see license.txt

import hashlib
import json
import frappe
from frappe import _
from frappe.utils import (
	add_days, getdate, nowdate, today, cint, flt, format_date, format_datetime, now_datetime
)


@frappe.whitelist()
def get_projects(status=None, search=None, project_type=None):
	"""Return list of projects with module summary, completion rate, and task statistics."""
	filters = {}
	if status and status != "All":
		filters["status"] = status
	if project_type and project_type != "All":
		filters["project_type"] = project_type

	or_filters = []
	if search:
		or_filters = [
			["project_name", "like", f"%{search}%"],
			["name", "like", f"%{search}%"],
			["client_poc_name", "like", f"%{search}%"],
			["client_poc_email", "like", f"%{search}%"],
		]

	fields = [
		"name",
		"project_name",
		"project_type",
		"status",
		"priority",
		"percent_complete",
		"expected_start_date",
		"expected_end_date",
		"actual_start_date",
		"actual_end_date",
		"customer",
		"client_poc_name",
		"client_poc_email",
		"client_poc_phone",
		"partner_poc",
		"project_manager",
		"implementation_stage",
		"auto_emails",
		"project_health",
		"auto_weekly_update",
		"auto_monthly_feedback",
		"last_weekly_update_sent",
		"last_feedback_survey_sent",
		"customer_feedback_score",
		"_user_tags",
		"_assign",
		"creation",
		"modified",
	]

	projects = frappe.get_all(
		"Project",
		filters=filters,
		or_filters=or_filters if or_filters else None,
		fields=fields,
		order_by="modified desc",
	)

	today_date = getdate(nowdate())

	for p in projects:
		# Parse user tags
		p["tags"] = [t for t in (p.get("_user_tags") or "").split(",") if t]
		p["assignees"] = json.loads(p.get("_assign") or "[]")

		# Get selected modules
		modules = frappe.get_all(
			"Project Implementation Module",
			filters={"parent": p.name},
			fields=["name", "module", "module_name", "status", "lead", "progress", "notes"],
			order_by="idx asc",
		)

		# Attach module icon and color
		for m in modules:
			mod_info = frappe.db.get_value(
				"Implementation Module",
				m.module,
				["module_name", "icon", "color"],
				as_dict=True,
			)
			if mod_info:
				m["module_title"] = mod_info.module_name
				m["icon"] = mod_info.icon
				m["color"] = mod_info.color

		p["modules"] = modules

		# Calculate task stats & estimated hours
		task_stats = frappe.db.sql(
			"""
			SELECT
				COUNT(*) as total_tasks,
				SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
				SUM(CASE WHEN status IN ('Open', 'Working', 'Pending Review') THEN 1 ELSE 0 END) as open_tasks,
				SUM(CASE WHEN status != 'Completed' AND status != 'Cancelled' AND exp_end_date IS NOT NULL AND exp_end_date < %s THEN 1 ELSE 0 END) as overdue_tasks,
				SUM(CASE WHEN is_milestone = 1 THEN 1 ELSE 0 END) as milestone_count,
				SUM(COALESCE(expected_time, 0)) as total_estimated_hours,
				SUM(CASE WHEN status = 'Completed' THEN COALESCE(expected_time, 0) ELSE 0 END) as completed_estimated_hours,
				SUM(COALESCE(actual_time, 0)) as total_actual_hours
			FROM `tabTask`
			WHERE project = %s
			""",
			(today_date, p.name),
			as_dict=True,
		)[0]

		p["total_tasks"] = cint(task_stats.total_tasks)
		p["completed_tasks"] = cint(task_stats.completed_tasks)
		p["open_tasks"] = cint(task_stats.open_tasks)
		p["overdue_tasks"] = cint(task_stats.overdue_tasks)
		p["milestone_count"] = cint(task_stats.milestone_count)
		p["total_estimated_hours"] = flt(task_stats.total_estimated_hours)
		p["completed_estimated_hours"] = flt(task_stats.completed_estimated_hours)
		p["total_actual_hours"] = flt(task_stats.total_actual_hours)

		# Dual progress calculation: hour-based where maintained, fallback to task count
		if p["total_estimated_hours"] > 0:
			p["percent_complete"] = round((p["completed_estimated_hours"] / p["total_estimated_hours"]) * 100, 1)
			p["progress_basis"] = "hours"
		elif p["total_tasks"] > 0:
			p["percent_complete"] = round((p["completed_tasks"] / p["total_tasks"]) * 100, 1)
			p["progress_basis"] = "tasks"
		else:
			p["percent_complete"] = flt(p.get("percent_complete") or 0)
			p["progress_basis"] = "manual"

		# Health status default
		if not p.get("project_health"):
			if p["overdue_tasks"] >= 5 or (p["total_tasks"] > 0 and (p["overdue_tasks"] / p["total_tasks"]) >= 0.25):
				p["project_health"] = "At Risk"
			elif p["overdue_tasks"] >= 2 or (p["total_tasks"] > 0 and (p["overdue_tasks"] / p["total_tasks"]) >= 0.10):
				p["project_health"] = "Needs Attention"
			else:
				p["project_health"] = "On Track"

		# Fetch User display names for PM & Partner POC
		if p.get("project_manager"):
			p["project_manager_name"] = frappe.db.get_value("User", p.project_manager, "full_name") or p.project_manager
		if p.get("partner_poc"):
			p["partner_poc_name"] = frappe.db.get_value("User", p.partner_poc, "full_name") or p.partner_poc

	return projects


@frappe.whitelist()
def get_project(project_name):
	"""Return comprehensive single project dashboard data with dual progress, unified activities, and governance."""
	if not frappe.db.exists("Project", project_name):
		frappe.throw(_("Project {0} not found").format(project_name), frappe.DoesNotExistError)

	doc = frappe.get_doc("Project", project_name)
	project_data = doc.as_dict()

	today_date = getdate(nowdate())

	# Tags and assignees
	project_data["tags"] = [t for t in (doc._user_tags or "").split(",") if t]
	project_data["assignees"] = json.loads(doc._assign or "[]")

	# Fetch user names
	if project_data.get("project_manager"):
		project_data["project_manager_name"] = frappe.db.get_value("User", project_data["project_manager"], "full_name") or project_data["project_manager"]
		project_data["project_manager_image"] = frappe.db.get_value("User", project_data["project_manager"], "user_image")
	if project_data.get("partner_poc"):
		project_data["partner_poc_name"] = frappe.db.get_value("User", project_data["partner_poc"], "full_name") or project_data["partner_poc"]
		project_data["partner_poc_image"] = frappe.db.get_value("User", project_data["partner_poc"], "user_image")

	# Parse governance data (Change Requests, UAT, Training, Handover, Documents, Email Snapshots)
	raw_gov = project_data.get("governance_data")
	gov = {}
	if raw_gov and isinstance(raw_gov, str):
		try:
			gov = json.loads(raw_gov)
		except Exception:
			gov = {}
	elif isinstance(raw_gov, dict):
		gov = raw_gov

	gov.setdefault("documents", [])
	gov.setdefault("email_snapshots", [])
	gov.setdefault("change_requests", [])
	gov.setdefault("uat_signoffs", [])
	gov.setdefault("training_sessions", [])
	gov.setdefault("support_handover", {
		"config_summary": False,
		"documentation_provided": False,
		"known_issues_logged": False,
		"support_portal_access": False,
		"customer_signoff": False,
		"notes": "",
	})
	gov.setdefault("sales_handover", {
		"sow_signed": True,
		"initial_payment": True,
		"scope_documented": True,
		"environment_ready": False,
		"notes": "",
	})
	project_data["governance"] = gov

	# Modules with dual progress & task stats
	modules = []
	for m in doc.selected_modules:
		m_dict = m.as_dict()
		mod_info = frappe.db.get_value(
			"Implementation Module",
			m.module,
			["module_name", "icon", "color", "description"],
			as_dict=True,
		)
		if mod_info:
			m_dict["module_title"] = mod_info.module_name
			m_dict["icon"] = mod_info.icon
			m_dict["color"] = mod_info.color
			m_dict["description"] = mod_info.description

		# Module task breakdown & hours
		mod_task_stats = frappe.db.sql(
			"""
			SELECT
				COUNT(*) as total,
				SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
				SUM(CASE WHEN status = 'Working' THEN 1 ELSE 0 END) as in_progress,
				SUM(CASE WHEN status != 'Completed' AND status != 'Cancelled' AND exp_end_date IS NOT NULL AND exp_end_date < %s THEN 1 ELSE 0 END) as overdue,
				SUM(COALESCE(expected_time, 0)) as total_hours,
				SUM(CASE WHEN status = 'Completed' THEN COALESCE(expected_time, 0) ELSE 0 END) as completed_hours
			FROM `tabTask`
			WHERE project = %s AND implementation_module = %s
			""",
			(today_date, project_name, m.module),
			as_dict=True,
		)[0]

		m_dict["total_tasks"] = cint(mod_task_stats.total)
		m_dict["completed_tasks"] = cint(mod_task_stats.completed)
		m_dict["in_progress_tasks"] = cint(mod_task_stats.in_progress)
		m_dict["overdue_tasks"] = cint(mod_task_stats.overdue)
		m_dict["total_hours"] = flt(mod_task_stats.total_hours)
		m_dict["completed_hours"] = flt(mod_task_stats.completed_hours)

		if m_dict["total_hours"] > 0:
			m_dict["progress"] = round((m_dict["completed_hours"] / m_dict["total_hours"]) * 100, 1)
			m_dict["progress_basis"] = "hours"
		elif m_dict["total_tasks"] > 0:
			m_dict["progress"] = round((m_dict["completed_tasks"] / m_dict["total_tasks"]) * 100, 1)
			m_dict["progress_basis"] = "tasks"
		else:
			m_dict["progress"] = 0.0
			m_dict["progress_basis"] = "tasks"

		if m_dict.get("lead"):
			m_dict["lead_name"] = frappe.db.get_value("User", m_dict["lead"], "full_name") or m_dict["lead"]

		modules.append(m_dict)

	project_data["modules"] = modules

	# Tasks list
	tasks = frappe.get_all(
		"Task",
		filters={"project": project_name},
		fields=[
			"name",
			"subject",
			"status",
			"priority",
			"progress",
			"is_milestone",
			"exp_start_date",
			"exp_end_date",
			"expected_time",
			"actual_time",
			"implementation_module",
			"client_visible",
			"_assign",
			"_user_tags",
			"modified",
			"completed_on",
		],
		order_by="exp_start_date asc, modified desc",
	)

	module_map = {m["module"]: m for m in modules}

	for t in tasks:
		t["tags"] = [tag for tag in (t.get("_user_tags") or "").split(",") if tag]
		t["assignees"] = json.loads(t.get("_assign") or "[]")
		t["is_overdue"] = bool(
			t.get("status") not in ("Completed", "Cancelled")
			and t.get("exp_end_date")
			and getdate(t.get("exp_end_date")) < today_date
		)
		mod = module_map.get(t.get("implementation_module"))
		if mod:
			t["module_title"] = mod.get("module_title")
			t["module_color"] = mod.get("color")
			t["module_icon"] = mod.get("icon")

	project_data["tasks"] = tasks

	# Overall statistics & dual progress calculation
	total_tasks = len(tasks)
	completed_tasks = sum(1 for t in tasks if t.status == "Completed")
	open_tasks = sum(1 for t in tasks if t.status in ("Open", "Working", "Pending Review"))
	overdue_tasks = sum(1 for t in tasks if t.get("is_overdue"))
	milestones = [t for t in tasks if t.is_milestone]

	total_est_hours = sum(flt(t.get("expected_time") or 0) for t in tasks)
	comp_est_hours = sum(flt(t.get("expected_time") or 0) for t in tasks if t.status == "Completed")
	total_act_hours = sum(flt(t.get("actual_time") or 0) for t in tasks)

	if total_est_hours > 0:
		percent_complete = round((comp_est_hours / total_est_hours * 100), 1)
		progress_basis = "hours"
	elif total_tasks > 0:
		percent_complete = round((completed_tasks / total_tasks * 100), 1)
		progress_basis = "tasks"
	else:
		percent_complete = 0.0
		progress_basis = "manual"

	# Health status calculation
	project_health = project_data.get("project_health")
	if not project_health:
		if overdue_tasks >= 5 or (total_tasks > 0 and (overdue_tasks / total_tasks) >= 0.25):
			project_health = "At Risk"
		elif overdue_tasks >= 2 or (total_tasks > 0 and (overdue_tasks / total_tasks) >= 0.10):
			project_health = "Needs Attention"
		else:
			project_health = "On Track"
		project_data["project_health"] = project_health

	project_data["stats"] = {
		"total_tasks": total_tasks,
		"completed_tasks": completed_tasks,
		"open_tasks": open_tasks,
		"overdue_tasks": overdue_tasks,
		"milestone_count": len(milestones),
		"completed_milestones": sum(1 for m in milestones if m.status == "Completed"),
		"total_estimated_hours": total_est_hours,
		"completed_estimated_hours": comp_est_hours,
		"total_actual_hours": total_act_hours,
		"percent_complete": percent_complete,
		"progress_basis": progress_basis,
	}

	# Unified 360° Activity Feed: Project Communications, Project Comments, Task Communications, Task Comments
	activities = frappe.db.sql(
		"""
		SELECT
			'Communication' as activity_type,
			comm.name,
			comm.communication_medium as comment_type,
			comm.sender,
			comm.sender_full_name as sender_name,
			comm.subject,
			comm.content,
			comm.recipients,
			comm.cc,
			comm.sent_or_received,
			comm.creation as timestamp,
			'Project' as reference_doctype,
			comm.reference_name as doc_name,
			'' as task_name,
			'' as task_subject
		FROM `tabCommunication` comm
		WHERE comm.reference_doctype = 'Project' AND comm.reference_name = %s
		UNION ALL
		SELECT
			'Comment' as activity_type,
			c.name,
			c.comment_type,
			c.comment_email as sender,
			c.comment_by as sender_name,
			c.content as subject,
			c.content,
			'' as recipients,
			'' as cc,
			'Sent' as sent_or_received,
			c.creation as timestamp,
			'Project' as reference_doctype,
			c.reference_name as doc_name,
			'' as task_name,
			'' as task_subject
		FROM `tabComment` c
		WHERE c.reference_doctype = 'Project' AND c.reference_name = %s AND c.comment_type = 'Comment'
		UNION ALL
		SELECT
			'Communication' as activity_type,
			comm.name,
			comm.communication_medium as comment_type,
			comm.sender,
			comm.sender_full_name as sender_name,
			comm.subject,
			comm.content,
			comm.recipients,
			comm.cc,
			comm.sent_or_received,
			comm.creation as timestamp,
			'Task' as reference_doctype,
			comm.reference_name as doc_name,
			t.name as task_name,
			t.subject as task_subject
		FROM `tabCommunication` comm
		JOIN `tabTask` t ON t.name = comm.reference_name
		WHERE t.project = %s AND comm.reference_doctype = 'Task'
		UNION ALL
		SELECT
			'Comment' as activity_type,
			c.name,
			c.comment_type,
			c.comment_email as sender,
			c.comment_by as sender_name,
			c.content as subject,
			c.content,
			'' as recipients,
			'' as cc,
			'Sent' as sent_or_received,
			c.creation as timestamp,
			'Task' as reference_doctype,
			c.reference_name as doc_name,
			t.name as task_name,
			t.subject as task_subject
		FROM `tabComment` c
		JOIN `tabTask` t ON t.name = c.reference_name
		WHERE t.project = %s AND c.comment_type = 'Comment'
		ORDER BY timestamp desc
		LIMIT 50
		""",
		(project_name, project_name, project_name, project_name),
		as_dict=True,
	)

	user_cache = {}
	for act in activities:
		email = act.get("sender")
		if email and email not in user_cache:
			user_cache[email] = {
				"full_name": frappe.db.get_value("User", email, "full_name") or email,
				"image": frappe.db.get_value("User", email, "user_image"),
			}
		if email in user_cache:
			act["sender_name"] = user_cache[email]["full_name"]
			act["sender_image"] = user_cache[email]["image"]

		subj = (act.get("subject") or "").lower()
		ref = act.get("reference_doctype")
		if "weekly update" in subj:
			act["badge"] = "Weekly Update"
			act["badge_tone"] = "blue"
		elif "feedback" in subj:
			act["badge"] = "Feedback Survey"
			act["badge_tone"] = "amber"
		elif "kickoff" in subj or "kick-off" in subj:
			act["badge"] = "Kick-off"
			act["badge_tone"] = "teal"
		elif "handover" in subj:
			act["badge"] = "Handover"
			act["badge_tone"] = "purple"
		elif "change request" in subj:
			act["badge"] = "Change Request"
			act["badge_tone"] = "coral"
		elif ref == "Project":
			act["badge"] = "Project Email" if act.get("activity_type") == "Communication" else "Project Note"
			act["badge_tone"] = "slate"
		else:
			act["badge"] = "Task Message" if act.get("activity_type") == "Communication" else "Task Comment"
			act["badge_tone"] = "gray"

	project_data["activity"] = activities
	project_data["recent_activities"] = activities

	# Aggregated Files: Project Files + Task Files + Governance Documents (Scope, Discussion Notes, Drive Links)
	task_names = [t.name for t in tasks]
	file_fields = ["name", "file_name", "file_url", "file_size", "creation", "attached_to_doctype", "attached_to_name", "owner"]
	project_files = frappe.get_all(
		"File",
		filters={"attached_to_doctype": "Project", "attached_to_name": project_name},
		fields=file_fields,
		order_by="creation desc",
		limit=50,
	)
	for pf in project_files:
		pf["category"] = "Project Attachment"
		pf["source"] = "project"

	task_files = []
	if task_names:
		task_files = frappe.get_all(
			"File",
			filters={"attached_to_doctype": "Task", "attached_to_name": ["in", task_names]},
			fields=file_fields,
			order_by="creation desc",
			limit=50,
		)
	subject_by_task = {t.name: t.subject for t in tasks}
	for row in task_files:
		row["task_subject"] = subject_by_task.get(row.attached_to_name) or row.attached_to_name
		row["category"] = "Task Attachment"
		row["source"] = "task"

	gov_docs = []
	for gdoc in gov.get("documents", []):
		gov_docs.append({
			"name": gdoc.get("id"),
			"file_name": gdoc.get("title") or gdoc.get("file_name") or "Document",
			"file_url": gdoc.get("file_url") or gdoc.get("drive_link") or "#",
			"file_size": gdoc.get("file_size") or 0,
			"creation": gdoc.get("uploaded_at"),
			"attached_to_doctype": "Project",
			"attached_to_name": project_name,
			"category": gdoc.get("category") or "Scope Document",
			"source": "governance",
			"drive_link": gdoc.get("drive_link"),
			"drive_owner": gdoc.get("drive_owner"),
			"drive_version": gdoc.get("drive_version"),
			"notes": gdoc.get("notes"),
		})

	project_data["files"] = gov_docs + project_files + task_files

	return project_data


# -----------------------------------------------------------------------------
# Customer Communications & Email Template Generator
# -----------------------------------------------------------------------------

@frappe.whitelist()
def get_project_email_template(project_name, template_type="weekly_update", custom_params=None):
	"""Auto-prepare structured email content with live project data, module progress, and tasks."""
	if not frappe.db.exists("Project", project_name):
		frappe.throw(_("Project {0} not found").format(project_name))

	project = get_project(project_name)
	stats = project.get("stats") or {}
	modules = project.get("modules") or []
	tasks = project.get("tasks") or []

	today_date = getdate(nowdate())
	start_of_week = add_days(today_date, -7)
	reporting_window = f"{format_date(start_of_week)} – {format_date(today_date)}"

	# Filter completed tasks in the last 7 days (fallback to recent completed if none)
	completed_this_week = [
		t for t in tasks
		if t.get("status") == "Completed" and (
			(t.get("completed_on") and getdate(t.get("completed_on")) >= start_of_week) or
			(t.get("modified") and getdate(t.get("modified")) >= start_of_week)
		)
	]
	if not completed_this_week:
		completed_this_week = [t for t in tasks if t.get("status") == "Completed"][:5]

	upcoming_tasks = [t for t in tasks if t.get("status") in ("Working", "Open")][:6]
	overdue_tasks = [t for t in tasks if t.get("is_overdue")][:5]

	client_poc_email = project.get("client_poc_email") or ""
	recipients = [client_poc_email] if client_poc_email else []

	cc = []
	if project.get("project_manager"):
		pm_email = frappe.db.get_value("User", project.get("project_manager"), "email") or project.get("project_manager")
		if pm_email and pm_email not in cc and pm_email != client_poc_email:
			cc.append(pm_email)
	if project.get("partner_poc"):
		partner_email = frappe.db.get_value("User", project.get("partner_poc"), "email") or project.get("partner_poc")
		if partner_email and partner_email not in cc and partner_email != client_poc_email:
			cc.append(partner_email)

	pm_name = project.get("project_manager_name") or project.get("project_manager") or "Beveren Delivery Team"
	client_name = project.get("client_poc_name") or "Valued Client"
	project_title = project.get("project_name") or project_name

	subject = ""
	html_content = ""

	if template_type == "weekly_update":
		subject = f"[Weekly Update] {project_title} - Implementation Progress ({reporting_window})"

		modules_rows = ""
		for m in modules:
			bar_w = min(100, max(0, round(m.get("progress", 0))))
			status_color = "#10b981" if bar_w == 100 else ("#3b82f6" if bar_w > 0 else "#9ca3af")
			status_badge = "Completed" if bar_w == 100 else ("In Progress" if bar_w > 0 else "Pending")
			modules_rows += f"""
			<tr style="border-bottom: 1px solid #f1f5f9;">
				<td style="padding: 10px 12px; font-weight: 600; color: #1e293b;">{m.get('module_title') or m.get('module_name')}</td>
				<td style="padding: 10px 12px; color: #64748b; font-size: 13px;">{m.get('completed_tasks', 0)}/{m.get('total_tasks', 0)} tasks</td>
				<td style="padding: 10px 12px; width: 140px;">
					<div style="background-color: #e2e8f0; border-radius: 9999px; height: 7px; overflow: hidden; width: 100%;">
						<div style="background-color: {status_color}; height: 100%; width: {bar_w}%;"></div>
					</div>
				</td>
				<td style="padding: 10px 12px; text-align: right; font-weight: 700; color: #334155; font-size: 13px;">{bar_w}%</td>
				<td style="padding: 10px 12px; text-align: right;">
					<span style="display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; background-color: {status_color}18; color: {status_color};">{status_badge}</span>
				</td>
			</tr>
			"""

		completed_items = ""
		if completed_this_week:
			for t in completed_this_week[:6]:
				completed_items += f"""
				<li style="margin-bottom: 8px; color: #334155;">
					<span style="color: #10b981; font-weight: bold; margin-right: 6px;">✓</span>
					<strong>{t.get('subject')}</strong> 
					<span style="color: #64748b; font-size: 12px;">({t.get('module_title') or 'General'})</span>
				</li>
				"""
		else:
			completed_items = '<li style="color: #64748b; font-style: italic;">Ongoing sprint configuration and workflow definition in progress.</li>'

		upcoming_items = ""
		if upcoming_tasks:
			for t in upcoming_tasks[:5]:
				due_str = f" · Due {format_date(t.get('exp_end_date'))}" if t.get('exp_end_date') else ""
				upcoming_items += f"""
				<li style="margin-bottom: 8px; color: #334155;">
					<span style="color: #3b82f6; font-weight: bold; margin-right: 6px;">→</span>
					<strong>{t.get('subject')}</strong>
					<span style="color: #64748b; font-size: 12px;">({t.get('module_title') or 'General'}{due_str})</span>
				</li>
				"""
		else:
			upcoming_items = '<li style="color: #64748b; font-style: italic;">No immediate scheduled tasks for next week.</li>'

		blockers_section = ""
		if overdue_tasks:
			blockers_list = ""
			for t in overdue_tasks[:4]:
				blockers_list += f"""
				<li style="margin-bottom: 6px; color: #b91c1c;">
					<strong>{t.get('subject')}</strong> – <span style="font-size: 12px;">Overdue since {format_date(t.get('exp_end_date'))}</span>
				</li>
				"""
			blockers_section = f"""
			<div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; padding: 14px 16px; margin: 20px 0;">
				<div style="font-weight: 700; color: #991b1b; font-size: 14px; margin-bottom: 8px;">
					⚠️ Active Blockers & Overdue Items ({len(overdue_tasks)})
				</div>
				<ul style="margin: 0; padding-left: 20px; font-size: 13px;">
					{blockers_list}
				</ul>
			</div>
			"""

		html_content = f"""
		<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 680px; margin: 0 auto; background-color: #ffffff; color: #1e293b; line-height: 1.6; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
			<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 28px 32px;">
				<div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin-bottom: 4px;">
					Weekly Implementation Progress Report
				</div>
				<h1 style="margin: 0 0 8px; font-size: 22px; font-weight: 700; color: #ffffff;">{project_title}</h1>
				<div style="font-size: 13px; color: #cbd5e1;">
					Reporting Window: <b>{reporting_window}</b> · ERPNext Rollout
				</div>
			</div>

			<div style="padding: 28px 32px;">
				<p style="margin-top: 0; font-size: 14px; color: #334155;">
					Dear <b>{client_name}</b>,
				</p>
				<p style="font-size: 14px; color: #475569;">
					Here is your weekly implementation update summarizing delivered tasks, active workstream status, and next steps for the upcoming sprint.
				</p>

				<div style="display: table; width: 100%; margin: 20px 0 24px;">
					<div style="display: table-cell; width: 33.3%; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; text-align: center;">
						<div style="font-size: 11px; text-transform: uppercase; font-weight: 600; color: #64748b;">Overall Progress</div>
						<div style="font-size: 24px; font-weight: 800; color: #0f172a; margin-top: 2px;">{stats.get('percent_complete')}%</div>
						<div style="font-size: 11px; color: #10b981; font-weight: 600;">Based on {stats.get('progress_basis', 'hours')}</div>
					</div>
					<div style="display: table-cell; width: 2%;"></div>
					<div style="display: table-cell; width: 32.3%; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; text-align: center;">
						<div style="font-size: 11px; text-transform: uppercase; font-weight: 600; color: #64748b;">Completed Tasks</div>
						<div style="font-size: 24px; font-weight: 800; color: #10b981; margin-top: 2px;">{stats.get('completed_tasks')}</div>
						<div style="font-size: 11px; color: #64748b;">of {stats.get('total_tasks')} total tasks</div>
					</div>
					<div style="display: table-cell; width: 2%;"></div>
					<div style="display: table-cell; width: 30.3%; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; text-align: center;">
						<div style="font-size: 11px; text-transform: uppercase; font-weight: 600; color: #64748b;">Target Go-Live</div>
						<div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-top: 6px;">{format_date(project.get('expected_end_date')) or 'TBD'}</div>
						<div style="font-size: 11px; color: #64748b;">{project.get('implementation_stage') or 'Discovery'} Phase</div>
					</div>
				</div>

				<div style="margin: 24px 0;">
					<h3 style="font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 12px; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">
						Workstream / Module Breakdown
					</h3>
					<table style="width: 100%; border-collapse: collapse; font-size: 13px;">
						<thead>
							<tr style="background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left; font-size: 11px; text-transform: uppercase; color: #64748b;">
								<th style="padding: 8px 12px;">Module</th>
								<th style="padding: 8px 12px;">Tasks</th>
								<th style="padding: 8px 12px;">Progress</th>
								<th style="padding: 8px 12px; text-align: right;">Rate</th>
								<th style="padding: 8px 12px; text-align: right;">Status</th>
							</tr>
						</thead>
						<tbody>
							{modules_rows}
						</tbody>
					</table>
				</div>

				<div style="margin: 24px 0;">
					<h3 style="font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 10px;">
						Key Work Completed This Period
					</h3>
					<ul style="margin: 0; padding-left: 20px; font-size: 13px;">
						{completed_items}
					</ul>
				</div>

				{blockers_section}

				<div style="margin: 24px 0;">
					<h3 style="font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 10px;">
						Priorities & Next Steps for Upcoming Week
					</h3>
					<ul style="margin: 0; padding-left: 20px; font-size: 13px;">
						{upcoming_items}
					</ul>
				</div>

				<div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 16px; margin: 20px 0;">
					<div style="font-weight: 700; color: #166534; font-size: 13px; margin-bottom: 6px;">
						📋 Customer Action Required
					</div>
					<p style="margin: 0; font-size: 13px; color: #15803d;">
						Please review any completed module sign-offs and verify pending data templates. Feel free to reply directly to this email with any feedback or questions.
					</p>
				</div>

				<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
				<div style="font-size: 13px; color: #64748b;">
					Warm regards,<br />
					<strong style="color: #0f172a;">{pm_name}</strong><br />
					ERPNext Consulting Practice · Beveren Software
				</div>
			</div>
		</div>
		"""

	elif template_type == "monthly_feedback":
		subject = f"[Monthly Project Feedback] {project_title} - Client Satisfaction Review"
		html_content = f"""
		<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 680px; margin: 0 auto; background-color: #ffffff; color: #1e293b; line-height: 1.6; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
			<div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); color: #ffffff; padding: 28px 32px;">
				<div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #a5b4fc; margin-bottom: 4px;">
					Client Quality & Satisfaction Survey
				</div>
				<h1 style="margin: 0 0 8px; font-size: 22px; font-weight: 700; color: #ffffff;">{project_title}</h1>
				<div style="font-size: 13px; color: #c7d2fe;">
					Monthly Implementation Governance Review
				</div>
			</div>

			<div style="padding: 28px 32px;">
				<p style="margin-top: 0; font-size: 14px; color: #334155;">
					Dear <b>{client_name}</b>,
				</p>
				<p style="font-size: 14px; color: #475569;">
					As part of our commitment to delivering exceptional ERPNext solutions, we invite you to evaluate our progress and teamwork over the past month.
				</p>

				<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin: 20px 0;">
					<div style="font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 8px;">Month in Review Snapshot</div>
					<div style="font-size: 13px; color: #334155;">
						• Current Phase: <b>{project.get('implementation_stage') or 'Discovery'}</b><br />
						• Project Completion: <b>{stats.get('percent_complete')}%</b> ({stats.get('completed_tasks')} of {stats.get('total_tasks')} tasks delivered)<br />
						• Target Go-Live: <b>{format_date(project.get('expected_end_date')) or 'TBD'}</b>
					</div>
				</div>

				<h3 style="font-size: 15px; font-weight: 700; color: #0f172a; margin: 24px 0 12px;">
					Satisfaction Evaluation (1 to 5 Stars)
				</h3>

				<div style="space-y: 12px;">
					<div style="padding: 12px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px;">
						<div style="font-weight: 600; font-size: 13px; color: #1e293b;">1. Delivery Velocity & Milestone Adherence</div>
						<div style="font-size: 12px; color: #64748b; margin-top: 2px;">Are timelines, sprint commitments, and sprint handoffs meeting expectations?</div>
						<div style="font-size: 16px; margin-top: 6px; color: #f59e0b;">⭐ ⭐ ⭐ ⭐ ⭐</div>
					</div>

					<div style="padding: 12px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px;">
						<div style="font-weight: 600; font-size: 13px; color: #1e293b;">2. Consulting Quality & Technical Competence</div>
						<div style="font-size: 12px; color: #64748b; margin-top: 2px;">Did our consulting team demonstrate deep ERPNext configuration expertise?</div>
						<div style="font-size: 16px; margin-top: 6px; color: #f59e0b;">⭐ ⭐ ⭐ ⭐ ⭐</div>
					</div>

					<div style="padding: 12px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px;">
						<div style="font-weight: 600; font-size: 13px; color: #1e293b;">3. Communication, Updates & Responsiveness</div>
						<div style="font-size: 12px; color: #64748b; margin-top: 2px;">Are questions and blockers resolved promptly with clear transparency?</div>
						<div style="font-size: 16px; margin-top: 6px; color: #f59e0b;">⭐ ⭐ ⭐ ⭐ ⭐</div>
					</div>

					<div style="padding: 12px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px;">
						<div style="font-weight: 600; font-size: 13px; color: #1e293b;">4. ERPNext Solution Fit for Business Needs</div>
						<div style="font-size: 12px; color: #64748b; margin-top: 2px;">Is the configured system aligning well with your day-to-day operations?</div>
						<div style="font-size: 16px; margin-top: 6px; color: #f59e0b;">⭐ ⭐ ⭐ ⭐ ⭐</div>
					</div>
				</div>

				<div style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 16px; margin: 20px 0;">
					<div style="font-weight: 700; color: #1e40af; font-size: 13px; margin-bottom: 4px;">
						How to respond:
					</div>
					<p style="margin: 0; font-size: 13px; color: #1d4ed8;">
						Simply reply to this email with your ratings (1–5) and any suggestions or praise. Your feedback directly shapes our consulting priorities for next month!
					</p>
				</div>

				<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
				<div style="font-size: 13px; color: #64748b;">
					Warm regards,<br />
					<strong style="color: #0f172a;">{pm_name}</strong><br />
					Client Success Practice · Beveren Software
				</div>
			</div>
		</div>
		"""

	elif template_type == "kickoff":
		subject = f"[Project Kickoff] {project_title} - ERPNext Implementation Launch & Roadmap"
		mod_list = "".join([f"<li style='margin-bottom: 4px;'><b>{m.get('module_title') or m.get('module_name')}</b></li>" for m in modules])
		html_content = f"""
		<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 680px; margin: 0 auto; background-color: #ffffff; color: #1e293b; line-height: 1.6; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
			<div style="background: linear-gradient(135deg, #065f46 0%, #047857 100%); color: #ffffff; padding: 28px 32px;">
				<div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #a7f3d0; margin-bottom: 4px;">
					Project Launch & Implementation Roadmap
				</div>
				<h1 style="margin: 0 0 8px; font-size: 22px; font-weight: 700; color: #ffffff;">{project_title}</h1>
				<div style="font-size: 13px; color: #d1fae5;">
					ERPNext Implementation Kickoff Notice
				</div>
			</div>

			<div style="padding: 28px 32px;">
				<p style="margin-top: 0; font-size: 14px; color: #334155;">
					Dear <b>{client_name}</b> and Project Stakeholders,
				</p>
				<p style="font-size: 14px; color: #475569;">
					We are thrilled to officially launch the ERPNext implementation for <b>{project_title}</b>. This document outlines our implementation scope, schedule, governance team, and kickoff agenda.
				</p>

				<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin: 20px 0;">
					<h3 style="font-size: 14px; font-weight: 700; color: #0f172a; margin: 0 0 10px;">Implementation Scope & Modules</h3>
					<ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #334155;">
						{mod_list}
					</ul>
				</div>

				<h3 style="font-size: 15px; font-weight: 700; color: #0f172a; margin: 24px 0 10px;">
					Roadmap & Key Milestones
				</h3>
				<div style="font-size: 13px; color: #334155;">
					• Expected Start Date: <b>{format_date(project.get('expected_start_date')) or today()}</b><br />
					• Target Go-Live Date: <b>{format_date(project.get('expected_end_date')) or 'TBD'}</b><br />
					• Implementation Phases: <b>Discovery ➔ Design ➔ Config ➔ Migration ➔ UAT ➔ Go-Live</b>
				</div>

				<h3 style="font-size: 15px; font-weight: 700; color: #0f172a; margin: 24px 0 10px;">
					Kickoff Meeting Agenda & Preparation
				</h3>
				<ol style="margin: 0; padding-left: 20px; font-size: 13px; color: #334155;">
					<li>Introductions of core project team & role alignment</li>
					<li>Review of business requirements & implementation scope baseline</li>
					<li>Data migration templates & opening balance cutover plan</li>
					<li>Weekly communication rhythm & steering committee review schedule</li>
					<li>Next steps & Day 1 workshop calendar</li>
				</ol>

				<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
				<div style="font-size: 13px; color: #64748b;">
					Warm regards,<br />
					<strong style="color: #0f172a;">{pm_name}</strong><br />
					ERPNext Project Practice · Beveren Software
				</div>
			</div>
		</div>
		"""

	elif template_type == "sales_handover":
		subject = f"[Sales Handover] {project_title} - Project Handover & Transition Summary"
		html_content = f"""
		<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 680px; margin: 0 auto; background-color: #ffffff; color: #1e293b; line-height: 1.6; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
			<div style="background: linear-gradient(135deg, #701a75 0%, #86198f 100%); color: #ffffff; padding: 28px 32px;">
				<div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #f5d0fe; margin-bottom: 4px;">
					Commercial to Delivery Transition
				</div>
				<h1 style="margin: 0 0 8px; font-size: 22px; font-weight: 700; color: #ffffff;">{project_title}</h1>
				<div style="font-size: 13px; color: #fae8ff;">
					Sales Department Handover & Scope Baseline
				</div>
			</div>

			<div style="padding: 28px 32px;">
				<p style="margin-top: 0; font-size: 14px; color: #334155;">
					Dear <b>{client_name}</b> and Delivery Team,
				</p>
				<p style="font-size: 14px; color: #475569;">
					This document formally marks the completion of the presales phase and handover to the Implementation Consulting Practice for <b>{project_title}</b>.
				</p>

				<div style="background-color: #fdf4ff; border: 1px solid #f0abfc; border-radius: 12px; padding: 18px; margin: 20px 0;">
					<h3 style="font-size: 14px; font-weight: 700; color: #701a75; margin: 0 0 10px;">Handover Checklist & Readiness</h3>
					<div style="font-size: 13px; color: #4a044e; space-y: 6px;">
						✓ Commercial Statement of Work (SOW) confirmed<br />
						✓ Implementation scope baseline & module checklist established<br />
						✓ Assigned Project Manager: <b>{pm_name}</b><br />
						✓ Client Lead: <b>{client_name}</b> ({client_poc_email})<br />
						✓ Target Go-Live: <b>{format_date(project.get('expected_end_date')) or 'TBD'}</b>
					</div>
				</div>

				<p style="font-size: 14px; color: #334155;">
					The delivery team is now preparing the project workspace, task blueprints, and kickoff workshop schedule.
				</p>

				<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
				<div style="font-size: 13px; color: #64748b;">
					Warm regards,<br />
					<strong style="color: #0f172a;">Sales & Delivery Practices</strong><br />
					Beveren Software
				</div>
			</div>
		</div>
		"""

	else:  # Custom email template
		subject = f"[{project_title}] Update regarding ERPNext Rollout"
		html_content = f"""
		<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 680px; margin: 0 auto; background-color: #ffffff; color: #1e293b; line-height: 1.6; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden;">
			<div style="padding: 24px 28px; background-color: #f8fafc; border-bottom: 1px solid #e2e8f0;">
				<h2 style="margin: 0; font-size: 18px; color: #0f172a;">{project_title}</h2>
				<span style="font-size: 12px; color: #64748b;">ERPNext Implementation Update</span>
			</div>
			<div style="padding: 24px 28px;">
				<p>Dear <b>{client_name}</b>,</p>
				<p>Please find our latest update regarding your ERPNext rollout.</p>
				<p style="color: #64748b; font-style: italic;">[Add your custom message content here]</p>
				<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
				<div style="font-size: 13px; color: #64748b;">
					Warm regards,<br />
					<strong style="color: #0f172a;">{pm_name}</strong><br />
					ERPNext Consulting Team · Beveren Software
				</div>
			</div>
		</div>
		"""

	# Available documents that can be attached
	available_docs = []
	for f in project.get("files") or []:
		available_docs.append({
			"name": f.get("name"),
			"title": f.get("file_name"),
			"category": f.get("category") or "Project Document",
			"file_url": f.get("file_url"),
			"file_size": f.get("file_size"),
		})

	return {
		"template_type": template_type,
		"subject": subject,
		"recipients": recipients,
		"cc": cc,
		"content": html_content.strip(),
		"metrics": {
			"percent_complete": stats.get("percent_complete"),
			"progress_basis": stats.get("progress_basis"),
			"completed_tasks_count": len(completed_this_week),
			"total_tasks": stats.get("total_tasks"),
			"overdue_tasks_count": len(overdue_tasks),
			"reporting_window": reporting_window,
		},
		"available_documents": available_docs,
	}


@frappe.whitelist()
def send_project_email(
	project_name,
	template_type=None,
	recipients=None,
	cc=None,
	bcc=None,
	subject=None,
	message=None,
	attachments=None,
	progress_snapshot=None,
	force=0,
	data=None,
):
	"""Send email to customer, record in ERPNext Communication doctype, and log snapshot in project activity."""
	if data and isinstance(data, (dict, str)):
		if isinstance(data, str):
			try:
				data = json.loads(data)
			except Exception:
				data = {}
		template_type = data.get("template_type") or template_type
		recipients = data.get("recipients") or recipients
		cc = data.get("cc") or cc
		bcc = data.get("bcc") or bcc
		subject = data.get("subject") or subject
		message = data.get("message") or data.get("content") or message
		attachments = data.get("attachments") or attachments
		progress_snapshot = data.get("progress_snapshot") or progress_snapshot
		force = data.get("force") or force

	if not frappe.db.exists("Project", project_name):
		frappe.throw(_("Project {0} not found").format(project_name))

	if isinstance(recipients, str):
		try:
			recipients = json.loads(recipients)
		except Exception:
			recipients = [r.strip() for r in recipients.split(",") if r.strip()]

	if not recipients:
		frappe.throw(_("At least one recipient email address is required."))

	if isinstance(cc, str):
		try:
			cc = json.loads(cc)
		except Exception:
			cc = [c.strip() for c in cc.split(",") if c.strip()]

	if isinstance(bcc, str):
		try:
			bcc = json.loads(bcc)
		except Exception:
			bcc = [b.strip() for b in bcc.split(",") if b.strip()]

	if isinstance(attachments, str):
		try:
			attachments = json.loads(attachments)
		except Exception:
			attachments = []

	if isinstance(progress_snapshot, str):
		try:
			progress_snapshot = json.loads(progress_snapshot)
		except Exception:
			progress_snapshot = {}

	doc = frappe.get_doc("Project", project_name)

	# Duplicate prevention check (for weekly updates within same 5-day window)
	today_date = getdate(nowdate())
	if template_type == "weekly_update" and not cint(force):
		if doc.last_weekly_update_sent:
			days_since = (today_date - getdate(doc.last_weekly_update_sent)).days
			if days_since < 5:
				return {
					"warning": True,
					"message": _("A weekly update was already sent {0} days ago on {1}. Check 'force' to send again.").format(
						days_since, format_date(doc.last_weekly_update_sent)
					)
				}

	# 1. Send via Frappe mailer
	email_args = {
		"recipients": recipients,
		"cc": cc or None,
		"bcc": bcc or None,
		"subject": subject,
		"message": message,
		"reference_doctype": "Project",
		"reference_name": project_name,
	}

	# Attach files if provided
	processed_attachments = []
	if attachments:
		for a in attachments:
			file_url = a.get("file_url") if isinstance(a, dict) else a
			if not file_url or not isinstance(file_url, str):
				continue
			file_doc = frappe.db.get_value("File", {"file_url": file_url}, ["name", "file_name", "is_private"], as_dict=True)
			if file_doc:
				try:
					f = frappe.get_doc("File", file_doc.name)
					content = f.get_content()
					if content:
						processed_attachments.append({
							"fname": file_doc.file_name or file_url.split("/")[-1],
							"fcontent": content,
						})
				except Exception:
					pass
			else:
				try:
					import os
					site_path = frappe.get_site_path()
					disk_path = site_path + ("" if file_url.startswith("/") else "/") + file_url
					if os.path.exists(disk_path):
						with open(disk_path, "rb") as fp:
							processed_attachments.append({
								"fname": file_url.split("/")[-1],
								"fcontent": fp.read(),
							})
				except Exception:
					pass

	if processed_attachments:
		email_args["attachments"] = processed_attachments

	try:
		frappe.sendmail(**email_args)
	except Exception as e:
		frappe.log_error(f"Error sending project email: {str(e)}", "Project Email")
		frappe.throw(_("Failed to deliver email: {0}").format(str(e)))

	# 2. Record Communication in tabCommunication
	sender_email = frappe.session.user
	sender_name = frappe.db.get_value("User", sender_email, "full_name") or sender_email

	comm = frappe.get_doc({
		"doctype": "Communication",
		"communication_type": "Communication",
		"communication_medium": "Email",
		"sent_or_received": "Sent",
		"sender": sender_email,
		"sender_full_name": sender_name,
		"recipients": ", ".join(recipients) if isinstance(recipients, list) else recipients,
		"cc": ", ".join(cc) if isinstance(cc, list) and cc else "",
		"bcc": ", ".join(bcc) if isinstance(bcc, list) and bcc else "",
		"subject": subject,
		"content": message,
		"reference_doctype": "Project",
		"reference_name": project_name,
	})
	comm.insert(ignore_permissions=True)

	# 3. Add Project Activity Comment
	label = template_type.replace("_", " ").title()
	comm_summary = f"<b>{label}</b> sent to <i>{', '.join(recipients)}</i>: <b>{subject}</b>"
	frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Comment",
		"reference_doctype": "Project",
		"reference_name": project_name,
		"content": comm_summary,
		"comment_email": sender_email,
		"comment_by": sender_name,
	}).insert(ignore_permissions=True)

	# 4. Save historical snapshot into governance_data
	raw_gov = doc.governance_data
	gov = {}
	if raw_gov and isinstance(raw_gov, str):
		try:
			gov = json.loads(raw_gov)
		except Exception:
			gov = {}
	elif isinstance(raw_gov, dict):
		gov = raw_gov

	gov.setdefault("email_snapshots", [])
	snapshot = {
		"id": f"SNAP-{frappe.generate_hash(length=8)}",
		"template_type": template_type,
		"subject": subject,
		"recipients": recipients,
		"cc": cc or [],
		"content": message,
		"sent_at": str(now_datetime()),
		"sent_by": sender_email,
		"sent_by_name": sender_name,
		"status": "Sent",
		"progress_snapshot": progress_snapshot or {},
	}
	gov["email_snapshots"].insert(0, snapshot)
	if len(gov["email_snapshots"]) > 50:
		gov["email_snapshots"] = gov["email_snapshots"][:50]

	doc.governance_data = json.dumps(gov)

	# Update tracking timestamp
	if template_type == "weekly_update":
		doc.last_weekly_update_sent = now_datetime()
	elif template_type == "monthly_feedback":
		doc.last_feedback_survey_sent = now_datetime()

	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"success": True,
		"communication_name": comm.name,
		"message": _("Email successfully sent and logged into Project Activity."),
		"snapshot": snapshot,
	}


# -----------------------------------------------------------------------------
# Document Governance (Scope Docs, Discussion Notes, Governed Drive Links)
# -----------------------------------------------------------------------------

@frappe.whitelist()
def attach_project_governance_doc(
	project_name,
	title=None,
	category="Scope Document",
	file_url=None,
	file_name=None,
	file_size=0,
	drive_link=None,
	drive_owner=None,
	drive_version=None,
	notes=None,
	data=None,
):
	"""Attach dedicated Scope document, Discussion note, or Governed Google Drive link to Project."""
	if data and isinstance(data, (dict, str)):
		if isinstance(data, str):
			try:
				data = json.loads(data)
			except Exception:
				data = {}
		title = data.get("title") or title
		category = data.get("category") or category
		file_url = data.get("file_url") or file_url
		file_name = data.get("file_name") or file_name
		file_size = data.get("file_size") or file_size
		drive_link = data.get("drive_link") or data.get("url") or drive_link
		drive_owner = data.get("drive_owner") or data.get("owner") or drive_owner
		drive_version = data.get("drive_version") or data.get("version") or drive_version
		notes = data.get("notes") or notes
	if not frappe.db.exists("Project", project_name):
		frappe.throw(_("Project {0} not found").format(project_name))

	if not title:
		frappe.throw(_("Document title is required"))

	doc = frappe.get_doc("Project", project_name)
	raw_gov = doc.governance_data
	gov = {}
	if raw_gov and isinstance(raw_gov, str):
		try:
			gov = json.loads(raw_gov)
		except Exception:
			gov = {}
	elif isinstance(raw_gov, dict):
		gov = raw_gov

	gov.setdefault("documents", [])

	doc_id = f"DOC-{frappe.generate_hash(length=8)}"
	new_doc = {
		"id": doc_id,
		"title": title.strip(),
		"category": category,
		"file_url": file_url or "",
		"file_name": file_name or (title + (".pdf" if not drive_link else "")),
		"file_size": cint(file_size),
		"drive_link": drive_link or "",
		"drive_owner": drive_owner or "",
		"drive_version": drive_version or "v1.0",
		"notes": notes or "",
		"uploaded_by": frappe.session.user,
		"uploaded_by_name": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
		"uploaded_at": str(now_datetime()),
	}

	gov["documents"].insert(0, new_doc)
	doc.governance_data = json.dumps(gov)
	doc.save(ignore_permissions=True)

	# Log Project activity comment
	sender_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
	cat_label = category or "Scope Document"
	frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Comment",
		"reference_doctype": "Project",
		"reference_name": project_name,
		"content": f"Attached <b>{cat_label}</b>: <i>{title}</i>",
		"comment_email": frappe.session.user,
		"comment_by": sender_name,
	}).insert(ignore_permissions=True)

	frappe.db.commit()

	return {
		"success": True,
		"document": new_doc,
		"message": _("Document attached successfully."),
	}


@frappe.whitelist()
def delete_project_governance_doc(project_name, doc_id):
	"""Remove a governance document from project."""
	if not frappe.db.exists("Project", project_name):
		frappe.throw(_("Project not found"))

	doc = frappe.get_doc("Project", project_name)
	raw_gov = doc.governance_data
	if not raw_gov:
		return {"success": True}

	gov = json.loads(raw_gov) if isinstance(raw_gov, str) else raw_gov
	docs = gov.get("documents", [])
	gov["documents"] = [d for d in docs if d.get("id") != doc_id]

	doc.governance_data = json.dumps(gov)
	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return {"success": True, "message": _("Document removed.")}


# -----------------------------------------------------------------------------
# Project Governance & Approval Management
# -----------------------------------------------------------------------------

@frappe.whitelist()
def update_project_governance(project_name, data):
	"""Update health, automated communication preferences, or feedback score."""
	if not frappe.db.exists("Project", project_name):
		frappe.throw(_("Project not found"))

	if isinstance(data, str):
		data = json.loads(data)

	doc = frappe.get_doc("Project", project_name)

	allowed = [
		"project_health", "health_notes", "auto_weekly_update",
		"auto_monthly_feedback", "customer_feedback_score", "customer_feedback_notes"
	]
	for f in allowed:
		if f in data:
			doc.set(f, data[f])

	if "governance" in data:
		raw_gov = doc.governance_data
		gov = json.loads(raw_gov) if raw_gov and isinstance(raw_gov, str) else (raw_gov or {})
		gov.update(data["governance"])
		doc.governance_data = json.dumps(gov)

	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return get_project(project_name)


@frappe.whitelist()
def record_governance_item(project_name, item_type, item_data):
	"""Record a Change Request, UAT Sign-off, Training Session, or Handover checklist item."""
	if not frappe.db.exists("Project", project_name):
		frappe.throw(_("Project not found"))

	if isinstance(item_data, str):
		item_data = json.loads(item_data)

	doc = frappe.get_doc("Project", project_name)
	raw_gov = doc.governance_data
	gov = json.loads(raw_gov) if raw_gov and isinstance(raw_gov, str) else (raw_gov or {})

	if item_type not in gov:
		gov[item_type] = []

	if isinstance(gov[item_type], list):
		item_id = item_data.get("id") or f"{item_type.upper()[:3]}-{frappe.generate_hash(length=6)}"
		item_data["id"] = item_id
		item_data["recorded_at"] = str(now_datetime())
		item_data["recorded_by"] = frappe.session.user

		# Update existing or prepend new
		existing_idx = next((i for i, x in enumerate(gov[item_type]) if x.get("id") == item_id), None)
		if existing_idx is not None:
			gov[item_type][existing_idx] = item_data
		else:
			gov[item_type].insert(0, item_data)
	elif isinstance(gov[item_type], dict):
		gov[item_type].update(item_data)

	doc.governance_data = json.dumps(gov)
	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return {"success": True, "item": item_data}


# -----------------------------------------------------------------------------
# Scheduled Background Automation
# -----------------------------------------------------------------------------

def send_scheduled_weekly_updates():
	"""Background worker: Automatically sends weekly updates to clients on configured day."""
	eligible_projects = frappe.get_all(
		"Project",
		filters={
			"status": "Open",
			"is_active": 1,
			"auto_emails": 1,
			"auto_weekly_update": 1,
		},
		fields=["name", "project_name", "client_poc_email", "last_weekly_update_sent"],
	)

	today_date = getdate(nowdate())
	sent_count = 0

	for proj in eligible_projects:
		if not proj.client_poc_email:
			continue

		# Prevent duplicate if sent within past 5 days
		if proj.last_weekly_update_sent:
			days_since = (today_date - getdate(proj.last_weekly_update_sent)).days
			if days_since < 5:
				continue

		try:
			tpl = get_project_email_template(proj.name, "weekly_update")
			send_project_email(
				project_name=proj.name,
				template_type="weekly_update",
				recipients=tpl["recipients"],
				cc=tpl.get("cc"),
				subject=tpl["subject"],
				message=tpl["content"],
				progress_snapshot=tpl.get("metrics"),
			)
			sent_count += 1
		except Exception as e:
			frappe.log_error(f"Failed to auto-send weekly update for {proj.name}: {str(e)}", "Scheduled Project Update")

	if sent_count > 0:
		frappe.db.commit()

	return sent_count


def send_scheduled_monthly_feedback():
	"""Background worker: Automatically sends monthly feedback survey to clients."""
	eligible_projects = frappe.get_all(
		"Project",
		filters={
			"status": "Open",
			"is_active": 1,
			"auto_emails": 1,
			"auto_monthly_feedback": 1,
		},
		fields=["name", "project_name", "client_poc_email", "last_feedback_survey_sent"],
	)

	today_date = getdate(nowdate())
	sent_count = 0

	for proj in eligible_projects:
		if not proj.client_poc_email:
			continue

		# Prevent duplicate if sent within past 25 days
		if proj.last_feedback_survey_sent:
			days_since = (today_date - getdate(proj.last_feedback_survey_sent)).days
			if days_since < 25:
				continue

		try:
			tpl = get_project_email_template(proj.name, "monthly_feedback")
			send_project_email(
				project_name=proj.name,
				template_type="monthly_feedback",
				recipients=tpl["recipients"],
				cc=tpl.get("cc"),
				subject=tpl["subject"],
				message=tpl["content"],
				progress_snapshot=tpl.get("metrics"),
			)
			sent_count += 1
		except Exception as e:
			frappe.log_error(f"Failed to auto-send monthly feedback for {proj.name}: {str(e)}", "Scheduled Monthly Feedback")

	if sent_count > 0:
		frappe.db.commit()

	return sent_count


# -----------------------------------------------------------------------------
# Existing CRUD & Core Project APIs
# -----------------------------------------------------------------------------

@frappe.whitelist()
def create_project(data):
	"""Create a new Implementation Project and automatically generate tasks for selected modules."""
	if isinstance(data, str):
		data = json.loads(data)

	project_name = data.get("project_name")
	if not project_name:
		frappe.throw(_("Project Name is required"))

	expected_start = getdate(data.get("expected_start_date") or today())
	expected_end = getdate(data.get("expected_end_date") or add_days(expected_start, 60))

	doc = frappe.get_doc({
		"doctype": "Project",
		"project_name": project_name,
		"project_type": data.get("project_type") or "Implementation",
		"status": data.get("status") or "Open",
		"priority": data.get("priority") or "Medium",
		"expected_start_date": expected_start,
		"expected_end_date": expected_end,
		"client_poc_name": data.get("client_poc_name"),
		"client_poc_email": data.get("client_poc_email"),
		"client_poc_phone": data.get("client_poc_phone"),
		"partner_poc": data.get("partner_poc"),
		"project_manager": data.get("project_manager"),
		"implementation_stage": data.get("implementation_stage") or "Discovery",
		"auto_emails": cint(data.get("auto_emails", 1)),
		"project_health": data.get("project_health") or "On Track",
		"notes": data.get("notes") or "",
	})

	if doc.project_type and not frappe.db.exists("Project Type", doc.project_type):
		ptype = frappe.get_doc({"doctype": "Project Type", "project_type": doc.project_type})
		ptype.insert(ignore_permissions=True)

	selected_modules = data.get("selected_modules") or []
	for mod_code in selected_modules:
		mod_name = frappe.db.get_value("Implementation Module", mod_code, "module_name") or mod_code
		doc.append("selected_modules", {
			"module": mod_code,
			"module_name": mod_name,
			"status": "Pending",
			"progress": 0,
		})

	assigned_users = set()
	if doc.project_manager:
		assigned_users.add(doc.project_manager)
	if doc.partner_poc:
		assigned_users.add(doc.partner_poc)

	for u in assigned_users:
		doc.append("users", {"user": u})

	doc.insert(ignore_permissions=True)

	if data.get("tags"):
		from frappe.desk.doctype.tag.tag import add_tag
		for tag in data.get("tags"):
			if tag.strip():
				add_tag(tag.strip(), "Project", doc.name)

	created_tasks_count = 0
	for mod_code in selected_modules:
		mod_doc = frappe.get_doc("Implementation Module", mod_code)
		if not mod_doc.tasks:
			continue

		for template in mod_doc.tasks:
			task_start = add_days(expected_start, template.day_offset or 0)
			duration = template.duration_days or 3
			task_end = add_days(task_start, duration)

			task_doc = frappe.get_doc({
				"doctype": "Task",
				"subject": template.subject,
				"description": template.description or "",
				"project": doc.name,
				"implementation_module": mod_code,
				"priority": template.priority or "Medium",
				"is_milestone": cint(template.is_milestone),
				"expected_time": flt(template.expected_hours or 8),
				"task_weight": flt(template.task_weight or 0),
				"status": "Open",
				"exp_start_date": task_start,
				"exp_end_date": task_end,
				"client_visible": 1,
			})
			task_doc.insert(ignore_permissions=True)
			created_tasks_count += 1

	if doc.auto_emails and doc.client_poc_email:
		try:
			send_kickoff_email(doc, selected_modules, created_tasks_count)
		except Exception as e:
			frappe.log_error(f"Error sending kickoff email: {str(e)}", "Project Implementation Email")

	frappe.db.commit()

	return {
		"project_name": doc.name,
		"tasks_created": created_tasks_count,
		"message": _("Project {0} created with {1} automated tasks.").format(doc.name, created_tasks_count),
	}


def send_kickoff_email(project_doc, selected_modules, tasks_count):
	"""Send kickoff introduction email to the client point of contact."""
	mod_names = []
	for m in selected_modules:
		name = frappe.db.get_value("Implementation Module", m, "module_name") or m
		mod_names.append(f"<li><b>{name}</b></li>")

	modules_html = "<ul>" + "".join(mod_names) + "</ul>"
	subject = f"ERPNext Implementation Project Kickoff: {project_doc.project_name}"
	message = f"""
	<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1f2937;">
		<h2 style="color: #111827;">Welcome to your ERPNext Implementation!</h2>
		<p>Dear {project_doc.client_poc_name or 'Valued Client'},</p>
		<p>We are excited to begin your ERPNext implementation project: <b>{project_doc.project_name}</b>.</p>
		<p>Our team has set up your project roadmap spanning from <b>{project_doc.expected_start_date}</b> to <b>{project_doc.expected_end_date}</b>.</p>
		
		<h3 style="color: #374151;">Selected Modules in Scope:</h3>
		{modules_html}

		<p>A total of <b>{tasks_count} implementation tasks and milestones</b> have been scheduled to ensure a smooth configuration, data migration, and UAT.</p>
		<p>Your Project Manager is: <b>{project_doc.project_manager or 'Assigned Consultant'}</b>.</p>
		
		<hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0;" />
		<p style="font-size: 13px; color: #6b7280;">You will receive automated updates as tasks and milestones progress.</p>
	</div>
	"""

	frappe.sendmail(
		recipients=[project_doc.client_poc_email],
		subject=subject,
		message=message,
		reference_doctype="Project",
		reference_name=project_doc.name,
	)


@frappe.whitelist()
def update_project(project_name, data):
	"""Update project fields and recalulate completion."""
	if isinstance(data, str):
		data = json.loads(data)

	doc = frappe.get_doc("Project", project_name)

	allowed_fields = [
		"status", "priority", "implementation_stage", "expected_start_date",
		"expected_end_date", "actual_start_date", "actual_end_date",
		"client_poc_name", "client_poc_email", "client_poc_phone",
		"partner_poc", "project_manager", "auto_emails", "project_health",
		"health_notes", "auto_weekly_update", "auto_monthly_feedback",
		"customer_feedback_score", "customer_feedback_notes", "notes"
	]

	for field in allowed_fields:
		if field in data:
			doc.set(field, data[field])

	if "tags" in data:
		from frappe.desk.doctype.tag.tag import add_tag, remove_tag
		existing_tags = set([t for t in (doc._user_tags or "").split(",") if t])
		new_tags = set(data["tags"])
		for t in existing_tags - new_tags:
			remove_tag(t, "Project", project_name)
		for t in new_tags - existing_tags:
			if t.strip():
				add_tag(t.strip(), "Project", project_name)

	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return get_project(project_name)


@frappe.whitelist()
def add_module_to_project(project_name, module_code):
	"""Add a module to an existing project and generate its tasks."""
	if not frappe.db.exists("Project", project_name):
		frappe.throw(_("Project not found"))

	doc = frappe.get_doc("Project", project_name)

	for m in doc.selected_modules:
		if m.module == module_code:
			frappe.throw(_("Module already in project"))

	mod_name = frappe.db.get_value("Implementation Module", module_code, "module_name") or module_code
	doc.append("selected_modules", {
		"module": module_code,
		"module_name": mod_name,
		"status": "Pending",
		"progress": 0,
	})
	doc.save(ignore_permissions=True)

	mod_doc = frappe.get_doc("Implementation Module", module_code)
	start_date = getdate(doc.expected_start_date or today())
	created_count = 0

	for template in mod_doc.tasks:
		task_start = add_days(start_date, template.day_offset or 0)
		task_end = add_days(task_start, template.duration_days or 3)
		task = frappe.get_doc({
			"doctype": "Task",
			"subject": template.subject,
			"description": template.description or "",
			"project": doc.name,
			"implementation_module": module_code,
			"priority": template.priority or "Medium",
			"is_milestone": cint(template.is_milestone),
			"expected_time": flt(template.expected_hours or 8),
			"status": "Open",
			"exp_start_date": task_start,
			"exp_end_date": task_end,
			"client_visible": 1,
		})
		task.insert(ignore_permissions=True)
		created_count += 1

	frappe.db.commit()
	return {"message": _("Module added with {0} tasks generated.").format(created_count)}


@frappe.whitelist()
def delete_project(project_name):
	"""Delete a project and its tasks."""
	if not frappe.db.exists("Project", project_name):
		frappe.throw(_("Project not found"))

	tasks = frappe.get_all("Task", filters={"project": project_name}, pluck="name")
	for t in tasks:
		frappe.delete_doc("Task", t, ignore_permissions=True)

	frappe.delete_doc("Project", project_name, ignore_permissions=True)
	frappe.db.commit()
	return {"success": True}
