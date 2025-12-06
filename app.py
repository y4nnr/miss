from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'miss-france-2026-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/Miss')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='user', lazy=True)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    region = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))
    age = db.Column(db.Integer)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_place_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    second_place_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    third_place_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    score = db.Column(db.Integer, default=0)
    
    first_place = db.relationship('Candidate', foreign_keys=[first_place_id])
    second_place = db.relationship('Candidate', foreign_keys=[second_place_id])
    third_place = db.relationship('Candidate', foreign_keys=[third_place_id])

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_place_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=True)
    second_place_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=True)
    third_place_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_final = db.Column(db.Boolean, default=False)
    
    first_place = db.relationship('Candidate', foreign_keys=[first_place_id])
    second_place = db.relationship('Candidate', foreign_keys=[second_place_id])
    third_place = db.relationship('Candidate', foreign_keys=[third_place_id])

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(500), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    if not current_user.is_authenticated:
        flash('Accès refusé. Veuillez vous connecter.', 'error')
        return redirect(url_for('login')), 403
    flash('Accès refusé. Vous n\'avez pas les permissions nécessaires.', 'error')
    return redirect(url_for('dashboard')), 403

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return render_template('404.html'), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validation
        if not username or not password or not password_confirm:
            flash('Veuillez remplir tous les champs.', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Le nom d\'utilisateur doit contenir au moins 3 caractères.', 'error')
            return render_template('register.html')
        
        if len(password) < 4:
            flash('Le mot de passe doit contenir au moins 4 caractères.', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('register.html')
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.', 'error')
            return render_template('register.html')
        
        # Create new user
        try:
            new_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                is_admin=False
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la création du compte. Veuillez réessayer.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def calculate_breakdown(prediction, final_result):
    """
    Calculate points breakdown for a prediction using the EXACT same logic as calculate_scores().
    Returns a dict with 'first', 'second', 'third' keys containing point values.
    """
    breakdown = {'first': 0, 'second': 0, 'third': 0}
    
    if not final_result:
        return breakdown
    
    # Get final result IDs - use the same approach as calculate_scores()
    final_first = final_result.first_place_id
    final_second = final_result.second_place_id
    final_third = final_result.third_place_id
    
    if not all([final_first, final_second, final_third]):
        return breakdown
    
    # Calculate points for first position - EXACT same logic as calculate_scores()
    if prediction.first_place_id == final_first:
        breakdown['first'] = 5
    elif prediction.first_place_id in [final_second, final_third]:
        breakdown['first'] = 3
    else:
        breakdown['first'] = 0
    
    # Calculate points for second position - EXACT same logic as calculate_scores()
    if prediction.second_place_id == final_second:
        breakdown['second'] = 5
    elif prediction.second_place_id in [final_first, final_third]:
        breakdown['second'] = 3
    else:
        breakdown['second'] = 0
    
    # Calculate points for third position - EXACT same logic as calculate_scores()
    if prediction.third_place_id == final_third:
        breakdown['third'] = 5
    elif prediction.third_place_id in [final_first, final_second]:
        breakdown['third'] = 3
    else:
        breakdown['third'] = 0
    
    return breakdown

@app.context_processor
def inject_position_points():
    """Make position_points function available in all templates"""
    return dict(position_points=lambda pred, result, pos: calculate_breakdown(pred, result).get(pos, 0))

def get_votes_enabled():
    """Get votes enabled status from config"""
    config = Config.query.filter_by(key='votes_enabled').first()
    if config:
        return config.value.lower() == 'true'
    # Default to True if not set
    return True

def set_votes_enabled(enabled):
    """Set votes enabled status in config"""
    config = Config.query.filter_by(key='votes_enabled').first()
    if config:
        config.value = 'true' if enabled else 'false'
        config.updated_at = datetime.utcnow()
    else:
        config = Config(key='votes_enabled', value='true' if enabled else 'false')
        db.session.add(config)
    db.session.commit()

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """Central dashboard showing user's prediction, all predictions, and leaderboard"""
    # Admin should not make predictions, only view and manage results
    if current_user.is_admin:
        # Admin dashboard shows votes toggle and delete results button
        candidates = Candidate.query.order_by(Candidate.region).all()
        user_prediction = None  # Admin doesn't have predictions
        final_result = Result.query.filter_by(is_final=True).first()
        votes_enabled = get_votes_enabled()
        return render_template('dashboard.html', 
                             candidates=candidates, 
                             user_prediction=user_prediction,
                             user_points_breakdown=None,
                             all_predictions=[],
                             final_result=final_result,
                             votes_enabled=votes_enabled)
    
    candidates = Candidate.query.order_by(Candidate.region).all()
    user_prediction = Prediction.query.filter_by(user_id=current_user.id).first()
    # Re-query final_result to ensure we have fresh data - don't use refresh, just re-query
    final_result = Result.query.filter_by(is_final=True).first()
    
    # Get all predictions - sorted by score if results are final, otherwise by username
    if final_result and (final_result.first_place_id is not None and 
                         final_result.second_place_id is not None and 
                         final_result.third_place_id is not None):
        # Sort by score descending (NULLs last), then by username
        predictions_sorted = Prediction.query.join(User).order_by(
            func.coalesce(Prediction.score, -1).desc(), 
            User.username
        ).all()
        # Calculate ranks for each prediction
        all_predictions = []
        current_rank = 1
        previous_score = None
        for pred in predictions_sorted:
            if previous_score is not None and pred.score < previous_score:
                current_rank = len(all_predictions) + 1
            # Calculate points breakdown using the simple function
            points_breakdown = calculate_breakdown(pred, final_result)
            all_predictions.append({
                'prediction': pred,
                'rank': current_rank,
                'points_breakdown': points_breakdown
            })
            previous_score = pred.score
    else:
        # Sort by username when no results yet
        predictions_sorted = Prediction.query.join(User).order_by(User.username).all()
        all_predictions = [{'prediction': pred, 'rank': None, 'points_breakdown': None} for pred in predictions_sorted]
    
    # Get votes enabled status
    votes_enabled = get_votes_enabled()
    
    # Handle prediction submission (only for non-admin users and if votes are enabled)
    if request.method == 'POST' and not current_user.is_admin:
        # Check if votes are enabled - if not, reject the submission
        if not votes_enabled:
            flash('Les votes sont désactivés. Vous ne pouvez plus modifier vos prédictions après l\'entrée des résultats finaux.', 'error')
            # Recalculate user points breakdown for display
            user_points_breakdown = None
            if user_prediction and final_result and all([final_result.first_place_id, final_result.second_place_id, final_result.third_place_id]):
                user_points_breakdown = calculate_breakdown(user_prediction, final_result)
            return render_template('dashboard.html', 
                                 candidates=candidates, 
                                 user_prediction=user_prediction,
                                 user_points_breakdown=user_points_breakdown,
                                 all_predictions=all_predictions,
                                 final_result=final_result,
                                 votes_enabled=votes_enabled)
        
        # Votes are enabled, proceed with submission
        first_id = request.form.get('first_place')
        second_id = request.form.get('second_place')
        third_id = request.form.get('third_place')
        
        # Validation
        if not all([first_id, second_id, third_id]):
            flash('Veuillez sélectionner les trois places.', 'error')
            user_points_breakdown = None
            if (user_prediction and final_result and 
                final_result.first_place_id is not None and 
                final_result.second_place_id is not None and 
                final_result.third_place_id is not None):
                user_points_breakdown = calculate_breakdown(user_prediction, final_result)
            return render_template('dashboard.html', 
                                 candidates=candidates, 
                                 user_prediction=user_prediction,
                                 user_points_breakdown=user_points_breakdown,
                                 all_predictions=all_predictions,
                                 final_result=final_result,
                                 votes_enabled=votes_enabled)
        
        if first_id == second_id or first_id == third_id or second_id == third_id:
            flash('Vous ne pouvez pas sélectionner la même candidate plusieurs fois.', 'error')
            user_points_breakdown = None
            if (user_prediction and final_result and 
                final_result.first_place_id is not None and 
                final_result.second_place_id is not None and 
                final_result.third_place_id is not None):
                user_points_breakdown = calculate_breakdown(user_prediction, final_result)
            return render_template('dashboard.html', 
                                 candidates=candidates, 
                                 user_prediction=user_prediction,
                                 user_points_breakdown=user_points_breakdown,
                                 all_predictions=all_predictions,
                                 final_result=final_result,
                                 votes_enabled=votes_enabled)
        
        if user_prediction:
            # Update existing prediction
            user_prediction.first_place_id = int(first_id)
            user_prediction.second_place_id = int(second_id)
            user_prediction.third_place_id = int(third_id)
            user_prediction.updated_at = datetime.utcnow()
            
            # Recalculate score if final results exist
            final_result = Result.query.filter_by(is_final=True).first()
            if final_result and all([final_result.first_place_id, final_result.second_place_id, final_result.third_place_id]):
                score = 0
                if user_prediction.first_place_id == final_result.first_place_id:
                    score += 5
                elif user_prediction.first_place_id in [final_result.second_place_id, final_result.third_place_id]:
                    score += 3
                
                if user_prediction.second_place_id == final_result.second_place_id:
                    score += 5
                elif user_prediction.second_place_id in [final_result.first_place_id, final_result.third_place_id]:
                    score += 3
                
                if user_prediction.third_place_id == final_result.third_place_id:
                    score += 5
                elif user_prediction.third_place_id in [final_result.first_place_id, final_result.second_place_id]:
                    score += 3
                
                user_prediction.score = score
            
            flash('Votre prédiction a été mise à jour avec succès!', 'success')
        else:
            # Create new prediction
            user_prediction = Prediction(
                user_id=current_user.id,
                first_place_id=int(first_id),
                second_place_id=int(second_id),
                third_place_id=int(third_id),
                score=0  # Initialize score to 0
            )
            db.session.add(user_prediction)
            flash('Votre prédiction a été enregistrée avec succès!', 'success')
        
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    # Calculate points breakdown for user prediction if it exists
    user_points_breakdown = None
    if (user_prediction and final_result and 
        final_result.first_place_id is not None and 
        final_result.second_place_id is not None and 
        final_result.third_place_id is not None):
        user_points_breakdown = calculate_breakdown(user_prediction, final_result)
    
    return render_template('dashboard.html', 
                         candidates=candidates, 
                         user_prediction=user_prediction,
                         user_points_breakdown=user_points_breakdown,
                         all_predictions=all_predictions,
                         final_result=final_result,
                         votes_enabled=votes_enabled)

@app.route('/predictions', methods=['GET', 'POST'])
@login_required
def predictions():
    """Legacy route - redirect to dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/candidates')
@login_required
def candidates():
    candidates = Candidate.query.order_by(Candidate.region).all()
    return render_template('candidates.html', candidates=candidates)

@app.route('/all-predictions')
@login_required
def all_predictions():
    """Legacy route - redirect to dashboard"""
    return redirect(url_for('dashboard'))

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Accès refusé. Cette page est réservée aux administrateurs.', 'error')
            return redirect(url_for('predictions'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/toggle-votes', methods=['POST'])
@admin_required
def toggle_votes():
    """Toggle votes enabled/disabled"""
    enabled = request.form.get('enabled', 'false').lower() == 'true'
    set_votes_enabled(enabled)
    status = 'activés' if enabled else 'désactivés'
    flash(f'Les votes ont été {status}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/results', methods=['GET', 'POST'])
@admin_required
def results():
    """Set final results and calculate scores"""
    candidates = Candidate.query.order_by(Candidate.region).all()
    final_result = Result.query.filter_by(is_final=True).first()
    votes_enabled = get_votes_enabled()
    
    if request.method == 'POST':
        # Check if this is a delete request
        if request.form.get('action') == 'delete':
            if final_result:
                final_result.is_final = False
                # Reset all prediction scores to 0
                Prediction.query.update({Prediction.score: 0})
                db.session.commit()
                flash('Résultats finaux supprimés et scores réinitialisés!', 'success')
            else:
                flash('Aucun résultat final à supprimer.', 'error')
            return redirect(url_for('dashboard'))
        
        # Otherwise, it's a create/update request
        first_id = request.form.get('first_place')
        second_id = request.form.get('second_place')
        third_id = request.form.get('third_place')
        
        # Validation
        if not all([first_id, second_id, third_id]):
            flash('Veuillez sélectionner les trois places.', 'error')
            return render_template('results.html', candidates=candidates, final_result=final_result)
        
        if first_id == second_id or first_id == third_id or second_id == third_id:
            flash('Vous ne pouvez pas sélectionner la même candidate plusieurs fois.', 'error')
            return render_template('results.html', candidates=candidates, final_result=final_result)
        
        # Mark old results as not final
        Result.query.update({Result.is_final: False})
        
        # Create or update final result
        if final_result:
            final_result.first_place_id = int(first_id)
            final_result.second_place_id = int(second_id)
            final_result.third_place_id = int(third_id)
            final_result.is_final = True
        else:
            final_result = Result(
                first_place_id=int(first_id),
                second_place_id=int(second_id),
                third_place_id=int(third_id),
                is_final=True
            )
            db.session.add(final_result)
        
        db.session.commit()
        
        # Automatically disable votes when results are entered
        set_votes_enabled(False)
        
        # Calculate scores for all predictions
        calculate_scores()
        
        flash('Résultats finaux enregistrés et scores calculés! Les votes ont été automatiquement désactivés.', 'success')
        return redirect(url_for('results'))
    
    return render_template('results.html', candidates=candidates, final_result=final_result, votes_enabled=votes_enabled)

@app.route('/leaderboard')
@login_required
def leaderboard():
    """Legacy route - redirect to dashboard (leaderboard is now integrated in dashboard)"""
    return redirect(url_for('dashboard'))

def calculate_scores():
    """Calculate scores for all predictions based on final results"""
    final_result = Result.query.filter_by(is_final=True).first()
    
    if not final_result or not all([final_result.first_place_id, final_result.second_place_id, final_result.third_place_id]):
        return
    
    # Get all predictions
    predictions = Prediction.query.all()
    
    for pred in predictions:
        score = 0
        
        # Check each position
        # Perfect match: 5 points, correct candidate but wrong position: 3 points
        if pred.first_place_id == final_result.first_place_id:
            score += 5
        elif pred.first_place_id in [final_result.second_place_id, final_result.third_place_id]:
            score += 3
        
        if pred.second_place_id == final_result.second_place_id:
            score += 5
        elif pred.second_place_id in [final_result.first_place_id, final_result.third_place_id]:
            score += 3
        
        if pred.third_place_id == final_result.third_place_id:
            score += 5
        elif pred.third_place_id in [final_result.first_place_id, final_result.second_place_id]:
            score += 3
        
        pred.score = score
    
    try:
        db.session.commit()
        print(f"✅ Scores calculés pour {len(predictions)} prédictions")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur lors du calcul des scores: {e}")
        raise

if __name__ == '__main__':
    import socket
    with app.app_context():
        db.create_all()
    
    # Get local IP address for display
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"\n{'='*60}")
        print(f"🚀 Serveur démarré!")
        print(f"📱 Accès local:     http://localhost:5002")
        print(f"🌐 Accès réseau:    http://{local_ip}:5002")
        print(f"{'='*60}\n")
    except:
        print(f"\n🚀 Serveur démarré sur http://0.0.0.0:5002\n")
    
    # Run on all network interfaces (0.0.0.0) to allow access from local network
    # threaded=True allows handling multiple requests
    # use_reloader=False prevents issues with network access
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True, use_reloader=False)

