<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class DashboardController extends Controller
{
    private string $apiBase;

    public function __construct()
    {
        $this->apiBase = rtrim(config('services.solarsync.api_base', 'http://backend:8000'), '/');
    }

    public function index()
    {
        // Fetch power status
        $statusResponse = Http::timeout(5)->get("{$this->apiBase}/api/power/status");
        $powerStatus = $statusResponse->successful() ? $statusResponse->json() : null;

        // Fetch appliances
        $appliancesResponse = Http::timeout(5)->get("{$this->apiBase}/api/appliances");
        $appliances = $appliancesResponse->successful() ? ($appliancesResponse->json() ?? []) : [];

        // Fetch 24h history for chart
        $historyResponse = Http::timeout(5)->get("{$this->apiBase}/api/power/history", ['hours' => 24]);
        $history = $historyResponse->successful() ? ($historyResponse->json() ?? []) : [];

        return view('dashboard', [
            'solarProduction' => $powerStatus['solar_production_w'] ?? null,
            'gridDraw'        => $powerStatus['grid_draw_w'] ?? null,
            'surplus'         => $powerStatus['surplus_w'] ?? null,
            'appliances'      => $appliances,
            'chartData'       => $this->buildChartData($history),
        ]);
    }

    public function status()
    {
        $response = Http::timeout(5)->get("{$this->apiBase}/api/power/status");

        if ($response->successful()) {
            return response()->json($response->json());
        }

        return response()->json([
            'solar_production_w' => null,
            'grid_draw_w'        => null,
            'surplus_w'          => null,
            'timestamp'          => null,
        ]);
    }

    public function override(Request $request, int $id)
    {
        $validated = $request->validate([
            'override_on' => ['nullable', 'boolean'],
        ]);

        $response = Http::timeout(5)->post(
            "{$this->apiBase}/api/appliances/{$id}/override",
            ['override_on' => $validated['override_on'] ?? null]
        );

        if ($response->successful()) {
            return response()->json($response->json());
        }

        return response()->json(['error' => 'Failed to update override'], 502);
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function buildChartData(array $history): array
    {
        $labels = [];
        $solar  = [];
        $grid   = [];
        $surplus = [];

        foreach ($history as $point) {
            // Format timestamp to HH:MM for readability
            $ts = $point['timestamp'] ?? '';
            try {
                $labels[] = (new \DateTime($ts))->format('H:i');
            } catch (\Exception) {
                $labels[] = $ts;
            }
            $solar[]   = $point['solar_production_w'] ?? 0;
            $grid[]    = $point['grid_draw_w'] ?? 0;
            $surplus[] = $point['surplus_w'] ?? 0;
        }

        return compact('labels', 'solar', 'grid', 'surplus');
    }
}
