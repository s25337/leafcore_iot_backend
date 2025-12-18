<script>
  let {
    value = $bindable(0),
    min = 0,
    max = 100,
    size = 260,
    stroke = 12,
    startAngle = -130,
    endAngle = 130,
    label = '',
    unit = '',
    gradient = ['#7dd3fc','#60a5fa','#a78bfa','#f472b6','#fb7185'],
    decimals = 0,
    fontScale = 0.20
  } = $props();

  const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n));
  const rng = max - min;

  const r = (size/2) - stroke*1.2;
  const cx = size/2, cy = size/2;
  const arcLen = Math.abs(endAngle - startAngle);
  const circumference = 2 * Math.PI * r;
  const arcRatio = arcLen / 360;
  const arcCirc = circumference * arcRatio;

  let t = $derived((clamp(value,min,max) - min) / rng);
  let dash = $derived(`${arcCirc * t} ${arcCirc}`);

  const angToXY = (deg) => {
    const rad = (deg - 90) * Math.PI/180;
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
  };
  let knobAngle = $derived(startAngle + t * (endAngle - startAngle));
  let [kx, ky] = $derived(angToXY(knobAngle));

  let dragging = $state(false);
  let container;

  const angleFromPoint = (x, y) => {
    const dx = x - cx;
    const dy = y - cy;
    let deg = Math.atan2(dy, dx) * 180 / Math.PI + 90;
    if (deg < 0) deg += 360;
    return deg;
  };

  const projectToArc = (deg) => {
    const a0 = (startAngle + 360) % 360;
    const a1 = (endAngle + 360) % 360;

    if (a0 < a1) {
      if (deg < a0) return a0;
      if (deg > a1) return a1;
      return deg;
    } else {
      if (deg >= a0 || deg <= a1) return deg;
      const toA0 = ((deg - a0 + 360) % 360);
      const toA1 = ((a1 - deg + 360) % 360);
      return toA0 < toA1 ? a0 : a1;
    }
  };

  const updateValue = (clientX, clientY) => {
    if (!container) return;
    const rect = container.getBoundingClientRect();
    const scaleX = size / rect.width;
    const scaleY = size / rect.height;
    const x = (clientX - rect.left) * scaleX;
    const y = (clientY - rect.top) * scaleY;
    let deg = angleFromPoint(x, y);
    deg = projectToArc(deg);

    const span = endAngle - startAngle;
    let tt = (deg - startAngle) / span;
    tt = clamp(tt, 0, 1);

    const nv = min + tt * rng;
    value = Math.round(nv * (10**decimals)) / (10**decimals);
  };

  const gid = `g-${Math.random().toString(36).slice(2,9)}`;
  
  // Knob radius - responsive
  let knobRadius = $derived(stroke * 1.8);
  
  // Min/Max label positions
  let [sx, sy] = $derived(angToXY(startAngle));
  let [ex, ey] = $derived(angToXY(endAngle));
</script>

<div
  bind:this={container}
  role="slider"
  tabindex="0"
  aria-valuenow={value}
  aria-valuemin={min}
  aria-valuemax={max}
  class="circular-slider"
  style="cursor:{dragging ? 'grabbing' : 'grab'};touch-action:none;user-select:none;"
  onpointerdown={(e) => {
    dragging = true;
    updateValue(e.clientX, e.clientY);
    container?.setPointerCapture(e.pointerId);
  }}
  onpointermove={(e) => {
    if (dragging) updateValue(e.clientX, e.clientY);
  }}
  onpointerup={(e) => {
    dragging = false;
    container?.releasePointerCapture(e.pointerId);
  }}
  onpointercancel={(e) => {
    dragging = false;
    container?.releasePointerCapture(e.pointerId);
  }}
>
  <svg width="100%" height="100%" viewBox="0 0 {size} {size}" preserveAspectRatio="xMidYMid meet">
    <defs>
      <linearGradient id={gid} x1="0%" y1="0%" x2="100%" y2="100%">
        {#each gradient as c, i}
          <stop offset="{(i/(gradient.length-1))*100}%" stop-color={c} />
        {/each}
      </linearGradient>
    </defs>

    <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.12)" stroke-width={stroke} />

    <g transform="rotate({startAngle} {cx} {cy})">
      <circle
        cx={cx} cy={cy} r={r}
        fill="none"
        stroke="url(#{gid})"
        stroke-width={stroke}
        stroke-linecap="round"
        stroke-dasharray="{arcCirc} {arcCirc}"
        opacity="0.35"
      />
      <circle
        cx={cx} cy={cy} r={r}
        fill="none"
        stroke="url(#{gid})"
        stroke-width={stroke}
        stroke-linecap="round"
        stroke-dasharray={dash}
      />
    </g>

    <!-- Gałka z wartością -->
    <g class="knob-group">
      <circle 
        cx={kx} 
        cy={ky} 
        r={knobRadius} 
        fill="url(#{gid})" 
        stroke="rgba(255,255,255,0.3)" 
        stroke-width="2"
        filter="drop-shadow(0 2px 8px rgba(0,0,0,0.3))"
      />
      <text 
        x={kx} 
        y={ky} 
        text-anchor="middle" 
        dominant-baseline="middle"
        style="font-size:{knobRadius * 0.6}px; font-weight:700; pointer-events:none;" 
        fill="#fff"
      >
        {value}
      </text>
    </g>

    <!-- Wartość minimalna przy początku okręgu -->
    <text 
      x={sx} 
      y={sy} 
      text-anchor="middle" 
      dominant-baseline="middle"
      style="font-size:12px; font-weight:500; pointer-events:none;" 
      fill="rgba(255,255,255,0.5)"
      transform="translate({sx < cx ? -15 : 15}, {sy < cy ? -8 : 8})"
    >
      {min}
    </text>

    <!-- Wartość maksymalna przy końcu okręgu -->
    <text 
      x={ex} 
      y={ey} 
      text-anchor="middle" 
      dominant-baseline="middle"
      style="font-size:12px; font-weight:500; pointer-events:none;" 
      fill="rgba(255,255,255,0.5)"
      transform="translate({ex < cx ? -15 : 15}, {ey < cy ? -8 : 8})"
    >
      {max}
    </text>

    <g dominant-baseline="middle" text-anchor="middle">
      <text x={cx} y={cy + size*0.01} style="font-size:{size*fontScale}px; font-weight:700;pointer-events:none;" fill="#fff">
        {value}{unit}
      </text>
      {#if label}
        <text x={cx} y={cy + size*0.16} style="font-size:13px; letter-spacing:.5px; text-transform:capitalize; opacity:0.7;pointer-events:none;" fill="rgba(220,230,255,.9)">
          {label}
        </text>
      {/if}
    </g>
  </svg>
</div>

<style>
  .circular-slider { 
    display: block;
    width: 100%;
    max-width: 100%;
    aspect-ratio: 1;
    position: relative;
  }
  
  svg {
    display: block;
    pointer-events: none;
    width: 100%;
    height: 100%;
  }
  
  .knob-group {
    transition: filter 0.2s ease;
  }
  
  .circular-slider:active .knob-group {
    filter: brightness(1.2);
  }
</style>
