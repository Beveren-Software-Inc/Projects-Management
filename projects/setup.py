# Copyright (c) 2026, Beveren Software and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
	setup_custom_fields()
	seed_default_modules_and_templates()


def after_migrate():
	setup_custom_fields()
	seed_default_modules_and_templates()


def setup_custom_fields():
	"""Create custom fields on core Project and Task DocTypes."""
	custom_fields = {
		"Project": [
			{
				"fieldname": "client_poc_name",
				"label": "Client Point of Contact",
				"fieldtype": "Data",
				"insert_after": "customer",
				"in_list_view": 0,
			},
			{
				"fieldname": "client_poc_email",
				"label": "Client Email",
				"fieldtype": "Data",
				"options": "Email",
				"insert_after": "client_poc_name",
			},
			{
				"fieldname": "client_poc_phone",
				"label": "Client Phone",
				"fieldtype": "Data",
				"insert_after": "client_poc_email",
			},
			{
				"fieldname": "partner_poc",
				"label": "Partner Point of Contact",
				"fieldtype": "Link",
				"options": "User",
				"insert_after": "client_poc_phone",
			},
			{
				"fieldname": "project_manager",
				"label": "Project Manager",
				"fieldtype": "Link",
				"options": "User",
				"insert_after": "partner_poc",
			},
			{
				"fieldname": "implementation_stage",
				"label": "Implementation Stage",
				"fieldtype": "Select",
				"options": "Discovery\nDesign\nConfiguration & Customization\nData Migration\nUAT & Training\nGo-Live\nHypercare Support\nClosed",
				"default": "Discovery",
				"insert_after": "project_manager",
			},
			{
				"fieldname": "auto_emails",
				"label": "Enable Auto Emails to Client",
				"fieldtype": "Check",
				"default": "1",
				"insert_after": "implementation_stage",
			},
			{
				"fieldname": "selected_modules",
				"label": "Implementation Modules",
				"fieldtype": "Table",
				"options": "Project Implementation Module",
				"insert_after": "auto_emails",
			},
			{
				"fieldname": "project_health",
				"label": "Project Health",
				"fieldtype": "Select",
				"options": "On Track\nNeeds Attention\nAt Risk",
				"default": "On Track",
				"insert_after": "selected_modules",
			},
			{
				"fieldname": "health_notes",
				"label": "Health Notes & Summary",
				"fieldtype": "Small Text",
				"insert_after": "project_health",
			},
			{
				"fieldname": "auto_weekly_update",
				"label": "Automate Weekly Updates",
				"fieldtype": "Check",
				"default": "1",
				"insert_after": "health_notes",
			},
			{
				"fieldname": "auto_monthly_feedback",
				"label": "Automate Monthly Feedback Survey",
				"fieldtype": "Check",
				"default": "1",
				"insert_after": "auto_weekly_update",
			},
			{
				"fieldname": "last_weekly_update_sent",
				"label": "Last Weekly Update Sent",
				"fieldtype": "Datetime",
				"insert_after": "auto_monthly_feedback",
			},
			{
				"fieldname": "last_feedback_survey_sent",
				"label": "Last Feedback Survey Sent",
				"fieldtype": "Datetime",
				"insert_after": "last_weekly_update_sent",
			},
			{
				"fieldname": "customer_feedback_score",
				"label": "Customer Feedback Score",
				"fieldtype": "Select",
				"options": "5 - Exceptional\n4 - Satisfied\n3 - Neutral\n2 - Needs Improvement\n1 - Critical",
				"insert_after": "last_feedback_survey_sent",
			},
			{
				"fieldname": "customer_feedback_notes",
				"label": "Customer Feedback Notes",
				"fieldtype": "Small Text",
				"insert_after": "customer_feedback_score",
			},
			{
				"fieldname": "governance_data",
				"label": "Project Governance Data",
				"fieldtype": "Long Text",
				"insert_after": "customer_feedback_notes",
			},
		],
		"Task": [
			{
				"fieldname": "implementation_module",
				"label": "Implementation Module",
				"fieldtype": "Link",
				"options": "Implementation Module",
				"insert_after": "project",
				"in_list_view": 1,
				"in_standard_filter": 1,
			},
			{
				"fieldname": "client_visible",
				"label": "Visible to Client",
				"fieldtype": "Check",
				"default": "1",
				"insert_after": "implementation_module",
			},
		],
	}

	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()


