# Frontend i18n Setup - Deutsch, Englisch, Spanisch ✅

## ✅ Implementiert:

### 1. i18n-Konfiguration
- `src/i18n/config.ts` - i18next Konfiguration
- `src/i18n/index.ts` - Exports
- `src/i18n/locales/de.json` - Deutsche Übersetzungen
- `src/i18n/locales/en.json` - Englische Übersetzungen
- `src/i18n/locales/es.json` - Spanische Übersetzungen

### 2. Komponenten
- `src/components/settings/SettingsDashboard.tsx` - Einstellungen mit Language Switcher
- `src/components/settings/LanguageSwitcher.tsx` - Kompakter Language Switcher für Header

### 3. Umgestellte Komponenten
- ✅ `ApprovalQueue.tsx` - Auf i18n umgestellt
- ⏳ `MarketplaceDashboard.tsx` - Kann noch umgestellt werden
- ⏳ Andere Komponenten - Können nach Bedarf umgestellt werden

---

## 📦 Dependencies (package.json)

Füge diese Dependencies hinzu:

```json
{
  "dependencies": {
    "i18next": "^23.7.0",
    "react-i18next": "^13.5.0"
  }
}
```

Installation:
```bash
npm install i18next react-i18next
# oder
yarn add i18next react-i18next
```

---

## 🚀 Setup in der App

### 1. i18n in der Haupt-App initialisieren

In deiner `App.tsx` oder `main.tsx`:

```typescript
import './i18n/config'; // i18n initialisieren
import { SettingsDashboard } from './components/settings/SettingsDashboard';
import { LanguageSwitcher } from './components/settings/LanguageSwitcher';

function App() {
  return (
    <div>
      {/* Language Switcher im Header */}
      <header>
        <LanguageSwitcher />
      </header>
      
      {/* Routes */}
      <Route path="/settings" component={SettingsDashboard} />
    </div>
  );
}
```

### 2. Komponenten verwenden

```typescript
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('common.loading')}</h1>
      <button>{t('common.save')}</button>
    </div>
  );
}
```

---

## 🌍 Unterstützte Sprachen

- 🇩🇪 **Deutsch (de)** - Default
- 🇬🇧 **English (en)**
- 🇪🇸 **Español (es)**

---

## 📝 Translation Keys

### Common
- `common.loading`, `common.error`, `common.success`
- `common.save`, `common.cancel`, `common.delete`
- `common.search`, `common.filter`, etc.

### Settings
- `settings.title`, `settings.language`
- `settings.general`, `settings.notifications`, etc.

### Marketplace
- `marketplace.title`, `marketplace.searchPlaceholder`
- `marketplace.install`, `marketplace.uninstall`, etc.

### Integrations
- `integrations.title`, `integrations.approvalQueue`
- `integrations.approve`, `integrations.reject`, etc.

### Analytics & Realtime
- `analytics.title`, `analytics.overview`
- `realtime.title`, `realtime.metrics`, etc.

---

## 🔧 Language Switcher

### In Settings:
```typescript
import { SettingsDashboard } from './components/settings/SettingsDashboard';

<Route path="/settings" component={SettingsDashboard} />
```

### Im Header (kompakt):
```typescript
import { LanguageSwitcher } from './components/settings/LanguageSwitcher';

<header>
  <LanguageSwitcher />
</header>
```

---

## ✅ Status

- ✅ i18n-Konfiguration erstellt
- ✅ Translation-Dateien (DE, EN, ES)
- ✅ Settings Dashboard mit Language Switcher
- ✅ Language Switcher Komponente
- ✅ ApprovalQueue auf i18n umgestellt
- ⏳ MarketplaceDashboard kann noch umgestellt werden
- ⏳ Weitere Komponenten nach Bedarf

---

## 📌 Nächste Schritte

1. **Dependencies installieren:**
   ```bash
   npm install i18next react-i18next
   ```

2. **i18n in App initialisieren:**
   ```typescript
   import './i18n/config';
   ```

3. **Language Switcher hinzufügen:**
   - In Settings: `<SettingsDashboard />`
   - Im Header: `<LanguageSwitcher />`

4. **Weitere Komponenten umstellen:**
   - `MarketplaceDashboard.tsx`
   - `AnalyticsDashboard.tsx`
   - `RealtimeDashboard.tsx`
   - etc.

---

**Frontend i18n ist bereit!** 🎉

Die Sprache wird in `localStorage` gespeichert und bleibt nach Reload erhalten.
