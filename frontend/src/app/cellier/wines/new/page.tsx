'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import styles from './wine-form.module.css'

export default function NewWinePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    name: '',
    producer: '',
    vintage: '',
    wine_type: 'red',
    country: '',
    region: '',
    appellation: '',
    alcohol_content: '',
    tasting_notes: '',
    current_quantity: '1',
    purchase_price: '',
    purchase_location: '',
    cellar_location: '',
    rating: '',
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Prepare data
      const data: any = {
        name: formData.name,
        wine_type: formData.wine_type,
        current_quantity: parseInt(formData.current_quantity) || 0,
      }

      if (formData.producer) data.producer = formData.producer
      if (formData.vintage) data.vintage = parseInt(formData.vintage)
      if (formData.country) data.country = formData.country
      if (formData.region) data.region = formData.region
      if (formData.appellation) data.appellation = formData.appellation
      if (formData.alcohol_content) data.alcohol_content = parseFloat(formData.alcohol_content)
      if (formData.tasting_notes) data.tasting_notes = formData.tasting_notes
      if (formData.purchase_price) data.purchase_price = parseFloat(formData.purchase_price)
      if (formData.purchase_location) data.purchase_location = formData.purchase_location
      if (formData.cellar_location) data.cellar_location = formData.cellar_location
      if (formData.rating) data.rating = parseFloat(formData.rating)

      const response = await fetch(`${apiUrl}/api/v2/wines/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create wine')
      }

      const wine = await response.json()
      router.push(`/cellier/wines/${wine.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🍷 Ajouter un vin</h1>
        <Link href="/cellier">
          <button className={styles.backButton}>← Retour au cellier</button>
        </Link>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.section}>
          <h2>Informations de base</h2>
          
          <div className={styles.formGroup}>
            <label htmlFor="name">Nom du vin *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Ex: Château Margaux"
            />
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="producer">Producteur</label>
              <input
                type="text"
                id="producer"
                name="producer"
                value={formData.producer}
                onChange={handleChange}
                placeholder="Ex: Château Margaux"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="vintage">Millésime</label>
              <input
                type="number"
                id="vintage"
                name="vintage"
                value={formData.vintage}
                onChange={handleChange}
                min="1800"
                max={new Date().getFullYear() + 1}
                placeholder="Ex: 2015"
              />
            </div>
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="wine_type">Type de vin *</label>
              <select
                id="wine_type"
                name="wine_type"
                value={formData.wine_type}
                onChange={handleChange}
                required
              >
                <option value="red">Rouge</option>
                <option value="white">Blanc</option>
                <option value="rosé">Rosé</option>
                <option value="sparkling">Mousseux</option>
                <option value="dessert">Dessert</option>
                <option value="fortified">Fortifié</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="alcohol_content">Alcool (%)</label>
              <input
                type="number"
                id="alcohol_content"
                name="alcohol_content"
                value={formData.alcohol_content}
                onChange={handleChange}
                step="0.1"
                min="0"
                max="100"
                placeholder="Ex: 13.5"
              />
            </div>
          </div>
        </div>

        <div className={styles.section}>
          <h2>Provenance</h2>
          
          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="country">Pays</label>
              <input
                type="text"
                id="country"
                name="country"
                value={formData.country}
                onChange={handleChange}
                placeholder="Ex: France"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="region">Région</label>
              <input
                type="text"
                id="region"
                name="region"
                value={formData.region}
                onChange={handleChange}
                placeholder="Ex: Bordeaux"
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="appellation">Appellation</label>
            <input
              type="text"
              id="appellation"
              name="appellation"
              value={formData.appellation}
              onChange={handleChange}
              placeholder="Ex: Margaux"
            />
          </div>
        </div>

        <div className={styles.section}>
          <h2>Cave</h2>
          
          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="current_quantity">Quantité (bouteilles) *</label>
              <input
                type="number"
                id="current_quantity"
                name="current_quantity"
                value={formData.current_quantity}
                onChange={handleChange}
                min="0"
                required
                placeholder="Ex: 1"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="cellar_location">Emplacement</label>
              <input
                type="text"
                id="cellar_location"
                name="cellar_location"
                value={formData.cellar_location}
                onChange={handleChange}
                placeholder="Ex: Rangée 3, Étagère 2"
              />
            </div>
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="purchase_price">Prix d'achat ($)</label>
              <input
                type="number"
                id="purchase_price"
                name="purchase_price"
                value={formData.purchase_price}
                onChange={handleChange}
                step="0.01"
                min="0"
                placeholder="Ex: 45.00"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="purchase_location">Lieu d'achat</label>
              <input
                type="text"
                id="purchase_location"
                name="purchase_location"
                value={formData.purchase_location}
                onChange={handleChange}
                placeholder="Ex: SAQ"
              />
            </div>
          </div>
        </div>

        <div className={styles.section}>
          <h2>Notes</h2>
          
          <div className={styles.formGroup}>
            <label htmlFor="tasting_notes">Notes de dégustation</label>
            <textarea
              id="tasting_notes"
              name="tasting_notes"
              value={formData.tasting_notes}
              onChange={handleChange}
              rows={4}
              placeholder="Décrivez les arômes, la structure, vos impressions..."
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="rating">Note personnelle (0-5)</label>
            <input
              type="number"
              id="rating"
              name="rating"
              value={formData.rating}
              onChange={handleChange}
              step="0.5"
              min="0"
              max="5"
              placeholder="Ex: 4.5"
            />
          </div>
        </div>

        <div className={styles.actions}>
          <Link href="/cellier">
            <button type="button" className={styles.cancelButton}>
              Annuler
            </button>
          </Link>
          <button type="submit" className={styles.submitButton} disabled={loading}>
            {loading ? 'Ajout en cours...' : 'Ajouter le vin'}
          </button>
        </div>
      </form>
    </div>
  )
}
