const JOURNAL_KEY = 'tarot_journal_v1';
const MAX_ENTRIES = 40;

function readAll() {
  try {
    const raw = localStorage.getItem(JOURNAL_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeAll(entries) {
  localStorage.setItem(JOURNAL_KEY, JSON.stringify(entries.slice(0, MAX_ENTRIES)));
}

export function loadJournal() {
  return readAll();
}

export function saveJournalEntry(entry) {
  const id = entry.id || (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()));
  const record = {
    ...entry,
    id,
    createdAt: entry.createdAt || new Date().toISOString(),
  };
  const next = [record, ...readAll().filter((item) => item.id !== id)];
  writeAll(next);
  return record;
}

export function removeJournalEntry(id) {
  writeAll(readAll().filter((item) => item.id !== id));
}

export function clearJournal() {
  writeAll([]);
}

export function snapshotCards(drawnCards, spread) {
  return (drawnCards || []).map((item, index) => ({
    name: item.card?.name,
    name_cn: item.card?.name_cn,
    img: item.card?.img,
    reversed: !!item.reversed,
    position: spread?.positions?.[index] || item.position || '',
    position_cn: spread?.positions_cn?.[index] || item.position_cn || '',
  }));
}
