'use client'

import { useState } from 'react'
import Link from 'next/link'
import styles from './upload.module.css'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState<string>('')
  const [error, setError] = useState<string>('')

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

      // Use Next.js proxy route (configured in next.config.js)
      const response = await fetch('/api/ocr/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Erreur lors du téléchargement')
      }

      const data = await response.json()
      setMessage(`Image téléchargée avec succès! ID de traitement: ${data.id}`)
      setFile(null)
      
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Télécharger une recette</h1>
        <Link href="/" className={styles.backButton}>← Retour</Link>
      </header>

      <div className={styles.card}>
        <div className={styles.notice}>
          <p>⚠️ Authentification requise</p>
          <p className={styles.noticeText}>
            Pour télécharger une recette, vous devez vous connecter avec Google ou Apple.
            Cette fonctionnalité sera disponible une fois l'authentification OAuth configurée.
          </p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
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
                  <p className={styles.uploadIcon}>📸</p>
                  <p>Cliquez pour sélectionner une image de recette</p>
                  <p className={styles.uploadHint}>JPG, PNG (max 10MB)</p>
                </div>
              )}
            </label>
            <input
              id="file-input"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className={styles.fileInput}
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
            disabled={!file || uploading}
            className={styles.submitButton}
          >
            {uploading ? 'Téléchargement...' : 'Télécharger et extraire'}
          </button>
        </form>

        <div className={styles.info}>
          <h3>Comment ça fonctionne?</h3>
          <ol>
            <li>Prenez une photo de votre recette papier</li>
            <li>Téléchargez l'image ci-dessus</li>
            <li>Notre système OCR extrait automatiquement le texte</li>
            <li>Vérifiez et enregistrez votre recette</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
