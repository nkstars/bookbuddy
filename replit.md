# Book Recommender System

## Overview

A Streamlit-based book recommendation application that leverages Google's Gemini AI to provide intelligent book suggestions. The system analyzes user queries to understand preferences and generates personalized recommendations with book covers from Open Library. Features special handling for anime-related requests, mixing anime-specific content with thematically similar general literature.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Layout**: Wide layout with collapsed sidebar for immersive experience
- **Theme**: Dark mode interface for user comfort
- **State Management**: Session-based with persistent search functionality allowing continuous queries

**Rationale**: Streamlit chosen for rapid development and built-in UI components. Dark mode reduces eye strain and provides modern aesthetic. Wide layout maximizes screen real estate for displaying multiple book recommendations.

### AI Integration Layer
- **Model**: Google Gemini 1.5 Flash (free-tier model)
- **Caching**: Resource-level caching of model initialization to minimize API overhead
- **Dual-prompt Strategy**: 
  1. Anime detection prompt to identify Japanese animation/manga requests
  2. Context-aware recommendation prompt that adapts based on query type

**Rationale**: Gemini 1.5 Flash provides fast response times critical for interactive recommendations. Two-stage prompting ensures appropriate book mixing (anime + general) when relevant. Caching prevents redundant API initialization on reruns.

### Recommendation Logic
- **Output Format**: Exactly 7 recommendations per query
- **Anime-aware Mixing**: When anime-related query detected, provides 3-4 anime-related books + 3-4 thematically similar general books
- **Metadata Structure**: Each recommendation includes title (series name only), author, 2-3 sentence summary, and genre/category

**Rationale**: Seven recommendations strike balance between choice and overwhelming users. Anime-aware mixing expands user horizons beyond single medium while respecting original interest. Series-level naming avoids confusion from volume numbers.

### Cover Image Retrieval
- **Source**: Open Library Cover API
- **Fallback Strategy**: Default placeholder image when covers unavailable
- **Format**: PIL Image processing for consistent display

**Rationale**: Open Library provides free, reliable cover images. Fallback ensures UI never displays broken images. PIL enables image manipulation if needed for responsive display.

### Performance Optimization
- **API Key Configuration**: Environment variable with hardcoded fallback for development
- **Model Caching**: `@st.cache_resource` decorator prevents re-initialization
- **Minimal Loading**: Streamlined prompts and single-pass recommendations reduce latency

**Rationale**: Caching eliminates redundant expensive operations. Environment variables enable secure production deployment while fallback aids development workflow.

## External Dependencies

### AI Service
- **Google Generative AI (Gemini)**: Core recommendation engine
  - API Key required: Configured via `GOOGLE_API_KEY` environment variable
  - Model: `gemini-1.5-flash` (free tier)
  - Purpose: Natural language understanding and book recommendation generation

### Image Service  
- **Open Library Cover API**: Book cover image source
  - Endpoint: Open Library covers database
  - Purpose: Retrieve cover images for recommended books
  - No authentication required

### Python Libraries
- **Streamlit**: Web application framework
- **google-generativeai**: Official Gemini SDK
- **requests**: HTTP client for Open Library API calls
- **PIL (Pillow)**: Image processing and manipulation
- **os**: Environment variable access
- **time**: Potential rate limiting or delays
- **io**: In-memory binary streams for image handling

### Environment Configuration
- Required environment variable: `GOOGLE_API_KEY` (falls back to hardcoded key in development)
- No database dependencies
- No authentication system required