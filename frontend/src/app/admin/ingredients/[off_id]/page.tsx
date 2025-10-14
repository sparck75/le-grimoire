'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

interface Ingredient {
  id: string;
  off_id: string;
  name: string;
  names: Record<string, string>;
  english_name: string;
  french_name: string;
  parents: string[];
  children: string[];
  properties: Record<string, string>;
  is_vegan: boolean;
  is_vegetarian: boolean;
  wikidata_id?: string;
  ciqual_food_code?: string;
  custom: boolean;
}

interface IngredientDetailProps {
  params: {
    off_id: string;
  };
}

async function getIngredientDetails(off_id: string): Promise<Ingredient | null> {
  try {
    const url = `http://localhost:8000/api/admin/ingredients/${encodeURIComponent(off_id)}`;
    console.log(`Fetching ingredient from: ${url}`);
    
    const response = await fetch(url, { cache: 'no-store' });
    
    if (!response.ok) {
      console.error(`Failed to fetch ingredient: ${response.status}`);
      return null;
    }
    
    const data = await response.json();
    console.log(`Successfully fetched ingredient:`, data.off_id);
    return data;
  } catch (error) {
    console.error('Error fetching ingredient details:', error);
    return null;
  }
}

async function getParentIngredients(parentIds: string[]): Promise<Ingredient[]> {
  try {
    const parentPromises = parentIds.map(async (parentId) => {
      const response = await fetch(
        `http://localhost:8000/api/admin/ingredients/${encodeURIComponent(parentId)}`,
        { cache: 'no-store' }
      );
      if (response.ok) {
        return await response.json();
      }
      return null;
    });
    
    const parents = await Promise.all(parentPromises);
    return parents.filter((p): p is Ingredient => p !== null);
  } catch (error) {
    console.error('Error fetching parent ingredients:', error);
    return [];
  }
}

async function getChildIngredients(childIds: string[]): Promise<Ingredient[]> {
  try {
    const childPromises = childIds.map(async (childId) => {
      const response = await fetch(
        `http://localhost:8000/api/admin/ingredients/${encodeURIComponent(childId)}`,
        { cache: 'no-store' }
      );
      if (response.ok) {
        return await response.json();
      }
      return null;
    });
    
    const children = await Promise.all(childPromises);
    return children.filter((c): c is Ingredient => c !== null);
  } catch (error) {
    console.error('Error fetching child ingredients:', error);
    return [];
  }
}

