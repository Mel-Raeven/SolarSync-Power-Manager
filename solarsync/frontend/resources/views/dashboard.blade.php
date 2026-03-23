@extends('layouts.app')

@section('title', 'Dashboard')

@push('head')
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
@endpush

@section('content')

{{-- Flash message --}}
@if (session('success'))
    <div class="mb-6 bg-green-50 border border-green-200 rounded-lg px-5 py-4 flex items-center gap-3">
        <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
        </svg>
        <p class="text-sm text-green-700 font-medium">{{ session('success') }}</p>
    </div>
@endif

<div class="mb-8 flex items-center justify-between">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-gray-500 mt-1 text-sm">Live solar power overview</p>
    </div>
    <span class="text-xs text-gray-400" id="last-updated">Updated just now</span>
</div>

{{-- ── Power cards (auto-refreshing) ──────────────────────────────────────── --}}
<div
    x-data="powerCards()"
    x-init="init()"
    class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8"
>
    {{-- Solar Production --}}
    <div class="bg-white rounded-xl border border-solar-200 px-6 py-5 shadow-sm">
        <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-solar-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round"
                      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/>
            </svg>
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Solar production</p>
        </div>
        <p class="text-3xl font-bold text-solar-600">
            <span x-text="solar !== null ? solar + ' W' : '— W'">{{ $solarProduction !== null ? $solarProduction . ' W' : '— W' }}</span>
        </p>
    </div>

    {{-- Grid Draw --}}
    <div class="bg-white rounded-xl border border-gray-200 px-6 py-5 shadow-sm">
        <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round"
                      d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Grid draw</p>
        </div>
        <p class="text-3xl font-bold text-gray-800">
            <span x-text="grid !== null ? grid + ' W' : '— W'">{{ $gridDraw !== null ? $gridDraw . ' W' : '— W' }}</span>
        </p>
    </div>

    {{-- Surplus --}}
    <div class="bg-green-50 rounded-xl border border-green-200 px-6 py-5 shadow-sm">
        <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round"
                      d="M5 3l14 9-14 9V3z"/>
            </svg>
            <p class="text-xs font-semibold text-green-500 uppercase tracking-wide">Surplus</p>
        </div>
        <p class="text-3xl font-bold text-green-700">
            <span x-text="surplus !== null ? surplus + ' W' : '— W'">{{ $surplus !== null ? $surplus . ' W' : '— W' }}</span>
        </p>
    </div>
</div>

{{-- ── Appliances ───────────────────────────────────────────────────────────── --}}
<div class="bg-white rounded-xl border border-gray-200 shadow-sm mb-8">
    <div class="px-6 py-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-900">Appliances</h2>
        <p class="text-xs text-gray-400 mt-0.5">Manual overrides take priority over solar scheduling</p>
    </div>

    @if (count($appliances) === 0)
        <div class="px-6 py-10 text-center text-gray-400 text-sm">
            No appliances configured yet.
            <a href="{{ route('onboarding.step4') }}" class="text-solar-600 hover:underline ml-1">Add one</a>.
        </div>
    @else
        <ul class="divide-y divide-gray-100">
            @foreach ($appliances as $appliance)
            <li
                x-data="applianceOverride({{ $appliance['id'] }}, {{ json_encode($appliance['override_on']) }})"
                class="px-6 py-4 flex items-center gap-4"
            >
                {{-- Status dot --}}
                <span
                    class="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    :class="{
                        'bg-green-400': '{{ $appliance['status'] }}' === 'running',
                        'bg-gray-300':  '{{ $appliance['status'] }}' === 'idle',
                        'bg-red-400':   '{{ $appliance['status'] }}' === 'disabled'
                    }"
                    title="{{ $appliance['status'] }}"
                ></span>

                {{-- Name + meta --}}
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                        <span class="font-medium text-gray-900 text-sm truncate">{{ $appliance['name'] }}</span>
                        <span class="text-xs text-gray-400">{{ $appliance['watt_draw'] }} W</span>
                        {{-- Schedule mode badge --}}
                        @php
                            $badgeClasses = match($appliance['schedule_mode']) {
                                'solar_only'       => 'bg-solar-100 text-solar-700',
                                'solar_preferred'  => 'bg-amber-50 text-amber-600',
                                'time_window'      => 'bg-blue-50 text-blue-600',
                                'manual'           => 'bg-gray-100 text-gray-500',
                                default            => 'bg-gray-100 text-gray-500',
                            };
                            $badgeLabel = match($appliance['schedule_mode']) {
                                'solar_only'      => 'Solar only',
                                'solar_preferred' => 'Solar preferred',
                                'time_window'     => 'Time window',
                                'manual'          => 'Manual',
                                default           => $appliance['schedule_mode'],
                            };
                        @endphp
                        <span class="text-xs px-2 py-0.5 rounded-full font-medium {{ $badgeClasses }}">{{ $badgeLabel }}</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-0.5">
                        Priority {{ $appliance['priority'] ?? '—' }}
                        <template x-if="overrideOn !== null">
                            <span class="ml-2 font-semibold" :class="overrideOn ? 'text-solar-600' : 'text-gray-400'">
                                — Override <span x-text="overrideOn ? 'ON' : 'OFF'"></span>
                            </span>
                        </template>
                    </p>
                </div>

                {{-- Override toggle --}}
                <div class="flex items-center gap-2 flex-shrink-0">
                    <span class="text-xs text-gray-400 hidden sm:inline">Override</span>
                    <div class="flex rounded-lg overflow-hidden border border-gray-200 text-xs font-medium">
                        <button
                            @click="setOverride(true)"
                            :disabled="loading"
                            :class="overrideOn === true
                                ? 'bg-solar-500 text-white'
                                : 'bg-white text-gray-500 hover:bg-gray-50'"
                            class="px-3 py-1.5 transition-colors"
                        >ON</button>
                        <button
                            @click="setOverride(null)"
                            :disabled="loading"
                            :class="overrideOn === null
                                ? 'bg-gray-200 text-gray-700'
                                : 'bg-white text-gray-500 hover:bg-gray-50'"
                            class="px-3 py-1.5 border-x border-gray-200 transition-colors"
                        >AUTO</button>
                        <button
                            @click="setOverride(false)"
                            :disabled="loading"
                            :class="overrideOn === false
                                ? 'bg-red-500 text-white'
                                : 'bg-white text-gray-500 hover:bg-gray-50'"
                            class="px-3 py-1.5 transition-colors"
                        >OFF</button>
                    </div>
                    <span x-show="loading" class="text-xs text-gray-400 animate-pulse">saving…</span>
                    <span x-show="error" class="text-xs text-red-500" x-text="error"></span>
                </div>
            </li>
            @endforeach
        </ul>
    @endif
