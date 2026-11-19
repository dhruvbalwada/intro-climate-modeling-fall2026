"""Supplied numerical routines for the classroom carbon-model comparison.

Public inputs use emissions in ppm/year. The simplified FaIR-style carbon
routine internally converts to GtC for its uptake calibration coefficients.
It is a teaching adaptation, not the full FaIR package or a validated projection.
"""

import numpy as np
from scipy.optimize import minimize_scalar, least_squares

GTC_PER_PPM = 2.124
PARTITIONS = np.array([0.2173, 0.2240, 0.2824, 0.2763])
BASE_TIMESCALES = np.array([np.inf, 394.4, 36.54, 4.304])


def annual_response(times, tau, years, rates):
    """Exact one-box response to a rate held constant within each year.

    Returns the decay of a unit initial anomaly and the emissions-only response.
    Initial time is January 1 of years[0].
    """
    times = np.asarray(times, dtype=float)
    years, rates = np.asarray(years, dtype=int), np.asarray(rates, dtype=float)
    if tau <= 0 or len(years) != len(rates) or len(years) == 0:
        raise ValueError("Supply positive tau and matching nonempty years/rates.")
    if not np.array_equal(years, np.arange(years[0], years[-1] + 1)):
        raise ValueError("Emissions years must be consecutive.")
    elapsed = times - years[0]
    if np.any(elapsed < 0) or np.any(elapsed > len(years)):
        raise ValueError("Concentration times must lie inside the emissions record.")
    yearly = np.zeros(len(rates) + 1)
    decay = np.exp(-1 / tau)
    gain = -tau * np.expm1(-1 / tau)
    for i, rate in enumerate(rates):
        yearly[i + 1] = yearly[i] * decay + rate * gain
    index = np.minimum(np.floor(elapsed).astype(int), len(years) - 1)
    fraction = elapsed - index
    forced = yearly[index] * np.exp(-fraction / tau) + rates[index] * (-tau * np.expm1(-fraction / tau))
    return np.exp(-elapsed / tau), forced


def fit_one_box(times, observed, training, years, rates, reference=280.0):
    """Jointly fit tau, initial excess and fixed-phase seasonal amplitude."""
    times, observed, training = np.asarray(times), np.asarray(observed), np.asarray(training, dtype=bool)
    seasonal = np.sin(2 * np.pi * (times - 1958))

    def candidate(log_tau):
        tau = np.exp(log_tau)
        decay, forced = annual_response(times, tau, years, rates)
        design = np.column_stack([decay, seasonal])
        coef = np.linalg.lstsq(design[training], observed[training] - reference - forced[training], rcond=None)[0]
        trend = reference + coef[0] * decay + forced
        prediction = trend + coef[1] * seasonal
        return np.mean((prediction[training] - observed[training])**2), coef, trend, prediction

    grid = np.linspace(np.log(0.1), np.log(10000), 181)
    best = int(np.argmin([candidate(z)[0] for z in grid]))
    if best in (0, len(grid) - 1):
        raise RuntimeError("The uptake fit reached the search boundary.")
    result = minimize_scalar(lambda z: candidate(z)[0], bounds=(grid[best-1], grid[best+1]),
                             method="bounded", options={"xatol": 1e-11})
    if not result.success:
        raise RuntimeError("The one-box calibration did not converge.")
    _, coef, trend, prediction = candidate(result.x)
    return {"tau": float(np.exp(result.x)), "initial_excess": float(coef[0]),
            "amplitude": float(coef[1]), "reference": reference,
            "trend": trend, "prediction": prediction}


def one_box_trend(times, fitted, years, rates):
    decay, forced = annual_response(times, fitted["tau"], years, rates)
    return fitted["reference"] + fitted["initial_excess"] * decay + forced


# The 100-year pulse-retention rule is kept out of the main teaching sequence.
# This lookup solves the FaIR v1.3 timescale-scaling equation. Its infinite-
# timescale component contributes 100*a[0] to the integrated pulse response.
_alpha = np.exp(np.linspace(-12, 12, 12001))
_scaled = _alpha[:, None] * BASE_TIMESCALES[None, 1:]
_retention = 100 * PARTITIONS[0] + np.sum(
    PARTITIONS[None, 1:] * _scaled * (-np.expm1(-100 / _scaled)), axis=1
)


def four_box_trend(years, rates_ppm, parameters, step=1/12):
    """Simplified FaIR response; 1850 baseline 285 ppm, zero additional pools.

    Published fractions/base timescales are fixed. r0 and rU control changes in
    uptake efficiency; the temperature feedback is omitted. Parameters are
    calibrated to the historical station record, not interpreted as independently
    measured process properties. Earlier emissions initialize the response modes.
    """
    years, rates_ppm = np.asarray(years, dtype=int), np.asarray(rates_ppm, dtype=float)
    if years[0] != 1850 or not np.array_equal(years, np.arange(1850, years[-1] + 1)):
        raise ValueError("The richer model requires consecutive emissions from 1850.")
    subdivisions = int(round(1 / step))
    if not np.isclose(subdivisions * step, 1):
        raise ValueError("Time step must divide one year.")
    emissions = np.repeat(rates_ppm * GTC_PER_PPM, subdivisions)
    r0, rU = parameters
    pools = np.zeros(4)
    cumulative = 0.0
    trend = np.zeros(len(emissions) + 1)
    for n, emission in enumerate(emissions):
        uptake_gtc = cumulative - pools.sum()
        target = np.clip(r0 + rU * uptake_gtc, _retention[0], 97.0)
        scale = np.interp(target, _retention, _alpha)
        tau = scale * BASE_TIMESCALES[1:]
        pools[0] += PARTITIONS[0] * emission * step
        pools[1:] = pools[1:] * np.exp(-step/tau) + PARTITIONS[1:] * emission * (-tau*np.expm1(-step/tau))
        cumulative += emission * step
        trend[n+1] = pools.sum() / GTC_PER_PPM
    return 1850 + np.arange(len(trend)) * step, 285.0 + trend


def fit_four_box(times, observed, training, years, rates_ppm):
    """Fit two uptake-rule coefficients and one annual sine amplitude."""
    times, observed, training = np.asarray(times), np.asarray(observed), np.asarray(training, dtype=bool)
    seasonal = np.sin(2*np.pi*(times-1958))[:, None]

    def candidate(parameters):
        edges, response = four_box_trend(years, rates_ppm, parameters)
        trend = np.interp(times, edges, response)
        amplitude = np.linalg.lstsq(seasonal[training], observed[training]-trend[training], rcond=None)[0][0]
        return trend + amplitude*seasonal[:, 0], trend, float(amplitude)

    result = least_squares(lambda p: (candidate(p)[0]-observed)[training], [35.0, 0.019],
                           bounds=([22.0, 0.0], [65.0, 0.1]), diff_step=1e-4,
                           ftol=1e-9, xtol=1e-9, gtol=1e-8)
    if not result.success:
        raise RuntimeError("The richer-model calibration did not converge.")
    prediction, trend, amplitude = candidate(result.x)
    return {"parameters": result.x, "amplitude": amplitude,
            "prediction": prediction, "trend": trend}
