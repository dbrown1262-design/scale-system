from datetime import datetime
from unittest import result
from supabase import create_client, Client

supabase_url = "https://figubkupxgxcrxtvsoji.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpZ3Via3VweGd4Y3J4dHZzb2ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjAyNjk4NTksImV4cCI6MjAzNTg0NTg1OX0.049XyTPGjxGqliuBWnk1HWEBypP_J76h73qfLwCQxpw"
supabase = create_client(supabase_url, supabase_key)

# Connect to Supabase
scaleschema = "scale"
sb = supabase.schema(scaleschema)

def LoadCrops():
#    print("LoadCrops called")
    res = (sb.table("scalecrops").select("CropNo, HarvestDate, CropStat")
            .eq("CropStat", "Active").order("CropNo", desc=True).execute())
    crops = res.data or []
    result = []
    for c in crops:
        crop_no = c.get("CropNo")
        date = c.get("HarvestDate")
        label = f"{crop_no} - {date}" if date else str(crop_no)
        result.append((label))
#    print("LoadCrops result:", result)
    return ["Select"] + result

def LoadAllCrops():
    """Load all crops (Active and Inactive) for editing purposes"""
    res = (sb.table("scalecrops").select("CropNo, HarvestDate, CropStat")
            .order("CropNo", desc=True).execute())
    crops = res.data or []
    result = []
    for c in crops:
        crop_no = c.get("CropNo")
        date = c.get("HarvestDate")
        stat = c.get("CropStat", "")
        label = f"{crop_no} - {date} ({stat})" if date else f"{crop_no} ({stat})"
        result.append(label)
    return ["Select", "New Crop"] + result

def GetCropData(crop_no: int):
    res = sb.schema("scale").table("scalecrops").select("*").eq("CropNo", crop_no).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]
    return None

def InsertCrop(CropNo, HarvestDate, CropStat):
    data = {
        "CropNo": CropNo,
        "HarvestDate": HarvestDate,
        "CropStat": CropStat
    }
    res = sb.schema("scale").table("scalecrops").insert(data).execute()
    return res.data[0]  

def UpdateCrop(CropNo, HarvestDate, CropStat):
    data = {
        "HarvestDate": HarvestDate,
        "CropStat": CropStat
    }
    res = sb.schema("scale").table("scalecrops").update(data).eq("CropNo", CropNo).execute()
    return res.data[0]

def LoadStrains(crop_no: int):
    print("LoadStrains for CropNo:", crop_no)
    res = sb.schema("scale").table("scaleplants").select("Strain").eq("CropNo", crop_no).execute()
    strains = sorted({row["Strain"] for row in res.data if row.get("Strain")}) if res.data else []
    return ["Select"] + strains

def GetOnePlant(PlantNo):
    result = (
        sb.schema("scale")
        .table("scaleplants")
        .select("Strain", "WetWeight, DryWeight")
        .eq("PlantNo", PlantNo)
        .execute()
    )
    if result.data:
        print(result.data)
        return result.data
    else:
        return None

def LoadPlantTags(CropNo, Strain):
    result = (
        sb.schema("scale")
        .table("scaleplants")
        .select("Strain", "PlantNo")
        .eq("CropNo", CropNo)
        .eq("Strain", Strain)   
        .execute()
    )
    if result.data:
        return result.data
    else:
        return None

def CountPlants(CropNo, Strain):
    result = (
        sb.schema("scale")
        .table("scaleplants")
        .select("PlantNo", count="exact")
        .eq("CropNo", CropNo)
        .eq("Strain", Strain)   
        .execute()
    )
    if result.data:
        count = result.count if hasattr(result, 'count') else 0
        return count
    else:
        return 0

def UpdateDryWeight(PlantNo, DryWeight):
    print("Updating DryWeight")
    upd = {"DryWeight": DryWeight, "DryDate": datetime.now().isoformat()}
    res = sb.schema("scale").table("scaleplants").update(upd, returning="representation").eq("PlantNo", PlantNo).execute()
    print(res)
    return res.data[0]

def UpdateWetWeight(PlantNo, WetWeight):
    upd = {"WetWeight": WetWeight, "WetDate": datetime.now().isoformat()}
    res = sb.schema("scale").table("scaleplants").update(upd, returning="representation").eq("PlantNo", PlantNo).execute()
    print(res)
    return res.data[0]


def InsertScaleLog(PlantNo: str, Strain: str, PlantType: str, Weight: int):
    data = {
        "PlantNo": PlantNo,
        "Strain": Strain,
        "PlantType": PlantType,
        "Weight": Weight,
        "ScaleDate": datetime.now().isoformat()  
    }
    result = sb.schema("scale").table("scalelog").insert(data).execute()
    return result

"""Scalebuck table functions"""

