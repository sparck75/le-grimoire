-- Le Grimoire Database Schema
-- PostgreSQL initialization script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    oauth_provider VARCHAR(50) NOT NULL, -- 'google' or 'apple'
    oauth_provider_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(oauth_provider, oauth_provider_id)
);

-- Create recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    ingredients TEXT[] NOT NULL,
    instructions TEXT NOT NULL,
    servings INTEGER,
    prep_time INTEGER, -- in minutes
    cook_time INTEGER, -- in minutes
    total_time INTEGER, -- in minutes
    category VARCHAR(100),
    cuisine VARCHAR(100),
    image_url TEXT,
    original_image_url TEXT,
    source VARCHAR(255),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create recipe_tags table
CREATE TABLE IF NOT EXISTS recipe_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(recipe_id, tag)
);

-- Create grocery_stores table
CREATE TABLE IF NOT EXISTS grocery_stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL, -- 'iga', 'metro'
    website_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create grocery_specials table
CREATE TABLE IF NOT EXISTS grocery_specials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID REFERENCES grocery_stores(id) ON DELETE CASCADE,
    product_name VARCHAR(500) NOT NULL,
    product_category VARCHAR(100),
    original_price DECIMAL(10, 2),
    special_price DECIMAL(10, 2) NOT NULL,
    discount_percentage DECIMAL(5, 2),
    unit VARCHAR(50), -- 'lb', 'kg', 'unit', 'l'
    description TEXT,
    image_url TEXT,
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create shopping_lists table
CREATE TABLE IF NOT EXISTS shopping_lists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create shopping_list_items table
CREATE TABLE IF NOT EXISTS shopping_list_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shopping_list_id UUID REFERENCES shopping_lists(id) ON DELETE CASCADE,
    recipe_id UUID REFERENCES recipes(id) ON DELETE SET NULL,
    ingredient_name VARCHAR(500) NOT NULL,
    quantity DECIMAL(10, 2),
    unit VARCHAR(50),
    is_purchased BOOLEAN DEFAULT false,
    matched_special_id UUID REFERENCES grocery_specials(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create favorites table
CREATE TABLE IF NOT EXISTS favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, recipe_id)
);

-- Create ocr_jobs table for tracking OCR processing
CREATE TABLE IF NOT EXISTS ocr_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    image_path TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    extracted_text TEXT,
    parsed_recipe_id UUID REFERENCES recipes(id) ON DELETE SET NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_recipes_user_id ON recipes(user_id);
CREATE INDEX IF NOT EXISTS idx_recipes_is_public ON recipes(is_public);
CREATE INDEX IF NOT EXISTS idx_recipes_created_at ON recipes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recipe_tags_recipe_id ON recipe_tags(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_tags_tag ON recipe_tags(tag);
CREATE INDEX IF NOT EXISTS idx_grocery_specials_store_id ON grocery_specials(store_id);
CREATE INDEX IF NOT EXISTS idx_grocery_specials_valid_dates ON grocery_specials(valid_from, valid_until);
CREATE INDEX IF NOT EXISTS idx_shopping_list_items_list_id ON shopping_list_items(shopping_list_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_ocr_jobs_user_id ON ocr_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_ocr_jobs_status ON ocr_jobs(status);

-- Insert default grocery stores
INSERT INTO grocery_stores (name, code, website_url) VALUES
    ('IGA', 'iga', 'https://www.iga.net'),
    ('Metro', 'metro', 'https://www.metro.ca')
ON CONFLICT (code) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recipes_updated_at BEFORE UPDATE ON recipes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_grocery_specials_updated_at BEFORE UPDATE ON grocery_specials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shopping_lists_updated_at BEFORE UPDATE ON shopping_lists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shopping_list_items_updated_at BEFORE UPDATE ON shopping_list_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ocr_jobs_updated_at BEFORE UPDATE ON ocr_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
