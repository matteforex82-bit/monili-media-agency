/**
 * Consulenze da 15 minuti: dal Google Calendar del negozio al foglio «Consulenze».
 * Vedi docs/prd-back-office.md §4. Da incollare in Estensioni → Apps Script, dentro il foglio
 * «Appuntamenti Consulenza 2026» sull'account del negozio. Funziona solo dentro Google: nessun dato esce.
 *
 * Cosa legge (formato reale degli eventi Calendly Free, prova del 24/11/2026):
 *  - titolo «<nome cliente> and I Monili Ravenna»
 *  - luogo = numero di telefono della cliente
 *  - descrizione con i link per annullare e spostare
 * Non copia l'e-mail della cliente. Le risposte alle domande Calendly non arrivano nell'evento.
 */

const CONFIG = {
  SHEET_NAME: 'Consulenze',
  SYNC_DAYS_AHEAD: 60,      // quanto in avanti guarda il calendario
  RETENTION_DAYS: 30,       // un mese dalla fine della consulenza, poi la riga si cancella
  TITLE_SUFFIX: ' and I Monili Ravenna',
  CALENDLY_MARK: 'calendly.com/cancellations',  // riconosce gli eventi creati da Calendly
  // Testo della domanda facoltativa in Calendly (come compare nell'evento, prova del 24/11/2026).
  // Se lo cambi in Calendly, cambialo anche qui, altrimenti nella nota resterà anche il testo della domanda.
  REMINDER_MINUTES: [120, 60],  // avvisi prima della consulenza: 2 ore e 1 ora
  QUESTION_TEXT: /Per favore, condividi tutto ciò che può essere utile per preparare il nostro incontro\.:?\s*/i
};

const HEADERS = ['ID evento', 'Data e ora', 'Nome', 'WhatsApp', 'Annulla', 'Sposta', 'Stato', 'Elimina dal', 'Nota della cliente'];
const COL = { ID: 0, WHEN: 1, NAME: 2, PHONE: 3, CANCEL: 4, RESCHEDULE: 5, STATE: 6, DELETE_AFTER: 7, NOTE: 8 };
const STATE_BOOKED = 'prenotata';
const STATE_CANCELLED = 'annullata';

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(CONFIG.SHEET_NAME);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
    sheet.hideColumns(1 + COL.ID);
    // Stato scelto da elenco: lo staff segna «fatta» o «non presentata» a mano.
    const rule = SpreadsheetApp.newDataValidation()
      .requireValueInList([STATE_BOOKED, 'fatta', 'non presentata', STATE_CANCELLED], true).build();
    sheet.getRange(2, 1 + COL.STATE, 1000, 1).setDataValidation(rule);
  }
  // Intestazioni sempre allineate (aggiunge anche le colonne nuove).
  sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight('bold');
  // Il numero comincia con «+»: senza formato testo Fogli lo legge come formula (#ERROR!).
  sheet.getRange(2, 1 + COL.PHONE, 1000, 1).setNumberFormat('@');
  sheet.getRange(2, 1 + COL.NOTE, 1000, 1).setWrap(true);
  return sheet;
}

function parseEvent_(ev) {
  const description = ev.getDescription() || '';
  if (description.indexOf(CONFIG.CALENDLY_MARK) === -1) return null; // non è una consulenza Calendly
  const title = ev.getTitle() || '';
  const name = title.endsWith(CONFIG.TITLE_SUFFIX) ? title.slice(0, -CONFIG.TITLE_SUFFIX.length) : title;
  const cancel = (description.match(/https:\/\/calendly\.com\/cancellations\/[\w-]+/) || [''])[0];
  const resched = (description.match(/https:\/\/calendly\.com\/reschedulings\/[\w-]+/) || [''])[0];
  // Nota/risposte della cliente: quello che resta della descrizione tolte le parti fisse di Calendly.
  // Formato da confermare con una prenotazione di prova in cui la cliente scrive un commento.
  let note = description.split('Need to make changes to this event?')[0]
    .replace(/<[^>]+>/g, '\n')
    .replace(/Event Name[^\n]*\n?/i, '')
    .replace(/Location:[^\n]*\n?/i, '')
    .replace(/Consulenza Gratuita in videochiamata 15min/i, '')
    // Calendly scrive «<testo della domanda>: <risposta>»: teniamo solo la risposta.
    // Se la cliente non scrive nulla il campo resta vuoto.
    .replace(CONFIG.QUESTION_TEXT, '')
    .replace(/\n{2,}/g, '\n')
    .trim();
  const end = ev.getEndTime();
  const deleteAfter = new Date(end.getTime() + CONFIG.RETENTION_DAYS * 24 * 3600 * 1000);
  return {
    id: ev.getId(),
    start: ev.getStartTime(),
    name: name,
    phone: ev.getLocation() || '',
    cancel: cancel,
    reschedule: resched,
    deleteAfter: deleteAfter,
    note: note
  };
}