</div>

{{-- ── 24-hour power chart ───────────────────────────────────────────────────── --}}
<div class="bg-white rounded-xl border border-gray-200 shadow-sm">
    <div class="px-6 py-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-900">Last 24 hours</h2>
        <p class="text-xs text-gray-400 mt-0.5">Solar production, surplus and grid draw</p>
    </div>
    <div class="px-6 py-6">
        @if (count($chartData['labels']) === 0)
            <p class="text-sm text-gray-400 text-center py-8">No history data available yet.</p>
        @else
            <canvas id="powerChart" height="100"></canvas>
        @endif
    </div>
</div>

@endsection

{{-- ── Scripts ──────────────────────────────────────────────────────────────── --}}
@section('scripts')
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<script>
// ── Power cards: auto-refresh every 60 s ─────────────────────────────────────
function powerCards() {
    return {
        solar:   {{ $solarProduction !== null ? $solarProduction : 'null' }},
        grid:    {{ $gridDraw !== null ? $gridDraw : 'null' }},
        surplus: {{ $surplus !== null ? $surplus : 'null' }},
        timer:   null,

        init() {
            this.timer = setInterval(() => this.refresh(), 60_000);
        },

        async refresh() {
            try {
                const res = await fetch('{{ route('dashboard.status') }}', {
                    headers: { 'Accept': 'application/json' }
                });
                if (!res.ok) return;
                const data = await res.json();
                this.solar   = data.solar_production_w ?? null;
                this.grid    = data.grid_draw_w ?? null;
                this.surplus = data.surplus_w ?? null;

                document.getElementById('last-updated').textContent =
                    'Updated ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            } catch (e) {
                // silently ignore network errors
            }
        }
    };
}

// ── Appliance override toggle ─────────────────────────────────────────────────
function applianceOverride(id, initialOverride) {
    return {
        overrideOn: initialOverride,
        loading:    false,
        error:      null,

        async setOverride(value) {
            if (this.loading) return;
            this.loading = true;
            this.error   = null;
            try {
                const res = await fetch(`/appliances/${id}/override`, {
                    method:  'POST',
                    headers: {
                        'Content-Type':     'application/json',
                        'Accept':           'application/json',
                        'X-CSRF-TOKEN':     document.querySelector('meta[name="csrf-token"]').content,
                    },
                    body: JSON.stringify({ override_on: value }),
                });
                if (!res.ok) {
                    const body = await res.json().catch(() => ({}));
                    this.error = body.error ?? 'Failed to save';
                } else {
                    this.overrideOn = value;
                }
            } catch (e) {
                this.error = 'Network error';
            } finally {
                this.loading = false;
            }
        }
    };
}

// ── Chart.js 24-hour line chart ───────────────────────────────────────────────
(function () {
    const canvas = document.getElementById('powerChart');
    if (!canvas) return;

    const chartData = @json($chartData);

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label:           'Solar (W)',
                    data:            chartData.solar,
                    borderColor:     '#f59e0b',
                    backgroundColor: 'rgba(245,158,11,0.08)',
                    borderWidth:     2,
                    pointRadius:     2,
                    tension:         0.3,
                    fill:            true,
                },
                {
                    label:           'Surplus (W)',
                    data:            chartData.surplus,
                    borderColor:     '#22c55e',
                    backgroundColor: 'rgba(34,197,94,0.08)',
                    borderWidth:     2,
                    pointRadius:     2,
                    tension:         0.3,
                    fill:            true,
                },
                {
                    label:           'Grid draw (W)',
                    data:            chartData.grid,
                    borderColor:     '#9ca3af',
                    backgroundColor: 'rgba(156,163,175,0.06)',
                    borderWidth:     2,
                    pointRadius:     2,
                    tension:         0.3,
                    fill:            false,
                },
            ],
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { font: { size: 12 }, boxWidth: 14 },
                },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y} W`,
                    },
                },
            },
            scales: {
                x: {
                    ticks: {
                        maxTicksLimit: 12,
                        font: { size: 11 },
                    },
                    grid: { color: 'rgba(0,0,0,0.04)' },
                },
                y: {
                    title: { display: true, text: 'Watts', font: { size: 11 } },
                    ticks: { font: { size: 11 } },
                    grid:  { color: 'rgba(0,0,0,0.04)' },
                    beginAtZero: true,
                },
            },
        },
    });
})();
</script>
@endsection
