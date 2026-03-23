{{-- Onboarding progress stepper --}}
{{-- Usage: @include('partials.onboarding-progress', ['step' => 2, 'totalSteps' => 4]) --}}

@php
$steps = [
    1 => 'Welcome',
    2 => 'Energy Source',
    3 => 'Hub Setup',
    4 => 'First Appliance',
];
@endphp

<div class="mb-10">
    <div class="flex items-center justify-between">
        @foreach ($steps as $num => $label)
            @php
                $isComplete = $num < $step;
                $isCurrent  = $num === $step;
                $isPending  = $num > $step;
            @endphp

            {{-- Step circle + label --}}
            <div class="flex flex-col items-center flex-1 {{ $loop->last ? '' : 'relative' }}">
                {{-- Connector line (before the circle except first) --}}
                @if (! $loop->first)
                    <div class="absolute top-4 right-1/2 h-0.5 w-full
                        {{ $isComplete || $isCurrent ? 'bg-solar-400' : 'bg-gray-200' }}
                        -translate-y-1/2 -z-10"></div>
                @endif

                <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold z-10
                    {{ $isComplete ? 'bg-solar-500 text-white' :
                       ($isCurrent ? 'bg-solar-500 text-white ring-4 ring-solar-100' :
                       'bg-gray-200 text-gray-500') }}">
                    @if ($isComplete)
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                        </svg>
                    @else
                        {{ $num }}
                    @endif
                </div>

                <span class="mt-2 text-xs text-center
                    {{ $isCurrent ? 'text-solar-700 font-semibold' :
                       ($isComplete ? 'text-gray-500' : 'text-gray-400') }}">
                    {{ $label }}
                </span>
            </div>
        @endforeach
    </div>
</div>
