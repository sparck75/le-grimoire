'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import styles from '../wine-form.module.css'

export default function NewWineManualPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [uploadingImage, setUploadingImage] = useState(false)
  const [showCamera, setShowCamera] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  
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

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedImage(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      })
      setStream(mediaStream)
      setShowCamera(true)
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      alert('Impossible d\'accéder à la caméra. Veuillez vérifier les permissions.')
      console.error('Camera error:', err)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setShowCamera(false)
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], 'wine-bottle.jpg', { type: 'image/jpeg' })
            setSelectedImage(file)
            
            const reader = new FileReader()
            reader.onloadend = () => {
              setImagePreview(reader.result as string)
            }
            reader.readAsDataURL(file)
            
            stopCamera()
          }
        }, 'image/jpeg', 0.9)
      }
    }
  }

  const uploadImageToWine = async (wineId: string) => {
    if (!selectedImage) return

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')

      const formDataUpload = new FormData()
      formDataUpload.append('file', selectedImage)

      setUploadingImage(true)

      const response = await fetch(`${apiUrl}/api/v2/wines/${wineId}/image`, {
        method: 'POST',
        headers: token ? {
          'Authorization': `Bearer ${token}`
        } : {},
        body: formDataUpload
      })

      if (!response.ok) {
        console.error('Failed to upload image')
      }
    } catch (err) {
      console.error('Error uploading image:', err)
    } finally {
      setUploadingImage(false)
    }
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

      const token = localStorage.getItem('access_token')
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${apiUrl}/api/v2/wines/`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create wine')
      }

      const wine = await response.json()

      // Upload image if selected
      if (selectedImage && wine.id) {
        await uploadImageToWine(wine.id)
      }

      // Redirect to cellier main page (wine detail page doesn't exist yet)
      router.push(`/cellier`)
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
        {/* Image Upload Section */}
        <div className={styles.imageSection}>
          <h2>Photo de la bouteille</h2>
          
          {showCamera ? (
            <div className={styles.cameraContainer}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className={styles.cameraVideo}
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
              <div className={styles.cameraControls}>
                <button
                  type="button"
                  onClick={capturePhoto}
                  className={styles.captureButton}
                >
                  📸 Prendre la photo
                </button>
                <button
                  type="button"
                  onClick={stopCamera}
                  className={styles.cancelButton}
                >
                  ✖ Annuler
                </button>
              </div>
            </div>
          ) : (
            <div className={styles.imageUploadArea}>
              <div className={styles.imagePreview}>
                {imagePreview ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={imagePreview}
                    alt="Aperçu"
                  />
                ) : (
                  <div className={styles.imagePreviewIcon}>🍷</div>
                )}
              </div>
              
              <div className={styles.imageUploadControls}>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  <button
                    type="button"
                    onClick={startCamera}
                    className={styles.imageUploadButton}
                  >
                    📷 Prendre une photo
                  </button>
                  <label htmlFor="wine-image" className={styles.imageUploadButton}>
                    �️ Choisir une photo
                  </label>
                </div>
                <input
                  id="wine-image"
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  style={{ display: 'none' }}
                />
                <p className={styles.imageUploadHint}>
                  Prenez une photo avec votre caméra ou choisissez une image existante
                </p>
                {selectedImage && (
                  <p className={styles.imageUploadSuccess}>
                    ✓ {selectedImage.name}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

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
              <label htmlFor="purchase_price">Prix d&apos;achat ($)</label>
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
              <label htmlFor="purchase_location">Lieu d&apos;achat</label>
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
          <button type="submit" className={styles.submitButton} disabled={loading || uploadingImage}>
            {uploadingImage ? 'Téléchargement de l\'image...' : loading ? 'Ajout en cours...' : 'Ajouter le vin'}
          </button>
        </div>
      </form>
    </div>
  )
}
