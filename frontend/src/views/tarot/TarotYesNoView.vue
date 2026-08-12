<template>
  <TarotShell
    :show-candle="true"
    :show-sigil="true"
    :show-hud="true"
    :oracle-pose="oraclePose"
    :oracle-line="oracleLine"
    :oracle-sparkle="step === 'shuffle' || loading"
    :quest="['提问', '抽牌', '神谕']"
    :quest-index="questIndex"
  >
    <div class="max-w-3xl mx-auto px-4 pb-16 flex flex-col items-center text-center">
      <p class="text-[10px] tracking-[0.45em] uppercase text-mystic-purple mb-2">Yes / No</p>
      <h2 class="text-3xl sm:text-4xl tracking-widest uppercase glow-text mb-2">是非一问</h2>
      <p class="text-gray-400 text-sm mb-10 font-chinese-body">只问一件事。牌会倾斜，但很少替你承担选择。</p>

      <div v-if="step === 'ask'" class="w-full max-w-xl">
        <input
          v-model="question"
          type="text"
          placeholder="是，还是不是？"
          class="w-full bg-transparent border-b-2 border-mystic-gold p-4 text-xl sm:text-2xl focus:outline-none text-center placeholder-gray-600 font-chinese-body"
          @keydown.enter="draw"
        />
        <button
          type="button"
          :disabled="!question.trim() || !deck.length"
          class="mt-10 px-10 py-3 border border-mystic-gold hover:bg-mystic-gold hover:text-black transition-all tracking-widest uppercase disabled:opacity-50"
          @click="draw"
        >
          求问
        </button>
      </div>

      <div v-else-if="step === 'shuffle'" class="h-72 flex flex-col items-center justify-center gap-3">
        <OracleSprite pose="shuffle" size="lg" :sparkle="true" />
        <div class="w-28 h-40 rounded-xl overflow-hidden border border-mystic-gold shuffle-pulse">
          <img src="/mystic/tarot-card-back.jpg" alt="" class="w-full h-full object-cover" />
        </div>
      </div>

      <template v-else>
        <TarotCard
          :card="drawn.card"
          :revealed="revealed"
          :reversed="drawn.reversed"
          size="xl"
          @click="reveal"
        />
        <p class="mt-4 text-mystic-gold font-chinese-title text-xl">
          {{ drawn.card.name_cn }}
          <span v-if="drawn.reversed" class="text-rose-300 text-sm ml-2">逆位</span>
        </p>
        <ReadingResult
          v-if="revealed"
          class="mt-10 w-full"
          :loading="loading"
          :interpretation="interpretation"
          :summary="summary"
          :advice="advice"
          :tone="tone"
          :verdict="verdict"
          :spread="spreadStub"
          :drawn-cards="[drawn]"
          @again="reset"
        />
      </template>
    </div>
  </TarotShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import api from '../../api/tarot';
import TarotShell from '../../components/tarot/TarotShell.vue';
import TarotCard from '../../components/tarot/TarotCard.vue';
import ReadingResult from '../../components/tarot/ReadingResult.vue';
import OracleSprite from '../../components/tarot/OracleSprite.vue';
import { rollReversed, shuffleDeck } from '../../composables/useTarotDeck';
import { saveJournalEntry } from '../../composables/useTarotJournal';

const question = ref('');
const deck = ref([]);
const step = ref('ask');
const drawn = ref(null);
const revealed = ref(false);
const loading = ref(false);
const interpretation = ref('');
const summary = ref('');
const advice = ref('');
const tone = ref('');
const verdict = ref('');
const spreadStub = { positions: ['The Answer'], positions_cn: ['答案'] };

const questIndex = computed(() => {
  if (step.value === 'ask') return 0;
  if (step.value === 'shuffle' || (step.value === 'reveal' && !revealed.value)) return 1;
  return 2;
});

const oraclePose = computed(() => {
  if (loading.value) return 'divine';
  if (step.value === 'ask') return 'think';
  if (step.value === 'shuffle') return 'shuffle';
  if (verdict.value === 'yes' || verdict.value === 'lean_yes') return 'celebrate';
  if (verdict.value === 'no' || verdict.value === 'lean_no') return 'surprise';
  if (revealed.value) return 'look';
  return 'draw';
});

const oracleLine = computed(() => {
  if (loading.value) return '是或否，牌自己会倾斜。我只负责把倾斜读出来。';
  if (step.value === 'ask') return '只问一件事。牌会给倾向，选择还是你的。';
  if (step.value === 'shuffle') return '一问一牌。别眨眼。';
  if (revealed.value && interpretation.value) return '倾向只是风向。走不走，还得你自己迈。';
  if (step.value === 'reveal') return '点开它。答案在正面，也在你听见的第一句话里。';
  return '';
});

onMounted(async () => {
  try {
    const res = await api.getCards();
    deck.value = res.data;
  } catch (e) {
    console.error(e);
  }
});

function draw() {
  if (!question.value.trim() || !deck.value.length) return;
  const shuffled = shuffleDeck(deck.value);
  drawn.value = {
    card: shuffled[0],
    reversed: rollReversed(true, 0.32),
    revealed: false,
  };
  step.value = 'shuffle';
  setTimeout(() => { step.value = 'reveal'; }, 1400);
}

function reveal() {
  if (revealed.value) return;
  revealed.value = true;
  drawn.value.revealed = true;
  ask();
}

async function ask() {
  loading.value = true;
  try {
    const card = drawn.value.card;
    const res = await api.divine(
      question.value,
      [{
        name: card.name,
        name_cn: card.name_cn,
        position: 'The Answer',
        position_cn: '答案',
        reversed: drawn.value.reversed,
        keywords: card.keywords,
        meaning: drawn.value.reversed
          ? (card.meanings_shadow || [])[0]
          : (card.meanings_light || [])[0],
      }],
      'yes_no',
      'yesno',
    );
    interpretation.value = res.data.interpretation;
    summary.value = res.data.summary || '';
    advice.value = res.data.advice || '';
    tone.value = res.data.tone || '';
    verdict.value = res.data.verdict || 'unclear';
    saveJournalEntry({
      mode: 'yesno',
      question: question.value,
      spreadName: 'yes_no',
      spreadNameCn: '是非一问',
      cards: [{
        name: card.name,
        name_cn: card.name_cn,
        img: card.img,
        reversed: drawn.value.reversed,
        position: 'The Answer',
        position_cn: '答案',
      }],
      interpretation: interpretation.value,
      summary: summary.value,
      advice: advice.value,
      tone: tone.value,
      verdict: verdict.value,
    });
  } catch (e) {
    console.error(e);
    interpretation.value = 'The oracle is silent today.';
    summary.value = '神谕暂时无法显示，请稍后再试。';
    verdict.value = 'unclear';
  } finally {
    loading.value = false;
  }
}

function reset() {
  step.value = 'ask';
  question.value = '';
  drawn.value = null;
  revealed.value = false;
  interpretation.value = '';
  summary.value = '';
  advice.value = '';
  tone.value = '';
  verdict.value = '';
}
</script>

<style scoped>
.glow-text { text-shadow: 0 0 12px rgba(255, 215, 0, 0.45); }
.shuffle-pulse { animation: pulseFlip 1.4s ease-in-out infinite; }
@keyframes pulseFlip {
  0%, 100% { transform: rotateY(0deg) scale(1); }
  50% { transform: rotateY(18deg) scale(1.04); filter: drop-shadow(0 0 18px rgba(255,215,0,0.45)); }
}
</style>
