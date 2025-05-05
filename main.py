from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import json
import os
from pathlib import Path

app = FastAPI(title="BTG Positions Webhook")

# Criar diretório para armazenar os arquivos JSON
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

class PositionData(BaseModel):
    accountNumber: Optional[str] = None
    fileSize: int
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    url: str

class WebhookPayload(BaseModel):
    errors: list
    response: PositionData

API_KEY = "finacap2025"

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    return x_api_key

def save_to_json(data: dict):
    # Criar nome do arquivo baseado no timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = DATA_DIR / f"position_{timestamp}.json"
    
    # Adicionar timestamp de recebimento
    data["received_at"] = datetime.now().isoformat()
    
    # Salvar dados em arquivo JSON
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

@app.post("/webhook/positions")
async def receive_positions(
    data: WebhookPayload,
    api_key: str = Depends(verify_api_key)
):
    try:
        # Converter os dados para dicionário
        data_dict = data.dict()
        
        # Salvar em arquivo JSON
        filename = save_to_json(data_dict)
        
        return {
            "status": "success", 
            "message": "Dados recebidos e salvos com sucesso",
            "file": str(filename)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 