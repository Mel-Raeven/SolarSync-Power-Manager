@extends('layouts.app')

@section('title', 'Add Appliance')

@section('content')

<div class="max-w-xl mx-auto">

    <div class="mb-8">
        <a href="{{ route('appliances.index') }}"
           class="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
            </svg>
            Back to appliances
        </a>
        <h1 class="mt-3 text-2xl font-bold text-gray-900">Add appliance</h1>
        <p class="mt-1 text-sm text-gray-500">Connect a new device to SolarSync.</p>
    </div>

    @if (session('error'))
        <div class="mb-6 flex items-center gap-3 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
            <svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
            <p class="text-sm text-red-700">{{ session('error') }}</p>
        </div>
    @endif

    @if ($errors->any())
        <div class="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 space-y-1">
            @foreach ($errors->all() as $error)
                <p class="text-sm text-red-600">{{ $error }}</p>
            @endforeach
        </div>
    @endif

    <form method="POST" action="{{ route('appliances.store') }}">
        @csrf
        @include('appliances._form', ['appliance' => null])
    </form>

</div>

<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>

@endsection
