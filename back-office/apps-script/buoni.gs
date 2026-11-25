/**
 * Buoni digitali — I Monili Ravenna (Modulo B2 del back-office).
 * PRD: docs/prd-back-office.md §5.
 *
 * Gira nel progetto Apps Script LEGATO al foglio «Buoni digitali 2026»,
 * sull'account moniliravenna@gmail.com. Questa è una copia: quella viva è su Google.
 *
 * Regole (brainstorming §10): un buono vale in UN solo negozio (17 o 21); importo libero;
 * uso parziale con saldo; scadenza a un mese (Natale 2026: 25/1/2027); al portatore;
 * il saldo si calcola dai movimenti; nessun doppio addebito.
 *
 * Il foglio NON si modifica a mano: si usa il menu «Buoni».
 */

var CONFIG = {
  TZ: 'Europe/Rome',
  NEGOZI: ['17', '21'],
  CONSEGNE: ['digitale', 'ritiro'],
  METODI: ['bonifico', 'sumup', 'satispay'],
  SCADENZA_MESI: 1,
  // ASSUNZIONE DA CONFERMARE CON MATTEO: i buoni emessi in questa finestra scadono il 25/1/2027.
  NATALE: { DAL: '2026-11-25', AL: '2026-12-25', SCADENZA: '2027-01-25' },
  PREFISSO: 'MD-',
  LUNGHEZZA_CODICE: 12,
  ALFABETO: 'ABCDEFGHJKMNPQRSTUVWXYZ23456789', // 31 caratteri, senza 0/O, 1/I/L
  FOGLIO_BUONI: 'Buoni',
  FOGLIO_MOVIMENTI: 'Movimenti'
};

var COL_BUONI = ['riferimento', 'codice', 'negozio', 'importo', 'saldo', 'emissione', 'scadenza',
  'stato', 'consegna', 'metodo', 'rif_pagamento', 'acquirente', 'contatto', 'destinatario',
  'messaggio', 'note'];
var COL_MOV = ['codice', 'data', 'tipo', 'importo', 'operatore', 'id_operazione', 'nota'];
var STATI = ['in attesa', 'attivo', 'usato', 'scaduto', 'annullato'];

/* ---------- funzioni pure (provate anche fuori da Google) ---------- */

function codiceDaByte_(bytes, lunghezza, alfabeto) {
  // Scarta i byte che sbilancerebbero la distribuzione (niente bias).
  var n = alfabeto.length, limite = 256 - (256 % n), out = '';
  for (var i = 0; i < bytes.length && out.length < lunghezza; i++) {
    var b = bytes[i] & 255;
    if (b < limite) out += alfabeto.charAt(b % n);
  }
  return out;
}

function formattaCodice_(grezzo) {
  return CONFIG.PREFISSO + grezzo.match(/.{1,4}/g).join('-');
}

