<template>
  <TarotShell :show-candle="step === 'pick' || step === 'reveal'">
    <div class="w-full max-w-6xl mx-auto flex flex-col items-center px-4 pb-16">
      <div class="text-center my-4 sm:my-6">
        <h2 class="text-2xl sm:text-3xl mb-2 tracking-widest uppercase glow-text">The Ritual</h2>
        <p class="text-gray-400 text-sm italic h-6 font-chinese-body">{{ stepHint }}</p>
      </div>

      <div class="w-full min-h-[560px] flex flex-col items-center justify-start pt-2">
        <transition name="smooth" mode="out-in">
          <div v-if="step === 'spread'" key="spread" class="w-full flex flex-col items-center">
            <h3 class="text-lg text-gray-300 mb-6 tracking-widest uppercase">选择牌阵</h3>
            <SpreadSelector :spreads="spreads" @select="selectSpread" />
          </div>

          <div v-else-if="step === 'input'" key="input" class="w-full max-w-xl flex flex-col items-center pt-8">
            <div class="mb-4 text-center">
              <span class="text-mystic-purple text-sm">{{ selectedSpread?.name_cn }}</span>
              <span class="text-gray-500 text-xs ml-2">({{ selectedSpread?.card_count }} 张)</span>
            </div>
            <input
              v-model="question"
              type="text"
              placeholder="把问题放进这道缝里…"
              class="w-full bg-transparent border-b-2 border-mystic-gold p-4 text-xl sm:text-2xl focus:outline-none text-center placeholder-gray-600 transition-colors focus:border-mystic-purple font-chinese-body"
              @keydown.enter="handleEnter"
              @compositionstart="isComposing = true"
              @compositionend="isComposing = false"
            />
            <label class="mt-8 flex items-center gap-3 text-sm text-gray-400 cursor-pointer select-none">
              <input v-model="allowReversed" type="checkbox" class="accent-mystic-gold" />
              <span class="font-chinese-body">允许逆位（约三成机会，阴影面向你）</span>
            </label>
            <div class="flex gap-4 mt-10">
              <button type="button" class="px-6 py-2 border border-gray-600 text-gray-400 hover:border-mystic-gold hover:text-mystic-gold transition-all" @click="step = 'spread'">
                ← 返回
              </button>
              <button
                type="button"
                :disabled="!question"
                class="px-10 py-3 border border-mystic-gold hover:bg-mystic-gold hover:text-black transition-all duration-500 uppercase tracking-widest disabled:opacity-50 disabled:cursor-not-allowed"
                @click="startShuffle"
              >
                开始仪式
              </button>
            </div>
          </div>

          <div v-else-if="step === 'shuffle'" key="shuffle" class="w-full h-80 flex flex-col items-center justify-center relative">
            <div class="relative w-40 h-60 sm:w-48 sm:h-72 shuffle-container">
              <div
                v-for="index in 10"
                :key="index"
                class="absolute w-full h-full rounded-xl shadow-2xl shuffle-card overflow-hidden border border-mystic-gold/70"
                :style="{ '--delay': `${index * 0.07}s`, '--offset': `${(index - 5) * 4}px`, zIndex: 12 - index }"
              >
                <img src="/mystic/tarot-card-back.jpg" alt="" class="w-full h-full object-cover" />
              </div>
            </div>
            <div class="mt-8 text-mystic-purple tracking-widest uppercase text-sm flex items-center gap-2">
              <span class="shuffle-dot"></span>
              <span class="shuffle-dot" style="animation-delay: 0.2s"></span>
              <span class="shuffle-dot" style="animation-delay: 0.4s"></span>
              <span class="ml-2">洗牌 · Shuffling the Arcana</span>
            </div>
          </div>

          <div v-else-if="step === 'pick'" key="pick" class="w-full flex flex-col items-center">
            <div class="relative w-full h-[320px] sm:h-[380px] md:h-[450px] rounded-2xl md:rounded-3xl overflow-hidden">
              <img src="/tarot-table-bg.png" alt="" class="absolute inset-0 w-full h-full object-cover" />
              <div class="absolute inset-0 vignette-overlay"></div>
              <div class="absolute inset-0 bg-gradient-to-t from-mystic-dark via-transparent to-mystic-dark/50"></div>
              <div class="absolute top-4 sm:top-6 left-0 right-0 text-center z-20">
                <span class="text-mystic-gold text-base sm:text-xl drop-shadow-lg bg-black/50 px-4 sm:px-6 py-1.5 sm:py-2 rounded-full">
                  请抽出 {{ remainingPicks }} 张 · {{ positionLabel(selectedSpread, drawnCards.length) }}
                </span>
              </div>
              <div class="absolute bottom-8 sm:bottom-12 left-0 right-0 flex justify-center overflow-visible px-2">
                <div class="relative w-full" :style="{ maxWidth: containerWidth + 'px', height: isMobile ? '100px' : '140px' }">
                  <button
                    v-for="(card, index) in shuffledDeck.slice(0, displayCardCount)"
                    :key="card.id"
                    type="button"
                    class="deck-card absolute transition-all duration-300 hover:z-[100] p-0 border-0 bg-transparent"
                    :class="[
                      isMobile ? 'w-10 h-14 hover:-translate-y-4' : 'w-14 h-20 md:w-16 md:h-24 hover:-translate-y-8 hover:scale-110',
                      pickedIndices.has(index) ? 'card-fly-out pointer-events-none' : '',
                      cardsRevealed ? 'card-slide-in' : 'opacity-0',
                    ]"
                    :style="getHorizontalStyle(index)"
                    @click="pickCard(index)"
                  >
                    <img src="/mystic/tarot-card-back.jpg" alt="" class="w-full h-full object-cover rounded-md border border-mystic-gold shadow-xl" />
                  </button>
                </div>
              </div>
            </div>

            <transition-group v-if="drawnCards.length" name="selected-card" tag="div" class="flex justify-center flex-wrap gap-3 sm:gap-6 mt-4 sm:mt-6 px-2">
              <button
                v-for="(readingCard, index) in drawnCards"
                :key="readingCard.deckIndex"
                type="button"
                class="text-center cursor-pointer group bg-transparent border-0 p-0"
                @click="undoCardSelection(index)"
              >
                <span class="text-mystic-purple text-xs block mb-1 sm:mb-2 font-medium truncate max-w-[72px]">
                  {{ positionLabel(selectedSpread, index) }}
                </span>
                <div class="w-12 h-[4.5rem] sm:w-16 sm:h-24 rounded-lg overflow-hidden border-2 border-mystic-gold group-hover:border-red-500 transition-all">
                  <img src="/mystic/tarot-card-back.jpg" alt="" class="w-full h-full object-cover" />
                </div>
                <span class="text-gray-500 text-xs mt-1 block opacity-0 group-hover:opacity-100">撤销</span>
              </button>
            </transition-group>
          </div>

          <div v-else-if="step === 'reveal'" key="reveal" class="w-full flex flex-col items-center">
            <SpreadLayout :spread="selectedSpread" :drawn-cards="drawnCards" @reveal="revealCard" />
            <ReadingResult
              v-if="allRevealed"
              class="mt-10 w-full"
              :loading="loadingAI"
              :interpretation="aiInterpretation"
              :summary="aiSummary"
              :advice="aiAdvice"
              :tone="aiTone"
              :spread="selectedSpread"
              :drawn-cards="drawnCards"
              @again="reset"
              @save-image="exportAsImage"
              @save-text="exportAsText"
            />
          </div>
        </transition>
      </div>
    </div>
  </TarotShell>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import html2canvas from 'html2canvas';
