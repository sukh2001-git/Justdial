import frappe
import json
from frappe import _

@frappe.whitelist()
def capture_lead(**kwargs):
    """
    API endpoint to capture lead data from external source.
    Handles both regular form data and JSON payloads.
    If phone exists, updates the lead, otherwise creates a new one.
    """
    try:
        if frappe.request and frappe.request.data:
            try:
                data = json.loads(frappe.request.data)
            except:
                data = frappe.form_dict
        else:
            data = frappe.form_dict
        
        frappe.log_error("Received justdial data", data)
        
        mobile = data.get("mobile", "")
        phone = data.get("phone", "")
        
        # Check if lead with this phone number already exists
        existing_lead = None
        
        if mobile:
            existing_lead = frappe.db.get_value("Lead", {"mobile_no": mobile}, "name")
            
        if not existing_lead and phone:
            existing_lead = frappe.db.get_value("Lead", {"phone": phone}, "name")
        
        if existing_lead:
            # Updating existing lead
            lead = frappe.get_doc("Lead", existing_lead)
            frappe.log_error("Found existing lead", lead.name)
        else:
            # Create new lead
            lead = frappe.new_doc("Lead")
            
        # Update lead fields
        lead.lead_name = data.get("name", "")
        lead.company_name = data.get("company", "")
        lead.mobile_no = mobile
        lead.phone = phone
        lead.email_id = data.get("email", "")
        lead.source = "Justdial"
        lead.city = data.get("city", "")
        lead.type_of_lead = data.get("leadtype", "")
        lead.category = data.get("category", "")
        lead.area = data.get("area", "")
        lead.branch_area = data.get("brancharea", "")
        lead.pincode = data.get("pincode", "")
        lead.branch_pin = data.get("branchpin", "")
        lead.date = data.get("date", "")
        lead.time = data.get("time", "")
        
        if existing_lead:
            lead.save(ignore_permissions=True)
            frappe.log_error("Lead updated successfully", lead.as_dict())
        else:
            lead.insert(ignore_permissions=True)
            frappe.log_error("New lead created successfully", lead.as_dict())
            
        frappe.db.commit()
        
        return "RECEIVED"
        
    except Exception as e:
        frappe.log_error("Error processing lead", str(e))
        frappe.db.rollback()
        return "ERROR"