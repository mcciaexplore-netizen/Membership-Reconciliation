import base64
import sys
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Add root to python path to access src
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ingest import load_config
from src.matcher import reconcile
from src.reporter import write_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Membership Reconciliation Engine is running."}


@app.post("/api/reconcile")
async def reconcile_files(
    bank_file: UploadFile = File(...),
    backend_file: UploadFile = File(...)
):
    try:
        # Load raw bytes
        bank_bytes = await bank_file.read()
        backend_bytes = await backend_file.read()
        
        # Load config
        config = load_config(ROOT / "config" / "config.yaml")
        
        import os
        import tempfile

        from src.ingest import load_backend_data, load_bank_statement
        
        # Write bytes to temporary files to use existing ingest logic
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx" if backend_file.filename.endswith("xlsx") else ".csv") as temp_backend:
            temp_backend.write(backend_bytes)
            backend_path = temp_backend.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx" if bank_file.filename.endswith("xlsx") else ".csv") as temp_bank:
            temp_bank.write(bank_bytes)
            bank_path = temp_bank.name

        try:
            bank_df = load_bank_statement(bank_path, config)
            backend_df = load_backend_data(backend_path, config)
        finally:
            # Clean up temp files
            if os.path.exists(bank_path):
                os.remove(bank_path)
            if os.path.exists(backend_path):
                os.remove(backend_path)

        # Run reconciliation
        result = reconcile(bank_df, backend_df, config)

        # Generate Excel report via temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_out:
            out_path = temp_out.name
            
        try:
            write_report(result, out_path)
            with open(out_path, "rb") as f:
                excel_base64 = base64.b64encode(f.read()).decode('utf-8')
        finally:
            if os.path.exists(out_path):
                os.remove(out_path)
            # also remove the audit log created by write_report
            audit_path = out_path.replace(".xlsx", ".audit_log.json")
            if os.path.exists(audit_path):
                os.remove(audit_path)

        # Generate summary payload
        summary = result.summary
        
        import json

        from fastapi.responses import Response
        
        # Convert DataFrames to dicts for frontend rendering, properly handling pandas/numpy types
        def df_to_dict(df):
            if df.empty:
                return []
            return json.loads(df.to_json(orient="records", date_format="iso"))

        payload = {
            "summary": summary,
            "data": {
                "matched": df_to_dict(result.matched),
                "unmatched_bank": df_to_dict(result.unmatched_bank),
                "unmatched_backend": df_to_dict(result.unmatched_backend),
                "partial": df_to_dict(result.partial),
                "duplicates_bank": df_to_dict(result.duplicates_bank),
                "duplicates_backend": df_to_dict(result.duplicates_backend),
            },
            "excel_base64": excel_base64
        }
        
        # Serialize the entire payload explicitly to handle any remaining numpy types in the summary
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if hasattr(obj, 'item'):
                    return obj.item()
                return super().default(obj)
                
        json_payload = json.dumps(payload, cls=NumpyEncoder)
        return Response(content=json_payload, media_type="application/json")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e!s}")

