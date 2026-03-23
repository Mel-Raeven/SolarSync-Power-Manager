<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class SettingsController extends Controller
{
    private string $apiBase;

    public function __construct()
    {
        $this->apiBase = rtrim(config('services.solarsync.api_base', 'http://backend:8000'), '/');
    }

    // ── Page ──────────────────────────────────────────────────────────────────

    public function index()
    {
        $hubsResponse      = Http::timeout(5)->get("{$this->apiBase}/api/hubs");
        $providersResponse = Http::timeout(5)->get("{$this->apiBase}/api/hubs/energy-providers");
        $settingsResponse  = Http::timeout(5)->get("{$this->apiBase}/api/settings");

        $hubs      = $hubsResponse->successful()      ? ($hubsResponse->json()      ?? []) : [];
        $providers = $providersResponse->successful() ? ($providersResponse->json() ?? []) : [];
        $settings  = $settingsResponse->successful()  ? ($settingsResponse->json()  ?? []) : [];

        // Convert settings array to key-value map for easy access in the view
        $settingsMap = [];
        foreach ($settings as $setting) {
            $settingsMap[$setting['key']] = $setting['value'];
        }

        return view('settings', [
            'hubs'        => $hubs,
            'providers'   => $providers,
            'settingsMap' => $settingsMap,
        ]);
    }

    // ── Hubs ──────────────────────────────────────────────────────────────────

    public function updateHub(Request $request, int $id)
    {
        $validated = $request->validate([
            'name'        => ['required', 'string', 'max:100'],
            'mac_address' => ['required', 'string', 'max:17'],
            'email'       => ['required', 'email'],
            'password'    => ['nullable', 'string', 'min:4'],
        ]);

        $payload = [
            'name'        => $validated['name'],
            'mac_address' => $validated['mac_address'],
            'email'       => $validated['email'],
        ];

        if (! empty($validated['password'])) {
            $payload['password_hash'] = $validated['password'];
        }

        Http::timeout(5)->put("{$this->apiBase}/api/hubs/{$id}", $payload);

        return redirect()->route('settings.index')->with('success', 'Hub updated successfully.');
    }

    public function deleteHub(int $id)
    {
        Http::timeout(5)->delete("{$this->apiBase}/api/hubs/{$id}");

        return redirect()->route('settings.index')->with('success', 'Hub removed.');
    }

    // ── Energy providers ──────────────────────────────────────────────────────

    public function addEnergyProvider(Request $request)
    {
        $validated = $request->validate([
            'name'          => ['required', 'string', 'max:100'],
            'provider_type' => ['required', 'in:kaku_p1,solaredge,mqtt'],
            // SolarEdge extra fields
            'api_key'       => ['nullable', 'string'],
            'site_id'       => ['nullable', 'string'],
            // MQTT extra fields
            'topic'         => ['nullable', 'string'],
        ]);

        $config = [];

        if ($validated['provider_type'] === 'solaredge') {
            $config['api_key'] = $validated['api_key'] ?? '';
            $config['site_id'] = $validated['site_id'] ?? '';
        } elseif ($validated['provider_type'] === 'mqtt') {
            $config['topic'] = $validated['topic'] ?? '';
        }

        Http::timeout(5)->post("{$this->apiBase}/api/hubs/energy-providers", [
            'name'          => $validated['name'],
            'provider_type' => $validated['provider_type'],
            'config'        => $config,
        ]);

        return redirect()->route('settings.index')->with('success', 'Energy provider added.');
    }

    public function deleteEnergyProvider(int $id)
    {
        Http::timeout(5)->delete("{$this->apiBase}/api/hubs/energy-providers/{$id}");

        return redirect()->route('settings.index')->with('success', 'Energy provider removed.');
    }

    // ── General settings ──────────────────────────────────────────────────────

    public function updateSetting(Request $request)
    {
        $validated = $request->validate([
            'key'   => ['required', 'string', 'max:100'],
            'value' => ['required', 'string'],
        ]);

        Http::timeout(5)->post("{$this->apiBase}/api/settings", [
            'key'   => $validated['key'],
            'value' => $validated['value'],
        ]);

        return redirect()->route('settings.index')->with('success', 'Setting saved.');
    }
}
