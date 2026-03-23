<?php

use App\Http\Controllers\ApplianceController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\OnboardingController;
use App\Http\Controllers\SettingsController;
use Illuminate\Support\Facades\Route;

// ── Public ────────────────────────────────────────────────────────────────────

Route::get('/login', [AuthController::class, 'showLogin'])->name('login');
Route::post('/login', [AuthController::class, 'login'])->name('login.submit');

// ── Authenticated ─────────────────────────────────────────────────────────────

Route::middleware('auth')->group(function () {

    Route::post('/logout', [AuthController::class, 'logout'])->name('logout');

    // Root redirect: onboarding if not complete, else dashboard
    Route::get('/', [OnboardingController::class, 'index'])->name('home');

    // Dashboard
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');
    Route::get('/dashboard/status', [DashboardController::class, 'status'])->name('dashboard.status');
    Route::post('/appliances/{id}/override', [DashboardController::class, 'override'])->name('appliances.override');

    // Onboarding wizard
    Route::prefix('onboarding')->name('onboarding.')->group(function () {
        Route::get('/1',  [OnboardingController::class, 'step1'])->name('step1');
        Route::post('/1', [OnboardingController::class, 'step1Submit'])->name('step1.submit');

        Route::get('/2',  [OnboardingController::class, 'step2'])->name('step2');
        Route::post('/2', [OnboardingController::class, 'step2Submit'])->name('step2.submit');

        Route::get('/3',  [OnboardingController::class, 'step3'])->name('step3');
        Route::post('/3', [OnboardingController::class, 'step3Submit'])->name('step3.submit');

        Route::get('/4',  [OnboardingController::class, 'step4'])->name('step4');
        Route::post('/4', [OnboardingController::class, 'step4Submit'])->name('step4.submit');

        // AJAX: discover plugs for a hub
        Route::get('/discover-plugs', [OnboardingController::class, 'discoverPlugs'])->name('discover-plugs');
    });

    // Appliances management
    Route::get('/appliances',              [ApplianceController::class, 'index'])->name('appliances.index');
    Route::get('/appliances/create',       [ApplianceController::class, 'create'])->name('appliances.create');
    Route::post('/appliances',             [ApplianceController::class, 'store'])->name('appliances.store');
    Route::get('/appliances/{id}/edit',    [ApplianceController::class, 'edit'])->name('appliances.edit');
    Route::put('/appliances/{id}',         [ApplianceController::class, 'update'])->name('appliances.update');
    Route::delete('/appliances/{id}',      [ApplianceController::class, 'destroy'])->name('appliances.destroy');
    Route::post('/appliances/{id}/toggle', [ApplianceController::class, 'toggle'])->name('appliances.toggle');

    // Settings
    Route::get('/settings',                              [SettingsController::class, 'index'])->name('settings.index');
    Route::put('/settings/hubs/{id}',                    [SettingsController::class, 'updateHub'])->name('settings.hubs.update');
    Route::delete('/settings/hubs/{id}',                 [SettingsController::class, 'deleteHub'])->name('settings.hubs.delete');
    Route::post('/settings/energy-providers',            [SettingsController::class, 'addEnergyProvider'])->name('settings.providers.add');
    Route::delete('/settings/energy-providers/{id}',     [SettingsController::class, 'deleteEnergyProvider'])->name('settings.providers.delete');
    Route::post('/settings/setting',                     [SettingsController::class, 'updateSetting'])->name('settings.update');

});
