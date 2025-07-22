# pdf_database_integration.py
# -*- coding: utf-8 -*-
"""
Vollständige Datenbankintegration für PDF-Generierung
Erweitert das moderne PDF-Design-System um echte Datenbankverbindungen
für Produktbilder, Firmendokumente, Vorlagen und Datenblätter
"""

import os
import base64
import sqlite3
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime
import traceback

class PDFDatabaseConnector:
    """
    Zentrale Datenbankverbindung für PDF-Generierung
    """
    
    def __init__(self, db_connection_func: Optional[Callable] = None):
        self.get_db_connection = db_connection_func
        if not self.get_db_connection:
            try:
                from database import get_db_connection
                self.get_db_connection = get_db_connection
            except ImportError:
                print("⚠️ Datenbankfunktionen nicht verfügbar")
                self.get_db_connection = None
    
    def get_connection(self) -> Optional[sqlite3.Connection]:
        """Sichere Datenbankverbindung"""
        if self.get_db_connection:
            return self.get_db_connection()
        return None

class EnhancedProductDataLoader:
    """
    Erweiterte Produktdatenladung mit Bildern und Datenblättern
    """
    
    def __init__(self, db_connector: PDFDatabaseConnector):
        self.db = db_connector
    
    def load_complete_product_data(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Lädt vollständige Produktdaten inklusive Bild und Datenblatt"""
        conn = self.db.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, model_name, manufacturer, price_euro, 
                       description, technical_data, image_base64, 
                       datasheet_link_db_path, capacity_w, power_kw, 
                       warranty_years, efficiency_percent, pros, cons,
                       length_m, width_m, weight_kg, origin_country, rating
                FROM products 
                WHERE id = ?
            """, (product_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            product_data = dict(row)
            
            # Datenblatt-Pfad laden
            if product_data.get('datasheet_link_db_path'):
                datasheet_path = self._get_datasheet_full_path(product_data['datasheet_link_db_path'])
                product_data['datasheet_full_path'] = datasheet_path
                product_data['has_datasheet'] = os.path.exists(datasheet_path) if datasheet_path else False
            else:
                product_data['has_datasheet'] = False
            
            # Zusätzliche Bildverarbeitung
            if product_data.get('image_base64'):
                product_data['has_image'] = True
                # Prüfe Bildgröße für PDF-Optimierung
                try:
                    img_data = base64.b64decode(product_data['image_base64'])
                    product_data['image_size_bytes'] = len(img_data)
                except:
                    product_data['has_image'] = False
            else:
                product_data['has_image'] = False
            
            return product_data
            
        except Exception as e:
            print(f"⚠️ Fehler beim Laden Produktdaten ID {product_id}: {e}")
            return None
        finally:
            conn.close()
    
    def _get_datasheet_full_path(self, db_path: str) -> Optional[str]:
        """Erstellt vollständigen Pfad zum Produktdatenblatt"""
        try:
            # Basis-Verzeichnis für Produktdatenblätter
            base_dir = os.path.join(os.getcwd(), "data", "product_datasheets")
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
            
            full_path = os.path.join(base_dir, db_path)
            return full_path if os.path.exists(full_path) else None
        except Exception as e:
            print(f"⚠️ Fehler bei Datenblatt-Pfad: {e}")
            return None
    
    def load_products_by_category(self, category: str, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lädt alle Produkte einer Kategorie mit vollständigen Daten"""
        conn = self.db.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT id, category, model_name, manufacturer, price_euro, 
                       description, image_base64, capacity_w, power_kw
                FROM products 
                WHERE category = ?
            """
            params = [category]
            
            if company_id:
                query += " AND (company_id = ? OR company_id IS NULL)"
                params.append(company_id)
            
            query += " ORDER BY model_name COLLATE NOCASE"
            
            cursor.execute(query, params)
            products = []
            
            for row in cursor.fetchall():
                product = dict(row)
                product['has_image'] = bool(product.get('image_base64'))
                products.append(product)
            
            return products
            
        except Exception as e:
            print(f"⚠️ Fehler beim Laden Produktkategorie {category}: {e}")
            return []
        finally:
            conn.close()

class CompanyDocumentLoader:
    """
    Lädt Firmendokumente und -vorlagen für PDF-Integration
    """
    
    def __init__(self, db_connector: PDFDatabaseConnector):
        self.db = db_connector
    
    def load_company_documents(self, company_id: int, document_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Lädt alle verfügbaren Firmendokumente"""
        conn = self.db.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            if document_types:
                placeholders = ','.join(['?' for _ in document_types])
                query = f"""
                    SELECT id, company_id, document_type, display_name, 
                           file_name, absolute_file_path, uploaded_at
                    FROM company_documents 
                    WHERE company_id = ? AND document_type IN ({placeholders})
                    ORDER BY document_type, display_name COLLATE NOCASE
                """
                params = [company_id] + document_types
            else:
                query = """
                    SELECT id, company_id, document_type, display_name, 
                           file_name, absolute_file_path, uploaded_at
                    FROM company_documents 
                    WHERE company_id = ?
                    ORDER BY document_type, display_name COLLATE NOCASE
                """
                params = [company_id]
            
            cursor.execute(query, params)
            documents = []
            
            for row in cursor.fetchall():
                doc = dict(row)
                # Prüfe Dateiverfügbarkeit
                file_path = doc.get('absolute_file_path')
                doc['file_exists'] = os.path.exists(file_path) if file_path else False
                doc['file_size_mb'] = self._get_file_size_mb(file_path) if doc['file_exists'] else 0
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"⚠️ Fehler beim Laden Firmendokumente für Company {company_id}: {e}")
            return []
        finally:
            conn.close()
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Berechnet Dateigröße in MB"""
        try:
            size_bytes = os.path.getsize(file_path)
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0.0
    
    def load_company_info(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Lädt vollständige Firmeninformationen"""
        conn = self.db.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, logo_base64, street, zip_code, city, 
                       phone, email, website, tax_id, commercial_register, 
                       bank_details, pdf_footer_text
                FROM companies 
                WHERE id = ?
            """, (company_id,))
            
            row = cursor.fetchone()
            if row:
                company_data = dict(row)
                company_data['has_logo'] = bool(company_data.get('logo_base64'))
                return company_data
            
            return None
            
        except Exception as e:
            print(f"⚠️ Fehler beim Laden Firmeninfo ID {company_id}: {e}")
            return None
        finally:
            conn.close()

class ImageTemplateManager:
    """
    Verwaltet firmenspezifische Bildvorlagen für PDFs
    """
    
    def __init__(self, db_connector: PDFDatabaseConnector):
        self.db = db_connector
    
    def load_company_image_templates(self, company_id: int, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lädt firmenspezifische Bildvorlagen"""
        conn = self.db.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            if template_type:
                query = """
                    SELECT id, company_id, name, template_type, file_path, 
                           created_at, updated_at
                    FROM company_image_templates 
                    WHERE company_id = ? AND template_type = ?
                    ORDER BY name COLLATE NOCASE
                """
                params = (company_id, template_type)
            else:
                query = """
                    SELECT id, company_id, name, template_type, file_path, 
                           created_at, updated_at
                    FROM company_image_templates 
                    WHERE company_id = ?
                    ORDER BY template_type, name COLLATE NOCASE
                """
                params = (company_id,)
            
            cursor.execute(query, params)
            templates = []
            
            for row in cursor.fetchall():
                template = dict(row)
                # Vollständigen Pfad erstellen
                template['absolute_file_path'] = self._get_template_full_path(template['file_path'])
                template['file_exists'] = os.path.exists(template['absolute_file_path'])
                
                if template['file_exists']:
                    template['image_data'] = self._load_image_data(template['absolute_file_path'])
                else:
                    template['image_data'] = None
                
                templates.append(template)
            
            return templates
            
        except Exception as e:
            print(f"⚠️ Fehler beim Laden Bildvorlagen für Company {company_id}: {e}")
            return []
        finally:
            conn.close()
    
    def _get_template_full_path(self, file_path: str) -> str:
        """Erstellt vollständigen Pfad zur Bildvorlage"""
        base_dir = os.path.join(os.getcwd(), "data", "company_docs")
        return os.path.join(base_dir, file_path)
    
    def _load_image_data(self, file_path: str) -> Optional[bytes]:
        """Lädt Bilddaten als Bytes"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ Fehler beim Laden Bilddaten {file_path}: {e}")
            return None

class PDFTemplateManager:
    """
    Verwaltet PDF-Textvorlagen und -Layouts
    """
    
    def __init__(self, db_connector: PDFDatabaseConnector):
        self.db = db_connector
    
    def load_pdf_templates(self, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lädt verfügbare PDF-Vorlagen"""
        conn = self.db.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            if template_type:
                query = """
                    SELECT id, template_type, name, content, created_at, updated_at
                    FROM pdf_templates 
                    WHERE template_type = ?
                    ORDER BY name COLLATE NOCASE
                """
                params = (template_type,)
            else:
                query = """
                    SELECT id, template_type, name, content, created_at, updated_at
                    FROM pdf_templates 
                    ORDER BY template_type, name COLLATE NOCASE
                """
                params = ()
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"⚠️ Fehler beim Laden PDF-Vorlagen: {e}")
            return []
        finally:
            conn.close()
    
    def load_company_text_templates(self, company_id: int, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lädt firmenspezifische Textvorlagen"""
        conn = self.db.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            if template_type:
                query = """
                    SELECT id, company_id, name, content, template_type, 
                           created_at, updated_at
                    FROM company_text_templates 
                    WHERE company_id = ? AND template_type = ?
                    ORDER BY name COLLATE NOCASE
                """
                params = (company_id, template_type)
            else:
                query = """
                    SELECT id, company_id, name, content, template_type, 
                           created_at, updated_at
                    FROM company_text_templates 
                    WHERE company_id = ?
                    ORDER BY template_type, name COLLATE NOCASE
                """
                params = (company_id,)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"⚠️ Fehler beim Laden Textvorlagen für Company {company_id}: {e}")
            return []
        finally:
            conn.close()

class ComprehensivePDFDataManager:
    """
    Zentrale Klasse die alle Datenbankverbindungen für PDF-Generierung verwaltet
    """
    
    def __init__(self, db_connection_func: Optional[Callable] = None):
        self.db_connector = PDFDatabaseConnector(db_connection_func)
        self.product_loader = EnhancedProductDataLoader(self.db_connector)
        self.document_loader = CompanyDocumentLoader(self.db_connector)
        self.image_manager = ImageTemplateManager(self.db_connector)
        self.template_manager = PDFTemplateManager(self.db_connector)
    
    def create_complete_pdf_dataset(self, project_data: Dict[str, Any], 
                                  company_id: int, 
                                  include_product_images: bool = True,
                                  include_company_docs: bool = True,
                                  include_datasheets: bool = True) -> Dict[str, Any]:
        """
        Erstellt vollständigen Datensatz für PDF-Generierung
        Lädt alle benötigten Daten aus der Datenbank
        """
        print(f"🔄 Lade vollständige PDF-Daten für Company {company_id}...")
        
        # Firmeninformationen
        company_info = self.document_loader.load_company_info(company_id)
        
        # Produktdaten mit Bildern
        products_with_data = []
        komponenten = project_data.get('komponenten', {})
        
        for component_type, component_data in komponenten.items():
            if isinstance(component_data, dict) and 'produkt_id' in component_data:
                product_id = component_data['produkt_id']
                product_data = self.product_loader.load_complete_product_data(product_id)
                
                if product_data:
                    enhanced_product = {
                        'component_type': component_type,
                        'quantity': component_data.get('anzahl', 1),
                        'product_data': product_data,
                        'has_image': product_data.get('has_image', False),
                        'has_datasheet': product_data.get('has_datasheet', False)
                    }
                    products_with_data.append(enhanced_product)
        
        # Firmendokumente
        company_documents = []
        if include_company_docs:
            doc_types = ['certificate', 'warranty', 'technical_docs', 'brochure']
            company_documents = self.document_loader.load_company_documents(company_id, doc_types)
        
        # Bildvorlagen
        image_templates = []
        if include_product_images:
            image_templates = self.image_manager.load_company_image_templates(company_id)
        
        # Textvorlagen
        text_templates = self.template_manager.load_company_text_templates(company_id)
        
        # Installation Examples (falls verfügbar)
        installation_images = self.image_manager.load_company_image_templates(
            company_id, 'installation_example'
        )
        
        dataset = {
            'company_info': company_info,
            'products_enhanced': products_with_data,
            'company_documents': company_documents,
            'image_templates': image_templates,
            'text_templates': text_templates,
            'installation_examples': installation_images,
            'data_statistics': {
                'total_products': len(products_with_data),
                'products_with_images': len([p for p in products_with_data if p['has_image']]),
                'products_with_datasheets': len([p for p in products_with_data if p['has_datasheet']]),
                'total_documents': len(company_documents),
                'available_documents': len([d for d in company_documents if d['file_exists']]),
                'image_templates_count': len(image_templates),
                'text_templates_count': len(text_templates),
                'installation_examples_count': len(installation_images)
            },
            'content_completeness': self._calculate_content_completeness(
                products_with_data, company_documents, image_templates, company_info
            )
        }
        
        print(f"✅ PDF-Daten geladen: {dataset['data_statistics']}")
        return dataset
    
    def _calculate_content_completeness(self, products: List[Dict], documents: List[Dict], 
                                      images: List[Dict], company_info: Optional[Dict]) -> float:
        """Berechnet Vollständigkeit der verfügbaren Inhalte (0-100%)"""
        score = 0
        max_score = 100
        
        # Firmeninfo (20%)
        if company_info:
            score += 10
            if company_info.get('has_logo'):
                score += 10
        
        # Produktbilder (30%)
        if products:
            products_with_images = len([p for p in products if p['has_image']])
            image_score = (products_with_images / len(products)) * 30
            score += image_score
        
        # Firmendokumente (25%)
        if documents:
            available_docs = len([d for d in documents if d['file_exists']])
            doc_score = min((available_docs / 3) * 25, 25)  # Max bei 3+ Dokumenten
            score += doc_score
        
        # Bildvorlagen (25%)
        if images:
            template_score = min((len(images) / 5) * 25, 25)  # Max bei 5+ Vorlagen
            score += template_score
        
        return round(score, 1)
    
    def get_product_image_as_base64(self, product_id: int) -> Optional[str]:
        """Lädt Produktbild als Base64-String"""
        product_data = self.product_loader.load_complete_product_data(product_id)
        if product_data and product_data.get('image_base64'):
            return product_data['image_base64']
        return None
    
    def get_company_logo_as_base64(self, company_id: int) -> Optional[str]:
        """Lädt Firmenlogo als Base64-String"""
        company_info = self.document_loader.load_company_info(company_id)
        if company_info and company_info.get('logo_base64'):
            return company_info['logo_base64']
        return None
    
    def create_product_showcase_data(self, product_ids: List[int]) -> List[Dict[str, Any]]:
        """Erstellt Showcase-Daten für ausgewählte Produkte"""
        showcase_products = []
        
        for product_id in product_ids:
            product_data = self.product_loader.load_complete_product_data(product_id)
            if product_data:
                showcase_item = {
                    'id': product_id,
                    'name': f"{product_data.get('manufacturer', '')} {product_data.get('model_name', '')}".strip(),
                    'category': product_data.get('category', ''),
                    'description': product_data.get('description', ''),
                    'technical_specs': {
                        'Leistung': f"{product_data.get('capacity_w', 0)} W" if product_data.get('capacity_w') else None,
                        'Wechselrichter': f"{product_data.get('power_kw', 0)} kW" if product_data.get('power_kw') else None,
                        'Garantie': f"{product_data.get('warranty_years', 0)} Jahre" if product_data.get('warranty_years') else None,
                        'Effizienz': f"{product_data.get('efficiency_percent', 0)}%" if product_data.get('efficiency_percent') else None,
                        'Abmessungen': f"{product_data.get('length_m', 0)}m x {product_data.get('width_m', 0)}m" if product_data.get('length_m') and product_data.get('width_m') else None,
                        'Gewicht': f"{product_data.get('weight_kg', 0)} kg" if product_data.get('weight_kg') else None
                    },
                    'image_base64': product_data.get('image_base64'),
                    'has_image': product_data.get('has_image', False),
                    'has_datasheet': product_data.get('has_datasheet', False),
                    'datasheet_path': product_data.get('datasheet_full_path'),
                    'price': product_data.get('price_euro', 0),
                    'pros': product_data.get('pros', '').split('\n') if product_data.get('pros') else [],
                    'cons': product_data.get('cons', '').split('\n') if product_data.get('cons') else [],
                    'rating': product_data.get('rating', 0)
                }
                
                # Bereinige technische Spezifikationen (entferne None-Werte)
                showcase_item['technical_specs'] = {
                    k: v for k, v in showcase_item['technical_specs'].items() if v is not None
                }
                
                showcase_products.append(showcase_item)
        
        return showcase_products

# Factory-Funktionen für einfache Integration
def create_pdf_data_manager(db_connection_func: Optional[Callable] = None) -> ComprehensivePDFDataManager:
    """Factory-Funktion für PDF-Datenmanager"""
    return ComprehensivePDFDataManager(db_connection_func)

def load_complete_pdf_data(project_data: Dict[str, Any], 
                          company_id: int,
                          db_connection_func: Optional[Callable] = None) -> Dict[str, Any]:
    """Vereinfachte Funktion zum Laden aller PDF-Daten"""
    manager = create_pdf_data_manager(db_connection_func)
    return manager.create_complete_pdf_dataset(project_data, company_id)

def get_enhanced_product_list(product_ids: List[int], 
                             db_connection_func: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """Lädt erweiterte Produktliste mit allen Daten"""
    manager = create_pdf_data_manager(db_connection_func)
    return manager.create_product_showcase_data(product_ids)
