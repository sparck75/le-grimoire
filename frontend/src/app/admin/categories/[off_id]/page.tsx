'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

interface Category {
  off_id: string;
  name: string;
  names: Record<string, string>;
  english_name: string;
  french_name: string;
  icon?: string;
  parents: string[];
  children: string[];
  wikidata_id?: string;
  is_top_level: boolean;
}

interface CategoryDetailProps {
  params: {
    off_id: string;
  };
}

async function getCategoryDetails(off_id: string): Promise<Category | null> {
  try {
    // Client component always uses localhost
    const url = `http://localhost:8000/api/admin/ingredients/categories/${encodeURIComponent(off_id)}`;
    console.log(`Fetching category from: ${url}`);
    
    const response = await fetch(url, { cache: 'no-store' });
    
    console.log(`Response status: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Failed to fetch category: ${response.status} ${response.statusText}`, errorText);
      return null;
    }
    
    const data = await response.json();
    console.log(`Successfully fetched category:`, data.off_id);
    return data;
  } catch (error) {
    console.error('Error fetching category details:', error);
    return null;
  }
}

async function getParentCategories(parentIds: string[]): Promise<Category[]> {
  try {
    const parentPromises = parentIds.map(async (parentId) => {
      const response = await fetch(
        `http://localhost:8000/api/admin/ingredients/categories/${encodeURIComponent(parentId)}`,
        { cache: 'no-store' }
      );
      if (response.ok) {
        return await response.json();
      }
      return null;
    });
    
    const parents = await Promise.all(parentPromises);
    return parents.filter((p): p is Category => p !== null);
  } catch (error) {
    console.error('Error fetching parent categories:', error);
    return [];
  }
}

async function getChildCategories(childIds: string[]): Promise<Category[]> {
  try {
    const childPromises = childIds.map(async (childId) => {
      const response = await fetch(
        `http://localhost:8000/api/admin/ingredients/categories/${encodeURIComponent(childId)}`,
        { cache: 'no-store' }
      );
      if (response.ok) {
        return await response.json();
      }
      return null;
    });
    
    const children = await Promise.all(childPromises);
    return children.filter((c): c is Category => c !== null);
  } catch (error) {
    console.error('Error fetching child categories:', error);
    return [];
  }
}

export default function CategoryDetailPage({ params }: CategoryDetailProps) {
  const [category, setCategory] = useState<Category | null>(null);
  const [parents, setParents] = useState<Category[]>([]);
  const [children, setChildren] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCategory() {
      try {
        setLoading(true);
        // Decode the URL parameter since it comes encoded (e.g., "en%3Awines-from-italy" -> "en:wines-from-italy")
        const decodedOffId = decodeURIComponent(params.off_id);
        const categoryData = await getCategoryDetails(decodedOffId);
        
        if (!categoryData) {
          setError(`Category with ID "${decodedOffId}" not found`);
          return;
        }
        
        setCategory(categoryData);
        
        // Load parents and children
        if (categoryData.parents.length > 0) {
          const parentsData = await getParentCategories(categoryData.parents);
          setParents(parentsData);
        }
        
        if (categoryData.children.length > 0) {
          const childrenData = await getChildCategories(categoryData.children);
          setChildren(childrenData);
        }
      } catch (err) {
        setError('Failed to load category');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    
    loadCategory();
  }, [params.off_id]);

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Loading...</h1>
      </div>
    );
  }
  
  if (error || !category) {
    return (
      <div style={{ padding: '2rem' }}>
        <h1>Category Not Found</h1>
        <p>{error || 'Category not found'}</p>
        <Link href="/admin/categories" style={{ color: '#0070f3', textDecoration: 'underline' }}>
          ← Back to Categories
        </Link>
      </div>
    );
  }
  
  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Breadcrumb Navigation */}
      <nav style={{ marginBottom: '2rem', fontSize: '0.9rem' }}>
        <Link href="/admin/categories" style={{ color: '#0070f3', textDecoration: 'none' }}>
          Categories
        </Link>
        {parents.map((parent) => (
          <span key={parent.off_id}>
            {' → '}
            <Link href={`/admin/categories/${parent.off_id}`} style={{ color: '#0070f3', textDecoration: 'none' }}>
              {parent.icon} {parent.english_name || parent.name}
            </Link>
          </span>
        ))}
        <span style={{ color: '#666' }}>
          {' → '}
          {category.icon} {category.english_name || category.name}
        </span>
      </nav>

      {/* Category Header */}
      <div style={{ marginBottom: '2rem', borderBottom: '2px solid #eee', paddingBottom: '1rem' }}>
        <h1 style={{ fontSize: '2.5rem', margin: '0 0 1rem 0' }}>
          {category.icon && <span style={{ marginRight: '0.5rem' }}>{category.icon}</span>}
          {category.english_name || category.name}
        </h1>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div>
            <strong>Off ID:</strong> <code style={{ background: '#f5f5f5', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>{category.off_id}</code>
          </div>
          <div>
            <strong>English Name:</strong> {category.english_name || 'N/A'}
          </div>
          <div>
            <strong>French Name:</strong> {category.french_name || 'N/A'}
          </div>
          {category.wikidata_id && (
            <div>
              <strong>Wikidata:</strong>{' '}
              <a
                href={`https://www.wikidata.org/wiki/${category.wikidata_id}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#0070f3' }}
              >
                {category.wikidata_id}
              </a>
            </div>
          )}
          <div>
            <strong>Type:</strong>{' '}
            <span style={{ 
              background: category.is_top_level ? '#d4edda' : '#f8f9fa',
              color: category.is_top_level ? '#155724' : '#666',
              padding: '0.2rem 0.5rem',
              borderRadius: '4px',
              fontSize: '0.9rem'
            }}>
              {category.is_top_level ? '🏠 Top Level' : '📁 Sub-category'}
            </span>
          </div>
        </div>
      </div>

      {/* Parent Categories */}
      {parents.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            ⬆️ Parent Categories ({parents.length})
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
            {parents.map((parent) => (
              <Link
                key={parent.off_id}
                href={`/admin/categories/${parent.off_id}`}
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
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{parent.icon || '📁'}</div>
                <div style={{ fontWeight: 'bold' }}>{parent.english_name || parent.name}</div>
                <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
                  {parent.children.length} subcategories
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Child Categories */}
      {children.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            ⬇️ Subcategories ({children.length})
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
            {children.map((child) => (
              <Link
                key={child.off_id}
                href={`/admin/categories/${child.off_id}`}
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
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{child.icon || '📁'}</div>
                <div style={{ fontWeight: 'bold' }}>{child.english_name || child.name}</div>
                <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
                  {child.children.length} subcategories
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* No children message */}
      {children.length === 0 && (
        <section style={{ padding: '2rem', background: '#f8f9fa', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🏁</div>
          <p style={{ color: '#666' }}>This is a leaf category with no subcategories.</p>
        </section>
      )}

      {/* Back button */}
      <div style={{ marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid #eee' }}>
        <Link href="/admin/categories" style={{ color: '#0070f3', textDecoration: 'underline' }}>
          ← Back to Categories List
        </Link>
      </div>
    </div>
  );
}
