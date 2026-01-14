from unittest import result
from supabase import create_client, Client

supabase_url = "https://figubkupxgxcrxtvsoji.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpZ3Via3VweGd4Y3J4dHZzb2ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjAyNjk4NTksImV4cCI6MjAzNTg0NTg1OX0.049XyTPGjxGqliuBWnk1HWEBypP_J76h73qfLwCQxpw"
supabase = create_client(supabase_url, supabase_key)

# Connect to Supabase
scaleschema = "scale"
sb = supabase.schema(scaleschema)


def GetSopActivities():
    """
    Returns ordered list of unique SOP Activity folder names
    from table: sopindex(Activity, SeqNo, FileName, Descr)
    """
    resp = (
        sb.table("sopindex")
        .select("Activity")
        .order("Activity")
        .execute()
    )

    if not resp.data:
        return []

    # De-duplicate while preserving order
    activities = []
    for row in resp.data:
        act = row["Activity"]
        if act not in activities:
            activities.append(act)

    return activities

def GetSopFiles(activity: str):
    """
    Returns ordered list of SOP files for given activity
    from table: sopindex(Activity, SeqNo, FileName, Descr)
    """
    resp = (
        sb.table("sopindex")
        .select("FileName, Descr")
        .eq("Activity", activity)
        .order("SeqNo")
        .execute()
    )

    if not resp.data:
        return []

    files = []
    for row in resp.data:
        files.append((row["FileName"], row["Descr"]))

    return files

def InsertSopIndex(activity: str, seq_no: int, file_name: str, descr: str):
    """
    Inserts a new SOP index record into sopindex table
    """
    print(f"Inserting SOP Index: Activity={activity}, SeqNo={seq_no}, FileName={file_name}, Descr={descr}")
    ins = {
        "Activity": activity,
        "SeqNo": seq_no,
        "FileName": file_name,
        "Descr": descr
    }
    resp = sb.table("sopindex").insert(ins).execute()
    return resp.data[0]

def GetOneSopFile(activity: str, file_name: str):
    """
    Returns one SOP file record from sopindex table
    """
    resp = (
        sb.table("sopindex")
        .select("Activity, SeqNo, FileName, Descr")
        .eq("Activity", activity)
        .eq("FileName", file_name)
        .execute()
    )

    if resp.data and len(resp.data) > 0:
        return resp.data[0]
    else:
        return None

def UpdateSopIndex(activity: str, file_name: str, seq_no: int, descr: str):
    """
    Updates the description of an existing SOP index record
    """
    resp = (
        sb.table("sopindex")
        .update({"Descr": descr, "SeqNo": seq_no})
        .eq("Activity", activity)
        .eq("FileName", file_name)
        .execute()
    )
    return resp.data

#r = GetOneSopFile("Harvest", "WeighHarvest.md")
#print(r)
