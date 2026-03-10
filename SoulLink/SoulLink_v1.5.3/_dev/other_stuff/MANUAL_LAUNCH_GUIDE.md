# SoulLink Manual Launch Guide

## Quick Start (Manual Mode)

### Step 1: Start Backend

```bash
# Navigate to backend directory
cd D:\Coding\SoulLink_v1.5.3\backend

# Activate virtual environment (if you have one)
# If no venv exists, create one first:
# python -m venv venv
.\venv\Scripts\activate

# Install dependencies (if needed)
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Start Frontend (Separate Terminal)

```bash
# Navigate to frontend directory
cd D:\Coding\SoulLink_v1.5.3\frontend

# Run Flutter app
flutter run -d windows
```

## Troubleshooting

### "uvicorn not found"
- Make sure you've activated the Python virtual environment
- Install uvicorn: `pip install uvicorn`

### Flutter build errors
- Try: `flutter clean`
- Then: `flutter pub get`
- Then retry: `flutter run -d windows`

### No virtual environment?
Create one:
```bash
cd D:\Coding\SoulLink_v1.5.3\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
