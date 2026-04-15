# REST API Reference

## Start Server

```bash
pip install hydrosovereign[api]
uvicorn hydrosovereign.api_server:app --host 0.0.0.0 --port 8000
```

Interactive docs: `http://localhost:8000/docs`

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Package info |
| POST | `/analyze` | Full basin analysis |
| GET | `/analyze/all` | All 26 basins ranked |
| GET | `/basins` | List basins |
| GET | `/basins/{name}` | Single basin |
| POST | `/indices` | ATDI/HIFD/CI |
| POST | `/wqi` | Water Quality Index |
| POST | `/negotiate` | Negotiation AI |
| POST | `/forecast` | Discharge forecast |
| GET | `/legal/{name}` | UNWC 1997 assessment |
| GET | `/alerts/{name}` | Alert levels |
| GET | `/health` | Health check |

## Example: Analyze Basin

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"name": "Blue Nile (GERD)", "include_ai": true}'
```

## Docker

```bash
docker pull saifeldinalkedir/hydrosovereign:6.5.0
docker run -p 8000:8000 saifeldinalkedir/hydrosovereign:6.5.0
```