function normalizzaCodice_(testo) {
  var t = String(testo || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (t.length === CONFIG.LUNGHEZZA_CODICE + 2 && t.indexOf('MD') === 0) t = t.substring(2);
  return t.length === CONFIG.LUNGHEZZA_CODICE ? formattaCodice_(t) : '';
}

function aggiungiMesi_(iso, mesi) {
  var p = iso.split('-'), y = +p[0], m = +p[1] - 1, d = +p[2];
  var dt = new Date(Date.UTC(y, m + mesi, 1));
  var ultimo = new Date(Date.UTC(dt.getUTCFullYear(), dt.getUTCMonth() + 1, 0)).getUTCDate();
  dt.setUTCDate(Math.min(d, ultimo));
  return dt.toISOString().substring(0, 10);
}

function calcolaScadenza_(emissioneIso) {
  var n = CONFIG.NATALE;
  if (emissioneIso >= n.DAL && emissioneIso <= n.AL) return n.SCADENZA;
  return aggiungiMesi_(emissioneIso, CONFIG.SCADENZA_MESI);
}

function importoValido_(v) {
  var n = Number(v);
  return isFinite(n) && n > 0 && Math.abs(n * 100 - Math.round(n * 100)) < 1e-6;
}

if (typeof module !== 'undefined') {
  module.exports = { CONFIG: CONFIG, codiceDaByte_: codiceDaByte_, formattaCodice_: formattaCodice_,
    normalizzaCodice_: normalizzaCodice_, aggiungiMesi_: aggiungiMesi_,
    calcolaScadenza_: calcolaScadenza_, importoValido_: importoValido_ };
}

/* ---------- accesso al foglio ---------- */

function oggi_() { return Utilities.formatDate(new Date(), CONFIG.TZ, 'yyyy-MM-dd'); }
function ss_() { return SpreadsheetApp.getActiveSpreadsheet(); }

function casuali_(quanti) {
  // UUID v4 di Google: casuale crittografico. 32 cifre esadecimali = 16 byte per UUID.
  var bytes = [];
  while (bytes.length < quanti) {
    var hex = Utilities.getUuid().replace(/-/g, '');
    for (var i = 0; i < hex.length; i += 2) bytes.push(parseInt(hex.substr(i, 2), 16));
  }
  return bytes;
}

function nuovoGrezzo_(lunghezza) {
  var out = '';
  while (out.length < lunghezza) {
    out += codiceDaByte_(casuali_(32), lunghezza - out.length, CONFIG.ALFABETO);
  }
  return out;
}

function leggi_(foglio, colonne) {
  var n = foglio.getLastRow() - 1;
  if (n < 1) return [];
  var v = foglio.getRange(2, 1, n, colonne.length).getValues();
  return v.map(function (r, i) {
    var o = { _riga: i + 2 };
    colonne.forEach(function (c, k) { o[c] = r[k]; });
    return o;
  });
}

function buoni_() { return leggi_(ss_().getSheetByName(CONFIG.FOGLIO_BUONI), COL_BUONI); }
function movimenti_() { return leggi_(ss_().getSheetByName(CONFIG.FOGLIO_MOVIMENTI), COL_MOV); }

function scrivi_(foglio, colonne, oggetto) {
  var riga = colonne.map(function (c) { return oggetto[c] === undefined ? '' : oggetto[c]; });
  var r = foglio.getLastRow() + 1;
  foglio.getRange(r, 1, 1, colonne.length).setValues([riga]);
  return r;
}

function impostaCella_(riga, colonna, valore) {
  ss_().getSheetByName(CONFIG.FOGLIO_BUONI).getRange(riga, COL_BUONI.indexOf(colonna) + 1).setValue(valore);
}

function saldoDa_(codice) {
  var s = 0;
  movimenti_().forEach(function (m) { if (m.codice === codice) s += Number(m.importo); });
  return Math.round(s * 100) / 100;
}

function aggiungiMovimento_(codice, tipo, importo, operatore, idOp, nota) {
  scrivi_(ss_().getSheetByName(CONFIG.FOGLIO_MOVIMENTI), COL_MOV, {
    codice: codice, data: oggi_(), tipo: tipo, importo: importo,
    operatore: operatore || Session.getActiveUser().getEmail() || 'sconosciuto',
    id_operazione: idOp || '', nota: nota || ''
  });
}

function conBlocco_(fn) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try { return fn(); } finally { lock.releaseLock(); }
}

function ko_(m) { return { ok: false, messaggio: m }; }

/* ---------- operazioni ---------- */

