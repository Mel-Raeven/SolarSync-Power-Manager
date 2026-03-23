@extends('layouts.app')

@section('title', 'Add First Appliance')

@section('content')

@include('partials.onboarding-progress', ['step' => $step, 'totalSteps' => $totalSteps])

<div class="max-w-xl mx-auto" x-data="applianceForm()">

    <h1 class="text-2xl font-bold text-gray-900 mb-2">Add your first appliance</h1>
    <p class="text-gray-500 mb-8">
        Tell SolarSync about an appliance to control. You can add more after setup.
    </p>

    @if ($errors->any())
        <div class="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            @foreach ($errors->all() as $error)
                <p class="text-sm text-red-600">{{ $error }}</p>
            @endforeach
        </div>
    @endif

    <form method="POST" action="{{ route('onboarding.step4.submit') }}" class="space-y-5">
        @csrf

        {{-- Name --}}
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Appliance name</label>
            <input type="text" name="name" value="{{ old('name') }}" required
                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                          focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent"
                   placeholder="Pool pump">
        </div>

        {{-- Watt draw --}}
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Power draw (watts)</label>
            <input type="number" name="watt_draw" value="{{ old('watt_draw') }}" required min="1" max="100000"
                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                          focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent"
                   placeholder="750">
            <p class="mt-1.5 text-xs text-gray-400">Check the label on the device or its manual.</p>
        </div>

        {{-- Schedule mode --}}
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Schedule mode</label>
            <select name="schedule_mode" x-model="mode"
                    class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm bg-white
                           focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                <option value="solar_only" {{ old('schedule_mode') === 'solar_only' ? 'selected' : '' }}>Solar only — runs only when there's surplus</option>
                <option value="solar_preferred" {{ old('schedule_mode') === 'solar_preferred' ? 'selected' : '' }}>Solar preferred — prefers surplus, falls back to grid</option>
                <option value="time_window" {{ old('schedule_mode') === 'time_window' ? 'selected' : '' }}>Time window — solar surplus within a time window</option>
                <option value="manual" {{ old('schedule_mode') === 'manual' ? 'selected' : '' }}>Manual — controlled by you only</option>
            </select>
        </div>

        {{-- Time window (conditional) --}}
        <div x-show="mode === 'time_window'" x-transition class="grid grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Start time</label>
                <input type="time" name="time_window_start" value="{{ old('time_window_start', '09:00') }}"
                       class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                              focus:outline-none focus:ring-2 focus:ring-solar-500">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End time</label>
                <input type="time" name="time_window_end" value="{{ old('time_window_end', '18:00') }}"
                       class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                              focus:outline-none focus:ring-2 focus:ring-solar-500">
            </div>
        </div>

        {{-- Hub + plug selection --}}
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Hub</label>
            <select name="hub_id" x-model="hubId" x-on:change="loadPlugs()"
                    class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm bg-white
                           focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                <option value="">Select a hub…</option>
                @foreach ($hubs as $hub)
                    <option value="{{ $hub['id'] }}" {{ old('hub_id') == $hub['id'] ? 'selected' : '' }}>
                        {{ $hub['name'] }}
                    </option>
                @endforeach
            </select>
        </div>

        <div x-show="hubId" x-transition>
            <label class="block text-sm font-medium text-gray-700 mb-1">Smart plug</label>
            <select name="plug_id"
                    class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm bg-white
                           focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                <option value="">
                    <span x-text="loadingPlugs ? 'Loading plugs…' : 'Select a plug…'"></span>
                </option>
                <template x-for="plug in plugs" :key="plug.id">
                    <option :value="plug.id" x-text="plug.name + ' (' + plug.type + ')'"></option>
                </template>
            </select>
        </div>

        {{-- Priority --}}
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Priority <span class="text-gray-400 font-normal">(1 = highest)</span></label>
            <input type="number" name="priority" value="{{ old('priority', 1) }}" min="1" max="10"
                   class="w-32 rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                          focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
        </div>

        <div class="flex justify-between items-center pt-2">
            <a href="{{ route('onboarding.step3') }}" class="text-sm text-gray-500 hover:text-gray-700">Back</a>
            <button type="submit"
                class="inline-flex items-center gap-2 bg-solar-500 hover:bg-solar-600 text-white font-semibold
                       rounded-lg px-6 py-2.5 text-sm transition-colors duration-150 shadow-sm">
                Finish setup
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                </svg>
            </button>
        </div>

    </form>

</div>

<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
<script>
function applianceForm() {
    return {
        mode: '{{ old('schedule_mode', 'solar_only') }}',
        hubId: '{{ old('hub_id', '') }}',
        plugs: [],
        loadingPlugs: false,

        loadPlugs() {
            if (! this.hubId) return;
            this.loadingPlugs = true;
            this.plugs = [];
            fetch(`/onboarding/discover-plugs?hub_id=${this.hubId}`, {
                headers: { 'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content }
            })
            .then(r => r.json())
            .then(data => { this.plugs = data; })
            .catch(() => {})
            .finally(() => { this.loadingPlugs = false; });
        }
    }
}
</script>

@endsection
