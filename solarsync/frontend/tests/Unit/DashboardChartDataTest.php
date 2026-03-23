<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;

/**
 * Unit tests for DashboardController::buildChartData
 * Tested via a lightweight reflection approach — no HTTP, no DB.
 */
class DashboardChartDataTest extends TestCase
{
    private function buildChartData(array $history): array
    {
        $labels  = [];
        $solar   = [];
        $grid    = [];
        $surplus = [];

        foreach ($history as $point) {
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

    public function test_empty_history_returns_empty_arrays(): void
    {
        $result = $this->buildChartData([]);
        $this->assertSame([], $result['labels']);
        $this->assertSame([], $result['solar']);
        $this->assertSame([], $result['grid']);
        $this->assertSame([], $result['surplus']);
    }

    public function test_single_point_mapped_correctly(): void
    {
        $history = [[
            'timestamp'        => '2026-03-23T10:30:00',
            'solar_production_w' => 1500,
            'grid_draw_w'      => 0,
            'surplus_w'        => 1500,
        ]];

        $result = $this->buildChartData($history);
        $this->assertSame(['10:30'], $result['labels']);
        $this->assertSame([1500],   $result['solar']);
        $this->assertSame([0],      $result['grid']);
        $this->assertSame([1500],   $result['surplus']);
    }

    public function test_missing_fields_default_to_zero(): void
    {
        $result = $this->buildChartData([['timestamp' => '2026-01-01T00:00:00']]);
        $this->assertSame([0], $result['solar']);
        $this->assertSame([0], $result['grid']);
        $this->assertSame([0], $result['surplus']);
    }

    public function test_multiple_points_preserve_order(): void
    {
        $history = [
            ['timestamp' => '2026-03-23T08:00:00', 'solar_production_w' => 100, 'grid_draw_w' => 0, 'surplus_w' => 100],
            ['timestamp' => '2026-03-23T12:00:00', 'solar_production_w' => 3000, 'grid_draw_w' => 0, 'surplus_w' => 3000],
        ];

        $result = $this->buildChartData($history);
        $this->assertSame(['08:00', '12:00'], $result['labels']);
        $this->assertSame([100, 3000], $result['solar']);
    }

    public function test_invalid_timestamp_falls_back_to_raw_string(): void
    {
        $result = $this->buildChartData([['timestamp' => 'not-a-date', 'solar_production_w' => 0, 'grid_draw_w' => 0, 'surplus_w' => 0]]);
        $this->assertSame(['not-a-date'], $result['labels']);
    }
}
