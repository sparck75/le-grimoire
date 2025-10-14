import type { Metadata } from 'next'
import './globals.css'
import Navigation from './components/Navigation'
import { LanguageProvider } from './context/LanguageContext'

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
      <body>
        <LanguageProvider>
          <Navigation />
          {children}
        </LanguageProvider>
      </body>
    </html>
  )
}
