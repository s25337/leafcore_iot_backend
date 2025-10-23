<script>
  export let value = 0;
  export let min = 0;
  export let max = 100;
  export let size = 260;            // px
  export let stroke = 12;           // grubość pierścienia
  export let startAngle = -130;     // gdzie zaczyna się łuk (deg)
  export let endAngle = 130;        // gdzie kończy się łuk (deg)
  export let label = '';
  export let unit = '';
  export let gradient = ['#7dd3fc','#60a5fa','#a78bfa','#f472b6','#fb7185']; // kolory obwódki
  export let decimals = 0;
  export let fontScale = 0.28;      // rozmiar liczby względem średnicy

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
  $: t = (clamp(value,min,max) - min) / rng;
  $: dash = `${arcCirc * t} ${arcCirc}`;

  // położenie gałki
  const angToXY = (deg) => {
    const rad = (deg - 90) * Math.PI/180;
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
  };
  $: knobAngle = startAngle + t * (endAngle - startAngle);
  $: [kx, ky] = angToXY(knobAngle);

  let dragging = false;

  const angleFromPoint = (x, y) => {
    const dx = x - cx;
    const dy = y - cy;
    let deg = Math.atan2(dy, dx) * 180 / Math.PI + 90;
    // sprowadź do zakresu [0,360)
    if (deg < 0) deg += 360;
    return deg;
  };

  const projectToArc = (deg) => {
    // Normalizuj tak, by porównywać z naszym zakresem (może przechodzić przez 0)
    const a0 = (startAngle + 360) % 360;
    const a1 = (endAngle + 360) % 360;

    // Zbuduj funkcję sprawdzania odległości kątowej w obu kierunkach
    const norm = d => (d+360)%360;

    let d0 = norm(deg - a0);
    let d1 = norm(a1 - a0);

    // jeśli łuk nie zawija przez 0
    if (a0 < a1) {
      if (deg < a0) return a0;
      if (deg > a1) return a1;
      return deg;
    } else {
      // łuk zawija przez 0
      // zakres to [a0..360) ∪ [0..a1]
      if (deg >= a0 || deg <= a1) return deg;
      // wybierz bliższy koniec
      const toA0 = norm(deg - a0);
      const toA1 = norm(a1 - deg);
      return toA0 < toA1 ? a0 : a1;
    }
  };

  const setByPointer = (clientX, clientY, el) => {
    const rect = el.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    let deg = angleFromPoint(x, y);
    deg = projectToArc(deg);

    // przemapuj na t
    let tt = (deg - startAngle) / (endAngle - startAngle);
    // gdy zakres zawija, end-start ujemny — obsłuż:
    const span = endAngle - startAngle;
    tt = (deg - startAngle) / span;
    tt = clamp(tt, 0, 1);

    const nv = min + tt * rng;
    value = Math.round(nv * (10**decimals)) / (10**decimals);
  };

  let svgRef;

  const onPointerDown = (e) => {
    dragging = true;
    svgRef.setPointerCapture(e.pointerId);
    setByPointer(e.clientX, e.clientY, svgRef);
  };
  const onPointerMove = (e) => {
    if (!dragging) return;
    setByPointer(e.clientX, e.clientY, svgRef);
  };
  const onPointerUp = (e) => {
    dragging = false;
    svgRef.releasePointerCapture(e.pointerId);
    // emit change event (opcjonalne)
    const ev = new CustomEvent('change', { detail: value });
    dispatchEvent(ev);
  };

  // gradient id unikalny per instancja
  const gid = `g-${Math.random().toString(36).slice(2,9)}`;
</script>

<svg
  bind:this={svgRef}
  width={size}
  height={size}
  on:pointerdown={onPointerDown}
  on:pointermove={onPointerMove}
  on:pointerup={onPointerUp}
  on:pointercancel={onPointerUp}
  style="cursor:grab; touch-action:none;"
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