/** Richiesta dal sito: nasce «in attesa», senza codice e senza credito. */
function creaRichiesta(d) {
  if (CONFIG.NEGOZI.indexOf(String(d.negozio)) < 0) return ko_('Negozio non valido (17 o 21).');
  if (!importoValido_(d.importo)) return ko_('Importo non valido.');
  if (CONFIG.CONSEGNE.indexOf(d.consegna) < 0) return ko_('Consegna non valida.');
  if (CONFIG.METODI.indexOf(d.metodo) < 0) return ko_('Metodo di pagamento non valido.');
  return conBlocco_(function () {
    var esistenti = {};
    buoni_().forEach(function (b) { esistenti[b.riferimento] = true; });
    var rif;
    do { rif = 'R-' + nuovoGrezzo_(6); } while (esistenti[rif]);
    scrivi_(ss_().getSheetByName(CONFIG.FOGLIO_BUONI), COL_BUONI, {
      riferimento: rif, negozio: String(d.negozio), importo: Number(d.importo), saldo: 0,
      stato: 'in attesa', consegna: d.consegna, metodo: d.metodo,
      acquirente: d.acquirente || '', contatto: d.contatto || '', destinatario: d.destinatario || '',
      messaggio: d.messaggio || '', note: d.note || ''
    });
    return { ok: true, riferimento: rif };
  });
}

/** Dopo aver verificato l'incasso: genera il codice e dà credito. */
function attiva(riferimento, rifPagamento, operatore) {
  return conBlocco_(function () {
    var b = buoni_().filter(function (x) { return x.riferimento === riferimento; })[0];
    if (!b) return ko_('Richiesta non trovata.');
    if (b.stato !== 'in attesa') return ko_('La richiesta non è «in attesa» (stato: ' + b.stato + ').');
    var usati = {};
    buoni_().forEach(function (x) { if (x.codice) usati[x.codice] = true; });
    var codice;
    do { codice = formattaCodice_(nuovoGrezzo_(CONFIG.LUNGHEZZA_CODICE)); } while (usati[codice]);
    var em = oggi_();
    impostaCella_(b._riga, 'codice', codice);
    impostaCella_(b._riga, 'emissione', em);
    impostaCella_(b._riga, 'scadenza', calcolaScadenza_(em));
    impostaCella_(b._riga, 'rif_pagamento', rifPagamento || '');
    impostaCella_(b._riga, 'stato', 'attivo');
    aggiungiMovimento_(codice, 'carica', Number(b.importo), operatore, '', 'incasso verificato');
    impostaCella_(b._riga, 'saldo', saldoDa_(codice));
    return { ok: true, codice: codice, negozio: String(b.negozio), scadenza: calcolaScadenza_(em),
             importo: Number(b.importo), consegna: b.consegna };
  });
}

function trovaPerCodice_(codice) {
  var c = normalizzaCodice_(codice);
  if (!c) return null;
  return buoni_().filter(function (x) { return x.codice === c; })[0] || null;
}

function controllo_(b, negozio) {
  // Messaggio generico se il codice non esiste: non rivela nulla.
  if (!b) return ko_('Codice non valido.');
  if (String(b.negozio) !== String(negozio)) return ko_('Buono valido solo nel negozio ' + b.negozio + '.');
  if (b.stato === 'annullato') return ko_('Buono annullato.');
  if (b.stato === 'usato') return ko_('Buono già interamente usato.');
  if (b.stato === 'in attesa') return ko_('Buono non ancora attivo.');
  if (String(b.scadenza) < oggi_()) return ko_('Buono scaduto il ' + b.scadenza + '.');
  return { ok: true };
}

/** Solo lettura: dice se il buono è utilizzabile in quel negozio e con quale saldo. */
function verifica(codice, negozio) {
  var b = trovaPerCodice_(codice), c = controllo_(b, negozio);
  if (!c.ok) return c;
  return { ok: true, codice: b.codice, negozio: String(b.negozio), saldo: saldoDa_(b.codice), scadenza: b.scadenza };
}

