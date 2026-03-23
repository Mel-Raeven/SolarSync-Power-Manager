@extends('layouts.app')

@section('title', 'Appliances')

@section('content')

<div class="flex items-center justify-between mb-8">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Appliances</h1>
        <p class="mt-1 text-sm text-gray-500">Manage the devices SolarSync controls.</p>
    </div>
    <a href="{{ route('appliances.create') }}"
       class="inline-flex items-center gap-2 bg-solar-500 hover:bg-solar-600 text-white font-semibold
              rounded-lg px-4 py-2.5 text-sm transition-colors duration-150 shadow-sm">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Add appliance
    </a>
</div>

{{-- Flash messages --}}
@if (session('success'))
    <div class="mb-6 flex items-center gap-3 bg-green-50 border border-green-200 rounded-lg px-4 py-3">
        <svg class="w-5 h-5 text-green-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
        </svg>
        <p class="text-sm text-green-700">{{ session('success') }}</p>
    </div>
@endif

@if (session('error'))
    <div class="mb-6 flex items-center gap-3 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
        <svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
        <p class="text-sm text-red-700">{{ session('error') }}</p>
    </div>
@endif

@if (count($appliances) === 0)
    {{-- Empty state --}}
    <div class="text-center py-20 border-2 border-dashed border-gray-200 rounded-xl">
        <svg class="mx-auto w-12 h-12 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/>
        </svg>
        <p class="text-gray-500 font-medium">No appliances yet</p>
        <p class="text-sm text-gray-400 mt-1">Add an appliance to start scheduling.</p>
        <a href="{{ route('appliances.create') }}"
           class="mt-5 inline-flex items-center gap-2 bg-solar-500 hover:bg-solar-600 text-white font-semibold
                  rounded-lg px-4 py-2.5 text-sm transition-colors duration-150 shadow-sm">
            Add appliance
        </a>
    </div>
@else
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Appliance</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Watts</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Schedule</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Priority</th>
                    <th class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                @foreach ($appliances as $appliance)
                @php
                    $scheduleBadge = match($appliance['schedule_mode']) {
                        'solar_only'       => ['bg-green-100 text-green-800',  'Solar only'],
                        'solar_preferred'  => ['bg-amber-100 text-amber-800',  'Solar preferred'],
                        'time_window'      => ['bg-blue-100 text-blue-800',    'Time window'],
                        'manual'           => ['bg-gray-100 text-gray-700',    'Manual'],
                        default            => ['bg-gray-100 text-gray-700',    $appliance['schedule_mode']],
                    };
                    $statusDot = match($appliance['status'] ?? 'idle') {
                        'running'  => 'bg-green-400',
                        'disabled' => 'bg-red-400',
                        default    => 'bg-gray-300',
                    };
                    $statusLabel = match($appliance['status'] ?? 'idle') {
                        'running'  => 'Running',
                        'disabled' => 'Disabled',
                        default    => 'Idle',
                    };
                    $isDisabled = ($appliance['status'] ?? 'idle') === 'disabled';
                @endphp
                <tr class="hover:bg-gray-50 transition-colors duration-100">
                    <td class="px-6 py-4">
                        <span class="font-medium text-gray-900 text-sm">{{ $appliance['name'] }}</span>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-600">
                        {{ number_format($appliance['watt_draw']) }} W
                    </td>
                    <td class="px-6 py-4">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {{ $scheduleBadge[0] }}">
                            {{ $scheduleBadge[1] }}
                        </span>
                    </td>
                    <td class="px-6 py-4">
                        <span class="inline-flex items-center gap-1.5 text-sm text-gray-600">
                            <span class="w-2 h-2 rounded-full {{ $statusDot }}"></span>
                            {{ $statusLabel }}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-600">
                        {{ $appliance['priority'] ?? 1 }}
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex items-center justify-end gap-2">
                            {{-- Edit --}}
                            <a href="{{ route('appliances.edit', $appliance['id']) }}"
                               class="inline-flex items-center gap-1 border border-gray-300 hover:bg-gray-50 text-gray-700
                                      rounded-lg px-3 py-1.5 text-xs font-medium transition-colors duration-100">
                                Edit
                            </a>

                            {{-- Enable / Disable toggle --}}
                            <form method="POST" action="{{ route('appliances.toggle', $appliance['id']) }}">
                                @csrf
                                <button type="submit"
                                        class="inline-flex items-center border text-xs font-medium rounded-lg px-3 py-1.5 transition-colors duration-100
                                               {{ $isDisabled
                                                    ? 'border-green-300 text-green-700 hover:bg-green-50'
                                                    : 'border-gray-300 text-gray-700 hover:bg-gray-50' }}">
                                    {{ $isDisabled ? 'Enable' : 'Disable' }}
                                </button>
                            </form>

                            {{-- Delete --}}
                            <form method="POST" action="{{ route('appliances.destroy', $appliance['id']) }}"
                                  class="delete-form" data-name="{{ $appliance['name'] }}">
                                @csrf
                                @method('DELETE')
                                <button type="submit"
                                        class="inline-flex items-center bg-red-500 hover:bg-red-600 text-white
                                               rounded-lg px-3 py-1.5 text-xs font-medium transition-colors duration-100">
                                    Delete
                                </button>
                            </form>
                        </div>
                    </td>
                </tr>
                @endforeach
            </tbody>
        </table>
    </div>
@endif

<script>
document.querySelectorAll('.delete-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
        var name = form.getAttribute('data-name');
        if (!confirm('Delete "' + name + '"? This cannot be undone.')) {
            e.preventDefault();
        }
    });
});
</script>

@endsection
