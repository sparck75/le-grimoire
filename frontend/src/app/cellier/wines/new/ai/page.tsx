'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import styles from '../wine-form.module.css'

interface SuggestedImage {
  url: string
  thumbnail_url?: string
  source: string
  title?: string
  context_url?: string
  relevance_score: number
}

interface ExtractedWineData {
  name: string
  producer?: string
  vintage?: number
  wine_type: string
  country?: string
  region?: string
  appellation?: string
  alcohol_content?: number
  grape_varieties?: string[]
  classification?: string
  tasting_notes?: string
  suggested_lwin7?: string
  suggested_images?: SuggestedImage[]
  confidence_score?: number
  image_url?: string
  front_label_image?: string
  back_label_image?: string
  bottle_image?: string
}

export default function NewWineAIPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [extracting, setExtracting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Multi-image support
  const [frontLabelImage, setFrontLabelImage] = useState<File | null>(null)
  const [backLabelImage, setBackLabelImage] = useState<File | null>(null)
  const [bottleImage, setBottleImage] = useState<File | null>(null)
  const [frontLabelPreview, setFrontLabelPreview] = useState<string | null>(null)
  const [backLabelPreview, setBackLabelPreview] = useState<string | null>(null)
  const [bottlePreview, setBottlePreview] = useState<string | null>(null)
  
  const [extractedData, setExtractedData] = useState<ExtractedWineData | null>(null)
  const [uploadingImages, setUploadingImages] = useState(false)
  const [showCamera, setShowCamera] = useState(false)
  const [activeImageType, setActiveImageType] = useState<'front' | 'back' | 'bottle'>('front')
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
    current_quantity: '1',
    purchase_price: '',
    purchase_location: '',
    cellar_location: '',
    rating: '',
  })

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>, imageType: 'front' | 'back' | 'bottle') => {
    const file = e.target.files?.[0]
    if (file) {
      setError(null)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        const preview = reader.result as string
        if (imageType === 'front') {
          setFrontLabelImage(file)
          setFrontLabelPreview(preview)
        } else if (imageType === 'back') {
          setBackLabelImage(file)
          setBackLabelPreview(preview)
        } else {
          setBottleImage(file)
          setBottlePreview(preview)
        }
      }
      reader.readAsDataURL(file)
    }
  }

  const clearImage = (imageType: 'front' | 'back' | 'bottle') => {
    if (imageType === 'front') {
      setFrontLabelImage(null)
      setFrontLabelPreview(null)
    } else if (imageType === 'back') {
      setBackLabelImage(null)
      setBackLabelPreview(null)
    } else {
      setBottleImage(null)
      setBottlePreview(null)
    }
  }

  const startCamera = async (imageType: 'front' | 'back' | 'bottle') => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' } // Use back camera on mobile
      })
      setStream(mediaStream)
      setShowCamera(true)
      setActiveImageType(imageType)
      setError(null)
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      setError('Impossible d\'accéder à la caméra. Veuillez vérifier les permissions.')
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
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      // Draw video frame to canvas
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        
        // Convert canvas to blob
        canvas.toBlob((blob) => {
          if (blob) {
            // Create File from blob
            const fileName = activeImageType === 'front' ? 'front-label.jpg' : 
                           activeImageType === 'back' ? 'back-label.jpg' : 'bottle.jpg'
            const file = new File([blob], fileName, { type: 'image/jpeg' })
            
            // Create preview
            const reader = new FileReader()
            reader.onloadend = () => {
              const preview = reader.result as string
              if (activeImageType === 'front') {
                setFrontLabelImage(file)
                setFrontLabelPreview(preview)
              } else if (activeImageType === 'back') {
                setBackLabelImage(file)
                setBackLabelPreview(preview)
              } else {
                setBottleImage(file)
                setBottlePreview(preview)
              }
            }
            reader.readAsDataURL(file)
            
            // Stop camera
            stopCamera()
          }
        }, 'image/jpeg', 0.9)
      }
    }
  }

  const extractWineData = async () => {
    // Require at least the front label image
    if (!frontLabelImage) {
      setError('Veuillez sélectionner au moins la photo de l\'étiquette avant')
      return
    }

    setExtracting(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const formDataUpload = new FormData()
      
      // Append all available images
      if (frontLabelImage) formDataUpload.append('front_label', frontLabelImage)
      if (backLabelImage) formDataUpload.append('back_label', backLabelImage)
      if (bottleImage) formDataUpload.append('bottle', bottleImage)
      formDataUpload.append('enrich_with_lwin', 'true')

      // Use new AI wine extraction endpoint with LWIN enrichment and multi-image support
      const response = await fetch(`${apiUrl}/api/v2/ai-wine/extract`, {
        method: 'POST',
        body: formDataUpload
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erreur lors de l\'extraction')
      }

      const extracted = await response.json()
      setExtractedData(extracted)
      
      // Populate form with extracted data (enriched with LWIN if available)
      setFormData(prev => ({
        ...prev,
        name: extracted.name || prev.name,
        producer: extracted.producer || prev.producer,
        vintage: extracted.vintage ? String(extracted.vintage) : prev.vintage,
        wine_type: extracted.wine_type || prev.wine_type,
        country: extracted.country || prev.country,
        region: extracted.region || prev.region,
        appellation: extracted.appellation || prev.appellation,
        alcohol_content: extracted.alcohol_content ? String(extracted.alcohol_content) : prev.alcohol_content,
      }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'extraction. Veuillez réessayer.')
    } finally {
      setExtracting(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value} = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const uploadImagesToWine = async (wineId: string) => {
    if (!frontLabelImage && !backLabelImage && !bottleImage) return

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')

      const formDataUpload = new FormData()
      if (frontLabelImage) formDataUpload.append('front_label', frontLabelImage)
      if (backLabelImage) formDataUpload.append('back_label', backLabelImage)
      if (bottleImage) formDataUpload.append('bottle', bottleImage)

      setUploadingImages(true)

      const response = await fetch(`${apiUrl}/api/v2/wines/${wineId}/images`, {
        method: 'POST',
        headers: token ? {
          'Authorization': `Bearer ${token}`
        } : {},
        body: formDataUpload
      })

      if (!response.ok) {
        console.error('Failed to upload images')
      }
    } catch (err) {
      console.error('Error uploading images:', err)
    } finally {
      setUploadingImages(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      
      // Use the AI wine extraction endpoint which preserves all metadata
      // Update extractedData with form edits (keeping all extraction data including images)
      const updatedExtractionData = {
        ...extractedData,
        name: formData.name,
        producer: formData.producer || extractedData?.producer,
        vintage: formData.vintage ? parseInt(formData.vintage) : extractedData?.vintage,
        wine_type: formData.wine_type,
        country: formData.country || extractedData?.country,
        region: formData.region || extractedData?.region,
        appellation: formData.appellation || extractedData?.appellation,
        alcohol_content: formData.alcohol_content ? parseFloat(formData.alcohol_content) : extractedData?.alcohol_content,
        current_quantity: parseInt(formData.current_quantity) || 1,
        purchase_price: formData.purchase_price ? parseFloat(formData.purchase_price) : undefined,
        purchase_location: formData.purchase_location || undefined,
        cellar_location: formData.cellar_location || undefined,
        rating: formData.rating ? parseFloat(formData.rating) : undefined,
        // IMPORTANT: Preserve image URLs from extraction (already uploaded during extraction)
        image_url: extractedData?.image_url,
        front_label_image: extractedData?.front_label_image,
        back_label_image: extractedData?.back_label_image,
        bottle_image: extractedData?.bottle_image,
      }

      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      // Use the AI wine extraction endpoint to preserve LWIN data and image sources
      const response = await fetch(`${apiUrl}/api/v2/ai-wine/create-from-extraction`, {
        method: 'POST',
        headers,
        body: JSON.stringify(updatedExtractionData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create wine')
      }

      const result = await response.json()
      const wineId = result.wine_id

      // Note: Images are already uploaded during extraction
      // No need to upload again - they're saved during /api/v2/ai-wine/extract
      // The extraction endpoint handles all 3 images: front_label, back_label, bottle

      // Redirect to cellier main page
      router.push(`/cellier`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🤖 Ajouter un vin avec l&apos;IA</h1>
        <Link href="/cellier/wines/new">
          <button className={styles.backButton}>← Retour</button>
        </Link>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {!extractedData ? (
        // Step 1: Upload and extract
        <div className={styles.form}>
          <div className={styles.section}>
            <h2>📸 Photos du vin</h2>
            <p style={{ color: '#666', marginBottom: '1.5rem' }}>
              Prenez des photos claires de votre vin. L&apos;IA extraira automatiquement
              les informations comme le nom, le producteur, le millésime, la région, etc.
            </p>
            
            {showCamera ? (
              // Camera view
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
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
                {/* Front Label */}
                <div className={styles.imageUploadArea}>
                  <h3 style={{ marginBottom: '1rem', fontSize: '1rem', color: '#333' }}>Étiquette avant *</h3>
                  <div className={styles.imagePreview}>
                    {frontLabelPreview ? (
                      <>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={frontLabelPreview} alt="Étiquette avant" />
                        <button
                          type="button"
                          onClick={() => clearImage('front')}
                          style={{ position: 'absolute', top: '8px', right: '8px', background: 'rgba(255,0,0,0.8)', color: 'white', border: 'none', borderRadius: '50%', width: '32px', height: '32px', cursor: 'pointer' }}
                        >
                          ✖
                        </button>
                      </>
                    ) : (
                      <div className={styles.imagePreviewIcon}>�️</div>
                    )}
                  </div>
                  
                  <div className={styles.imageUploadControls}>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <button
                        type="button"
                        onClick={() => startCamera('front')}
                        className={styles.imageUploadButton}
                        style={{ fontSize: '0.85rem', padding: '0.5rem 0.75rem' }}
                      >
                        📷 Photo
                      </button>
                      <label htmlFor="front-label-image" className={styles.imageUploadButton} style={{ fontSize: '0.85rem', padding: '0.5rem 0.75rem' }}>
                        🖼️ Fichier
                      </label>
                    </div>
                    <input
                      id="front-label-image"
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleImageChange(e, 'front')}
                      style={{ display: 'none' }}
                    />
                    {frontLabelImage && (
                      <p className={styles.imageUploadSuccess} style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
                        ✓ {frontLabelImage.name}
                      </p>
                    )}
                  </div>
                </div>

                {/* Back Label */}
                <div className={styles.imageUploadArea}>
                  <h3 style={{ marginBottom: '1rem', fontSize: '1rem', color: '#333' }}>Étiquette arrière</h3>
                  <div className={styles.imagePreview}>
                    {backLabelPreview ? (
                      <>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={backLabelPreview} alt="Étiquette arrière" />
                        <button
                          type="button"
                          onClick={() => clearImage('back')}
                          style={{ position: 'absolute', top: '8px', right: '8px', background: 'rgba(255,0,0,0.8)', color: 'white', border: 'none', borderRadius: '50%', width: '32px', height: '32px', cursor: 'pointer' }}
                        >
                          ✖
                        </button>
                      </>
                    ) : (
                      <div className={styles.imagePreviewIcon}>🏷️</div>
                    )}
                  </div>
                  
                  <div className={styles.imageUploadControls}>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <button
                        type="button"
                        onClick={() => startCamera('back')}
                        className={styles.imageUploadButton}
                        style={{ fontSize: '0.85rem', padding: '0.5rem 0.75rem' }}
                      >
                        📷 Photo
                      </button>
                      <label htmlFor="back-label-image" className={styles.imageUploadButton} style={{ fontSize: '0.85rem', padding: '0.5rem 0.75rem' }}>
                        🖼️ Fichier
                      </label>
                    </div>
                    <input
                      id="back-label-image"
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleImageChange(e, 'back')}
                      style={{ display: 'none' }}
                    />
                    {backLabelImage && (
                      <p className={styles.imageUploadSuccess} style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
                        ✓ {backLabelImage.name}
                      </p>
                    )}
                  </div>
                </div>

                {/* Full Bottle */}
                <div className={styles.imageUploadArea}>
                  <h3 style={{ marginBottom: '1rem', fontSize: '1rem', color: '#333' }}>Bouteille complète</h3>
                  <div className={styles.imagePreview}>
                    {bottlePreview ? (
                      <>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={bottlePreview} alt="Bouteille" />
                        <button
                          type="button"
                          onClick={() => clearImage('bottle')}
                          style={{ position: 'absolute', top: '8px', right: '8px', background: 'rgba(255,0,0,0.8)', color: 'white', border: 'none', borderRadius: '50%', width: '32px', height: '32px', cursor: 'pointer' }}
                        >
                          ✖
                        </button>
                      </>
                    ) : (
                      <div className={styles.imagePreviewIcon}>🍷</div>
                    )}
                  </div>
                  
                  <div className={styles.imageUploadControls}>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <button
                        type="button"
                        onClick={() => startCamera('bottle')}
                        className={styles.imageUploadButton}
                        style={{ fontSize: '0.85rem', padding: '0.5rem 0.75rem' }}
                      >
                        📷 Photo
                      </button>
                      <label htmlFor="bottle-image" className={styles.imageUploadButton} style={{ fontSize: '0.85rem', padding: '0.5rem 0.75rem' }}>
                        🖼️ Fichier
                      </label>
                    </div>
                    <input
                      id="bottle-image"
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleImageChange(e, 'bottle')}
                      style={{ display: 'none' }}
                    />
                    {bottleImage && (
                      <p className={styles.imageUploadSuccess} style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
                        ✓ {bottleImage.name}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            <p style={{ color: '#666', fontSize: '0.9rem', marginTop: '1rem', fontStyle: 'italic' }}>
              * L&apos;étiquette avant est requise pour l&apos;extraction automatique
            </p>
          </div>

          <div className={styles.actions}>
            <Link href="/cellier/wines/new">
              <button type="button" className={styles.cancelButton}>
                Annuler
              </button>
            </Link>
            <button 
              onClick={extractWineData} 
              className={styles.submitButton} 
              disabled={!frontLabelImage || extracting}
            >
              {extracting ? '🤖 Extraction en cours...' : '🤖 Extraire les informations'}
            </button>
          </div>
        </div>
      ) : (
        // Step 2: Review and edit extracted data
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.section} style={{ background: '#e8f5e9', borderLeft: '4px solid #4caf50' }}>
            <h2>✅ Informations extraites</h2>
            <p style={{ color: '#2e7d32', marginBottom: '0' }}>
              L&apos;IA a extrait les informations ci-dessous. Vous pouvez les modifier si nécessaire
              avant d&apos;ajouter le vin à votre cellier.
            </p>
            {extractedData.confidence_score && (
              <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#555' }}>
                <strong>Score de confiance:</strong> {(extractedData.confidence_score * 100).toFixed(0)}%
                {extractedData.confidence_score < 0.7 && (
                  <span style={{ color: '#f57c00', marginLeft: '0.5rem' }}>
                    ⚠️ Vérifiez attentivement les données extraites
                  </span>
                )}
              </div>
            )}
          </div>

          {extractedData.suggested_lwin7 && (
            <div className={styles.section} style={{ background: '#e3f2fd', borderLeft: '4px solid #2196f3' }}>
              <h2>🍷 Enrichissement LWIN</h2>
              <p style={{ color: '#1565c0', marginBottom: '0.5rem' }}>
                Ce vin a été enrichi avec la base de données LWIN (Liv-ex Wine Identification Number)
              </p>
              <div style={{ fontSize: '0.9rem', color: '#555' }}>
                <strong>Code LWIN7:</strong> {extractedData.suggested_lwin7}
              </div>
              {extractedData.grape_varieties && extractedData.grape_varieties.length > 0 && (
                <div style={{ fontSize: '0.9rem', color: '#555', marginTop: '0.5rem' }}>
                  <strong>Cépages:</strong> {extractedData.grape_varieties.join(', ')}
                </div>
              )}
              {extractedData.classification && (
                <div style={{ fontSize: '0.9rem', color: '#555', marginTop: '0.5rem' }}>
                  <strong>Classification:</strong> {extractedData.classification}
                </div>
              )}
            </div>
          )}

          {extractedData.suggested_images && extractedData.suggested_images.length > 0 && (
            <div className={styles.section} style={{ background: '#f3e5f5', borderLeft: '4px solid #9c27b0', padding: '1rem' }}>
              <h2 style={{ marginBottom: '0.5rem' }}>📸 Images trouvées sur Internet</h2>
              <p style={{ color: '#7b1fa2', marginBottom: '0.75rem', fontSize: '0.85rem' }}>
                {extractedData.suggested_images.length} image(s) correspondante(s) trouvée(s) en ligne. 
                Ces images seront enregistrées avec votre vin pour référence.
              </p>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
                gap: '0.75rem'
              }}>
                {extractedData.suggested_images.map((img, index) => (
                  <div key={index} style={{
                    border: '2px solid #e0e0e0',
                    borderRadius: '6px',
                    overflow: 'hidden',
                    background: 'white',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.03)'
                    e.currentTarget.style.boxShadow = '0 3px 6px rgba(0,0,0,0.2)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)'
                    e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)'
                  }}
                  onClick={() => window.open(img.context_url || img.url, '_blank')}
                  >
                    <div style={{ 
                      height: '140px',
                      background: '#f9f9f9',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      overflow: 'hidden'
                    }}>
                      <img 
                        src={img.thumbnail_url || img.url} 
                        alt={img.title || `Wine image ${index + 1}`}
                        style={{
                          maxWidth: '100%',
                          maxHeight: '100%',
                          objectFit: 'contain'
                        }}
                        onError={(e) => {
                          e.currentTarget.style.display = 'none'
                          e.currentTarget.parentElement!.innerHTML = '<div style="color: #999; font-size: 0.7rem; text-align: center; padding: 0.5rem;">Image non disponible</div>'
                        }}
                      />
                    </div>
                    <div style={{ 
                      padding: '0.4rem',
                      fontSize: '0.7rem',
                      color: '#666',
                      borderTop: '1px solid #e0e0e0'
                    }}>
                      <div style={{ 
                        fontWeight: 'bold', 
                        marginBottom: '0.2rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.25rem'
                      }}>
                        {img.source === 'google' && '🔍'}
                        {img.source === 'vivino' && '🍷'}
                        <span style={{ color: '#4caf50', fontSize: '0.65rem' }}>
                          {Math.round(img.relevance_score * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div style={{
                marginTop: '1rem',
                padding: '0.75rem',
                background: 'rgba(156, 39, 176, 0.1)',
                borderRadius: '4px',
                fontSize: '0.85rem',
                color: '#7b1fa2'
              }}>
                💡 <strong>Note:</strong> Ces images seront automatiquement enregistrées avec votre vin. 
                Cliquez sur une image pour voir la source complète.
              </div>
            </div>
          )}

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
            <h2>Informations du cellier</h2>
            
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
            <button 
              type="button" 
              className={styles.cancelButton}
              onClick={() => {
                setExtractedData(null)
                setFormData({
                  name: '',
                  producer: '',
                  vintage: '',
                  wine_type: 'red',
                  country: '',
                  region: '',
                  appellation: '',
                  alcohol_content: '',
                  current_quantity: '1',
                  purchase_price: '',
                  purchase_location: '',
                  cellar_location: '',
                  rating: '',
                })
              }}
            >
              ← Réessayer l&apos;extraction
            </button>
            <button type="submit" className={styles.submitButton} disabled={loading || uploadingImages}>
              {uploadingImages ? 'Téléchargement des images...' : loading ? 'Ajout en cours...' : 'Ajouter au cellier'}
            </button>
          </div>
        </form>
      )}
    </div>
  )
}
