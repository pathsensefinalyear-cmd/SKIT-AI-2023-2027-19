"""
PathSense Backend Runner
Author: Team PathSense (SKIT Jaipur, 7th Sem Minor Project)
Team:
  1. Sharafat Khan (23ESKCA098)
  2. Soham Manocha (23ESKCA102)
  3. Sourabh Nagar (23ESKCA105)
  4. Vedic Baurasi (23ESKCA119)

Starts the high-performance ASGI REST API server on uvicorn.
Usage:
    python backend/run_backend.py --port 8000
"""

import sys
import os
import argparse
import uvicorn


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(description="PathSense Backend REST API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    print("=" * 70)
    print("      PATHSENSE AI: BACKEND PRODUCTION REST API SERVER            ")
    print("=" * 70)
    print("Academic Context: 7th Semester B.Tech Minor Project")
    print("Institution     : Swami Keshvanand Institute of Technology (SKIT), Jaipur")
    print("Department      : Computer Science & Artificial Intelligence (CS-AI)")
    print("-" * 70)
    print("Team Members:")
    print("  1. Sharafat Khan  (23ESKCA098) - Lead Architect & Edge AI")
    print("  2. Soham Manocha   (23ESKCA102) - Computer Vision & Dataset Pipeline")
    print("  3. Sourabh Nagar   (23ESKCA105) - Backend Engine & Telemetry Sync")
    print("  4. Vedic Baurasi   (23ESKCA119) - Dashboard & GIS Heatmap")
    print("-" * 70)
    print(f"Backend Server  : http://{args.host}:{args.port}")
    print(f"Health API      : http://{args.host}:{args.port}/api/v1/health")
    print(f"Heatmap API     : http://{args.host}:{args.port}/api/v1/heatmap")
    print(f"Detect API      : http://{args.host}:{args.port}/api/v1/detect")
    print(f"Telemetry API   : http://{args.host}:{args.port}/api/v1/telemetry")
    print(f"Database        : SQLite (logs/pathsense.db)")
    print("=" * 70)

    uvicorn.run(
        "backend.api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
