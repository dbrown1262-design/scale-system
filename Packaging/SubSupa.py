from supabase import create_client, Client
from datetime import datetime

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

def LoadPackageTypes():
    # Return all package type rows with expected columns
    res = (
        sb.schema("scale")
        .table("packagetypes")
        .select("id,PackageType,UnitWeight,NumUnits,TotWeight")
        .order("PackageType")
        .execute()
    )
    return res.data or []

def InsertPackageType(PackageType: str, UnitWeight: float, NumUnits: int, TotWeight: float):
    data = {
        "PackageType": PackageType,
        "UnitWeight": UnitWeight,
        "NumUnits": NumUnits,
        "TotWeight": TotWeight,
    }
    res = sb.schema("scale").table("packagetypes").insert(data).execute()
    return res.data

def UpdatePackageType(row_id: int, PackageType: str, UnitWeight: float, NumUnits: int, TotWeight: float):
    data = {
        "PackageType": PackageType,
        "UnitWeight": UnitWeight,
        "NumUnits": NumUnits,
        "TotWeight": TotWeight,
    }
    res = sb.schema("scale").table("packagetypes").update(data).eq("id", row_id).execute()
    return res.data

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


#################################################################################################
#
# Code to enter daily packaging activity
#
#################################################################################################

def GetPackages(BatchId, PackageType):
    # Execute the query and return the data list (include UnitWeight)
    result = (
        sb.schema("scale")
        .table("packages")
        .select("BatchId, PackageType, TotUnits, TotWeight, batchtable(Strain, BatchType)")
        .eq("BatchId", BatchId)
        .eq("PackageType", PackageType)
        .execute()
    )
    return result.data or []

#res = GetPackages("TS202501", "Jars")
#print("Packages loaded:", res)

def GetPackageWeight(PackageType: str):
    # Return the unit weight (grams) for the package type
    res = sb.schema("scale").table("packagetypes").select("UnitWeight").eq("PackageType", PackageType).execute()
    if res.data:
        return res.data[0].get("UnitWeight")
    return None

def InsertPackage(BatchId: str, PackageType: str, UnitWeight: float, TotUnits: int, TotWeight: float, PackDate: str = None):
    # Accept PackDate as ISO string; if missing, use current timestamp
    if PackDate is None:
        PackDate = datetime.now().isoformat()
    data = {
        "BatchId": BatchId,
        "PackageType": PackageType,
        "TotUnits": TotUnits,
        "TotWeight": TotWeight,
        "PackDate": PackDate,
    }
    res = sb.schema("scale").table("packages").insert(data).execute()
    return res.data

def LoadBatches(CropNo, Strain):
    batches = ["Select"]
    res = (sb.schema("scale")
        .table("batchtable")
        .select("BatchId", "BatchType")
        .eq("CropNo", CropNo)
        .eq("Strain", Strain)
        .order("BatchId")
        .execute())
    for row in res.data or []:
        batch_id = row.get("BatchId")
        batch_type = row.get("BatchType")
        entry = f"{batch_id} ({batch_type})" if batch_type else batch_id
        batches.append(entry)
    return batches



#################################################################################################
#
# Hash Run functions
#
# hashbatch Table: 	BatchId, Type, Status (In Process, Finished)
# hashruns Table:	BatchId, RunNo, CropNo, Strain, Source, StartWeight, EndWeight
#
#
#################################################################################################

def NewHashBatch(BatchId: str, Type: str):
    data = {
        "BatchId": BatchId,
        "Type": Type,
        "Status": "",
    }
    res = sb.schema("scale").table("hashbatch").insert(data).execute()
    return res.data

def GetHashBatches(Type: str):
    res = sb.schema("scale").table("hashbatch").select("BatchId").eq("Type", Type).order("BatchId").execute()
    return res.data or []

def GetRunNos(BatchId: str):
    res = sb.schema("scale").table("hashruns").select("RunNo").eq("BatchId", BatchId).order("RunNo", desc=True).execute()
    run_nos = [row["RunNo"] for row in res.data or [] if row.get("RunNo") is not None]
    return run_nos  

def GetNewRunNo(BatchId: str):
    run_nos = GetRunNos(BatchId)
    if run_nos:
        return max(run_nos) + 1
    return 1

def InsertHashRun(BatchId: str, RunNo: int):
    data = {
        "BatchId": BatchId,
        "RunNo": RunNo,
        "CropNo": None,
        "Strain": None,
        "Source": None,
        "StartWeight": 0,
        "EndWeight": 0,
    }
    res = sb.schema("scale").table("hashruns").insert(data).execute()
    return res.data

def GetRunRec(BatchId: str, RunNo: int):
    res = sb.schema("scale").table("hashruns").select("CropNo, Strain, Source, StartWeight, EndWeight").eq("BatchId", BatchId).eq("RunNo", RunNo).execute()
    if res.data:
        return res.data[0]
    return None

def GetRuns(BatchId: str):
    res = sb.schema("scale").table("hashruns").select("RunNo, CropNo, Strain, Source, StartWeight, EndWeight").eq("BatchId", BatchId).order("RunNo").execute()
    return res.data or []

def SaveHashStartWeight(BatchId: str, RunNo: int, CropNo: str, Strain: str, Source: str, StartWeight: float):
    upd = {
        "CropNo": CropNo,
        "Strain": Strain,
        "Source": Source,
        "StartWeight": StartWeight
    }
    res = sb.schema("scale").table("hashruns").update(upd).eq("BatchId", BatchId).eq("RunNo", RunNo).execute()
    return res.data

def SaveHashEndWeight(BatchId: str, RunNo: int, EndWeight: float):
    upd = {
        "EndWeight": EndWeight
    }
    res = sb.schema("scale").table("hashruns").update(upd).eq("BatchId", BatchId).eq("RunNo", RunNo).execute()
    return res.data
