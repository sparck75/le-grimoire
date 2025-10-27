'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '../../contexts/AuthContext'
import styles from './upload.module.css'

export default function UploadPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [message, setMessage] = useState<string>('')
  const [error, setError] = useState<string>('')
  const [uploadMethod, setUploadMethod] = useState<'upload' | 'camera'>('camera')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError('')
      setMessage('')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file) {
      setError('Veuillez sélectionner une image')
      return
    }

    setUploading(true)
    setError('')
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Upload image
      setMessage('Téléchargement de l\'image...')
      const response = await fetch('/api/ocr/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Erreur lors du téléchargement')
      }

      const data = await response.json()
      const jobId = data.id
      
      // Process OCR
      setUploading(false)
      setProcessing(true)
      setMessage('Extraction du texte en cours...')
      
      // Poll for OCR completion (simplified - in production use WebSocket or server-sent events)
      let attempts = 0
      const maxAttempts = 30 // 30 seconds max
      
      const checkStatus = async () => {
        try {
          const statusResponse = await fetch(`/api/ocr/jobs/${jobId}`)
          if (!statusResponse.ok) {
            throw new Error('Erreur lors de la vérification du statut')
          }
          
          const statusData = await statusResponse.json()
          
          if (statusData.status === 'completed') {
            setMessage('Extraction terminée! Redirection...')
            // Redirect to manual recipe form with OCR data
            setTimeout(() => {
              router.push(`/recipes/new/manual?ocr=${jobId}`)
            }, 1500)
          } else if (statusData.status === 'failed') {
            throw new Error(statusData.error_message || 'L\'extraction a échoué')
          } else if (attempts < maxAttempts) {
            attempts++
            setTimeout(checkStatus, 1000)
          } else {
            throw new Error('Délai d\'attente dépassé. Veuillez réessayer.')
          }
        } catch (err) {
          setProcessing(false)
          setError(err instanceof Error ? err.message : 'Une erreur est survenue')
        }
      }
      
      // Start status checking
      setTimeout(checkStatus, 1000)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
      setUploading(false)
      setProcessing(false)
    }
  }

  // Check authentication
  const canUpload = user && (user.role === 'collaborator' || user.role === 'admin')

  if (!canUpload) {
    return (
      <div className={styles.container}>
        <header className={styles.header}>
          <h1>Télécharger une recette</h1>
          <Link href="/" className={styles.backButton}>← Retour</Link>
        </header>
        <div className={styles.card}>
          <div className={styles.notice}>
            <p>⚠️ Accès restreint</p>
            <p className={styles.noticeText}>
              Vous devez être connecté en tant que collaborateur ou administrateur pour télécharger des recettes.
            </p>
          </div>
          <Link href="/login" className={styles.loginButton}>
            Se connecter
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Télécharger une recette</h1>
        <Link href="/recipes/new" className={styles.backButton}>← Retour</Link>
      </header>

      <div className={styles.card}>
        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Method selector */}
          <div className={styles.methodSelector}>
            <button
              type="button"
              className={uploadMethod === 'camera' ? styles.methodActive : styles.methodInactive}
              onClick={() => setUploadMethod('camera')}
            >
              📷 Prendre une photo
            </button>
            <button
              type="button"
              className={uploadMethod === 'upload' ? styles.methodActive : styles.methodInactive}
              onClick={() => setUploadMethod('upload')}
            >
              📤 Choisir une image
            </button>
          </div>

          <div className={styles.uploadArea}>
            <label htmlFor="file-input" className={styles.uploadLabel}>
              {file ? (
                <div>
                  <p>📄 {file.name}</p>
                  <p className={styles.fileSize}>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div>
                  <p className={styles.uploadIcon}>{uploadMethod === 'camera' ? '📷' : '📸'}</p>
                  <p>{uploadMethod === 'camera' ? 'Cliquez pour prendre une photo' : 'Cliquez pour sélectionner une image de recette'}</p>
                  <p className={styles.uploadHint}>JPG, PNG (max 10MB)</p>
                </div>
              )}
            </label>
            <input
              id="file-input"
              type="file"
              accept="image/*"
              capture={uploadMethod === 'camera' ? 'environment' : undefined}
              onChange={handleFileChange}
              className={styles.fileInput}
              disabled={uploading || processing}
            />
          </div>

          {message && (
            <div className={styles.success}>
              {message}
            </div>
          )}

          {error && (
            <div className={styles.error}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={!file || uploading || processing}
            className={styles.submitButton}
          >
            {uploading ? 'Téléchargement...' : processing ? 'Traitement en cours...' : 'Télécharger et extraire'}
          </button>
        </form>

        <div className={styles.info}>
          <h3>Comment ça fonctionne?</h3>
          <ol>
            <li>Prenez une photo avec votre caméra ou choisissez une image existante</li>
            <li>Téléchargez l'image ci-dessus</li>
            <li>Notre système OCR extrait automatiquement le texte</li>
            <li>Vous serez redirigé vers le formulaire de création avec le texte pré-rempli</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