/** Scala un importo. idOperazione evita il doppio addebito se la richiesta viene ripetuta. */
function usa(codice, negozio, importo, operatore, idOperazione) {
  if (!importoValido_(importo)) return ko_('Importo non valido.');
  return conBlocco_(function () {
    var b = trovaPerCodice_(codice);
    if (idOperazione && b) {
      var gia = movimenti_().filter(function (m) { return m.codice === b.codice && m.id_operazione === idOperazione; })[0];
      if (gia) return { ok: true, ripetuta: true, saldo: saldoDa_(b.codice), messaggio: 'Operazione già registrata.' };
    }
    var c = controllo_(b, negozio);
    if (!c.ok) return c;
    var saldo = saldoDa_(b.codice), imp = Number(importo);
    if (imp > saldo + 1e-9) return ko_('Saldo insufficiente: restano ' + saldo.toFixed(2) + ' €.');
    aggiungiMovimento_(b.codice, 'uso', -imp, operatore, idOperazione, 'negozio ' + negozio);
    var nuovo = saldoDa_(b.codice);
    impostaCella_(b._riga, 'saldo', nuovo);
    if (nuovo <= 0) impostaCella_(b._riga, 'stato', 'usato');
    return { ok: true, saldo: nuovo, scadenza: b.scadenza };
  });
}

/** Recesso o errore: azzera il residuo e chiude il buono. Se già usato in parte, decide una persona. */
function annulla(riferimentoOCodice, motivo, operatore) {
  return conBlocco_(function () {
    var chiave = String(riferimentoOCodice || '').trim();
    var cod = normalizzaCodice_(chiave);
    var b = buoni_().filter(function (x) { return x.riferimento === chiave || (cod && x.codice === cod); })[0];
    if (!b) return ko_('Buono non trovato.');
    if (b.stato === 'annullato') return ko_('Già annullato.');
    if (b.stato === 'in attesa') {
      impostaCella_(b._riga, 'stato', 'annullato');
      impostaCella_(b._riga, 'note', ((b.note || '') + ' annullato: ' + (motivo || '')).trim());
      return { ok: true };
    }
    var saldo = saldoDa_(b.codice);
    if (saldo !== Number(b.importo)) {
      return ko_('Il buono è stato già usato in parte (saldo ' + saldo.toFixed(2) + ' €): serve una decisione a mano.');
    }
    aggiungiMovimento_(b.codice, 'annullo', -saldo, operatore, '', motivo || '');
    impostaCella_(b._riga, 'saldo', 0);
    impostaCella_(b._riga, 'stato', 'annullato');
    return { ok: true };
  });
}

/** Ogni giorno: i buoni attivi oltre la scadenza passano a «scaduto». */
function aggiornaScaduti() {
  return conBlocco_(function () {
    var n = 0;
    buoni_().forEach(function (b) {
      if (b.stato === 'attivo' && String(b.scadenza) < oggi_()) { impostaCella_(b._riga, 'stato', 'scaduto'); n++; }
    });
    return n;
  });
}

/** Il saldo scritto nel foglio deve coincidere con la somma dei movimenti. */
function controllaCoerenza() {
  var problemi = [];
  buoni_().forEach(function (b) {
    if (b.codice && saldoDa_(b.codice) !== Number(b.saldo)) problemi.push(b.codice + ': saldo foglio ' + b.saldo + ' ≠ movimenti ' + saldoDa_(b.codice));
    if (b.stato !== 'in attesa' && b.stato !== 'annullato' && !b.codice) problemi.push(b.riferimento + ': nessun codice');
  });
  return problemi;
}

/* ---------- preparazione del foglio, trigger e menu ---------- */

function preparaFoglio() {
  var ss = ss_();
  [[CONFIG.FOGLIO_BUONI, COL_BUONI], [CONFIG.FOGLIO_MOVIMENTI, COL_MOV]].forEach(function (x) {
    var f = ss.getSheetByName(x[0]) || ss.insertSheet(x[0]);
    f.getRange(1, 1, 1, x[1].length).setValues([x[1]]).setFontWeight('bold');
    f.setFrozenRows(1);
    // Testo semplice per tutto tranne gli importi: date AAAA-MM-GG e numeri che iniziano con «+» non si rovinano.
    f.getRange(2, 1, 1000, x[1].length).setNumberFormat('@');
  });
  var b = ss.getSheetByName(CONFIG.FOGLIO_BUONI), m = ss.getSheetByName(CONFIG.FOGLIO_MOVIMENTI);
  ['importo', 'saldo'].forEach(function (c) { b.getRange(2, COL_BUONI.indexOf(c) + 1, 1000, 1).setNumberFormat('0.00'); });
  m.getRange(2, COL_MOV.indexOf('importo') + 1, 1000, 1).setNumberFormat('0.00');
  var rega = SpreadsheetApp.newDataValidation();
  b.getRange(2, COL_BUONI.indexOf('stato') + 1, 1000, 1).setDataValidation(rega.requireValueInList(STATI, true).build());
  b.getRange(2, COL_BUONI.indexOf('negozio') + 1, 1000, 1).setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(CONFIG.NEGOZI, true).build());
  var def = ss.getSheetByName('Foglio1') || ss.getSheetByName('Sheet1');
  if (def && ss.getSheets().length > 2) ss.deleteSheet(def);
  b.setColumnWidths(1, COL_BUONI.length, 120);
  SpreadsheetApp.getUi().alert('Fogli «Buoni» e «Movimenti» pronti. Ora esegui installaTrigger.');
}

