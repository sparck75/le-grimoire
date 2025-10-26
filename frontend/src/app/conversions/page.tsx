'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  convertUnit, 
  getUnitsByCategory, 
  allUnits,
  volumeToWeight,
  weightToVolume,
  ingredientDensities,
  type UnitCategory 
} from '../utils/conversions';
import styles from './conversions.module.css';

export default function ConversionsPage() {
  const [category, setCategory] = useState<UnitCategory>('volume');
  const [inputValue, setInputValue] = useState<string>('1');
  const [fromUnit, setFromUnit] = useState<string>('tasse');
  const [toUnit, setToUnit] = useState<string>('ml');
  const [result, setResult] = useState<number | null>(null);
  
  // Volume-Weight conversion
  const [showVolumeWeight, setShowVolumeWeight] = useState(false);
  const [ingredient, setIngredient] = useState<string>('farine');
  const [volumeWeightValue, setVolumeWeightValue] = useState<string>('250');
  const [volumeWeightResult, setVolumeWeightResult] = useState<number | null>(null);
  const [isVolumeToWeight, setIsVolumeToWeight] = useState(true);

  // Perform conversion when inputs change
  useEffect(() => {
    const numValue = parseFloat(inputValue);
    if (!isNaN(numValue) && fromUnit && toUnit) {
      const converted = convertUnit(numValue, fromUnit, toUnit);
      setResult(converted);
    } else {
      setResult(null);
    }
  }, [inputValue, fromUnit, toUnit]);

  // Update units when category changes
  useEffect(() => {
    const units = getUnitsByCategory(category);
    const unitKeys = Object.keys(units);
    if (unitKeys.length >= 2) {
      setFromUnit(unitKeys[0]);
      setToUnit(unitKeys[1]);
    }
  }, [category]);

  // Volume-Weight conversion effect
  useEffect(() => {
    const numValue = parseFloat(volumeWeightValue);
    if (!isNaN(numValue) && ingredient) {
      const converted = isVolumeToWeight 
        ? volumeToWeight(numValue, ingredient)
        : weightToVolume(numValue, ingredient);
      setVolumeWeightResult(converted);
    } else {
      setVolumeWeightResult(null);
    }
  }, [volumeWeightValue, ingredient, isVolumeToWeight]);

  const currentUnits = getUnitsByCategory(category);
  const categories: { key: UnitCategory; label: string; icon: string }[] = [
    { key: 'volume', label: 'Volume', icon: '🥤' },
    { key: 'weight', label: 'Poids', icon: '⚖️' },
    { key: 'temperature', label: 'Température', icon: '🌡️' },
    { key: 'length', label: 'Longueur', icon: '📏' },
  ];

  const formatResult = (value: number | null): string => {
    if (value === null) return '—';
    
    // Round to 2 decimal places, but remove trailing zeros
    const rounded = Math.round(value * 100) / 100;
    return rounded.toString();
  };

  return (
    <div className={styles.page}>
      <div className={styles.container}>
      <div className={styles.header}>
        <Link href="/" className={styles.backButton}>
          ← Retour
        </Link>
        <h1 className={styles.title}>Conversions d'Unités</h1>
        <p className={styles.subtitle}>
          Convertissez facilement vos mesures de cuisine
        </p>
      </div>

      {/* Category Selector */}
      <div className={styles.categorySelector}>
        {categories.map((cat) => (
          <button
            key={cat.key}
            className={`${styles.categoryButton} ${category === cat.key ? styles.active : ''}`}
            onClick={() => setCategory(cat.key)}
          >
            <span className={styles.categoryIcon}>{cat.icon}</span>
            <span>{cat.label}</span>
          </button>
        ))}
      </div>

      {/* Main Conversion Card */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h2>Convertir {categories.find(c => c.key === category)?.label}</h2>
        </div>
        
        <div className={styles.conversionRow}>
          {/* From Input */}
          <div className={styles.inputWrapper}>
            <label className={styles.label}>De:</label>
            <input
              type="number"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className={styles.inputCompact}
              placeholder="Valeur"
              step="any"
            />
            <select
              value={fromUnit}
              onChange={(e) => setFromUnit(e.target.value)}
              className={styles.selectCompact}
            >
              {Object.entries(currentUnits).map(([key, unit]) => (
                <option key={key} value={key}>
                  {unit.symbol}
                </option>
              ))}
            </select>
          </div>

          {/* Swap Button */}
          <button
            className={styles.swapButtonCompact}
            onClick={() => {
              const temp = fromUnit;
              setFromUnit(toUnit);
              setToUnit(temp);
            }}
            title="Inverser"
          >
            ⇄
          </button>

          {/* To Result */}
          <div className={styles.inputWrapper}>
            <label className={styles.label}>À:</label>
            <div className={styles.resultCompact}>
              {formatResult(result)}
            </div>
            <select
              value={toUnit}
              onChange={(e) => setToUnit(e.target.value)}
              className={styles.selectCompact}
            >
              {Object.entries(currentUnits).map(([key, unit]) => (
                <option key={key} value={key}>
                  {unit.symbol}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Volume-Weight Conversion Card (for cooking ingredients) */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h2>Conversion Volume ↔ Poids</h2>
        </div>

        <p className={styles.cardDescription}>
          Convertissez entre volume et poids pour les ingrédients courants
        </p>

        <div className={styles.ingredientSelector}>
          <label className={styles.label}>Ingrédient:</label>
          <select
            value={ingredient}
            onChange={(e) => setIngredient(e.target.value)}
            className={styles.selectFull}
          >
            {Object.keys(ingredientDensities).map((key) => (
              <option key={key} value={key}>
                {key.charAt(0).toUpperCase() + key.slice(1).replace('-', ' ')}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.conversionTypeSelector}>
          <button
            className={`${styles.typeButton} ${isVolumeToWeight ? styles.active : ''}`}
            onClick={() => setIsVolumeToWeight(true)}
          >
            Volume → Poids
          </button>
          <button
            className={`${styles.typeButton} ${!isVolumeToWeight ? styles.active : ''}`}
            onClick={() => setIsVolumeToWeight(false)}
          >
            Poids → Volume
          </button>
        </div>

        <div className={styles.volumeWeightGrid}>
          <div className={styles.conversionSection}>
            <label className={styles.label}>
              {isVolumeToWeight ? 'Volume (ml):' : 'Poids (g):'}
            </label>
            <input
              type="number"
              value={volumeWeightValue}
              onChange={(e) => setVolumeWeightValue(e.target.value)}
              className={styles.input}
              placeholder="Entrez une valeur"
              step="any"
            />
          </div>

          <div className={styles.equalsSign}>=</div>

          <div className={styles.conversionSection}>
            <label className={styles.label}>
              {isVolumeToWeight ? 'Poids (g):' : 'Volume (ml):'}
            </label>
            <div className={styles.result}>
              <strong>{formatResult(volumeWeightResult)}</strong>
              <span className={styles.unitName}>{isVolumeToWeight ? 'grammes' : 'millilitres'}</span>
            </div>
          </div>
        </div>

        <div className={styles.densityNote}>
          💡 Densité: {ingredientDensities[ingredient]?.toFixed(3)} g/ml
        </div>
      </div>

      {/* Common Conversions Reference Table - MOVED TO BOTTOM */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h2>📋 Table de Référence</h2>
        </div>

        <div className={styles.referenceTable}>
          <div className={styles.tableSection}>
            <h3>Volume</h3>
            <table>
              <tbody>
                <tr><td>1 tasse</td><td>=</td><td>250 ml</td></tr>
                <tr><td>1 c. à soupe</td><td>=</td><td>15 ml</td></tr>
                <tr><td>1 c. à thé</td><td>=</td><td>5 ml</td></tr>
                <tr><td>1 L</td><td>=</td><td>1000 ml</td></tr>
                <tr><td>4 tasses</td><td>=</td><td>1 L</td></tr>
                <tr><td>1 oz liq.</td><td>=</td><td>30 ml</td></tr>
                <tr><td>1 pinte</td><td>=</td><td>500 ml</td></tr>
              </tbody>
            </table>
          </div>

          <div className={styles.tableSection}>
            <h3>Poids</h3>
            <table>
              <tbody>
                <tr><td>1 kg</td><td>=</td><td>1000 g</td></tr>
                <tr><td>1 lb</td><td>=</td><td>454 g</td></tr>
                <tr><td>1 oz</td><td>=</td><td>28 g</td></tr>
                <tr><td>500 g</td><td>=</td><td>1.1 lb</td></tr>
                <tr><td>100 g</td><td>=</td><td>3.5 oz</td></tr>
                <tr><td>250 g</td><td>=</td><td>8.8 oz</td></tr>
              </tbody>
            </table>
          </div>

          <div className={styles.tableSection}>
            <h3>Température</h3>
            <table>
              <tbody>
                <tr><td>150°C</td><td>=</td><td>300°F</td></tr>
                <tr><td>180°C</td><td>=</td><td>356°F</td></tr>
                <tr><td>200°C</td><td>=</td><td>392°F</td></tr>
                <tr><td>220°C</td><td>=</td><td>428°F</td></tr>
                <tr><td>0°C</td><td>=</td><td>32°F</td></tr>
                <tr><td>100°C</td><td>=</td><td>212°F</td></tr>
              </tbody>
            </table>
          </div>

          <div className={styles.tableSection}>
            <h3>Longueur</h3>
            <table>
              <tbody>
                <tr><td>1 cm</td><td>=</td><td>0.39 pouces</td></tr>
                <tr><td>1 m</td><td>=</td><td>3.28 pieds</td></tr>
                <tr><td>1 pouce</td><td>=</td><td>2.54 cm</td></tr>
                <tr><td>1 pied</td><td>=</td><td>30.48 cm</td></tr>
                <tr><td>10 cm</td><td>=</td><td>4 pouces</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      </div>
    </div>
  );
}
