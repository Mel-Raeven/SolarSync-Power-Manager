<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AuthTest extends TestCase
{
    use RefreshDatabase;

    // ── Login page ────────────────────────────────────────────────────────────

    public function test_login_page_is_accessible(): void
    {
        $response = $this->get('/login');
        $response->assertStatus(200);
        $response->assertSee('Login');
    }

    public function test_authenticated_user_is_redirected_from_login(): void
    {
        $user = User::factory()->create();
        $response = $this->actingAs($user)->get('/login');
        $response->assertRedirect(route('dashboard'));
    }

    // ── Login submission ──────────────────────────────────────────────────────

    public function test_user_can_login_with_valid_credentials(): void
    {
        $user = User::factory()->create([
            'name'     => 'admin',
            'password' => bcrypt('secret'),
        ]);

        $response = $this->post('/login', [
            'username' => 'admin',
            'password' => 'secret',
        ]);

        $response->assertRedirect(route('dashboard'));
        $this->assertAuthenticatedAs($user);
    }

    public function test_login_fails_with_wrong_password(): void
    {
        User::factory()->create([
            'name'     => 'admin',
            'password' => bcrypt('secret'),
        ]);

        $response = $this->post('/login', [
            'username' => 'admin',
            'password' => 'wrong',
        ]);

        $response->assertSessionHasErrors(['username']);
        $this->assertGuest();
    }

    public function test_login_fails_with_unknown_username(): void
    {
        $response = $this->post('/login', [
            'username' => 'nobody',
            'password' => 'anything',
        ]);

        $response->assertSessionHasErrors(['username']);
        $this->assertGuest();
    }

    public function test_login_requires_username(): void
    {
        $response = $this->post('/login', ['password' => 'secret']);
        $response->assertSessionHasErrors(['username']);
    }

    public function test_login_requires_password(): void
    {
        $response = $this->post('/login', ['username' => 'admin']);
        $response->assertSessionHasErrors(['password']);
    }

    // ── Logout ────────────────────────────────────────────────────────────────

    public function test_authenticated_user_can_logout(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user);

        $response = $this->post('/logout');
        $response->assertRedirect(route('login'));
        $this->assertGuest();
    }

    // ── Auth middleware ───────────────────────────────────────────────────────

    public function test_unauthenticated_user_redirected_to_login(): void
    {
        $this->get('/dashboard')->assertRedirect('/login');
        $this->get('/appliances')->assertRedirect('/login');
        $this->get('/settings')->assertRedirect('/login');
    }
}
