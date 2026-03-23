<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    /**
     * Create the single household user from environment variables.
     *
     * SOLARSYNC_USERNAME and SOLARSYNC_PASSWORD must be set in .env
     * before running migrations+seed on first boot.
     */
    public function run(): void
    {
        $username = env('SOLARSYNC_USERNAME', 'admin');
        $password = env('SOLARSYNC_PASSWORD', 'changeme');

        User::updateOrCreate(
            ['name' => $username],
            [
                'name'     => $username,
                'email'    => $username . '@solarsync.local',
                'password' => Hash::make($password),
            ]
        );
    }
}
