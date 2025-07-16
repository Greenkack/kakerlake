"""
PyInstaller hook for streamlit - fixes metadata issues
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

# Collect all streamlit data files
datas = collect_data_files('streamlit')

# Collect streamlit metadata
datas += copy_metadata('streamlit')

# Collect all streamlit submodules
hiddenimports = collect_submodules('streamlit')

# Additional hidden imports that are often missed
hiddenimports += [
    'streamlit.web.cli',
    'streamlit.web.server.server',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.state.session_state',
    'streamlit.components.v1.components',
    'streamlit.delta_generator',
    'streamlit.file_util',
    'streamlit.source_util',
    'streamlit.util',
    'streamlit.logger',
    'streamlit.config',
    'streamlit.errors',
    'streamlit.version',
    'streamlit._is_running_with_streamlit',
    'importlib_metadata',
    'pkg_resources',
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
    'idna',
    'altair',
    'numpy',
    'pandas',
]
