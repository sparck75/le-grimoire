'use client'

import { useState, useRef } from 'react'
import styles from './BarcodeScanner.module.css'

interface BarcodeScannerProps {
  onBarcodeDetected: (barcode: string) => void
  onClose: () => void
}

export default function BarcodeScanner({ onBarcodeDetected, onClose }: BarcodeScannerProps) {
  const [manualBarcode, setManualBarcode] = useState('')
  const [scanning, setScanning] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  // Note: Full barcode scanning with camera requires additional libraries like zxing-js
  // For now, we provide manual input option
  
  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (manualBarcode.trim()) {
      onBarcodeDetected(manualBarcode.trim())
    }
  }

  const startCamera = async () => {
    setScanning(true)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } // Use back camera on mobile
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (err) {
      alert('Impossible d\'accéder à la caméra. Veuillez entrer le code-barres manuellement.')
      setScanning(false)
    }
  }

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      stream.getTracks().forEach(track => track.stop())
      videoRef.current.srcObject = null
    }
    setScanning(false)
  }

  const handleClose = () => {
    stopCamera()
    onClose()
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h2>📷 Scanner un Code-Barres</h2>
          <button onClick={handleClose} className={styles.closeButton}>
            ✕
          </button>
        </div>

        <div className={styles.content}>
          {!scanning ? (
            <>
              <div className={styles.manualInput}>
                <form onSubmit={handleManualSubmit}>
                  <label>
                    Entrez le code-barres manuellement:
                  </label>
                  <input
                    type="text"
                    value={manualBarcode}
                    onChange={(e) => setManualBarcode(e.target.value)}
                    placeholder="Ex: 3760059560123"
                    className={styles.input}
                    autoFocus
                  />
                  <div className={styles.actions}>
                    <button type="submit" className={styles.submitButton}>
                      🔍 Rechercher
                    </button>
                    <button
                      type="button"
                      onClick={startCamera}
                      className={styles.cameraButton}
                    >
                      📷 Utiliser la Caméra
                    </button>
                  </div>
                </form>
              </div>

              <div className={styles.hint}>
                <p>💡 <strong>Astuce:</strong> Le code-barres se trouve généralement sur le dos de la bouteille.</p>
              </div>
            </>
          ) : (
            <div className={styles.cameraView}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className={styles.video}
              />
              <div className={styles.scannerOverlay}>
                <div className={styles.scannerFrame} />
                <p className={styles.scannerText}>
                  Alignez le code-barres dans le cadre
                </p>
              </div>
              <button
                onClick={stopCamera}
                className={styles.stopButton}
              >
                Annuler
              </button>
              <p className={styles.cameraNote}>
                📝 La détection automatique nécessite une bibliothèque supplémentaire.
                <br />
                Pour l'instant, veuillez entrer le code manuellement.
              </p>
            </div>
          )}
        </div>

        <div className={styles.footer}>
          <button onClick={handleClose} className={styles.cancelButton}>
            Fermer
          </button>
        </div>
      </div>
    </div>
  )
}
