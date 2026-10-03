<template>
  <div class="xianxia-backdrop">
    <div class="sun-aura-glow"></div>
    <div class="mountain-layer far-mountains">
      <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path fill="#7ba3c4" fill-opacity="0.45" d="M0,160 Q120,80 240,150 T480,100 T720,170 T960,90 T1200,160 T1440,110 L1440,320 L0,320 Z"></path>
      </svg>
    </div>
    <div class="mountain-layer mid-mountains">
      <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path fill="#4b759a" fill-opacity="0.65" d="M0,210 L60,160 L90,185 L140,130 L180,175 L250,110 L310,180 L380,135 L440,200 L510,120 L580,190 L670,140 L740,210 L820,125 L900,200 L980,130 L1060,190 L1150,140 L1230,210 L1320,150 L1440,190 L1440,320 L0,320 Z"></path>
      </svg>
    </div>
    <div class="mountain-layer near-mountains">
      <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path fill="#2c4660" fill-opacity="0.9" d="M0,260 L40,210 L80,240 L130,170 L180,230 L230,190 L290,270 L350,195 L400,245 L480,175 L540,255 L610,190 L680,275 L760,185 L820,245 L890,170 L950,235 L1020,180 L1100,265 L1180,190 L1250,250 L1340,195 L1440,240 L1440,320 L0,320 Z"></path>
      </svg>
    </div>
    <div class="sea-of-clouds-wrapper">
      <div class="sea-of-clouds wave-1"></div>
      <div class="sea-of-clouds wave-2"></div>
    </div>
    <div class="floating-clouds">
      <div class="cloud-cluster cloud-1"></div>
      <div class="cloud-cluster cloud-2"></div>
      <div class="cloud-cluster cloud-3"></div>
    </div>
    <div class="spirit-particle-field">
      <div v-for="n in 25" :key="n" :class="'spirit-particle p-' + n"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'XianxiaBackdrop',
}
</script>