/**
 * Scrive una riga. Il numero comincia con «+»: la cella va messa in formato testo PRIMA di scrivere,
 * e si evita appendRow, che interpreta il «+» come formula (#ERROR!).
 */
function scriviRiga_(sheet, rowNumber, line) {
  sheet.getRange(rowNumber, 1 + COL.PHONE).setNumberFormat('@');
  sheet.getRange(rowNumber, 1, 1, HEADERS.length).setValues([line]);
}

/** Allinea il foglio al calendario. Gira ogni 5 minuti (vedi installaTrigger). */
function syncConsulenze() {
  const sheet = getSheet_();
  const now = new Date();
  const from = new Date(now.getTime() - CONFIG.RETENTION_DAYS * 24 * 3600 * 1000);
  const to = new Date(now.getTime() + CONFIG.SYNC_DAYS_AHEAD * 24 * 3600 * 1000);
  const events = CalendarApp.getDefaultCalendar().getEvents(from, to);

  const seen = {};
  events.forEach(function (ev) {
    const data = parseEvent_(ev);
    if (!data) return;
    seen[data.id] = data;
    if (data.start > now) impostaPromemoria_(ev);
  });

  const lastRow = sheet.getLastRow();
  const values = lastRow > 1 ? sheet.getRange(2, 1, lastRow - 1, HEADERS.length).getValues() : [];
  const rowById = {};
  values.forEach(function (row, i) { rowById[row[COL.ID]] = i; });

  // 1) aggiorna o aggiunge
  Object.keys(seen).forEach(function (id) {
    const d = seen[id];
    const line = [d.id, d.start, d.name, d.phone, d.cancel, d.reschedule, STATE_BOOKED, d.deleteAfter, d.note];
    if (id in rowById) {
      const i = rowById[id];
      const current = values[i];
      // Stato scelto a mano (fatta, non presentata) resta; se era annullata e l'evento è tornato, torna prenotata.
      const state = current[COL.STATE] && current[COL.STATE] !== STATE_CANCELLED ? current[COL.STATE] : STATE_BOOKED;
      line[COL.STATE] = state;
      scriviRiga_(sheet, i + 2, line);
    } else {
      scriviRiga_(sheet, sheet.getLastRow() + 1, line);
    }
  });

  // 2) l'evento è sparito dal calendario e la consulenza era futura: la cliente ha annullato
  values.forEach(function (row, i) {
    const id = row[COL.ID];
    if (id in seen) return;
    const when = new Date(row[COL.WHEN]);
    if (when > now && row[COL.STATE] === STATE_BOOKED) {
      sheet.getRange(i + 2, 1 + COL.STATE).setValue(STATE_CANCELLED);
    }
  });

  cancellaScadute_();
  cancellaEventiScaduti_();
}

/**
 * Cancella dal Calendario gli eventi Calendly finiti da più di RETENTION_DAYS (nome e numero della cliente
 * restano altrimenti per sempre nel Calendario). Tocca solo eventi con la firma di Calendly.
 * Google Calendario li tiene ancora nel cestino per circa 30 giorni.
 */
function cancellaEventiScaduti_() {
  const day = 24 * 3600 * 1000;
  const now = new Date();
  const limit = new Date(now.getTime() - CONFIG.RETENTION_DAYS * day);
  const from = new Date(now.getTime() - (CONFIG.RETENTION_DAYS + 120) * day);
  CalendarApp.getDefaultCalendar().getEvents(from, limit).forEach(function (ev) {
    if ((ev.getDescription() || '').indexOf(CONFIG.CALENDLY_MARK) === -1) return;
    if (ev.getEndTime() < limit) ev.deleteEvent();
  });
}

/** Promemoria 2 ore e 1 ora prima, sul calendario del negozio (vedi PRD §4). */
function impostaPromemoria_(ev) {
  const wanted = CONFIG.REMINDER_MINUTES;
  const have = ev.getPopupReminders().slice().sort(function (a, b) { return b - a; });
  const ok = have.length === wanted.length && wanted.every(function (m, i) { return have[i] === m; });
  if (ok) return;
  ev.removeAllReminders();
  wanted.forEach(function (m) { ev.addPopupReminder(m); });
}

/** Cancella le righe oltre la data «Elimina dal» (un mese dopo la consulenza). */
function cancellaScadute_() {
  const sheet = getSheet_();
  const now = new Date();
  for (let r = sheet.getLastRow(); r >= 2; r--) {
    const deleteAfter = sheet.getRange(r, 1 + COL.DELETE_AFTER).getValue();
    if (deleteAfter instanceof Date && deleteAfter < now) sheet.deleteRow(r);
  }
}

/** Da lanciare una volta sola dal menu «Esegui»: crea l'esecuzione automatica ogni 5 minuti. */
function installaTrigger() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'syncConsulenze') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('syncConsulenze').timeBased().everyMinutes(5).create();
  syncConsulenze();
}
