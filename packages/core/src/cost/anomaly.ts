// ============================================================
// Cost Anomaly Detection — Z-Score based
// Flags unusual spending patterns
// ============================================================

export interface AnomalyResult {
  isAnomaly: boolean;
  zScore: number;
  currentValue: number;
  mean: number;
  stdDev: number;
}

/** Detect anomalies using z-score (>2.5 standard deviations = anomaly) */
export function detectAnomaly(
  currentValue: number,
  historicalValues: number[],
  threshold: number = 2.5,
): AnomalyResult {
  if (historicalValues.length < 3) {
    // Not enough data to determine anomaly
    return {
      isAnomaly: false,
      zScore: 0,
      currentValue,
      mean: currentValue,
      stdDev: 0,
    };
  }

  const mean =
    historicalValues.reduce((a, b) => a + b, 0) / historicalValues.length;
  const variance =
    historicalValues.reduce((sum, val) => sum + (val - mean) ** 2, 0) /
    historicalValues.length;
  const stdDev = Math.sqrt(variance);

  if (stdDev === 0) {
    return {
      isAnomaly: currentValue !== mean,
      zScore: currentValue === mean ? 0 : Infinity,
      currentValue,
      mean,
      stdDev: 0,
    };
  }

  const zScore = (currentValue - mean) / stdDev;

  return {
    isAnomaly: zScore > threshold,
    zScore,
    currentValue,
    mean,
    stdDev,
  };
}
