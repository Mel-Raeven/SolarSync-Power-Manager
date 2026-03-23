<!DOCTYPE html>
<html lang="en" class="h-full bg-gray-50">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'SolarSync') — SolarSync Power Manager</title>

    {{-- Tailwind CDN (replaced by Vite build in production) --}}
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        solar: {
                            50:  '#fffbeb',
                            100: '#fef3c7',
                            400: '#fbbf24',
                            500: '#f59e0b',
                            600: '#d97706',
                            700: '#b45309',
                        }
                    }
                }
            }
        }
    </script>
</head>
<body class="h-full">

    {{-- Top nav (only shown when logged in) --}}
    @auth
    <nav class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-14 items-center">
                <a href="{{ route('home') }}" class="flex items-center gap-2 font-semibold text-solar-700 text-lg">
                    <svg class="w-6 h-6 text-solar-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round"
                              d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/>
                    </svg>
                    SolarSync
                </a>

                <div class="flex items-center gap-4">
                    <a href="{{ route('dashboard') }}" class="text-sm text-gray-600 hover:text-gray-900">Dashboard</a>
                    <a href="{{ route('settings.index') }}" class="text-sm text-gray-600 hover:text-gray-900">Settings</a>
                    <form method="POST" action="{{ route('logout') }}">
                        @csrf
                        <button type="submit" class="text-sm text-gray-500 hover:text-red-600">Logout</button>
                    </form>
                </div>
            </div>
        </div>
    </nav>
    @endauth

    <main class="@yield('main-class', 'max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10')">
        @yield('content')
    </main>

    @yield('scripts')

</body>
</html>