function installaTrigger() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'aggiornaScaduti') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('aggiornaScaduti').timeBased().everyDays(1).atHour(6).create();
}

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Buoni')
    .addItem('Attiva richiesta selezionata (dopo l\'incasso)', 'menuAttiva')
    .addItem('Verifica un buono', 'menuVerifica')
    .addItem('Usa un buono', 'menuUsa')
    .addItem('Annulla riga selezionata', 'menuAnnulla')
    .addSeparator()
    .addItem('Controlla coerenza saldi', 'menuCoerenza')
    .addToUi();
}

function chiedi_(titolo, testo) {
  var r = SpreadsheetApp.getUi().prompt(titolo, testo, SpreadsheetApp.getUi().ButtonSet.OK_CANCEL);
  return r.getSelectedButton() === SpreadsheetApp.getUi().Button.OK ? r.getResponseText().trim() : null;
}
function dire_(t) { SpreadsheetApp.getUi().alert(t); }

function rigaSelezionata_() {
  var f = ss_().getActiveSheet();
  if (f.getName() !== CONFIG.FOGLIO_BUONI || f.getActiveRange().getRow() < 2) return null;
  return buoni_().filter(function (b) { return b._riga === f.getActiveRange().getRow(); })[0] || null;
}

function menuAttiva() {
  var b = rigaSelezionata_();
  if (!b) return dire_('Seleziona una riga nella scheda «Buoni».');
  var rif = chiedi_('Attiva ' + b.riferimento, 'Importo da incassare: ' + b.importo + ' €, negozio ' + b.negozio + ', metodo ' + b.metodo +
    '. Hai verificato l\'incasso? Scrivi il riferimento del pagamento (causale o nota) per confermare:');
  if (rif === null) return;
  var r = attiva(b.riferimento, rif);
  dire_(r.ok ? 'Attivato. Codice: ' + r.codice + '\nNegozio ' + r.negozio + ', scade il ' + r.scadenza + '.\nInvialo alla cliente (consegna: ' + r.consegna + ').' : r.messaggio);
}

function menuVerifica() {
  var c = chiedi_('Verifica buono', 'Codice:'); if (c === null) return;
  var n = chiedi_('Verifica buono', 'Sei nel negozio (17 o 21)?'); if (n === null) return;
  var r = verifica(c, n);
  dire_(r.ok ? 'Valido. Saldo ' + r.saldo.toFixed(2) + ' €, scade il ' + r.scadenza + '.' : r.messaggio);
}

function menuUsa() {
  var c = chiedi_('Usa buono', 'Codice:'); if (c === null) return;
  var n = chiedi_('Usa buono', 'Sei nel negozio (17 o 21)?'); if (n === null) return;
  var v = verifica(c, n);
  if (!v.ok) return dire_(v.messaggio);
  var i = chiedi_('Usa buono', 'Saldo ' + v.saldo.toFixed(2) + ' €. Importo da scalare:'); if (i === null) return;
  var idOp = Utilities.getUuid();
  var r = usa(c, n, String(i).replace(',', '.'), null, idOp);
  dire_(r.ok ? 'Fatto. Saldo residuo ' + r.saldo.toFixed(2) + ' €.' : r.messaggio);
}

