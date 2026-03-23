<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class ApplianceTest extends TestCase
{
    use RefreshDatabase;

    private User $user;

    protected function setUp(): void
    {
        parent::setUp();
        $this->user = User::factory()->create();
    }

    private function fakeAppliance(array $overrides = []): array
    {
        return array_merge([
            'id'            => 1,
            'name'          => 'Pool Pump',
            'watt_draw'     => 750,
            'schedule_mode' => 'solar_only',
            'priority'      => 3,
            'status'        => 'idle',
            'is_enabled'    => true,
            'hub_id'        => 1,
            'plug_entity_id' => '42',
        ], $overrides);
    }

    // ── Index ─────────────────────────────────────────────────────────────────

    public function test_index_requires_auth(): void
    {
        $this->get('/appliances')->assertRedirect('/login');
    }

    public function test_index_lists_appliances(): void
    {
        Http::fake([
            '*/api/appliances' => Http::response([$this->fakeAppliance()], 200),
            '*/api/hubs'       => Http::response([], 200),
        ]);

        $this->actingAs($this->user)
            ->get('/appliances')
            ->assertStatus(200)
            ->assertSee('Pool Pump');
    }

    // ── Create ────────────────────────────────────────────────────────────────

    public function test_create_page_loads(): void
    {
        Http::fake(['*/api/hubs' => Http::response([], 200)]);

        $this->actingAs($this->user)
            ->get('/appliances/create')
            ->assertStatus(200);
    }

    public function test_store_valid_appliance(): void
    {
        Http::fake([
            '*/api/appliances' => Http::response($this->fakeAppliance(), 201),
        ]);

        $this->actingAs($this->user)
            ->post('/appliances', [
                'name'          => 'Pool Pump',
                'watt_draw'     => 750,
                'schedule_mode' => 'solar_only',
                'priority'      => 3,
                'hub_id'        => 1,
                'plug_id'       => '42',
            ])
            ->assertRedirect(route('appliances.index'))
            ->assertSessionHas('success');
    }

    public function test_store_requires_name(): void
    {
        $this->actingAs($this->user)
            ->post('/appliances', [
                'watt_draw'     => 750,
                'schedule_mode' => 'solar_only',
                'hub_id'        => 1,
                'plug_id'       => '42',
            ])
            ->assertSessionHasErrors(['name']);
    }

    public function test_store_requires_valid_watt_draw(): void
    {
        $this->actingAs($this->user)
            ->post('/appliances', [
                'name'          => 'Pump',
                'watt_draw'     => 0,   // invalid: min 1
                'schedule_mode' => 'solar_only',
                'hub_id'        => 1,
                'plug_id'       => '42',
            ])
            ->assertSessionHasErrors(['watt_draw']);
    }

    public function test_store_requires_valid_schedule_mode(): void
    {
        $this->actingAs($this->user)
            ->post('/appliances', [
                'name'          => 'Pump',
                'watt_draw'     => 750,
                'schedule_mode' => 'invalid_mode',
                'hub_id'        => 1,
                'plug_id'       => '42',
            ])
            ->assertSessionHasErrors(['schedule_mode']);
    }

    public function test_store_time_window_required_when_mode_is_time_window(): void
    {
        $this->actingAs($this->user)
            ->post('/appliances', [
                'name'          => 'Pump',
                'watt_draw'     => 750,
                'schedule_mode' => 'time_window',
                'hub_id'        => 1,
                'plug_id'       => '42',
                // time_window_start and _end deliberately missing
            ])
            ->assertSessionHasErrors(['time_window_start', 'time_window_end']);
    }

    public function test_store_shows_error_when_api_fails(): void
    {
        Http::fake(['*/api/appliances' => Http::response(null, 500)]);

        $this->actingAs($this->user)
            ->post('/appliances', [
                'name'          => 'Pump',
                'watt_draw'     => 750,
                'schedule_mode' => 'solar_only',
                'hub_id'        => 1,
                'plug_id'       => '42',
            ])
            ->assertRedirect()
            ->assertSessionHas('error');
    }

    // ── Edit / Update ─────────────────────────────────────────────────────────

    public function test_edit_page_loads(): void
    {
        Http::fake([
            '*/api/appliances/1' => Http::response($this->fakeAppliance(), 200),
            '*/api/hubs'         => Http::response([], 200),
        ]);

        $this->actingAs($this->user)
            ->get('/appliances/1/edit')
            ->assertStatus(200)
            ->assertSee('Pool Pump');
    }

    public function test_edit_redirects_when_appliance_not_found(): void
    {
        Http::fake([
            '*/api/appliances/999' => Http::response(null, 404),
            '*/api/hubs'           => Http::response([], 200),
        ]);

        $this->actingAs($this->user)
            ->get('/appliances/999/edit')
            ->assertRedirect(route('appliances.index'))
            ->assertSessionHas('error');
    }

    public function test_update_valid_appliance(): void
    {
        Http::fake([
            '*/api/appliances/1' => Http::response($this->fakeAppliance(['name' => 'Updated']), 200),
        ]);

        $this->actingAs($this->user)
            ->put('/appliances/1', [
                'name'          => 'Updated',
                'watt_draw'     => 750,
                'schedule_mode' => 'solar_only',
                'hub_id'        => 1,
                'plug_id'       => '42',
            ])
            ->assertRedirect(route('appliances.index'))
            ->assertSessionHas('success');
    }

    // ── Delete ────────────────────────────────────────────────────────────────

    public function test_destroy_appliance(): void
    {
        Http::fake(['*/api/appliances/1' => Http::response(null, 204)]);

        $this->actingAs($this->user)
            ->delete('/appliances/1')
            ->assertRedirect(route('appliances.index'))
            ->assertSessionHas('success');
    }

    public function test_destroy_shows_error_when_api_fails(): void
    {
        Http::fake(['*/api/appliances/1' => Http::response(null, 500)]);

        $this->actingAs($this->user)
            ->delete('/appliances/1')
            ->assertRedirect()
            ->assertSessionHas('error');
    }

    // ── Toggle ────────────────────────────────────────────────────────────────

    public function test_toggle_appliance(): void
    {
        Http::fake(['*/api/appliances/1/toggle' => Http::response($this->fakeAppliance(), 200)]);

        $this->actingAs($this->user)
            ->post('/appliances/1/toggle')
            ->assertRedirect()
            ->assertSessionHas('success');
    }
}
