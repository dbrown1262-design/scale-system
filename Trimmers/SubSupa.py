from unittest import result
from supabase import create_client, Client

supabase_url = "https://figubkupxgxcrxtvsoji.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpZ3Via3VweGd4Y3J4dHZzb2ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjAyNjk4NTksImV4cCI6MjAzNTg0NTg1OX0.049XyTPGjxGqliuBWnk1HWEBypP_J76h73qfLwCQxpw"
supabase = create_client(supabase_url, supabase_key)

# Connect to Supabase
scaleschema = "scale"
sb = supabase.schema(scaleschema)

def LoadCrops():
    res = (sb.table("scalecrops").select("CropNo, HarvestDate, CropStat")
            .eq("CropStat", "Active").order("CropNo", desc=True).execute())
    crops = res.data or []
    result = []
    for c in crops:
        crop_no = c.get("CropNo")
        date = c.get("HarvestDate")
        label = f"{crop_no} - {date}" if date else str(crop_no)
        result.append((label))
    return ["Select"] + result


def LoadStrains(crop_no: int):
    res = sb.schema("scale").table("scaleplants").select("Strain").eq("CropNo", crop_no).execute()
    strains = sorted({row["Strain"] for row in res.data if row.get("Strain")}) if res.data else []
    return ["Select"] + strains

def LoadTrimmers():
    res = sb.schema("scale").table("scaletrimmers").select("TrimmerName").eq("TrimmerStat", 'Active').execute()
    trimmers = sorted({row["TrimmerName"] for row in res.data if row.get("TrimmerName")}) if res.data else []
    return ["Select"] + trimmers

def SaveTrimmer(trimmer, flower_grams, smalls_grams, crop_no, strain, trimdate, ampm, StartTime, EndTime):
    res = (sb.schema("scale")
        .table("dailytrim")
        .select("FlowerGrams", "SmallsGrams")
        .eq("TrimmerName", trimmer).eq("TrimDate", trimdate)
        .eq("CropNo", int(crop_no)).eq("Strain", strain).eq("AmPm", ampm)
        .execute())
    existing_flower = 0.0
    existing_smalls = 0.0
    if res.data:
        if res.data[0]:
           existing_flower = float(res.data[0].get("FlowerGrams") or 0.0)
           existing_smalls = float(res.data[0].get("SmallsGrams") or 0.0)
        if flower_grams == 0:
            flower_grams = existing_flower
        if smalls_grams == 0:
            smalls_grams = existing_smalls
        upd = {
            "FlowerGrams": flower_grams,
            "SmallsGrams": smalls_grams,
        }
        (sb.schema("scale").table("dailytrim").update(upd).eq("TrimmerName", trimmer)
         .eq("TrimDate", trimdate).eq("AmPm", ampm).execute())
    else:
        sb.schema("scale").table("dailytrim").insert({
            "TrimmerName": trimmer,
            "TrimDate": trimdate.isoformat(),
            "CropNo": int(crop_no),
            "Strain": strain,
            "FlowerGrams": flower_grams,
            "SmallsGrams": smalls_grams,
            "AmPm": ampm,
            "StartTime": StartTime,
            "EndTime": EndTime, 
        }).execute()



def GetTrimmers():
    Order = [{"column": "TrimmerStat"}, {"column": "TrimmerName"}]
    res = sb.schema("scale").table("scaletrimmers").select("id,TrimmerName,TrimmerStat").order("TrimmerStat").order("TrimmerName").execute()
    return res.data or []

def AddTrimmer(trimmer_name: str, trimmer_stat: str):
    ins = {"TrimmerName": trimmer_name, "TrimmerStat": trimmer_stat}
    res = sb.schema("scale").table("scaletrimmers").insert(ins, returning="representation").execute()
    return res.data[0]

def UpdateTrimmer(row_id: int, trimmer_name: str, trimmer_stat: str):
    upd = {"TrimmerName": trimmer_name, "TrimmerStat": trimmer_stat}
    res = sb.schema("scale").table("scaletrimmers").update(upd, returning="representation").eq("id", row_id).execute()
    return res.data[0]

