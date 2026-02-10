from unittest import result
from supabase import create_client, Client

supabase_url = "https://figubkupxgxcrxtvsoji.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpZ3Via3VweGd4Y3J4dHZzb2ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjAyNjk4NTksImV4cCI6MjAzNTg0NTg1OX0.049XyTPGjxGqliuBWnk1HWEBypP_J76h73qfLwCQxpw"
supabase = create_client(supabase_url, supabase_key)

# Connect to Supabase
scaleschema = "scale"
sb = supabase.schema(scaleschema)

"""
Tables:

supplies:    		Vendor, Dept, Descr, size
suppliesvendors:	VendorName, Status
suppliesdept:		Dept
suppliesordered:	VendorName, Descr, Size, Qty, OrderDate, ReceiveDate
"""

def LoadVendors():
    res = (sb.table("suppliesvendors").select("VendorName, Status").eq("Status", "Active").order("VendorName").execute())
    vendors = res.data or []
    result = []
    for v in vendors:
        vendor_name = v.get("VendorName")
        label = vendor_name if vendor_name else ""
        result.append((label))
    return ["Select"] + result

def LoadDepts():
    res = sb.table("suppliesdept").select("Dept").order("Dept").execute()
    depts = res.data or []
    result = []
    for d in depts:
        dept_name = d.get("Dept")
        label = dept_name if dept_name else ""
        result.append((label))
    return ["Select"] + result

def LoadSupplies(vendor: str, dept: str):
    q = sb.table("supplies").select("Descr, Size").order("Descr").order("Size")
    if vendor != "Select":
        q = q.eq("Vendor", vendor)
    if dept != "Select":
        q = q.eq("Dept", dept)
    res = q.execute()
    supplies = res.data or []
    result = []
    for s in supplies:
        descr = s.get("Descr") or ""
        size = s.get("Size") or ""
        label = f"{descr} - {size}" if size else descr
        result.append((label))
    return ["Select"] + result

def InsertVendor(vendor_name: str):
    ins = {"VendorName": vendor_name, "Status": "Active"}
    res = sb.table("suppliesvendors").insert(ins, returning="representation").execute()
    return res.data[0]

def InsertDept(dept_name: str):
    ins = {"Dept": dept_name}
    res = sb.table("suppliesdept").insert(ins, returning="representation").execute()
    return res.data[0]  

def InsertSupply(vendor: str, dept: str, descr: str, size: str):
    ins = {"Vendor": vendor, "Dept": dept, "Descr": descr, "Size": size}
    res = sb.table("supplies").insert(ins, returning="representation").execute()
    return res.data[0]

def InsertOrder(vendor_name: str, descr: str, size: str, qty: int, order_date: str):
    ins = {
        "VendorName": vendor_name,
        "Descr": descr,
        "Size": size,
        "Qty": qty,
        "OrderDate": order_date
    }
    res = sb.table("suppliesordered").insert(ins, returning="representation").execute()
    return res.data[0]

def GetOpenOrders():
    q = sb.table("suppliesordered").select("*").order("OrderDate", desc=True).is_("ReceiveDate", None)
    res = q.execute()
    return res.data or []

def UpdateOrder(order_id: int, receive_date: str):
    upd = {"ReceiveDate": receive_date}
    res = sb.table("suppliesordered").update(upd, returning="representation").eq("id", order_id).execute()
    return res.data[0]

def GetSupplies(vendor_filter: str, dept_filter: str):
    q = sb.table("supplies").select("Vendor, Dept, Descr, Size").order("Vendor").order("Descr").order("Size")
    if vendor_filter != "Select":
        q = q.eq("Vendor", vendor_filter)
    if dept_filter != "Select":
        q = q.eq("Dept", dept_filter)
    
    res = q.execute()
    supplies = res.data or []
    return supplies

def ViewSupplies(vendor_filter: str, dept_filter: str, order_status: str):
    """Get supply orders with optional filters for vendor, dept, and order status.
    
    Args:
        vendor_filter: Vendor name or "Any" for all vendors
        dept_filter: Department name or "Any" for all departments
        order_status: "All", "Pending", or "Completed"
    
    Returns:
        List of order dictionaries with id, VendorName, Dept, Descr, Size, Qty, OrderDate, ReceiveDate
    """
    # Build query for orders
    q = sb.table("suppliesordered").select("id, VendorName, Descr, Size, Qty, OrderDate, ReceiveDate").order("OrderDate", desc=True)
    
    # Apply status filter
    if order_status == "Pending":
        q = q.is_("ReceiveDate", None)
    elif order_status == "Completed":
        q = q.not_.is_("ReceiveDate", None)
    # "All" means no filter on ReceiveDate
    
    # Apply vendor filter
    if vendor_filter != "Any" and vendor_filter != "Select":
        q = q.eq("VendorName", vendor_filter)
    
    res = q.execute()
    orders = res.data or []
    
    # For each order, get the Dept from the supplies table
    result = []
    for order in orders:
        vendor_name = order.get("VendorName", "")
        descr = order.get("Descr", "")
        size = order.get("Size", "")
        
        # Get dept from supplies table
        supply_q = sb.table("supplies").select("Dept").eq("Vendor", vendor_name).eq("Descr", descr).eq("Size", size).limit(1)
        supply_res = supply_q.execute()
        supply_data = supply_res.data or []
        dept_name = supply_data[0].get("Dept", "") if supply_data else ""
        
        # Apply dept filter
        if dept_filter != "Any" and dept_filter != "Select" and dept_name != dept_filter:
            continue
        
        # Add dept to order data
        order_with_dept = dict(order)
        order_with_dept["Dept"] = dept_name
        result.append(order_with_dept)
    
    return result


#res = GetOpenOrders()
#print(res)

