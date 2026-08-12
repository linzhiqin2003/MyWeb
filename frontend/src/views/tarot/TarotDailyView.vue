<template>
  <TarotShell
    :show-candle="true"
    :show-hud="true"
    :oracle-pose="oraclePose"
    :oracle-line="oracleLine"
    :oracle-sparkle="loading || !revealed"
  >
    <div class="max-w-3xl mx-auto px-4 pb-16 flex flex-col items-center text-center">
      <p class="text-[10px] tracking-[0.45em] uppercase text-mystic-purple mb-2">Daily Oracle</p>
      <h2 class="text-3xl sm:text-4xl tracking-widest uppercase glow-text mb-2">今日神谕</h2>
      <p class="text-gray-400 text-sm mb-10 font-chinese-body">{{ dateLabel }} · 同一天只会见这一张脸</p>

      <div v-if="error" class="text-rose-300 font-chinese-body">{{ error }}</div>
      <div v-else-if="!daily" class="text-mystic-purple animate-pulse tracking-widest text-sm">正在请出今日之牌…</div>
      <template v-else>
        <p class="text-xs tracking-[0.3em] uppercase text-gray-500 mb-3">
          {{ daily.reversed ? 'Reversed · 逆位' : 'Upright · 正位' }}
        </p>
        <TarotCard
          :card="daily.card"
          :revealed="revealed"
          :reversed="daily.reversed"
          size="xl"
          @click="onReveal"
        />
        <h3 class="mt-6 text-2xl text-mystic-gold font-chinese-title">
          {{ daily.card.name_cn }}
          <span class="text-sm text-gray-500 ml-2 tracking-widest uppercase">{{ daily.card.name }}</span>
        </h3>
        <div class="flex flex-wrap justify-center gap-2 mt-3">
          <span v-for="kw in daily.keywords" :key="kw" class="px-2 py-0.5 text-xs rounded bg-mystic-purple/20 text-mystic-purple">{{ kw }}</span>
        </div>
        <p class="mt-5 max-w-lg text-gray-300 font-chinese-body leading-relaxed">{{ daily.meaning }}</p>

        <button
          v-if="revealed && !interpretation"
          type="button"
          :disabled="loading"
          class="mt-8 px-8 py-3 border border-mystic-gold hover:bg-mystic-gold hover:text-black transition-all tracking-widest uppercase disabled:opacity-50"
          @click="askOracle"
        >
          {{ loading ? '神谕降临中…' : '请神谕解读今日' }}
        </button>

        <ReadingResult
          v-if="interpretation || loading"
          class="mt-10 w-full"
          :loading="loading"
          :interpretation="interpretation"
          :summary="summary"
          :advice="advice"
          :tone="tone"
          :spread="spreadStub"
          :drawn-cards="drawnStub"
          again-label="回到圣所"
          @again="$router.push('/tarot')"
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
import { saveJournalEntry } from '../../composables/useTarotJournal';

const daily = ref(null);
const revealed = ref(false);
const loading = ref(false);
const error = ref('');
const interpretation = ref('');
const summary = ref('');
const advice = ref('');
const tone = ref('');

const oraclePose = computed(() => {
  if (error.value) return 'think';
  if (!daily.value) return 'meditate';
  if (loading.value) return 'divine';
  if (interpretation.value) return 'celebrate';
  if (revealed.value) return 'look';
  return 'draw';
});

const oracleLine = computed(() => {
  if (error.value) return '今日的牌还没到。晚点再来找我。';
  if (!daily.value) return '我去把今天那张请出来……';
  if (loading.value) return '今天这张牌话有点密。等我听完。';
  if (interpretation.value) return '同一天不会换脸。明天再来，才是下一张。';
  if (revealed.value) return `${daily.value.card.name_cn}。要不要让我把今日的话翻译给你听？`;
  return '今天只给一张。点它，让它翻过来。';
});

const dateLabel = computed(() => {
  const iso = daily.value?.date;
  const d = iso ? new Date(`${iso}T00:00:00`) : new Date();
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });
});

const spreadStub = computed(() => ({
  positions: ['The Message'],
  positions_cn: ['今日'],
}));

const drawnStub = computed(() => {
  if (!daily.value) return [];
  return [{ card: daily.value.card, reversed: daily.value.reversed, revealed: true }];
});

onMounted(async () => {
  try {
    const res = await api.getDaily();
    daily.value = res.data;
  } catch (e) {
    console.error(e);
    error.value = '今日神谕尚未就绪。';
  }
});

function onReveal() {
  revealed.value = true;
}

async function askOracle() {
  if (!daily.value) return;
  loading.value = true;
  try {
    const card = daily.value.card;
    const res = await api.divine(
      `今日指引 · ${daily.value.date}`,
      [{
        name: card.name,
        name_cn: card.name_cn,
        position: 'The Message',
        position_cn: '今日',
        reversed: daily.value.reversed,
        keywords: card.keywords,
        meaning: daily.value.meaning,
      }],
      'single_card',
      'daily',
    );
    interpretation.value = res.data.interpretation;
    summary.value = res.data.summary || '';
    advice.value = res.data.advice || '';
    tone.value = res.data.tone || '';
    saveJournalEntry({
      mode: 'daily',
      question: `今日指引 · ${daily.value.date}`,
      spreadName: 'single_card',
      spreadNameCn: '今日神谕',
      cards: [{
        name: card.name,
        name_cn: card.name_cn,
        img: card.img,
        reversed: daily.value.reversed,
        position: 'The Message',
        position_cn: '今日',
      }],
      interpretation: interpretation.value,
      summary: summary.value,
      advice: advice.value,
      tone: tone.value,
    });
  } catch (e) {
    console.error(e);
    interpretation.value = 'The oracle is silent today.';
    summary.value = '神谕暂时无法显示，请稍后再试。';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.glow-text { text-shadow: 0 0 12px rgba(255, 215, 0, 0.45); }
</style>
