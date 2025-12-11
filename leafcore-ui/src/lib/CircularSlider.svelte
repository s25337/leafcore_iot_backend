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
    fontScale = 0.28
  } = $props();

  const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n));
  const rng = max - min;

  // geometra
  const r = (size/2) - stroke*1.2;
  const cx = size/2, cy = size/2;
  const arcLen = Math.abs(endAngle - startAngle);
  const circumference = 2 * Math.PI * r;
  const arcRatio = arcLen / 360;
  const arcCirc = circumference * arcRatio;

  // procent w obrębie łuku
  let t = $derived((clamp(value,min,max) - min) / rng);
  let dash = $derived(`${arcCirc * t} ${arcCirc}`);

  // położenie gałki
  const angToXY = (deg) => {
    const rad = (deg - 90) * Math.PI/180;
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
  };
  let knobAngle = $derived(startAngle + t * (endAngle - startAngle));
  let [kx, ky] = $derived(angToXY(knobAngle));

  let dragging = $state(false);
  let svgRef; // zwykła zmienna dla bind:this

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

    const norm = d => (d+360)%360;

    let d0 = norm(deg - a0);
    let d1 = norm(a1 - a0);

    if (a0 < a1) {
      if (deg < a0) return a0;
      if (deg > a1) return a1;
      return deg;
    } else {
      if (deg >= a0 || deg <= a1) return deg;
      const toA0 = norm(deg - a0);
      const toA1 = norm(a1 - deg);
      return toA0 < toA1 ? a0 : a1;
    }
  };

  const setByPointer = (clientX, clientY, el) => {
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    let deg = angleFromPoint(x, y);
    deg = projectToArc(deg);

    const span = endAngle - startAngle;
    let tt = (deg - startAngle) / span;
    tt = clamp(tt, 0, 1);

    const nv = min + tt * rng;
    value = Math.round(nv * (10**decimals)) / (10**decimals);
  };

  const onPointerDown = (e) => {
    if (!svgRef) return;
    dragging = true;
    svgRef.setPointerCapture(e.pointerId);
    setByPointer(e.clientX, e.clientY, svgRef);
  };

  const onPointerMove = (e) => {
    if (!dragging || !svgRef) return;
    setByPointer(e.clientX, e.clientY, svgRef);
  };

  const onPointerUp = (e) => {
    if (!svgRef) return;
    dragging = false;
    svgRef.releasePointerCapture(e.pointerId);
  };

  // gradient id unikalny per instancja
  const gid = `g-${Math.random().toString(36).slice(2,9)}`;
</script>

<svg
  bind:this={svgRef}
  width={size}
  height={size}
  onpointerdown={onPointerDown}
  onpointermove={onPointerMove}
  onpointerup={onPointerUp}
  onpointercancel={onPointerUp}
  style="cursor:grab; touch-action:none; user-select:none;"
  viewBox={`0 0 ${size} ${size}`}
>
  <defs>
    <linearGradient id={gid} x1="0%" y1="0%" x2="100%" y2="100%">
      {#each gradient as c, i}
        <stop offset={(i/(gradient.length-1))*100 + '%'} stop-color={c} />
      {/each}
    </linearGradient>
  </defs>

  <!-- cienka baza -->
  <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.12)" stroke-width={stroke} />

  <!-- widoczny łuk w tle -->
  <g transform={`rotate(${startAngle} ${cx} ${cy})`}>
    <circle
      cx={cx} cy={cy} r={r}
      fill="none"
      stroke="url(#{gid})"
      stroke-width={stroke}
      stroke-linecap="round"
      stroke-dasharray={arcCirc + ' ' + arcCirc}
      stroke-dashoffset="0"
      opacity="0.35"
    />
    <!-- wartość -->
    <circle
      cx={cx} cy={cy} r={r}
      fill="none"
      stroke="url(#{gid})"
      stroke-width={stroke}
      stroke-linecap="round"
      stroke-dasharray={dash}
      stroke-dashoffset="0"
    />
  </g>

  <!-- gałka -->
  <circle cx={kx} cy={ky} r={stroke*1.1} fill={`url(#${gid})`} stroke="#0b1220" stroke-width="2" />

  <!-- tekst środka -->
  <g dominant-baseline="middle" text-anchor="middle">
    <text x={cx} y={cy - size*0.04} style={`font-size:${size*fontScale}px; font-weight:700;`} fill="#fff">
      {value}{unit}
    </text>
    {#if label}
      <text x={cx} y={cy + size*0.12} style="font-size:16px; letter-spacing:.5px;" fill="rgba(220,230,255,.7)">
        {label}
      </text>
    {/if}
  </g>
</svg>

<style>
  :global(svg){display:block}
</style>
