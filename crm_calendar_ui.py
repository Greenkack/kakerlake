"""
CRM Calendar UI Module
Autor: Gemini Ultra
Datum: 2025-06-21
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
import calendar
import json

try:
    from database import execute_query, get_db_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

class CRMCalendar:
    """CRM Kalender für Termine und Erinnerungen"""
    
    def __init__(self):
        self.appointment_types = {
            'consultation': {'name': 'Beratungstermin', 'color': '#3B82F6', 'icon': '💬'},
            'site_visit': {'name': 'Vor-Ort-Termin', 'color': '#10B981', 'icon': '🏠'},
            'installation': {'name': 'Installation', 'color': '#F59E0B', 'icon': '🔧'},
            'follow_up': {'name': 'Nachfassung', 'color': '#8B5CF6', 'icon': '📞'},
            'reminder': {'name': 'Erinnerung', 'color': '#EF4444', 'icon': '⏰'},
            'maintenance': {'name': 'Wartung', 'color': '#6B7280', 'icon': '🛠️'}
        }
    
    def render_calendar_interface(self, texts: Dict[str, str]):
        """Rendert die Kalender-Hauptoberfläche"""
        st.header("📅 CRM Kalender & Termine")
        
        if not DATABASE_AVAILABLE:
            st.error("Datenbankverbindung nicht verfügbar")
            return
        
        # Tabs für verschiedene Ansichten
        tab1, tab2, tab3 = st.tabs(["📅 Kalenderansicht", "➕ Neuer Termin", "📋 Terminliste"])
        
        with tab1:
            self._render_calendar_view()
        
        with tab2:
            self._render_new_appointment_form()
        
        with tab3:
            self._render_appointment_list()
    
    def _render_calendar_view(self):
        """Rendert die Kalenderansicht"""
        st.subheader("📅 Monatsansicht")
        
        # Datum-Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("◀ Vorheriger Monat"):
                if 'calendar_date' not in st.session_state:
                    st.session_state.calendar_date = datetime.now().replace(day=1)
                
                # Vorheriger Monat
                if st.session_state.calendar_date.month == 1:
                    st.session_state.calendar_date = st.session_state.calendar_date.replace(
                        year=st.session_state.calendar_date.year - 1, month=12
                    )
                else:
                    st.session_state.calendar_date = st.session_state.calendar_date.replace(
                        month=st.session_state.calendar_date.month - 1
                    )
                st.rerun()
        
        with col2:
            if 'calendar_date' not in st.session_state:
                st.session_state.calendar_date = datetime.now().replace(day=1)
            
            current_date = st.session_state.calendar_date
            st.markdown(f"### {calendar.month_name[current_date.month]} {current_date.year}")
        
        with col3:
            if st.button("Nächster Monat ▶"):
                if 'calendar_date' not in st.session_state:
                    st.session_state.calendar_date = datetime.now().replace(day=1)
                
                # Nächster Monat
                if st.session_state.calendar_date.month == 12:
                    st.session_state.calendar_date = st.session_state.calendar_date.replace(
                        year=st.session_state.calendar_date.year + 1, month=1
                    )
                else:
                    st.session_state.calendar_date = st.session_state.calendar_date.replace(
                        month=st.session_state.calendar_date.month + 1
                    )
                st.rerun()
        
        # Kalender-Grid
        self._render_calendar_grid(st.session_state.calendar_date)
        
        # Heute-Button
        if st.button("📍 Heute"):
            st.session_state.calendar_date = datetime.now().replace(day=1)
            st.rerun()
    
    def _render_calendar_grid(self, current_date: datetime):
        """Rendert das Kalender-Grid"""
        # Termine für den Monat laden
        appointments = self._get_appointments_for_month(current_date.year, current_date.month)
        
        # Kalender-Header
        weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        cols = st.columns(7)
        for i, day in enumerate(weekdays):
            cols[i].markdown(f"**{day}**")
        
        # Kalender-Tage
        cal = calendar.monthcalendar(current_date.year, current_date.month)
        
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.markdown("&nbsp;")
                    else:
                        # Tag anzeigen
                        day_date = datetime(current_date.year, current_date.month, day)
                        day_appointments = [
                            apt for apt in appointments 
                            if apt['appointment_date'].date() == day_date.date()
                        ]
                        
                        # Tag-Container
                        if day_appointments:
                            apt_count = len(day_appointments)
                            st.markdown(f"""
                                <div style="border: 1px solid #ddd; padding: 5px; min-height: 60px; background-color: #f0f8ff;">
                                    <strong>{day}</strong><br>
                                    <small style="color: #666;">{apt_count} Termin{'e' if apt_count > 1 else ''}</small>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Termine anzeigen
                            for apt in day_appointments[:2]:  # Max 2 Termine anzeigen
                                apt_type = self.appointment_types.get(apt['type'], self.appointment_types['consultation'])
                                st.markdown(f"<small>{apt_type['icon']} {apt['title'][:15]}...</small>", unsafe_allow_html=True)
                            
                            if len(day_appointments) > 2:
                                st.markdown(f"<small>+{len(day_appointments) - 2} weitere</small>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div style="border: 1px solid #ddd; padding: 5px; min-height: 60px;">
                                    <strong>{day}</strong>
                                </div>
                            """, unsafe_allow_html=True)
    
    def _render_new_appointment_form(self):
        """Rendert das Formular für neue Termine"""
        st.subheader("➕ Neuen Termin erstellen")
        
        with st.form("new_appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Titel *", placeholder="z.B. Beratungstermin Herr Müller")
                
                appointment_type = st.selectbox(
                    "Termintyp *",
                    options=list(self.appointment_types.keys()),
                    format_func=lambda x: f"{self.appointment_types[x]['icon']} {self.appointment_types[x]['name']}"
                )
                
                appointment_date = st.date_input(
                    "Datum *",
                    value=datetime.now().date(),
                    min_value=datetime.now().date()
                )
                
                appointment_time = st.time_input(
                    "Uhrzeit *",
                    value=datetime.now().time().replace(minute=0, second=0, microsecond=0)
                )
            
            with col2:
                duration = st.number_input(
                    "Dauer (Minuten)",
                    min_value=15,
                    max_value=480,
                    value=60,
                    step=15
                )
                
                # Kunden-Auswahl (falls CRM-Daten verfügbar)
                try:
                    from database import get_all_active_customers
                    customers = get_all_active_customers()
                    
                    if customers:
                        customer_options = {0: "Kein Kunde zugeordnet"}
                        for customer in customers:
                            customer_options[customer['id']] = f"{customer['first_name']} {customer['last_name']}"
                        
                        customer_id = st.selectbox(
                            "Kunde",
                            options=list(customer_options.keys()),
                            format_func=lambda x: customer_options[x]
                        )
                    else:
                        customer_id = None
                        st.info("Keine Kunden verfügbar")
                except ImportError:
                    customer_id = None
                    st.info("CRM-Modul nicht verfügbar")
                
                location = st.text_input("Ort", placeholder="z.B. Büro, Kundenadresse")
                
                reminder_minutes = st.selectbox(
                    "Erinnerung",
                    options=[0, 15, 30, 60, 120, 1440],
                    format_func=lambda x: {
                        0: "Keine Erinnerung",
                        15: "15 Minuten vorher",
                        30: "30 Minuten vorher", 
                        60: "1 Stunde vorher",
                        120: "2 Stunden vorher",
                        1440: "1 Tag vorher"
                    }[x],
                    index=3  # Default: 1 Stunde
                )
            
            notes = st.text_area("Notizen", placeholder="Zusätzliche Informationen zum Termin")
            
            submitted = st.form_submit_button("📅 Termin erstellen", type="primary")
            
            if submitted:
                if title and appointment_date and appointment_time:
                    appointment_datetime = datetime.combine(appointment_date, appointment_time)
                    
                    appointment_data = {
                        'title': title,
                        'type': appointment_type,
                        'appointment_date': appointment_datetime,
                        'duration_minutes': duration,
                        'customer_id': customer_id if customer_id != 0 else None,
                        'location': location,
                        'notes': notes,
                        'reminder_minutes': reminder_minutes,
                        'status': 'scheduled'
                    }
                    
                    if self._create_appointment(appointment_data):
                        st.success("✅ Termin wurde erfolgreich erstellt!")
                        st.rerun()
                    else:
                        st.error("❌ Fehler beim Erstellen des Termins")
                else:
                    st.error("Bitte füllen Sie alle Pflichtfelder aus")
    
    def _render_appointment_list(self):
        """Rendert die Terminliste"""
        st.subheader("📋 Alle Termine")
        
        # Filter-Optionen
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "Termintyp filtern",
                options=['all'] + list(self.appointment_types.keys()),
                format_func=lambda x: "Alle Typen" if x == 'all' else f"{self.appointment_types[x]['icon']} {self.appointment_types[x]['name']}"
            )
        
        with col2:
            filter_period = st.selectbox(
                "Zeitraum",
                options=['upcoming', 'today', 'this_week', 'this_month', 'all'],
                format_func=lambda x: {
                    'upcoming': 'Anstehende Termine',
                    'today': 'Heute',
                    'this_week': 'Diese Woche',
                    'this_month': 'Dieser Monat',
                    'all': 'Alle Termine'
                }[x]
            )
        
        with col3:
            filter_status = st.selectbox(
                "Status",
                options=['all', 'scheduled', 'completed', 'cancelled'],
                format_func=lambda x: {
                    'all': 'Alle Status',
                    'scheduled': 'Geplant',
                    'completed': 'Abgeschlossen',
                    'cancelled': 'Abgesagt'
                }[x]
            )
        
        # Termine laden und anzeigen
        appointments = self._get_filtered_appointments(filter_type, filter_period, filter_status)
        
        if appointments:
            for appointment in appointments:
                self._render_appointment_card(appointment)
        else:
            st.info("Keine Termine gefunden")
    
    def _render_appointment_card(self, appointment: Dict[str, Any]):
        """Rendert eine Terminkarte"""
        apt_type = self.appointment_types.get(appointment['type'], self.appointment_types['consultation'])
        
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{apt_type['icon']} {appointment['title']}**")
                if appointment.get('customer_name'):
                    st.caption(f"👤 {appointment['customer_name']}")
                if appointment.get('location'):
                    st.caption(f"📍 {appointment['location']}")
            
            with col2:
                st.markdown(f"📅 {appointment['appointment_date'].strftime('%d.%m.%Y')}")
                st.markdown(f"🕐 {appointment['appointment_date'].strftime('%H:%M')} Uhr")
            
            with col3:
                status_colors = {
                    'scheduled': '🟡',
                    'completed': '🟢',
                    'cancelled': '🔴'
                }
                status_color = status_colors.get(appointment['status'], '⚪')
                st.markdown(f"{status_color} {appointment['status'].title()}")
                st.caption(f"⏱️ {appointment['duration_minutes']} Min.")
            
            with col4:
                if st.button("✏️", key=f"edit_{appointment['id']}", help="Bearbeiten"):
                    st.session_state.edit_appointment_id = appointment['id']
                    st.rerun()
                
                if st.button("🗑️", key=f"delete_{appointment['id']}", help="Löschen"):
                    if self._delete_appointment(appointment['id']):
                        st.success("Termin gelöscht")
                        st.rerun()
            
            if appointment.get('notes'):
                st.caption(f"📝 {appointment['notes']}")
            
            st.markdown("---")
    
    def _get_appointments_for_month(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Lädt Termine für einen bestimmten Monat"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Tabelle erstellen falls sie nicht existiert
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crm_appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    type TEXT NOT NULL,
                    appointment_date TIMESTAMP NOT NULL,
                    duration_minutes INTEGER DEFAULT 60,
                    customer_id INTEGER,
                    location TEXT,
                    notes TEXT,
                    reminder_minutes INTEGER DEFAULT 60,
                    status TEXT DEFAULT 'scheduled',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES crm_customers (id)
                )
            ''')
            
            # Termine für den Monat abfragen
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            cursor.execute('''
                SELECT a.*, c.first_name, c.last_name
                FROM crm_appointments a
                LEFT JOIN crm_customers c ON a.customer_id = c.id
                WHERE a.appointment_date >= ? AND a.appointment_date < ?
                ORDER BY a.appointment_date
            ''', (start_date, end_date))
            
            appointments = []
            for row in cursor.fetchall():
                appointment = {
                    'id': row[0],
                    'title': row[1],
                    'type': row[2],
                    'appointment_date': datetime.fromisoformat(row[3]),
                    'duration_minutes': row[4],
                    'customer_id': row[5],
                    'location': row[6],
                    'notes': row[7],
                    'reminder_minutes': row[8],
                    'status': row[9],
                    'created_at': row[10],
                    'updated_at': row[11],
                    'customer_name': f"{row[12] or ''} {row[13] or ''}".strip() if row[12] or row[13] else None
                }
                appointments.append(appointment)
            
            conn.close()
            return appointments
            
        except Exception as e:
            print(f"Fehler beim Laden der Monats-Termine: {e}")
            return []
    
    def _get_filtered_appointments(self, filter_type: str, filter_period: str, filter_status: str) -> List[Dict[str, Any]]:
        """Lädt gefilterte Termine"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Basis-Query
            query = '''
                SELECT a.*, c.first_name, c.last_name
                FROM crm_appointments a
                LEFT JOIN crm_customers c ON a.customer_id = c.id
                WHERE 1=1
            '''
            params = []
            
            # Typ-Filter
            if filter_type != 'all':
                query += ' AND a.type = ?'
                params.append(filter_type)
            
            # Status-Filter
            if filter_status != 'all':
                query += ' AND a.status = ?'
                params.append(filter_status)
            
            # Zeitraum-Filter
            now = datetime.now()
            if filter_period == 'today':
                start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)
                query += ' AND a.appointment_date >= ? AND a.appointment_date < ?'
                params.extend([start_of_day, end_of_day])
            elif filter_period == 'upcoming':
                query += ' AND a.appointment_date >= ?'
                params.append(now)
            elif filter_period == 'this_week':
                start_of_week = now - timedelta(days=now.weekday())
                start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_week = start_of_week + timedelta(days=7)
                query += ' AND a.appointment_date >= ? AND a.appointment_date < ?'
                params.extend([start_of_week, end_of_week])
            elif filter_period == 'this_month':
                start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    end_of_month = start_of_month.replace(year=now.year + 1, month=1)
                else:
                    end_of_month = start_of_month.replace(month=now.month + 1)
                query += ' AND a.appointment_date >= ? AND a.appointment_date < ?'
                params.extend([start_of_month, end_of_month])
            
            query += ' ORDER BY a.appointment_date'
            
            cursor.execute(query, params)
            
            appointments = []
            for row in cursor.fetchall():
                appointment = {
                    'id': row[0],
                    'title': row[1],
                    'type': row[2],
                    'appointment_date': datetime.fromisoformat(row[3]),
                    'duration_minutes': row[4],
                    'customer_id': row[5],
                    'location': row[6],
                    'notes': row[7],
                    'reminder_minutes': row[8],
                    'status': row[9],
                    'created_at': row[10],
                    'updated_at': row[11],
                    'customer_name': f"{row[12] or ''} {row[13] or ''}".strip() if row[12] or row[13] else None
                }
                appointments.append(appointment)
            
            conn.close()
            return appointments
            
        except Exception as e:
            print(f"Fehler beim Laden der gefilterten Termine: {e}")
            return []
    
    def _create_appointment(self, appointment_data: Dict[str, Any]) -> bool:
        """Erstellt einen neuen Termin"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO crm_appointments 
                (title, type, appointment_date, duration_minutes, customer_id, location, notes, reminder_minutes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                appointment_data['title'],
                appointment_data['type'],
                appointment_data['appointment_date'].isoformat(),
                appointment_data['duration_minutes'],
                appointment_data['customer_id'],
                appointment_data['location'],
                appointment_data['notes'],
                appointment_data['reminder_minutes'],
                appointment_data['status']
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Termins: {e}")
            return False
    
    def _delete_appointment(self, appointment_id: int) -> bool:
        """Löscht einen Termin"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM crm_appointments WHERE id = ?', (appointment_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Fehler beim Löschen des Termins: {e}")
            return False

