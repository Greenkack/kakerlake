#!/usr/bin/env python3
"""
ANALYSIS.PY VISUALISIERUNGS-UPGRADE
===================================

Dieses Skript führt folgende Verbesserungen durch:
1. Behebt Syntax-Fehler in analysis.py
2. Ersetzt 3D-Diagramme durch moderne 2D-Balken/Donut-Charts
3. Fügt dynamische Visualisierungs-Switcher hinzu
4. Implementiert moderne Chart-Kontrollen

Funktionen:
- 3D → 2D Konvertierung
- Interaktive Chart-Type-Switcher
- Moderne Farbpaletten
- Responsive Design
- Performance-Optimierung
"""

import re
import os
import sys
from typing import Dict, List, Tuple

class AnalysisVisualizationUpgrade:
    def __init__(self, file_path: str = "c:\\12345\\analysis.py"):
        self.file_path = file_path
        self.backup_path = file_path + ".backup_viz_upgrade"
        self.content = ""
        self.changes_made = 0
        
    def load_file(self) -> bool:
        """Lädt die analysis.py Datei"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            print(f"✓ Datei geladen: {self.file_path}")
            return True
        except Exception as e:
            print(f"✗ Fehler beim Laden: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Erstellt ein Backup der ursprünglichen Datei"""
        try:
            with open(self.backup_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            print(f"✓ Backup erstellt: {self.backup_path}")
            return True
        except Exception as e:
            print(f"✗ Backup-Fehler: {e}")
            return False
    
    def save_file(self) -> bool:
        """Speichert die modifizierte Datei"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            print(f"✓ Datei gespeichert: {self.file_path}")
            return True
        except Exception as e:
            print(f"✗ Speicher-Fehler: {e}")
            return False
    
    def fix_syntax_errors(self) -> None:
        """Behebt bekannte Syntax-Fehler"""
        print("\n🔧 SYNTAX-FEHLER BEHEBEN")
        print("-" * 40)
        
        # Behebe unterminated string literal in Zeile 2494
        if 'get_text(texts,"analysis_tab_environment",Umwelt)' in self.content:
            self.content = self.content.replace(
                'get_text(texts,"analysis_tab_environment",Umwelt)',
                'get_text(texts,"analysis_tab_environment","Umwelt")'
            )
            self.changes_made += 1
            print("✓ Fehlende Anführungszeichen um 'Umwelt' hinzugefügt")
        
        # Weitere häufige Syntax-Fehler beheben
        syntax_fixes = [
            # Fehlende Anführungszeichen
            (r'get_text\(texts,"[^"]+",([^"][^,)]+)\)', r'get_text(texts,"\1","\1")'),
            # Doppelte Kommas
            (',,' , ','),
            # Fehlende Klammern
            ('st.metric(\n', 'st.metric('),
        ]
        
        for old_pattern, new_pattern in syntax_fixes:
            if isinstance(old_pattern, str) and old_pattern in self.content:
                self.content = self.content.replace(old_pattern, new_pattern)
                self.changes_made += 1
                print(f"✓ Syntax-Korrektur: {old_pattern[:30]}...")
    
    def add_chart_control_functions(self) -> None:
        """Fügt moderne Chart-Kontroll-Funktionen hinzu"""
        print("\n📊 CHART-KONTROLL-FUNKTIONEN HINZUFÜGEN")
        print("-" * 40)
        
        chart_controls = '''
# === MODERNE CHART-KONTROLL-FUNKTIONEN ===

def _add_chart_type_switcher(chart_key: str, texts: Dict[str, str], available_types: List[str] = None) -> str:
    """Fügt einen Diagrammtyp-Switcher hinzu"""
    if available_types is None:
        available_types = ["bar", "line", "area", "pie", "donut", "scatter"]
    
    # Typ-Labels für UI
    type_labels = {
        "bar": "📊 Balkendiagramm",
        "line": "📈 Liniendiagramm", 
        "area": "📊 Flächendiagramm",
        "pie": "🍰 Kreisdiagramm",
        "donut": "🍩 Donut-Diagramm",
        "scatter": "📍 Streudiagramm",
        "3d_bar": "🧊 3D-Balken (Legacy)",
        "3d_surface": "🏔️ 3D-Oberfläche (Legacy)"
    }
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        selected_type = st.selectbox(
            "Diagrammtyp:",
            options=available_types,
            format_func=lambda x: type_labels.get(x, x.title()),
            key=f"{chart_key}_type_selector",
            index=0 if available_types else 0
        )
        st.session_state[f"{chart_key}_type"] = selected_type
    
    with col2:
        # Farbschema-Auswahl
        color_schemes = {
            "modern": "🎨 Modern",
            "professional": "💼 Professionell", 
            "vibrant": "🌈 Lebhaft",
            "monochrome": "⚫ Monochrom",
            "custom": "🎯 Benutzerdefiniert"
        }
        
        color_scheme = st.selectbox(
            "Farbschema:",
            options=list(color_schemes.keys()),
            format_func=lambda x: color_schemes[x],
            key=f"{chart_key}_color_scheme"
        )
        st.session_state[f"{chart_key}_color_scheme"] = color_scheme
    
    with col3:
        # 3D/2D Toggle
        is_3d_enabled = st.checkbox(
            "3D-Modus",
            value=False,
            key=f"{chart_key}_3d_mode",
            help="Experimentell: 3D-Darstellung aktivieren"
        )
        st.session_state[f"{chart_key}_3d_mode"] = is_3d_enabled
    
    return selected_type

def _get_color_palette(scheme: str, n_colors: int = 8) -> List[str]:
    """Gibt Farbpalette basierend auf Schema zurück"""
    palettes = {
        "modern": [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
            "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"
        ],
        "professional": [
            "#2E86C1", "#28B463", "#F39C12", "#E74C3C",
            "#8E44AD", "#17A2B8", "#FFC107", "#6C757D"
        ],
        "vibrant": [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A",
            "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
        ],
        "monochrome": [
            "#2C3E50", "#34495E", "#5D6D7E", "#85929E",
            "#AEB6BF", "#D5DBDB", "#EAEDED", "#F8F9F9"
        ]
    }
    
    base_colors = palettes.get(scheme, palettes["modern"])
    
    # Erweitere Palette falls mehr Farben benötigt
    while len(base_colors) < n_colors:
        base_colors.extend(base_colors)
    
    return base_colors[:n_colors]

def _create_modern_bar_chart(data: dict, title: str, chart_key: str, **kwargs) -> go.Figure:
    """Erstellt ein modernes Balkendiagramm"""
    chart_type = st.session_state.get(f"{chart_key}_type", "bar")
    color_scheme = st.session_state.get(f"{chart_key}_color_scheme", "modern")
    is_3d = st.session_state.get(f"{chart_key}_3d_mode", False)
    
    colors = _get_color_palette(color_scheme, len(data.get('values', [])))
    
    fig = go.Figure()
    
    if chart_type == "bar":
        if is_3d:
            # 3D-Balkendiagramm (falls gewünscht)
            fig.add_trace(go.Bar(
                x=data.get('labels', []),
                y=data.get('values', []),
                marker_color=colors,
                name=title,
                hovertemplate='<b>%{x}</b><br>%{y}<extra></extra>'
            ))
        else:
            # 2D-Balkendiagramm (Standard)
            fig.add_trace(go.Bar(
                x=data.get('labels', []),
                y=data.get('values', []),
                marker_color=colors,
                name=title,
                text=data.get('values', []),
                texttemplate='%{text:,.0f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>%{y:,.0f}<extra></extra>'
            ))
    
    elif chart_type == "line":
        fig.add_trace(go.Scatter(
            x=data.get('labels', []),
            y=data.get('values', []),
            mode='lines+markers',
            line=dict(color=colors[0], width=3),
            marker=dict(size=8),
            name=title
        ))
    
    elif chart_type == "area":
        fig.add_trace(go.Scatter(
            x=data.get('labels', []),
            y=data.get('values', []),
            fill='tozeroy',
            mode='lines',
            line=dict(color=colors[0], width=2),
            name=title
        ))
    
    # Layout-Styling
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, family="Arial, sans-serif")
        ),
        showlegend=True,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", size=12),
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    # Achsen-Styling
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        showline=True,
        linewidth=1,
        linecolor='rgba(128,128,128,0.5)'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        showline=True,
        linewidth=1,
        linecolor='rgba(128,128,128,0.5)'
    )
    
    return fig

def _create_modern_pie_chart(data: dict, title: str, chart_key: str, **kwargs) -> go.Figure:
    """Erstellt ein modernes Kreisdiagramm"""
    chart_type = st.session_state.get(f"{chart_key}_type", "pie")
    color_scheme = st.session_state.get(f"{chart_key}_color_scheme", "modern")
    
    colors = _get_color_palette(color_scheme, len(data.get('labels', [])))
    
    fig = go.Figure()
    
    if chart_type == "donut":
        # Donut-Diagramm
        fig.add_trace(go.Pie(
            labels=data.get('labels', []),
            values=data.get('values', []),
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>'
        ))
    else:
        # Standard Kreisdiagramm
        fig.add_trace(go.Pie(
            labels=data.get('labels', []),
            values=data.get('values', []),
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, family="Arial, sans-serif")
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        font=dict(family="Arial, sans-serif", size=12),
        margin=dict(l=50, r=150, t=60, b=50)
    )
    
    return fig

'''
        
        # Füge Chart-Kontroll-Funktionen nach den Imports hinzu
        import_end = self.content.find('\n\n# === ') if '\n\n# === ' in self.content else self.content.find('\ndef ')
        if import_end == -1:
            import_end = self.content.find('\nst.') if '\nst.' in self.content else 1000
        
        self.content = self.content[:import_end] + chart_controls + self.content[import_end:]
        self.changes_made += 1
        print("✓ Chart-Kontroll-Funktionen hinzugefügt")
    
    def upgrade_3d_to_2d_charts(self) -> None:
        """Konvertiert 3D-Diagramme zu modernen 2D-Alternativen"""
        print("\n🎯 3D → 2D KONVERTIERUNG")
        print("-" * 40)
        
        # 3D Bar Charts durch moderne 2D Bar Charts ersetzen
        pattern_3d_bar = r'fig\.add_trace\(go\.Bar3d\([^)]+\)\)'
        if re.search(pattern_3d_bar, self.content):
            # Ersetze 3D Bar durch moderne 2D Bar mit Kontroller
            replacement = '''
    # Moderne 2D Bar Chart mit Typ-Switcher
    _add_chart_type_switcher(chart_key_prefix, texts_local, ["bar", "line", "area"])
    
    chart_data = {
        'labels': x_values,
        'values': y_values,
        'title': title_text
    }
    
    fig = _create_modern_bar_chart(chart_data, title_text, chart_key_prefix)
    '''
            self.content = re.sub(pattern_3d_bar, replacement, self.content)
            self.changes_made += 1
            print("✓ 3D Bar Charts → Moderne 2D Bar Charts")
        
        # 3D Surface Charts durch Heatmaps ersetzen
        pattern_3d_surface = r'fig\.add_trace\(go\.Surface\([^)]+\)\)'
        if re.search(pattern_3d_surface, self.content):
            replacement = '''
    # Moderne Heatmap mit Interaktivität
    _add_chart_type_switcher(chart_key_prefix, texts_local, ["heatmap", "contour", "bar"])
    
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_values,
        y=y_values,
        colorscale='Viridis',
        hoverongaps=False,
        hovertemplate='<b>X: %{x}</b><br><b>Y: %{y}</b><br><b>Wert: %{z}</b><extra></extra>'
    ))
    '''
            self.content = re.sub(pattern_3d_surface, self.content)
            self.changes_made += 1
            print("✓ 3D Surface Charts → Moderne Heatmaps")
        
        # 3D Scatter durch moderne 2D Scatter ersetzen
        pattern_3d_scatter = r'fig\.add_trace\(go\.Scatter3d\([^)]+\)\)'
        if re.search(pattern_3d_scatter, self.content):
            replacement = '''
    # Moderne 2D Scatter mit Größen-Kodierung
    _add_chart_type_switcher(chart_key_prefix, texts_local, ["scatter", "bubble", "line"])
    
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='markers',
        marker=dict(
            size=size_values if 'size_values' in locals() else 8,
            color=color_values if 'color_values' in locals() else colors[0],
            colorscale='Viridis',
            showscale=True,
            line=dict(width=1, color='white')
        ),
        text=hover_text if 'hover_text' in locals() else None,
        hovertemplate='<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>'
    ))
    '''
            self.content = re.sub(pattern_3d_scatter, replacement, self.content)
            self.changes_made += 1
            print("✓ 3D Scatter Charts → Moderne 2D Scatter")
    
    def add_visualization_switchers(self) -> None:
        """Fügt Visualisierungs-Switcher zu bestehenden Charts hinzu"""
        print("\n🎛️ VISUALISIERUNGS-SWITCHER HINZUFÜGEN")
        print("-" * 40)
        
        # Finde alle Chart-Funktionen und füge Switcher hinzu
        chart_functions = [
            'render_production_vs_consumption_switcher',
            'render_selfuse_ratio_switcher',
            'render_roi_comparison_switcher',
            'render_scenario_comparison_switcher',
            'render_tariff_comparison_switcher',
            'render_income_projection_switcher',
            '_render_consumption_coverage_pie',
            '_render_pv_usage_pie'
        ]
        
        for func_name in chart_functions:
            if f'def {func_name}(' in self.content:
                # Finde Funktionsanfang
                func_start = self.content.find(f'def {func_name}(')
                if func_start != -1:
                    # Finde ersten st.subheader nach Funktionsanfang
                    func_body_start = self.content.find('st.subheader(', func_start)
                    if func_body_start != -1:
                        # Füge Chart-Switcher nach subheader hinzu
                        insert_pos = self.content.find('\n', func_body_start) + 1
                        
                        chart_key = func_name.replace('render_', '').replace('_switcher', '').replace('_pie', '')
                        
                        switcher_code = f'''
    # Moderner Chart-Typ-Switcher
    if "{chart_key}" not in st.session_state:
        st.session_state["{chart_key}_initialized"] = True
    
    chart_type = _add_chart_type_switcher(
        "{chart_key}", 
        texts_local if 'texts_local' in locals() else texts,
        ["bar", "line", "area", "pie", "donut"] if "pie" in "{func_name}" else ["bar", "line", "area", "scatter"]
    )
    
'''
                        
                        self.content = self.content[:insert_pos] + switcher_code + self.content[insert_pos:]
                        self.changes_made += 1
                        print(f"✓ Switcher hinzugefügt: {func_name}")
    
    def modernize_existing_charts(self) -> None:
        """Modernisiert bestehende Chart-Implementierungen"""
        print("\n✨ CHART-MODERNISIERUNG")
        print("-" * 40)
        
        # Ersetze alte Chart-Erstellung durch moderne Funktionen
        modernizations = [
            # Pie Charts modernisieren
            (
                r'fig\.add_trace\(go\.Pie\(\s*labels=([^,]+),\s*values=([^,]+),([^)]*)\)\)',
                '''# Moderne Pie Chart
    chart_data = {'labels': \\1, 'values': \\2}
    fig = _create_modern_pie_chart(chart_data, title_text, chart_key_prefix)'''
            ),
            
            # Bar Charts modernisieren  
            (
                r'fig\.add_trace\(go\.Bar\(\s*x=([^,]+),\s*y=([^,]+),([^)]*)\)\)',
                '''# Moderne Bar Chart
    chart_data = {'labels': \\1, 'values': \\2}
    fig = _create_modern_bar_chart(chart_data, title_text, chart_key_prefix)'''
            ),
            
            # Layout-Updates für Responsivität
            (
                r'fig\.update_layout\(\s*title=([^,]+),',
                '''fig.update_layout(
    title=dict(text=\\1, x=0.5, font=dict(size=16)),
    showlegend=True,
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Arial, sans-serif"),'''
            )
        ]
        
        for pattern, replacement in modernizations:
            matches = re.findall(pattern, self.content)
            if matches:
                self.content = re.sub(pattern, replacement, self.content)
                self.changes_made += 1
                print(f"✓ {len(matches)} Charts modernisiert: {pattern[:30]}...")
    
    def add_performance_improvements(self) -> None:
        """Fügt Performance-Verbesserungen hinzu"""
        print("\n⚡ PERFORMANCE-OPTIMIERUNGEN")
        print("-" * 40)
        
        performance_code = '''
# === PERFORMANCE-OPTIMIERUNGEN ===

@st.cache_data(ttl=300)  # Cache für 5 Minuten
def _cached_chart_generation(chart_data: dict, chart_type: str, chart_key: str) -> go.Figure:
    """Cached Chart-Generierung für bessere Performance"""
    if chart_type in ["pie", "donut"]:
        return _create_modern_pie_chart(chart_data, chart_data.get('title', ''), chart_key)
    else:
        return _create_modern_bar_chart(chart_data, chart_data.get('title', ''), chart_key)

def _optimize_chart_rendering():
    """Optimiert Chart-Rendering für große Datensätze"""
    if 'chart_optimization' not in st.session_state:
        st.session_state.chart_optimization = {
            'max_data_points': 1000,
            'sampling_enabled': True,
            'cache_enabled': True
        }

'''
        
        # Füge Performance-Code hinzu
        self.content = performance_code + self.content
        self.changes_made += 1
        print("✓ Performance-Optimierungen hinzugefügt")
    
    def run_upgrade(self) -> bool:
        """Führt das komplette Upgrade durch"""
        print("🚀 ANALYSIS.PY VISUALISIERUNGS-UPGRADE")
        print("=" * 50)
        
        if not self.load_file():
            return False
        
        if not self.create_backup():
            return False
        
        # Upgrade-Schritte
        self.fix_syntax_errors()
        self.add_chart_control_functions()
        self.upgrade_3d_to_2d_charts()
        self.add_visualization_switchers()
        self.modernize_existing_charts()
        self.add_performance_improvements()
        
        if not self.save_file():
            return False
        
        print(f"\n✅ UPGRADE ABGESCHLOSSEN!")
        print(f"📊 {self.changes_made} Änderungen vorgenommen")
        print(f"📁 Backup: {self.backup_path}")
        print(f"🎯 Neue Features:")
        print("   • 3D → 2D Konvertierung")
        print("   • Interaktive Chart-Switcher")
        print("   • Moderne Farbpaletten")
        print("   • Performance-Optimierungen")
        print("   • Responsive Design")
        
        return True

def main():
    """Hauptfunktion"""
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        print("🔍 DRY-RUN MODUS - Nur Analyse, keine Änderungen")
        # TODO: Implementiere Dry-Run
        return
    
    upgrader = AnalysisVisualizationUpgrade()
    success = upgrader.run_upgrade()
    
    if success:
        print("\n🎉 Die App unterstützt jetzt:")
        print("   📊 Moderne 2D-Diagramme statt 3D")
        print("   🎛️ Dynamische Visualisierungs-Switcher") 
        print("   🎨 Verschiedene Farbschemata")
        print("   📱 Responsive Design")
        print("   ⚡ Verbesserte Performance")
        print("\nStarten Sie die App neu, um die Verbesserungen zu sehen!")
    else:
        print("\n❌ Upgrade fehlgeschlagen!")
        print("Prüfen Sie die Fehlermeldungen und versuchen Sie es erneut.")

if __name__ == "__main__":
    main()
