<template>
  <canvas ref="canvas" class="fixed inset-0 z-0 pointer-events-none"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const canvas = ref(null);
let ctx = null;
let animationId = null;
let stars = [];
let shootingStars = [];
let dust = [];

const config = {
  starCount: 180,
  dustCount: 55,
  starMinSize: 0.4,
  starMaxSize: 2.2,
  shootingStarChance: 0.0018,
  colors: ['#ffd700', '#ffffff', '#c4b5fd', '#93c5fd', '#fde68a'],
};

class Star {
  constructor(width, height) {
    this.reset(width, height);
  }

  reset(width, height) {
    this.x = Math.random() * width;
    this.y = Math.random() * height;
    this.size = config.starMinSize + Math.random() * (config.starMaxSize - config.starMinSize);
    this.color = config.colors[Math.floor(Math.random() * config.colors.length)];
    this.alpha = Math.random();
    this.alphaDirection = Math.random() > 0.5 ? 1 : -1;
    this.speed = 0.004 + Math.random() * 0.016;
    this.flare = Math.random() > 0.88;
  }

  update() {
    this.alpha += this.alphaDirection * this.speed;
    if (this.alpha >= 1) {
      this.alpha = 1;
      this.alphaDirection = -1;
    } else if (this.alpha <= 0.15) {
      this.alpha = 0.15;
      this.alphaDirection = 1;
    }
  }

  draw(context) {
    context.globalAlpha = this.alpha;
    if (this.flare && this.alpha > 0.7) {
      context.strokeStyle = this.color;
      context.lineWidth = 0.6;
      context.beginPath();
      context.moveTo(this.x - this.size * 4, this.y);
      context.lineTo(this.x + this.size * 4, this.y);
      context.moveTo(this.x, this.y - this.size * 4);
      context.lineTo(this.x, this.y + this.size * 4);
      context.stroke();
    }
    context.beginPath();
    context.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    context.fillStyle = this.color;
    context.fill();
    context.globalAlpha = 1;
  }
}

class Dust {
  constructor(width, height) {
    this.reset(width, height, true);
  }

  reset(width, height, anywhere = false) {
    this.x = Math.random() * width;
    this.y = anywhere ? Math.random() * height : height + Math.random() * 40;
    this.size = 0.6 + Math.random() * 1.6;
    this.speedY = 0.15 + Math.random() * 0.35;
    this.drift = (Math.random() - 0.5) * 0.4;
    this.alpha = 0.15 + Math.random() * 0.35;
  }

  update(width, height) {
    this.y -= this.speedY;
    this.x += this.drift;
    if (this.y < -10 || this.x < -10 || this.x > width + 10) {
      this.reset(width, height, false);
    }
  }

  draw(context) {
    context.beginPath();
    context.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    context.fillStyle = `rgba(255, 215, 0, ${this.alpha})`;
    context.fill();
  }
}

class ShootingStar {
  constructor(width, height) {
    this.reset(width, height);
  }

  reset(width, height) {
    this.x = Math.random() * width;
    this.y = Math.random() * height * 0.35;
    this.length = 70 + Math.random() * 70;
    this.speed = 8 + Math.random() * 7;
    this.angle = Math.PI / 4 + (Math.random() - 0.5) * 0.35;
    this.opacity = 1;
    this.active = true;
  }

  update(height) {
    this.x += Math.cos(this.angle) * this.speed;
    this.y += Math.sin(this.angle) * this.speed;
    this.opacity -= 0.016;
    if (this.y > height || this.opacity <= 0) this.active = false;
  }

  draw(context) {
    if (!this.active) return;
    const tailX = this.x - Math.cos(this.angle) * this.length;
    const tailY = this.y - Math.sin(this.angle) * this.length;
    const gradient = context.createLinearGradient(tailX, tailY, this.x, this.y);
    gradient.addColorStop(0, 'rgba(255, 215, 0, 0)');
    gradient.addColorStop(1, `rgba(255, 248, 220, ${this.opacity})`);
    context.beginPath();
    context.moveTo(tailX, tailY);
    context.lineTo(this.x, this.y);
    context.strokeStyle = gradient;
    context.lineWidth = 2;
    context.stroke();
    context.beginPath();
    context.arc(this.x, this.y, 2.4, 0, Math.PI * 2);
    context.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
    context.fill();
  }
}

function init() {
  if (!canvas.value) return;
  ctx = canvas.value.getContext('2d');
  resizeCanvas();
  stars = Array.from({ length: config.starCount }, () => new Star(canvas.value.width, canvas.value.height));
  dust = Array.from({ length: config.dustCount }, () => new Dust(canvas.value.width, canvas.value.height));
  animate();
}

function resizeCanvas() {
  if (!canvas.value) return;
  canvas.value.width = window.innerWidth;
  canvas.value.height = window.innerHeight;
}

function animate() {
  if (!ctx || !canvas.value) return;
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
  stars.forEach((star) => {
    star.update();
    star.draw(ctx);
  });
  dust.forEach((speck) => {
    speck.update(canvas.value.width, canvas.value.height);
    speck.draw(ctx);
  });
  if (Math.random() < config.shootingStarChance) {
    shootingStars.push(new ShootingStar(canvas.value.width, canvas.value.height));
  }
  shootingStars = shootingStars.filter((item) => item.active);
  shootingStars.forEach((item) => {
    item.update(canvas.value.height);
    item.draw(ctx);
  });
  animationId = requestAnimationFrame(animate);
}

onMounted(() => {
  init();
  window.addEventListener('resize', resizeCanvas);
});

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId);
  window.removeEventListener('resize', resizeCanvas);
});
</script>
