# Copyright (c) 2026, Beveren Software and contributors
# For license information, please see license.txt

import html
import json
import re
import frappe
from frappe import _
from frappe.desk.form.assign_to import add as add_assignment, remove as remove_assignment
from frappe.utils import getdate, nowdate, flt, cint, add_to_date, now_datetime, is_html, escape_html, strip_html_tags
from frappe.utils.html_utils import sanitize_html, clean_email_html


@frappe.whitelist()
def get_tasks(
	project=None,
	module=None,
	status=None,
	priority=None,
	assigned_to=None,
	is_milestone=None,
	search=None,
):
	"""Fetch tasks with assignee metadata, module details, and project details."""
	filters = {}
	if project and project != "All":
		filters["project"] = project
	if module and module != "All":
		filters["implementation_module"] = module
	if status and status != "All":
		filters["status"] = status
	if priority and priority != "All":
		filters["priority"] = priority
	if is_milestone is not None and is_milestone != "":
		filters["is_milestone"] = cint(is_milestone)

	or_filters = []
	if search:
		or_filters = [
			["subject", "like", f"%{search}%"],
			["name", "like", f"%{search}%"],
			["project", "like", f"%{search}%"],
		]

	fields = [
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
		"expected_time",
		"actual_time",
		"_assign",
		"_user_tags",
		"modified",
		"creation",
	]

	tasks = frappe.get_all(
		"Task",
		filters=filters,
		or_filters=or_filters if or_filters else None,
		fields=fields,
		order_by="exp_end_date asc, modified desc",
	)

	today_date = getdate(nowdate())

	# Fetch module lookups
	modules = {
		m.name: m for m in frappe.get_all(
			"Implementation Module",
			fields=["name", "module_name", "icon", "color"]
		)
	}

	# Fetch project lookups
	project_names = list(set([t.project for t in tasks if t.project]))
	projects = {}
	if project_names:
		projects = {
			p.name: p for p in frappe.get_all(
				"Project",
				filters={"name": ["in", project_names]},
				fields=["name", "project_name", "client_poc_name", "client_poc_email"],
			)
		}

	user_cache = {}

	filtered_tasks = []
	for t in tasks:
		assignee_emails = json.loads(t.get("_assign") or "[]")
		
		# Filter by assigned_to if requested
		if assigned_to and assigned_to != "All":
			if assigned_to not in assignee_emails:
				continue

		t["assignee_emails"] = assignee_emails
		t["assignees"] = []
		for email in assignee_emails:
			if email not in user_cache:
				user_cache[email] = {
					"email": email,
					"full_name": frappe.db.get_value("User", email, "full_name") or email,
					"user_image": frappe.db.get_value("User", email, "user_image"),
				}
			t["assignees"].append(user_cache[email])

		t["tags"] = [tag for tag in (t.get("_user_tags") or "").split(",") if tag]

		t["is_overdue"] = bool(
			t.get("status") not in ("Completed", "Cancelled")
			and t.get("exp_end_date")
			and getdate(t.get("exp_end_date")) < today_date
		)

		# Attach module info
		mod = modules.get(t.get("implementation_module"))
		if mod:
			t["module_title"] = mod.module_name
			t["module_icon"] = mod.icon
			t["module_color"] = mod.color

		# Attach project info
		proj = projects.get(t.get("project"))
		if proj:
			t["project_title"] = proj.project_name
			t["client_poc_name"] = proj.client_poc_name

		filtered_tasks.append(t)

	return filtered_tasks


