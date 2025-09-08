import pandas as pd
import json
from io import BytesIO
from fastapi import UploadFile, HTTPException

async def parse_file(file: UploadFile, entity_type: str):
    filename = file.filename
    extension = filename.split(".")[-1].lower()
    try:
        content_bytes = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read file.")

    rows_to_send = []

    if extension == "xlsx":
        try:
            excel_file = pd.ExcelFile(BytesIO(content_bytes))
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)
                df = df.dropna(how="all")
                rows_to_send.extend(df.to_dict(orient="records"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid Excel file: {str(e)}")
    elif extension == "json":
        try:
            data = json.loads(content_bytes.decode("utf-8"))
            if isinstance(data, list):
                rows_to_send.extend(data)
            else:
                raise HTTPException(status_code=400, detail="JSON must be an array of objects.")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON file.")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload .xlsx or .json.")

    return rows_to_send
