<template>
  <div class="oracle-hud" @click="skipType">
    <ol v-if="quest.length" class="quest-row" aria-label="仪式进度">
      <li
        v-for="(label, index) in quest"
        :key="label"
        class="quest-pip"
        :class="{ done: index < questIndex, now: index === questIndex }"
      >
        <span class="pip-num">{{ index + 1 }}</span>
        <span class="pip-label">{{ label }}</span>
      </li>
    </ol>

    <div class="dialogue" :class="{ 'no-sprite': hideSprite }">
      <OracleSprite v-if="!hideSprite" :pose="pose" :size="size" :sparkle="sparkle" />
      <div class="box">
        <div class="nameplate">占卜师</div>
        <p class="line font-chinese-body">{{ shown }}<span v-if="typing" class="caret">▌</span></p>
        <span v-if="!typing" class="next-tri">▼</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onUnmounted, ref, watch } from 'vue';
import OracleSprite from './OracleSprite.vue';

const props = defineProps({
  pose: { type: String, default: 'idle' },
  line: { type: String, default: '' },
  quest: { type: Array, default: () => [] },
  questIndex: { type: Number, default: 0 },
  size: { type: String, default: 'md' },
  sparkle: { type: Boolean, default: false },
  hideSprite: { type: Boolean, default: false },
});

const shown = ref('');
const typing = ref(false);
let timer = null;

function clearTimer() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

function typeLine(text) {
  clearTimer();
  shown.value = '';
  const full = text || '';
  if (!full) {
    typing.value = false;
    return;
  }
  typing.value = true;
  let i = 0;
  timer = setInterval(() => {
    i += 1;
    shown.value = full.slice(0, i);
    if (i >= full.length) {
      typing.value = false;
      clearTimer();
    }
  }, 28);
}

function skipType() {
  if (!typing.value) return;
  clearTimer();
  shown.value = props.line || '';
  typing.value = false;
}

watch(() => props.line, (value) => typeLine(value), { immediate: true });

onUnmounted(clearTimer);
</script>

<style scoped>
.oracle-hud {
  width: 100%;
  max-width: 820px;
  margin: 0 auto;
  padding: 0 12px;
}
.quest-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  margin-bottom: 10px;
  list-style: none;
  padding: 0;
}
.quest-pip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border: 1px solid #333;
  color: #6b7280;
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-family: 'Press Start 2P', monospace;
}
.quest-pip.done { border-color: #a855f7; color: #c4b5fd; }
.quest-pip.now {
  border-color: #ffd700;
  color: #ffd700;
  box-shadow: 0 0 12px rgba(255, 215, 0, 0.25);
}
.pip-num { opacity: 0.7; }
.dialogue {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: rgba(6, 6, 14, 0.82);
  border: 2px solid #ffd700;
  box-shadow: 0 0 0 2px #1a1028, 0 12px 40px rgba(0, 0, 0, 0.45);
  padding: 8px 12px 10px;
}
.dialogue.no-sprite { padding-left: 16px; }
.box {
  position: relative;
  flex: 1;
  min-height: 72px;
  text-align: left;
  padding: 6px 8px 14px 4px;
}
.nameplate {
  display: inline-block;
  margin-bottom: 8px;
  padding: 3px 8px;
  background: #ffd700;
  color: #111;
  font-family: 'Press Start 2P', monospace;
  font-size: 9px;
  letter-spacing: 0.12em;
}
.line {
  color: #e5e7eb;
  font-size: 15px;
  line-height: 1.7;
  min-height: 2.6em;
}
.caret {
  color: #ffd700;
  animation: blink 0.8s steps(1) infinite;
}
.next-tri {
  position: absolute;
  right: 8px;
  bottom: 4px;
  color: #ffd700;
  font-size: 10px;
  animation: bounce 0.9s ease-in-out infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(3px); }
}
@media (max-width: 640px) {
  .pip-label { display: none; }
  .line { font-size: 14px; }
}
</style>