@frappe.whitelist()
def get_task(task_id):
	"""Return comprehensive ticket details including full activity timeline."""
	if not frappe.db.exists("Task", task_id):
		frappe.throw(_("Task {0} not found").format(task_id), frappe.DoesNotExistError)

	doc = frappe.get_doc("Task", task_id)
	task_data = doc.as_dict()

	today_date = getdate(nowdate())

	# Tags & Assignees
	task_data["tags"] = [tag for tag in (doc._user_tags or "").split(",") if tag]
	assignee_emails = json.loads(doc._assign or "[]")
	task_data["assignee_emails"] = assignee_emails
	task_data["assignees"] = []
	for email in assignee_emails:
		task_data["assignees"].append({
			"email": email,
			"full_name": frappe.db.get_value("User", email, "full_name") or email,
			"user_image": frappe.db.get_value("User", email, "user_image"),
		})

	task_data["is_overdue"] = bool(
		doc.status not in ("Completed", "Cancelled")
		and doc.exp_end_date
		and getdate(doc.exp_end_date) < today_date
	)

	# Module info
	if doc.implementation_module:
		mod = frappe.db.get_value(
			"Implementation Module",
			doc.implementation_module,
			["module_name", "icon", "color"],
			as_dict=True,
		)
		if mod:
			task_data["module_title"] = mod.module_name
			task_data["module_icon"] = mod.icon
			task_data["module_color"] = mod.color

	# Project info
	if doc.project:
		proj = frappe.db.get_value(
			"Project",
			doc.project,
			["project_name", "client_poc_name", "client_poc_email", "client_poc_phone", "project_manager"],
			as_dict=True,
		)
		if proj:
			task_data["project_title"] = proj.project_name
			task_data["client_poc_name"] = proj.client_poc_name
			task_data["client_poc_email"] = proj.client_poc_email
			task_data["project_manager"] = proj.project_manager

	# -------------------------------------------------------------------------
	# Helpdesk Ticket-Style Activity Timeline:
	# Comments, Emails (Communications), and System Version Changes
	# -------------------------------------------------------------------------
	timeline = []

	# 1. Comments
	comments = frappe.get_all(
		"Comment",
		filters={"reference_doctype": "Task", "reference_name": task_id},
		fields=["name", "comment_type", "comment_email", "comment_by", "content", "creation"],
		order_by="creation desc",
	)
	for c in comments:
		sender_name = c.comment_by or frappe.db.get_value("User", c.comment_email, "full_name") or c.comment_email
		if c.comment_type != "Comment":
			# Frappe's automatic activity (Assigned, Attachment, Edit, Info, ...) -> one-line activity row
			timeline.append({
				"type": "system",
				"id": c.name,
				"action": (c.comment_type or "").lower(),
				"sender": c.comment_email,
				"sender_name": sender_name,
				"content": _system_comment_text(c.comment_type, c.content, sender_name),
				"timestamp": c.creation,
			})
			continue

		user_img = frappe.db.get_value("User", c.comment_email, "user_image")
		timeline.append({
			"type": "comment",
			"id": c.name,
			"comment_type": c.comment_type,
			"sender": c.comment_email,
			"sender_name": sender_name,
			"sender_image": user_img,
			"content": _to_display_html(c.content),
			"timestamp": c.creation,
		})

	# 2. Communications (Emails)
	comms = frappe.get_all(
		"Communication",
		filters={"reference_doctype": "Task", "reference_name": task_id},
		fields=[
			"name",
			"communication_type",
			"communication_medium",
			"sender",
			"sender_full_name",
			"recipients",
			"subject",
			"content",
			"creation",
			"sent_or_received",
		],
		order_by="creation desc",
	)
	for cm in comms:
		user_img = frappe.db.get_value("User", cm.sender, "user_image")
		timeline.append({
			"type": "communication",
			"id": cm.name,
			"medium": cm.communication_medium or "Email",
			"direction": cm.sent_or_received,
			"sender": cm.sender,
			"sender_name": cm.sender_full_name or cm.sender,
			"sender_image": user_img,
			"recipients": cm.recipients,
			"subject": cm.subject,
			"content": _to_display_html(cm.content, email=True),
			"timestamp": cm.creation,
		})

	# 3. Document Creation Event
	timeline.append({
		"type": "system",
		"id": f"created-{task_id}",
		"action": "created",
		"sender": doc.owner,
		"sender_name": frappe.db.get_value("User", doc.owner, "full_name") or doc.owner,
		"content": f"Task created in project {task_data.get('project_title') or doc.project}",
		"timestamp": doc.creation,
	})

	# Sort chronological (newest first or oldest first)
	timeline.sort(key=lambda x: str(x["timestamp"]), reverse=True)
	task_data["activity_timeline"] = timeline

	task_data["owner_name"] = frappe.db.get_value("User", doc.owner, "full_name") or doc.owner
	task_data["owner_image"] = frappe.db.get_value("User", doc.owner, "user_image")
	task_data["description_html"] = _to_display_html(doc.description)

	# Real "viewed by" history (Frappe View Log)
	_log_task_view(doc)
	viewers = _get_task_viewers(task_id)
	# The View Log insert is committed after the response, so add the current view directly
	user = frappe.session.user
	if user != "Guest":
		viewers = [v for v in viewers if v["user"] != user]
		viewers.insert(0, {
			"user": user,
			"full_name": frappe.db.get_value("User", user, "full_name") or user,
			"user_image": frappe.db.get_value("User", user, "user_image"),
			"last_viewed": now_datetime(),
		})
		viewers = viewers[:5]
	task_data["viewers"] = viewers

	return task_data


