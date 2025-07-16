"""
Alternative build script for OmersSolarDingelDangel with direct PyInstaller approach
"""
import os
import subprocess
import sys
import shutil
from pathlib import Path

def main():
    print("🔨 Starting alternative OmersSolarDingelDangel EXE build process...")
    
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
    
    # Run PyInstaller with extensive parameters
    print("🔥 Building EXE with PyInstaller (direct approach)...")
    
    gui_path = src_dir / "omerssolar" / "gui.py"
    icon_path = src_dir / "omerssolar" / "assets" / "Omer.ico"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=OmersSolarDingelDangel",
        f"--icon={icon_path}",
        "--clean",
        "--noconfirm",
        
        # Collect all streamlit data and modules
        "--collect-data=streamlit",
        "--collect-submodules=streamlit",
        "--copy-metadata=streamlit",
        
        # Additional data collection
        "--collect-data=altair",
        "--collect-data=pandas",
        "--collect-data=numpy",
        "--collect-data=pyarrow",
        "--copy-metadata=altair",
        "--copy-metadata=pandas",
        "--copy-metadata=numpy",
        "--copy-metadata=pyarrow",
        
        # Hidden imports
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=streamlit.web.server",
        "--hidden-import=streamlit.runtime",
        "--hidden-import=streamlit.runtime.scriptrunner",
        "--hidden-import=streamlit.runtime.state",
        "--hidden-import=streamlit.components.v1",
        "--hidden-import=streamlit.delta_generator",
        "--hidden-import=streamlit.errors",
        "--hidden-import=streamlit.logger",
        "--hidden-import=streamlit.config",
        "--hidden-import=streamlit.file_util",
        "--hidden-import=streamlit.source_util",
        "--hidden-import=streamlit.util",
        "--hidden-import=streamlit.version",
        "--hidden-import=streamlit._is_running_with_streamlit",
        "--hidden-import=importlib_metadata",
        "--hidden-import=pkg_resources",
        "--hidden-import=click",
        "--hidden-import=tornado",
        "--hidden-import=watchdog",
        "--hidden-import=validators",
        "--hidden-import=toml",
        "--hidden-import=pyarrow",
        "--hidden-import=gitpython",
        "--hidden-import=pydeck",
        "--hidden-import=tzlocal",
        "--hidden-import=cachetools",
        "--hidden-import=blinker",
        "--hidden-import=packaging",
        "--hidden-import=protobuf",
        "--hidden-import=pillow",
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        "--hidden-import=certifi",
        "--hidden-import=charset_normalizer",
        "--hidden-import=idna",
        "--hidden-import=altair",
        "--hidden-import=numpy",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=omerssolar",
        "--hidden-import=omerssolar.database",
        "--hidden-import=omerssolar.calculations",
        "--hidden-import=omerssolar.analysis",
        "--hidden-import=omerssolar.product_db",
        "--hidden-import=omerssolar.pdf_generator",
        
        # Add data files
        f"--add-data={src_dir / 'omerssolar' / 'assets'};omerssolar/assets",
        f"--add-data={src_dir / 'omerssolar' / 'de.json'};omerssolar",
        f"--add-data={src_dir / 'omerssolar' / 'settings.json'};omerssolar",
        
        # Hook path
        f"--additional-hooks-dir={project_root}",
        
        # Main script
        str(gui_path)
    ]
    
    try:
        subprocess.run(cmd, cwd=project_root, check=True)
        
        print("✅ EXE file created successfully!")
        print(f"📍 Location: {dist_dir / 'OmersSolarDingelDangel.exe'}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building EXE: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Build completed successfully!")
        print("Your EXE file is ready in the 'dist' folder.")
    else:
        print("\n💥 Build failed. Please check the errors above.")
        sys.exit(1)
