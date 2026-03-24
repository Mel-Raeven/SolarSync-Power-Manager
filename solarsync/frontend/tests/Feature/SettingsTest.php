<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class SettingsTest extends TestCase
{
    use RefreshDatabase;

    private User $user;

    protected function setUp(): void
    {
        parent::setUp();
        $this->user = User::factory()->create();
    }

    // ── Index ─────────────────────────────────────────────────────────────────

    public function test_settings_requires_auth(): void
    {
        $this->get('/settings')->assertRedirect('/login');
    }

    public function test_settings_page_renders(): void
    {
        Http::fake([
            '*/api/hubs'                   => Http::response([], 200),
            '*/api/hubs/energy-providers'  => Http::response([], 200),
            '*/api/settings'               => Http::response([], 200),
        ]);

        $this->actingAs($this->user)
            ->get('/settings')
            ->assertStatus(200);
    }

    // ── Hub update ────────────────────────────────────────────────────────────

    public function test_update_hub_proxies_to_api(): void
    {
        Http::fake(['*/api/hubs/1' => Http::response(['id' => 1], 200)]);

        $this->actingAs($this->user)
            ->put('/settings/hubs/1', [
                'name'        => 'My Hub',
                'mac_address' => 'AA:BB:CC:DD:EE:FF',
                'email'       => 'test@example.com',
            ])
            ->assertRedirect(route('settings.index'))
            ->assertSessionHas('success');
    }

    public function test_update_hub_validates_email(): void
    {
        $this->actingAs($this->user)
            ->put('/settings/hubs/1', [
                'name'        => 'My Hub',
                'mac_address' => 'AA:BB:CC:DD:EE:FF',
                'email'       => 'not-an-email',
            ])
            ->assertSessionHasErrors(['email']);
    }

    public function test_update_hub_requires_name(): void
    {
        $this->actingAs($this->user)
            ->put('/settings/hubs/1', [
                'mac_address' => 'AA:BB:CC:DD:EE:FF',
                'email'       => 'test@example.com',
            ])
            ->assertSessionHasErrors(['name']);
    }

    // ── Hub delete ────────────────────────────────────────────────────────────

    public function test_delete_hub_proxies_to_api(): void
    {
        Http::fake(['*/api/hubs/1' => Http::response(null, 204)]);

        $this->actingAs($this->user)
            ->delete('/settings/hubs/1')
            ->assertRedirect(route('settings.index'))
            ->assertSessionHas('success');
    }

    // ── Energy provider add ───────────────────────────────────────────────────

    public function test_add_energy_provider_solaredge(): void
    {
        Http::fake(['*/api/hubs/energy-providers' => Http::response(['id' => 1], 201)]);

        $this->actingAs($this->user)
            ->post('/settings/energy-providers', [
                'name'          => 'SolarEdge Home',
                'provider_type' => 'solaredge',
                'api_key'       => 'ABC123',
                'site_id'       => '99999',
            ])
            ->assertRedirect(route('settings.index'))
            ->assertSessionHas('success');
    }

    public function test_add_energy_provider_requires_name(): void
    {
        $this->actingAs($this->user)
            ->post('/settings/energy-providers', [
                'provider_type' => 'solaredge',
            ])
            ->assertSessionHasErrors(['name']);
    }

    public function test_add_energy_provider_requires_valid_type(): void
    {
        $this->actingAs($this->user)
            ->post('/settings/energy-providers', [
                'name'          => 'Test',
                'provider_type' => 'unsupported_type',
            ])
            ->assertSessionHasErrors(['provider_type']);
    }

    // ── Energy provider delete ────────────────────────────────────────────────

    public function test_delete_energy_provider(): void
    {
        Http::fake(['*/api/hubs/energy-providers/1' => Http::response(null, 204)]);

        $this->actingAs($this->user)
            ->delete('/settings/energy-providers/1')
            ->assertRedirect(route('settings.index'))
            ->assertSessionHas('success');
    }

    // ── General settings ──────────────────────────────────────────────────────

    public function test_update_setting(): void
    {
        Http::fake(['*/api/settings' => Http::response(['key' => 'poll_interval_seconds', 'value' => '300'], 200)]);

        $this->actingAs($this->user)
            ->post('/settings/setting', [
                'key'   => 'poll_interval_seconds',
                'value' => '300',
            ])
            ->assertRedirect(route('settings.index'))
            ->assertSessionHas('success');
    }

    public function test_update_setting_requires_key(): void
    {
        $this->actingAs($this->user)
            ->post('/settings/setting', ['value' => '300'])
            ->assertSessionHasErrors(['key']);
    }

    public function test_update_setting_requires_value(): void
    {
        $this->actingAs($this->user)
            ->post('/settings/setting', ['key' => 'poll_interval_seconds'])
            ->assertSessionHasErrors(['value']);
    }

    public function test_update_setting_rejects_unknown_key(): void
    {
        $this->actingAs($this->user)
            ->post('/settings/setting', [
                'key'   => 'unknown_key',
                'value' => 'some_value',
            ])
            ->assertSessionHasErrors(['key']);
    }
}