BLOCK_TAG_RE = re.compile(r"<(p|div|br|ul|ol|li|table|blockquote|pre|h[1-6])\b", re.IGNORECASE)


def _to_display_html(content, email=False):
	"""Safe HTML for the activity timeline.

	Notes typed in this app are plain text (keep line breaks); notes from Desk and
	emails are HTML (sanitize to prevent XSS)."""
	if not content:
		return ""
	if not is_html(content):
		return escape_html(content).replace("\n", "<br>")
	cleaned = clean_email_html(content) if email else sanitize_html(
		content, always_sanitize=True, disallowed_tags=["html", "head", "meta", "link", "body", "style"]
	)
	# Plain text with a few inline tags (typed in the composer) -> keep its line breaks
	if not BLOCK_TAG_RE.search(cleaned):
		cleaned = cleaned.strip().replace("\n", "<br>")
	return cleaned


def _system_comment_text(comment_type, content, sender_name):
	"""Readable one-liner for Frappe activity comments, always mentioning who did it."""
	text = _to_plain_text(content)
	if comment_type == "Assigned":
		# "X assigned Y: <document title/name>" -> "X assigned Y"
		text = text.split(":", 1)[0].strip()
	elif comment_type == "Assignment Completed":
		# "Assignment of Y removed by X" -> "X removed assignment of Y"
		match = re.match(r"^Assignment of (.+) removed by (.+?)\.?$", text)
		if match:
			text = f"{match.group(2)} removed assignment of {match.group(1)}"
	elif comment_type == "Attachment":
		text = f"attached {text}"
	elif comment_type == "Attachment Removed":
		text = f"removed attachment {text}"
	if sender_name and not text.startswith(sender_name):
		text = f"{sender_name} {text[:1].lower()}{text[1:]}" if text else sender_name
	return text


def _to_plain_text(content):
	"""Collapse HTML into a single readable line, e.g. 'Administrator assigned bala: demo2'."""
	if not content:
		return ""
	return " ".join(html.unescape(strip_html_tags(content)).split())


VIEW_LOG_THROTTLE_MINUTES = 30


def _log_task_view(doc):
	"""Record a View Log for the current user, at most once per throttle window."""
	user = frappe.session.user
	if user == "Guest":
		return
	recent = frappe.db.exists(
		"View Log",
		{
			"reference_doctype": doc.doctype,
			"reference_name": doc.name,
			"viewed_by": user,
			"creation": [">", add_to_date(now_datetime(), minutes=-VIEW_LOG_THROTTLE_MINUTES)],
		},
	)
	if not recent:
		doc.add_viewed(user=user, force=True)


def _get_task_viewers(task_id, limit=5):
	"""Latest view per user for a task, newest first."""
	rows = frappe.get_all(
		"View Log",
		filters={"reference_doctype": "Task", "reference_name": task_id},
		fields=["viewed_by", {"MAX": "creation", "as": "last_viewed"}],
		group_by="viewed_by",
		order_by="last_viewed desc",
		limit=limit,
		ignore_permissions=True,
	)
	viewers = []
	for row in rows:
		user_info = frappe.db.get_value("User", row.viewed_by, ["full_name", "user_image"], as_dict=True) or {}
		viewers.append({
			"user": row.viewed_by,
			"full_name": user_info.get("full_name") or row.viewed_by,
			"user_image": user_info.get("user_image"),
			"last_viewed": row.last_viewed,
		})
	return viewers


