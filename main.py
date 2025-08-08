from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from io import BytesIO
from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from sklearn.linear_model import LinearRegression
import ssl
import certifi
import requests

app = FastAPI()

# Static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routes
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/live-data", response_class=HTMLResponse)
async def live_data(request: Request):
    file_id = "14IXqCZ1Vr3T4-vEKH6oDd223QHXhF5eP"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Use requests with certifi SSL certificates to fetch CSV
    response = requests.get(url, verify=certifi.where())
    response.raise_for_status()  # Will raise HTTPError if request failed

    # Load CSV content into pandas DataFrame
    csv_data = StringIO(response.text)
    df = pd.read_csv(csv_data)

    # Take last 10 rows of relevant sensor columns
    recent = df.tail(10)[["Temperature", "Humidity", "Moisture", "Distance"]]

    # Ideal constants
    IDEAL_TEMP = 20
    IDEAL_HUMIDITY = 70
    IDEAL_MOISTURE = 300
    IDEAL_DISTANCE = 5

    # Calculate HealthScore for each row
    recent["HealthScore"] = 100 \
        - abs(recent["Temperature"] - IDEAL_TEMP) * 1.0 \
        - abs(recent["Humidity"] - IDEAL_HUMIDITY) * 0.5 \
        - abs(recent["Moisture"] - IDEAL_MOISTURE) * 0.2 \
        - abs(recent["Distance"] - IDEAL_DISTANCE) * 5.0
    recent["HealthScore"] = recent["HealthScore"].clip(0, 100)

    average_health = round(recent["HealthScore"].mean(), 2)

    # Plot predicted health scores
    plt.figure(figsize=(8, 4))
    plt.plot(recent.index, recent["HealthScore"], marker='o', color='green')
    plt.title("Recent Predicted Plant Health")
    plt.xlabel("Record")
    plt.ylabel("Health Score (%)")
    plt.ylim(0, 100)
    plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    chart_image = base64.b64encode(buf.read()).decode('utf-8')

    return templates.TemplateResponse("live_data.html", {
        "request": request,
        "chart_image": chart_image,
        "average_health": average_health
    })

@app.get("/about-this-project", response_class=HTMLResponse)
def about_project(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# WebSocket-related
class SensorData(BaseModel):
    temperature: float
    humidity: float
    soilMoisture: Optional[int] = None
    distance: Optional[int] = None
    waterDetected: Optional[int] = None

data_list = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.post("/data")
async def receive_data(data: SensorData):
    data_list.append(data)
    await manager.broadcast(data.dict())
    return {"message": "Data received"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health-predictor", response_class=HTMLResponse)
async def health_form(request: Request):
    return templates.TemplateResponse("health_predictor.html", {"request": request})

@app.post("/health-predictor", response_class=HTMLResponse)
async def health_predictor(
    request: Request,
    temperature1: float = Form(...), humidity1: float = Form(...), moisture1: float = Form(...), distance1: float = Form(...),
    temperature2: float = Form(...), humidity2: float = Form(...), moisture2: float = Form(...), distance2: float = Form(...),
    temperature3: float = Form(...), humidity3: float = Form(...), moisture3: float = Form(...), distance3: float = Form(...),
    temperature4: float = Form(...), humidity4: float = Form(...), moisture4: float = Form(...), distance4: float = Form(...),
    temperature5: float = Form(...), humidity5: float = Form(...), moisture5: float = Form(...), distance5: float = Form(...)
):
    # Construct DataFrame
    df = pd.DataFrame({
        "Temperature": [temperature1, temperature2, temperature3, temperature4, temperature5],
        "Humidity":    [humidity1, humidity2, humidity3, humidity4, humidity5],
        "Moisture":    [moisture1, moisture2, moisture3, moisture4, moisture5],
        "Distance":    [distance1, distance2, distance3, distance4, distance5]
    })

    # Ideal constants
    IDEAL_TEMP = 20
    IDEAL_HUMIDITY = 70
    IDEAL_MOISTURE = 300
    IDEAL_DISTANCE = 5

    # Compute HealthScore
    df["HealthScore"] = 100 \
        - abs(df["Temperature"] - IDEAL_TEMP) * 1.0 \
        - abs(df["Humidity"] - IDEAL_HUMIDITY) * 0.5 \
        - abs(df["Moisture"] - IDEAL_MOISTURE) * 0.2 \
        - abs(df["Distance"] - IDEAL_DISTANCE) * 5.0
    df["HealthScore"] = df["HealthScore"].clip(0, 100)

    # Model training
    X = df[["Temperature", "Humidity", "Moisture", "Distance"]]
    y = df["HealthScore"]

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    avg_predicted_health = round(y_pred.mean(), 2)

    # Generate plot
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, 6), y_pred, marker='o', color='green')
    plt.title("🌿 Predicted Plant Health Score Over 5 Days")
    plt.xlabel("Day")
    plt.ylabel("Predicted Health Score")
    plt.ylim(0, 100)
    plt.grid(True)

    # Convert plot to base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.read()).decode('utf-8')


    return templates.TemplateResponse("health_predictor.html", {
    "request": request,
    "predicted_health_avg": avg_predicted_health,
    "plot_image": plot_base64,
    "input_data": df.to_dict(orient="records"),
    "show_results": True
})

@app.get("/ssl-check")
def ssl_check():
    cert_path = certifi.where()
    try:
        context = ssl.create_default_context(cafile=cert_path)
        return {"status": "success", "cert_path": cert_path}
    except Exception as e:
        return {"status": "failure", "error": str(e)}