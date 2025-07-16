"""
Build script without Google module conflicts
"""
import os
import subprocess
import sys
import shutil
from pathlib import Path

def main():
    print("🔧 Building OmersSolarDingelDangel without Google conflicts...")
    
    # Get the project root directory
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    try:
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
    except PermissionError:
        print("⚠️ Warning: Could not remove dist directory (in use)")
    
    try:
        if build_dir.exists():
            shutil.rmtree(build_dir)
    except PermissionError:
        print("⚠️ Warning: Could not remove build directory (in use)")
    
    # Create dist directory
    dist_dir.mkdir(exist_ok=True)
    
    # Create a temporary launcher that excludes problematic modules
    launcher_content = '''#!/usr/bin/env python3
"""
Safe launcher for OmersSolarDingelDangel without Google module conflicts
"""

import sys
import os
import traceback

def main():
    """Main entry point for the standalone application."""
    print("🚀 OmersSolarDingelDangel Starting (Safe Mode)...")
    
    try:
        # Add the current directory to the Python path
        if hasattr(sys, '_MEIPASS'):
            # Running in PyInstaller bundle
            bundle_dir = sys._MEIPASS
            print(f"📦 Running from PyInstaller bundle: {bundle_dir}")
        else:
            # Running normally
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Add bundle directory to sys.path
        sys.path.insert(0, bundle_dir)
        
        # Set environment variables for Streamlit
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
        os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'false'
        os.environ['STREAMLIT_LOGGER_LEVEL'] = 'warning'
        
        print("📋 Importing required modules...")
        
        # Import Streamlit directly without google conflicts
        import streamlit.web.cli as st_cli
        
        print("✅ Streamlit imported successfully")
        
        # Get the path to the GUI file
        gui_file_path = os.path.join(bundle_dir, 'omerssolar', 'gui.py')
        if not os.path.exists(gui_file_path):
            # Try alternative paths
            alt_paths = [
                os.path.join(bundle_dir, 'gui.py'),
                os.path.join(bundle_dir, 'src', 'omerssolar', 'gui.py')
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    gui_file_path = alt_path
                    break
        
        print(f"📄 GUI file path: {gui_file_path}")
        
        if not os.path.exists(gui_file_path):
            raise FileNotFoundError(f"GUI file not found at: {gui_file_path}")
        
        # Prepare Streamlit command line arguments
        sys.argv = [
            'streamlit',
            'run',
            gui_file_path,
            '--server.headless=true',
            '--browser.gatherUsageStats=false',
            '--server.runOnSave=false',
            '--logger.level=warning',
            '--server.port=8501',
            '--server.address=localhost'
        ]
        
        print("🌐 Starting Streamlit application...")
        print("🔗 The application will open in your default web browser")
        print("📍 If it doesn't open automatically, go to: http://localhost:8501")
        
        # Start Streamlit
        st_cli.main()
        
    except KeyboardInterrupt:
        print("\\n⏹️ Application stopped by user")
        return 0
    except Exception as e:
        print(f"\\n❌ Error starting application: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        print("📋 Full traceback:")
        traceback.print_exc()
        
        # Keep console open for debugging
        try:
            input("\\n📌 Press Enter to exit...")
        except:
            pass
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    safe_launcher_path = src_dir / "safe_launcher.py"
    with open(safe_launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print(f"📝 Created safe launcher: {safe_launcher_path}")
    
    # Run PyInstaller with the safe launcher
    print("🔥 Building EXE with safe launcher...")
    
    icon_path = src_dir / "omerssolar" / "assets" / "Omer.ico"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",  # Use console for debugging
        "--name=OmersSolarDingelDangel_Safe",
        f"--icon={icon_path}",
        "--clean",
        "--noconfirm",
        
        # Collect streamlit without protobuf conflicts
        "--collect-data=streamlit",
        "--copy-metadata=streamlit",
        
        # Other essential packages
        "--collect-data=altair",
        "--collect-data=pandas",
        "--collect-data=numpy",
        "--copy-metadata=altair",
        "--copy-metadata=pandas", 
        "--copy-metadata=numpy",
        "--copy-metadata=importlib_metadata",
        
        # Hidden imports for Streamlit (minimal set)
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=streamlit.web.server",
        "--hidden-import=streamlit.runtime",
        "--hidden-import=streamlit.components.v1",
        "--hidden-import=streamlit.delta_generator",
        "--hidden-import=streamlit.config",
        "--hidden-import=streamlit.logger",
        
        # Core Python imports
        "--hidden-import=importlib_metadata",
        "--hidden-import=pkg_resources",
        "--hidden-import=click",
        "--hidden-import=tornado",
        "--hidden-import=watchdog",
        "--hidden-import=validators",
        "--hidden-import=toml",
        "--hidden-import=altair",
        "--hidden-import=numpy",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        
        # Our application modules (excluding google module)
        "--hidden-import=omerssolar.gui",
        "--hidden-import=omerssolar.database",
        "--hidden-import=omerssolar.calculations",
        "--hidden-import=omerssolar.analysis",
        "--hidden-import=omerssolar.product_db",
        "--hidden-import=omerssolar.pdf_generator",
        
        # Add data files
        f"--add-data={src_dir / 'omerssolar' / 'assets'};omerssolar/assets",
        f"--add-data={src_dir / 'omerssolar' / 'de.json'};omerssolar",
        f"--add-data={src_dir / 'omerssolar' / 'settings.json'};omerssolar",
        f"--add-data={src_dir / 'omerssolar' / 'gui.py'};omerssolar",
        f"--add-data={src_dir / 'omerssolar' / 'database.py'};omerssolar",
        f"--add-data={src_dir / 'omerssolar' / 'calculations.py'};omerssolar",
        f"--add-data={src_dir / 'omerssolar' / 'analysis.py'};omerssolar",
        f"--add-data={src_dir / 'omerssolar' / 'product_db.py'};omerssolar",
        f"--add-data={src_dir / 'omerssolar' / 'pdf_generator.py'};omerssolar",
        
        # Exclude problematic modules
        "--exclude-module=google",
        "--exclude-module=google.genai",
        "--exclude-module=googles",
        
        # Paths
        f"--paths={src_dir}",
        f"--paths={src_dir / 'omerssolar'}",
        
        # Main script (the safe launcher)
        str(safe_launcher_path)
    ]
    
    try:
        subprocess.run(cmd, cwd=project_root, check=True)
        
        print("✅ EXE file created successfully!")
        print(f"📍 Location: {dist_dir / 'OmersSolarDingelDangel_Safe.exe'}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building EXE: {e}")
        return False
    finally:
        # Clean up temporary launcher
        if safe_launcher_path.exists():
            safe_launcher_path.unlink()

if __name__ == "__main__":
    success = main()
    if success:
        print("\\n🎉 Build completed successfully!")
        print("🔧 This version should avoid Google module conflicts.")
    else:
        print("\\n💥 Build failed. Please check the errors above.")
        sys.exit(1)