def _ensure_project_dates_accommodate_task(project, exp_start_date=None, exp_end_date=None):
	"""Ensure parent Project start/end dates encompass the task's timeline to prevent ERPNext validation errors."""
	if not project or not frappe.db.exists("Project", project):
		return
	try:
		proj = frappe.db.get_value(
			"Project",
			project,
			["name", "expected_start_date", "expected_end_date"],
			as_dict=True,
		)
		if not proj:
			return

		updates = {}
		if exp_start_date:
			t_start = getdate(exp_start_date)
			if proj.expected_start_date and t_start < getdate(proj.expected_start_date):
				updates["expected_start_date"] = t_start
			elif not proj.expected_start_date:
				updates["expected_start_date"] = t_start

		if exp_end_date:
			t_end = getdate(exp_end_date)
			if proj.expected_end_date and t_end > getdate(proj.expected_end_date):
				updates["expected_end_date"] = t_end
			elif not proj.expected_end_date:
				updates["expected_end_date"] = t_end

		if updates:
			# Ensure expected_start_date <= expected_end_date on Project
			cur_start = updates.get("expected_start_date", proj.expected_start_date)
			cur_end = updates.get("expected_end_date", proj.expected_end_date)
			if cur_start and cur_end and getdate(cur_start) > getdate(cur_end):
				updates["expected_end_date"] = cur_start

			frappe.db.set_value("Project", project, updates, update_modified=False)
			frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Failed to adapt project dates for task: {str(e)}", "Projects App")


@frappe.whitelist()
def create_task(data):
	"""Create a task and assign users."""
	if isinstance(data, str):
		data = json.loads(data)

	subject = data.get("subject")
	if not subject:
		frappe.throw(_("Task subject is required"))

	project = data.get("project")
	exp_start_date = data.get("exp_start_date")
	exp_end_date = data.get("exp_end_date")

	# Ensure task exp_end_date >= exp_start_date
	if exp_start_date and exp_end_date:
		if getdate(exp_end_date) < getdate(exp_start_date):
			exp_end_date = exp_start_date

	if project:
		_ensure_project_dates_accommodate_task(project, exp_start_date, exp_end_date)

	doc = frappe.get_doc({
		"doctype": "Task",
		"subject": subject,
		"project": project,
		"implementation_module": data.get("implementation_module"),
		"priority": data.get("priority") or "Medium",
		"status": data.get("status") or "Open",
		"is_milestone": cint(data.get("is_milestone", 0)),
		"exp_start_date": exp_start_date,
		"exp_end_date": exp_end_date,
		"expected_time": flt(data.get("expected_time", 8)),
		"progress": flt(data.get("progress", 0)),
		"description": data.get("description") or "",
		"client_visible": cint(data.get("client_visible", 1)),
	})
	doc.insert(ignore_permissions=True)

	# Handle assignment
	assigned_users = data.get("assignees") or []
	if assigned_users:
		for user in assigned_users:
			try:
				add_assignment({
					"doctype": "Task",
					"name": doc.name,
					"assign_to": [user],
					"description": f"Assigned to Task: {subject}",
				})
			except Exception:
				pass

	# Add tags
	if data.get("tags"):
		from frappe.desk.doctype.tag.tag import add_tag
		for tag in data.get("tags"):
			if tag.strip():
				add_tag(tag.strip(), "Task", doc.name)

	frappe.db.commit()
	if doc.project:
		_update_project_completion(doc.project)

	return get_task(doc.name)


@frappe.whitelist()
def update_task(task_id, data):
	"""Update task fields and refresh parent project progress."""
	if isinstance(data, str):
		data = json.loads(data)

	doc = frappe.get_doc("Task", task_id)
	old_status = doc.status

	target_project = data.get("project") or doc.project
	target_start = data.get("exp_start_date") or doc.exp_start_date
	target_end = data.get("exp_end_date") or doc.exp_end_date

	if target_start and target_end:
		if getdate(target_end) < getdate(target_start):
			target_end = target_start
			if "exp_end_date" in data:
				data["exp_end_date"] = target_end

	if target_project and (data.get("exp_end_date") or data.get("exp_start_date") or data.get("project")):
		_ensure_project_dates_accommodate_task(target_project, target_start, target_end)

	allowed_fields = [
		"subject", "status", "priority", "progress", "is_milestone",
		"exp_start_date", "exp_end_date", "expected_time", "actual_time",
		"description", "implementation_module", "client_visible", "project"
	]

	for f in allowed_fields:
		if f in data:
			doc.set(f, data[f])

	if "client_poc_name" in data and doc.project:
		frappe.db.set_value("Project", doc.project, "client_poc_name", data["client_poc_name"], update_modified=False)
	if "client_poc_email" in data and doc.project:
		frappe.db.set_value("Project", doc.project, "client_poc_email", data["client_poc_email"], update_modified=False)

	# Automatically update progress to 100 if completed
	if doc.status == "Completed" and old_status != "Completed":
		doc.progress = 100
	elif doc.status == "Open" and doc.progress == 100:
		doc.progress = 0

	doc.save(ignore_permissions=True)

	# Tags
	if "tags" in data:
		from frappe.desk.doctype.tag.tag import add_tag, remove_tag
		existing_tags = set([t for t in (doc._user_tags or "").split(",") if t])
		new_tags = set(data["tags"])
		for t in existing_tags - new_tags:
			remove_tag(t, "Task", task_id)
		for t in new_tags - existing_tags:
			if t.strip():
				add_tag(t.strip(), "Task", task_id)

	frappe.db.commit()

	if doc.project:
		_update_project_completion(doc.project)

	return get_task(task_id)


