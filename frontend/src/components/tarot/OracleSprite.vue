<template>
  <div class="oracle-sprite" :class="[sizeClass, `mode-${meta.mode}`, { sparkle: sparkle }]" :style="spriteStyle" :aria-label="pose">
    <span class="oracle-ground"></span>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import core from '../../assets/sprites/core.png';
import tarot from '../../assets/sprites/tarot.png';
import emote from '../../assets/sprites/emote.png';
import rest from '../../assets/sprites/rest.png';

const SHEETS = {
  core: { src: core, fw: 137, fh: 256, n: 3 },
  tarot: { src: tarot, fw: 130, fh: 200, n: 3 },
  emote: { src: emote, fw: 174, fh: 256, n: 3 },
  rest: { src: rest, fw: 142, fh: 256, n: 3 },
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
};

const props = defineProps({
  pose: { type: String, default: 'idle' },
  size: { type: String, default: 'md' },
  sparkle: { type: Boolean, default: false },
});

const meta = computed(() => POSES[props.pose] || POSES.idle);
const sheet = computed(() => SHEETS[meta.value.sheet]);

const sizeClass = computed(() => `size-${props.size}`);

const spriteStyle = computed(() => {
  const { fw, fh, n, src } = sheet.value;
  const frame = meta.value.frame || 0;
  return {
    '--fw': fw,
    '--fh': fh,
    '--n': n,
    '--frame': frame,
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
  mix-blend-mode: lighten;
  flex-shrink: 0;
}
.size-sm { --h: 88px; }
.size-md { --h: 120px; }
.size-lg { --h: 156px; }
.size-hero { --h: clamp(140px, 28vh, 220px); }

.oracle-ground {
  position: absolute;
  left: 50%;
  bottom: 2px;
  width: 52%;
  height: 8px;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(255, 215, 0, 0.28), transparent);
  mix-blend-mode: normal;
  pointer-events: none;
}

.mode-blink {
  animation: oracleBlink 5.2s steps(1) infinite, oracleBreathe 3.6s ease-in-out infinite;
}
.mode-wave {
  background-position: calc(-2 * var(--h) * var(--fw) / var(--fh)) 0;
  animation: oracleBreathe 3.2s ease-in-out infinite, oracleBob 2.4s ease-in-out infinite;
}
.mode-hold {
  background-position: calc(var(--frame) * -1 * var(--h) * var(--fw) / var(--fh)) 0;
  animation: oracleBreathe 3.8s ease-in-out infinite;
}
.mode-loop3 {
  animation: oracleLoop3 2.4s steps(3) infinite, oracleBreathe 3.2s ease-in-out infinite;
}

@keyframes oracleBlink {
  0%, 92% { background-position: 0 0; }
  93%, 96% { background-position: calc(-1 * var(--h) * var(--fw) / var(--fh)) 0; }
  97%, 100% { background-position: 0 0; }
}
@keyframes oracleBreathe {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.985); }
}
@keyframes oracleBob {
  0%, 100% { transform: translateY(0) scaleY(1); }
  50% { transform: translateY(-6px) scaleY(0.99); }
}
@keyframes oracleLoop3 {
  from { background-position: 0 0; }
  to { background-position: calc(-3 * var(--h) * var(--fw) / var(--fh)) 0; }
}

.sparkle::before,
.sparkle::after {
  content: '✦';
  position: absolute;
  color: #ffd700;
  font-size: 10px;
  animation: spark 1.6s ease-in-out infinite;
  pointer-events: none;
  mix-blend-mode: normal;
}
.sparkle::before { top: 8%; right: 6%; animation-delay: 0s; }
.sparkle::after { top: 22%; left: 4%; animation-delay: 0.7s; font-size: 8px; }
@keyframes spark {
  0%, 100% { opacity: 0.2; transform: scale(0.7); }
  50% { opacity: 1; transform: scale(1.15); }
}
</style>
