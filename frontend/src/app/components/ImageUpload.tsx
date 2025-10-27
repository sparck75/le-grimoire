'use client';

import { useState } from 'react';
import styles from './ImageUpload.module.css';

interface ImageUploadProps {
  currentImageUrl?: string | null;
  onImageChange: (imageUrl: string | null, file: File | null) => void;
  label?: string;
}

export default function ImageUpload({ currentImageUrl, onImageChange, label = "Image de la recette" }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(currentImageUrl || null);
  const [uploading, setUploading] = useState(false);
  const [uploadMethod, setUploadMethod] = useState<'upload' | 'camera' | 'url'>('upload');

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    await uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Veuillez sélectionner une image valide');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('L\'image ne doit pas dépasser 5 MB');
      return;
    }

    setUploading(true);

    try {
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);

      // Upload to backend
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/recipes/upload-image', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Échec du téléchargement de l\'image');
      }

      const data = await response.json();
      onImageChange(data.url, file);
    } catch (error) {
      console.error('Error uploading image:', error);
      alert('Erreur lors du téléchargement de l\'image');
      setPreview(currentImageUrl || null);
    } finally {
      setUploading(false);
    }
  };

  const handleUrlChange = (url: string) => {
    setPreview(url || null);
    onImageChange(url || null, null);
  };

  const handleRemove = () => {
    setPreview(null);
    onImageChange(null, null);
    // Reset file input
    const fileInput = document.getElementById('image-upload-input') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  };

  return (
    <div className={styles.container}>
      <label className={styles.label}>{label}</label>

      {/* Method selector */}
      <div className={styles.methodSelector}>
        <button
          type="button"
          className={uploadMethod === 'upload' ? styles.methodActive : styles.methodInactive}
          onClick={() => setUploadMethod('upload')}
        >
          📤 Télécharger
        </button>
        <button
          type="button"
          className={uploadMethod === 'camera' ? styles.methodActive : styles.methodInactive}
          onClick={() => setUploadMethod('camera')}
        >
          📷 Caméra
        </button>
        <button
          type="button"
          className={uploadMethod === 'url' ? styles.methodActive : styles.methodInactive}
          onClick={() => setUploadMethod('url')}
        >
          🔗 URL
        </button>
      </div>

      {uploadMethod === 'upload' ? (
        <div className={styles.uploadArea}>
          {preview ? (
            <div className={styles.previewContainer}>
              <img src={preview} alt="Preview" className={styles.preview} />
              <button
                type="button"
                onClick={handleRemove}
                className={styles.removeButton}
                disabled={uploading}
              >
                ✕ Supprimer
              </button>
            </div>
          ) : (
            <label htmlFor="image-upload-input" className={styles.uploadLabel}>
              <div className={styles.uploadIcon}>📸</div>
              <p className={styles.uploadText}>
                {uploading ? 'Téléchargement...' : 'Cliquez pour sélectionner une image'}
              </p>
              <p className={styles.uploadHint}>JPG, PNG, GIF (max 5MB)</p>
            </label>
          )}
          <input
            id="image-upload-input"
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className={styles.fileInput}
            disabled={uploading}
          />
        </div>
      ) : uploadMethod === 'camera' ? (
        <div className={styles.uploadArea}>
          {preview ? (
            <div className={styles.previewContainer}>
              <img src={preview} alt="Preview" className={styles.preview} />
              <button
                type="button"
                onClick={handleRemove}
                className={styles.removeButton}
                disabled={uploading}
              >
                ✕ Supprimer
              </button>
            </div>
          ) : (
            <label htmlFor="camera-capture-input" className={styles.uploadLabel}>
              <div className={styles.uploadIcon}>📷</div>
              <p className={styles.uploadText}>
                {uploading ? 'Téléchargement...' : 'Cliquez pour prendre une photo'}
              </p>
              <p className={styles.uploadHint}>Utilisez l'appareil photo de votre appareil</p>
            </label>
          )}
          <input
            id="camera-capture-input"
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFileChange}
            className={styles.fileInput}
            disabled={uploading}
          />
        </div>
      ) : (
        <div className={styles.urlArea}>
          <input
            type="url"
            value={preview || ''}
            onChange={(e) => handleUrlChange(e.target.value)}
            placeholder="https://exemple.com/image.jpg"
            className={styles.urlInput}
          />
          {preview && (
            <div className={styles.previewContainer}>
              <img src={preview} alt="Preview" className={styles.preview} />
              <button
                type="button"
                onClick={handleRemove}
                className={styles.removeButton}
              >
                ✕ Supprimer
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
