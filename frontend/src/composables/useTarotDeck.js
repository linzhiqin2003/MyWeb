export function shuffleDeck(cards) {
  const arr = [...cards];
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export function rollReversed(allow = true, chance = 0.28) {
  return !!allow && Math.random() < chance;
}

export function positionLabel(spread, index, fallback = '') {
  if (!spread) return fallback || `位置 ${index + 1}`;
  return spread.positions_cn?.[index] || spread.positions?.[index] || fallback || `位置 ${index + 1}`;
}

export function cardDisplayName(card) {
  if (!card) return '';
  return card.name_cn ? `${card.name_cn}` : card.name;
}

export function cardImage(card) {
  if (!card?.img) return '';
  return `/cards/${card.img}`;
}

export const VERDICT_META = {
  yes: { label: '是', sub: 'The cards lean yes', cls: 'verdict-yes' },
  lean_yes: { label: '倾向是', sub: 'A yes, with conditions', cls: 'verdict-lean-yes' },
  unclear: { label: '迷雾', sub: 'Not yet a yes or a no', cls: 'verdict-unclear' },
  lean_no: { label: '倾向否', sub: 'A no, unless something shifts', cls: 'verdict-lean-no' },
  no: { label: '否', sub: 'The cards lean no', cls: 'verdict-no' },
};

export const TONE_META = {
  hopeful: { label: '希望', color: '#fbbf24' },
  cautionary: { label: '警醒', color: '#fb7185' },
  transformative: { label: '转化', color: '#c084fc' },
  conflicted: { label: '拉扯', color: '#94a3b8' },
  serene: { label: '宁静', color: '#7dd3fc' },
};

export const CATEGORY_META = {
  glance: '速览',
  classic: '经典',
  depth: '深度',
  relation: '关系',
  decision: '抉择',
  inner: '内在',
  timing: '时序',
};

export const DIFFICULTY_META = {
  beginner: '入门',
  intermediate: '进阶',
  advanced: '高阶',
};
