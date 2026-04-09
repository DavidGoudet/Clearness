# Development Workflow

## Starting Development

1. **Backend**: Activate venv and start Django server
   ```bash
   cd backend && source venv/bin/activate && python manage.py runserver
   ```

2. **Frontend**: Start Vite dev server
   ```bash
   cd frontend && npm run dev
   ```

## Adding a New Feature

1. Define or update Django models in `backend/api/models.py`
2. Run `python manage.py makemigrations && python manage.py migrate`
3. Create/update serializers in `backend/api/serializers.py`
4. Create/update views in `backend/api/views.py`
5. Register URL patterns in `backend/api/urls.py`
6. Update frontend API calls in `frontend/src/api.js`
7. Build React components in `frontend/src/components/`
8. Run tests: `python manage.py test` and `npm run lint`

## Pre-commit Checklist

- [ ] Django migrations are up to date
- [ ] API endpoints return correct JSON
- [ ] Frontend lint passes
- [ ] Tests pass
