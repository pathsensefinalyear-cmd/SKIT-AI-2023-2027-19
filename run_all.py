"""
PathSense AI: Unified Process Launcher
Author: Team PathSense (SKIT Jaipur, 7th Sem Minor Project)
Team:
  1. Sharafat Khan (23ESKCA098)
  2. Soham Manocha (23ESKCA102)
  3. Sourabh Nagar (23ESKCA105)
  4. Vedic Baurasi (23ESKCA119)

Spawns both:
  1. Backend REST API Server (Port 8000)
  2. Streamlit Geospatial Dashboard (Port 8501)
Gracefully handles shutdown on Ctrl + C.

Usage:
  python run_all.py
"""

import os
import sys
import time
import subprocess
import signal

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 72)
    print("           PATHSENSE AI: UNIFIED ONE-CLICK LAUNCHER             ")
    print("=" * 72)
    print("Academic Context : 7th Semester B.Tech Minor Project")
    print("Institution      : Swami Keshvanand Institute of Technology (SKIT), Jaipur")
    print("Department       : Computer Science & Artificial Intelligence (CS-AI)")
    print("-" * 72)
    print("Team Members:")
    print("  1. Sharafat Khan  (23ESKCA098)")
    print("  2. Soham Manocha  (23ESKCA102)")
    print("  3. Sourabh Nagar  (23ESKCA105)")
    print("  4. Vedic Baurasi  (23ESKCA119)")
    print("=" * 72)

    python_exec = sys.executable

    # 1. Start Backend API Server
    print("\n[1/2] Starting PathSense REST API Server on http://127.0.0.1:8000 ...")
    backend_cmd = [python_exec, os.path.join(PROJECT_ROOT, "backend", "run_backend.py"), "--port", "8000"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=PROJECT_ROOT)

    time.sleep(2)

    # 2. Start Streamlit Dashboard
    print("[2/2] Launching Streamlit Dashboard on http://localhost:8501 ...")
    streamlit_cmd = [
        python_exec, "-m", "streamlit", "run",
        os.path.join(PROJECT_ROOT, "dashboard", "app.py"),
        "--server.port", "8501",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        streamlit_proc = subprocess.Popen(streamlit_cmd, cwd=PROJECT_ROOT)
        print("\n" + "=" * 72)
        print(" [OK] Both Services Running! Press Ctrl+C in this terminal to stop both.")
        print("=" * 72 + "\n")
        streamlit_proc.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Stopping PathSense services...")
    finally:
        try:
            backend_proc.terminate()
            backend_proc.wait(timeout=2)
        except Exception:
            backend_proc.kill()
        print("[OK] PathSense shutdown complete.")

if __name__ == "__main__":
    main()