def LoadTotes(CropNo, Strain):
    res = (sb.schema("scale").table("scalebuck").select("ToteNo")
            .eq("CropNo", CropNo)
            .eq("Strain", Strain)
            .order("ToteNo", desc=True).execute())
    crops = res.data or []
    result = ["Select"]
    for c in crops:
        Toteno = c.get("ToteNo")
        date = c.get("HarvestDate")
        label = str(Toteno)
        result.append((label))
    return result

def GetNewToteNo(CropNo, Strain):
    result = (
        sb.schema("scale")
        .table("scalebuck")  # change table name if different
        .select("ToteNo")
        .eq("CropNo", CropNo)
        .eq("Strain", Strain)
        .order("ToteNo", desc=True)
        .limit(1)
        .execute()
    )

    if result.data and len(result.data) > 0:
        NewToteNo = result.data[0]["ToteNo"] + 1
        return NewToteNo
    else:
        return 1
    
def CheckTag(TagNo):
    result = (
        sb.schema("scale")
        .table("metrictags")
        .select("TagNo")
        .eq("TagNo", TagNo)
        .execute()
    )
    if result.data:
        return True
    else:
        return False
def GetOneTag(TagNo):
    result = (
        sb.schema("scale")
        .table("scalebuck")
        .select("Weight")
        .eq("TagNo", TagNo)
        .execute()
    )
    if result.data:
        Weight = result.data[0]["Weight"]
        return Weight
    else:
        return None

def InsertNewTag(CropNo, Strain, TagNo):
    data = {
        "CropNo": CropNo,
        "Strain": Strain,
        "TagNo": TagNo,
        "BuckDate": datetime.now().isoformat()  
    }
    result = sb.schema("scale").table("scalebuck").insert(data).execute()
    return result

def UpdateTagWeight(TagNo, Weight):
    upd = {"Weight": Weight}
    res = sb.schema("scale").table("scalebuck").update(upd, returning="representation").eq("TagNo", TagNo).execute()

def LoadToteReport(StartDate, EndDate):
    """Load all rows from scalebuck where BuckDate is between StartDate and EndDate
    
    Args:
        StartDate: Start date string in format 'YYYY-MM-DD'
        EndDate: End date string in format 'YYYY-MM-DD'
    
    Returns:
        List of scalebuck records within the date range
    """
    res = (sb.schema("scale").table("scalebuck")
            .select("*")
            .gte("BuckDate", StartDate)
            .lte("BuckDate", EndDate)
            .order("TagNo")
            .execute())
    return res.data or []

#res = LoadToteReport("2025-12-01", "2025-12-31")
#print(res)

def GetHarvestDate(CropNo):
    res = sb.schema("scale").table("scalecrops").select("HarvestDate").eq("CropNo", CropNo).execute()
    if res.data and len(res.data) > 0:
        return res.data[0].get("HarvestDate")
    else:
        return None


"""batchtable functions"""


def LoadOneBatch(CropNo, Strain):
    print("LoadOneBatch:", CropNo, Strain)
    res = (sb.schema("scale").table("batchtable").select("BatchId", "BatchType")
            .eq("CropNo", CropNo)
            .eq("Strain", Strain)
            .order("BatchId", desc=True).execute())
    return res.data

def LoadAllBatches(CropNo):
    print("LoadAllBatches for CropNo:", CropNo)
    res = (sb.schema("scale").table("batchtable").select("Strain,BatchType,BatchId")
            .eq("CropNo", CropNo)
            .order("Strain").order("BatchType").order("BatchId").execute())
    return res.data

def InsertBatchId(CropNo, Strain, BatchType, BatchId):
    print("InsertBatchId:", CropNo, Strain, BatchType, BatchId)
    data = {
        "CropNo": CropNo,
        "Strain": Strain,
        "BatchType": BatchType,
        "BatchId": BatchId
    }
    result = sb.schema("scale").table("batchtable").insert(data).execute()
    return result

def UpdateBatchId(CropNo, Strain, BatchType, BatchId):
    print("UpdateBatchId:", CropNo, Strain, BatchType, BatchId)
    upd = {"BatchId": BatchId}
    res = sb.schema("scale").table("batchtable").update(upd, returning="representation").eq("CropNo", CropNo).eq("Strain", Strain).eq("BatchType", BatchType).execute()
    return res.data


def UpdateBatchRow(CropNo, Strain, BatchType, OldBatchId, NewBatchId):
    """Update a single batchtable row identified by the old BatchId value.

    This allows multiple BatchId rows to exist for the same Crop/Strain/BatchType
    and updates only the specific row the user selected.
    """
    print("UpdateBatchRow:", CropNo, Strain, BatchType, OldBatchId, "->", NewBatchId)
    upd = {"BatchId": NewBatchId}
    res = (sb.schema("scale").table("batchtable").update(upd, returning="representation")
           .eq("CropNo", CropNo)
           .eq("Strain", Strain)
           .eq("BatchType", BatchType)
           .eq("BatchId", OldBatchId)
           .execute())
    return res.data