@frappe.whitelist()
def bulk_update_tasks(task_ids, data):
	"""Bulk update multiple tasks (status, priority, assignee, due date, module, milestone)."""
	if isinstance(task_ids, str):
		task_ids = json.loads(task_ids)
	if isinstance(data, str):
		data = json.loads(data)

	if not task_ids:
		return {"success": False, "message": "No tasks selected"}

	affected_projects = set()

	for task_id in task_ids:
		try:
			doc = frappe.get_doc("Task", task_id)
			old_status = doc.status

			if "status" in data and data["status"]:
				doc.status = data["status"]
				if doc.status == "Completed" and old_status != "Completed":
					doc.progress = 100
				elif doc.status == "Open" and doc.progress == 100:
					doc.progress = 0

			if "priority" in data and data["priority"]:
				doc.priority = data["priority"]

			if "exp_end_date" in data and data["exp_end_date"]:
				doc.exp_end_date = data["exp_end_date"]
				if doc.project:
					_ensure_project_dates_accommodate_task(doc.project, doc.exp_start_date, doc.exp_end_date)

			if "implementation_module" in data and data["implementation_module"]:
				doc.implementation_module = data["implementation_module"]

			if "is_milestone" in data and data["is_milestone"] is not None:
				doc.is_milestone = int(data["is_milestone"])

			if "assigned_to" in data and data["assigned_to"]:
				assignee = data["assigned_to"].strip()
				if assignee:
					from frappe.desk.form.assign_to import add as add_assign
					try:
						add_assign({
							"doctype": "Task",
							"name": task_id,
							"assign_to": [assignee],
							"description": "Bulk assigned task",
						})
					except Exception:
						pass

			doc.save(ignore_permissions=True)
			if doc.project:
				affected_projects.add(doc.project)
		except Exception as e:
			frappe.log_error(f"Failed to bulk update task {task_id}: {str(e)}", "Bulk Update Tasks")

	frappe.db.commit()

	for proj in affected_projects:
		_update_project_completion(proj)

	return {
		"success": True,
		"updated_count": len(task_ids),
	}


@frappe.whitelist()
def bulk_delete_tasks(task_ids):
	"""Bulk delete multiple tasks."""
	if isinstance(task_ids, str):
		task_ids = json.loads(task_ids)

	if not task_ids:
		return {"success": False, "message": "No tasks selected"}

	affected_projects = set()
	for task_id in task_ids:
		try:
			doc = frappe.get_doc("Task", task_id)
			if doc.project:
				affected_projects.add(doc.project)
			frappe.delete_doc("Task", task_id, ignore_permissions=True)
		except Exception:
			pass

	frappe.db.commit()

	for proj in affected_projects:
		_update_project_completion(proj)

	return {
		"success": True,
		"deleted_count": len(task_ids),
	}


@frappe.whitelist()
def quick_update_status(task_id, status):
	"""Quick status update e.g. for Kanban board column drag-and-drop."""
	doc = frappe.get_doc("Task", task_id)
	doc.status = status
	if status == "Completed":
		doc.progress = 100
	doc.save(ignore_permissions=True)
	frappe.db.commit()

	if doc.project:
		_update_project_completion(doc.project)

	return {"success": True, "task_id": task_id, "status": status}


