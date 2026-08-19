<template>
  <div class="w-full max-w-6xl px-4 space-y-10">
    <section v-for="group in grouped" :key="group.key">
      <div class="flex items-center gap-3 mb-4">
        <span class="text-mystic-gold/80 tracking-[0.35em] uppercase text-xs">{{ group.label }}</span>
        <span class="flex-1 h-px bg-gradient-to-r from-mystic-gold/40 to-transparent"></span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <button
          v-for="spread in group.items"
          :key="spread.id || spread.name"
          type="button"
          class="relative text-left group cursor-pointer bg-black/40 border border-gray-800 rounded-2xl p-6 pl-10 hover:border-mystic-gold transition-all duration-300 hover:shadow-xl hover:shadow-mystic-gold/20 hover:-translate-y-1 overflow-hidden"
          @click="$emit('select', spread)"
        >
          <span class="rpg-cursor">▶</span>
          <div class="absolute -top-3 -right-3 bg-mystic-gold text-black text-xs font-bold px-3 py-1.5 rounded-full shadow-lg z-20">
            {{ spread.card_count }} 牌
          </div>
          <div class="relative z-10">
            <p class="text-[10px] tracking-[0.3em] uppercase text-mystic-purple mb-2">
              {{ difficultyLabel(spread.difficulty) }}
            </p>
            <h3 class="text-xl text-mystic-gold mb-2 font-chinese-title">{{ spread.name_cn }}</h3>
            <p class="text-sm text-gray-400 mb-4 line-clamp-2 font-chinese-body">
              {{ spread.blurb || spread.description_cn || spread.description }}
            </p>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="(pos, idx) in (spread.positions_cn || spread.positions).slice(0, 4)"
                :key="idx"
                class="text-[10px] bg-gray-800/80 text-gray-300 px-2 py-1 rounded"
              >
                {{ pos }}
              </span>
              <span v-if="(spread.positions_cn || spread.positions).length > 4" class="text-[10px] text-gray-500">
                +{{ (spread.positions_cn || spread.positions).length - 4 }}
              </span>
            </div>
          </div>
          <div class="absolute inset-0 rounded-2xl bg-gradient-to-br from-mystic-gold/0 to-mystic-purple/0 group-hover:from-mystic-gold/5 group-hover:to-mystic-purple/15 transition-all duration-300 pointer-events-none"></div>
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { CATEGORY_META, DIFFICULTY_META } from '../../composables/useTarotDeck';

const props = defineProps({
  spreads: { type: Array, required: true },
});

defineEmits(['select']);

const ORDER = ['glance', 'classic', 'depth', 'relation', 'decision', 'inner', 'timing'];

const grouped = computed(() => {
  const map = {};
  for (const spread of props.spreads || []) {
    const key = spread.category || 'classic';
    if (!map[key]) map[key] = [];
    map[key].push(spread);
  }
  return ORDER.filter((key) => map[key]?.length).map((key) => ({
    key,
    label: CATEGORY_META[key] || key,
    items: map[key],
  }));
});

function difficultyLabel(value) {
  return DIFFICULTY_META[value] || '';
}
</script>

<style scoped>
.rpg-cursor {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: transparent;
  font-size: 12px;
  z-index: 20;
}
.group:hover .rpg-cursor {
  color: #ffd700;
  animation: nudge 0.6s ease-in-out infinite;
}
@keyframes nudge {
  0%, 100% { transform: translateY(-50%) translateX(0); }
  50% { transform: translateY(-50%) translateX(4px); }
}
</style>
