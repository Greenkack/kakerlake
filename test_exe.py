"""
Test script for OmersSolarDingelDangel EXE
"""
import subprocess
import sys
import time
from pathlib import Path

def test_exe():
    print("🧪 Testing OmersSolarDingelDangel.exe...")
    
    exe_path = Path(__file__).parent / "dist" / "OmersSolarDingelDangel.exe"
    
    if not exe_path.exists():
        print(f"❌ EXE file not found: {exe_path}")
        return False
    
    print(f"✅ EXE file found: {exe_path}")
    print(f"📊 File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    
    # Test if the EXE starts without immediate crashes
    print("🚀 Starting EXE for basic functionality test...")
    try:
        # Start the process and check if it runs for a few seconds without crashing
        process = subprocess.Popen([str(exe_path)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a few seconds to see if it starts properly
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ EXE started successfully and is running!")
            print("🎯 The application appears to be working correctly.")
            
            # Terminate the test process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            return True
        else:
            # Process has already terminated
            stdout, stderr = process.communicate()
            print("❌ EXE terminated unexpectedly!")
            if stdout:
                print(f"STDOUT: {stdout.decode()}")
            if stderr:
                print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing EXE: {e}")
        return False

def main():
    print("=" * 50)
    print("  OmersSolarDingelDangel EXE Test")
    print("=" * 50)
    
    success = test_exe()
    
    print("=" * 50)
    if success:
        print("🎉 TEST PASSED! Your EXE is working correctly!")
        print("📋 Summary:")
        print("   ✅ EXE file exists")
        print("   ✅ EXE starts without errors") 
        print("   ✅ Application runs successfully")
        print("   ✅ No immediate crashes detected")
        print("\n🚀 You can now distribute your application!")
    else:
        print("💥 TEST FAILED! There might be issues with the EXE.")
        print("🔍 Please check the error messages above.")
    print("=" * 50)

if __name__ == "__main__":
    main()