function menuAnnulla() {
  var b = rigaSelezionata_();
  if (!b) return dire_('Seleziona una riga nella scheda «Buoni».');
  var m = chiedi_('Annulla ' + b.riferimento, 'Motivo (es. recesso):'); if (m === null) return;
  var r = annulla(b.riferimento, m);
  dire_(r.ok ? 'Annullato.' : r.messaggio);
}

function menuCoerenza() {
  var p = controllaCoerenza();
  dire_(p.length ? p.join('\n') : 'Tutto coerente.');
}

/* ---------- collaudo con dati finti ---------- */

function attendi_(cond, msg) { if (!cond) throw new Error('PROVA FALLITA: ' + msg); }

/** Esegui da Apps Script. Usa dati finti marcati PROVA; poi esegui puliziaProva. */
function provaCollaudo() {
  var base = { negozio: '17', importo: 50, consegna: 'digitale', metodo: 'satispay', note: 'PROVA' };
  var r = creaRichiesta(base); attendi_(r.ok, 'richiesta');
  attendi_(!verifica('MD-AAAA-BBBB-CCCC', '17').ok, 'codice inesistente');
  var a = attiva(r.riferimento, 'PROVA-1'); attendi_(a.ok, 'attivazione');
  attendi_(!attiva(r.riferimento, 'x').ok, 'doppia attivazione');
  attendi_(a.codice.indexOf('MD-') === 0, 'prefisso');
  attendi_(!verifica(a.codice, '21').ok, 'negozio sbagliato');
  attendi_(usa(a.codice, '17', 20, 'prova', 'op1').ok, 'uso 20');
  var rip = usa(a.codice, '17', 20, 'prova', 'op1');
  attendi_(rip.ok && rip.ripetuta && rip.saldo === 30, 'ripetizione non deve riaddebitare');
  attendi_(!usa(a.codice, '17', 40, 'prova', 'op2').ok, 'oltre saldo');
  attendi_(usa(a.codice.toLowerCase().replace(/-/g, ' '), '17', 30, 'prova', 'op3').ok, 'uso del resto, codice digitato male');
  attendi_(!usa(a.codice, '17', 1, 'prova', 'op4').ok, 'buono finito');
  var r2 = creaRichiesta(base), a2 = attiva(r2.riferimento, 'PROVA-2');
  impostaCella_(trovaPerCodice_(a2.codice)._riga, 'scadenza', '2000-01-01');
  attendi_(!usa(a2.codice, '17', 5, 'prova', 'op5').ok, 'scaduto');
  var r3 = creaRichiesta(base), a3 = attiva(r3.riferimento, 'PROVA-3');
  attendi_(annulla(a3.codice, 'recesso di prova').ok, 'annullo');
  attendi_(!usa(a3.codice, '17', 5, 'prova', 'op6').ok, 'annullato');
  attendi_(!creaRichiesta({ negozio: '99', importo: 10, consegna: 'digitale', metodo: 'sumup' }).ok, 'negozio 99');
  attendi_(!creaRichiesta({ negozio: '17', importo: -5, consegna: 'digitale', metodo: 'sumup' }).ok, 'importo negativo');
  var p = controllaCoerenza(); attendi_(p.length === 0, 'coerenza: ' + p.join('; '));
  Logger.log('Collaudo superato.');
  return 'Collaudo superato. Esegui puliziaProva per togliere le righe di prova.';
}

function puliziaProva() {
  var f = ss_().getSheetByName(CONFIG.FOGLIO_BUONI), codici = {};
  buoni_().reverse().forEach(function (b) {
    if (String(b.note).indexOf('PROVA') >= 0) { if (b.codice) codici[b.codice] = true; f.deleteRow(b._riga); }
  });
  var m = ss_().getSheetByName(CONFIG.FOGLIO_MOVIMENTI);
  movimenti_().reverse().forEach(function (x) { if (codici[x.codice]) m.deleteRow(x._riga); });
}
