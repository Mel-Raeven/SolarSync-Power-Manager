<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class OnboardingController extends Controller
{
    private string $apiBase;

    public function __construct()
    {
        $this->apiBase = rtrim(config('services.solarsync.api_base', 'http://backend:8000'), '/');
    }

    // ── Step routing ─────────────────────────────────────────────────────────

    public function index()
    {
        $state = $this->getOnboardingState();

        return match (true) {
            ! $state['completed'] && $state['current_step'] === 1 => redirect()->route('onboarding.step1'),
            ! $state['completed'] && $state['current_step'] === 2 => redirect()->route('onboarding.step2'),
            ! $state['completed'] && $state['current_step'] === 3 => redirect()->route('onboarding.step3'),
            ! $state['completed'] && $state['current_step'] === 4 => redirect()->route('onboarding.step4'),
            default => redirect()->route('dashboard'),
        };
    }

    // ── Step 1: Welcome ───────────────────────────────────────────────────────

    public function step1()
    {
        return view('onboarding.step1-welcome', [
            'step' => 1,
            'totalSteps' => 4,
        ]);
    }

    public function step1Submit(Request $request)
    {
        $this->completeStep(1);

        return redirect()->route('onboarding.step2');
    }

    // ── Step 2: Energy source ─────────────────────────────────────────────────

    public function step2()
    {
        return view('onboarding.step2-energy-source', [
            'step' => 2,
            'totalSteps' => 4,
        ]);
    }

    public function step2Submit(Request $request)
    {
        $validated = $request->validate([
            'energy_source' => ['required', 'in:kaku_p1,solaredge,both'],
            // SolarEdge fields (conditional)
            'solaredge_api_key' => ['required_if:energy_source,solaredge,both', 'nullable', 'string'],
            'solaredge_site_id' => ['required_if:energy_source,solaredge,both', 'nullable', 'string'],
        ]);

        // Persist settings to API
        Http::post("{$this->apiBase}/api/settings", [
            'key' => 'energy_source',
            'value' => $validated['energy_source'],
        ]);

        if (! empty($validated['solaredge_api_key'])) {
            Http::post("{$this->apiBase}/api/settings", [
                'key' => 'solaredge_api_key',
                'value' => $validated['solaredge_api_key'],
            ]);
            Http::post("{$this->apiBase}/api/settings", [
                'key' => 'solaredge_site_id',
                'value' => $validated['solaredge_site_id'],
            ]);
        }

        $this->completeStep(2);

        return redirect()->route('onboarding.step3');
    }

    // ── Step 3: Hub setup + plug discovery ────────────────────────────────────

    public function step3()
    {
        return view('onboarding.step3-hub-setup', [
            'step' => 3,
            'totalSteps' => 4,
        ]);
    }

    public function step3Submit(Request $request)
    {
        $validated = $request->validate([
            'hub_mac'   => ['required', 'string'],
            'hub_email' => ['required', 'email'],
            'hub_password' => ['required', 'string'],
        ]);

        // Create hub via API
        $response = Http::post("{$this->apiBase}/api/hubs", [
            'name'         => 'ICS2000',
            'hub_type'     => 'ics2000',
            'mac_address'  => $validated['hub_mac'],
            'email'        => $validated['hub_email'],
            'password_hash' => $validated['hub_password'],
        ]);

        if ($response->failed()) {
            return back()->withErrors(['hub_mac' => 'Could not connect to hub. Please check your credentials.'])->withInput();
        }

        $this->completeStep(3);

        return redirect()->route('onboarding.step4')->with('hub_id', $response->json('id'));
    }

    public function discoverPlugs(Request $request)
    {
        $hubId = $request->input('hub_id');
        $plugs = Http::get("{$this->apiBase}/api/hubs/{$hubId}/plugs")->json();

        return response()->json($plugs);
    }

    // ── Step 4: First appliance ───────────────────────────────────────────────

    public function step4()
    {
        // Fetch hubs so user can select one for plug assignment
        $hubs = Http::get("{$this->apiBase}/api/hubs")->json() ?? [];

        return view('onboarding.step4-first-appliance', [
            'step' => 4,
            'totalSteps' => 4,
            'hubs' => $hubs,
        ]);
    }

    public function step4Submit(Request $request)
    {
        $validated = $request->validate([
            'name'          => ['required', 'string', 'max:100'],
            'watt_draw'     => ['required', 'integer', 'min:1', 'max:100000'],
            'schedule_mode' => ['required', 'in:solar_only,solar_preferred,time_window,manual'],
            'plug_id'       => ['required', 'string'],
            'hub_id'        => ['required', 'integer'],
            'time_window_start' => ['nullable', 'date_format:H:i'],
            'time_window_end'   => ['nullable', 'date_format:H:i'],
            'priority'      => ['nullable', 'integer', 'min:1', 'max:10'],
        ]);

        Http::post("{$this->apiBase}/api/appliances", $validated);

        $this->completeStep(4);

        return redirect()->route('dashboard')->with('success', 'Setup complete! SolarSync is now running.');
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function getOnboardingState(): array
    {
        $response = Http::get("{$this->apiBase}/api/onboarding");

        if ($response->successful()) {
            return $response->json();
        }

        return ['completed' => false, 'current_step' => 1];
    }

    private function completeStep(int $step): void
    {
        Http::post("{$this->apiBase}/api/onboarding/step/{$step}/complete");
    }
}
