<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Symfony\Component\HttpFoundation\Response;

class RequirePasswordChange
{
    public function handle(Request $request, Closure $next): Response
    {
        if (Auth::check() && Auth::user()->must_change_password) {
            // Allow the change-password routes through to avoid a redirect loop
            if ($request->routeIs('auth.change-password') || $request->routeIs('auth.change-password.update')) {
                return $next($request);
            }

            return redirect()->route('auth.change-password');
        }

        return $next($request);
    }
}
