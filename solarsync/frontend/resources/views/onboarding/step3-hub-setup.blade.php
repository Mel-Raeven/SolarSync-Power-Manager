@extends('layouts.app')

@section('title', 'Hub Setup')

@section('content')

@include('partials.onboarding-progress', ['step' => $step, 'totalSteps' => $totalSteps])

<div class="max-w-xl mx-auto">

    <h1 class="text-2xl font-bold text-gray-900 mb-2">Connect your ICS2000 hub</h1>
    <p class="text-gray-500 mb-8">
        Enter the credentials for your KlikAanKlikUit ICS2000 hub.
        These are the same credentials you use in the KaKu app.
    </p>

    @if ($errors->any())
        <div class="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p class="text-sm font-semibold text-red-700 mb-1">Could not connect to hub</p>
            @foreach ($errors->all() as $error)
                <p class="text-sm text-red-600">{{ $error }}</p>
            @endforeach
        </div>
    @endif

    <form method="POST" action="{{ route('onboarding.step3.submit') }}" class="space-y-5">
        @csrf

        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Hub MAC address</label>
            <input type="text" name="hub_mac" value="{{ old('hub_mac') }}" required
                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-mono
                          focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent"
                   placeholder="AA:BB:CC:DD:EE:FF">
            <p class="mt-1.5 text-xs text-gray-400">Found on the sticker on the bottom of the hub.</p>
        </div>

        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Account e-mail</label>
            <input type="email" name="hub_email" value="{{ old('hub_email') }}" required
                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                          focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent"
                   placeholder="you@example.com">
        </div>

        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input type="password" name="hub_password" required
                   class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm
                          focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent">
            <p class="mt-1.5 text-xs text-gray-400">
                Your KaKu account password. Stored only on this device and never shared.
            </p>
        </div>

        <div class="flex justify-between items-center pt-2">
            <a href="{{ route('onboarding.step2') }}" class="text-sm text-gray-500 hover:text-gray-700">Back</a>
            <button type="submit"
                class="inline-flex items-center gap-2 bg-solar-500 hover:bg-solar-600 text-white font-semibold
                       rounded-lg px-6 py-2.5 text-sm transition-colors duration-150 shadow-sm">
                Connect hub
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/>
                </svg>
            </button>
        </div>

    </form>

</div>

@endsection
