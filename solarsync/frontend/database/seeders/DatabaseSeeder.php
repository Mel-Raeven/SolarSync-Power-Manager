<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the default admin user.
     *
     * Credentials are intentionally admin/admin with must_change_password=true.
     * The user is forced to set their own password on first login before they
     * can access anything else in the application.
     */
    public function run(): void
    {
        User::updateOrCreate(
            ['name' => 'admin'],
            [
                'name'                 => 'admin',
                'email'                => 'admin@solarsync.local',
                'password'             => Hash::make('admin'),
                'must_change_password' => true,
            ]
        );
    }
}
