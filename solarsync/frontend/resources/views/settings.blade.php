@extends('layouts.app')

@section('title', 'Settings')

@section('content')

{{-- Alpine.js --}}
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>

{{-- Flash messages --}}
@if (session('success'))
    <div class="mb-6 bg-green-50 border border-green-200 rounded-lg px-5 py-4 flex items-center gap-3">
        <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
        </svg>
        <p class="text-sm text-green-700 font-medium">{{ session('success') }}</p>
    </div>
@endif

@if ($errors->any())
    <div class="mb-6 bg-red-50 border border-red-200 rounded-lg px-5 py-4">
        <p class="text-sm text-red-700 font-medium mb-1">Please fix the following errors:</p>
        <ul class="list-disc list-inside text-sm text-red-600 space-y-0.5">
            @foreach ($errors->all() as $error)
                <li>{{ $error }}</li>
            @endforeach
        </ul>
    </div>
@endif

<div class="mb-8">
    <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
    <p class="text-gray-500 mt-1 text-sm">Manage hubs, energy providers, and system configuration.</p>
</div>

{{-- ═══════════════════════════════════════════════════════════════════════════
     Section 1: Hub Configuration
     ═══════════════════════════════════════════════════════════════════════════ --}}

<div class="mb-10">
    <h2 class="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-3 mb-5">Hub Configuration</h2>

    @forelse ($hubs as $hub)
        <div class="bg-white rounded-xl border border-gray-200 p-5 mb-4"
             x-data="{ editing: false }">

            {{-- Hub summary row --}}
            <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                        <span class="font-semibold text-gray-900">{{ $hub['name'] }}</span>
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-solar-100 text-solar-700">
                            {{ $hub['hub_type'] }}
                        </span>
                    </div>
                    <p class="text-sm text-gray-500 mt-1">
                        <span class="font-mono">{{ $hub['mac_address'] }}</span>
                        &nbsp;&middot;&nbsp;
                        {{ $hub['email'] }}
                    </p>
                </div>
                <div class="flex items-center gap-2 flex-shrink-0">
                    <button type="button"
                            @click="editing = !editing"
                            class="bg-solar-500 hover:bg-solar-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors">
                        <span x-text="editing ? 'Cancel' : 'Edit'">Edit</span>
                    </button>

                    <form method="POST" action="{{ route('settings.hubs.delete', $hub['id']) }}"
                          onsubmit="return confirm('Remove hub \'{{ addslashes($hub['name']) }}\'? This cannot be undone.')">
                        @csrf
                        @method('DELETE')
                        <button type="submit"
                                class="bg-red-500 hover:bg-red-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors">
                            Delete
                        </button>
                    </form>
                </div>
            </div>

            {{-- Inline edit form --}}
            <div x-show="editing" x-transition class="mt-5 border-t border-gray-100 pt-5">
                <form method="POST" action="{{ route('settings.hubs.update', $hub['id']) }}" class="space-y-4">
                    @csrf
                    @method('PUT')

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
                            <input type="text"
                                   name="name"
                                   value="{{ old('name', $hub['name']) }}"
                                   required
                                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">MAC Address</label>
                            <input type="text"
                                   name="mac_address"
                                   value="{{ old('mac_address', $hub['mac_address']) }}"
                                   required
                                   placeholder="AA:BB:CC:DD:EE:FF"
                                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input type="email"
                                   name="email"
                                   value="{{ old('email', $hub['email']) }}"
                                   required
                                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                New Password
                                <span class="text-gray-400 font-normal">(leave blank to keep current)</span>
                            </label>
                            <input type="password"
                                   name="password"
                                   autocomplete="new-password"
                                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                        </div>
                    </div>

                    <div class="flex justify-end">
                        <button type="submit"
                                class="bg-solar-500 hover:bg-solar-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors">
                            Save Changes
                        </button>
                    </div>
                </form>
            </div>

        </div>
    @empty
        <p class="text-sm text-gray-400 py-4">No hubs configured yet.</p>
    @endforelse
</div>

{{-- ═══════════════════════════════════════════════════════════════════════════
     Section 2: Energy Providers
     ═══════════════════════════════════════════════════════════════════════════ --}}