def seed_default_modules_and_templates():
	"""Seed comprehensive ERPNext implementation modules and standard task templates."""
	modules_data = [
		{
			"module_name": "Accounts & Finance",
			"module_code": "accounts",
			"color": "#10B981", # Emerald
			"icon": "CreditCard",
			"sequence_order": 1,
			"description": "Chart of Accounts, banking, tax templates, cost centers, payment terms, and financial reporting.",
			"tasks": [
				{
					"subject": "Chart of Accounts Architecture & Review",
					"description": "Define and configure Chart of Accounts hierarchy, account types, and currency setup matching client financial structure.",
					"day_offset": 1,
					"duration_days": 3,
					"expected_hours": 12,
					"priority": "High",
					"is_milestone": 0,
				},
				{
					"subject": "Cost Centers & Accounting Dimensions",
					"description": "Setup departmental cost centers, project dimensions, and budgeting rules.",
					"day_offset": 4,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Tax Templates & Withholding Setup",
					"description": "Configure sales & purchase tax charges templates, GST / VAT compliance settings, and withholding tax categories.",
					"day_offset": 6,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "High",
					"is_milestone": 0,
				},
				{
					"subject": "Bank Accounts, Payment Modes & Terms",
					"description": "Create bank ledgers, bank clearance rules, payment gateways, and credit payment terms templates.",
					"day_offset": 8,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Opening Balance Verification & Journal Entry",
					"description": "Prepare, validate and post opening balance journal vouchers for trial balance sign-off.",
					"day_offset": 10,
					"duration_days": 3,
					"expected_hours": 16,
					"priority": "Urgent",
					"is_milestone": 1,
				},
				{
					"subject": "Accounts UAT & Finance Sign-Off",
					"description": "Conduct end-to-end user acceptance testing for billing, payment entries, ledger reconciliations, and financial statements.",
					"day_offset": 13,
					"duration_days": 2,
					"expected_hours": 10,
					"priority": "High",
					"is_milestone": 1,
				},
			],
		},
		{
			"module_name": "Buying & Procurement",
			"module_code": "buying",
			"color": "#F59E0B", # Amber
			"icon": "ShoppingCart",
			"sequence_order": 2,
			"description": "Supplier management, purchase requisitions, RFQ, purchase orders, and supplier scorecards.",
			"tasks": [
				{
					"subject": "Supplier Groups & Supplier Master Import",
					"description": "Cleanse and upload supplier masters, supplier classification, tax IDs, and default payment terms.",
					"day_offset": 3,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Procurement Flow & Approval Matrix",
					"description": "Configure Material Request -> RFQ -> Supplier Quotation -> Purchase Order workflow and purchase approval thresholds.",
					"day_offset": 5,
					"duration_days": 3,
					"expected_hours": 12,
					"priority": "High",
					"is_milestone": 0,
				},
				{
					"subject": "Purchase Pricing Rules & Landed Cost Setup",
					"description": "Configure supplier pricing rules, discount structures, freight & customs landed cost allocation.",
					"day_offset": 8,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Procurement Flow UAT & Sign-Off",
					"description": "Perform procurement test cycles including PO generation, goods receipt note matching, and purchase invoice three-way matching.",
					"day_offset": 11,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "High",
					"is_milestone": 1,
				},
			],
		},
		{
			"module_name": "Selling & Order Management",
			"module_code": "selling",
			"color": "#3B82F6", # Blue
			"icon": "TrendingUp",
			"sequence_order": 3,
			"description": "Customer masters, quotation, sales order, delivery notes, sales commissions, and pricing rules.",
			"tasks": [
				{
					"subject": "Customer Groups, Territories & Master Data Import",
					"description": "Setup customer group tree, sales territories, sales persons, and import customer database.",
					"day_offset": 3,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Sales Workflow & Order Management Setup",
					"description": "Configure Quotation -> Sales Order -> Delivery Note -> Sales Invoice cycle, credit limit checks, and delivery stop rules.",
					"day_offset": 5,
					"duration_days": 3,
					"expected_hours": 12,
					"priority": "High",
					"is_milestone": 0,
				},
				{
					"subject": "Price Lists, Discounts & Promotion Rules",
					"description": "Configure selling price lists, item discounts, promotional pricing rules, and sales partner commissions.",
					"day_offset": 8,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Sales Print Formats & Auto Notification Alerts",
					"description": "Design custom print formats for quotations and invoices, and configure email/WhatsApp dispatch notifications.",
					"day_offset": 10,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Sales Flow UAT & Sign-Off",
					"description": "Simulate end-to-end sales transactions with sales team and secure formal user sign-off.",
					"day_offset": 12,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "High",
					"is_milestone": 1,
				},
			],
		},
		{
			"module_name": "Stock & Inventory Management",
			"module_code": "stock",
			"color": "#8B5CF6", # Violet
			"icon": "Package",
			"sequence_order": 4,
			"description": "Warehouses, item master, valuation (FIFO/Moving Avg), batch/serial tracking, and stock reconciliations.",
			"tasks": [
				{
					"subject": "Warehouse Tree & Hierarchy Setup",
					"description": "Structure multi-level warehouse hierarchy including Transit, Scrap, Quarantine, and Finished Goods warehouses.",
					"day_offset": 2,
					"duration_days": 2,
					"expected_hours": 6,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "UOMs & Item Master Data Cleansing",
					"description": "Setup base and conversion UOMs, item attributes, variants, barcodes, and upload verified item masters.",
					"day_offset": 4,
					"duration_days": 4,
					"expected_hours": 16,
					"priority": "High",
					"is_milestone": 0,
				},
				{
					"subject": "Serial & Batch Tracking Configuration",
					"description": "Configure batch numbering rules, expiry date monitoring, and individual serial number tracking where applicable.",
					"day_offset": 8,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Opening Stock Take & Stock Entry",
					"description": "Conduct physical count cut-off, prepare opening valuation sheets, and post opening stock reconciliation entry.",
					"day_offset": 10,
					"duration_days": 3,
					"expected_hours": 16,
					"priority": "Urgent",
					"is_milestone": 1,
				},
				{
					"subject": "Stock Transfer, Delivery & Inventory UAT",
					"description": "Test inter-warehouse stock transfers, return processing, and real-time ledger balance updates.",
					"day_offset": 13,
					"duration_days": 2,
					"expected_hours": 10,
					"priority": "High",
					"is_milestone": 1,
				},
			],
		},
		{
			"module_name": "HRMS & Payroll",
			"module_code": "hrms",
			"color": "#EC4899", # Pink
			"icon": "Users",
			"sequence_order": 5,
			"description": "Employee lifecycle, leave management, attendance shifts, salary structures, and monthly payroll processing.",
			"tasks": [
				{
					"subject": "Company Org Structure, Branches & Designations",
					"description": "Configure departments, designations, branches, and organizational reporting hierarchy.",
					"day_offset": 2,
					"duration_days": 2,
					"expected_hours": 6,
					"priority": "Low",
					"is_milestone": 0,
				},
				{
					"subject": "Employee Master & Document Data Import",
					"description": "Import employee records, personal data, bank accounts, emergency contacts, and statutory IDs.",
					"day_offset": 4,
					"duration_days": 3,
					"expected_hours": 12,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Leave Types, Holiday Lists & Leave Policy Allocation",
					"description": "Define annual leave, sick leave, maternity policies, holiday lists, and allocate opening leave balances.",
					"day_offset": 7,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Attendance Shifts & Biometric Integration",
					"description": "Configure shift types, check-in rules, grace periods, and configure biometric device checkin sync.",
					"day_offset": 9,
					"duration_days": 3,
					"expected_hours": 12,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Salary Components, Structures & Payroll Run",
					"description": "Setup earnings and deductions, tax slabs, create employee salary structures, and execute test payroll batch.",
					"day_offset": 12,
					"duration_days": 3,
					"expected_hours": 14,
					"priority": "High",
					"is_milestone": 1,
				},
				{
					"subject": "HR & Payroll UAT & Sign-Off",
					"description": "Verify payslip generation, bank payment exports, leave applications, and obtain HR sign-off.",
					"day_offset": 15,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "High",
					"is_milestone": 1,
				},
			],
		},
		{
			"module_name": "CRM & Pipeline Management",
			"module_code": "crm",
			"color": "#6366F1", # Indigo
			"icon": "Target",
			"sequence_order": 6,
			"description": "Leads, deals/opportunities, lead sources, email integration, and sales pipeline analytics.",
			"tasks": [
				{
					"subject": "Lead Sources, Statuses & Custom Fields Setup",
					"description": "Define lead stages, qualification criteria, custom intake fields, and lost reasons.",
					"day_offset": 3,
					"duration_days": 2,
					"expected_hours": 6,
					"priority": "Low",
					"is_milestone": 0,
				},
				{
					"subject": "Lead Assignment Rules & Email Ingestion",
					"description": "Configure round-robin assignment rules for incoming web leads and configure team email inboxes.",
					"day_offset": 5,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Opportunity Pipeline & Conversion Flow",
					"description": "Setup opportunity sales stages, probability rates, and seamless quotation creation flow.",
					"day_offset": 7,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "CRM UAT & Sales Pipeline Sign-Off",
					"description": "Test lead capture, status progression, email logging, and sales pipeline reporting.",
					"day_offset": 9,
					"duration_days": 2,
					"expected_hours": 6,
					"priority": "Medium",
					"is_milestone": 1,
				},
			],
		},
		{
			"module_name": "Manufacturing (MRP)",
			"module_code": "manufacturing",
			"color": "#059669", # Green
			"icon": "Cpu",
			"sequence_order": 7,
			"description": "Workstations, operations, multi-level BOMs, production planning, work orders, and job cards.",
			"tasks": [
				{
					"subject": "Workstations & Production Operations Setup",
					"description": "Define production stations, hourly operating costs, capacity limits, and operation master catalog.",
					"day_offset": 4,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Bill of Materials (BOM) Architecture",
					"description": "Create single-level and multi-level BOMs, scrap items, operational routing, and cost estimations.",
					"day_offset": 6,
					"duration_days": 4,
					"expected_hours": 16,
					"priority": "High",
					"is_milestone": 0,
				},
				{
					"subject": "Production Plan & Work Order Workflow",
					"description": "Configure Production Planning tool, raw material reservation, work order release, and job card logging.",
					"day_offset": 10,
					"duration_days": 3,
					"expected_hours": 12,
					"priority": "High",
					"is_milestone": 0,
				},
				{
					"subject": "Manufacturing UAT & Production Floor Sign-Off",
					"description": "Execute pilot manufacturing run from raw material issue to finished goods receipt and scrap reconciliation.",
					"day_offset": 13,
					"duration_days": 3,
					"expected_hours": 12,
					"priority": "High",
					"is_milestone": 1,
				},
			],
		},
		{
			"module_name": "Helpdesk & Customer Support",
			"module_code": "helpdesk",
			"color": "#06B6D4", # Cyan
			"icon": "LifeBuoy",
			"sequence_order": 8,
			"description": "Support tickets, SLA agreements, service level priority, knowledge base, and customer portal.",
			"tasks": [
				{
					"subject": "Support Ticket Types & SLA Service Levels",
					"description": "Define ticket priorities, first response and resolution SLA policies, and business hour schedules.",
					"day_offset": 4,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Support Inboxes & Auto-Assignment Configuration",
					"description": "Integrate support email inboxes (IMAP/OAuth) and setup automated ticket routing to agent groups.",
					"day_offset": 6,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Helpdesk Workflow Testing & Sign-Off",
					"description": "Test ticket submission, agent communications, resolution sign-off, and customer satisfaction surveys.",
					"day_offset": 8,
					"duration_days": 2,
					"expected_hours": 6,
					"priority": "Medium",
					"is_milestone": 1,
				},
			],
		},
		{
			"module_name": "Asset Management",
			"module_code": "assets",
			"color": "#64748B", # Slate
			"icon": "Server",
			"sequence_order": 9,
			"description": "Fixed assets, asset categories, depreciation schedules, maintenance logs, and asset movements.",
			"tasks": [
				{
					"subject": "Asset Categories & Depreciation Methods",
					"description": "Configure asset categories, depreciation methods (straight-line, written-down value), and depreciation accounts.",
					"day_offset": 5,
					"duration_days": 2,
					"expected_hours": 8,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Asset Master & Opening Value Upload",
					"description": "Upload existing fixed assets, gross purchase values, accumulated depreciation, and asset custodians.",
					"day_offset": 7,
					"duration_days": 3,
					"expected_hours": 10,
					"priority": "Medium",
					"is_milestone": 0,
				},
				{
					"subject": "Depreciation Schedule Test & Sign-Off",
					"description": "Validate automated depreciation entry generation and asset disposal/sale workflow.",
					"day_offset": 10,
					"duration_days": 2,
					"expected_hours": 6,
					"priority": "Medium",
					"is_milestone": 1,
				},
			],
		},
	]

	for mod in modules_data:
		doc_name = mod["module_code"]
		if frappe.db.exists("Implementation Module", doc_name):
			doc = frappe.get_doc("Implementation Module", doc_name)
			doc.module_name = mod["module_name"]
			doc.color = mod["color"]
			doc.icon = mod["icon"]
			doc.sequence_order = mod["sequence_order"]
			doc.description = mod["description"]
			# Update tasks if empty
			if not doc.tasks:
				for task in mod["tasks"]:
					doc.append("tasks", task)
			doc.save(ignore_permissions=True)
		else:
			doc = frappe.get_doc({
				"doctype": "Implementation Module",
				"module_name": mod["module_name"],
				"module_code": mod["module_code"],
				"color": mod["color"],
				"icon": mod["icon"],
				"sequence_order": mod["sequence_order"],
				"description": mod["description"],
				"is_active": 1,
				"tasks": mod["tasks"]
			})
			doc.insert(ignore_permissions=True)

	frappe.db.commit()

