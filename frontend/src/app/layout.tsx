import type { Metadata } from 'next'
import './globals.css'
import Navigation from './components/Navigation'
import { LanguageProvider } from './context/LanguageContext'
import { AuthProvider } from '@/contexts/AuthContext'

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
        <AuthProvider>
          <LanguageProvider>
            <Navigation />
            {children}
          </LanguageProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