<div class="mb-10">
    <h2 class="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-3 mb-5">Energy Providers</h2>

    {{-- Existing providers --}}
    @if (count($providers) > 0)
        <div class="space-y-3 mb-6">
            @foreach ($providers as $provider)
                <div class="bg-white rounded-xl border border-gray-200 p-5 flex items-center justify-between gap-4">
                    <div class="flex items-center gap-3">
                        <span class="font-semibold text-gray-900">{{ $provider['name'] }}</span>
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                            @if($provider['provider_type'] === 'solaredge') bg-blue-100 text-blue-700
                            @elseif($provider['provider_type'] === 'mqtt') bg-purple-100 text-purple-700
                            @else bg-solar-100 text-solar-700
                            @endif">
                            {{ $provider['provider_type'] }}
                        </span>
                        @if (isset($provider['is_active']) && $provider['is_active'])
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                active
                            </span>
                        @endif
                    </div>

                    <form method="POST" action="{{ route('settings.providers.delete', $provider['id']) }}"
                          onsubmit="return confirm('Remove provider \'{{ addslashes($provider['name']) }}\'?')">
                        @csrf
                        @method('DELETE')
                        <button type="submit"
                                class="bg-red-500 hover:bg-red-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors">
                            Delete
                        </button>
                    </form>
                </div>
            @endforeach
        </div>
    @else
        <p class="text-sm text-gray-400 mb-6">No energy providers configured yet.</p>
    @endif

    {{-- Add provider form --}}
    <div class="bg-white rounded-xl border border-gray-200 p-5"
         x-data="{ providerType: '{{ old('provider_type', 'kaku_p1') }}' }">

        <h3 class="font-semibold text-gray-800 text-sm mb-4">Add Energy Provider</h3>

        <form method="POST" action="{{ route('settings.providers.add') }}" class="space-y-4">
            @csrf

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Provider Name</label>
                    <input type="text"
                           name="name"
                           value="{{ old('name') }}"
                           required
                           placeholder="e.g. My SolarEdge"
                           class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Provider Type</label>
                    <select name="provider_type"
                            x-model="providerType"
                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent bg-white">
                        <option value="kaku_p1" {{ old('provider_type') === 'kaku_p1' ? 'selected' : '' }}>KaKu P1 (ICS2000)</option>
                        <option value="solaredge" {{ old('provider_type') === 'solaredge' ? 'selected' : '' }}>SolarEdge Cloud API</option>
                        <option value="mqtt" {{ old('provider_type') === 'mqtt' ? 'selected' : '' }}>MQTT</option>
                    </select>
                </div>
            </div>

            {{-- SolarEdge extra fields --}}
            <div x-show="providerType === 'solaredge'" x-transition class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                    <input type="text"
                           name="api_key"
                           value="{{ old('api_key') }}"
                           placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                           class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Site ID</label>
                    <input type="text"
                           name="site_id"
                           value="{{ old('site_id') }}"
                           placeholder="123456"
                           class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                </div>
            </div>

            {{-- MQTT extra fields --}}
            <div x-show="providerType === 'mqtt'" x-transition>
                <label class="block text-sm font-medium text-gray-700 mb-1">MQTT Topic</label>
                <input type="text"
                       name="topic"
                       value="{{ old('topic') }}"
                       placeholder="solar/power"
                       class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
            </div>

            <div class="flex justify-end">
                <button type="submit"
                        class="bg-solar-500 hover:bg-solar-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors">
                    Add Provider
                </button>
            </div>
        </form>
    </div>
</div>

{{-- ═══════════════════════════════════════════════════════════════════════════
     Section 3: General Settings
     ═══════════════════════════════════════════════════════════════════════════ --}}

<div class="mb-10">
    <h2 class="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-3 mb-5">General Settings</h2>

    <div class="bg-white rounded-xl border border-gray-200 p-5">
        <form method="POST" action="{{ route('settings.update') }}" class="flex items-end gap-4 flex-wrap">
            @csrf

            <input type="hidden" name="key" value="poll_interval_seconds">

            <div class="flex-1 min-w-48">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Poll Interval
                    <span class="text-gray-400 font-normal">(seconds)</span>
                </label>
                <input type="number"
                       name="value"
                       value="{{ old('value', $settingsMap['poll_interval_seconds'] ?? 300) }}"
                       min="10"
                       max="3600"
                       required
                       class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
                <p class="text-xs text-gray-400 mt-1">How often the solar engine polls energy data. Minimum 10 s, maximum 3600 s.</p>
            </div>

            <div>
                <button type="submit"
                        class="bg-solar-500 hover:bg-solar-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors">
                    Save
                </button>
            </div>
        </form>
    </div>
</div>

{{-- ═══════════════════════════════════════════════════════════════════════════
     Section 4: Solar Scheduler Status
     ═══════════════════════════════════════════════════════════════════════════ --}}

<div class="mb-10">
    <h2 class="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-3 mb-5">Solar Scheduler Status</h2>

    <div class="bg-solar-50 border border-solar-100 rounded-xl p-5 flex items-start gap-4">
        <svg class="w-5 h-5 text-solar-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/>
        </svg>
        <div class="text-sm text-solar-800">
            <p>
                The solar engine runs every
                <strong>{{ $settingsMap['poll_interval_seconds'] ?? 300 }} seconds</strong>.
            </p>
            @if (! empty($settingsMap['last_run']))
                <p class="mt-1 text-solar-700">
                    Last run:
                    <span class="font-mono">{{ $settingsMap['last_run'] }}</span>
                </p>
            @else
                <p class="mt-1 text-solar-600 opacity-75">Last run: not available yet.</p>
            @endif
        </div>
    </div>
</div>

@endsection
