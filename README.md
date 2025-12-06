# Miss France Prediction App

A web application for predicting and scoring Miss France competition results.

## Features

- User registration and authentication
- Prediction system for top 3 candidates
- Automatic score calculation (5 pts for exact position, 3 pts for podium)
- Real-time leaderboard with breakdown scores
- Admin panel for entering final results
- Vote toggle system (enable/disable predictions)

## Setup

### Local Development

1. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Set up PostgreSQL database:
```bash
createdb Miss
```

3. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Initialize database:
```bash
python init_db.py
```

5. Run the app:
```bash
python app.py
```

The app will be available at `http://localhost:5002`

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions.

## Environment Variables

- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: PostgreSQL connection string
- `PORT`: Server port (default: 5002)
- `FLASK_DEBUG`: Enable debug mode (default: False)

## License

Private project
