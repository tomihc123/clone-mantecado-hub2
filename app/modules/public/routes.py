import logging

from flask import render_template
from app.modules.featuremodel.services import FeatureModelService
from app.modules.public import public_bp
from app.modules.dataset.services import DataSetService

logger = logging.getLogger(__name__)

@public_bp.route("/")
def index():
    logger.info("Access index")
    dataset_service = DataSetService()
    feature_model_service = FeatureModelService()

    # Fetch dataset statistics
    datasets_counter = dataset_service.count_synchronized_datasets()
    feature_models_counter = feature_model_service.count_feature_models()
    total_dataset_downloads = dataset_service.total_dataset_downloads()
    total_dataset_views = dataset_service.total_dataset_views()

    # Render the main page
    return render_template("public/index.html")

@public_bp.route("/dashboard")
def dashboard():
    dataset_service = DataSetService()
    feature_model_service = FeatureModelService()

    # Fetch data for dashboard
    datasets_counter = dataset_service.count_synchronized_datasets()
    feature_models_counter = feature_model_service.count_feature_models()
    total_dataset_downloads = dataset_service.total_dataset_downloads()
    total_dataset_views = dataset_service.total_dataset_views()

    # Pass data to the dashboard template
    return render_template("public/dashboard.html",
                           datasets_counter=datasets_counter,
                           feature_models_counter=feature_models_counter,
                           total_dataset_downloads=total_dataset_downloads,
                           total_dataset_views=total_dataset_views)
