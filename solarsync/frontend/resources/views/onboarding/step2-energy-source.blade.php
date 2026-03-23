@extends('layouts.app')

@section('title', 'Energy Source')

@section('content')

@include('partials.onboarding-progress', ['step' => $step, 'totalSteps' => $totalSteps])

<div class="max-w-xl mx-auto">

    <h1 class="text-2xl font-bold text-gray-900 mb-2">Choose your energy source</h1>
    <p class="text-gray-500 mb-8">
        SolarSync needs to read your current solar surplus. Select how your system reports it.
    </p>

    <form method="POST" action="{{ route('onboarding.step2.submit') }}" x-data="{ source: '{{ old('energy_source', 'kaku_p1') }}' }">
        @csrf

        {{-- Source options --}}
        <div class="space-y-3 mb-8">

            {{-- KaKu P1 --}}
            <label class="flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-colors
                          :class="{ 'border-solar-500 bg-solar-50': source === 'kaku_p1', 'border-gray-200 bg-white': source !== 'kaku_p1' }"
                   x-on:click="source = 'kaku_p1'">
                <input type="radio" name="energy_source" value="kaku_p1"
                       class="mt-0.5 text-solar-500 focus:ring-solar-400"
                       x-bind:checked="source === 'kaku_p1'" {{ old('energy_source') === 'kaku_p1' || ! old('energy_source') ? 'checked' : '' }}>
                <div>
                    <div class="font-semibold text-gray-900 text-sm">KlikAanKlikUit P1 (ICS2000)</div>
                    <div class="text-sm text-gray-500 mt-0.5">
                        Reads surplus from the KaKu ICS2000 P1 energy module connected to your smart meter.
                    </div>
                </div>
            </label>

            {{-- SolarEdge --}}
            <label class="flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-colors
                          :class="{ 'border-solar-500 bg-solar-50': source === 'solaredge', 'border-gray-200 bg-white': source !== 'solaredge' }"
                   x-on:click="source = 'solaredge'">
                <input type="radio" name="energy_source" value="solaredge"
                       class="mt-0.5 text-solar-500 focus:ring-solar-400"
                       x-bind:checked="source === 'solaredge'" {{ old('energy_source') === 'solaredge' ? 'checked' : '' }}>
                <div>
                    <div class="font-semibold text-gray-900 text-sm">SolarEdge Cloud API</div>
                    <div class="text-sm text-gray-500 mt-0.5">
                        Reads production from the SolarEdge monitoring portal using your API key and site ID.
                    </div>
                </div>
            </label>

            {{-- Both --}}
            <label class="flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-colors
                          :class="{ 'border-solar-500 bg-solar-50': source === 'both', 'border-gray-200 bg-white': source !== 'both' }"
                   x-on:click="source = 'both'">
                <input type="radio" name="energy_source" value="both"
                       class="mt-0.5 text-solar-500 focus:ring-solar-400"
                       x-bind:checked="source === 'both'" {{ old('energy_source') === 'both' ? 'checked' : '' }}>
                <div>
                    <div class="font-semibold text-gray-900 text-sm">Both (P1 for surplus + SolarEdge for production)</div>
                    <div class="text-sm text-gray-500 mt-0.5">
                        Uses P1 net surplus for decisions and SolarEdge for production figures on the dashboard.
                    </div>
                </div>
            </label>

        </div>

        {{-- SolarEdge credentials (shown when solaredge or both) --}}
        <div x-show="source === 'solaredge' || source === 'both'"
             x-transition
             class="bg-white rounded-xl border border-gray-200 p-5 mb-8 space-y-4">

            <h3 class="font-semibold text-gray-800 text-sm">SolarEdge credentials</h3>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                <input type="text" name="solaredge_api_key" value="{{ old('solaredge_api_key') }}"
                       class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                              focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent"
                       placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx">
                @error('solaredge_api_key')
                    <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                @enderror
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Site ID</label>
                <input type="text" name="solaredge_site_id" value="{{ old('solaredge_site_id') }}"
                       class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                              focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent"
                       placeholder="123456">
                @error('solaredge_site_id')
                    <p class="mt-1 text-sm text-red-600">{{ $message }}</p>
                @enderror
            </div>

        </div>

        <div class="flex justify-between items-center">
            <a href="{{ route('onboarding.step1') }}" class="text-sm text-gray-500 hover:text-gray-700">Back</a>
            <button type="submit"
                class="inline-flex items-center gap-2 bg-solar-500 hover:bg-solar-600 text-white font-semibold
                       rounded-lg px-6 py-2.5 text-sm transition-colors duration-150 shadow-sm">
                Continue
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/>
                </svg>
            </button>
        </div>

    </form>

</div>

{{-- Alpine.js for reactive radio toggle --}}
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>

@endsection
