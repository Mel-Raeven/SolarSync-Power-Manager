@extends('layouts.app')

@section('title', 'Welcome')

@section('content')

@include('partials.onboarding-progress', ['step' => $step, 'totalSteps' => $totalSteps])

<div class="max-w-xl mx-auto text-center">

    <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-solar-100 mb-6">
        <svg class="w-10 h-10 text-solar-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/>
        </svg>
    </div>

    <h1 class="text-3xl font-bold text-gray-900 mb-3">Welcome to SolarSync</h1>
    <p class="text-gray-500 mb-2">
        SolarSync automatically turns on your household appliances — pool pump, EV charger, washing machine —
        when your solar panels are producing more energy than you need.
    </p>
    <p class="text-gray-500 mb-8">
        This wizard takes about 3 minutes. Let's get your system set up.
    </p>

    {{-- System status checks --}}
    <div class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100 text-left mb-8">
        <div class="flex items-center gap-3 px-5 py-3.5">
            <div class="w-2 h-2 rounded-full bg-green-400 flex-shrink-0"></div>
            <span class="text-sm text-gray-700">API backend reachable</span>
        </div>
        <div class="flex items-center gap-3 px-5 py-3.5">
            <div class="w-2 h-2 rounded-full bg-green-400 flex-shrink-0"></div>
            <span class="text-sm text-gray-700">Database available</span>
        </div>
        <div class="flex items-center gap-3 px-5 py-3.5">
            <div class="w-2 h-2 rounded-full bg-green-400 flex-shrink-0"></div>
            <span class="text-sm text-gray-700">MQTT broker running</span>
        </div>
    </div>

    <form method="POST" action="{{ route('onboarding.step1.submit') }}">
        @csrf
        <button type="submit"
            class="inline-flex items-center gap-2 bg-solar-500 hover:bg-solar-600 text-white font-semibold
                   rounded-lg px-8 py-3 text-sm transition-colors duration-150 shadow-sm">
            Get started
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/>
            </svg>
        </button>
    </form>

</div>

@endsection
