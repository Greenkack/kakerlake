"""
CRM Pipeline UI Module
Autor: Gemini Ultra
Datum: 2025-06-21
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

try:
    from database import get_db_connection, get_all_active_customers
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

class CRMPipeline:
    """CRM Pipeline Management für Sales-Prozess"""
    
    def __init__(self):
        self.pipeline_stages = {
            'lead': {
                'name': 'Lead',
                'description': 'Neuer Interessent',
                'color': '#94A3B8',
                'icon': '🎯',
                'order': 1
            },
            'qualified': {
                'name': 'Qualifiziert',
                'description': 'Lead wurde qualifiziert',
                'color': '#3B82F6',
                'icon': '✅',
                'order': 2
            },
            'proposal': {
                'name': 'Angebot',
                'description': 'Angebot wurde erstellt',
                'color': '#F59E0B',
                'icon': '📄',
                'order': 3
            },
            'negotiation': {
                'name': 'Verhandlung',
                'description': 'In Verhandlung',
                'color': '#8B5CF6',
                'icon': '🤝',
                'order': 4
            },
            'won': {
                'name': 'Gewonnen',
                'description': 'Auftrag gewonnen',
                'color': '#10B981',
                'icon': '🎉',
                'order': 5
            },
            'lost': {
                'name': 'Verloren',
                'description': 'Auftrag verloren',
                'color': '#EF4444',
                'icon': '❌',
                'order': 6
            }
        }
        
        self.lead_sources = [
            'Website', 'Empfehlung', 'Social Media', 'Kaltakquise',
            'Messe', 'Online-Werbung', 'Printmedien', 'Sonstiges'
        ]
    
    def render_pipeline_interface(self, texts: Dict[str, str]):
        """Rendert die Pipeline-Hauptoberfläche"""
        st.header("CRM Sales Pipeline")
        
        if not DATABASE_AVAILABLE:
            st.error("Datenbankverbindung nicht verfügbar")
            return
        
        # Tabs für verschiedene Ansichten
        tab1, tab2, tab3, tab4 = st.tabs(["Pipeline-Übersicht", "Neuer Lead", "Lead-Liste", "Analytics"])
        
        with tab1:
            self._render_pipeline_overview()
        
        with tab2:
            self._render_new_lead_form()
        
        with tab3:
            self._render_lead_list()
        
        with tab4:
            self._render_pipeline_analytics()
    
    def _render_pipeline_overview(self):
        """Rendert die Pipeline-Übersicht im Kanban-Stil"""
        st.subheader("Pipeline-Übersicht")
        
        # Pipeline-Statistiken
        stats = self._get_pipeline_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Gesamte Leads",
                stats['total_leads'],
                delta=f"+{stats['new_leads_this_month']} diesen Monat"
            )
        
        with col2:
            st.metric(
                "Pipeline-Wert",
                f"{stats['total_pipeline_value']:,.0f} €",
                delta=f"{stats['avg_deal_value']:,.0f} € Ø"
            )
        
        with col3:
            st.metric(
                "Conversion Rate",
                f"{stats['conversion_rate']:.1f}%",
                delta=f"{stats['monthly_conversion_change']:+.1f}%"
            )
        
        with col4:
            st.metric(
                "Ø Verkaufszyklus",
                f"{stats['avg_sales_cycle']} Tage",
                delta=f"{stats['cycle_trend']:+.0f} Tage"
            )
        
        st.markdown("---")
        
        # Kanban-Board
        stages = sorted(self.pipeline_stages.items(), key=lambda x: x[1]['order'])
        active_stages = [(k, v) for k, v in stages if k not in ['won', 'lost']]
        
        # Aktive Pipeline-Stufen
        cols = st.columns(len(active_stages))
        
        for idx, (stage_key, stage_info) in enumerate(active_stages):
            with cols[idx]:
                leads_in_stage = self._get_leads_by_stage(stage_key)
                stage_value = sum(lead.get('estimated_value', 0) for lead in leads_in_stage)
                
                st.markdown(f"""
                    <div style="background-color: {stage_info['color']}20; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                        <h4 style="margin: 0; color: {stage_info['color']};">
                            {stage_info['icon']} {stage_info['name']}
                        </h4>
                        <p style="margin: 5px 0; font-size: 0.8em; color: #666;">
                            {len(leads_in_stage)} Leads • {stage_value:,.0f} €
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Leads in dieser Stufe anzeigen
                for lead in leads_in_stage[:5]:  # Max 5 Leads pro Spalte
                    self._render_pipeline_lead_card(lead, stage_key)
                
                if len(leads_in_stage) > 5:
                    st.caption(f"+ {len(leads_in_stage) - 5} weitere Leads")
        
        # Geschlossene Deals (separate Sektion)
        st.markdown("---")
        st.subheader("Geschlossene Deals (letzte 30 Tage)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            won_leads = self._get_recent_closed_leads('won')
            st.markdown("### Gewonnene Aufträge")
            if won_leads:
                for lead in won_leads[:3]:
                    st.success(f"{lead['company_name']} - {lead['estimated_value']:,.0f} €")
            else:
                st.info("Keine gewonnenen Aufträge in den letzten 30 Tagen")
        
        with col2:
            lost_leads = self._get_recent_closed_leads('lost')
            st.markdown("### Verlorene Aufträge")
            if lost_leads:
                for lead in lost_leads[:3]:
                    st.error(f"{lead['company_name']} - {lead['estimated_value']:,.0f} €")
            else:
                st.info("Keine verlorenen Aufträge in den letzten 30 Tagen")
    
    def _render_pipeline_lead_card(self, lead: Dict[str, Any], stage_key: str):
        """Rendert eine Lead-Karte in der Pipeline"""
        days_in_stage = (datetime.now() - datetime.fromisoformat(lead['stage_changed_at'])).days
        
        with st.container():
            # Lead-Info
            st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 8px; margin: 5px 0; border-radius: 5px; background-color: white;">
                    <strong>{lead['company_name']}</strong><br>
                    <small>{lead['estimated_value']:,.0f} €</small><br>
                    <small>{days_in_stage} Tage in Stufe</small>
                </div>
            """, unsafe_allow_html=True)
            
            # Aktions-Buttons (klein)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👁️", key=f"view_{lead['id']}", help="Details anzeigen"):
                    st.session_state.selected_lead_id = lead['id']
                    st.rerun()
            
            with col2:
                if st.button("➡️", key=f"move_{lead['id']}", help="Stufe ändern"):
                    st.session_state.move_lead_id = lead['id']
                    st.rerun()
    
    def _render_new_lead_form(self):
        """Rendert das Formular für neue Leads"""
        st.subheader("Neuen Lead erstellen")
        
        with st.form("new_lead_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Kontaktdaten")
                company_name = st.text_input("Firmenname *", placeholder="z.B. Mustermann GmbH")
                contact_person = st.text_input("Ansprechpartner *", placeholder="Max Mustermann")
                email = st.text_input("E-Mail", placeholder="max@mustermann.de")
                phone = st.text_input("Telefon", placeholder="+49 123 456789")
                address = st.text_area("Adresse", placeholder="Straße, PLZ Ort")
            
            with col2:
                st.markdown("#### Lead-Details")
                lead_source = st.selectbox("Lead-Quelle *", options=self.lead_sources)
                
                estimated_value = st.number_input(
                    "Geschätzter Auftragswert (€) *",
                    min_value=1000,
                    max_value=1000000,
                    value=25000,
                    step=1000
                )
                
                probability = st.slider(
                    "Abschlusswahrscheinlichkeit (%)",
                    min_value=0,
                    max_value=100,
                    value=50,
                    step=5
                )
                
                expected_close_date = st.date_input(
                    "Erwartetes Abschlussdatum",
                    value=datetime.now().date() + timedelta(days=30)
                )
                
                initial_stage = st.selectbox(
                    "Startstufe",
                    options=['lead', 'qualified'],
                    format_func=lambda x: f"{self.pipeline_stages[x]['icon']} {self.pipeline_stages[x]['name']}"
                )
            
            notes = st.text_area("Notizen", placeholder="Zusätzliche Informationen zum Lead")
            
            submitted = st.form_submit_button("Lead erstellen", type="primary")
            
            if submitted:
                if company_name and contact_person and estimated_value:
                    lead_data = {
                        'company_name': company_name,
                        'contact_person': contact_person,
                        'email': email,
                        'phone': phone,
                        'address': address,
                        'lead_source': lead_source,
                        'estimated_value': estimated_value,
                        'probability': probability,
                        'expected_close_date': expected_close_date,
                        'stage': initial_stage,
                        'notes': notes
                    }
                    
                    if self._create_lead(lead_data):
                        st.success("Lead wurde erfolgreich erstellt!")
                        st.rerun()
                    else:
                        st.error("Fehler beim Erstellen des Leads")
                else:
                    st.error("Bitte füllen Sie alle Pflichtfelder aus")
    
    def _render_lead_list(self):
        """Rendert die Lead-Liste mit Filter- und Sortieroptionen"""
        st.subheader("Lead-Verwaltung")
        
        # Filter
        col1, col2, col3 = st.columns(3)
        
        with col1:
            stage_filter = st.selectbox(
                "Stufe filtern",
                options=['all'] + list(self.pipeline_stages.keys()),
                format_func=lambda x: "Alle Stufen" if x == 'all' else f"{self.pipeline_stages[x]['icon']} {self.pipeline_stages[x]['name']}"
            )
        
        with col2:
            source_filter = st.selectbox(
                "Quelle filtern",
                options=['all'] + self.lead_sources,
                format_func=lambda x: "Alle Quellen" if x == 'all' else x
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sortieren nach",
                options=['created_at', 'estimated_value', 'probability', 'expected_close_date'],
                format_func=lambda x: {
                    'created_at': 'Erstellungsdatum',
                    'estimated_value': 'Auftragswert',
                    'probability': 'Wahrscheinlichkeit',
                    'expected_close_date': 'Erwartetes Datum'
                }[x]
            )
        
        # Leads laden und anzeigen
        leads = self._get_filtered_leads(stage_filter, source_filter, sort_by)
        
        if leads:
            for lead in leads:
                self._render_lead_detail_card(lead)
        else:
            st.info("Keine Leads gefunden")
    
    def _render_lead_detail_card(self, lead: Dict[str, Any]):
        """Rendert eine detaillierte Lead-Karte"""
        stage_info = self.pipeline_stages[lead['stage']]
        days_in_stage = (datetime.now() - datetime.fromisoformat(lead['stage_changed_at'])).days
        
        with st.expander(f"{stage_info['icon']} {lead['company_name']} - {lead['estimated_value']:,.0f} €", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Kontaktdaten:**")
                st.text(f"{lead['contact_person']}")
                if lead['email']:
                    st.text(f"{lead['email']}")
                if lead['phone']:
                    st.text(f"{lead['phone']}")
                if lead['address']:
                    st.text(f"{lead['address']}")
            
            with col2:
                st.markdown("**Lead-Details:**")
                st.text(f"Quelle: {lead['lead_source']}")
                st.text(f"Wert: {lead['estimated_value']:,.0f} €")
                st.text(f"Wahrscheinlichkeit: {lead['probability']}%")
                st.text(f"Erwarteter Abschluss: {lead['expected_close_date']}")
            
            with col3:
                st.markdown("**Status:**")
                st.text(f"Aktuelle Stufe: {stage_info['name']}")
                st.text(f"⏱{days_in_stage} Tage in dieser Stufe")
                st.text(f"Erstellt: {lead['created_at'][:10]}")
                
                # Gewichteter Wert
                weighted_value = lead['estimated_value'] * lead['probability'] / 100
                st.text(f"Gewichteter Wert: {weighted_value:,.0f} €")
            
            # Notizen
            if lead['notes']:
                st.markdown("**Notizen:**")
                st.text(lead['notes'])
            
            # Aktionen
            st.markdown("---")
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            
            with action_col1:
                if st.button("Bearbeiten", key=f"edit_lead_{lead['id']}"):
                    st.session_state.edit_lead_id = lead['id']
                    st.rerun()
            
            with action_col2:
                next_stage = self._get_next_stage(lead['stage'])
                if next_stage:
                    next_stage_info = self.pipeline_stages[next_stage]
                    if st.button(f"{next_stage_info['name']}", key=f"next_stage_{lead['id']}"):
                        self._update_lead_stage(lead['id'], next_stage)
                        st.success(f"Lead zu '{next_stage_info['name']}' verschoben")
                        st.rerun()
            
            with action_col3:
                if st.button("Verloren", key=f"lost_{lead['id']}"):
                    self._update_lead_stage(lead['id'], 'lost')
                    st.error("Lead als 'Verloren' markiert")
                    st.rerun()
            
            with action_col4:
                if st.button("Löschen", key=f"delete_lead_{lead['id']}"):
                    if self._delete_lead(lead['id']):
                        st.success("Lead gelöscht")
                        st.rerun()
    
    def _render_pipeline_analytics(self):
        """Rendert Pipeline-Analytics und Berichte"""
        st.subheader("Pipeline Analytics")
        
        # Zeitraum-Auswahl
        period = st.selectbox(
            "Analysezeitraum",
            options=['last_30_days', 'last_90_days', 'this_year', 'all_time'],
            format_func=lambda x: {
                'last_30_days': 'Letzte 30 Tage',
                'last_90_days': 'Letzte 90 Tage', 
                'this_year': 'Dieses Jahr',
                'all_time': 'Gesamtzeitraum'
            }[x]
        )
        
        analytics_data = self._get_analytics_data(period)
        
        # KPI-Dashboard
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Neue Leads",
                analytics_data['new_leads'],
                delta=f"{analytics_data['leads_growth']:+.1f}%"
            )
        
        with col2:
            st.metric(
                "Gewonnene Deals",
                analytics_data['won_deals'],
                delta=f"{analytics_data['won_value']:,.0f} €"
            )
        
        with col3:
            st.metric(
                "Conversion Rate",
                f"{analytics_data['conversion_rate']:.1f}%",
                delta=f"{analytics_data['conversion_change']:+.1f}%"
            )
        
        with col4:
            st.metric(
                "Ø Deal-Größe",
                f"{analytics_data['avg_deal_size']:,.0f} €",
                delta=f"{analytics_data['deal_size_change']:+.1f}%"
            )
        
        # Charts
        tab1, tab2, tab3 = st.tabs(["Pipeline-Trichter", "Trend-Analyse", "Quellen-Performance"])
        
        with tab1:
            self._render_pipeline_funnel(analytics_data)
        
        with tab2:
            self._render_trend_analysis(analytics_data)
        
        with tab3:
            self._render_source_performance(analytics_data)
    
    def _render_pipeline_funnel(self, analytics_data: Dict[str, Any]):
        """Rendert den Pipeline-Trichter"""
        st.markdown("#### Pipeline-Trichter")
        
        funnel_data = analytics_data.get('funnel_data', {})
        
        # Einfache Text-Darstellung des Trichters
        stages = ['lead', 'qualified', 'proposal', 'negotiation', 'won']
        
        for i, stage in enumerate(stages):
            stage_info = self.pipeline_stages[stage]
            count = funnel_data.get(stage, 0)
            
            if i == 0:
                conversion = 100.0
            else:
                prev_count = funnel_data.get(stages[i-1], 1)
                conversion = (count / prev_count * 100) if prev_count > 0 else 0
            
            # Balken-Darstellung
            bar_width = max(10, int(conversion))
            bar = "█" * (bar_width // 5)
            
            st.markdown(f"""
                **{stage_info['icon']} {stage_info['name']}**  
                {bar} {count} Leads ({conversion:.1f}%)
            """)
    
    def _render_trend_analysis(self, analytics_data: Dict[str, Any]):
        """Rendert Trend-Analysen"""
        st.markdown("#### Lead-Trends")
        
        trend_data = analytics_data.get('trend_data', {})
        
        # Vereinfachte Trend-Darstellung
        st.markdown("**Monatliche Lead-Entwicklung:**")
        for month, data in trend_data.items():
            st.text(f"{month}: {data['new_leads']} neue Leads, {data['won_deals']} gewonnen")
    
    def _render_source_performance(self, analytics_data: Dict[str, Any]):
        """Rendert Quellen-Performance"""
        st.markdown("####  Lead-Quellen Performance")
        
        source_data = analytics_data.get('source_performance', {})
        
        for source, data in source_data.items():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.text(f"{source}")
            with col2:
                st.text(f"Leads: {data['count']}")
            with col3:
                st.text(f"Conversion: {data['conversion_rate']:.1f}%")
    
    # Helper methods
    def _get_pipeline_statistics(self) -> Dict[str, Any]:
        """Lädt Pipeline-Statistiken"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Basis-Statistiken
            cursor.execute('SELECT COUNT(*) FROM crm_leads WHERE stage NOT IN ("won", "lost")')
            active_leads = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM crm_leads')
            total_leads = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(estimated_value) FROM crm_leads WHERE stage NOT IN ("won", "lost")')
            pipeline_value = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT AVG(estimated_value) FROM crm_leads')
            avg_deal_value = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_leads': total_leads,
                'active_leads': active_leads,
                'total_pipeline_value': pipeline_value,
                'avg_deal_value': avg_deal_value,
                'conversion_rate': 25.5,  # Mock data
                'new_leads_this_month': 12,  # Mock data
                'monthly_conversion_change': 2.3,  # Mock data
                'avg_sales_cycle': 45,  # Mock data
                'cycle_trend': -3  # Mock data
            }
            
        except Exception as e:
            print(f"Fehler beim Laden der Pipeline-Statistiken: {e}")
            return {
                'total_leads': 0, 'active_leads': 0, 'total_pipeline_value': 0,
                'avg_deal_value': 0, 'conversion_rate': 0, 'new_leads_this_month': 0,
                'monthly_conversion_change': 0, 'avg_sales_cycle': 0, 'cycle_trend': 0
            }
    
    def _get_leads_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """Lädt Leads nach Pipeline-Stufe"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Tabelle erstellen falls sie nicht existiert
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crm_leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    contact_person TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    lead_source TEXT,
                    estimated_value REAL DEFAULT 0,
                    probability INTEGER DEFAULT 50,
                    expected_close_date DATE,
                    stage TEXT DEFAULT 'lead',
                    stage_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                SELECT * FROM crm_leads 
                WHERE stage = ? 
                ORDER BY stage_changed_at DESC
            ''', (stage,))
            
            leads = []
            for row in cursor.fetchall():
                lead = {
                    'id': row[0],
                    'company_name': row[1],
                    'contact_person': row[2],
                    'email': row[3],
                    'phone': row[4],
                    'address': row[5],
                    'lead_source': row[6],
                    'estimated_value': row[7],
                    'probability': row[8],
                    'expected_close_date': row[9],
                    'stage': row[10],
                    'stage_changed_at': row[11],
                    'notes': row[12],
                    'created_at': row[13],
                    'updated_at': row[14]
                }
                leads.append(lead)
            
            conn.close()
            return leads
            
        except Exception as e:
            print(f"Fehler beim Laden der Leads für Stufe {stage}: {e}")
            return []
    
    def _get_recent_closed_leads(self, status: str) -> List[Dict[str, Any]]:
        """Lädt kürzlich geschlossene Leads (won/lost)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            cursor.execute('''
                SELECT * FROM crm_leads 
                WHERE stage = ? AND stage_changed_at >= ?
                ORDER BY stage_changed_at DESC
            ''', (status, thirty_days_ago.isoformat()))
            
            leads = []
            for row in cursor.fetchall():
                lead = {
                    'id': row[0],
                    'company_name': row[1],
                    'contact_person': row[2],
                    'estimated_value': row[7],
                    'stage_changed_at': row[11]
                }
                leads.append(lead)
            
            conn.close()
            return leads
            
        except Exception as e:
            print(f"Fehler beim Laden der geschlossenen Leads: {e}")
            return []
    
    def _get_filtered_leads(self, stage_filter: str, source_filter: str, sort_by: str) -> List[Dict[str, Any]]:
        """Lädt gefilterte Leads"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM crm_leads WHERE 1=1'
            params = []
            
            if stage_filter != 'all':
                query += ' AND stage = ?'
                params.append(stage_filter)
            
            if source_filter != 'all':
                query += ' AND lead_source = ?'
                params.append(source_filter)
            
            # Sortierung
            if sort_by == 'estimated_value':
                query += ' ORDER BY estimated_value DESC'
            elif sort_by == 'probability':
                query += ' ORDER BY probability DESC'
            elif sort_by == 'expected_close_date':
                query += ' ORDER BY expected_close_date ASC'
            else:
                query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            
            leads = []
            for row in cursor.fetchall():
                lead = {
                    'id': row[0],
                    'company_name': row[1],
                    'contact_person': row[2],
                    'email': row[3],
                    'phone': row[4],
                    'address': row[5],
                    'lead_source': row[6],
                    'estimated_value': row[7],
                    'probability': row[8],
                    'expected_close_date': row[9],
                    'stage': row[10],
                    'stage_changed_at': row[11],
                    'notes': row[12],
                    'created_at': row[13],
                    'updated_at': row[14]
                }
                leads.append(lead)
            
            conn.close()
            return leads
            
        except Exception as e:
            print(f"Fehler beim Laden der gefilterten Leads: {e}")
            return []
    
    def _create_lead(self, lead_data: Dict[str, Any]) -> bool:
        """Erstellt einen neuen Lead"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO crm_leads 
                (company_name, contact_person, email, phone, address, lead_source, 
                 estimated_value, probability, expected_close_date, stage, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead_data['company_name'],
                lead_data['contact_person'],
                lead_data['email'],
                lead_data['phone'],
                lead_data['address'],
                lead_data['lead_source'],
                lead_data['estimated_value'],
                lead_data['probability'],
                lead_data['expected_close_date'].isoformat(),
                lead_data['stage'],
                lead_data['notes']
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Leads: {e}")
            return False
    
    def _update_lead_stage(self, lead_id: int, new_stage: str) -> bool:
        """Aktualisiert die Pipeline-Stufe eines Leads"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE crm_leads 
                SET stage = ?, stage_changed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_stage, lead_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Lead-Stufe: {e}")
            return False
    
    def _delete_lead(self, lead_id: int) -> bool:
        """Löscht einen Lead"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM crm_leads WHERE id = ?', (lead_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Fehler beim Löschen des Leads: {e}")
            return False
    
    def _get_next_stage(self, current_stage: str) -> Optional[str]:
        """Ermittelt die nächste Pipeline-Stufe"""
        stage_order = ['lead', 'qualified', 'proposal', 'negotiation', 'won']
        
        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _get_analytics_data(self, period: str) -> Dict[str, Any]:
        """Lädt Analytics-Daten für den gewählten Zeitraum"""
        # Mock data für Demo-Zwecke
        return {
            'new_leads': 45,
            'leads_growth': 12.5,
            'won_deals': 8,
            'won_value': 185000,
            'conversion_rate': 18.2,
            'conversion_change': 3.1,
            'avg_deal_size': 23125,
            'deal_size_change': 8.7,
            'funnel_data': {
                'lead': 45,
                'qualified': 28,
                'proposal': 15,
                'negotiation': 12,
                'won': 8
            },
            'trend_data': {
                'Januar': {'new_leads': 12, 'won_deals': 2},
                'Februar': {'new_leads': 18, 'won_deals': 4},
                'März': {'new_leads': 15, 'won_deals': 2}
            },
            'source_performance': {
                'Website': {'count': 18, 'conversion_rate': 22.2},
                'Empfehlung': {'count': 12, 'conversion_rate': 33.3},
                'Social Media': {'count': 8, 'conversion_rate': 12.5},
                'Kaltakquise': {'count': 7, 'conversion_rate': 14.3}
            }
        }

def render_crm_pipeline(texts: Dict[str, str], module_name: Optional[str] = None):
    """Haupt-Render-Funktion für CRM-Pipeline"""
    if module_name:
        st.title(module_name)
    pipeline_manager = CRMPipeline()
    pipeline_manager.render_pipeline_interface(texts)

# Änderungshistorie
# 2025-06-21, Gemini Ultra: CRM Pipeline UI implementiert
#                           - Kanban-Style Pipeline-Übersicht
#                           - Lead-Management mit vollständigem Lifecycle
#                           - Analytics und Reporting
#                           - Pipeline-Statistiken und KPIs
