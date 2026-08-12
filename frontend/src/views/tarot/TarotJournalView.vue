<template>
  <TarotShell>
    <div class="max-w-3xl mx-auto px-4 pb-16">
      <div class="text-center mb-8">
        <p class="text-[10px] tracking-[0.45em] uppercase text-mystic-purple mb-2">Journal</p>
        <h2 class="text-3xl tracking-widest uppercase glow-text mb-2">占卜手记</h2>
        <p class="text-gray-400 text-sm font-chinese-body">只存在于这台设备上。把问过的话留下来。</p>
      </div>

      <div v-if="!entries.length" class="text-center text-gray-500 font-chinese-body py-16">
        还没有留下任何一次询问。
        <router-link to="/tarot/ritual" class="block mt-4 text-mystic-gold hover:underline">去举行一次仪式</router-link>
      </div>

      <div v-else class="space-y-4">
        <div class="flex justify-end">
          <button type="button" class="text-xs text-gray-500 hover:text-rose-300" @click="wipe">清空手记</button>
        </div>
        <article
          v-for="entry in entries"
          :key="entry.id"
          class="border border-gray-800 bg-black/40 rounded-2xl p-5 hover:border-mystic-gold/40 transition-colors"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-[10px] tracking-[0.3em] uppercase text-mystic-purple">{{ modeLabel(entry.mode) }} · {{ entry.spreadNameCn || entry.spreadName }}</p>
              <h3 class="text-mystic-gold font-chinese-title mt-1">{{ entry.question }}</h3>
              <p class="text-xs text-gray-500 mt-1">{{ formatDate(entry.createdAt) }}</p>
            </div>
            <button type="button" class="text-gray-600 hover:text-rose-300 text-sm" @click="remove(entry.id)">✕</button>
          </div>
          <div class="flex flex-wrap gap-2 mt-3">
            <span
              v-for="(card, i) in entry.cards"
              :key="i"
              class="text-[11px] px-2 py-1 rounded bg-gray-800 text-gray-300"
            >
              {{ card.position_cn || card.position }} · {{ card.name_cn || card.name }}{{ card.reversed ? ' 逆' : '' }}
            </span>
          </div>
          <p v-if="entry.verdict" class="mt-3 text-sm text-mystic-gold">倾向：{{ verdictLabel(entry.verdict) }}</p>
          <p v-if="entry.summary" class="mt-3 text-sm text-gray-300 font-chinese-body leading-relaxed">{{ entry.summary }}</p>
          <p v-if="entry.advice" class="mt-2 text-sm text-amber-100/80 font-chinese-body">{{ entry.advice }}</p>
        </article>
      </div>
    </div>
  </TarotShell>
</template>

<script setup>
import { ref } from 'vue';
import TarotShell from '../../components/tarot/TarotShell.vue';
import { clearJournal, loadJournal, removeJournalEntry } from '../../composables/useTarotJournal';
import { VERDICT_META } from '../../composables/useTarotDeck';

const entries = ref(loadJournal());

function refresh() {
  entries.value = loadJournal();
}

function remove(id) {
  removeJournalEntry(id);
  refresh();
}

function wipe() {
  if (!confirm('清空全部手记？')) return;
  clearJournal();
  refresh();
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('zh-CN');
  } catch {
    return iso;
  }
}

function modeLabel(mode) {
  return { ritual: '仪式', daily: '今日', yesno: '是非' }[mode] || mode;
}

function verdictLabel(verdict) {
  return VERDICT_META[verdict]?.label || verdict;
}
</script>

<style scoped>
.glow-text { text-shadow: 0 0 12px rgba(255, 215, 0, 0.45); }
</style>