def GetTrimmerList():
    """
    Returns a list of active trimmer names ordered by name.
    Expects table: scale.scaletrimmers with fields TrimmerName, TrimmerStat ('Active'/'Inactive')
    """
    res = (
        sb.schema("scale")
        .table("scaletrimmers")
        .select("TrimmerName,TrimmerStat")
        .eq("TrimmerStat", "Active")
        .order("TrimmerName")
        .execute()
    )
    data = res.data or []
    # unique, ordered names
    names = []
    seen = set()
    for r in data:
        name = r.get("TrimmerName")
        if name and name not in seen:
            names.append(name)
            seen.add(name)
    return names

def GetTrimSummary(trimmer_name=None, start_date=None, end_date=None):
    q = (
        sb.schema("scale")
        .table("dailytrim")
        .select("TrimmerName,TrimDate,CropNo,Strain,FlowerGrams,SmallsGrams,AmPm, StartTime,EndTime")
    )
    if trimmer_name:
        q = q.eq("TrimmerName", trimmer_name)
    if start_date and end_date:
        q = q.gte("TrimDate", start_date.isoformat()).lte("TrimDate", end_date.isoformat())
    q = q.order("TrimDate").order("Strain").order("AmPm", desc=True)
    res = q.execute()
    return res.data or []

def LoadFlowerTrimRecords(crop_no: int, strain: str):
    q = (
        sb.schema("scale")
        .table("dailytrim")
        .select("TrimmerName,TrimDate,CropNo,Strain,FlowerGrams,SmallsGrams,BatchId")
        .eq("CropNo", crop_no)
        .eq("Strain", strain)
        .order("TrimDate")
        .order("TrimmerName")
    )
    res = q.execute()
    return res.data or []

def UpdateBatchId(CropNo, Strain, BatchId):
    """Update BatchId for matching dailytrim rows."""
    match_key = {
        "CropNo": CropNo,
        "Strain": Strain,
    }
    new_values = {
        "BatchId": BatchId
    }
    return (
        sb.schema("scale")
        .table("dailytrim")
        .update(new_values)
        .match(match_key)
        .execute()
    )

def GetRatesMap():
    """
    Returns a dict keyed by (CropNo, Strain) -> BigsRate (float).
    Only BigsRate is returned (used for Flower/Bigs pay).
    Expects table: scale.trimrates with columns CropNo (int), Strain (text), BigsRate (numeric)
    """
    res = (
        sb.schema("scale")
        .table("trimrates")
        .select("CropNo,Strain,BigsRate")
        .execute()
    )
    data = res.data or []
    rates = {}
    for r in data:
        key = (int(r.get("CropNo")), (r.get("Strain") or "").strip())
        rates[key] = float(r.get("BigsRate") or 0.0)
    return rates

def GetOneTrimDay(TrimmerName, TrimDate, CropNo=None, Strain=None):
    query = (
        sb.schema("scale")
        .table("dailytrim")
        .select("TrimmerName,TrimDate,CropNo,Strain,AmPm,FlowerGrams,SmallsGrams,StartTime,EndTime")
        .eq("TrimmerName", TrimmerName)
        .eq("TrimDate", TrimDate)
    )
    if CropNo is not None:
        query = query.eq("CropNo", CropNo)
    if Strain is not None:
        query = query.eq("Strain", Strain)
    
    result = query.execute()
    if result.data:
        return result.data
    else:
        return []

