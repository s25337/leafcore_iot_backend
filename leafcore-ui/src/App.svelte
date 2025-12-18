<script>
  import Circular from './lib/CircularSlider.svelte';

  // --- Stany
  let temp = 28;        // °C
  let hum = 30;         // %
  let lightOn = true;   // stan światła
  let waterTank = 200;  // ml w zbiorniku

  // --- Zapis/odczyt lokalny
  const load = () => {
    try {
      const raw = localStorage.getItem('leaf-panel-v1');
      if (!raw) return;
      const s = JSON.parse(raw);
      if (Number.isFinite(s.temp)) temp = s.temp;
      if (Number.isFinite(s.hum)) hum = s.hum;
      if (typeof s.lightOn === 'boolean') lightOn = s.lightOn;
      if (Number.isFinite(s.waterTank)) waterTank = s.waterTank;
    } catch {}
  };

  const save = () => {
    localStorage.setItem('leaf-panel-v1', JSON.stringify({ temp, hum, lightOn, waterTank }));
  };

  // --- Debounce
  let tmr;
  const sync = () => {
    clearTimeout(tmr);
    tmr = setTimeout(() => {
      save();
    }, 300);
  };

  load();

  // --- Zegar
  let now = new Date();
  const pad = (n)=> String(n).padStart(2,'0');
  const timeStr = () => `${pad(now.getHours())}:${pad(now.getMinutes())}`;
  const dateStr = () => now.toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric' });

  const tick = () => { now = new Date(); };
  const timer = setInterval(tick, 1000);

  $: time = timeStr();
  $: date = dateStr();

  // --- reaguj na zmianę wartości
  $: { temp; hum; lightOn; waterTank; sync(); }

  // --- Toggle light
  const toggleLight = () => {
    lightOn = !lightOn;
  };
</script>

