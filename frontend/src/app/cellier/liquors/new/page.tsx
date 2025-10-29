'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import styles from './liquor-form.module.css'

export default function NewLiquorPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    name: '',
    brand: '',
    distillery: '',
    spirit_type: 'whiskey',
    country: '',
    region: '',
    subtype: '',
    alcohol_content: '',
    age_statement: '',
    tasting_notes: '',
    current_quantity: '100',
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
        spirit_type: formData.spirit_type,
        current_quantity: parseInt(formData.current_quantity) || 100,
      }

      if (formData.brand) data.brand = formData.brand
      if (formData.distillery) data.distillery = formData.distillery
      if (formData.country) data.country = formData.country
      if (formData.region) data.region = formData.region
      if (formData.subtype) data.subtype = formData.subtype
      if (formData.alcohol_content) data.alcohol_content = parseFloat(formData.alcohol_content)
      if (formData.age_statement) data.age_statement = formData.age_statement
      if (formData.tasting_notes) data.tasting_notes = formData.tasting_notes
      if (formData.purchase_price) data.purchase_price = parseFloat(formData.purchase_price)
      if (formData.purchase_location) data.purchase_location = formData.purchase_location
      if (formData.cellar_location) data.cellar_location = formData.cellar_location
      if (formData.rating) data.rating = parseFloat(formData.rating)

      const response = await fetch(`${apiUrl}/api/v2/liquors/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create liquor')
      }

      const liquor = await response.json()
      router.push(`/cellier/liquors/${liquor.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🥃 Ajouter un spiritueux</h1>
        <Link href="/cellier">
          <button className={styles.backButton}>← Retour au cellier</button>
        </Link>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.section}>
          <h2>Informations de base</h2>
          
          <div className={styles.formGroup}>
            <label htmlFor="name">Nom du spiritueux *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Ex: Lagavulin 16 Year Old"
            />
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="brand">Marque</label>
              <input
                type="text"
                id="brand"
                name="brand"
                value={formData.brand}
                onChange={handleChange}
                placeholder="Ex: Lagavulin"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="distillery">Distillerie</label>
              <input
                type="text"
                id="distillery"
                name="distillery"
                value={formData.distillery}
                onChange={handleChange}
                placeholder="Ex: Lagavulin Distillery"
              />
            </div>
          </div>

          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="spirit_type">Type de spiritueux *</label>
              <select
                id="spirit_type"
                name="spirit_type"
                value={formData.spirit_type}
                onChange={handleChange}
                required
              >
                <option value="whiskey">Whisky</option>
                <option value="vodka">Vodka</option>
                <option value="rum">Rhum</option>
                <option value="gin">Gin</option>
                <option value="tequila">Tequila</option>
                <option value="brandy">Brandy</option>
                <option value="cognac">Cognac</option>
                <option value="liqueur">Liqueur</option>
                <option value="other">Autre</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="subtype">Sous-type</label>
              <input
                type="text"
                id="subtype"
                name="subtype"
                value={formData.subtype}
                onChange={handleChange}
                placeholder="Ex: Scotch, Bourbon, etc."
              />
            </div>
          </div>

          <div className={styles.formRow}>
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
                placeholder="Ex: 43.0"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="age_statement">Âge</label>
              <input
                type="text"
                id="age_statement"
                name="age_statement"
                value={formData.age_statement}
                onChange={handleChange}
                placeholder="Ex: 16 ans, XO"
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
                placeholder="Ex: Écosse"
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
                placeholder="Ex: Islay"
              />
            </div>
          </div>
        </div>

        <div className={styles.section}>
          <h2>Cave</h2>
          
          <div className={styles.formRow}>
            <div className={styles.formGroup}>
              <label htmlFor="current_quantity">Niveau restant (%) *</label>
              <input
                type="number"
                id="current_quantity"
                name="current_quantity"
                value={formData.current_quantity}
                onChange={handleChange}
                min="0"
                max="100"
                required
                placeholder="Ex: 100"
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
                placeholder="Ex: Bar, étagère du haut"
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
                placeholder="Ex: 125.00"
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
              placeholder="Décrivez les arômes, la texture, vos impressions..."
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
              placeholder="Ex: 5.0"
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
            {loading ? 'Ajout en cours...' : 'Ajouter le spiritueux'}
          </button>
        </div>
      </form>
    </div>
  )
}
