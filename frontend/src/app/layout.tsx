import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Le Grimoire - Vos recettes de cuisine',
  description: 'Extraire, sauvegarder et partager des recettes de cuisine avec OCR',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  )
}
