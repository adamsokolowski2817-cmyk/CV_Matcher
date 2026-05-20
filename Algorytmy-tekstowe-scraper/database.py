import sqlite3
import numpy as np
import io

def adapt_array(arr):
    """Konwertuje tablicę numpy na wartość binarną do zapisu w SQLite."""
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    """Konwertuje wartość binarną z SQLite z powrotem na tablicę numpy."""
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

# Rejestracja adaptera i konwertera dla numpy array
sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("ARRAY", convert_array)

class OfferDatabase:
    def __init__(self, db_path='offers.db'):
        """
        Inicjalizuje połączenie z bazą danych i tworzy tabelę.
        Ustawienie detect_types=sqlite3.PARSE_DECLTYPES pozwala na 
        automatyczne korzystanie z naszego konwertera.
        """
        self.conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        # Dzięki row_factory wiersze będą zachowywać się jak słowniki
        self.conn.row_factory = sqlite3.Row  
        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS offers (
            id TEXT PRIMARY KEY,
            title TEXT,
            price TEXT,
            location TEXT,
            contract TEXT,
            work_load TEXT,
            description TEXT,
            url TEXT,
            source TEXT,
            vector ARRAY
        )
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()

    def insert_offer(self, offer_data, vector=None):
        """
        Zapis (lub aktualizacja) oferty do bazy.
        Parametry:
        - offer_data: z kluczami: id, title, price, location, contract, work_load, description, url
        - vector: opcjonalny wektor w formacie numpy (np.ndarray)
        """
        query = """
        INSERT OR REPLACE INTO offers 
        (id, title, price, location, contract, work_load, description, url, source, vector) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor = self.conn.cursor()
        
        cursor.execute(query, (
            offer_data.get('id'),
            offer_data.get('title'),
            offer_data.get('price'),
            offer_data.get('location'),
            offer_data.get('contract'),
            offer_data.get('work_load'),
            offer_data.get('description'),
            offer_data.get('url'),
            offer_data.get('source'),
            vector
        ))
        self.conn.commit()

    def get_offer_by_id(self, offer_id):
        """
        Wyszukanie i odczyt pojedynczej oferty po id.
        Zwraca słownik z danymi lub None.
        """
        query = "SELECT * FROM offers WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (offer_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_offer_by_url(self, url):
        """
        Wyszukanie pojedynczej oferty na podstawie URL.
        Zwraca słownik z danymi lub None.
        """
        query = "SELECT * FROM offers WHERE url = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (url,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_offers(self):
        """
        Odczyt wszystkich ofert z bazy.
        Zwraca listę słowników.
        """
        query = "SELECT * FROM offers"
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_offer_by_id(self, offer_id):
        """
        Usuwanie pojedynczej oferty po id.
        """
        query = "DELETE FROM offers WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (offer_id,))
        self.conn.commit()

    def delete_all_offers(self):
        """
        Czyszczenie całej bazy danych ofert.
        """
        query = "DELETE FROM offers"
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
    
    def close(self):
        """
        Zamknięcie połączenia z bazą.
        """
        self.conn.close()
    
    # Kontekst menadżer do ułatwienia zarządzania połączeniem (z użyciem instrukcji with)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