export default function IngredientDetailPage({ params }: IngredientDetailProps) {
  const [ingredient, setIngredient] = useState<Ingredient | null>(null);
  const [parents, setParents] = useState<Ingredient[]>([]);
  const [children, setChildren] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadIngredient() {
      try {
        setLoading(true);
        const decodedOffId = decodeURIComponent(params.off_id);
        const ingredientData = await getIngredientDetails(decodedOffId);
        
        if (!ingredientData) {
          setError(`Ingredient with ID "${decodedOffId}" not found`);
          return;
        }
        
        setIngredient(ingredientData);
        
        // Load parents and children
        if (ingredientData.parents.length > 0) {
          const parentsData = await getParentIngredients(ingredientData.parents);
          setParents(parentsData);
        }
        
        if (ingredientData.children.length > 0) {
          const childrenData = await getChildIngredients(ingredientData.children);
          setChildren(childrenData);
        }
      } catch (err) {
        setError('Failed to load ingredient');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    
    loadIngredient();
  }, [params.off_id]);

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Loading...</h1>
      </div>
    );
  }
  
  if (error || !ingredient) {
    return (
      <div style={{ padding: '2rem' }}>
        <h1>Ingredient Not Found</h1>
        <p>{error || 'Ingredient not found'}</p>
        <Link href="/admin/ingredients" style={{ color: '#0070f3', textDecoration: 'underline' }}>
          ← Back to Ingredients
        </Link>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Breadcrumb Navigation */}
      <nav style={{ marginBottom: '2rem', fontSize: '0.9rem' }}>
        <Link href="/admin/ingredients" style={{ color: '#0070f3', textDecoration: 'none' }}>
          Ingredients
        </Link>
        {parents.map((parent) => (
          <span key={parent.off_id}>
            {' → '}
            <Link href={`/admin/ingredients/${parent.off_id}`} style={{ color: '#0070f3', textDecoration: 'none' }}>
              {parent.english_name || parent.name}
            </Link>
          </span>
        ))}
        <span style={{ color: '#666' }}>
          {' → '}
          {ingredient.english_name || ingredient.name}
        </span>
      </nav>

      {/* Ingredient Header */}
      <div style={{ marginBottom: '2rem', borderBottom: '2px solid #eee', paddingBottom: '1rem' }}>
        <h1 style={{ fontSize: '2.5rem', margin: '0 0 1rem 0' }}>
          {ingredient.english_name || ingredient.name}
        </h1>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div>
            <strong>Off ID:</strong> <code style={{ background: '#f5f5f5', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>{ingredient.off_id}</code>
          </div>
          <div>
            <strong>English Name:</strong> {ingredient.english_name || 'N/A'}
          </div>
          <div>
            <strong>French Name:</strong> {ingredient.french_name || 'N/A'}
          </div>
          <div>
            <strong>Vegan:</strong>{' '}
            <span style={{ 
              background: ingredient.is_vegan ? '#d4edda' : '#f8d7da',
              color: ingredient.is_vegan ? '#155724' : '#721c24',
              padding: '0.2rem 0.5rem',
              borderRadius: '4px',
              fontSize: '0.9rem'
            }}>
              {ingredient.is_vegan ? '✅ Yes' : '❌ No'}
            </span>
          </div>
          <div>
            <strong>Vegetarian:</strong>{' '}
            <span style={{ 
              background: ingredient.is_vegetarian ? '#d4edda' : '#f8d7da',
              color: ingredient.is_vegetarian ? '#155724' : '#721c24',
              padding: '0.2rem 0.5rem',
              borderRadius: '4px',
              fontSize: '0.9rem'
            }}>
              {ingredient.is_vegetarian ? '✅ Yes' : '❌ No'}
            </span>
          </div>
          {ingredient.wikidata_id && (
            <div>
              <strong>Wikidata:</strong>{' '}
              <a
                href={`https://www.wikidata.org/wiki/${ingredient.wikidata_id}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#0070f3' }}
              >
                {ingredient.wikidata_id}
              </a>
            </div>
          )}
          {ingredient.ciqual_food_code && (
            <div>
              <strong>CIQUAL Code:</strong> {ingredient.ciqual_food_code}
            </div>
          )}
          <div>
            <strong>Source:</strong>{' '}
            <span style={{ 
              background: ingredient.custom ? '#fff3cd' : '#d1ecf1',
              color: ingredient.custom ? '#856404' : '#0c5460',
              padding: '0.2rem 0.5rem',
              borderRadius: '4px',
              fontSize: '0.9rem'
            }}>
              {ingredient.custom ? '✏️ Custom' : '🌐 OpenFoodFacts'}
            </span>
          </div>
        </div>
      </div>

      {/* All Language Names */}
      {ingredient.names && Object.keys(ingredient.names).length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            🌍 Names in All Languages ({Object.keys(ingredient.names).length})
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '0.5rem' }}>
            {Object.entries(ingredient.names).map(([lang, name]) => (
              <div key={lang} style={{ padding: '0.5rem', background: '#f8f9fa', borderRadius: '4px' }}>
                <strong style={{ color: '#666', fontSize: '0.85rem', textTransform: 'uppercase' }}>{lang}:</strong>{' '}
                {name}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Properties */}
      {ingredient.properties && Object.keys(ingredient.properties).length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            ⚙️ Properties
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.5rem' }}>
            {Object.entries(ingredient.properties).map(([key, value]) => (
              <div key={key} style={{ padding: '0.5rem', background: '#f8f9fa', borderRadius: '4px' }}>
                <strong>{key}:</strong> {value}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Parent Ingredients */}
      {parents.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            ⬆️ Parent Ingredients ({parents.length})
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
            {parents.map((parent) => (
              <Link
                key={parent.off_id}
                href={`/admin/ingredients/${parent.off_id}`}
                style={{
                  display: 'block',
                  padding: '1rem',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  color: 'inherit',
                  transition: 'all 0.2s',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = '#0070f3';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = '#ddd';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ fontWeight: 'bold' }}>{parent.english_name || parent.name}</div>
                <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.25rem' }}>
                  {parent.off_id}
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Child Ingredients */}
      {children.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            ⬇️ Child Ingredients ({children.length})
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
            {children.map((child) => (
              <Link
                key={child.off_id}
                href={`/admin/ingredients/${child.off_id}`}
                style={{
                  display: 'block',
                  padding: '1rem',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  color: 'inherit',
                  transition: 'all 0.2s',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = '#0070f3';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = '#ddd';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ fontWeight: 'bold' }}>{child.english_name || child.name}</div>
                <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.25rem' }}>
                  {child.off_id}
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* No children message */}
      {children.length === 0 && parents.length === 0 && (
        <section style={{ padding: '2rem', background: '#f8f9fa', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🧪</div>
          <p style={{ color: '#666' }}>This is a standalone ingredient with no parent or child relationships.</p>
        </section>
      )}

      {/* Back button */}
      <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid #eee' }}>
        <Link href="/admin/ingredients" style={{ color: '#0070f3', textDecoration: 'underline' }}>
          ← Back to Ingredients List
        </Link>
      </div>
    </div>
  );
}
