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
        "Status": "In Process",
    }
    res = sb.schema("scale").table("hashbatch").insert(data).execute()
    return res.data

def GetHashBatches(Type: str):
    res = sb.schema("scale").table("hashbatch").select("BatchId").eq("Type", Type).order("BatchId").execute()
    Batches = [row["BatchId"] for row in res.data or [] if row.get("BatchId") is not None]
    return Batches or []

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
def GetOneBatch(BatchId):
    print("GetOneBatch:", BatchId)
    res = (sb.schema("scale").table("hashbatch").select("Type, BatchDate")
            .eq("BatchId", BatchId)
            .order("BatchId", desc=True).execute())
    BatchDate = res.data[0].get("BatchDate") if res.data and len(res.data) > 0 else None
    return res.data

def GetHashLabelData(BatchId):
    # Read all hashruns rows for the given BatchId and return:
    #  - list of unique {"Strain":..., "Source":...} rows
    #  - sum of EndWeight across all runs
    res = (sb.schema("scale").table("hashbatch").select("Type, BatchDate")
            .eq("BatchId", BatchId)
            .order("BatchId", desc=True).execute())
    BatchDate = res.data[0].get("BatchDate") if res.data and len(res.data) > 0 else None
    res = sb.schema("scale").table("hashruns").select("Strain, Source, EndWeight").eq("BatchId", BatchId).execute()
    rows = res.data or []
    seen = set()
    unique_pairs = []
    TotalGrams = 0.0
    NumStrains = 0
    Strain1 = ""
    Strain2 = ""
    Strain3 = ""
    Strain4 = ""
    for r in rows:
        strain = r.get("Strain") or ""
        source = r.get("Source") or ""
        key = (strain, source)
        if key not in seen:
            seen.add(key)
            NumStrains += 1
            if NumStrains == 1:
                Strain1 = strain
            elif NumStrains == 2:
                Strain2 = strain
            elif NumStrains == 3:
                Strain3 = strain
            elif NumStrains == 4:
                Strain4 = strain
        ew = r.get("EndWeight")
        try:
            if ew is None:
                val = 0.0
            else:
                val = float(ew)
        except Exception:
            val = 0.0
        TotalGrams += val

    return (BatchDate, NumStrains, Strain1, Strain2, Strain3, Strain4, TotalGrams)

def GetHashBatchStrain(BatchId):
    # Return strain (numstrains =1) or "Mixed" (numstrains >1)
    (BatchDate, NumStrains, Strain1, Strain2, Strain3, Strain4, TotalGrams) = GetHashLabelData(BatchId)
    if NumStrains > 1:
        return "Mixed"
    return Strain1

#strain = GetHashBatchStrain("TSHash202501")
#print("Test GetHashBatchStrain:", strain)
#################################################################################################
#
# Rosin Run functions
#
# rosinbatch Table:   BatchId, Type, Status (In Process, Finished), BatchDate
# rosinruns Table:	  BatchId, RunNo, Source, StartWeight, EndWeight
#
#
#################################################################################################

def NewRosinBatch(BatchId):
    data = {
        "BatchId": BatchId,
        "Type": "Rosin",
        "Status": "In Process",
    }
    res = sb.schema("scale").table("rosinbatch").insert(data).execute()
    return res.data

def GetRosinBatches():
    Batches = ["Select", "New"]
    res = sb.schema("scale").table("rosinbatch").select("BatchId").order("BatchId").execute()
    for row in res.data:
        Batches.append(row.get("BatchId"))
    return Batches

def GetRosinRunNos(BatchId: str):
    RunNos = ["Select", "New"]
    res = sb.schema("scale").table("rosinruns").select("RunNo").eq("BatchId", BatchId).order("RunNo", desc=True).execute()
    for row in res.data:
        RunNos.append(row.get("RunNo"))
    return RunNos

def GetNewRosinRunNo(BatchId: str):
    # Query the rosinruns table for the single highest RunNo for this BatchId
    res = sb.schema("scale").table("rosinruns").select("RunNo").eq("BatchId", BatchId).order("RunNo", desc=True).limit(1).execute()
    if res.data and len(res.data) > 0:
        try:
            last = int(res.data[0].get("RunNo") or 0)
        except Exception:
            last = 0
        return last + 1
    return 1

def InsertRosinRun(BatchId: str, RunNo: int):
    data = {
        "BatchId": BatchId,
        "RunNo": RunNo,
        "Source": None,
        "StartWeight": 0,
        "EndWeight": 0,
    }
    res = sb.schema("scale").table("rosinruns").insert(data).execute()
    return res.data

def GetRosinRunRec(BatchId: str, RunNo: int):
    res = sb.schema("scale").table("rosinruns").select("Source, StartWeight, EndWeight").eq("BatchId", BatchId).eq("RunNo", RunNo).execute()
    if res.data:
        return res.data[0]
    return None

def LoadSourceCombo():
    res = sb.schema("scale").table("hashbatch").select("BatchId").order("BatchId").execute()
    sources = [row["BatchId"] for row in res.data or [] if row.get("BatchId") is not None]
    print("LoadSourceCombo:", sources)
    return ["Select"] + sources

def GetRosinRuns(BatchId: str):
    res = sb.schema("scale").table("rosinruns").select("RunNo, Source, StartWeight, EndWeight").eq("BatchId", BatchId).order("RunNo").execute()
    return res.data or []

def SaveRosinStartWeight(BatchId: str, RunNo: int, Source: str, StartWeight: float):
    upd = {
        "Source": Source,
        "StartWeight": StartWeight
    }
    res = sb.schema("scale").table("rosinruns").update(upd).eq("BatchId", BatchId).eq("RunNo", RunNo).execute()
    return res.data

def SaveRosinEndWeight(BatchId: str, RunNo: int, EndWeight: float):
    upd = {
        "EndWeight": EndWeight
    }
    res = sb.schema("scale").table("rosinruns").update(upd).eq("BatchId", BatchId).eq("RunNo", RunNo).execute()
    return res.data

def GetRosinLabelData(BatchId):
    # Read all hashruns rows for the given BatchId and return:
    #  - list of unique {"Strain":..., "Source":...} rows
    #  - sum of EndWeight across all runs
    res = (sb.schema("scale").table("rosinbatch").select("BatchDate")
            .eq("BatchId", BatchId)
            .order("BatchId", desc=True).execute())
    BatchDate = res.data[0].get("BatchDate") if res.data and len(res.data) > 0 else None
    res = sb.schema("scale").table("rosinruns").select("Source, EndWeight").eq("BatchId", BatchId).execute()
    rows = res.data or []
    seen = set()
    TotalGrams = 0.0
    NumStrains = 0
    Strain1 = ""
    Strain2 = ""
    Strain3 = ""
    Strain4 = ""
    for r in rows:
        strain = r.get("Source") or ""
        key = (strain)
        if key not in seen:
            seen.add(key)
            s = GetHashBatchStrain(strain)
            NumStrains += 1
            strain = f"{strain} ({s})"
            if NumStrains == 1:
                Strain1 = strain
            elif NumStrains == 2:
                Strain2 = strain
            elif NumStrains == 3:
                Strain3 = strain
            elif NumStrains == 4:
                Strain4 = strain
        ew = r.get("EndWeight")
        try:
            if ew is None:
                val = 0.0
            else:
                val = float(ew)
        except Exception:
            val = 0.0
        TotalGrams += val

    return (BatchDate, Strain1, Strain2, Strain3, Strain4, TotalGrams)


