<template>
  <TarotShell
    :show-hud="true"
    oracle-pose="sit"
    oracle-line="七十八张脸。点开一张，看它的光和影。"
  >
    <div class="max-w-6xl mx-auto px-4 pb-16">
      <div class="text-center mb-8">
        <p class="text-[10px] tracking-[0.45em] uppercase text-mystic-purple mb-2">Codex</p>
        <h2 class="text-3xl tracking-widest uppercase glow-text mb-2">星图典藏</h2>
        <p class="text-gray-400 text-sm font-chinese-body">七十八张牌。点开一张，看它的光与影。</p>
      </div>

      <div class="flex flex-col sm:flex-row gap-3 items-center justify-center mb-8">
        <input
          v-model="query"
          type="search"
          placeholder="搜索牌名 / 关键词"
          class="w-full sm:w-72 bg-black/40 border border-gray-700 rounded-full px-4 py-2 text-sm text-gray-200 focus:border-mystic-gold focus:outline-none font-chinese-body"
        />
        <div class="flex flex-wrap justify-center gap-2">
          <button
            v-for="chip in chips"
            :key="chip.value"
            type="button"
            class="px-3 py-1 rounded-full text-xs border transition-colors"
            :class="filter === chip.value ? 'border-mystic-gold text-mystic-gold bg-mystic-gold/10' : 'border-gray-700 text-gray-400 hover:border-mystic-gold/50'"
            @click="filter = chip.value"
          >
            {{ chip.label }}
          </button>
        </div>
      </div>

      <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3">
        <button
          v-for="card in filtered"
          :key="card.id"
          type="button"
          class="group text-left bg-transparent border-0 p-0"
          @click="selected = card"
        >
          <div class="rounded-lg overflow-hidden border border-gray-800 group-hover:border-mystic-gold transition-all group-hover:-translate-y-1 group-hover:shadow-[0_0_18px_rgba(255,215,0,0.25)]">
            <img :src="`/cards/${card.img}`" :alt="card.name" class="w-full aspect-[2/3] object-cover" />
          </div>
          <p class="mt-1 text-[11px] text-center text-gray-400 group-hover:text-mystic-gold font-chinese-body truncate">
            {{ card.name_cn || card.name }}
          </p>
        </button>
      </div>
    </div>

    <div v-if="selected" class="fixed inset-0 z-40 flex items-center justify-center p-4" @click.self="selected = null">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="selected = null"></div>
      <div class="relative z-10 max-w-3xl w-full bg-[#0d0d1a] border border-mystic-gold/30 rounded-2xl p-5 sm:p-8 grid sm:grid-cols-[180px_1fr] gap-6">
        <img :src="`/cards/${selected.img}`" :alt="selected.name" class="w-40 sm:w-full mx-auto rounded-xl border-2 border-mystic-gold shadow-2xl" />
        <div class="text-left">
          <p class="text-[10px] tracking-[0.3em] uppercase text-mystic-purple">
            {{ selected.arcana }} · {{ selected.suit !== 'None' ? selected.suit : 'Major' }} · {{ selected.element }}
          </p>
          <h3 class="text-2xl text-mystic-gold font-chinese-title mt-1">{{ selected.name_cn }}</h3>
          <p class="text-sm text-gray-500 tracking-widest uppercase mb-3">{{ selected.name }}</p>
          <div class="flex flex-wrap gap-1 mb-4">
            <span v-for="kw in selected.keywords" :key="kw" class="px-2 py-0.5 text-xs rounded bg-mystic-purple/20 text-mystic-purple">{{ kw }}</span>
          </div>
          <div class="space-y-3 font-chinese-body text-sm leading-relaxed">
            <div>
              <p class="text-mystic-gold text-xs tracking-widest uppercase mb-1">正位</p>
              <p class="text-gray-300">{{ (selected.meanings_light || []).join(' · ') }}</p>
            </div>
            <div>
              <p class="text-rose-300 text-xs tracking-widest uppercase mb-1">逆位</p>
              <p class="text-gray-400">{{ (selected.meanings_shadow || []).join(' · ') }}</p>
            </div>
          </div>
          <button type="button" class="mt-6 text-xs text-gray-500 hover:text-mystic-gold" @click="selected = null">关闭</button>
        </div>
      </div>
    </div>
  </TarotShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import api from '../../api/tarot';
import TarotShell from '../../components/tarot/TarotShell.vue';

const cards = ref([]);
const query = ref('');
const filter = ref('all');
const selected = ref(null);

const chips = [
  { value: 'all', label: '全部' },
  { value: 'Major', label: '大阿卡纳' },
  { value: 'Wands', label: '权杖' },
  { value: 'Cups', label: '圣杯' },
  { value: 'Swords', label: '宝剑' },
  { value: 'Pentacles', label: '星币' },
];

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  return cards.value.filter((card) => {
    const byFilter = filter.value === 'all'
      || card.arcana === filter.value
      || card.suit === filter.value;
    if (!byFilter) return false;
    if (!q) return true;
    const blob = [card.name, card.name_cn, ...(card.keywords || [])].join(' ').toLowerCase();
    return blob.includes(q);
  });
});

onMounted(async () => {
  try {
    const res = await api.getCards();
    cards.value = res.data;
  } catch (e) {
    console.error(e);
  }
});
</script>

<style scoped>
.glow-text { text-shadow: 0 0 12px rgba(255, 215, 0, 0.45); }
</style>