@frappe.whitelist()
def add_comment(task_id, content):
	"""Post comment to task activity feed."""
	if not content or not content.strip():
		frappe.throw(_("Comment cannot be empty"))

	doc = frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Comment",
		"reference_doctype": "Task",
		"reference_name": task_id,
		"content": content,
		"comment_email": frappe.session.user,
		"comment_by": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"type": "comment",
		"id": doc.name,
		"comment_type": "Comment",
		"sender": doc.comment_email,
		"sender_name": doc.comment_by,
		"sender_image": frappe.db.get_value("User", frappe.session.user, "user_image"),
		"content": _to_display_html(doc.content),
		"timestamp": doc.creation,
	}


def _get_own_comment(comment_id):
	"""Return a task Comment the current user may change (author or System Manager)."""
	comment = frappe.get_doc("Comment", comment_id)
	if comment.reference_doctype != "Task" or comment.comment_type != "Comment":
		frappe.throw(_("Only task comments can be changed"), frappe.PermissionError)
	if comment.comment_email != frappe.session.user and "System Manager" not in frappe.get_roles():
		frappe.throw(_("You can only change your own comments"), frappe.PermissionError)
	return comment


@frappe.whitelist(methods=["POST"])
def edit_comment(comment_id, content):
	"""Edit the text of the current user's task comment."""
	if not content or not content.strip():
		frappe.throw(_("Comment cannot be empty"))
	comment = _get_own_comment(comment_id)
	comment.content = content
	comment.save(ignore_permissions=True)
	return {"id": comment.name, "content": _to_display_html(comment.content)}


@frappe.whitelist(methods=["POST"])
def delete_comment(comment_id):
	"""Delete the current user's task comment."""
	comment = _get_own_comment(comment_id)
	frappe.delete_doc("Comment", comment.name, ignore_permissions=True)
	return {"id": comment_id}


@frappe.whitelist()
def send_task_email(task_id, recipients, subject, message):
	"""Send an email regarding the task and log as Communication."""
	if not recipients:
		frappe.throw(_("Recipients are required"))
	if not message:
		frappe.throw(_("Message is required"))

	if isinstance(recipients, str):
		recipient_list = [r.strip() for r in recipients.split(",") if r.strip()]
	else:
		recipient_list = recipients

	task_doc = frappe.get_doc("Task", task_id)
	if not subject:
		subject = f"[{task_doc.name}] {task_doc.subject}"

	# Send email via Frappe mailer
	frappe.sendmail(
		recipients=recipient_list,
		subject=subject,
		message=message,
		reference_doctype="Task",
		reference_name=task_id,
	)

	# Create Communication record
	comm = frappe.get_doc({
		"doctype": "Communication",
		"communication_type": "Communication",
		"communication_medium": "Email",
		"sent_or_received": "Sent",
		"sender": frappe.session.user,
		"sender_full_name": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
		"recipients": ", ".join(recipient_list),
		"subject": subject,
		"content": message,
		"reference_doctype": "Task",
		"reference_name": task_id,
	})
	comm.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"type": "communication",
		"id": comm.name,
		"medium": "Email",
		"direction": "Sent",
		"sender": comm.sender,
		"sender_name": comm.sender_full_name,
		"sender_image": frappe.db.get_value("User", comm.sender, "user_image"),
		"recipients": comm.recipients,
		"subject": comm.subject,
		"content": comm.content,
		"timestamp": comm.creation,
	}


@frappe.whitelist()
def assign_task(task_id, user_email, action="add"):
	"""Assign or unassign user from task, and notify them."""
	if action == "add":
		add_assignment({
			"doctype": "Task",
			"name": task_id,
			"assign_to": [user_email],
			"description": f"Assigned to {task_id}",
		})
	else:
		remove_assignment("Task", task_id, user_email)

	frappe.db.commit()
	return get_task(task_id)


def _update_project_completion(project_name):
	"""Helper to recalculate and store completion percentage on Project and Modules."""
	if not project_name:
		return

	stats = frappe.db.sql(
		"""
		SELECT
			COUNT(*) as total,
			SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
		FROM `tabTask`
		WHERE project = %s
		""",
		project_name,
		as_dict=True,
	)[0]

	total = cint(stats.total)
	completed = cint(stats.completed)
	percent = round((completed / total * 100), 1) if total > 0 else 0

	frappe.db.set_value("Project", project_name, "percent_complete", percent, update_modified=False)

	# Update module progress in child table
	p_doc = frappe.get_doc("Project", project_name)
	for m in p_doc.selected_modules:
		m_stats = frappe.db.sql(
			"""
			SELECT
				COUNT(*) as total,
				SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
			FROM `tabTask`
			WHERE project = %s AND implementation_module = %s
			""",
			(project_name, m.module),
			as_dict=True,
		)[0]
		m_total = cint(m_stats.total)
		m_completed = cint(m_stats.completed)
		m_prog = round((m_completed / m_total * 100), 1) if m_total > 0 else 0
		m.progress = m_prog
		if m_prog == 100:
			m.status = "Completed"
		elif m_prog > 0:
			m.status = "In Progress"

	p_doc.save(ignore_permissions=True)
	frappe.db.commit()


