<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ApplianceController extends Controller
{
    private string $apiBase;
    private string $apiKey;

    public function __construct()
    {
        $this->apiBase = rtrim(config('services.solarsync.api_base', 'http://backend:8000'), '/');
        $this->apiKey  = config('services.solarsync.internal_api_key', '');
    }

    private function apiClient()
    {
        return Http::withHeaders(['X-Internal-API-Key' => $this->apiKey]);
    }

    // ── Index ─────────────────────────────────────────────────────────────────

    public function index()
    {
        $appliancesResponse = $this->apiClient()->get("{$this->apiBase}/api/appliances");
        $hubsResponse       = $this->apiClient()->get("{$this->apiBase}/api/hubs");

        $appliances = $appliancesResponse->successful() ? $appliancesResponse->json() : [];
        $hubs       = $hubsResponse->successful()       ? $hubsResponse->json()       : [];

        return view('appliances.index', compact('appliances', 'hubs'));
    }

    // ── Create ────────────────────────────────────────────────────────────────

    public function create()
    {
        $hubsResponse = $this->apiClient()->get("{$this->apiBase}/api/hubs");
        $hubs = $hubsResponse->successful() ? $hubsResponse->json() : [];

        return view('appliances.create', compact('hubs'));
    }

    // ── Store ─────────────────────────────────────────────────────────────────

    public function store(Request $request)
    {
        $validated = $request->validate([
            'name'               => ['required', 'string', 'max:100'],
            'watt_draw'          => ['required', 'integer', 'min:1', 'max:100000'],
            'schedule_mode'      => ['required', 'in:solar_only,solar_preferred,time_window,manual'],
            'priority'           => ['nullable', 'integer', 'min:1', 'max:10'],
            'hub_id'             => ['required', 'integer'],
            'plug_id'            => ['required', 'string'],
            'time_window_start'  => ['nullable', 'date_format:H:i', 'required_if:schedule_mode,time_window'],
            'time_window_end'    => ['nullable', 'date_format:H:i', 'required_if:schedule_mode,time_window'],
        ]);

        $response = $this->apiClient()->post("{$this->apiBase}/api/appliances", $validated);

        if ($response->failed()) {
            return redirect()->back()
                ->withInput()
                ->with('error', 'Could not create appliance. Please try again.');
        }

        return redirect()->route('appliances.index')
            ->with('success', 'Appliance added successfully.');
    }

    // ── Edit ──────────────────────────────────────────────────────────────────

    public function edit(int $id)
    {
        $applianceResponse = $this->apiClient()->get("{$this->apiBase}/api/appliances/{$id}");
        $hubsResponse      = $this->apiClient()->get("{$this->apiBase}/api/hubs");

        if ($applianceResponse->failed()) {
            return redirect()->route('appliances.index')
                ->with('error', 'Appliance not found.');
        }

        $appliance = $applianceResponse->json();
        $hubs      = $hubsResponse->successful() ? $hubsResponse->json() : [];

        return view('appliances.edit', compact('appliance', 'hubs'));
    }

    // ── Update ────────────────────────────────────────────────────────────────

    public function update(Request $request, int $id)
    {
        $validated = $request->validate([
            'name'               => ['required', 'string', 'max:100'],
            'watt_draw'          => ['required', 'integer', 'min:1', 'max:100000'],
            'schedule_mode'      => ['required', 'in:solar_only,solar_preferred,time_window,manual'],
            'priority'           => ['nullable', 'integer', 'min:1', 'max:10'],
            'hub_id'             => ['required', 'integer'],
            'plug_id'            => ['required', 'string'],
            'time_window_start'  => ['nullable', 'date_format:H:i', 'required_if:schedule_mode,time_window'],
            'time_window_end'    => ['nullable', 'date_format:H:i', 'required_if:schedule_mode,time_window'],
        ]);

        $response = $this->apiClient()->put("{$this->apiBase}/api/appliances/{$id}", $validated);

        if ($response->failed()) {
            return redirect()->back()
                ->withInput()
                ->with('error', 'Could not update appliance. Please try again.');
        }

        return redirect()->route('appliances.index')
            ->with('success', 'Appliance updated successfully.');
    }

    // ── Destroy ───────────────────────────────────────────────────────────────

    public function destroy(int $id)
    {
        $response = $this->apiClient()->delete("{$this->apiBase}/api/appliances/{$id}");

        if ($response->failed()) {
            return redirect()->route('appliances.index')
                ->with('error', 'Could not delete appliance. Please try again.');
        }

        return redirect()->route('appliances.index')
            ->with('success', 'Appliance deleted.');
    }

    // ── Toggle ────────────────────────────────────────────────────────────────

    public function toggle(int $id)
    {
        $response = $this->apiClient()->post("{$this->apiBase}/api/appliances/{$id}/toggle");

        if ($response->failed()) {
            return redirect()->back()
                ->with('error', 'Could not toggle appliance. Please try again.');
        }

        return redirect()->back()
            ->with('success', 'Appliance updated.');
    }
}
