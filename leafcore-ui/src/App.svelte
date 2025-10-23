<script>
  import Circular from './lib/CircularSlider.svelte';

  // --- Stany (wartości trzech suwaków)
  let temp = 28;        // °C
  let hum = 30;         // %
  let days = 4;         // dni od ostatniego podlewania

  // --- Zapis/odczyt lokalny
  const load = () => {
    try {
      const raw = localStorage.getItem('leaf-panel-v1');
      if (!raw) return;
      const s = JSON.parse(raw);
      if (Number.isFinite(s.temp)) temp = s.temp;
      if (Number.isFinite(s.hum)) hum = s.hum;
      if (Number.isFinite(s.days)) days = s.days;
    } catch {}
  };

  const save = () => {
    localStorage.setItem('leaf-panel-v1', JSON.stringify({ temp, hum, days }));
  };

  // --- Debounce (żeby nie zapisywać co milisekundę)
  let tmr;
  const sync = () => {
    clearTimeout(tmr);
    tmr = setTimeout(() => {
      save();
    }, 300);
  };

  load();

  // --- Zegar (data + czas w nagłówku)
  let now = new Date();
  const pad = (n)=> String(n).padStart(2,'0');
  const timeStr = () => `${pad(now.getHours())}:${pad(now.getMinutes())}`;
  const dateStr = () => now.toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric' });

  const tick = () => { now = new Date(); };
  const timer = setInterval(tick, 1000);

  $: time = timeStr();
  $: date = dateStr();

  // --- reaguj na zmianę wartości
  $: { temp; hum; days; sync(); }
</script>

<div class="container">
  <!-- Górny zegar -->
  <div class="header">
    <div class="date">{date}</div>
    <div class="time">{time}</div>
  </div>

  <!-- Trzy okrągłe suwaki -->
  <div class="grid">
    <!-- Temperatura -->
    <div class="card">
      <Circular
        bind:value={temp}
        min={10}
        max={40}
        unit="°C"
        label="temperature"
        gradient={['#60a5fa','#a78bfa','#fb7185']}
        size={280}
        stroke={14}
        startAngle={-140}
        endAngle={140}
      />
    </div>

    <!-- Wilgotność -->
    <div class="card">
      <Circular
        bind:value={hum}
        min={0}
        max={100}
        unit="%"
        label="humidity"
        gradient={['#34d399','#22c55e','#a3e635']}
        size={280}
        stroke={14}
        startAngle={-140}
        endAngle={140}
      />
    </div>

    <!-- Dni podlewania -->
    <div class="card">
      <Circular
        bind:value={days}
        min={0}
        max={14}
        unit=" days"
        label="watering"
        gradient={['#60a5fa','#38bdf8','#0ea5e9']}
        size={280}
        stroke={14}
        startAngle={-140}
        endAngle={140}
      />
      <div class="footer">Tip: przeciągnij po okręgu, by zmienić</div>
    </div>
  </div>
</div>