def UpdateDailyTrim(TrimmerName, TrimDate, CropNo, Strain, FlowerGrams, SmallsGrams, AmPm):
    upd = {
        "FlowerGrams": FlowerGrams,
        "SmallsGrams": SmallsGrams,
        "AmPm": AmPm
    }
    result = (
        sb.schema("scale")
        .table("dailytrim")
        .select("TrimmerName,TrimDate,CropNo,Strain,AmPm,FlowerGrams,SmallsGrams,StartTime,EndTime")
        .eq("TrimmerName", TrimmerName)
        .eq("TrimDate", TrimDate)
        .eq("CropNo", CropNo)
        .eq("Strain", Strain)
        .eq("AmPm", AmPm)
        .execute()
        )
    if result.data:
        res = (
            sb.schema("scale")
            .table("dailytrim")
            .update(upd, returning="representation")
            .eq("TrimmerName", TrimmerName)
            .eq("TrimDate", TrimDate)
            .eq("CropNo", CropNo)
            .eq("Strain", Strain)
            .eq("AmPm", AmPm)
            .execute()
        )
        return res.data
    else:    
        if AmPm == "Morning":
            StartTime = "08:00"
            EndTime = "12:00"
        else:
            StartTime = "13:00"
            EndTime = "17:00"
        sb.schema("scale").table("dailytrim").insert({
            "TrimmerName": TrimmerName,
            "TrimDate": TrimDate,
            "CropNo": int(CropNo),
            "Strain": Strain,
            "FlowerGrams": FlowerGrams,
            "SmallsGrams": SmallsGrams,
            "AmPm": AmPm,
            "StartTime": StartTime,
            "EndTime": EndTime, 
        }).execute()


#################################################################################################
#
# DailyTrimEditor code to edit daily trim records
#
#################################################################################################

def SelectDailytrim(trim_date, trimmer=None, ampm=None):
    """Fetch rows from dailytrim table using filters."""
    q = sb.schema("scale").table("dailytrim").select(
        "TrimmerName,TrimDate,CropNo,Strain,AmPm,FlowerGrams,SmallsGrams,StartTime,EndTime"
    ).eq("TrimDate", trim_date)

    if trimmer:
        q = q.ilike("TrimmerName", trimmer)
    if ampm:
        q = q.eq("AmPm", ampm)

    q = q.order("TrimmerName").order("AmPm", desc=True).order("CropNo").order("Strain")
    return q.execute()

def UpdateDailytrim(match_key: dict, new_values: dict):
    """Update one row based on the match key."""
    return (
        sb.schema("scale")
        .table("dailytrim")
        .update(new_values)
        .match(match_key)
        .execute()
    )

#################################################################################################
#
# Weigh Trim functions
#
#################################################################################################

def CheckTrimBag(CropNo: int, Strain: str, TagNo: str):
    """Load existing ToteNos for crop and strain."""
    res = (
        sb.schema("scale")
        .table("scaletrim")
        .select("TagNo")
        .eq("CropNo", CropNo)
        .eq("Strain", Strain)
        .eq("TagNo", TagNo)
        .order("TagNo", desc=True)
        .execute()
    )
    ReturnVal = "OkToAdd"
    for row in res.data or []:
        tag_no = row.get("TagNo")
        crop_no = row.get("CropNo")
        strain = row.get("Strain")  
        if CropNo == crop_no and Strain == strain and TagNo == tag_no:
            ReturnVal = "InUse"
        else:
            ReturnVal = "Error"


def InsertTrimBag(CropNo: int, Strain: str, TagNo: int, TrimDate):
    """Insert a new TagNo for crop and strain."""
    data = {
        "CropNo": int(CropNo),
        "Strain": Strain,
        "TagNo": int(TagNo),
        "TrimDate": TrimDate
    }
    res = sb.schema("scale").table("scaletrim").insert(data).execute()
    return res.data[0]

def UpdateTrimBag(TagNo: int, Weight: float):
    """Update weight for a given TagNo."""
    upd = {"Weight": Weight}
    res = sb.schema("scale").table("scaletrim").update(upd, returning="representation").eq("TagNo", TagNo).execute()
    return res.data[0]
#testcrop = LoadCrops()
#print(testcrop)

#trimmers = GetTrimmers()
#print(trimmers)
#testlist = GetStrains(19)
#print(testlist)