# Copyright (c) 2026, Beveren Software and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate, today, cint, flt


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

		# Calculate task stats
		task_stats = frappe.db.sql(
			"""
			SELECT
				COUNT(*) as total_tasks,
				SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
				SUM(CASE WHEN status IN ('Open', 'Working', 'Pending Review') THEN 1 ELSE 0 END) as open_tasks,
				SUM(CASE WHEN status != 'Completed' AND status != 'Cancelled' AND exp_end_date IS NOT NULL AND exp_end_date < %s THEN 1 ELSE 0 END) as overdue_tasks,
				SUM(CASE WHEN is_milestone = 1 THEN 1 ELSE 0 END) as milestone_count
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

		# Calculated completion percentage
		if p["total_tasks"] > 0:
			calculated_percent = round((p["completed_tasks"] / p["total_tasks"]) * 100, 1)
			p["percent_complete"] = calculated_percent
		else:
			p["percent_complete"] = flt(p.get("percent_complete") or 0)

		# Fetch User display names for PM & Partner POC
		if p.get("project_manager"):
			p["project_manager_name"] = frappe.db.get_value("User", p.project_manager, "full_name") or p.project_manager
		if p.get("partner_poc"):
			p["partner_poc_name"] = frappe.db.get_value("User", p.partner_poc, "full_name") or p.partner_poc

	return projects


@frappe.whitelist()
def get_project(project_name):
	"""Return comprehensive single project dashboard data."""
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

	# Modules with their specific task stats
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

		# Module task breakdown
		mod_task_stats = frappe.db.sql(
			"""
			SELECT
				COUNT(*) as total,
				SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
				SUM(CASE WHEN status = 'Working' THEN 1 ELSE 0 END) as in_progress,
				SUM(CASE WHEN status != 'Completed' AND status != 'Cancelled' AND exp_end_date IS NOT NULL AND exp_end_date < %s THEN 1 ELSE 0 END) as overdue
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

		if m_dict["total_tasks"] > 0:
			m_dict["progress"] = round((m_dict["completed_tasks"] / m_dict["total_tasks"]) * 100, 1)

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
		],
		order_by="exp_start_date asc, modified desc",
	)

	# Module lookup map for fast tagging
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

	# Overall statistics
	total_tasks = len(tasks)
	completed_tasks = sum(1 for t in tasks if t.status == "Completed")
	open_tasks = sum(1 for t in tasks if t.status in ("Open", "Working", "Pending Review"))
	overdue_tasks = sum(1 for t in tasks if t.get("is_overdue"))
	milestones = [t for t in tasks if t.is_milestone]

	project_data["stats"] = {
		"total_tasks": total_tasks,
		"completed_tasks": completed_tasks,
		"open_tasks": open_tasks,
		"overdue_tasks": overdue_tasks,
		"milestone_count": len(milestones),
		"completed_milestones": sum(1 for m in milestones if m.status == "Completed"),
		"percent_complete": round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0,
	}

	# Recent activity (comments & communications)
	activities = frappe.db.sql(
		"""
		SELECT
			'Comment' as activity_type,
			c.name,
			c.comment_type,
			c.comment_email as sender,
			c.comment_by as sender_name,
			c.content,
			c.creation as timestamp,
			c.reference_name as task_name
		FROM `tabComment` c
		JOIN `tabTask` t ON t.name = c.reference_name
		WHERE t.project = %s AND c.comment_type = 'Comment'
		UNION ALL
		SELECT
			'Communication' as activity_type,
			comm.name,
			comm.communication_medium as comment_type,
			comm.sender,
			comm.sender_full_name as sender_name,
			comm.subject as content,
			comm.creation as timestamp,
			comm.reference_name as task_name
		FROM `tabCommunication` comm
		JOIN `tabTask` t ON t.name = comm.reference_name
		WHERE t.project = %s AND comm.reference_doctype = 'Task'
		ORDER BY timestamp desc
		LIMIT 15
		""",
		(project_name, project_name),
		as_dict=True,
	)
	project_data["recent_activities"] = activities

	return project_data


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

	# 1. Create Project document
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
		"notes": data.get("notes") or "",
	})

	# Ensure project type exists
	if doc.project_type and not frappe.db.exists("Project Type", doc.project_type):
		ptype = frappe.get_doc({"doctype": "Project Type", "project_type": doc.project_type})
		ptype.insert(ignore_permissions=True)

	# Add selected modules to child table
	selected_modules = data.get("selected_modules") or []
	for mod_code in selected_modules:
		mod_name = frappe.db.get_value("Implementation Module", mod_code, "module_name") or mod_code
		doc.append("selected_modules", {
			"module": mod_code,
			"module_name": mod_name,
			"status": "Pending",
			"progress": 0,
		})

	# Add project manager / partner POC to Project Users table
	assigned_users = set()
	if doc.project_manager:
		assigned_users.add(doc.project_manager)
	if doc.partner_poc:
		assigned_users.add(doc.partner_poc)

	for u in assigned_users:
		doc.append("users", {"user": u})

	doc.insert(ignore_permissions=True)

	# Add tags if provided
	if data.get("tags"):
		from frappe.desk.doctype.tag.tag import add_tag
		for tag in data.get("tags"):
			if tag.strip():
				add_tag(tag.strip(), "Project", doc.name)

	# 2. Automated Task Generation from Module Templates
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

	# 3. Auto Email to Client PoC if enabled
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
		"partner_poc", "project_manager", "auto_emails", "notes"
	]

	for field in allowed_fields:
		if field in data:
			doc.set(field, data[field])

	# Update tags
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

	# Check if already added
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

	# Generate tasks
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

	# Delete tasks
	tasks = frappe.get_all("Task", filters={"project": project_name}, pluck="name")
	for t in tasks:
		frappe.delete_doc("Task", t, ignore_permissions=True)

	frappe.delete_doc("Project", project_name, ignore_permissions=True)
	frappe.db.commit()
	return {"success": True}
