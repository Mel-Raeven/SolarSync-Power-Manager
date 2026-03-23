{{--
    Shared appliance form partial.
    Variables expected:
      $hubs      – array of hubs from API
      $appliance – null (create) or array (edit, for prefill)
--}}

@php
    $isEdit          = ! is_null($appliance);
    $oldMode         = old('schedule_mode', $isEdit ? $appliance['schedule_mode'] : 'solar_only');
    $oldHubId        = old('hub_id',        $isEdit ? $appliance['hub_id']        : '');
    $oldPlugId       = old('plug_id',       $isEdit ? $appliance['plug_id']       : '');
    $oldPriority     = old('priority',      $isEdit ? ($appliance['priority'] ?? 1) : 1);
    $oldName         = old('name',          $isEdit ? $appliance['name']          : '');
    $oldWattDraw     = old('watt_draw',     $isEdit ? $appliance['watt_draw']     : '');
    $oldWindowStart  = old('time_window_start', $isEdit ? ($appliance['time_window_start'] ?? '09:00') : '09:00');
    $oldWindowEnd    = old('time_window_end',   $isEdit ? ($appliance['time_window_end']   ?? '18:00') : '18:00');
@endphp

<div x-data="applianceForm()" class="space-y-5">

    {{-- Name --}}
    <div>
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Appliance name</label>
        <input type="text" id="name" name="name" value="{{ $oldName }}" required maxlength="100"
               class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                      focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent"
               placeholder="Pool pump">
    </div>

    {{-- Watt draw --}}
    <div>
        <label for="watt_draw" class="block text-sm font-medium text-gray-700 mb-1">Power draw (watts)</label>
        <input type="number" id="watt_draw" name="watt_draw" value="{{ $oldWattDraw }}" required min="1" max="100000"
               class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                      focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent"
               placeholder="750">
        <p class="mt-1.5 text-xs text-gray-400">Check the label on the device or its manual.</p>
    </div>

    {{-- Schedule mode --}}
    <div>
        <label for="schedule_mode" class="block text-sm font-medium text-gray-700 mb-1">Schedule mode</label>
        <select id="schedule_mode" name="schedule_mode" x-model="mode"
                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm bg-white
                       focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
            <option value="solar_only"      {{ $oldMode === 'solar_only'      ? 'selected' : '' }}>Solar only — runs only when there's surplus</option>
            <option value="solar_preferred" {{ $oldMode === 'solar_preferred' ? 'selected' : '' }}>Solar preferred — prefers surplus, falls back to grid</option>
            <option value="time_window"     {{ $oldMode === 'time_window'     ? 'selected' : '' }}>Time window — solar surplus within a time window</option>
            <option value="manual"          {{ $oldMode === 'manual'          ? 'selected' : '' }}>Manual — controlled by you only</option>
        </select>
    </div>

    {{-- Time window (shown only when schedule_mode = time_window) --}}
    <div x-show="mode === 'time_window'" x-transition class="grid grid-cols-2 gap-4">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Start time</label>
            <input type="time" name="time_window_start" value="{{ $oldWindowStart }}"
                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                          focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">End time</label>
            <input type="time" name="time_window_end" value="{{ $oldWindowEnd }}"
                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                          focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
        </div>
    </div>

    {{-- Hub select --}}
    <div>
        <label for="hub_id" class="block text-sm font-medium text-gray-700 mb-1">Hub</label>
        <select id="hub_id" name="hub_id" x-model="hubId" x-on:change="loadPlugs()"
                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm bg-white
                       focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
            <option value="">Select a hub…</option>
            @foreach ($hubs as $hub)
                <option value="{{ $hub['id'] }}" {{ (string) $oldHubId === (string) $hub['id'] ? 'selected' : '' }}>
                    {{ $hub['name'] }}
                </option>
            @endforeach
        </select>
    </div>

    {{-- Plug select (loaded via AJAX when hub changes) --}}
    <div x-show="hubId" x-transition>
        <label for="plug_id" class="block text-sm font-medium text-gray-700 mb-1">Smart plug</label>
        <select id="plug_id" name="plug_id"
                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm bg-white
                       focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
            <template x-if="loadingPlugs">
                <option value="">Loading plugs…</option>
            </template>
            <template x-if="!loadingPlugs && plugs.length === 0">
                <option value="">Select a plug…</option>
            </template>
            <template x-for="plug in plugs" :key="plug.id">
                <option :value="plug.id"
                        :selected="plug.id == selectedPlugId"
                        x-text="plug.name + ' (' + plug.type + ')'"></option>
            </template>
        </select>
    </div>

    {{-- Priority --}}
    <div>
        <label for="priority" class="block text-sm font-medium text-gray-700 mb-1">
            Priority <span class="text-gray-400 font-normal">(1 = highest)</span>
        </label>
        <input type="number" id="priority" name="priority" value="{{ $oldPriority }}" min="1" max="10"
               class="w-32 rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                      focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
    </div>

    {{-- Submit --}}
    <div class="flex justify-between items-center pt-2">
        <a href="{{ route('appliances.index') }}"
           class="text-sm border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium
                  rounded-lg px-4 py-2.5 transition-colors duration-100">
            Cancel
        </a>
        <button type="submit"
                class="inline-flex items-center gap-2 bg-solar-500 hover:bg-solar-600 text-white font-semibold
                       rounded-lg px-6 py-2.5 text-sm transition-colors duration-150 shadow-sm">
            {{ $isEdit ? 'Save changes' : 'Add appliance' }}
        </button>
    </div>

</div>

<script>
function applianceForm() {
    return {
        mode: '{{ $oldMode }}',
        hubId: '{{ $oldHubId }}',
        selectedPlugId: '{{ $oldPlugId }}',
        plugs: [],
        loadingPlugs: false,

        init() {
            if (this.hubId) {
                this.loadPlugs();
            }
        },

        loadPlugs() {
            if (! this.hubId) return;
            this.loadingPlugs = true;
            this.plugs = [];
            fetch('/onboarding/discover-plugs?hub_id=' + this.hubId, {
                headers: { 'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content }
            })
            .then(function (r) { return r.json(); })
            .then(function (data) { this.plugs = data; }.bind(this))
            .catch(function () {})
            .finally(function () { this.loadingPlugs = false; }.bind(this));
        }
    };
}
</script>