"""Metric tags table functions"""

def CheckTag(TagNo):
    """Check if a tag number exists in the metrictags table (was issued by Metric)."""
    result = (
        sb.schema("scale")
        .table("metrictags")
        .select("TagNo")
        .eq("TagNo", TagNo)
        .execute()
    )
    return result.data is not None and len(result.data) > 0

def GetOneTag(CropNo, Strain, TagNo):
    """Get weight data for a specific metric tag if it has been used."""
    result = (
        sb.schema("scale")
        .table("scalebuck")
        .select("Weight")
        .eq("CropNo", CropNo)
        .eq("Strain", Strain)
        .eq("TagNo", TagNo)
        .execute()
    )
    if result.data and len(result.data) > 0:
        return result.data[0].get("Weight")
    else:
        return None

def InsertNewTag(CropNo, Strain, TagNo, Weight):
    """Insert a new metric tag with weight data."""
    data = {
        "CropNo": CropNo,
        "Strain": Strain,
        "TagNo": TagNo,
        "Weight": Weight,
        "BuckDate": datetime.now().isoformat()
    }
    result = sb.schema("scale").table("scalebuck").insert(data).execute()
    return result

def UpdateTagWeight(CropNo, Strain, TagNo, Weight):
    """Update the weight for an existing metric tag."""
    upd = {"Weight": Weight}
    res = (
        sb.schema("scale")
        .table("scalebuck")
        .update(upd, returning="representation")
        .eq("CropNo", CropNo)
        .eq("Strain", Strain)
        .eq("ToteNo", TagNo)
        .execute()
    )
    return res.data

""" Metrc Tags routines to verify the tag type for each script"""

def GetMetrcType(MetrcId):
    prefix = MetrcId[:-9]
    res = (
        sb.schema("scale")
        .table("metrctagtypes")
        .select("MetrcType")
        .eq("MetrcId", prefix)
        .execute()
    )

    if res.data and len(res.data) > 0:
        return res.data[0].get("MetrcType")
    else:
        return None

#mtype = GetMetrcType("1A4120300001DE2000000001")
#print(mtype)

def LoadMetrcTypes():
    res = (
        sb.schema("scale")
        .table("metrctagtypes")
        .select("MetrcId", "MetrcType")
        .execute()
    )
    return res.data or []

def InsertMetrcType(MetrcId: str, MetrcType: str):
    """Insert a new Metrc tag type"""
    data = {
        "MetrcId": MetrcId,
        "MetrcType": MetrcType
    }
    res = sb.schema("scale").table("metrctagtypes").insert(data).execute()
    return res.data[0] if res.data else None

def UpdateMetrcType(MetrcId: str, MetrcType: str):
    """Update an existing Metrc tag type"""
    data = {
        "MetrcType": MetrcType
    }
    res = sb.schema("scale").table("metrctagtypes").update(data).eq("MetrcId", MetrcId).execute()
    return res.data[0] if res.data else None


def CheckTags(crop_no: str, strain: str):
    """
    Returns:
        {
            "start_seq": int,
            "end_seq": int,
            "count": int,
            "missing": list   # empty if continuous
        }
    """

    # Pull plant IDs for the strain
    resp = (
        sb.table("scaleplants")
        .select("PlantNo")
        .eq("CropNo", crop_no)
        .eq("Strain", strain)
        .execute()
    )

    rows = resp.data
    if not rows:
        return None

    # Extract sequence numbers (last 9 digits)
    seqs = []
    for r in rows:
        plant_id = r["PlantNo"]
        seq = int(plant_id[-9:])
        seqs.append(seq)

    seqs.sort()

    start_seq = seqs[0]
    end_seq   = seqs[-1]

    # Check for gaps
    expected = set(range(start_seq, end_seq + 1))
    missing = sorted(list(expected - set(seqs)))

    return {
        "start_seq": start_seq,
        "end_seq": end_seq,
        "count": len(seqs),
        "missing": missing
    }

(Start, End, Count, Missing) = CheckTags(21, "Sherb").values()
print(f"Start: {Start}, End: {End}, Count: {Count}, Missing: {Missing}")


""" 
ToteNo = LoadTotes(1, "Test Strain")
print("ToteNos:", ToteNo)
ToteNo = GetNewToteNo(1, "Test Strain")
print("New ToteNo:", ToteNo)
result = InsertNewTote(1, "Test Strain", ToteNo)
print("InsertNewTote result:", result)  
"""

#count = CountPlants(1, "Test Strain")
#print("CountPlants result:", count)

#testcrop = LoadCrops()
#print(testcrop)

#trimmers = GetTrimmers()
#print(trimmers)
#testlist = GetStrains(19)
#print(testlist)