import FileSaver from 'file-saver';
import api from '../../api/tarot';
import SpreadSelector from '../../components/tarot/SpreadSelector.vue';
import SpreadLayout from '../../components/tarot/SpreadLayout.vue';
import ReadingResult from '../../components/tarot/ReadingResult.vue';
import TarotShell from '../../components/tarot/TarotShell.vue';
import { positionLabel, rollReversed, shuffleDeck } from '../../composables/useTarotDeck';
import { saveJournalEntry, snapshotCards } from '../../composables/useTarotJournal';

const step = ref('spread');
const question = ref('');
const deck = ref([]);
const shuffledDeck = ref([]);
const spreads = ref([]);
const selectedSpread = ref(null);
const drawnCards = ref([]);
const pickedIndices = ref(new Set());
const aiInterpretation = ref('');
const aiSummary = ref('');
const aiAdvice = ref('');
const aiTone = ref('');
const loadingAI = ref(false);
const isComposing = ref(false);
const cardsRevealed = ref(false);
const allowReversed = ref(true);
const isMobile = ref(false);
const containerWidth = ref(900);

const updateLayout = () => {
  const width = window.innerWidth;
  isMobile.value = width < 768;
  containerWidth.value = Math.min(900, Math.max(300, width - 32));
};

onMounted(async () => {
  updateLayout();
  window.addEventListener('resize', updateLayout);
  try {
    const [cardsRes, spreadsRes] = await Promise.all([api.getCards(), api.getSpreads()]);
    deck.value = cardsRes.data;
    spreads.value = spreadsRes.data;
  } catch (e) {
    console.error('Failed to load data', e);
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', updateLayout);
});

const displayCardCount = computed(() => shuffledDeck.value.length);
const remainingPicks = computed(() => (selectedSpread.value?.card_count || 3) - drawnCards.value.length);
const allRevealed = computed(() => drawnCards.value.length > 0 && drawnCards.value.every((c) => c.revealed));
const stepHint = computed(() => {
  switch (step.value) {
    case 'spread': return '选一种问法，决定故事有多深…';
    case 'input': return '把注意力放进问题里';
    case 'shuffle': return '';
    case 'pick': return '凭直觉抽牌，不必解释为什么是这一张';
    case 'reveal': return '一张一张翻开，让牌自己说话';
    default: return '';
  }
});

function selectSpread(spread) {
  selectedSpread.value = spread;
  allowReversed.value = spread.allow_reversed !== false;
  step.value = 'input';
}

function handleEnter(e) {
  if (isComposing.value || e.isComposing) return;
  startShuffle();
}

function getHorizontalStyle(index) {
  const total = displayCardCount.value || 78;
  const mobile = isMobile.value;
  const cWidth = containerWidth.value;
  const cardWidth = mobile ? 40 : 64;
  const maxOverlap = mobile ? 8 : 12;
  const calculatedOverlap = (cWidth - cardWidth - 20) / (total - 1);
  const overlap = Math.max(3, Math.min(maxOverlap, calculatedOverlap));
  const totalWidth = (total - 1) * overlap + cardWidth;
  const centerOffset = Math.max(10, (cWidth - totalWidth) / 2);
  const xPos = centerOffset + index * overlap;
  const centerIndex = total / 2;
  const distFromCenter = Math.abs(index - centerIndex);
  const arcHeight = Math.pow(distFromCenter, 1.3) * (mobile ? 0.05 : 0.1);
  const rotation = (index - centerIndex) * (mobile ? 0.15 : 0.25);
  return {
    left: `${xPos}px`,
    transform: `translateY(${arcHeight}px) rotate(${rotation}deg)`,
    zIndex: index,
    animationDelay: `${index * 0.006}s`,
  };
}

function startShuffle() {
  if (!question.value || !selectedSpread.value) return;
  shuffledDeck.value = shuffleDeck(deck.value);
  cardsRevealed.value = false;
  step.value = 'shuffle';
  setTimeout(() => {
    step.value = 'pick';
    setTimeout(() => { cardsRevealed.value = true; }, 80);
  }, 2400);
}

function pickCard(index) {
  if (pickedIndices.value.has(index) || remainingPicks.value <= 0) return;
  pickedIndices.value = new Set([...pickedIndices.value, index]);
  drawnCards.value.push({
    card: shuffledDeck.value[index],
    deckIndex: index,
    revealed: false,
    reversed: rollReversed(allowReversed.value),
  });
  if (remainingPicks.value <= 0) {
    setTimeout(() => { step.value = 'reveal'; }, 450);
  }
}

function undoCardSelection(previewIndex) {
  const removed = drawnCards.value[previewIndex];
  if (removed?.deckIndex !== undefined) {
    const next = new Set(pickedIndices.value);
    next.delete(removed.deckIndex);
    pickedIndices.value = next;
  }
  drawnCards.value.splice(previewIndex, 1);
}

function revealCard(index) {
  if (drawnCards.value[index].revealed) return;
  drawnCards.value[index].revealed = true;
  if (drawnCards.value.every((c) => c.revealed)) getAIInterpretation();
}

async function getAIInterpretation() {
  loadingAI.value = true;
  try {
    const payloadCards = drawnCards.value.map((c, i) => ({
      name: c.card.name,
      name_cn: c.card.name_cn,
      position: selectedSpread.value?.positions[i] || `Position ${i + 1}`,
      position_cn: selectedSpread.value?.positions_cn?.[i] || '',
      reversed: c.reversed,
      keywords: c.card.keywords || [],
      meaning: c.reversed
        ? (c.card.meanings_shadow || [])[0]
        : (c.card.meanings_light || [])[0],
    }));
    const response = await api.divine(question.value, payloadCards, selectedSpread.value?.name, 'ritual');
    aiInterpretation.value = response.data.interpretation;
    aiSummary.value = response.data.summary || '';
    aiAdvice.value = response.data.advice || '';
    aiTone.value = response.data.tone || '';
    saveJournalEntry({
      mode: 'ritual',
      question: question.value,
      spreadName: selectedSpread.value?.name,
      spreadNameCn: selectedSpread.value?.name_cn,
      cards: snapshotCards(drawnCards.value, selectedSpread.value),
      interpretation: aiInterpretation.value,
      summary: aiSummary.value,
      advice: aiAdvice.value,
      tone: aiTone.value,
    });
  } catch (e) {
    console.error('Oracle silent', e);
    aiInterpretation.value = 'The oracle is silent today.';
    aiSummary.value = '神谕暂时无法显示，请稍后再试。';
  } finally {
    loadingAI.value = false;
  }
}

function reset() {
  step.value = 'spread';
  question.value = '';
  selectedSpread.value = null;
  shuffledDeck.value = [];
  drawnCards.value = [];
  pickedIndices.value = new Set();
  aiInterpretation.value = '';
  aiSummary.value = '';
  aiAdvice.value = '';
  aiTone.value = '';
  cardsRevealed.value = false;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text || '';
  return div.innerHTML;
}

async function exportAsImage() {
  const exportDiv = document.createElement('div');
  exportDiv.id = 'tarot-export-container';
  exportDiv.style.cssText = 'position:fixed;top:0;left:-9999px;width:700px;background:#0a0a12;padding:40px;color:white;z-index:99999;font-family:"Noto Serif SC",serif;';
  const now = new Date();
  const dateStr = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
  exportDiv.innerHTML = `
    <div style="text-align:center;margin-bottom:24px;">
      <h1 style="color:#ffd700;font-size:26px;">Tarot Sanctum</h1>
      <p style="color:#888;font-size:13px;">${dateStr}</p>
    </div>
    <p style="color:#e5e7eb;margin-bottom:16px;">问题：${escapeHtml(question.value)}</p>
    <p style="color:#a855f7;margin-bottom:16px;">牌阵：${escapeHtml(selectedSpread.value?.name_cn || '')}</p>
    <div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-bottom:20px;">
      ${drawnCards.value.map((rc, i) => `
        <div style="width:110px;text-align:center;">
          <div style="color:#888;font-size:11px;min-height:28px;">${escapeHtml(positionLabel(selectedSpread.value, i))}${rc.reversed ? ' · 逆位' : ''}</div>
          <img src="${window.location.origin}/cards/${rc.card.img}" style="width:100px;height:150px;object-fit:cover;border:2px solid #ffd700;border-radius:8px;" crossorigin="anonymous" />
          <div style="color:#ffd700;font-size:12px;margin-top:6px;">${escapeHtml(rc.card.name_cn || rc.card.name)}</div>
        </div>`).join('')}
    </div>
    <p style="color:#d1d5db;font-size:14px;line-height:1.8;white-space:pre-line;">${escapeHtml(aiInterpretation.value)}</p>
    <p style="color:#fff;margin-top:16px;line-height:1.8;">${escapeHtml(aiSummary.value)}</p>
    <p style="color:#fde68a;margin-top:12px;">${escapeHtml(aiAdvice.value)}</p>
  `;
  document.body.appendChild(exportDiv);
  try {
    await Promise.all([...exportDiv.querySelectorAll('img')].map((img) => new Promise((resolve) => {
      if (img.complete) resolve();
      else { img.onload = resolve; img.onerror = resolve; }
    })));
    await new Promise((r) => setTimeout(r, 400));
    const canvas = await html2canvas(exportDiv, { backgroundColor: '#0a0a12', scale: 2, useCORS: true, width: 700, windowWidth: 700 });
    await new Promise((resolve, reject) => {
      canvas.toBlob((blob) => (blob ? (FileSaver.saveAs(blob, `tarot-reading-${now.getTime()}.png`), resolve()) : reject()), 'image/png');
    });
  } catch (e) {
    console.error(e);
    alert('导出失败，请重试');
  } finally {
    exportDiv.remove();
  }
}

function exportAsText() {
  const now = new Date();
  const cardList = drawnCards.value.map((rc, i) =>
    `  ${positionLabel(selectedSpread.value, i)}: ${rc.card.name_cn || rc.card.name}${rc.reversed ? '（逆位）' : ''}`
  ).join('\n');
  const content = `TAROT SANCTUM / 塔罗占卜\n${now.toLocaleString('zh-CN')}\n\n问题：${question.value}\n牌阵：${selectedSpread.value?.name_cn || ''}\n${cardList}\n\n${aiInterpretation.value}\n\n总结：${aiSummary.value}\n建议：${aiAdvice.value}\n`;
  FileSaver.saveAs(new Blob([content], { type: 'text/plain;charset=utf-8' }), `tarot-reading-${now.getTime()}.txt`);
}
</script>

<style scoped>
.glow-text { text-shadow: 0 0 10px rgba(255, 215, 0, 0.5), 0 0 20px rgba(255, 215, 0, 0.3); }
.smooth-enter-active { transition: all 0.4s ease-out; }
.smooth-leave-active { transition: all 0.3s ease-in; }
.smooth-enter-from { opacity: 0; transform: translateY(20px); }
.smooth-leave-to { opacity: 0; transform: translateY(-10px); }
.vignette-overlay {
  background: radial-gradient(ellipse at center, transparent 30%, rgba(13, 13, 31, 0.6) 70%, rgba(13, 13, 31, 0.95) 100%);
}
.card-slide-in { animation: slideIn 0.5s ease-out forwards; }
@keyframes slideIn {
  from { opacity: 0; transform: translateY(30px) scale(0.9); }
  to { opacity: 1; }
}
.card-fly-out { animation: flyOut 0.5s ease-out forwards; pointer-events: none; }
@keyframes flyOut {
  0% { opacity: 1; transform: translateY(0) scale(1); }
  50% { opacity: 0.8; transform: translateY(-100px) scale(1.2); }
  100% { opacity: 0; transform: translateY(-200px) scale(0.5); }
}
.selected-card-enter-active { animation: cardAppear 0.4s ease-out; }
.selected-card-leave-active { animation: cardDisappear 0.3s ease-in; }
@keyframes cardAppear {
  0% { opacity: 0; transform: translateY(-50px) scale(0.5); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes cardDisappear {
  to { opacity: 0; transform: translateY(50px) scale(0.5); }
}
.deck-card:hover { filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.6)); }
.shuffle-container { perspective: 1000px; }
.shuffle-card {
  animation: shuffleCard 2.4s ease-in-out infinite;
  animation-delay: var(--delay, 0s);
  transform-origin: center bottom;
}
@keyframes shuffleCard {
  0%, 100% { transform: translateX(var(--offset, 0)) translateY(0) rotateY(0deg); }
  25% { transform: translateX(calc(var(--offset, 0) + 46px)) translateY(-28px) rotateY(18deg) rotateZ(6deg); }
  50% { transform: translateX(var(--offset, 0)) translateY(-70px) scale(1.06); }
  75% { transform: translateX(calc(var(--offset, 0) - 36px)) translateY(-24px) rotateY(-14deg); }
}
.shuffle-dot {
  width: 6px; height: 6px; background: currentColor; border-radius: 50%;
  animation: dotPulse 0.6s ease-in-out infinite alternate;
}
@keyframes dotPulse {
  from { opacity: 0.3; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1.2); }
}
</style>
