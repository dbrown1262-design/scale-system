from datetime import datetime
from supabase import create_client, Client

supabase_url = "https://figubkupxgxcrxtvsoji.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpZ3Via3VweGd4Y3J4dHZzb2ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjAyNjk4NTksImV4cCI6MjAzNTg0NTg1OX0.049XyTPGjxGqliuBWnk1HWEBypP_J76h73qfLwCQxpw"
supabase = create_client(supabase_url, supabase_key)

# Connect to Supabase
scaleschema = "scale"
sb = supabase.schema(scaleschema)

def LoadCrops():
    print("LoadCrops called")
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
def GetOneTote(CropNo, Strain, ToteNo):
    result = (
        sb.schema("scale")
        .table("scalebuck")
        .select("Weight")
        .eq("CropNo", CropNo)
        .eq("Strain", Strain)
        .eq("ToteNo", ToteNo)
        .execute()
    )
    if result.data:
        Weight = result.data[0]["Weight"]
        return Weight
    else:
        return None

def InsertNewTote(CropNo, Strain, ToteNo):
    data = {
        "CropNo": CropNo,
        "Strain": Strain,
        "ToteNo": ToteNo,
        "BuckDate": datetime.now().isoformat()  
    }
    result = sb.schema("scale").table("scalebuck").insert(data).execute()
    return result

def UpdateToteWeight(CropNo, Strain, ToteNo, Weight):
    upd = {"Weight": Weight}
    res = sb.schema("scale").table("scalebuck").update(upd, returning="representation").eq("CropNo", CropNo).eq("Strain", Strain).eq("ToteNo", ToteNo).execute()

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