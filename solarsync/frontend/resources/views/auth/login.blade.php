@extends('layouts.app')

@section('title', 'Login')

@section('main-class', 'min-h-screen flex items-center justify-center bg-gray-50')

@section('content')
<div class="w-full max-w-sm">

    {{-- Logo --}}
    <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-solar-100 mb-4">
            <svg class="w-8 h-8 text-solar-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round"
                      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/>
            </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">SolarSync</h1>
        <p class="text-sm text-gray-500 mt-1">Power Manager</p>
    </div>

    {{-- Card --}}
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
        <h2 class="text-lg font-semibold text-gray-900 mb-6">Sign in</h2>

        <form method="POST" action="{{ route('login.submit') }}" class="space-y-5">
            @csrf

            <div>
                <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input
                    type="text"
                    id="username"
                    name="username"
                    value="{{ old('username') }}"
                    required
                    autofocus
                    class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm shadow-sm
                           focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent
                           @error('username') border-red-400 @enderror"
                    placeholder="admin"
                >
                @error('username')
                    <p class="mt-1.5 text-sm text-red-600">{{ $message }}</p>
                @enderror
            </div>

            <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input
                    type="password"
                    id="password"
                    name="password"
                    required
                    class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm shadow-sm
                           focus:outline-none focus:ring-2 focus:ring-solar-500 focus:border-transparent"
                >
            </div>

            <div class="flex items-center gap-2">
                <input type="checkbox" name="remember" id="remember" class="rounded border-gray-300 text-solar-600">
                <label for="remember" class="text-sm text-gray-600">Remember me</label>
            </div>

            <button type="submit"
                class="w-full bg-solar-500 hover:bg-solar-600 text-white font-semibold rounded-lg px-4 py-2.5 text-sm
                       transition-colors duration-150 shadow-sm">
                Sign in
            </button>
        </form>
    </div>

</div>
@endsection
