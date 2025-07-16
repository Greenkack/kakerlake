"""
Build script to create EXE file for OmersSolarDingelDangel using wheel and PyInstaller
"""
import os
import subprocess
import sys
import shutil
from pathlib import Path

def main():
    print("🔨 Starting OmersSolarDingelDangel EXE build process...")
    
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
    
    # Create wheel package
    print("📦 Building wheel package...")
    try:
        subprocess.run([sys.executable, "-m", "build", "--wheel"], 
                      cwd=project_root, check=True)
        print("✅ Wheel package created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building wheel: {e}")
        return False
    
    # Install the wheel in development mode
    print("📥 Installing package in development mode...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                      cwd=project_root, check=True)
        print("✅ Package installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing package: {e}")
        return False    # Create PyInstaller spec for better control
    print("📝 Creating PyInstaller spec file...")
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect streamlit data and submodules
streamlit_datas = collect_data_files('streamlit')
streamlit_hiddenimports = collect_submodules('streamlit')

a = Analysis(
    [r'{src_dir / "omerssolar" / "gui.py"}'],
    pathex=[r'{project_root}'],
    binaries=[],
    datas=[
        (r'{src_dir / "omerssolar" / "assets"}', 'omerssolar/assets'),
        (r'{src_dir / "omerssolar" / "de.json"}', 'omerssolar'),
        (r'{src_dir / "omerssolar" / "settings.json"}', 'omerssolar'),
    ] + streamlit_datas,
    hiddenimports=[
        'streamlit',
        'streamlit.web',
        'streamlit.web.cli',
        'streamlit.web.server',
        'streamlit.runtime',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.state',
        'streamlit.components',
        'streamlit.components.v1',
        'streamlit.delta_generator',
        'streamlit.errors',
        'streamlit.logger',
        'streamlit.config',
        'streamlit.file_util',
        'streamlit.source_util',
        'streamlit.util',
        'streamlit.version',
        'streamlit._is_running_with_streamlit',
        'altair',
        'numpy',
        'pandas',
        'openpyxl',
        'omerssolar',
        'omerssolar.database',
        'omerssolar.calculations',
        'omerssolar.analysis',
        'omerssolar.product_db',
        'omerssolar.pdf_generator',
        'pkg_resources',
        'importlib_metadata',
        'click',
        'tornado',
        'watchdog',
        'validators',
        'toml',
        'pyarrow',
        'gitpython',
        'pydeck',
        'tzlocal',
        'cachetools',
        'blinker',
        'packaging',
        'protobuf',
        'pillow',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',    ] + streamlit_hiddenimports,
    hookspath=[r'{project_root}'],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OmersSolarDingelDangel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{src_dir / "omerssolar" / "assets" / "Omer.ico"}',
)
'''
    
    spec_file = project_root / "OmersSolarDingelDangel.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ PyInstaller spec file created!")
    
    # Run PyInstaller
    print("🔥 Building EXE with PyInstaller...")
    try:
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ], cwd=project_root, check=True)
        
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
