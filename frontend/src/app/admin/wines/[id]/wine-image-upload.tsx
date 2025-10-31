/**
 * WineImageUpload Component
 * 
 * Upload component for wine images with support for three image types:
 * - Front label (for OCR/AI extraction)
 * - Back label (for OCR/AI extraction)
 * - Full bottle (for catalog display)
 * 
 * Features:
 * - Three separate file inputs
 * - Image preview
 * - Drag and drop support
 * - Upload progress indicators
 * - File validation
 */

import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import styles from './wine-image-upload.module.css';

interface WineImageUploadProps {
  wineId: string;
  existingImages?: {
    front_label_image?: string | null;
    back_label_image?: string | null;
    bottle_image?: string | null;
  };
  onUploadComplete?: (images: {
    front_label_image?: string;
    back_label_image?: string;
    bottle_image?: string;
  }) => void;
}

interface ImagePreview {
  file: File;
  url: string;
}

export default function WineImageUpload({
  wineId,
  existingImages,
  onUploadComplete
}: WineImageUploadProps) {
  // State for image previews
  const [frontLabelPreview, setFrontLabelPreview] = useState<ImagePreview | null>(null);
  const [backLabelPreview, setBackLabelPreview] = useState<ImagePreview | null>(null);
  const [bottlePreview, setBottlePreview] = useState<ImagePreview | null>(null);

  // State for upload progress
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // File input refs
  const frontLabelRef = useRef<HTMLInputElement>(null);
  const backLabelRef = useRef<HTMLInputElement>(null);
  const bottleRef = useRef<HTMLInputElement>(null);

  // Drag state for each drop zone
  const [frontLabelDrag, setFrontLabelDrag] = useState(false);
  const [backLabelDrag, setBackLabelDrag] = useState(false);
  const [bottleDrag, setBottleDrag] = useState(false);

  /**
   * Validate image file
   */
  const validateFile = (file: File): string | null => {
    // Check file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      return 'Invalid file type. Please upload JPG, PNG, or WebP images.';
    }

    // Check file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      return 'File too large. Maximum size is 10 MB.';
    }

    return null;
  };

  /**
   * Create preview from file
   */
  const createPreview = (file: File): ImagePreview => {
    return {
      file,
      url: URL.createObjectURL(file)
    };
  };

  /**
   * Handle file selection
   */
  const handleFileSelect = (
    event: ChangeEvent<HTMLInputElement>,
    imageType: 'front_label' | 'back_label' | 'bottle'
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const error = validateFile(file);
    if (error) {
      setError(error);
      return;
    }

    setError(null);
    const preview = createPreview(file);

    if (imageType === 'front_label') {
      setFrontLabelPreview(preview);
    } else if (imageType === 'back_label') {
      setBackLabelPreview(preview);
    } else {
      setBottlePreview(preview);
    }
  };

  /**
   * Handle drag events
   */
  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleDragEnter = (
    event: DragEvent<HTMLDivElement>,
    imageType: 'front_label' | 'back_label' | 'bottle'
  ) => {
    event.preventDefault();
    if (imageType === 'front_label') setFrontLabelDrag(true);
    else if (imageType === 'back_label') setBackLabelDrag(true);
    else setBottleDrag(true);
  };

  const handleDragLeave = (
    event: DragEvent<HTMLDivElement>,
    imageType: 'front_label' | 'back_label' | 'bottle'
  ) => {
    event.preventDefault();
    if (imageType === 'front_label') setFrontLabelDrag(false);
    else if (imageType === 'back_label') setBackLabelDrag(false);
    else setBottleDrag(false);
  };

  const handleDrop = (
    event: DragEvent<HTMLDivElement>,
    imageType: 'front_label' | 'back_label' | 'bottle'
  ) => {
    event.preventDefault();
    
    // Reset drag state
    if (imageType === 'front_label') setFrontLabelDrag(false);
    else if (imageType === 'back_label') setBackLabelDrag(false);
    else setBottleDrag(false);

    const file = event.dataTransfer.files[0];
    if (!file) return;

    const error = validateFile(file);
    if (error) {
      setError(error);
      return;
    }

    setError(null);
    const preview = createPreview(file);

    if (imageType === 'front_label') {
      setFrontLabelPreview(preview);
    } else if (imageType === 'back_label') {
      setBackLabelPreview(preview);
    } else {
      setBottlePreview(preview);
    }
  };

  /**
   * Clear preview
   */
  const clearPreview = (imageType: 'front_label' | 'back_label' | 'bottle') => {
    if (imageType === 'front_label') {
      if (frontLabelPreview) URL.revokeObjectURL(frontLabelPreview.url);
      setFrontLabelPreview(null);
      if (frontLabelRef.current) frontLabelRef.current.value = '';
    } else if (imageType === 'back_label') {
      if (backLabelPreview) URL.revokeObjectURL(backLabelPreview.url);
      setBackLabelPreview(null);
      if (backLabelRef.current) backLabelRef.current.value = '';
    } else {
      if (bottlePreview) URL.revokeObjectURL(bottlePreview.url);
      setBottlePreview(null);
      if (bottleRef.current) bottleRef.current.value = '';
    }
  };

  /**
   * Upload images to backend
   */
  const handleUpload = async () => {
    // Check if any images selected
    if (!frontLabelPreview && !backLabelPreview && !bottlePreview) {
      setError('Please select at least one image to upload');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Not authenticated');
      }

      // Create FormData
      const formData = new FormData();
      if (frontLabelPreview) {
        formData.append('front_label', frontLabelPreview.file);
      }
      if (backLabelPreview) {
        formData.append('back_label', backLabelPreview.file);
      }
      if (bottlePreview) {
        formData.append('bottle', bottlePreview.file);
      }

      // Upload
      const response = await fetch(
        `http://192.168.1.100:8000/api/admin/wines/${wineId}/images`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setUploadProgress(100);
      setSuccess('Images uploaded successfully!');

      // Clear previews
      if (frontLabelPreview) URL.revokeObjectURL(frontLabelPreview.url);
      if (backLabelPreview) URL.revokeObjectURL(backLabelPreview.url);
      if (bottlePreview) URL.revokeObjectURL(bottlePreview.url);
      
      setFrontLabelPreview(null);
      setBackLabelPreview(null);
      setBottlePreview(null);

      // Clear file inputs
      if (frontLabelRef.current) frontLabelRef.current.value = '';
      if (backLabelRef.current) backLabelRef.current.value = '';
      if (bottleRef.current) bottleRef.current.value = '';

      // Callback
      if (onUploadComplete) {
        onUploadComplete(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Images du vin</h3>

      <div className={styles.uploadGrid}>
        {/* Front Label */}
        <div className={styles.uploadSection}>
          <h4 className={styles.sectionTitle}>Étiquette avant</h4>
          <p className={styles.sectionDescription}>
            Pour extraction OCR/AI des données
          </p>
          
          <div
            className={`${styles.dropZone} ${frontLabelDrag ? styles.dragActive : ''}`}
            onDragOver={handleDragOver}
            onDragEnter={(e) => handleDragEnter(e, 'front_label')}
            onDragLeave={(e) => handleDragLeave(e, 'front_label')}
            onDrop={(e) => handleDrop(e, 'front_label')}
            onClick={() => frontLabelRef.current?.click()}
          >
            {frontLabelPreview ? (
              <div className={styles.previewContainer}>
                <img
                  src={frontLabelPreview.url}
                  alt="Front label preview"
                  className={styles.preview}
                />
                <button
                  type="button"
                  className={styles.clearButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    clearPreview('front_label');
                  }}
                >
                  ×
                </button>
              </div>
            ) : existingImages?.front_label_image ? (
              <div className={styles.previewContainer}>
                <img
                  src={`http://192.168.1.100:8000/${existingImages.front_label_image}`}
                  alt="Front label"
                  className={styles.preview}
                />
                <div className={styles.existingLabel}>Actuel</div>
              </div>
            ) : (
              <div className={styles.dropZoneContent}>
                <p>📷</p>
                <p>Glisser-déposer ou cliquer</p>
                <p className={styles.dropZoneHint}>JPG, PNG, WebP (max 10 MB)</p>
              </div>
            )}
          </div>
          
          <input
            ref={frontLabelRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/webp"
            onChange={(e) => handleFileSelect(e, 'front_label')}
            className={styles.fileInput}
          />
        </div>

        {/* Back Label */}
        <div className={styles.uploadSection}>
          <h4 className={styles.sectionTitle}>Étiquette arrière</h4>
          <p className={styles.sectionDescription}>
            Pour extraction OCR/AI des données complémentaires
          </p>
          
          <div
            className={`${styles.dropZone} ${backLabelDrag ? styles.dragActive : ''}`}
            onDragOver={handleDragOver}
            onDragEnter={(e) => handleDragEnter(e, 'back_label')}
            onDragLeave={(e) => handleDragLeave(e, 'back_label')}
            onDrop={(e) => handleDrop(e, 'back_label')}
            onClick={() => backLabelRef.current?.click()}
          >
            {backLabelPreview ? (
              <div className={styles.previewContainer}>
                <img
                  src={backLabelPreview.url}
                  alt="Back label preview"
                  className={styles.preview}
                />
                <button
                  type="button"
                  className={styles.clearButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    clearPreview('back_label');
                  }}
                >
                  ×
                </button>
              </div>
            ) : existingImages?.back_label_image ? (
              <div className={styles.previewContainer}>
                <img
                  src={`http://192.168.1.100:8000/${existingImages.back_label_image}`}
                  alt="Back label"
                  className={styles.preview}
                />
                <div className={styles.existingLabel}>Actuel</div>
              </div>
            ) : (
              <div className={styles.dropZoneContent}>
                <p>📷</p>
                <p>Glisser-déposer ou cliquer</p>
                <p className={styles.dropZoneHint}>JPG, PNG, WebP (max 10 MB)</p>
              </div>
            )}
          </div>
          
          <input
            ref={backLabelRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/webp"
            onChange={(e) => handleFileSelect(e, 'back_label')}
            className={styles.fileInput}
          />
        </div>

        {/* Bottle Image */}
        <div className={styles.uploadSection}>
          <h4 className={styles.sectionTitle}>Bouteille complète</h4>
          <p className={styles.sectionDescription}>
            Pour affichage catalogue
          </p>
          
          <div
            className={`${styles.dropZone} ${bottleDrag ? styles.dragActive : ''}`}
            onDragOver={handleDragOver}
            onDragEnter={(e) => handleDragEnter(e, 'bottle')}
            onDragLeave={(e) => handleDragLeave(e, 'bottle')}
            onDrop={(e) => handleDrop(e, 'bottle')}
            onClick={() => bottleRef.current?.click()}
          >
            {bottlePreview ? (
              <div className={styles.previewContainer}>
                <img
                  src={bottlePreview.url}
                  alt="Bottle preview"
                  className={styles.preview}
                />
                <button
                  type="button"
                  className={styles.clearButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    clearPreview('bottle');
                  }}
                >
                  ×
                </button>
              </div>
            ) : existingImages?.bottle_image ? (
              <div className={styles.previewContainer}>
                <img
                  src={`http://192.168.1.100:8000/${existingImages.bottle_image}`}
                  alt="Bottle"
                  className={styles.preview}
                />
                <div className={styles.existingLabel}>Actuel</div>
              </div>
            ) : (
              <div className={styles.dropZoneContent}>
                <p>🍷</p>
                <p>Glisser-déposer ou cliquer</p>
                <p className={styles.dropZoneHint}>JPG, PNG, WebP (max 10 MB)</p>
              </div>
            )}
          </div>
          
          <input
            ref={bottleRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/webp"
            onChange={(e) => handleFileSelect(e, 'bottle')}
            className={styles.fileInput}
          />
        </div>
      </div>

      {/* Upload button and messages */}
      <div className={styles.uploadActions}>
        <button
          type="button"
          onClick={handleUpload}
          disabled={uploading || (!frontLabelPreview && !backLabelPreview && !bottlePreview)}
          className={styles.uploadButton}
        >
          {uploading ? 'Téléchargement...' : 'Télécharger les images'}
        </button>

        {uploading && (
          <div className={styles.progressBar}>
            <div
              className={styles.progressFill}
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        )}

        {error && (
          <div className={styles.error}>
            ❌ {error}
          </div>
        )}

        {success && (
          <div className={styles.success}>
            ✅ {success}
          </div>
        )}
      </div>
    </div>
  );
}