<div class="container">
  <!-- Górny nagłówek z czasem -->
  <div class="header">
    <div class="time">{time}</div>
    <div class="date">{date}</div>
  </div>

  <!-- Siatka 2x2 -->
  <div class="grid">
    <!-- Temperatura -->
    <div class="card large">
      <button class="power-btn" aria-label="Power">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2v10M18.36 6.64a9 9 0 1 1-12.73 0"/>
        </svg>
      </button>
      <div class="slider-wrapper">
        <Circular
          bind:value={temp}
          min={10}
          max={40}
          unit="°C"
          label="Temperature"
          gradient={['#60a5fa','#a78bfa','#fb7185']}
          size={280}
          stroke={14}
          startAngle={-140}
          endAngle={140}
        />
      </div>
    </div>

    <!-- Wilgotność -->
    <div class="card large">
      <button class="power-btn" aria-label="Power">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2v10M18.36 6.64a9 9 0 1 1-12.73 0"/>
        </svg>
      </button>
      <div class="slider-wrapper">
        <Circular
          bind:value={hum}
          min={0}
          max={100}
          unit="%"
          label="Humidity"
          gradient={['#60a5fa','#34d399','#22d3ee']}
          size={280}
          stroke={14}
          startAngle={-140}
          endAngle={140}
        />
      </div>
    </div>

    <!-- Light -->
    <div class="card small">
      <div class="card-header">
        <h3>Light</h3>
      </div>
      <div class="card-content">
        <div class="icon-circle" class:active={lightOn}>
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 18h6M10 22h4M12 3v3M12 3a6 6 0 0 0-6 6c0 3.5 2 5 4 7h4c2-2 4-3.5 4-7a6 6 0 0 0-6-6z"/>
          </svg>
        </div>
        <div class="info">
          <div class="status">{lightOn ? 'On' : 'Off'}</div>
          <div class="schedule">Schedule: 18:00 - 06:00</div>
        </div>
      </div>
    </div>

    <!-- Watering -->
    <div class="card small">
      <div class="card-header">
        <h3>Watering</h3>
      </div>
      <div class="card-content">
        <div class="icon-circle water">
          <svg width="70" height="70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
          </svg>
        </div>
        <div class="info">
          <div class="status">Next in: 2 : 10 : 54 : 33</div>
          <div class="schedule">Water tank: {waterTank} ml</div>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    overflow-x: hidden;
  }

  .container {
    min-height: 100vh;
    padding: 2.5rem;
    box-sizing: border-box;
    max-width: 1400px;
    margin: 0 auto;
  }

  .header {
    text-align: left;
    margin-bottom: 2.5rem;
    padding-left: 1rem;
  }

  .time {
    font-size: 3.5rem;
    font-weight: 300;
    letter-spacing: 1px;
    margin-bottom: 0.25rem;
  }

  .date {
    font-size: 1.125rem;
    opacity: 0.8;
    font-weight: 400;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: auto auto;
    gap: 2rem;
    max-width: 1200px;
  }

  .card {
    background: rgba(30, 30, 50, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 32px;
    padding: 2rem;
    position: relative;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }

  .card.large {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 420px;
  }

  .slider-wrapper {
    width: 100%;
    max-width: 320px;
    padding: 1rem;
  }

  .card.small {
    display: flex;
    flex-direction: column;
    min-height: 280px;
  }

  .power-btn {
    position: absolute;
    top: 1.5rem;
    right: 1.5rem;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(100, 180, 100, 0.15);
    border: 2px solid rgba(100, 200, 100, 0.3);
    color: rgba(150, 220, 150, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .power-btn:hover {
    background: rgba(100, 180, 100, 0.25);
    border-color: rgba(100, 200, 100, 0.5);
    color: rgba(150, 220, 150, 1);
  }

  .card-header {
    margin-bottom: 1.5rem;
  }

  .card-header h3 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 500;
    opacity: 0.9;
  }

  .card-content {
    display: flex;
    align-items: center;
    gap: 2rem;
    flex: 1;
  }

  .icon-circle {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: rgba(255, 200, 100, 0.1);
    border: 3px solid rgba(255, 180, 80, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(255, 200, 100, 0.5);
    flex-shrink: 0;
    transition: all 0.3s ease;
  }

  .icon-circle.active {
    background: rgba(255, 200, 100, 0.15);
    border-color: rgba(255, 180, 80, 0.6);
    color: rgba(255, 200, 100, 0.9);
    box-shadow: 0 0 30px rgba(255, 180, 80, 0.3);
  }

  .icon-circle.water {
    background: rgba(100, 200, 255, 0.1);
    border-color: rgba(100, 200, 255, 0.3);
    color: rgba(100, 200, 255, 0.6);
  }

  .info {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .status {
    font-size: 1.25rem;
    font-weight: 400;
  }

  .schedule {
    font-size: 0.95rem;
    opacity: 0.7;
  }

  /* Responsywność */
  @media (max-width: 1024px) {
    .grid {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .card.large {
      min-height: 380px;
    }

    .slider-wrapper {
      max-width: 280px;
    }

    .card.small {
      min-height: 220px;
    }
  }

  @media (max-width: 768px) {
    .container {
      padding: 1.5rem;
    }

    .time {
      font-size: 2.5rem;
    }

    .date {
      font-size: 1rem;
    }

    .card {
      padding: 1.5rem;
      border-radius: 24px;
    }

    .card.large {
      min-height: 340px;
    }

    .slider-wrapper {
      max-width: 240px;
      padding: 0.5rem;
    }

    .card-content {
      flex-direction: column;
      gap: 1.5rem;
    }

    .icon-circle {
      width: 120px;
      height: 120px;
    }

    .power-btn {
      width: 42px;
      height: 42px;
      top: 1rem;
      right: 1rem;
    }
  }

  @media (max-width: 480px) {
    .container {
      padding: 1rem;
    }

    .time {
      font-size: 2rem;
    }

    .slider-wrapper {
      max-width: 200px;
    }

    .card.large {
      min-height: 300px;
      padding: 1rem;
    }

    .card.small {
      min-height: 200px;
      padding: 1rem;
    }
  }
</style>
