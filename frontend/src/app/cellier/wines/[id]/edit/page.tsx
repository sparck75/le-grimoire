'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import styles from './edit.module.css'

interface Wine {
  id: string
  name: string
  producer?: string
  vintage?: number
  wine_type: string
  country: string
  region: string
  appellation?: string
  current_quantity: number
  purchase_date?: string
  purchase_price?: number
  purchase_location?: string
  cellar_location?: string
  drink_from?: number
  drink_until?: number
  peak_drinking?: string
  rating?: number
  tasting_notes: string
}

export default function EditWinePage() {
  const router = useRouter()
  const params = useParams()
  const wineId = params.id as string

  const [wine, setWine] = useState<Wine | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form fields (éditable)
  const [quantity, setQuantity] = useState(0)
  const [cellarLocation, setCellarLocation] = useState('')
  const [purchaseDate, setPurchaseDate] = useState('')
  const [purchasePrice, setPurchasePrice] = useState('')
  const [purchaseLocation, setPurchaseLocation] = useState('')
  const [drinkFrom, setDrinkFrom] = useState('')
  const [drinkUntil, setDrinkUntil] = useState('')
  const [peakDrinking, setPeakDrinking] = useState('')
  const [rating, setRating] = useState('')
  const [tastingNotes, setTastingNotes] = useState('')

  useEffect(() => {
    fetchWine()
  }, [wineId])

  async function fetchWine() {
    setLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')

      if (!token) {
        router.push('/login')
        return
      }

      const response = await fetch(`/api/v2/wines/${wineId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Vin non trouvé')
        }
        throw new Error('Erreur lors du chargement du vin')
      }

      const data = await response.json()
      setWine(data)

      // Pré-remplir les champs
      setQuantity(data.current_quantity || 0)
      setCellarLocation(data.cellar_location || '')
      setPurchaseDate(data.purchase_date ? data.purchase_date.split('T')[0] : '')
      setPurchasePrice(data.purchase_price?.toString() || '')
      setPurchaseLocation(data.purchase_location || '')
      setDrinkFrom(data.drink_from?.toString() || '')
      setDrinkUntil(data.drink_until?.toString() || '')
      setPeakDrinking(data.peak_drinking || '')
      setRating(data.rating?.toString() || '')
      setTastingNotes(data.tasting_notes || '')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')

      if (!token) {
        router.push('/login')
        return
      }

      const updateData = {
        current_quantity: quantity,
        cellar_location: cellarLocation || null,
        purchase_date: purchaseDate || null,
        purchase_price: purchasePrice ? parseFloat(purchasePrice) : null,
        purchase_location: purchaseLocation || null,
        drink_from: drinkFrom ? parseInt(drinkFrom) : null,
        drink_until: drinkUntil ? parseInt(drinkUntil) : null,
        peak_drinking: peakDrinking || null,
        rating: rating ? parseFloat(rating) : null,
        tasting_notes: tastingNotes || ''
      }

      const response = await fetch(`/api/v2/wines/${wineId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erreur lors de la mise à jour')
      }

      // Succès - retour à la page de détails
      router.push(`/cellier/wines/${wineId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Chargement du vin...</p>
        </div>
      </div>
    )
  }

  if (error || !wine) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>{error || 'Vin non trouvé'}</div>
        <Link href="/cellier">
          <button className={styles.backButton}>← Retour au cellier</button>
        </Link>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Link href={`/cellier/wines/${wineId}`}>
          <button className={styles.backButton}>← Retour aux détails</button>
        </Link>
        <h1>Modifier le vin</h1>
      </div>

      <div className={styles.wineInfo}>
        <h2>{wine.name}</h2>
        {wine.producer && <p className={styles.producer}>{wine.producer}</p>}
        <div className={styles.meta}>
          {wine.vintage && <span>{wine.vintage}</span>}
          <span>{wine.wine_type}</span>
          <span>{wine.region}, {wine.country}</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className={styles.form}>
        {error && <div className={styles.formError}>{error}</div>}

        {/* Section Inventaire */}
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>📦 Inventaire</h3>
          
          <div className={styles.formGroup}>
            <label htmlFor="quantity">Quantité en stock *</label>
            <input
              type="number"
              id="quantity"
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
              min="0"
              required
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="cellarLocation">Emplacement dans le cellier</label>
            <input
              type="text"
              id="cellarLocation"
              value={cellarLocation}
              onChange={(e) => setCellarLocation(e.target.value)}
              placeholder="Ex: Rangée A, Étagère 3"
              className={styles.input}
            />
            <small>Où se trouve ce vin dans votre cellier</small>
          </div>
        </div>

        {/* Section Achat */}
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>💰 Informations d'achat</h3>

          <div className={styles.formGroup}>
            <label htmlFor="purchaseDate">Date d'achat</label>
            <input
              type="date"
              id="purchaseDate"
              value={purchaseDate}
              onChange={(e) => setPurchaseDate(e.target.value)}
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="purchasePrice">Prix d'achat ($)</label>
            <input
              type="number"
              id="purchasePrice"
              value={purchasePrice}
              onChange={(e) => setPurchasePrice(e.target.value)}
              step="0.01"
              min="0"
              placeholder="0.00"
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="purchaseLocation">Lieu d'achat</label>
            <input
              type="text"
              id="purchaseLocation"
              value={purchaseLocation}
              onChange={(e) => setPurchaseLocation(e.target.value)}
              placeholder="Ex: SAQ Signature, Dépanneur du coin"
              className={styles.input}
            />
          </div>
        </div>

        {/* Section Fenêtre de consommation */}
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>🍷 Fenêtre de consommation</h3>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="drinkFrom">À boire à partir de</label>
              <input
                type="number"
                id="drinkFrom"
                value={drinkFrom}
                onChange={(e) => setDrinkFrom(e.target.value)}
                min="2000"
                max="2100"
                placeholder="Année"
                className={styles.input}
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="drinkUntil">À boire jusqu'à</label>
              <input
                type="number"
                id="drinkUntil"
                value={drinkUntil}
                onChange={(e) => setDrinkUntil(e.target.value)}
                min="2000"
                max="2100"
                placeholder="Année"
                className={styles.input}
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="peakDrinking">Période optimale</label>
            <input
              type="text"
              id="peakDrinking"
              value={peakDrinking}
              onChange={(e) => setPeakDrinking(e.target.value)}
              placeholder="Ex: 2025-2030"
              className={styles.input}
            />
            <small>La période où ce vin sera à son meilleur</small>
          </div>
        </div>

        {/* Section Évaluation */}
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>⭐ Évaluation personnelle</h3>

          <div className={styles.formGroup}>
            <label htmlFor="rating">Note (0-5)</label>
            <input
              type="number"
              id="rating"
              value={rating}
              onChange={(e) => setRating(e.target.value)}
              step="0.5"
              min="0"
              max="5"
              placeholder="0.0"
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="tastingNotes">Notes de dégustation</label>
            <textarea
              id="tastingNotes"
              value={tastingNotes}
              onChange={(e) => setTastingNotes(e.target.value)}
              rows={6}
              placeholder="Vos impressions personnelles sur ce vin..."
              className={styles.textarea}
            />
          </div>
        </div>

        {/* Boutons d'action */}
        <div className={styles.actions}>
          <Link href={`/cellier/wines/${wineId}`}>
            <button type="button" className={styles.cancelButton}>
              Annuler
            </button>
          </Link>
          <button
            type="submit"
            disabled={saving}
            className={styles.saveButton}
          >
            {saving ? '⏳ Enregistrement...' : '✅ Enregistrer les modifications'}
          </button>
        </div>
      </form>
    </div>
  )
}
