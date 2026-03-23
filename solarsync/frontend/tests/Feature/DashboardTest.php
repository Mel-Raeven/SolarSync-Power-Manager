<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class DashboardTest extends TestCase
{
    use RefreshDatabase;

    private User $user;

    protected function setUp(): void
    {
        parent::setUp();
        $this->user = User::factory()->create();
    }

    // ── Index page ────────────────────────────────────────────────────────────

    public function test_dashboard_requires_auth(): void
    {
        $this->get('/dashboard')->assertRedirect('/login');
    }

    public function test_dashboard_renders_with_api_data(): void
    {
        Http::fake([
            '*/api/power/status'   => Http::response([
                'solar_production_w' => 2500,
                'grid_draw_w'        => 0,
                'surplus_w'          => 2500,
            ], 200),
            '*/api/appliances'     => Http::response([
                [
                    'id'            => 1,
                    'name'          => 'Pool Pump',
                    'status'        => 'running',
                    'watt_draw'     => 750,
                    'schedule_mode' => 'solar_only',
                    'override_on'   => false,
                ],
            ], 200),
            '*/api/power/history*' => Http::response([], 200),
        ]);

        $this->actingAs($this->user)
            ->get('/dashboard')
            ->assertStatus(200)
            ->assertSee('Pool Pump');
    }

    public function test_dashboard_graceful_when_api_fails(): void
    {
        Http::fake([
            '*/api/power/status'   => Http::response(null, 503),
            '*/api/appliances'     => Http::response(null, 503),
            '*/api/power/history*' => Http::response(null, 503),
        ]);

        // Should still render (gracefully degrades)
        $this->actingAs($this->user)
            ->get('/dashboard')
            ->assertStatus(200);
    }

    // ── Status JSON endpoint ──────────────────────────────────────────────────

    public function test_status_returns_json_from_api(): void
    {
        Http::fake([
            '*/api/power/status' => Http::response([
                'solar_production_w' => 1000,
                'grid_draw_w'        => 200,
                'surplus_w'          => 800,
                'timestamp'          => '2026-03-23T12:00:00',
            ], 200),
        ]);

        $this->actingAs($this->user)
            ->get('/dashboard/status')
            ->assertStatus(200)
            ->assertJson(['solar_production_w' => 1000]);
    }

    public function test_status_returns_nulls_when_api_fails(): void
    {
        Http::fake([
            '*/api/power/status' => Http::response(null, 502),
        ]);

        $response = $this->actingAs($this->user)->get('/dashboard/status');
        $response->assertStatus(200);
        $response->assertJson(['solar_production_w' => null]);
    }

    // ── Override endpoint ─────────────────────────────────────────────────────

    public function test_override_proxies_to_api_and_returns_json(): void
    {
        Http::fake([
            '*/api/appliances/1/override' => Http::response(['id' => 1, 'status' => 'override_on'], 200),
        ]);

        $this->actingAs($this->user)
            ->post('/appliances/1/override', ['override_on' => true])
            ->assertStatus(200)
            ->assertJson(['status' => 'override_on']);
    }

    public function test_override_returns_502_when_api_fails(): void
    {
        Http::fake([
            '*/api/appliances/1/override' => Http::response(null, 500),
        ]);

        $this->actingAs($this->user)
            ->post('/appliances/1/override', ['override_on' => false])
            ->assertStatus(502);
    }
}
