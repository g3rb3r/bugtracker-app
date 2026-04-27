# 🎮 Bug Tracker - Panel QA

Aplikacja do zarządzania zgłoszeniami błędów w grach, stworzona dla zespołów QA.

## ✨ Funkcje

### 📋 Zarządzanie bugami
- **Dodawanie nowych bugów** z pełnym formularzem
- **Przeglądanie bugów** w trzech kategoriach: Wszystkie, W trakcie, Zakończone
- **Edycja istniejących bugów** z możliwością aktualizacji wszystkich pól
- **Usuwanie bugów** z potwierdzeniem

### 📸 Funkcjonalność screenshotsów
- **Dodawanie screenshotsów** do zgłoszeń (opcjonalne)
- **Automatyczne zapisywanie** w folderze `screenshots/`
- **Inteligentne nazewnictwo** plików: `tytuł_buga_1.png`, `tytuł_buga_2.png`, itd.
- **Podgląd miniatur** w oknie szczegółów buga
- **Powiększanie screenshotsów** po kliknięciu w miniaturę
- **Obsługa wielu formatów**: PNG, JPG, JPEG, GIF, BMP

### 🎨 Responsywny interfejs
- **Elastyczne okna** dostosowujące się do rozmiaru ekranu
- **Intuicyjny design** z kolorowymi przyciskami i ikonami
- **Przewijanie** w długich formularzach

## 🚀 Instalacja i uruchomienie

### Wymagania
- Python 3.6+
- Biblioteka PIL (Pillow)

### Instalacja zależności
```bash
pip install Pillow
```

### Uruchomienie
```bash
python main.py
```

## 📁 Struktura plików

```
bugtracker_app/
├── main.py              # Główny plik aplikacji
├── bugs.json            # Baza danych bugów
├── screenshots/         # Folder na screenshotsy
├── assets/             # Zasoby aplikacji
└── README.md           # Ten plik
```

## 💡 Jak używać

### Dodawanie nowego buga
1. Kliknij przycisk **"➕ Dodaj nowy bug"**
2. Wypełnij wszystkie wymagane pola:
   - Tytuł błędu
   - Informacje o środowisku (wersja gry, platforma, urządzenie, połączenie)
   - Kroki do odtworzenia
   - Oczekiwany i faktyczny rezultat
   - Ważność błędu
   - Notatki
3. **Opcjonalnie**: Dodaj screenshotsy klikając **"📷 Dodaj screenshot"**
4. Kliknij **"💾 Zapisz bug"**

### Przeglądanie i edycja bugów
1. Kliknij na tytuł buga w liście
2. W oknie szczegółów możesz:
   - **Przeglądać** wszystkie informacje
   - **Oglądać screenshotsy** jako miniatury
   - **Kliknąć na miniaturę** aby powiększyć screenshot
   - **Kliknąć "✏️ Edytuj raport"** aby włączyć tryb edycji
   - **Zmienić status** w trybie edycji
   - **Zapisać zmiany** lub **anulować edycję**

### Zarządzanie screenshotsami
- **Dodawanie**: Wybierz plik obrazu w formularzu
- **Usuwanie**: Kliknij ❌ obok nazwy pliku
- **Podgląd**: Kliknij na miniaturę w oknie szczegółów
- **Automatyczne nazewnictwo**: Pliki są zapisywane jako `tytuł_buga_1.png`, `tytuł_buga_2.png`, itd.

## 🔧 Konfiguracja

### Obsługiwane formaty obrazów
- PNG (zalecane)
- JPG/JPEG
- GIF
- BMP

### Maksymalny rozmiar miniatur
- Domyślnie: 80x80 pikseli
- Podgląd: Dostosowany do rozmiaru ekranu

## 🐛 Rozwiązywanie problemów

### Błąd "Nie można wyświetlić obrazu"
- Sprawdź czy plik obrazu nie jest uszkodzony
- Upewnij się, że format jest obsługiwany

### Screenshotsy nie są widoczne
- Sprawdź czy folder `screenshots/` istnieje
- Upewnij się, że pliki zostały poprawnie skopiowane

### Błąd przy zapisie
- Sprawdź uprawnienia do zapisu w folderze aplikacji
- Upewnij się, że `bugs.json` nie jest używany przez inną aplikację

## 📝 Format danych

Bugi są zapisywane w pliku `bugs.json` w formacie JSON:

```json
{
  "title": "Tytuł błędu",
  "environment": "Informacje o środowisku",
  "steps": "Kroki do odtworzenia",
  "expected": "Oczekiwany rezultat",
  "actual": "Faktyczny rezultat",
  "severity": "Ważność",
  "notes": "Notatki",
  "status": "Status",
  "screenshots": ["plik1.png", "plik2.png"]
}
```

## 🎯 Funkcje w planach

- [ ] Eksport raportów do PDF
- [ ] Filtrowanie po ważności
- [ ] Wyszukiwanie w treści bugów
- [ ] Statystyki i wykresy
- [ ] Integracja z systemami śledzenia bugów

---

**Autor**: Maja Gebler 
**Wersja**: 1.0  
**Data**: 2024

