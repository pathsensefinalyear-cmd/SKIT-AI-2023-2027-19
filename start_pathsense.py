"""
PathSense: Unified Application Launcher & Orchestrator
Author: Team PathSense (SKIT Jaipur, 7th Sem Minor Project)
Team:
  1. Sharafat Khan (23ESKCA098) - Lead Architect & Edge AI
  2. Soham Manocha (23ESKCA102) - Edge Inference & Pipeline
  3. Sourabh Nagar (23ESKCA105) - Backend REST API & Database
  4. Vedic Baurasi (23ESKCA119) - Geospatial Dashboard & ByteTrack

Provides single-command launching for:
  - Backend Starlette ASGI REST API (Port 8000)
  - Frontend Streamlit Geospatial Dashboard (Port 8501)
  - Automated SQLite database seeding & verification
"""

import os
import sys
import time
import argparse
import subprocess
import webbrowser

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

PYTHON_EXE = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable


def banner():
    print("=" * 72)
    print("           PATHSENSE AI: UNIFIED FULL-STACK LAUNCHER            ")
    print("=" * 72)
    print("Institution: Swami Keshvanand Institute of Technology (SKIT), Jaipur")
    print("Department : Computer Science & Artificial Intelligence (CS-AI)")
    print("Milestone  : 7th Semester B.Tech Minor Project")
    print("-" * 72)
    print("Team Members:")
    print("  1. Sharafat Khan  (23ESKCA098) - Lead Architect & Edge AI")
    print("  2. Soham Manocha   (23ESKCA102) - Computer Vision & Dataset Pipeline")
    print("  3. Sourabh Nagar   (23ESKCA105) - Backend Engine & Telemetry Sync")
    print("  4. Vedic Baurasi   (23ESKCA119) - Dashboard & GIS Heatmap")
    print("=" * 72)


def seed_database():
    print("\n[Step 1/3] Verifying and Seeding SQLite Database...")
    db_path = os.path.join(PROJECT_ROOT, "logs", "pathsense.db")
    from backend import seed_db
    if not os.path.exists(db_path) or os.path.getsize(db_path) < 1000:
        seed_db.force_reseed()
    else:
        seed_db.seed_from_csv()
    print("[OK] Database ready at: logs/pathsense.db")


def run_tests():
    print("\nRunning Backend Automated Test Suite...")
    res = subprocess.run([PYTHON_EXE, os.path.join(PROJECT_ROOT, "backend", "test_backend.py")])
    return res.returncode == 0


def run_backend(port=8000):
    print(f"\nStarting Starlette ASGI Backend on http://127.0.0.1:{port}...")
    proc = subprocess.Popen([
        PYTHON_EXE,
        os.path.join(PROJECT_ROOT, "backend", "run_backend.py"),
        "--port", str(port)
    ])
    return proc


def run_frontend(port=8501, headless=False):
    print(f"\nStarting Streamlit Geospatial Dashboard on http://localhost:{port}...")
    streamlit_exe = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "streamlit.exe")
    cmd = [
        streamlit_exe if os.path.exists(streamlit_exe) else "streamlit", "run",
        os.path.join(PROJECT_ROOT, "dashboard", "app.py"),
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    proc = subprocess.Popen(cmd)
    if not headless:
        try:
            time.sleep(2)
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass
    return proc


def main():
    banner()
    parser = argparse.ArgumentParser(description="PathSense Unified Launcher")
    parser.add_argument("--mode", choices=["all", "backend", "frontend", "test", "seed"],
                        default="all", help="Launch mode (default: all)")
    parser.add_argument("--backend-port", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("--frontend-port", type=int, default=8501, help="Frontend port (default: 8501)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    args = parser.parse_args()

    seed_database()

    if args.mode == "seed":
        print("\nDatabase seeded successfully. Exiting.")
        return

    if args.mode == "test":
        success = run_tests()
        sys.exit(0 if success else 1)

    processes = []

    try:
        if args.mode in ["all", "backend"]:
            b_proc = run_backend(args.backend_port)
            processes.append(b_proc)
            time.sleep(1.5)  # Allow backend to bind port

        if args.mode in ["all", "frontend"]:
            f_proc = run_frontend(args.frontend_port, headless=args.no_browser)
            processes.append(f_proc)

        print("\n" + "=" * 72)
        print("          SERVICES ARE LIVE AND CONNECTED                       ")
        print("=" * 72)
        if args.mode in ["all", "backend"]:
            print(f"  * REST API Engine   : http://127.0.0.1:{args.backend_port}")
            print(f"  * Health Diagnostic : http://127.0.0.1:{args.backend_port}/api/v1/health")
            print(f"  * Heatmap JSON Data : http://127.0.0.1:{args.backend_port}/api/v1/heatmap")
            print(f"  * Analytics Summary : http://127.0.0.1:{args.backend_port}/api/v1/analytics")
        if args.mode in ["all", "frontend"]:
            print(f"  * Web Dashboard     : http://localhost:{args.frontend_port}")
        print("=" * 72)
        print("Press Ctrl+C to stop all servers gracefully.\n")

        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\nShutting down servers...")
        for p in processes:
            p.terminate()
        print("All servers stopped.")


if __name__ == "__main__":
    main()