def render_crm_calendar(texts: Dict[str, str], module_name: Optional[str] = None):
    """Haupt-Render-Funktion für CRM-Kalender"""
    if module_name:
        st.title(module_name)
    calendar_manager = CRMCalendar()
    calendar_manager.render_calendar_interface(texts)

def render_calendar_ui(): # Beispiel für Ihre Haupt-UI-Funktion
    st.title("🗓️ Kalender & Terminplanung")

    # ... (Ihr bestehender Code für die Kalenderanzeige) ...
    st.write("Ihre geplanten Aktivitäten:")
    
    st.markdown("---")
    
    # --- PLATZHALTER FÜR GOOGLE KALENDER IMPORT by Seggeli Ultra ---
    with st.expander("📅 Google Kalender Import (Live-Synchronisation)", expanded=True):
        st.info("Hier werden Termine aus Ihrem verbundenen Google Kalender angezeigt. Klicken Sie, um einen Termin als neuen Lead im CRM zu speichern.")
        
        # PLATZHALTER: Hier würde der API-Aufruf an Google stattfinden.
        # Wir simulieren die Antwort mit Beispieldaten.
        google_events = [
            {'summary': 'Erstberatung mit Familie Huber', 'description': 'Thema: PV-Anlage für Neubau.\nE-Mail: familie.huber@mail.de\nTel: 0176 98765432', 'start_time': datetime(2025, 8, 20, 11, 0).isoformat()},
            {'summary': 'Technik-Check bei Solar Solutions GmbH', 'description': 'Kontakt: Herr Kurz\nE-Mail: kurz@solarsolutions.de', 'start_time': datetime(2025, 8, 21, 15, 0).isoformat()}
        ]

        # UI für jedes gefundene Event erstellen
        for i, event in enumerate(google_events):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**{event['summary']}**")
                st.caption(f"Zeitpunkt: {datetime.fromisoformat(event['start_time']).strftime('%d.%m.%Y %H:%M')}")
            with cols[1]:
                if st.button("Als Lead importieren", key=f"import_lead_btn_{i}"):
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        new_id = import_lead_from_calendar_event(cursor, event)
                        conn.commit()
                        conn.close()
                        if new_id:
                            st.success(f"Lead (ID: {new_id}) erfolgreich importiert!")
                            st.rerun()
                        else:
                            st.error("Import fehlgeschlagen.")
                    except Exception as e:
                        st.error(f"DB-Fehler: {e}")

        # Beispiel-Event 2
        event2_data = {
            'summary': 'Follow-Up bei Firma SolarTech GmbH',
            'description': 'Thema: Angebotsdetails besprechen.\nKontakt: Herr Weber\nE-Mail: weber@solartech.de',
            'start_time': datetime(2025, 8, 16, 14, 30).isoformat()
        }
        cols2 = st.columns([3, 1])
        with cols2[0]:
            st.write(f"**Titel:** {event2_data['summary']}")
            st.caption(f"**Zeit:** {event2_data['start_time']}")
        with cols2[1]:
            if st.button("Als Lead importieren", key="import_lead_2"):
                conn = get_db_connection()
                cursor = conn.cursor()
                new_id = import_lead_from_calendar_event(cursor, event2_data)
                conn.commit()
                conn.close()
                if new_id:
                    st.success(f"Lead 'SolarTech GmbH' (ID: {new_id}) erfolgreich importiert!")
                    st.rerun()
                else:
                    st.error("Import fehlgeschlagen.")
# Änderungshistorie
# 2025-06-21, Gemini Ultra: CRM Calendar UI implementiert
#                           - Monatskalender mit Terminanzeige
#                           - Termin-Erstellung und -Verwaltung
#                           - Kunde-Termin-Verknüpfung
#                           - Filter- und Suchfunktionen
