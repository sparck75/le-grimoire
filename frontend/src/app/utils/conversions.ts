/**
 * Unit conversion utilities for cooking measurements
 * Supports volume, weight, temperature, and length conversions
 */

export type UnitCategory = 'volume' | 'weight' | 'temperature' | 'length';

export interface UnitDefinition {
  name: string;
  symbol: string;
  category: UnitCategory;
  toBase: (value: number) => number;
  fromBase: (value: number) => number;
}

// Volume units (base: milliliters)
const volumeUnits: Record<string, UnitDefinition> = {
  ml: {
    name: 'Millilitre',
    symbol: 'ml',
    category: 'volume',
    toBase: (v) => v,
    fromBase: (v) => v,
  },
  l: {
    name: 'Litre',
    symbol: 'L',
    category: 'volume',
    toBase: (v) => v * 1000,
    fromBase: (v) => v / 1000,
  },
  'c-à-thé': {
    name: 'Cuillère à thé',
    symbol: 'c. à thé',
    category: 'volume',
    toBase: (v) => v * 5,
    fromBase: (v) => v / 5,
  },
  'c-à-soupe': {
    name: 'Cuillère à soupe',
    symbol: 'c. à soupe',
    category: 'volume',
    toBase: (v) => v * 15,
    fromBase: (v) => v / 15,
  },
  tasse: {
    name: 'Tasse',
    symbol: 'tasse',
    category: 'volume',
    toBase: (v) => v * 250,
    fromBase: (v) => v / 250,
  },
  'tasse-us': {
    name: 'Tasse US',
    symbol: 'tasse US',
    category: 'volume',
    toBase: (v) => v * 236.588,
    fromBase: (v) => v / 236.588,
  },
  'fl-oz': {
    name: 'Once liquide',
    symbol: 'fl oz',
    category: 'volume',
    toBase: (v) => v * 29.5735,
    fromBase: (v) => v / 29.5735,
  },
  pinte: {
    name: 'Pinte',
    symbol: 'pinte',
    category: 'volume',
    toBase: (v) => v * 473.176,
    fromBase: (v) => v / 473.176,
  },
  gallon: {
    name: 'Gallon',
    symbol: 'gal',
    category: 'volume',
    toBase: (v) => v * 3785.41,
    fromBase: (v) => v / 3785.41,
  },
};

// Weight units (base: grams)
const weightUnits: Record<string, UnitDefinition> = {
  g: {
    name: 'Gramme',
    symbol: 'g',
    category: 'weight',
    toBase: (v) => v,
    fromBase: (v) => v,
  },
  kg: {
    name: 'Kilogramme',
    symbol: 'kg',
    category: 'weight',
    toBase: (v) => v * 1000,
    fromBase: (v) => v / 1000,
  },
  mg: {
    name: 'Milligramme',
    symbol: 'mg',
    category: 'weight',
    toBase: (v) => v / 1000,
    fromBase: (v) => v * 1000,
  },
  oz: {
    name: 'Once',
    symbol: 'oz',
    category: 'weight',
    toBase: (v) => v * 28.3495,
    fromBase: (v) => v / 28.3495,
  },
  lb: {
    name: 'Livre',
    symbol: 'lb',
    category: 'weight',
    toBase: (v) => v * 453.592,
    fromBase: (v) => v / 453.592,
  },
};

// Temperature units
const temperatureUnits: Record<string, UnitDefinition> = {
  celsius: {
    name: 'Celsius',
    symbol: '°C',
    category: 'temperature',
    toBase: (v) => v,
    fromBase: (v) => v,
  },
  fahrenheit: {
    name: 'Fahrenheit',
    symbol: '°F',
    category: 'temperature',
    toBase: (v) => (v - 32) * 5/9,
    fromBase: (v) => (v * 9/5) + 32,
  },
  kelvin: {
    name: 'Kelvin',
    symbol: 'K',
    category: 'temperature',
    toBase: (v) => v - 273.15,
    fromBase: (v) => v + 273.15,
  },
};

// Length units (base: centimeters)
const lengthUnits: Record<string, UnitDefinition> = {
  cm: {
    name: 'Centimètre',
    symbol: 'cm',
    category: 'length',
    toBase: (v) => v,
    fromBase: (v) => v,
  },
  mm: {
    name: 'Millimètre',
    symbol: 'mm',
    category: 'length',
    toBase: (v) => v / 10,
    fromBase: (v) => v * 10,
  },
  m: {
    name: 'Mètre',
    symbol: 'm',
    category: 'length',
    toBase: (v) => v * 100,
    fromBase: (v) => v / 100,
  },
  inch: {
    name: 'Pouce',
    symbol: 'in',
    category: 'length',
    toBase: (v) => v * 2.54,
    fromBase: (v) => v / 2.54,
  },
  foot: {
    name: 'Pied',
    symbol: 'ft',
    category: 'length',
    toBase: (v) => v * 30.48,
    fromBase: (v) => v / 30.48,
  },
};

// Combined unit registry
export const allUnits: Record<string, UnitDefinition> = {
  ...volumeUnits,
  ...weightUnits,
  ...temperatureUnits,
  ...lengthUnits,
};

/**
 * Convert a value from one unit to another
 * @param value - The numeric value to convert
 * @param fromUnit - The source unit key
 * @param toUnit - The target unit key
 * @returns The converted value or null if conversion is not possible
 */
export function convertUnit(
  value: number,
  fromUnit: string,
  toUnit: string
): number | null {
  const from = allUnits[fromUnit];
  const to = allUnits[toUnit];

  if (!from || !to) {
    console.error(`Unknown unit: ${fromUnit} or ${toUnit}`);
    return null;
  }

  if (from.category !== to.category) {
    console.error(`Cannot convert between ${from.category} and ${to.category}`);
    return null;
  }

  // Convert to base unit, then to target unit
  const baseValue = from.toBase(value);
  const convertedValue = to.fromBase(baseValue);

  return convertedValue;
}

/**
 * Get all units for a specific category
 */
export function getUnitsByCategory(category: UnitCategory): Record<string, UnitDefinition> {
  return Object.fromEntries(
    Object.entries(allUnits).filter(([, unit]) => unit.category === category)
  );
}

/**
 * Get unit display name with symbol
 */
export function getUnitDisplay(unitKey: string): string {
  const unit = allUnits[unitKey];
  return unit ? `${unit.name} (${unit.symbol})` : unitKey;
}

/**
 * Common ingredient density conversions (volume to weight)
 * These are approximate and can vary based on ingredient properties
 */
export const ingredientDensities: Record<string, number> = {
  // Density in g/ml
  'farine': 0.593,
  'sucre': 0.845,
  'sucre-glace': 0.560,
  'beurre': 0.911,
  'huile': 0.92,
  'eau': 1.0,
  'lait': 1.03,
  'miel': 1.42,
  'sel': 1.217,
  'cacao': 0.528,
  'levure': 0.64,
};

/**
 * Convert volume to weight for common ingredients
 */
export function volumeToWeight(
  volumeMl: number,
  ingredientKey: string
): number | null {
  const density = ingredientDensities[ingredientKey];
  if (!density) return null;
  return volumeMl * density;
}

/**
 * Convert weight to volume for common ingredients
 */
export function weightToVolume(
  weightG: number,
  ingredientKey: string
): number | null {
  const density = ingredientDensities[ingredientKey];
  if (!density) return null;
  return weightG / density;
}
