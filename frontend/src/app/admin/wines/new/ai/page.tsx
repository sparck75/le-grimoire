'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import styles from '../wine-admin.module.css'

interface ExtractedWineData {
  name: string
  producer?: string
  vintage?: number
  wine_type: string
  country: string
  region: string
  appellation?: string
  alcohol_content?: number
  grape_varieties?: Array<{ name: string; percentage?: number }>
  tasting_notes?: string
}

export default function AdminAIWineExtractionPage() {
  const router = useRouter()
  const [step, setStep] = useState<'upload' | 'review'>('upload')
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [extracting, setExtracting] = useState(false)
  const [extractedData, setExtractedData] = useState<ExtractedWineData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  // Camera states
  const [showCamera, setShowCamera] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  // Form data for review step
  const [formData, setFormData] = useState<any>({})

  async function startCamera() {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      setShowCamera(true)
      setError(null)
    } catch (err) {
      setError('Impossible d\'accéder à la caméra')
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setShowCamera(false)
  }

  function capturePhoto() {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.drawImage(video, 0, 0)
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], 'wine-label.jpg', { type: 'image/jpeg' })
            setSelectedImage(file)
            setImagePreview(URL.createObjectURL(file))
            stopCamera()
          }
        }, 'image/jpeg', 0.9)
      }
    }
  }

  function handleImageSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedImage(file)
      setImagePreview(URL.createObjectURL(file))
      setError(null)
    }
  }

  async function extractWineData() {
    if (!selectedImage) {
      setError('Veuillez sélectionner une image')
      return
    }

    setExtracting(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const formData = new FormData()
      formData.append('file', selectedImage)

      const response = await fetch(`${apiUrl}/api/ai/extract-wine`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erreur lors de l\'extraction')
      }

      const data = await response.json()
      setExtractedData(data)
      setFormData({
        name: data.name || '',
        producer: data.producer || '',
        vintage: data.vintage || '',
        wine_type: data.wine_type || 'red',
        country: data.country || '',
        region: data.region || '',
        appellation: data.appellation || '',
        alcohol_content: data.alcohol_content || '',
        grape_varieties: data.grape_varieties || [],
        tasting_notes: data.tasting_notes || ''
      })
      setStep('review')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur d\'extraction')
    } finally {
      setExtracting(false)
    }
  }

  async function saveWine() {
    setSaving(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')

      if (!token) {
        throw new Error('Vous devez être connecté')
      }

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }

      // Create wine (admin endpoint - no user_id)
      const wineData = {
        ...formData,
        vintage: formData.vintage ? parseInt(formData.vintage) : null,
        alcohol_content: formData.alcohol_content ? parseFloat(formData.alcohol_content) : null,
        is_public: true // Admin wines are public/master wines
      }

      const response = await fetch(`${apiUrl}/api/admin/wines`, {
        method: 'POST',
        headers,
        body: JSON.stringify(wineData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erreur lors de la création')
      }

      const wine = await response.json()

      // Upload image if selected
      if (selectedImage && wine.id) {
        const imageFormData = new FormData()
        imageFormData.append('file', selectedImage)

        await fetch(`${apiUrl}/api/admin/wines/${wine.id}/image`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: imageFormData
        })
      }

      router.push('/admin/wines')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de sauvegarde')
      setSaving(false)
    }
  }

  if (step === 'upload') {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <Link href="/admin/wines/new">
            <button className={styles.backButton}>← Retour</button>
          </Link>
          <h1>🤖 Extraction IA - Vin</h1>
        </div>

        {error && (
          <div className={styles.error}>
            <p>❌ {error}</p>
          </div>
        )}

        <div className={styles.uploadSection}>
          <h2>📸 Prenez une photo de l'étiquette</h2>

          {!showCamera && !imagePreview && (
            <div className={styles.uploadOptions}>
              <button onClick={startCamera} className={styles.cameraButton}>
                📷 Ouvrir la caméra
              </button>
              <label className={styles.fileButton}>
                📁 Choisir une image
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  style={{ display: 'none' }}
                />
              </label>
            </div>
          )}

          {showCamera && (
            <div className={styles.cameraContainer}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className={styles.cameraVideo}
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
              <div className={styles.cameraControls}>
                <button onClick={capturePhoto} className={styles.captureButton}>
                  📸 Capturer
                </button>
                <button onClick={stopCamera} className={styles.cancelButton}>
                  ✖️ Annuler
                </button>
              </div>
            </div>
          )}

          {imagePreview && (
            <div className={styles.imagePreview}>
              <img src={imagePreview} alt="Wine label" />
              <div className={styles.imageActions}>
                <button
                  onClick={() => {
                    setImagePreview(null)
                    setSelectedImage(null)
                  }}
                  className={styles.changeButton}
                >
                  🔄 Changer
                </button>
                <button
                  onClick={extractWineData}
                  disabled={extracting}
                  className={styles.extractButton}
                >
                  {extracting ? '⏳ Extraction...' : '✨ Extraire les données'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Review step
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button onClick={() => setStep('upload')} className={styles.backButton}>
          ← Retour
        </button>
        <h1>✏️ Vérifier et compléter</h1>
      </div>

      {error && (
        <div className={styles.error}>
          <p>❌ {error}</p>
        </div>
      )}

      <div className={styles.form}>
        <div className={styles.formGroup}>
          <label>Nom du vin *</label>
          <input
            type="text"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label>Producteur</label>
          <input
            type="text"
            value={formData.producer || ''}
            onChange={(e) => setFormData({ ...formData, producer: e.target.value })}
          />
        </div>

        <div className={styles.formRow}>
          <div className={styles.formGroup}>
            <label>Millésime</label>
            <input
              type="number"
              value={formData.vintage || ''}
              onChange={(e) => setFormData({ ...formData, vintage: e.target.value })}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Type</label>
            <select
              value={formData.wine_type || 'red'}
              onChange={(e) => setFormData({ ...formData, wine_type: e.target.value })}
            >
              <option value="red">Rouge</option>
              <option value="white">Blanc</option>
              <option value="rosé">Rosé</option>
              <option value="sparkling">Mousseux</option>
              <option value="dessert">Dessert</option>
              <option value="fortified">Fortifié</option>
            </select>
          </div>
        </div>

        <div className={styles.formRow}>
          <div className={styles.formGroup}>
            <label>Pays</label>
            <input
              type="text"
              value={formData.country || ''}
              onChange={(e) => setFormData({ ...formData, country: e.target.value })}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Région</label>
            <input
              type="text"
              value={formData.region || ''}
              onChange={(e) => setFormData({ ...formData, region: e.target.value })}
            />
          </div>
        </div>

        <div className={styles.formGroup}>
          <label>Appellation</label>
          <input
            type="text"
            value={formData.appellation || ''}
            onChange={(e) => setFormData({ ...formData, appellation: e.target.value })}
          />
        </div>

        <div className={styles.formGroup}>
          <label>Alcool (%)</label>
          <input
            type="number"
            step="0.1"
            value={formData.alcohol_content || ''}
            onChange={(e) => setFormData({ ...formData, alcohol_content: e.target.value })}
          />
        </div>

        <div className={styles.formGroup}>
          <label>Notes de dégustation</label>
          <textarea
            value={formData.tasting_notes || ''}
            onChange={(e) => setFormData({ ...formData, tasting_notes: e.target.value })}
            rows={4}
          />
        </div>

        <div className={styles.formActions}>
          <button
            onClick={() => setStep('upload')}
            className={styles.cancelButton}
          >
            ← Retour
          </button>
          <button
            onClick={saveWine}
            disabled={saving || !formData.name}
            className={styles.submitButton}
          >
            {saving ? '⏳ Enregistrement...' : '💾 Enregistrer'}
          </button>
        </div>
      </div>
    </div>
  )
}
