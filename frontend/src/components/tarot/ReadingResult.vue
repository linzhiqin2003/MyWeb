<template>
  <div class="max-w-2xl mx-auto text-center bg-black/55 p-6 sm:p-8 rounded-2xl border border-gray-800 animate-fade-in-up backdrop-blur-sm">
    <div v-if="verdictMeta" class="mb-6">
      <div class="verdict-seal mx-auto" :class="verdictMeta.cls">
        {{ verdictMeta.label }}
      </div>
      <p class="text-xs tracking-[0.3em] uppercase text-gray-500 mt-2">{{ verdictMeta.sub }}</p>
    </div>

    <h3 class="text-xl text-mystic-gold mb-4 tracking-widest uppercase">Interpretation</h3>

    <div v-if="loading" class="text-mystic-purple animate-pulse mb-4 tracking-widest text-sm">
      神谕正在穿过迷雾…
    </div>
    <template v-else>
      <p class="text-gray-300 leading-relaxed mb-6 whitespace-pre-line text-sm">{{ interpretation }}</p>

      <div v-if="summary" class="mt-4 pt-5 border-t border-mystic-gold/30">
        <h4 class="text-lg text-mystic-gold mb-3 font-chinese-title">✦ 简明总结</h4>
        <p class="text-white leading-loose text-base bg-gradient-to-r from-mystic-purple/20 via-mystic-gold/10 to-mystic-purple/20 p-5 rounded-lg font-chinese-body">
          {{ summary }}
        </p>
      </div>

      <div v-if="advice" class="mt-5 text-left bg-black/30 border border-mystic-gold/20 rounded-xl p-4">
        <h4 class="text-mystic-gold text-sm tracking-widest uppercase mb-2">行动建议</h4>
        <p class="text-gray-200 font-chinese-body leading-relaxed">{{ advice }}</p>
      </div>

      <p v-if="toneMeta" class="mt-4 text-xs tracking-[0.25em] uppercase" :style="{ color: toneMeta.color }">
        能量 · {{ toneMeta.label }}
      </p>
    </template>

    <button
      v-if="drawnCards?.length"
      type="button"
      class="text-xs text-gray-500 hover:text-mystic-gold transition-colors flex items-center gap-2 mx-auto mt-6"
      @click="open = !open"
    >
      <span>{{ open ? '▼' : '▶' }}</span>
      <span>{{ open ? '收起' : '展开' }}牌意细读</span>
    </button>

    <div v-if="open" class="mt-4 text-left space-y-3 max-h-80 overflow-y-auto border-t border-gray-700 pt-4">
      <div v-for="(item, index) in drawnCards" :key="index" class="text-sm bg-black/30 p-3 rounded-lg">
        <div class="flex items-center gap-2 mb-2 flex-wrap">
          <strong class="text-mystic-purple">{{ positionLabel(spread, index) }}</strong>
          <span class="text-mystic-gold">{{ item.card.name_cn || item.card.name }}</span>
          <span v-if="item.reversed" class="text-[10px] text-rose-300 border border-rose-300/40 px-1.5 rounded">逆位</span>
        </div>
        <div v-if="item.card.keywords?.length" class="flex flex-wrap gap-1 mb-2">
          <span
            v-for="(kw, ki) in item.card.keywords"
            :key="ki"
            class="px-2 py-0.5 bg-mystic-purple/20 text-mystic-purple text-xs rounded"
          >{{ kw }}</span>
        </div>
        <p class="text-gray-400 text-xs leading-relaxed font-chinese-body">
          {{ item.reversed
            ? (item.card.meanings_shadow || []).join(' · ')
            : (item.card.meanings_light || item.card.fortune_telling || []).join(' · ') }}
        </p>
      </div>
    </div>

    <div v-if="!loading && interpretation" class="mt-8 pt-4 border-t border-gray-800 flex items-center justify-center gap-6 text-sm">
      <button type="button" class="text-gray-500 hover:text-mystic-gold transition-colors font-chinese-body" @click="$emit('save-image')">
        📷 保存图片
      </button>
      <span class="text-gray-700">|</span>
      <button type="button" class="text-gray-500 hover:text-mystic-gold transition-colors font-chinese-body" @click="$emit('save-text')">
        📄 保存文本
      </button>
    </div>

    <button
      type="button"
      class="mt-6 text-sm text-gray-500 hover:text-white underline decoration-mystic-purple font-chinese-body"
      @click="$emit('again')"
    >
      {{ againLabel }}
    </button>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { positionLabel, TONE_META, VERDICT_META } from '../../composables/useTarotDeck';

const props = defineProps({
  loading: Boolean,
  interpretation: String,
  summary: String,
  advice: String,
  tone: String,
  verdict: String,
  spread: Object,
  drawnCards: { type: Array, default: () => [] },
  againLabel: { type: String, default: '再问一次' },
});

defineEmits(['again', 'save-image', 'save-text']);

const open = ref(false);
const toneMeta = computed(() => TONE_META[props.tone] || null);
const verdictMeta = computed(() => VERDICT_META[props.verdict] || null);
</script>

<style scoped>
.animate-fade-in-up { animation: fadeInUp 0.6s ease-out forwards; }
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.verdict-seal {
  width: 7.5rem;
  height: 7.5rem;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  letter-spacing: 0.2em;
  border: 2px solid currentColor;
  animation: sealIn 0.8s cubic-bezier(0.2, 0.9, 0.2, 1);
}
.verdict-yes { color: #fbbf24; box-shadow: 0 0 28px rgba(251, 191, 36, 0.35); }
.verdict-lean-yes { color: #fde68a; box-shadow: 0 0 20px rgba(253, 230, 138, 0.25); }
.verdict-unclear { color: #c4b5fd; box-shadow: 0 0 20px rgba(196, 181, 253, 0.25); }
.verdict-lean-no { color: #fda4af; box-shadow: 0 0 20px rgba(253, 164, 175, 0.25); }
.verdict-no { color: #fb7185; box-shadow: 0 0 28px rgba(251, 113, 133, 0.3); }
@keyframes sealIn {
  from { transform: scale(0.4) rotate(-12deg); opacity: 0; }
  to { transform: scale(1) rotate(0); opacity: 1; }
}
</style>
