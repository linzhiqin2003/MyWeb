<template>
  <div
    class="oracle-sprite"
    :class="[sizeClass, `mode-${meta.mode}`, { sparkle, interactive }]"
    :style="spriteStyle"
    :aria-label="pose"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
  >
    <span class="oracle-ground"></span>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import core from '../../assets/sprites/core.png';
import tarot from '../../assets/sprites/tarot.png';
import emote from '../../assets/sprites/emote.png';
import rest from '../../assets/sprites/rest.png';
import walk from '../../assets/sprites/walk.png';
import walkBack from '../../assets/sprites/walk_back.png';

const SHEETS = {
  core: { src: core, fw: 137, fh: 256, n: 3 },
  tarot: { src: tarot, fw: 130, fh: 200, n: 3 },
  emote: { src: emote, fw: 174, fh: 256, n: 3 },
  rest: { src: rest, fw: 142, fh: 256, n: 3 },
  walk: { src: walk, fw: 147, fh: 256, n: 4 },
  walk_back: { src: walkBack, fw: 143, fh: 256, n: 4 },
};

const POSES = {
  greet: { sheet: 'core', mode: 'wave' },
  idle: { sheet: 'core', mode: 'blink' },
  think: { sheet: 'emote', mode: 'hold', frame: 0 },
  surprise: { sheet: 'emote', mode: 'hold', frame: 1 },
  celebrate: { sheet: 'emote', mode: 'hold', frame: 2 },
  look: { sheet: 'rest', mode: 'hold', frame: 0 },
  sit: { sheet: 'rest', mode: 'hold', frame: 1 },
  meditate: { sheet: 'rest', mode: 'hold', frame: 2 },
  draw: { sheet: 'tarot', mode: 'hold', frame: 0 },
  spread: { sheet: 'tarot', mode: 'hold', frame: 1 },
  divine: { sheet: 'tarot', mode: 'hold', frame: 2 },
  shuffle: { sheet: 'tarot', mode: 'loop3' },
  walk: { sheet: 'walk', mode: 'loop4' },
  walk_back: { sheet: 'walk_back', mode: 'loop4' },
};

const props = defineProps({
  pose: { type: String, default: 'idle' },
  size: { type: String, default: 'md' },
  sparkle: { type: Boolean, default: false },
  interactive: { type: Boolean, default: false },
});

const hovering = ref(false);
const meta = computed(() => {
  if (props.interactive && hovering.value && (props.pose === 'idle' || props.pose === 'greet')) {
    return POSES.greet;
  }
  return POSES[props.pose] || POSES.idle;
});
const sheet = computed(() => SHEETS[meta.value.sheet]);
const sizeClass = computed(() => `size-${props.size}`);

const spriteStyle = computed(() => {
  const { fw, fh, n, src } = sheet.value;
  return {
    '--fw': fw,
    '--fh': fh,
    '--n': n,
    '--frame': meta.value.frame || 0,
    backgroundImage: `url(${src})`,
  };
});
</script>

<style scoped>
.oracle-sprite {
  --h: 112px;
  position: relative;
  width: calc(var(--h) * var(--fw) / var(--fh));
  height: var(--h);
  background-repeat: no-repeat;
  background-size: calc(var(--h) * var(--fw) * var(--n) / var(--fh)) auto;
  image-rendering: pixelated;
  transform-origin: bottom center;
  flex-shrink: 0;
}
.size-sm { --h: 88px; }
.size-md { --h: 120px; }
.size-lg { --h: 156px; }
.size-hero { --h: clamp(148px, 32vh, 220px); }
.interactive { cursor: pointer; }

.oracle-ground {
  position: absolute;
  left: 50%;
  bottom: 0;
  width: 56px;
  height: 10px;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(168, 85, 247, 0.35), transparent);
  pointer-events: none;
}

.mode-blink {
  animation: oracleBlink 5.4s steps(1) infinite, oracleBreathe 3.8s ease-in-out infinite;
}
.mode-wave {
  background-position: calc(-2 * var(--h) * var(--fw) / var(--fh)) 0;
  animation: oracleBreathe 3.8s ease-in-out infinite;
}
.mode-hold {
  background-position: calc(var(--frame) * -1 * var(--h) * var(--fw) / var(--fh)) 0;
  animation: oracleBreathe 3.8s ease-in-out infinite;
}
.mode-loop3 {
  animation: oracleLoop3 2.7s steps(3) infinite;
}
.mode-loop4 {
  animation: oracleLoop4 0.72s steps(4) infinite;
}

@keyframes oracleBlink {
  0%, 93% { background-position: 0 0; }
  94%, 96.4% { background-position: calc(-1 * var(--h) * var(--fw) / var(--fh)) 0; }
  97%, 100% { background-position: 0 0; }
}
@keyframes oracleBreathe {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.988); }
}
@keyframes oracleLoop3 {
  from { background-position: 0 0; }
  to { background-position: calc(-3 * var(--h) * var(--fw) / var(--fh)) 0; }
}
@keyframes oracleLoop4 {
  from { background-position: 0 0; }
  to { background-position: calc(-4 * var(--h) * var(--fw) / var(--fh)) 0; }
}

.sparkle::before,
.sparkle::after {
  content: '✦';
  position: absolute;
  color: #ffd700;
  font-size: 10px;
  animation: spark 1.6s ease-in-out infinite;
  pointer-events: none;
}
.sparkle::before { top: 8%; right: 6%; }
.sparkle::after { top: 22%; left: 4%; animation-delay: 0.7s; font-size: 8px; }
@keyframes spark {
  0%, 100% { opacity: 0.2; transform: scale(0.7); }
  50% { opacity: 1; transform: scale(1.15); }
}
</style>