@frappe.whitelist()
def get_notifications(limit=30):
	"""Return notification logs with unread count and user details."""
	user = frappe.session.user
	filters = {}
	if user and user not in ("Guest", "Administrator"):
		filters["for_user"] = user

	logs = frappe.get_all(
		"Notification Log",
		filters=filters,
		fields=[
			"name",
			"subject",
			"email_content",
			"document_type",
			"document_name",
			"from_user",
			"type",
			"read",
			"creation",
		],
		order_by="creation desc",
		limit_page_length=cint(limit) or 30,
	)

	user_cache = {}
	for log in logs:
		sender = log.get("from_user")
		if sender:
			if sender not in user_cache:
				user_cache[sender] = {
					"name": frappe.db.get_value("User", sender, "full_name") or sender,
					"image": frappe.db.get_value("User", sender, "user_image"),
				}
			log["from_user_name"] = user_cache[sender]["name"]
			log["from_user_image"] = user_cache[sender]["image"]
		else:
			log["from_user_name"] = "System"
			log["from_user_image"] = None

		# If subject is raw HTML with strong tags, clean or keep
		try:
			from frappe.utils import pretty_date
			log["pretty_time"] = pretty_date(log["creation"])
		except Exception:
			log["pretty_time"] = str(log["creation"])

	unread_filters = {"read": 0}
	if user and user not in ("Guest", "Administrator"):
		unread_filters["for_user"] = user

	unread_count = frappe.db.count("Notification Log", filters=unread_filters)

	return {
		"notifications": logs,
		"unread_count": unread_count,
	}


@frappe.whitelist()
def mark_notification_read(notification_id):
	"""Mark single notification log as read."""
	if frappe.db.exists("Notification Log", notification_id):
		frappe.db.set_value("Notification Log", notification_id, "read", 1, update_modified=False)
		frappe.db.commit()
	return {"success": True}


@frappe.whitelist()
def mark_all_notifications_read():
	"""Mark all notifications as read for current user."""
	user = frappe.session.user
	filters = {"read": 0}
	if user and user not in ("Guest", "Administrator"):
		filters["for_user"] = user

	unread_names = frappe.get_all("Notification Log", filters=filters, pluck="name")
	for name in unread_names:
		frappe.db.set_value("Notification Log", name, "read", 1, update_modified=False)
	frappe.db.commit()

	return {"success": True, "marked_count": len(unread_names)}


@frappe.whitelist()
def global_search(query):
	"""Global command palette search across Tasks, Projects, and Modules."""
	if not query or len(query.strip()) < 1:
		return {"tasks": [], "projects": [], "modules": []}

	q = query.strip()

	# 1. Search Tasks
	tasks = frappe.get_all(
		"Task",
		or_filters=[
			["subject", "like", f"%{q}%"],
			["name", "like", f"%{q}%"],
			["project", "like", f"%{q}%"],
		],
		fields=["name", "subject", "project", "status", "priority", "implementation_module"],
		limit_page_length=6,
	)

	# 2. Search Projects
	projects = frappe.get_all(
		"Project",
		or_filters=[
			["project_name", "like", f"%{q}%"],
			["name", "like", f"%{q}%"],
			["client_poc_name", "like", f"%{q}%"],
		],
		fields=["name", "project_name", "status", "percent_complete", "client_poc_name"],
		limit_page_length=5,
	)

	# 3. Search Modules
	modules = frappe.get_all(
		"Implementation Module",
		or_filters=[
			["module_name", "like", f"%{q}%"],
			["module_code", "like", f"%{q}%"],
		],
		fields=["name", "module_name", "module_code", "icon", "color"],
		limit_page_length=4,
	)

	return {
		"tasks": tasks,
		"projects": projects,
		"modules": modules,
	}

